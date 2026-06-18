# subset-b-000697 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kprobes.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/kprobes.c

### Purpose
`kprobes.c` implements the LoongArch architecture backend for kernel probes. It plants LoongArch breakpoint instructions at probed text addresses, prepares either out-of-line single-step slots or simulated execution for instructions that cannot safely run from the slot, and connects breakpoint, single-step, and fault handling into the generic kprobes core.

### Important APIs, Types, And Functions
The file defines per-CPU `current_kprobe` and `kprobe_ctlblk`, exports the architecture hooks `arch_prepare_kprobe`, `arch_arm_kprobe`, `arch_disarm_kprobe`, `arch_remove_kprobe`, `kprobe_breakpoint_handler`, `kprobe_singlestep_handler`, `kprobe_fault_handler`, `arch_populate_kprobe_blacklist`, `arch_init_kprobes`, and `arch_trampoline_kprobe`. It uses LoongArch break encodings `BRK_KPROBE_BP` and `BRK_KPROBE_SSTEPBP`, `union loongarch_instruction`, instruction decoder helpers such as `insns_not_supported`, `insns_need_simulation`, and `arch_simulate_insn`, plus generic kprobe helpers for probe lookup, miss accounting, and handler invocation.

### Control Flow
Probe preparation validates 4-byte alignment, snapshots the original instruction, rejects unsupported opcodes, then either allocates a two-instruction slot containing the original instruction plus a single-step breakpoint or records that the instruction will be simulated. Arming replaces the probed instruction with `KPROBE_BP_INSN` and flushes instruction cache state; disarming restores the saved opcode. On breakpoint, the handler disables preemption, looks up the probe by `csr_era`, runs the pre-handler if present, and either redirects `csr_era` to the out-of-line slot or simulates the instruction and immediately post-processes. The single-step handler recognizes the slot breakpoint, restores the saved interrupt state, invokes post-handler logic, and resets current probe state.

### State, Persistence, And Dependencies
State is strictly runtime and per-CPU: current probe pointer, previous reentered probe state, saved interrupt flags, and probe status. Kprobe text patching persists until the probe is disarmed or removed. The backend depends on LoongArch trap delivery from `traps.c`, instruction-slot allocation from the generic kprobe layer, instruction decode/simulation support, and text-cache coherency helpers. It blacklists `__irqentry_text_start..__irqentry_text_end` so interrupt entry code cannot be probed.

### Integration Points
The trap path dispatches `BRK_KPROBE_BP` and `BRK_KPROBE_SSTEPBP` to this file. Generic kprobes call the architecture prepare/arm/disarm/remove hooks, and debugfs exposes the arch blacklist. The probe path also coexists with kgdb, uprobes, and BUG breakpoints by returning `false` for breakpoints it does not own.

### Risks
Incorrect interrupt masking around single-step can accidentally single-step into interrupt handlers. Reentrant probe handling is delicate: losing previous probe state or preemption state would corrupt nested probe execution. Simulated-instruction support must stay aligned with the LoongArch decoder; unsupported branch, PC-relative, or privileged instructions need rejection or correct simulation. The arming/disarming writes directly to kernel text, so cache flushing and races with removed breakpoints are high-risk.

### Test Signals
High-signal validation includes `CONFIG_KPROBES` selftests on LoongArch, probes on normal instructions and simulated instruction classes, nested probe tests, probe removal while hit, post-handler path redirection, fault-in-single-step recovery, and boot checks that kprobes blacklist entries cover interrupt entry symbols. Runtime failures usually appear as missed probes, stuck preemption, bad `csr_era`, or unexpected breakpoint traps in `do_bp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/lbt.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/lbt.S

### Purpose
`lbt.S` provides low-level save, restore, initialization, and signal-context transfer helpers for the LoongArch Binary Translation extension state. It preserves scratch registers, x86 compatibility flags, and x87 top-of-stack metadata used by LBT-aware task switching, signal delivery, and ptrace-style context export.

### Important APIs, Types, And Functions
Exported symbols are `_save_lbt`, `_restore_lbt`, `_save_lbt_context`, `_restore_lbt_context`, `_save_ftop_context`, and `_restore_ftop_context`; `_init_lbt` is local architecture setup. The code uses `movscr2gr`, `movgr2scr`, `x86mfflag`, `x86mtflag`, `x86mftop`, and `x86mttop`, plus `THREAD_SCR*` and `THREAD_EFLAGS` offsets from `asm-offsets.h`. The `EX` macro wraps user-memory loads/stores with exception-table fixups that return `-EFAULT`.

### Control Flow
Thread save/restore paths copy `$scr0..$scr3` and flag state between hardware and `thread_struct`. User signal helpers copy the same state to user buffers with fault recovery. FTOP restore masks the requested value to three bits, jumps through an eight-entry inline table, executes the matching immediate `x86mttop`, then returns success. Any protected user access fault branches to `.L_lbt_fault` and returns `-EFAULT`.

### State, Persistence, And Dependencies
The persistent state is the per-task LBT snapshot in `thread_struct` and user signal-frame LBT context. Hardware state persists only while the task owns the LBT unit. The file depends on LoongArch LBT instructions, the exception table mechanism, thread offset definitions, and C wrappers in `signal.c` and `traps.c`.

### Integration Points
`process.c` duplicates and clears LBT state across fork/exec boundaries, `traps.c` lazily initializes/restores LBT on BTD exceptions, and `signal.c` uses the context helpers when building or restoring extended signal frames. The GPL exports are available to architecture code and modules that need LBT context management.

### Risks
The routines assume exact offsets and register widths; stale `asm-offsets.h` values would corrupt unrelated thread fields. FTOP restore is marked non-standard stack frame, so unwinder assumptions are limited. Signal-context helpers must fault safely on invalid user pointers, and any missing exception-table annotation would turn a recoverable bad frame into a kernel fault.

### Test Signals
Exercise LBT workloads across context switch, signal delivery, sigreturn, fork, and exec. Add invalid-user-frame sigreturn tests for `-EFAULT`, FTOP values 0-7 plus masked out-of-range values, and mixed FPU/LBT signal frames. Build tests should cover `CONFIG_CPU_HAS_LBT` and unwinder warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/lbt.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/machine_kexec.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/machine_kexec.c

### Purpose
`machine_kexec.c` implements the LoongArch machine-level kexec and crash-kexec handoff. It prepares safe control code, copies command line data to a low safe area, stops secondary CPUs, converts kexec page-list addresses into directly accessible cached virtual addresses, masks interrupts, and jumps into the relocation stub that enters the next kernel.

### Important APIs, Types, And Functions
The public hooks are `machine_kexec_prepare`, `machine_kexec_cleanup`, `machine_shutdown`, `machine_crash_shutdown`, `machine_kexec`, `kexec_reboot`, and `crash_smp_send_stop` under SMP. Key state includes `reboot_code_buffer`, `cpus_in_crash`, `kexec_ready_to_reboot`, and latched EFI/cmdline/system-table/start/indirection addresses. It consumes `relocate_new_kernel`, `relocate_new_kernel_size`, and `kexec_smp_wait` from `relocate_kernel.S`.

### Control Flow
Prepare records EFI arguments, finds or copies the command line, sets `control_code_page` to `KEXEC_CONTROL_CODE`, copies the relocation stub there, and computes the relocated secondary wait function. Normal shutdown on SMP brings possible CPUs online and sends `kexec_shutdown_secondary`, which marks each CPU offline, disables IRQs, waits for `kexec_ready_to_reboot`, then enters the common reboot path. Crash shutdown saves crash CPU registers, sends crash IPIs, waits up to 10 seconds for other CPUs to save state, masks interrupts, and then `machine_kexec` updates indirection entries before releasing CPUs and jumping.

### State, Persistence, And Dependencies
The handoff state persists only through the reboot transition in fixed low physical/cached addresses `0x100000` and `0x108000`. It depends on generic kexec image layout, EFI boot arguments, LoongArch direct-map/cache helpers, crash dump CPU-save APIs, SMP IPI delivery, and the assembly relocation code.

### Integration Points
Generic `kernel/kexec*` calls these machine hooks. `machine_kexec_file.c` populates `image->arch.cmdline_ptr` for file-mode loads. Crash dump integration uses `crash_save_cpu`, `machine_kexec_mask_interrupts`, and crashkernel reservation from setup. Secondary CPUs enter the mailbox wait loop in `relocate_kernel.S`.

### Risks
The fixed safe memory range must remain reserved and truly safe; overlap with firmware, crashkernel, or loaded segments would corrupt handoff code or command line. Page-list virtual conversion mutates `image->head` entries and must preserve kexec flags. SMP crash paths can hang if secondary CPUs fail to service IPIs or if `kexec_ready_to_reboot` is never observed. Logging the command line may expose sensitive boot arguments.

### Test Signals
Validate normal `kexec -e`, file-mode kexec, crash-kexec, SMP secondary parking, CPU hotplug interactions, and EFI argument propagation. Inspect console for EFI/cmdline/start notices, ensure crash dumps contain per-CPU notes, and verify the new kernel receives the expected command line and initrd. Fault injection around missing command line and nonresponding secondary CPUs is useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/machine_kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/machine_kexec_file.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/machine_kexec_file.c

### Purpose
`machine_kexec_file.c` implements LoongArch support for the in-kernel `kexec_file_load` path. It selects EFI and ELF file loaders, constructs the modified command line, places initrd and crash dump metadata segments, and prepares cleanup for allocated ELF core headers.

### Important APIs, Types, And Functions
It exports the `kexec_file_loaders` array, `arch_kimage_file_post_load_cleanup`, and `load_other_segments`. Helper functions append `kexec_file`, `initrd=start,size`, `mem=size@start`, and `elfcorehdr=size@start` command-line tokens. Under `CONFIG_CRASH_DUMP`, `prepare_elf_headers` builds a `crash_mem` range list and calls `crash_prepare_elf64_headers`.

### Control Flow
`load_other_segments` allocates a bounded command-line buffer, appends the loader token, optionally creates and loads ELF core headers for crash images, optionally places initrd after the loaded kernel with a 1 GiB aligned/32 GiB window heuristic, checks command-line length, copies the caller command line after generated tokens, and stores `image->arch.cmdline_ptr`. On error it restores the original segment count and frees temporary command-line storage.

### State, Persistence, And Dependencies
Loaded initrd and ELF core header segments persist inside the `struct kimage` segment list until execution or cleanup. `image->elf_headers`, `elf_load_addr`, and `elf_headers_sz` record crash metadata. The code depends on generic `kexec_add_buffer`, memblock range iteration, crashkernel resources, and `COMMAND_LINE_SIZE`.

### Integration Points
Architecture-specific EFI and ELF loaders call `load_other_segments` after loading the kernel. `machine_kexec.c` later copies the generated command line to the safe handoff area. Crash dump tooling consumes `elfcorehdr` and `mem=` parameters generated here.

### Risks
Command-line construction is size-sensitive and uses formatted appends into a fixed buffer; missed bounds before `sprintf` would be dangerous if new tokens are added. Error cleanup resets only `nr_segments`, so any future side state must be cleaned explicitly. Initrd placement constraints need to match LoongArch boot-loader expectations. Crash memory exclusion must handle high and low crashkernel regions exactly.

### Test Signals
Run `kexec_file_load` with EFI and ELF kernels, with and without initrd, and verify `/proc/cmdline` in the next kernel includes `kexec_file` and correct initrd coordinates. Crash-kexec tests should validate vmcore creation and `elfcorehdr` parsing. Negative tests include too-long command lines and forced buffer placement failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/machine_kexec_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/mcount.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/mcount.S

### Purpose
`mcount.S` is the classic LoongArch `_mcount` implementation for function tracing and function graph tracing when dynamic patchable ftrace is not the active entry path. It calls the registered trace function with callsite and parent return addresses, and optionally rewrites function returns through the graph tracer.

### Important APIs, Types, And Functions
The main exported symbol is `_mcount`. It also defines `ftrace_stub`, `ftrace_graph_func`, `ftrace_graph_caller`, and `return_to_handler` when graph tracing is enabled. It calls `ftrace_trace_function`, `prepare_ftrace_return`, and `ftrace_return_to_handler`, while saving only `s0` and `ra` in a small local frame.

### Control Flow
At function entry, `_mcount` loads `ftrace_trace_function`; if it differs from `ftrace_stub`, it saves registers and calls the tracer with `ra` and the parent return address. It then checks graph tracing callbacks and either returns through `ftrace_stub` or calls `ftrace_graph_caller`, which asks `prepare_ftrace_return` to replace the parent return address. `return_to_handler` saves return-value registers, asks generic graph tracing for the real parent address, restores return values, and jumps there.

### State, Persistence, And Dependencies
State is controlled by global ftrace function pointers patched by generic tracing. The assembly depends on LoongArch ABI conventions, stack-frame offsets, and the compiler's mcount call sequence. No persistent storage is owned locally.

### Integration Points
This file integrates with `kernel/trace/ftrace.c`, graph tracer core, and LoongArch build flags that emit mcount calls. It is parallel to `mcount_dyn.S`, which handles patchable-function-entry/dynamic ftrace.

### Risks
The code relies on precise return-address interpretation; off-by-one-instruction callsite math would corrupt call graph output. Saving too few registers is safe only because psABI caller/callee rules are honored. Graph tracing must preserve return-value registers or traced functions will misbehave.

### Test Signals
Enable function tracer and function graph tracer, trace simple kernel functions, verify callsite and parent symbols, and run with modules if classic mcount is used. Stress with nested tracing and functions returning values in `a0/a1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/mcount.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/mcount_dyn.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/mcount_dyn.S

### Purpose
`mcount_dyn.S` implements the dynamic ftrace trampoline path for LoongArch patchable function entries. It builds partial or full `pt_regs`, invokes the selected ftrace operation, supports function graph tracing, and includes the direct-call trampoline used by dynamic ftrace direct calls.

### Important APIs, Types, And Functions
It defines `ftrace_stub`, `ftrace_common`, `ftrace_call`, `ftrace_graph_call`, `ftrace_caller`, `ftrace_regs_caller`, `ftrace_graph_caller`, `return_to_handler`, and `ftrace_stub_direct_tramp`. The `ftrace_regs_entry` macro saves argument registers, frame pointer, return addresses, and optionally all GPRs into a `PT_SIZE` frame matching `struct pt_regs`.

### Control Flow
Patchable function entry branches arrive with `t0` holding parent `ra`. The caller wrapper saves registers, computes `ip = ra - 8`, loads `function_trace_op`, and calls the patched `ftrace_call` site. If graph tracing is patched in, `ftrace_graph_caller` calls `prepare_ftrace_return` using the saved parent return slot. The common return path restores live ABI registers and either returns to the original function continuation or, when direct-call state is present in `PT_R13`, jumps to a direct target.

### State, Persistence, And Dependencies
Persistent state lives in generic ftrace static globals and dynamically patched branch sites, not in this file. The assembly depends on `-fpatchable-function-entry=2`, LoongArch module trampolines, `asm/ftrace.h` address constants, `asm/stackframe.h` pt_regs offsets, and graph/direct ftrace configuration.

### Integration Points
`ftrace_dyn.c` patches callsites and module trampolines to these entry points. Generic ftrace and graph tracer code supply callbacks, direct-call targets, and return handlers. The generated `pt_regs` shape is consumed by `CONFIG_DYNAMIC_FTRACE_WITH_REGS` callbacks.

### Risks
The entry contract is tight: compiler patchable-entry layout, module trampoline layout, and `ra - 8` callsite math must remain in sync. Incorrect saved register layout breaks ftrace-with-regs consumers. Direct-call return routing through `PT_R13` is subtle and can redirect control flow incorrectly if not initialized exactly.

### Test Signals
Run dynamic ftrace selftests, ftrace-with-regs probes, graph tracing, module tracing, and direct-call tracing. Inspect patched instructions in core kernel and modules and verify callbacks see correct `ip`, `parent_ip`, `op`, and register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/mcount_dyn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/mem.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/mem.c

### Purpose
`mem.c` seeds the early memblock allocator from EFI memory descriptors on LoongArch. It classifies usable and reserved firmware regions, reserves low memory and kernel image ranges, establishes PFN limits, and assigns all memory and reserved memblocks to node 0 before later NUMA setup may refine ownership.

### Important APIs, Types, And Functions
The file contains `memblock_init`. It iterates `for_each_efi_memory_desc`, reads `efi_memory_desc_t` fields, calls `memblock_add`, `memblock_reserve`, `memblock_set_current_limit`, and `memblock_set_node`, and updates `max_pfn` and `max_low_pfn`.

### Control Flow
Usable EFI types such as loader, boot-service, persistent, and conventional memory are added to memblock. PAL, unusable, and ACPI reclaim memory are added and then intentionally fall through to reserve them. Reserved/runtime/MMIO types are reserved without being added as normal RAM. After descriptor parsing, the first 2 MiB, the kernel text/data/bss range, and highmem limit are reserved/configured.

### State, Persistence, And Dependencies
The persistent boot state is the memblock memory and reserved region lists that drive page allocator initialization. It depends on EFI initialization having populated the memory map and on `_text`, `_end`, `PHYS_OFFSET`, `HIGHMEM_START`, and LoongArch physical-address helpers being correct.

### Integration Points
`setup_arch` calls `memblock_init` before page table and platform initialization. Later setup code applies `mem=` overrides, crashkernel/initrd reservations, NUMA coverage validation, resources, CMA, SWIOTLB, and memtest based on these memblock lists.

### Risks
Firmware memory classification mistakes can expose reserved/runtime memory to the allocator or hide usable RAM. The deliberate fallthrough for PAL/unusable/ACPI reclaim memory is important; removing it would add those regions as free. Reserving only the first 2 MiB assumes the platform's low-memory hazards fit that range.

### Test Signals
Boot with EFI memory-map debug and compare `/proc/iomem` against firmware. Test ACPI reclaim/unusable regions, highmem boundaries, `mem=` overrides, crashkernel reservations, and boot on systems with persistent memory descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/module-sections.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/module-sections.c

### Purpose
`module-sections.c` sizes and emits LoongArch module GOT, PLT, PLT index, and ftrace trampoline sections. It scans relocation records before final layout to reserve enough architecture-specific entries for long branches, GOT references, and dynamic ftrace trampolines.

### Important APIs, Types, And Functions
Public helpers are `module_emit_got_entry`, `module_emit_plt_entry`, and `module_frob_arch_sections`. Internal helpers include `compare_rela` and `count_max_entries`. The code manipulates `struct mod_section`, `struct got_entry`, `struct plt_entry`, `struct plt_idx_entry`, and relocation types such as `R_LARCH_SOP_PUSH_PLT_PCREL`, `R_LARCH_B26`, `R_LARCH_GOT_PC_HI20`, and `R_LARCH_GOT_PCADD_HI20`.

### Control Flow
`module_frob_arch_sections` finds `.got`, `.plt`, `.plt.idx`, and optional `.ftrace_trampoline` sections, rejects modules missing required sections, scans executable relocation sections, sorts relocations by info/addend to count unique PLT/GOT needs, then converts the empty sections to allocated `SHT_NOBITS` with cache-line alignment and computed size. Emission helpers reuse an existing matching entry when possible or append a new one and advance counters.

### State, Persistence, And Dependencies
The module's architecture section counters persist in `mod->arch` for relocation application. Generated GOT and PLT contents persist in loaded module memory and are executed/read by relocated code. Dependencies include module loader section mutation, LoongArch relocation definitions, ftrace trampoline constants, and section names produced by module linking.

### Integration Points
`module.c` calls `module_emit_got_entry` and `module_emit_plt_entry` while applying relocations. `module_finalize` initializes `.ftrace_trampoline` contents. Dynamic ftrace uses module trampoline slots for callsites outside direct branch range.

### Risks
Counting must match relocation application exactly; undercounting causes BUGs or rejection, while overcounting wastes module memory. Sorting relocation records mutates the in-memory module image before relocation and must be acceptable to the loader. Missing paired GOT relocations are detected late in `module_emit_got_entry`.

### Test Signals
Load modules with many external calls, far branch targets, GOT references, duplicate relocations, and dynamic ftrace enabled. Negative tests should include malformed modules missing `.got`/`.plt`/`.plt.idx` and bad unpaired GOT relocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/module-sections.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/module.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/module.c

### Purpose
`module.c` applies LoongArch ELF RELA relocations to loaded modules and finalizes architecture-specific module features. It implements the stack-operation relocation language, direct absolute/PC-relative relocations, long-branch PLT generation, GOT references, alternatives, ORC unwind metadata, and ftrace trampoline initialization.

### Important APIs, Types, And Functions
The main exported loader hook is `apply_relocate_add`, with `module_finalize` for post-relocation setup. Relocation handlers cover `R_LARCH_32`, `R_LARCH_64`, SOP push/pop/arithmetic relocations, add/sub relocations, `R_LARCH_B26`, PCADD/PCALA, GOT_PC/GOT_PCADD, and 32/64-bit PC-relative data relocations. Helpers use `union loongarch_instruction`, `signed_imm_check`, `unsigned_imm_check`, `module_emit_plt_entry`, `module_emit_got_entry`, `apply_alternatives`, and `unwind_module_init`.

### Control Flow
For each relocation entry, the loader computes `location`, symbol value plus addend, resolves weak unresolved symbols, chooses a handler, and applies instruction-field or data updates. SOP relocations push operands onto a bounded per-module stack, perform arithmetic/logic/select operations, and pop into encoded instruction fields with alignment/range checks. `B26` and PLT PC-relative relocations use PLT entries when the target is outside the signed 128 MiB branch reach. PCADD/GOT PCADD LO12 relocation handling scans for the corresponding HI20 relocation to compute the correct low residual.

### State, Persistence, And Dependencies
Relocation effects persist in module text/data, GOT, PLT, and unwind/ftrace sections. Temporary relocation stack state is local to one relocation section. The code depends on module section addresses, relocation order enough to find HI20 partners, LoongArch instruction bitfield definitions, and helper sections sized by `module-sections.c`.

### Integration Points
The generic module loader calls `apply_relocate_add` and `module_finalize`. Alternatives integrate with CPU feature patching, ORC metadata integrates with stack unwinding, and dynamic ftrace consumes initialized ftrace PLTs. GOT/PLT emission is shared with `module-sections.c`.

### Risks
Relocation range and alignment errors can create silent bad code if not caught; this file explicitly rejects overflow and unaligned branch/immediate values. The HI20/LO12 pairing scan is subtle and can fail on unexpected relocation sequences. Stack-operation relocations are vulnerable to malformed modules exhausting or underflowing `RELA_STACK_DEPTH`. Long-branch PLT decisions use strict `>= SZ_128M` and `< -SZ_128M` checks that must match ISA reach.

### Test Signals
Build and load modules with all supported relocation families, external calls beyond branch range, GOT references, alternatives, ORC unwinding, and dynamic ftrace. Run module load/unload under `CONFIG_32BIT` and `CONFIG_64BIT` where available. Malformed relocation tests should verify `-ENOEXEC`, `-EINVAL`, and unresolved non-weak symbol failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/numa.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/numa.c

### Purpose
`numa.c` manages early LoongArch CPU-to-node mapping, per-node CPU masks, per-CPU allocator placement, and ACPI/fake NUMA memory initialization. It bridges firmware topology and memblock memory ranges into Linux NUMA node state.

### Important APIs, Types, And Functions
Global state includes `numa_off`, `cpus_on_node`, `phys_cpus_on_node`, `__cpuid_to_node`, and optionally `__per_cpu_offset`. Important functions are `setup_per_cpu_areas`, `early_cpu_to_node`, `early_numa_add_cpu`, `numa_add_cpu`, `numa_remove_cpu`, `init_numa_memory`, and `pcibus_to_node`. ACPI NUMA support uses `numa_memblks_init`, `acpi_numa_init`, `memblock_validate_numa_coverage`, and `numa_add_memblk`.

### Control Flow
Early CPU discovery records physical CPU IDs into node masks. Per-CPU setup chooses embedded allocation for smaller node counts and page allocation otherwise, then computes each CPU's `__per_cpu_offset`. NUMA memory init clears CPU-node maps, parses SRAT/SLIT or fakes node 0, logs EFI memory by node, validates coverage, allocates node data, marks nodes online, updates PFN limits, and stores node/core counts in `loongson_sysconf`.

### State, Persistence, And Dependencies
CPU and memory node maps persist for scheduler, allocator, PCI locality, and hotplug. The code depends on EFI memory descriptors, ACPI NUMA parsing, memblock, Loongson CPU maps from SMP setup, and `nid_to_addrbase`/`pa_to_nid` platform address decoding.

### Integration Points
`setup_arch` calls `init_numa_memory` under `CONFIG_NUMA`; `smp_prepare_boot_cpu` and secondary CPU init call add/remove CPU helpers. The per-CPU allocator calls `pcpu_cpu_to_node` and `pcpu_populate_pte`. PCI code calls `pcibus_to_node`.

### Risks
Physical/logical CPU ID confusion is a main risk: `__cpuid_to_node` is indexed by physical ID, while `cpu_to_node` uses logical IDs later. Incomplete SRAT coverage returns `-EINVAL`. Fake NUMA assumes all memory is one node, which is safe only for non-ACPI systems. `cores_per_node` is derived from node 0 physical mask and may misrepresent asymmetric systems.

### Test Signals
Boot ACPI NUMA and non-ACPI systems, inspect `/sys/devices/system/node`, `/proc/zoneinfo`, CPU node masks, per-CPU allocation logs, and PCI locality. Test CPU hotplug and memory maps with holes or multiple address bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/paravirt.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/paravirt.c

### Purpose
`paravirt.c` enables LoongArch KVM paravirtual features: optimized IPI delivery, steal-time accounting, virtual preemption hints, and paravirtual spinlock static keys. It detects KVM by CPUCFG signature and switches architecture hooks when advertised features are present.

### Important APIs, Types, And Functions
Global keys are `virt_preempt_key`, `virt_spin_lock_key`, and `paravirt_steal_enabled` integration via generic code. Per-CPU state is `struct kvm_steal_time steal_time`. Important functions include `kvm_para_available`, `kvm_arch_para_features`, `pv_ipi_init`, `pv_time_init`, `pv_spinlock_init`, `paravt_steal_clock`, `pv_send_ipi_single`, `pv_send_ipi_mask`, and `pv_ipi_interrupt`.

### Control Flow
Feature detection reads CPUCFG signature and feature bits. If KVM IPI is available, `pv_ipi_init` saves native `mp_ops` and replaces init/send hooks; boot-CPU IPIs still go through native delivery. PV IPI sends coalesce action bits in per-CPU `irq_stat.message` and use KVM hypercalls, while SWI0 interrupt handling drains message bits and calls scheduler, call-function, irq-work, or IRQ migration handlers. Steal-time init registers the per-CPU physical address with KVM, installs CPU hotplug and reboot callbacks, updates the `pv_steal_clock` static call, and enables accounting static keys.

### State, Persistence, And Dependencies
Paravirt state persists in static keys, static calls, `mp_ops`, per-CPU steal-time pages, and hypervisor registration. It depends on KVM hypercall ABI, LoongArch CPUCFG feature bits, SWI0 IRQ mapping, SMP `irq_stat`, cpuhp, and reboot notifier infrastructure.

### Integration Points
SMP setup calls `pv_ipi_init`; boot CPU preparation calls `pv_spinlock_init`; `time_init` calls `pv_time_init`. Scheduler accounting reads steal time through the updated static call, and queued IPI actions use the same generic handlers as native IPI delivery.

### Risks
The steal-time structure must not cross a page boundary, and failure disables the feature. PV IPI bitmap clustering uses a 128-bit bitmap and physical CPU IDs; incorrect CPU map assumptions could miss CPUs. Replacing `mp_ops` must preserve native boot CPU behavior. The `no-steal-acc` early param disables runqueue accounting but not steal clock registration.

### Test Signals
Boot under KVM with and without advertised IPI, steal-time, preempt, and spinlock features. Check dmesg feature messages, `/proc/stat` steal accounting, CPU hotplug registration/unregistration hypercalls, IPI counters, and reboot notifier cleanup. Compare scheduler behavior with `no-steal-acc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/paravirt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/perf_event.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/perf_event.c

### Purpose
`perf_event.c` implements LoongArch hardware PMU support and perf callchains. It maps generic and cache perf events to Loongson PMU event IDs, allocates per-CPU counters, handles overflows, exposes a `cpu` PMU, and supplies kernel/user callchain walkers.

### Important APIs, Types, And Functions
Key types are `struct cpu_hw_events`, `struct loongarch_perf_event`, and `struct loongarch_pmu`. The PMU callbacks are `loongarch_pmu_event_init`, `add`, `del`, `start`, `stop`, `read`, `enable`, and `disable`, registered through `perf_pmu_register`. Counter/control CSR helpers operate on four CSR pairs, while initialization derives counter count and bit width from `LOONGARCH_CPUCFG6`. Callchain APIs are `perf_callchain_user` and `perf_callchain_kernel`.

### Control Flow
Event init rejects branch-stack sampling, checks event type and target CPU, requests the per-CPU `INT_PCOV` IRQ on first active event, maps the event, sets privilege filters, period state, and group validation. Add allocates a free counter in `used_mask`, disables it, stores the event pointer, and optionally starts it. Start programs the period and saved control state; PMU enable writes saved controls to hardware. Overflow IRQ pauses counters, scans used counters for the overflow bit, updates counts, reloads periods, calls `perf_event_overflow`, resumes counters, and runs irq work.

### State, Persistence, And Dependencies
Per-CPU event arrays, used masks, saved control registers, active event count, and raw-event mutex are runtime state. PMU CSR state persists while events are active. Dependencies include LoongArch PMU CSRs, interrupt mapping, generic perf core, stack unwinder, user access helpers, and CPU feature `cpu_has_pmp`.

### Integration Points
Generic perf opens the registered `"cpu"` PMU. `traps.c`/IRQ routing must deliver `INT_PCOV`. Stack unwinding integrates with ORC/prologue unwinder code. `perf_regs.c` provides register sampling support.

### Risks
The implementation defines `LOONGARCH_MAX_HWEVENTS` as 32 but CSR helpers only handle counters 0-3; if CPUCFG reports more than four counters, later reads/writes warn and return zero. Overflow uses bit 63 with `max_period = 2^63-1`, so counter width assumptions must match hardware. Group validation is a simple counter-count model and does not model event-specific counter constraints if future PMUs add them. Raw events share a global `raw_event` protected only during init.

### Test Signals
Run `perf stat` for cycles, instructions, cache refs/misses, branch events, raw events, and grouped events up to and beyond available counters. Run sampling to force overflow IRQs, user and kernel callchain collection, CPU hotplug, and concurrent perf opens/closes. Check dmesg for PMU counter count and invalid counter warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/perf_regs.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/perf_regs.c

### Purpose
`perf_regs.c` implements LoongArch register sampling ABI helpers for perf. It reports whether a task is using 32-bit or 64-bit register ABI, validates requested register masks, and extracts sampled register values from `pt_regs`.

### Important APIs, Types, And Functions
The file defines `perf_reg_abi`, `perf_reg_validate`, `perf_reg_value`, and `perf_get_regs_user`. It uses `PERF_REG_LOONGARCH_MAX`, `PERF_REG_LOONGARCH_PC`, `PERF_SAMPLE_REGS_ABI_32`, `PERF_SAMPLE_REGS_ABI_64`, and thread flag `TIF_32BIT_REGS`.

### Control Flow
ABI selection is compile-time fixed for 32-bit kernels and task-flag dependent for 64-bit kernels. Mask validation rejects empty masks and bits outside the LoongArch perf register range. Value lookup returns `csr_era` for the PC pseudo-register and GPR array entries otherwise. User register capture points perf at `task_pt_regs(current)`.

### State, Persistence, And Dependencies
No local state persists. It depends on stable `pt_regs` layout, LoongArch perf register enum definitions, and thread flags set by ABI/personality code.

### Integration Points
`perf_event_open` register sampling and sample formatting call these helpers. `perf_event.c` callchain and PMU support complement this file for complete perf samples.

### Risks
Register enum order must match `pt_regs->regs[]`; otherwise sampled register masks return wrong registers. `perf_get_regs_user` always samples current task registers, which is correct for perf user samples but would be wrong if reused for arbitrary tasks.

### Test Signals
Use `perf record --sample-regs` with GPR and PC masks on 32-bit and 64-bit tasks. Validate rejected masks and compare sampled PC/registers against ptrace or signal-frame register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/proc.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/proc.c

### Purpose
`proc.c` backs `/proc/cpuinfo` for LoongArch. It formats system type, per-CPU topology, CPU/FPU revision, frequency, BogoMIPS, TLB size, address widths, ISA level, feature flags, and hardware watchpoint counts through a `seq_file` iterator.

### Important APIs, Types, And Functions
The exported object is `cpuinfo_op`. Internal functions are `show_cpuinfo`, `c_start`, `c_next`, and `c_stop`. Data sources include `cpu_data`, `__cpu_family`, `__cpu_full_name`, `cpu_clock_freq`, `const_clock_freq`, `lpj_fine`, `cpu_pabits`, `cpu_vabits`, `get_system_type`, and CPU feature macros.

### Control Flow
The seq iterator maps positions to CPU numbers. `show_cpuinfo` skips offline CPUs under SMP, prints the system type once for CPU 0, computes display MHz and BogoMIPS with `do_div`, and emits feature strings conditionally based on global CPU capability flags.

### State, Persistence, And Dependencies
The file has no mutable state. It depends on CPU probing, time initialization, and SMP topology having populated `cpu_data` and frequency globals before users read `/proc/cpuinfo`.

### Integration Points
Generic procfs CPU info code uses `cpuinfo_op`. The reported feature names are user-visible ABI for tools parsing `/proc/cpuinfo`.

### Risks
Feature strings and field labels are de facto ABI; renaming can break scripts. The frequency/BogoMIPS math depends on valid `const_clock_freq` and `HZ`. Skipping offline CPUs means seq positions may not produce output for every possible CPU.

### Test Signals
Compare `/proc/cpuinfo` on single-core, SMP, hotplug, LSX/LASX/LBT, and watchpoint-capable systems. Verify CPU MHz against clocksource data and feature flags against CPUCFG probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/process.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/process.c

### Purpose
`process.c` implements LoongArch process/thread lifecycle support: user-mode thread setup, fork context copying, kernel-thread return paths, FPU/SIMD/LBT state handling across duplication, wait-channel lookup, stack classification, userspace stack randomization, cross-CPU backtraces, and ELF core register dumps.

### Important APIs, Types, And Functions
Important functions include `start_thread`, `flush_thread`, `arch_dup_task_struct`, `ret_from_fork`, `ret_from_kernel_thread`, `copy_thread`, `__get_wchan`, `get_stack_info`, `stack_top`, `arch_align_stack`, `arch_trigger_cpumask_backtrace`, and `loongarch_dump_regs32/64`. Global exports include stack canary support and `boot_option_idle_override`.

### Control Flow
`start_thread` drops privilege to PLV user, disables FP in EUEN, clears live math/SIMD/LBT flags, sets PC and SP, and resets FCSR. `arch_dup_task_struct` saves any live hardware FPU/SIMD state before copying task data, then copies only the relevant thread-state prefix plus optional LBT state unless RANDSTRUCT forces a full copy. `copy_thread` builds child `pt_regs` at the top of the kernel stack, sets scheduler return addresses for user or kernel threads, handles TLS, and clears lazy hardware ownership flags.

### State, Persistence, And Dependencies
Persistent per-task state is `thread_struct`, saved registers, FPU/SIMD/LBT context, hw breakpoints, VDSO placement, and task stack metadata. The code depends on LoongArch ABI register conventions, lazy FPU helpers, ptrace hardware breakpoint copying, unwinder APIs, stack layout constants, randomization, and NMI/backtrace infrastructure.

### Integration Points
Scheduler context switch assembly consumes fields set here. Exec and fork paths call these hooks. Signal, ptrace, perf, stacktrace, and core-dump code depend on consistent `pt_regs` and thread-state layout. Backtrace IPIs integrate with SMP call-single infrastructure.

### Risks
Lazy FPU/SIMD/LBT duplication is race-prone; saving live hardware state under preemption disable is essential. `copy_thread` must set child return registers exactly or fork/kernel-thread startup will return to the wrong path. Stack-info helpers trust saved stack sentinels for IRQ stacks and can misclassify corrupted stacks. VDSO stack-top reservation affects userspace ABI layout.

### Test Signals
Run fork/clone/exec, kernel thread creation, TLS tests, FP/LSX/LASX/LBT workloads across fork, ptrace hardware breakpoint inheritance, `/proc/<pid>/wchan`, stacktrace reliability, core dumps, and sysrq/NMI CPU backtraces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ptrace.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/ptrace.c

### Purpose
`ptrace.c` implements LoongArch ptrace and core-dump register access. It exposes GPR, FPR, CPUCFG, LSX, LASX, LBT, hardware breakpoint, and hardware watchpoint regsets; supports legacy `PTRACE_PEEKUSR`/`POKEUSR`; and implements ptrace single-step using hardware breakpoints.

### Important APIs, Types, And Functions
The file defines `ptrace_disable`, `task_user_regset_view`, `arch_ptrace`, `regs_query_register_offset`, `user_enable_single_step`, and `user_disable_single_step`. Regset handlers include `gpr_get/set`, `fpr_get/set`, `cfg_get/set`, `simd_get/set`, `lbt_get/set`, and `hw_break_get/set`. Hardware breakpoint helpers wrap perf breakpoints through `register_user_hw_breakpoint`, `modify_user_hw_breakpoint`, and architecture encode/decode helpers.

### Control Flow
Regset reads save live FPU state as needed, then copy data into `membuf`; writes initialize FP context when needed and copy user data into thread state. SIMD reads pad unavailable upper lanes with all ones based on whether FP, LSX, or LASX context is live. Hardware breakpoint regset writes ignore resource-info input, then apply address, mask, and control triplets, creating disabled perf breakpoint events lazily. Single-step sets or reuses instruction breakpoint slot 0 at current `csr_era`, records the address, and sets `TIF_SINGLESTEP`.

### State, Persistence, And Dependencies
Ptrace-visible state persists in `pt_regs`, `thread.fpu`, `thread.lbt`, `thread.hbp_break/watch`, thread flags `TIF_LOAD_WATCH` and `TIF_SINGLESTEP`, and per-task perf breakpoint events. The code depends on stable ELF note types, user regset ABI sizes, LoongArch CPUCFG, FPU/SIMD layout, perf hardware breakpoint support, and security/no-spec indexing helpers.

### Integration Points
Generic ptrace and core dump code use the regset view. `traps.c` handles watchpoint and single-step traps. `process.c` copies hardware breakpoints on fork and clears them on flush. Debuggers such as gdb consume the note types and legacy user offsets.

### Risks
The regset layout is ABI-sensitive. `ptrace_hbptriggered` has two loops using the same index variable and the watch loop overwrites the break-loop result, so signal errno identification should be reviewed carefully. Single-step reuses breakpoint slot 0, which can interact with user-programmed hardware breakpoints. Kernel address rejection differs between 32-bit and 64-bit address ranges and must match user/kernel split.

### Test Signals
Run gdb/ptrace tests for GPR/FPR/CPUCFG/LSX/LASX/LBT get/set, core dump note validation, legacy peek/poke offsets, hardware breakpoint/watchpoint programming, single-step over normal and LL/SC-like sequences, and detach cleanup. Include invalid regset sizes, out-of-range breakpoint indices, and kernel-space breakpoint addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/relocate.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/relocate.c

### Purpose
`relocate.c` performs early kernel relocation and KASLR fixups for LoongArch. It copies the kernel to a randomized aligned address when enabled, applies relative and absolute relocations, handles RELR entries, updates the runtime relocation offset, and registers a panic notifier that prints relocation information.

### Important APIs, Types, And Functions
The main entry is `relocate_kernel`. Helpers include `relocate_relative`, `relocate_absolute`, `rotate_xor`, `get_random_boot`, `kaslr_disabled`, `determine_relocation_address`, `relocation_addr_valid`, `update_reloc_offset`, and the panic notifier callback. It uses linker symbols `__rela_dyn_*`, `__relr_dyn_*`, `__la_abs_*`, `_text`, `_end`, `_sdata`, and `__bss_start`.

### Control Flow
The entry maps the firmware command line from `fw_arg1`, copies it into `boot_command_line`, chooses a KASLR destination unless `nokaslr`, hibernation resume parameters, or `kexec_file` disable randomization, validates alignment/non-overlap, computes base relocation offset, and unmaps the command line. If randomized, it copies the kernel image, flushes instruction/data ordering, adjusts `__current_thread_info`, and writes the new relocation offset into the relocated image. It then applies relative relocations and patches absolute address materialization instruction sequences.

### State, Persistence, And Dependencies
`reloc_offset` persists as the runtime offset and is printed on panic. The relocated kernel image and patched relocation entries are permanent for the booted kernel. Dependencies include early ioremap, random entropy, LoongArch instruction formats, linker-provided relocation sections, command-line policy, and panic notifier infrastructure.

### Integration Points
Early boot assembly calls `relocate_kernel`. `setup.c` later uses the copied `boot_command_line`. Panic reporting uses the notifier registered at `arch_initcall`. Kexec-file disables KASLR through the command-line marker added by `machine_kexec_file.c`.

### Risks
KASLR entropy is intentionally simple and early; it should not be treated as cryptographic. Absolute relocation patching assumes exact instruction sequences described by `struct rela_la_abs`. Destination validation only checks alignment and original-kernel overlap, so platform memory-map assumptions matter. Hibernation command-line detection disables KASLR to preserve resume behavior.

### Test Signals
Boot with and without `CONFIG_RANDOMIZE_BASE`, `nokaslr`, `resume=`, `noresume`, `nohibernate`, and kexec-file. Inspect dmesg/panic relocation output, verify symbol addresses move by a consistent offset, and test RELR-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/relocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/relocate_kernel.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/relocate_kernel.S

### Purpose
`relocate_kernel.S` is the kexec relocation stub copied to a safe low-memory control page. It interprets the generic kexec indirection page list, copies source pages to destination pages, synchronizes caches/barriers, and jumps to the new kernel. Under SMP it also provides the secondary CPU mailbox wait loop.

### Important APIs, Types, And Functions
Defined symbols are `relocate_new_kernel`, optional `kexec_smp_wait`, and data symbol `relocate_new_kernel_size`. The entry ABI passes EFI boot flag, command line pointer, system table pointer, start address, and first indirection entry in `a0..a4`.

### Control Flow
The stub saves the indirection pointer in `s0`; crash kernels with no indirection jump directly to `done`. Otherwise it loops over entries, updating destination address for `IND_DESTINATION`, switching list pages for `IND_INDIRECTION`, terminating on `IND_DONE`, and copying one page word-by-word for `IND_SOURCE`. The `done` path executes `ibar` and `dbar`, then jumps to `a3` preserving boot arguments. Secondary CPUs poll `LOONGARCH_IOCSR_MBUF0`, convert the mailbox PC to cached address space, and jump to it.

### State, Persistence, And Dependencies
The stub mutates physical memory at destination pages and relies on the copied control page remaining executable. It depends on generic kexec entry flag encodings, page size constants, LoongArch IOCSR mailbox, and cached address-space layout.

### Integration Points
`machine_kexec_prepare` copies this code and records its size; `machine_kexec` passes converted indirection entries. SMP shutdown sends secondaries into the relocated `kexec_smp_wait`.

### Risks
The copy loop assumes whole-page copies and correct virtual address conversion before entry. Cache/barrier sequencing is critical before entering the new kernel. The secondary mailbox polling loop can spin forever if firmware or boot CPU never writes a PC.

### Test Signals
Normal kexec with multiple source/destination/indirection pages, crash-kexec direct-entry path, SMP secondary restart, and page-size configuration changes should be tested. Early boot failures in the next kernel often indicate bad copy or stale I-cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/relocate_kernel.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/reset.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/reset.c

### Purpose
`reset.c` implements LoongArch halt, power-off, and restart machine operations. It stops other CPUs, disables local interrupts where appropriate, calls generic power/restart notifiers, and falls back to EFI, ACPI, or idle loops.

### Important APIs, Types, And Functions
The file defines exported `pm_power_off`, plus `machine_halt`, `machine_power_off`, and `machine_restart`. It integrates with `smp_send_stop`, `do_kernel_power_off`, `do_kernel_restart`, `efi.reset_system`, `efi_reboot`, `acpi_reboot`, and `enable_pci_wakeup`.

### Control Flow
All three operations stop SMP peers under `CONFIG_SMP`. Halt disables interrupts and interrupt masks, prints a safe-power-off message, flushes consoles, and idles forever. Power-off enables PCI wakeup under ACPI/PM, calls generic power-off hooks, attempts EFI shutdown, then idles. Restart calls generic restart hooks, chooses warm EFI reboot for pending capsules or cold otherwise, falls back to ACPI reboot, then idles.

### State, Persistence, And Dependencies
No persistent local state beyond `pm_power_off`. Machine state changes are external firmware/hardware side effects. Dependencies include SMP stop reliability, EFI runtime services, ACPI reboot support, PM wakeup setup, and console flushing.

### Integration Points
Generic reboot and power management code calls these architecture hooks. Platform drivers may assign `pm_power_off` through the exported symbol.

### Risks
If firmware reset calls return, the CPU remains in an idle loop with peers stopped. Restart ordering between generic notifiers, EFI capsule handling, and ACPI fallback affects firmware update flows. Halt disables local IRQs before console flush on panic-pending state, so console driver behavior matters.

### Test Signals
Test `reboot`, `poweroff`, `halt`, EFI capsule reboot, ACPI reboot fallback, SMP stop behavior, and wakeup-enabled poweroff. Verify no CPU continues running after stop and consoles flush expected messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook.c

### Purpose
`rethook.c` implements the LoongArch architecture glue for generic return hooks. It saves a function's original return address into a `rethook_node`, replaces the live return address with the architecture trampoline, and dispatches trampoline callbacks to the generic rethook handler.

### Important APIs, Types, And Functions
It defines `arch_rethook_trampoline_callback` and `arch_rethook_prepare`, and marks `arch_rethook_trampoline` as not probeable. It uses `struct rethook_node`, `struct pt_regs`, and `rethook_trampoline_handler`.

### Control Flow
Preparation records `regs->regs[1]` as `rhn->ret_addr`, clears `rhn->frame`, and overwrites `regs->regs[1]` with the assembly trampoline address. When the instrumented function returns, the trampoline builds `pt_regs` and calls `arch_rethook_trampoline_callback`, which asks generic rethook code for the real return address.

### State, Persistence, And Dependencies
Per-invocation state persists in the `rethook_node` until generic rethook handling completes. It depends on LoongArch using register 1 as return address, the assembly trampoline preserving registers, and kprobes/rethook recursion avoidance.

### Integration Points
Generic rethook and kretprobe infrastructure call this file. `rethook_trampoline.S` provides the actual control-transfer and register-save code.

### Risks
Replacing the return address is control-flow sensitive; any mismatch between `pt_regs` saved by assembly and generic rethook expectations can return to the wrong location. The `mcount` argument is ignored, so future mcount-specific behavior would need explicit handling.

### Test Signals
Run kretprobe/rethook tests on normal functions, nested returns, and functions with live argument/return registers. Confirm the trampoline is absent from kprobeable symbols and that original return addresses are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook.h -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook.h

### Purpose
`rethook.h` declares the LoongArch-local rethook callback and preparation helpers shared between C and assembly rethook code.

### Important APIs, Types, And Functions
It declares `arch_rethook_trampoline_callback(struct pt_regs *regs)` and `arch_rethook_prepare(struct rethook_node *rhn, struct pt_regs *regs, bool mcount)`. The include guard is `__LOONGARCH_RETHOOK_H`.

### Control Flow
The header has no executable control flow. It allows `rethook_trampoline.S` and `rethook.c` to agree on the callback interface.

### State, Persistence, And Dependencies
No state is stored. It depends on visible declarations of `struct pt_regs` and `struct rethook_node` at inclusion sites.

### Integration Points
Included by `rethook.c`; the assembly file calls the callback by symbol rather than through this header.

### Risks
Prototype drift between this header and the assembly call ABI would break return hooks. The `bool mcount` parameter in the prepare prototype must stay consistent with generic rethook expectations.

### Test Signals
Compilation with rethook/kretprobe enabled is the main validation. Runtime tests are covered by `rethook.c` and `rethook_trampoline.S`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook_trampoline.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook_trampoline.S

### Purpose
`rethook_trampoline.S` is the LoongArch return-hook trampoline. It saves a full base-register frame, calls the C rethook callback with a `pt_regs` pointer, uses the callback result as the real return address, restores registers and privilege/interrupt bits, and jumps back.

### Important APIs, Types, And Functions
The exported code symbol is `arch_rethook_trampoline`. Local macros `save_all_base_regs` and `restore_all_base_regs` use `cfi_st`/`cfi_ld` and `PT_*` offsets to save GPRs and selected CRMD bits. It calls `arch_rethook_trampoline_callback`.

### Control Flow
On entry, the trampoline allocates `PT_SIZE`, saves base registers and CRMD PLV/IE bits, records caller SP in `PT_R3`, passes `sp` as `pt_regs`, and calls the C callback. The callback returns the original or modified return address in `a0`; the trampoline moves it to `ra`, restores all saved registers and CRMD masked bits, drops the frame, and `jr ra`.

### State, Persistence, And Dependencies
Only stack-frame state persists during trampoline execution. The code depends on exact `struct pt_regs` offsets, CFI macros, LoongArch CSR access, and `rethook.c` callback semantics.

### Integration Points
`arch_rethook_prepare` installs this symbol into `regs->regs[1]`. Generic rethook/kretprobe code consumes the constructed `pt_regs`.

### Risks
All register save/restore offsets must match `pt_regs`; missing a live register can corrupt the interrupted function. Restoring CRMD PLV/IE bits with `csrxchg` changes privilege/interrupt state and must be limited to the intended mask. The trampoline has undefined unwind hints, so stack traces through it may be limited.

### Test Signals
Kretprobe/rethook stress tests should verify preserved arguments, return values, stack pointer, CRMD interrupt state, and nested hooks. Objtool/unwind diagnostics should be checked for this nonstandard control-flow path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook_trampoline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/setup.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/setup.c

### Purpose
`setup.c` is the main LoongArch architecture boot setup file. It initializes firmware arguments, CPU and SMBIOS metadata, command-line policy, FDT/ACPI/EFI platform state, memory reservations, resources, legacy I/O windows, possible CPU maps, and the architecture-specific `setup_arch` sequence.

### Important APIs, Types, And Functions
Global state includes `fw_arg0..2`, per-CPU `kernelsp`, `cpu_data`, `b_info`, `init_command_line`, `wc_enabled`, and kernel resource descriptors. Major functions are `arch_cpu_finalize_init`, `setup_writecombine`, `early_parse_mem`, `platform_init`, `arch_mem_init`, `resource_init`, `arch_reserve_pio_range`, `reserve_memblock_reserved_regions`, `prefill_possible_map`, and `setup_arch`.

### Control Flow
`setup_arch` probes CPU/unwinder, initializes environment and EFI/FDT, seeds memblock and page tables, builds boot command line, parses early params, reserves initrd, initializes ACPI/FDT/NUMA/DMI/EFI runtime platform state, then performs memory init, resource registration, jump-label setup, SMP possible-map setup, and KASAN init. Early `mem=` parsing can either enforce a global limit or replace firmware RAM maps with explicit ranges.

### State, Persistence, And Dependencies
Boot-time state persists in global command lines, memblock reservations, resource tree entries, CPU data, board info, write-combine flag, EFI runtime state, flattened/unflattened DT, and NUMA maps. Dependencies span EFI, ACPI, FDT, DMI/SMBIOS, memblock, SWIOTLB, DMA/CMA, crash dump, kexec, SMP, alternatives, and KASAN.

### Integration Points
This is called from generic early boot. `mem.c`, `numa.c`, `smp.c`, `time.c`, `relocate.c`, and platform firmware parsers all feed data into it. Resource and PIO registration affect drivers and `/proc/iomem`; command-line decisions affect every early parameter.

### Risks
Boot order is critical: command-line parsing, memblock setup, platform reservation, and NUMA initialization must occur before page allocator setup. `mem=` can remove firmware-discovered memory and must preserve node assignment under NUMA. FDT is skipped when ACPI root pointer exists. Legacy ISA I/O registration assumes the range starts at logic PIO offset 0. SMBIOS parsing uses fixed offsets and must match table versions.

### Test Signals
Boot ACPI and FDT systems, built-in DTB fallback, command-line force/extend/bootloader modes, `mem=` forms, crashkernel/vmcore reservation, initrd reservation, writecombine parameter, NUMA, legacy ISA I/O, EFI runtime, and KASAN builds. Compare `/proc/iomem`, DMI logs, and CPU possible/present masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/signal.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/signal.c

### Purpose
`signal.c` implements LoongArch signal delivery and sigreturn. It builds `rt_sigframe` records, saves/restores GPR and extended FP/LSX/LASX/LBT contexts, handles restartable syscalls around signal delivery, manages alternate stacks, and returns through the VDSO sigreturn stub.

### Important APIs, Types, And Functions
The user-visible syscall is `rt_sigreturn`; architecture entry point is `arch_do_signal_or_restart`. Internal helpers include context copy/save/restore functions for FPU, LSX, LASX, LBT, `parse_extcontext`, `setup_sigcontext`, `restore_sigcontext`, `setup_extcontext`, `get_sigframe`, `setup_rt_frame`, and `handle_signal`. Types include `struct extctx_layout`, `struct sctx_info`, `fpu_context`, `lsx_context`, `lasx_context`, and `lbt_context`.

### Control Flow
Signal delivery computes an aligned user frame, allocates extension contexts from the top downward with an end marker, writes siginfo/ucontext/sigmask, saves GPRs and live FP/SIMD/LBT state, then sets handler args in `a0..a2`, SP, RA to VDSO sigreturn, and ERA to the handler. Sigreturn validates frame access, restores blocked mask, parses extension records by magic/size, restores GPRs and optional extended state, handles pending FCSR exceptions, restores altstack, clears syscall restart flag, and returns restored `a0`.

### State, Persistence, And Dependencies
Persistent state crosses user/kernel boundary in the signal frame and thread saved contexts. The code depends on lazy FPU/SIMD/LBT ownership, user access helpers, VDSO layout, restart-block semantics, rseq signal delivery, signal stack helpers, and magic/size ABI values in `asm/sigframe.h`.

### Integration Points
Entry/exit code calls `arch_do_signal_or_restart` before returning to user mode. `lbt.S` and FPU assembly helpers perform hardware context transfer. `process.c` initializes thread FP/LBT state, and `traps.c` sets `thread.error_code` for address-error signal flags.

### Risks
Signal frame layout is ABI-sensitive. Extension parsing accepts records in user memory and must reject bad magic/size to avoid walking arbitrary memory. Lazy FP/SIMD/LBT save/restore is protected by preemption and pagefault disabling; mistakes can lose hardware state. `fcsr_pending` may force SIGFPE during sigreturn if handlers set enabled exception bits. Restart PC adjustment assumes 4-byte syscall instruction size.

### Test Signals
Run signal ABI tests for basic delivery, altstack overflow, sigreturn corruption, syscall restart variants, rseq, FP/LSX/LASX/LBT live contexts, pending FCSR exceptions, and 16-byte stack alignment. Compare signal-frame contents against ptrace/core dump register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/smp.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/smp.c

### Purpose
`smp.c` implements LoongArch SMP topology, IPI delivery, secondary CPU boot, CPU hotplug/dead loops, PM IPI restore, boot CPU preparation, stop-IPIs, and cross-CPU TLB shootdowns. It connects firmware CPU maps to Linux logical CPUs and manages sibling/core/LLC masks.

### Important APIs, Types, And Functions
Global maps include `__cpu_number_map`, `__cpu_logical_map`, `cpu_sibling_map`, `cpu_llc_shared_map`, `cpu_core_map`, `cpu_foreign_map`, `cpuboot_data`, and `mp_ops`. Key functions include `show_ipi_list`, `calculate_cpu_foreign_map`, `loongson_smp_setup`, `loongson_prepare_cpus`, `loongson_boot_secondary`, `loongson_init_secondary`, `loongson_smp_finish`, `smp_prepare_boot_cpu`, `smp_prepare_cpus`, `__cpu_up`, `start_secondary`, `smp_send_stop`, and the `flush_tlb_*` family.

### Control Flow
FDT setup maps hardware CPU IDs to logical IDs and initializes node state. Prepare paths parse ACPI topology, clear mailboxes, mark boot CPU online, set sibling/LLC/core masks, and enable paravirt hooks. Booting a secondary writes the physical entry address to mailbox 0 and sends `ACTION_BOOT_CPU`; the secondary syncs counters, sets per-CPU offset, probes CPU, initializes timer/IPI state, marks itself online, signals completions, enables IRQs, and enters the idle loop. TLB shootdowns either call remote CPUs via masks or clear stale `cpu_context` entries when the mm is local-only.

### State, Persistence, And Dependencies
Persistent state includes CPU maps, topology masks, per-CPU online/hotplug state, IOCSR mailbox/IPI registers, and mm context generation per CPU. Dependencies include ACPI/PPTT topology, OF CPU nodes, Loongson IOCSR IPI/mailbox registers, paravirt IPI hooks, timer sync, cpuhp, IRQ migration, and TLB local flush primitives.

### Integration Points
Generic SMP calls architecture prepare/boot/start/stop hooks. `/proc/interrupts` uses `show_ipi_list`. NUMA code consumes CPU maps. Paravirt may replace `mp_ops`. MM code calls `flush_tlb_all/mm/range/kernel_range/page/one`.

### Risks
CPU logical/physical maps must be initialized before IPIs and mailbox sends. Completion reuse in CPU bring-up assumes serialized CPU-up operations. Hotplug rejects I/O master CPUs and must migrate IRQs before disabling masks. TLB shootdown optimizations that skip remote IPIs rely on accurate `mm_users`, `current->mm`, and `cpu_context` state.

### Test Signals
Boot SMP via ACPI and FDT, CPU hotplug online/offline, hibernation nonboot CPU disable, paravirt and native IPIs, `/proc/interrupts` IPI counters, stop/reboot paths, and mm stress tests that exercise all TLB flush variants across multiple CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/stacktrace.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/stacktrace.c

### Purpose
`stacktrace.c` implements LoongArch stack walking for kernel, reliable kernel, and user stacks. It adapts saved/current frame state into the architecture unwinder and provides user frame-tail walking for perf and stacktrace consumers.

### Important APIs, Types, And Functions
Public functions are `arch_stack_walk`, `arch_stack_walk_reliable`, and `arch_stack_walk_user`. Helpers include `copy_stack_frame`. It uses `struct unwind_state`, `unwind_start`, `unwind_next_frame`, `unwind_get_return_address`, `unwind_error`, `thread_saved_fp`, `thread_saved_ra`, and `struct stack_frame`.

### Control Flow
Kernel walking builds dummy regs from current builtin frame/return address or saved task FP/RA when no regs are supplied, then iterates unwind frames until done or the consumer stops. Reliable walking additionally rejects null addresses, consumer refusal, and any unwind error. User walking starts from user FP register 22, copies frame tails inatomic, requires 16-byte alignment and monotonic frame growth, and feeds return addresses to the consumer.

### State, Persistence, And Dependencies
No local state persists. It depends on compiler frame-pointer conventions or ORC/prologue unwind support, task saved scheduler registers, user stack accessibility, and LoongArch `pt_regs` register numbering.

### Integration Points
Generic stacktrace APIs, perf callchains, livepatch reliability checks, warnings, and debugging tools call these functions. `process.c` stack classification and `traps.c` register dumps complement this file.

### Risks
Reliable stack walking is only as good as unwind metadata and saved registers. User frame walking assumes frame-pointer ABI and can stop early on optimized code. Inatomic user copies avoid sleeping but must tolerate partial faults.

### Test Signals
Run stacktrace selftests, livepatch reliable-stack checks, perf user/kernel callchains, optimized and frame-pointer builds, blocked-task stack traces, and invalid user FP chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/switch.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/switch.S

### Purpose
`switch.S` implements the LoongArch low-level scheduler context switch routine `__switch_to`. It saves non-scratch registers and scheduler metadata from the previous task, restores the next task state, switches thread pointer, updates saved kernel SP, and restores saved PRMD.

### Important APIs, Types, And Functions
The sole symbol is `__switch_to(prev, next, next_ti, sched_ra, sched_cfa)`. It uses `cpu_save_nonscratch`, `cpu_restore_nonscratch`, `THREAD_*` offsets, `TASK_STRUCT_OFFSET`, `set_saved_sp`, and optional stack protector canary update for non-SMP.

### Control Flow
The function reads current PRMD into previous thread state, saves callee-saved registers, stores scheduler return address and CFA, updates the stack canary when needed, moves `tp` to the next thread-info pointer, restores next non-scratch registers, writes the next saved stack pointer, restores next PRMD, and returns to the scheduler caller through `ra`.

### State, Persistence, And Dependencies
Persistent state is the saved non-scratch register set and CSR PRMD in each task's `thread_struct`, plus per-task kernel stack pointer metadata. It depends on exact offsets generated by `asm-offsets.h` and LoongArch calling convention.

### Integration Points
The generic scheduler calls this through architecture switch helpers. `process.c` initializes the thread fields consumed here. Stack unwinding uses stored scheduler RA/CFA.

### Risks
Any mismatch in offsets or saved register set causes task corruption. PRMD restore controls previous privilege/interrupt state and must match exception return expectations. 32-bit TASK_STRUCT offset adjustment must stay synchronized with struct layout.

### Test Signals
Scheduler stress, CPU hotplug, preemption, kernel threads, user threads, stack protector builds, and unwinder backtraces across context switches are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/switch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/syscall.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/syscall.c

### Purpose
`syscall.c` defines LoongArch syscall table wiring and syscall entry handling. It also provides LoongArch-specific `mmap` and `mmap2` syscalls that validate offset alignment before delegating to `ksys_mmap_pgoff`.

### Important APIs, Types, And Functions
Public pieces are `SYSCALL_DEFINE6(mmap)`, `SYSCALL_DEFINE6(mmap2)`, `sys_call_table`, and `do_syscall`. The syscall table includes either `asm/syscall_table_32.h` or `asm/syscall_table_64.h`. Entry uses `syscall_enter_from_user_mode`, `syscall_exit_to_user_mode`, `array_index_nospec`, and `add_random_kstack_offset`.

### Control Flow
`do_syscall` reads syscall number from `a7` (`regs[11]`), records a restart marker in `regs[0]`, advances ERA past the syscall instruction, saves original `a0`, initializes return value to `-ENOSYS`, runs generic syscall-enter hooks, randomizes kernel stack offset, dispatches through the nospec-indexed table if in range, places return value in `a0`, and exits to user mode.

### State, Persistence, And Dependencies
Syscall restart state persists transiently in `regs[0]` and `orig_a0` for signal handling. The syscall table is static kernel ABI. Dependencies include generated syscall headers, LoongArch syscall ABI register assignments, and generic entry/exit tracing, audit, seccomp, and random-kstack code.

### Integration Points
Low-level exception assembly calls `do_syscall`. `signal.c` interprets `regs[0]`, `regs[4]`, `orig_a0`, and ERA for syscall restart. Seccomp/audit/tracing hooks run through generic entry code.

### Risks
ERA adjustment and restart flag handling must match signal restart code exactly. `mmap2` offset shifting depends on `PAGE_SHIFT`. The syscall table default to `sys_ni_syscall` is safe only if generated includes cover all valid numbers.

### Test Signals
Run syscall ABI tests, seccomp/audit/tracepoint tests, interrupted syscall restart scenarios, `mmap`/`mmap2` offset alignment tests, and 32-bit vs 64-bit table builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/sysrq.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/sysrq.c

### Purpose
`sysrq.c` registers a LoongArch SysRq command that dumps TLB registers and entries. It serializes output and, on SMP, schedules work to request dumps from other CPUs.

### Important APIs, Types, And Functions
The file defines `sysrq_tlbdump_single`, `sysrq_tlbdump_othercpus`, `sysrq_handle_tlbdump`, `sysrq_tlbdump_op`, and `loongarch_sysrq_init`. It uses `dump_tlb_regs`, `dump_tlb_all`, `register_sysrq_key`, `smp_call_function`, a spinlock, and a work item.

### Control Flow
Pressing SysRq `x` dumps the current CPU under `show_lock`, then schedules work that calls the same dump routine on other CPUs via SMP call-function. Registration runs at `arch_initcall`.

### State, Persistence, And Dependencies
Only the spinlock and work item persist. The command depends on TLB dump helpers, SysRq being enabled, and SMP call-function availability.

### Integration Points
Generic SysRq dispatch invokes the registered key operation. TLB diagnostics integrate with LoongArch MMU and SMP subsystems.

### Risks
Dumping all TLB entries can be verbose and runs in diagnostic contexts; the spinlock prevents interleaved output but can delay CPUs. Scheduled work means remote CPU dumps may occur after the triggering context returns.

### Test Signals
Enable SysRq, trigger `x`, verify current and remote CPU dumps appear without interleaving, and test on UP/SMP and with CPUs hotplugged offline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/sysrq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/time.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/time.c

### Purpose
`time.c` provides LoongArch constant-counter clocksource, per-CPU clockevent, scheduler clock, timer IRQ handling, counter synchronization, and paravirtual time initialization.

### Important APIs, Types, And Functions
Exported globals are `cpu_clock_freq` and `const_clock_freq`. Important functions include `constant_clockevent_init`, `constant_clocksource_init`, `time_init`, `save_counter`, `sync_counter`, `constant_timer_interrupt`, timer state callbacks, `constant_timer_next_event`, `read_const_counter`, and `sched_clock_read`.

### Control Flow
`time_init` chooses constant-counter frequency from CPUCFG or CPU clock, computes initial counter offset, registers the local clockevent and clocksource, and initializes PV time. Clockevent init maps/request the per-CPU timer IRQ once, configures each CPU's `clock_event_device`, syncs the counter, sets `lpj_fine`, and installs cpuhp callbacks that enable timer interrupts on AP start and clear pending interrupts on death. Timer IRQ clears CSR timer interrupt and calls the clockevent handler.

### State, Persistence, And Dependencies
Persistent state includes global frequencies, `init_offset`, per-CPU clockevent devices, timer IRQ installation flags, CSR timer config, and registered clocksource/sched_clock. Dependencies include LoongArch CSRs, CPUCFG constant frequency calculation, generic clockchips/clocksource, cpuhp, and paravirt time.

### Integration Points
`setup.c`/CPU probe populate CPU clock data; `smp.c` calls `sync_counter` and AP clockevent init. Scheduler, timers, VDSO timekeeping, and delay loops consume the registered clocksource/event devices.

### Risks
`timer_irq_installed` and `irq` are static shared state in `constant_clockevent_init`; the first CPU must initialize before APs. Counter synchronization assumes writing `CNTC` with `init_offset` gives a common zero base. Min/max delta must match hardware timer bit width. Periodic mode divides by `HZ` and masks into CSR field.

### Test Signals
Boot timing, clocksource selection, timer interrupts on all CPUs, CPU hotplug, high-resolution timers, periodic/oneshot modes, sched_clock monotonicity, VDSO clock mode, and KVM steal-time interaction are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/topology.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/topology.c

### Purpose
`topology.c` supplies the LoongArch CPU hotplug policy hook for topology code. It marks I/O master CPUs as non-hotpluggable so platform-critical CPUs remain online.

### Important APIs, Types, And Functions
Under `CONFIG_HOTPLUG_CPU`, it defines `arch_cpu_is_hotpluggable(int cpu)` and calls `io_master(cpu)`.

### Control Flow
The function returns the negation of `io_master(cpu)`: normal CPUs are hotpluggable, I/O master CPUs are not.

### State, Persistence, And Dependencies
No local state is stored. It depends on `loongson_sysconf.cores_io_master` and related `io_master` logic populated during CPU/platform setup.

### Integration Points
Generic CPU hotplug and sysfs topology code call this hook to decide whether a CPU may be offlined. `smp.c` enforces the same policy in `loongson_cpu_disable`.

### Risks
Incorrect I/O master classification can either prevent useful hotplug or allow offlining a CPU needed for platform I/O/interrupt duties.

### Test Signals
Check `/sys/devices/system/cpu/cpu*/online` behavior and CPU hotplug attempts for I/O master and non-master CPUs. Validate consistency with `loongson_cpu_disable`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/traps.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/kernel/traps.c

### Purpose
`traps.c` is the central LoongArch exception and interrupt handling implementation. It maps exception codes to low-level handlers, prints register/stack diagnostics, handles breakpoints, FPU/SIMD/LBT lazy enable traps, alignment/bounds/address errors, reserved instructions, hardware watchpoints, vector table setup, IRQ stack switching, die/oops behavior, and trap initialization.

### Important APIs, Types, And Functions
Global exports include `exception_table`, `show_stack`, `show_regs`, `show_registers`, `die`, `do_fpe`, `do_ade`, `do_ale`, `do_bce`, `do_bp`, `do_watch`, `do_ri`, `do_fpu`, `do_lsx`, `do_lasx`, `do_lbt`, `do_reserved`, `cache_parity_error`, `handle_loongarch_irq`, `do_vint`, `per_cpu_trap_init`, `set_handler`, `set_merr_handler`, and `trap_init`. It uses `exception_handlers`, `eentry`, `tlbrentry`, and CSR printers for CRMD/PRMD/EUEN/ECFG/ESTAT.

### Control Flow
Boot-time trap init configures vector size and exception vector base, initializes default reserved handlers, installs TLB/cache handlers and per-exception handlers, and flushes I-cache. At runtime low-level assembly dispatches to handlers by exception code. Breakpoint handling decodes the break code and delegates to kgdb, kprobes, uprobes, BUG, divzero/overflow, or SIGTRAP paths. Lazy FPU/LSX/LASX/LBT handlers enable and restore context under preemption disable. `do_vint` switches to a per-CPU IRQ stack when necessary, calls the generic arch IRQ handler, and restores the original stack.

### State, Persistence, And Dependencies
Persistent state includes installed exception handler code, vector base CSRs, per-CPU ASID cache initialization, active_mm setup for early CPUs, unaligned access sysctls, and die counter. Dependencies include low-level handler symbols from assembly, TLB/cache init, kprobes/uprobes/kgdb/perf/hw-breakpoint hooks, FPU/SIMD/LBT helpers, unwinder, signal delivery, exception tables, kexec crash handling, and generic IRQ entry code.

### Integration Points
Entry assembly, MMU/TLB code, debug subsystems, perf, signal handling, kexec crash dump, SMP IRQ stacks, and CPU initialization all depend on this file. `kprobes.c`, `ptrace.c`, `stacktrace.c`, and `process.c` consume or feed trap state.

### Risks
Exception handlers are `noinstr` paths where tracing, lock ordering, and IRQ state must be controlled carefully. Breakpoint dispatch ordering matters because kgdb/kprobes/uprobes/BUG all share break instructions. Lazy FPU/SIMD/LBT paths can corrupt task state if ownership flags and hardware enables diverge. Vector installation copies code into executable memory and requires I-cache flushing. `do_watch` single-step skip logic around LL/SC and self-loops is subtle.

### Test Signals
Run exception selftests for SIGSEGV/SIGBUS/SIGILL/SIGTRAP/SIGFPE, kprobes/uprobes/kgdb breakpoints, BUG/WARN, unaligned access emulation, bounds-check faults, FP/LSX/LASX/LBT first-use traps, hardware watchpoints and ptrace single-step, IRQ stack unwinding, crash_kexec-on-oops, and CPU bring-up trap initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/traps.c -->
