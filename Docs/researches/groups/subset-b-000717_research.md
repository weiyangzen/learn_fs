# Research: subset-b-000717

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/head.S

## Purpose

`head.S` is the MMU-enabled Linux/m68k bootstrap for classic 68020/030/040/060 and platform families such as Amiga, Atari, Macintosh, HP300, VME, Q40, Apollo, Sun3x, and the virtual platform. It runs before normal C setup, consumes bootinfo records placed after `_end`, builds the first kernel page tables, maps the kernel and early machine I/O windows, enables the MMU and caches, installs an initial stack, calls `base_trap_init()`, and finally enters `start_kernel()`.

## Important APIs, Types, and Functions

The exported entry symbols are `_stext`, `_start`, and `__start`. The file also defines `kernel_pg_dir` at `_stext`, and data symbols consumed by C code: `availmem`, `m68k_init_mapped_size`, `m68k_pgtable_cachemode`, `m68k_supervisor_cachemode`, plus VME/Q40 support symbols when configured. Its internal macro-callable routines include `get_bi_record`, `mmu_map`, `mmu_map_tt`, `mmu_fixup_page_mmu_cache`, `mmu_temp_map`, `mmu_engage`, `mmu_get_root_table_entry`, `mmu_get_ptr_table_entry`, `mmu_get_page_table_entry`, `get_new_page`, serial output helpers, and optional early console helpers.

## Control Flow

Boot starts by setting the temporary stack to `_stext`, reading `BI_MACHTYPE`, `BI_CPUTYPE`, `BI_FPUTYPE`, and `BI_MMUTYPE`, converting CPU bits into local `CPUTYPE_*` flags, choosing cache attributes, raising interrupt priority to `0x2700`, and collecting machine-specific bootinfo needed for very early serial/video debug. It then initializes serial and optional Mac framebuffer console output.

The core path maps the initial kernel memory window at `PAGE_OFFSET`, adds per-machine I/O mappings through either full page tables or transparent translation registers, fixes MMU table cache attributes on 040/060, optionally dumps mappings, and calls `mmu_engage`. After the MMU transition it rewrites early physical addresses to their final logical mappings, enables CPU caches, switches to `init_thread_union`, initializes the exception vector base through `base_trap_init`, and jumps to `start_kernel`.

## State and Persistence Behavior

The file persists early architecture state in global words used by later C setup: boot CPU/machine attributes, page-table cache modes, initial mapped size, `availmem`, platform debug pointers, and the kernel page directory. It allocates early page and pointer tables by bumping `L(memory_start)` until `availmem` is fixed. It also permanently programs MMU root pointers, transparent translation registers, cache control registers, and, for debug builds, early serial or framebuffer state.

## Dependencies and Integration Points

It depends on bootinfo record layout from `<asm/bootinfo*.h>`, m68k page flag definitions, platform machine constants, `init_task`, `init_thread_union`, `base_trap_init`, and `start_kernel`. It is paired with `setup_mm.c`, which rereads bootinfo and consumes `availmem`, `m68k_*` globals, and platform machine hooks. `vectors.c` relies on `base_trap_init()` being called before the kernel uses instructions that may trap on 68060/FPU support code.

## Risks and Edge Cases

This is CPU- and board-specific assembly with many hard-coded physical ranges. Wrong bootinfo, stale machine constants, or misdetected CPU type can leave the kernel without valid I/O mappings or cache attributes. The MMU transition is fragile because the program counter, stack, frame pointer, and return address are all adjusted while switching root tables. Early page-table allocation assumes the bootinfo block directly follows the kernel and that free memory is page aligned after `BI_LAST`. Debug serial and console paths directly touch hardware and can hang if selected for the wrong board. Cache-mode regressions are especially risky on 040/060 because page tables and writeback caches have CPU-specific coherency rules.

## Test Signals

Useful evidence is successful boot on representative 030, 040, 060, Sun3x, and platform-specific configs; early printk progress characters through `J`/`K`; correct `/proc/cpuinfo` values later from the same globals; valid `availmem` and `m68k_init_mapped_size`; no bus error during MMU enable; and a final map showing kernel text/data and expected I/O ranges. Debug builds can enable `MMU_PRINT` or `CONFIG_EARLY_PRINTK` to trace map construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/ints.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/ints.c

## Purpose

`ints.c` provides the common Linux/m68k interrupt controller setup for autovector and user-vector interrupt ranges. It bridges architecture vector-table entries to the generic IRQ subsystem and lets machine code replace default IRQ chips or handlers for specific ranges.

## Important APIs, Types, and Functions

The main APIs are `init_IRQ()`, `m68k_setup_auto_interrupt()`, `m68k_setup_user_interrupt()`, `m68k_setup_irq_controller()`, `m68k_irq_startup_irq()`, `m68k_irq_startup()`, `m68k_irq_shutdown()`, `irq_canonicalize()`, and `handle_badint()`. Two default `irq_chip` instances, `auto_irq_chip` and `user_irq_chip`, use m68k startup/shutdown callbacks. The file references assembler fixup locations `auto_irqhandler_fixup[]` and `user_irqvec_fixup[]`, and the architecture `vectors[]` array.

## Control Flow

`init_IRQ()` assigns `handle_simple_irq` and the default autovector chip to `IRQ_AUTO_1` through `IRQ_AUTO_7`, then delegates board initialization to `mach_init_IRQ()`. Machine code may call `m68k_setup_auto_interrupt()` to patch the autovector handler address and flush the instruction cache. `m68k_setup_user_interrupt()` records the first external vector, assigns default handlers to a contiguous user IRQ range, writes the assembler vector offset fixup, and flushes I-cache. When an IRQ is started, the corresponding vector table entry becomes `auto_inthandler` or `user_inthandler`; shutdown restores `bad_inthandler`.

## State and Persistence Behavior

Persistent state includes `m68k_first_user_vec`, vector-table entries, default IRQ chip associations, and runtime `irq_err_count` increments through `handle_badint()`. The instruction stream is modified through the fixup arrays, making `flush_icache()` required after writes.

## Dependencies and Integration Points

This file depends on `vectors[]`, low-level entry handlers from m68k assembly, generic IRQ APIs, and machine hooks from `<asm/machdep.h>`. Q40 canonicalizes IRQ 11 to 10 for compatibility. `irq.c` provides `do_IRQ()` and the shared `irq_err_count` displayed in `/proc/interrupts`.

## Risks and Edge Cases

Incorrect user-vector base or count can index the vector table incorrectly; the code defends only with `BUG_ON(IRQ_USER + cnt > NR_IRQS)`. Fixup writes without an I-cache flush would keep old branch targets. Starting a user IRQ before `m68k_setup_user_interrupt()` has set `m68k_first_user_vec` can install a handler in the wrong vector slot. `handle_badint()` only warns, so repeated unexpected interrupts can flood logs while continuing to run.

## Test Signals

Build and boot with each platform IRQ controller, inspect `/proc/interrupts` for autovector/user IRQs, request and free IRQs while checking vector entries transition between real handlers and `bad_inthandler`, and confirm Q40 IRQ 11 canonicalizes to 10.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/ints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/ints.h -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/ints.h

## Purpose

`ints.h` is a tiny private header for m68k interrupt handling declarations. It gives assembly or sibling C files a typed declaration for the unexpected-interrupt handler without exposing the implementation details of `ints.c`.

## Important APIs, Types, and Functions

The header forward-declares `struct pt_regs` and declares `asmlinkage void handle_badint(struct pt_regs *regs);`. The `asmlinkage` qualifier preserves the calling convention expected by low-level trap/interrupt entry code.

## Control Flow

There is no executable control flow. Inclusion establishes the compile-time contract that an interrupt frame pointer will be passed to `handle_badint()`.

## State and Persistence Behavior

The header owns no state. Runtime state changes happen in `ints.c`, where `handle_badint()` increments `irq_err_count` and logs the vector.

## Dependencies and Integration Points

It depends only on `<linux/linkage.h>` for `asmlinkage`. It is included by `ints.c` and indirectly aligns with vector setup in `vectors.c` and interrupt entry assembly.

## Risks and Edge Cases

The risk is declaration drift. If low-level entry code or `ints.c` changes the handler signature without updating this header, the mismatch could break stack/register interpretation at interrupt time.

## Test Signals

Normal compile coverage is sufficient. Runtime evidence is generated by intentionally leaving a vector as `bad_inthandler` and observing `handle_badint()` warn with the expected `pt_regs->vector`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/ints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/irq.c

## Purpose

`irq.c` is the common IRQ entry shim and interrupt accounting support for m68k. It converts low-level architecture interrupt entry into generic Linux IRQ handling and provides the architecture-specific `/proc/interrupts` error line.

## Important APIs, Types, and Functions

`asmlinkage void do_IRQ(int irq, struct pt_regs *regs)` wraps `generic_handle_irq()`. `atomic_t irq_err_count` counts unexpected or spurious interrupts. `int arch_show_interrupts(struct seq_file *p, int prec)` prints the `ERR` line.

## Control Flow

The low-level interrupt path calls `do_IRQ()` with a decoded IRQ number and register frame. `do_IRQ()` installs `regs` through `set_irq_regs()`, calls `irq_enter()`, dispatches to the generic handler with `generic_handle_irq(irq)`, calls `irq_exit()`, and restores the previous IRQ register context.

## State and Persistence Behavior

This file persists only the global atomic `irq_err_count`. Per-CPU IRQ context state is temporarily swapped around each interrupt by `set_irq_regs()`.

## Dependencies and Integration Points

It depends on generic IRQ accounting and dispatch APIs, `struct pt_regs` from `<asm/traps.h>`, and `ints.c::handle_badint()` for incrementing `irq_err_count`. `/proc/interrupts` calls `arch_show_interrupts()` through generic seq-file code.

## Risks and Edge Cases

If low-level entry passes an out-of-range IRQ, generic IRQ code will handle the error path but the architecture shim has no local range check. Missing `set_irq_regs()` restoration would confuse nested interrupt diagnostics; this implementation restores unconditionally after `irq_exit()`.

## Test Signals

Interrupt-heavy boot, timer IRQ delivery, nested IRQ tracing, and `/proc/interrupts` should show normal device counts plus a stable `ERR` line. Triggering a bad vector should increment `irq_err_count`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/machine_kexec.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/machine_kexec.c

## Purpose

`machine_kexec.c` implements the m68k architecture handoff for `kexec`, copying a small physical relocation stub into the control page, disabling interruptions, flushing caches, and jumping to the relocation code with enough CPU/MMU state to disable the old address space and start the new kernel.

## Important APIs, Types, and Functions

The standard architecture hooks are `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_shutdown()`, `machine_crash_shutdown()`, and `machine_kexec()`. `relocate_kernel_t` is the no-return function type matching `relocate_new_kernel` from `relocate_kernel.S`.

## Control Flow

Prepare, cleanup, shutdown, and crash shutdown are no-ops. The real path in `machine_kexec()` gets the virtual address of `image->control_code_page`, copies `relocate_new_kernel` through `relocate_new_kernel_size`, disables local interrupts, logs `image->start`, flushes all caches, combines `m68k_cputype` and `m68k_mmutype` into `cpu_mmu_flags`, and calls the control-page stub with the relocation list head, entry point, and CPU/MMU flags.

## State and Persistence Behavior

The function mutates the control code page contents and CPU interrupt/cache state. It does not persist kernel data structures because control should never return. The flags passed to the stub encode current hardware features so the assembly can safely disable MMU/cache state.

## Dependencies and Integration Points

It depends on `relocate_kernel.S`, `<linux/kexec.h>` image layout, `page_address()`, `__flush_cache_all()`, and setup globals `m68k_cputype`/`m68k_mmutype`. It integrates with generic kexec core through the architecture hook names.

## Risks and Edge Cases

The relocation stub must fit in the control code page and must be cache coherent after the copy. If the CPU/MMU flag packing drifts from `relocate_kernel.S` expectations, the stub may take the wrong MMU-disable path. The no-op crash shutdown means platform devices are not quiesced here; crash-kexec depends on earlier generic and platform behavior.

## Test Signals

`kexec -l` followed by `kexec -e` should reach the new kernel entry on 030/040/060-capable configurations. Instrumentation should show the copied stub size below one page, interrupts disabled before jump, and no stale instruction cache execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/machine_kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/module.c

## Purpose

`module.c` provides m68k-specific relocation and fixup support for loadable modules. It applies ELF relocation records for module sections and patches architecture fixup records embedded by m68k assembly/C code.

## Important APIs, Types, and Functions

Under `CONFIG_MODULES`, `apply_relocate()` handles `Elf32_Rel`, `apply_relocate_add()` handles `Elf32_Rela`, and `module_finalize()` calls `module_fixup()`. `module_fixup(struct module *mod, struct m68k_fixup_info *start, struct m68k_fixup_info *end)` handles entries such as `m68k_fixup_memoffset` and `m68k_fixup_vnode_shift` when `CONFIG_MMU` is set.

## Control Flow

For each relocation record, the code computes the target location from the relocated section plus `r_offset`, resolves the symbol through `symindex`, and switches on `ELF32_R_TYPE`. `R_68K_32` adds or assigns the absolute symbol value, while `R_68K_PC32` adds or assigns a PC-relative value subtracting the relocation location. Unknown relocation types log the module name and return `-ENOEXEC`. Finalization walks the module fixup section and patches stored addresses with `m68k_memoffset` or `m68k_virt_to_node_shift`.

## State and Persistence Behavior

Relocations permanently mutate the module's loaded memory image. Fixups write architecture constants into addresses recorded by `.m68k_fixup` producers. No persistent storage is used.

## Dependencies and Integration Points

It depends on generic module loader section preparation, ELF relocation constants, `struct module`, and m68k fixup metadata. `relocate_kernel.S` uses `.m68k_fixup` records for virtual-to-physical adjustments, and modules can use the same mechanism.

## Risks and Edge Cases

Only `R_68K_32` and `R_68K_PC32` are supported. A toolchain or module that emits other relocation types will fail load. Relocation location arithmetic casts to `uint32_t *`, so unaligned targets would be dangerous if emitted. `module_finalize()` assumes fixup range pointers are valid and ordered.

## Test Signals

Load and unload a simple m68k module with absolute and PC-relative references, check `dmesg` for unknown relocation errors, and inspect loaded module memory or symbols to verify fixup values match `m68k_memoffset` and virtual node shift expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/pcibios.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/pcibios.c

## Purpose

`pcibios.c` supplies the minimal m68k PCI BIOS hooks needed by the generic PCI core: resource alignment, device enablement, and bus fixups.

## Important APIs, Types, and Functions

`pcibios_align_resource()` adjusts I/O and memory resource placement. `pcibios_enable_device()` enables assigned resources and sets bridge command bits. `pcibios_fixup_bus()` writes cache line size and latency timer defaults for devices on a bus.

## Control Flow

For I/O resources, `pcibios_align_resource()` avoids addresses whose low 10 bits fall in mirrored ISA ranges by rounding starts with bits `0x300` up to the next `0x400` boundary. Memory resources delegate to `pci_align_resource()`. `pcibios_enable_device()` first calls `pci_enable_resources()`. For PCI bridges it reads `PCI_COMMAND`, ensures I/O and memory decode bits are enabled, logs the change, and writes the new command word. Bus fixup iterates all devices and sets `PCI_CACHE_LINE_SIZE` to 8 and `PCI_LATENCY_TIMER` to 32.

## State and Persistence Behavior

The file persists configuration through PCI config-space writes. It does not allocate memory or keep private state.

## Dependencies and Integration Points

It integrates with generic PCI probing and resource allocation. It depends on `struct pci_dev`, `struct pci_bus`, PCI config accessors, and resource flags from `<linux/pci.h>` and `<linux/ioport.h>`.

## Risks and Edge Cases

`pcibios_enable_device()` declares `u16 cmd, newcmd;` but does not explicitly initialize `newcmd` from `cmd` before ORing bridge bits, which is a latent correctness risk if this source is compiled as shown. Resource alignment follows legacy ISA mirroring assumptions and may overconstrain unusual host bridges. Bus fixups apply uniform latency/cacheline values to all devices.

## Test Signals

PCI enumeration should allocate I/O resources outside mirrored low-bit windows, bridges should show I/O and memory decode enabled in config space, and no compiler warning should report use of uninitialized `newcmd`. Device probes behind bridges are the practical smoke test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/pcibios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/process.c

## Purpose

`process.c` implements architecture-specific process, idle, restart, fork, register dump, FPU core dump, and wait-channel behavior for m68k.

## Important APIs, Types, and Functions

Key functions are `arch_cpu_idle()`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, `show_regs()`, `flush_thread()`, `m68k_clone()`, `m68k_clone3()`, `copy_thread()`, `elf_core_copy_task_fpregs()`, and `__get_wchan()`. It exports `pm_power_off` and references return stubs `ret_from_fork` and `ret_from_kernel_thread`.

## Control Flow

Idle executes the m68k `stop` instruction with Atari-specific interrupt masking when required. Restart/halt delegate to machine hooks and then spin. `m68k_clone()` builds `kernel_clone_args` from pt_regs because m68k syscall arguments live in registers/stack in an architecture-specific arrangement; `m68k_clone3()` forwards to generic `sys_clone3()`. `copy_thread()` lays out a `fork_frame` at the top of the child kernel stack, either initializing a kernel-thread frame or copying the parent's switch stack and pt_regs, setting child return value `d0 = 0`, child USP, TLS, and optional FPU state. Core dump support saves or converts FPU state depending on emulator, ColdFire, or classic FPU.

## State and Persistence Behavior

The file mutates `task_struct->thread` fields such as `ksp`, `esp0`, `usp`, `fc`, FPU arrays, and thread-info TLS. It also interacts with machine hooks `mach_reset` and `mach_halt`. No file-system persistence exists.

## Dependencies and Integration Points

It depends on scheduler task stack layout, `struct switch_stack`, `struct pt_regs`, FPU feature macros, generic `kernel_clone()`, reboot hooks, and signal/ptrace expectations for saved register layout. `process.h` declares the clone wrappers used by syscall entry code.

## Risks and Edge Cases

Fork frame layout must stay synchronized with entry assembly, ptrace register offsets, and signal stack manipulation. FPU save/restore differs by emulator, ColdFire, 060, and 020/030/040; a wrong format check can corrupt user FPU context or core dumps. `__get_wchan()` assumes frame-pointer chains and stack bounds, so compiler or ABI changes can reduce reliability.

## Test Signals

Exercise `fork`, `clone`, `clone3`, kernel threads, TLS setup, core dumps with and without FPU use, and restart/halt/poweroff hooks. `show_regs()` output after forced traps should match the low-level pt_regs layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/process.h -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/process.h

## Purpose

`process.h` is the private declaration header for m68k process-related syscall wrappers.

## Important APIs, Types, and Functions

It forward-declares `struct pt_regs` and declares `asmlinkage int m68k_clone(struct pt_regs *regs);` plus `asmlinkage int m68k_clone3(struct pt_regs *regs);`.

## Control Flow

There is no executable control flow. The declarations let syscall entry code and `process.c` agree that clone wrappers receive a register-frame pointer.

## State and Persistence Behavior

The header owns no state. Runtime state changes happen in `process.c` through child stack/thread initialization.

## Dependencies and Integration Points

It depends on `<linux/linkage.h>` and on entry/syscall code that routes clone syscalls to these wrappers because m68k cannot directly use generic argument extraction.

## Risks and Edge Cases

If clone argument extraction moves out of `process.c`, this header must track the calling convention. A mismatch would be severe because the wrapper interprets saved registers as syscall arguments.

## Test Signals

Compile-time coverage plus runtime `clone`/`clone3` tests through libc or syscall tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/process.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/ptrace.c

## Purpose

`ptrace.c` implements m68k register access, single-step controls, syscall tracing hooks, and minimal ELF-FDPIC regset support for debuggers and core dumps.

## Important APIs, Types, and Functions

The file defines `ptrace_disable()`, `user_enable_single_step()`, `user_enable_block_step()` on MMU builds, `user_disable_single_step()`, `arch_ptrace()`, `syscall_trace_enter()`, `syscall_trace_leave()`, and optional `task_user_regset_view()`. Internal helpers `get_reg()` and `put_reg()` use `regoff[]` offsets into `pt_regs` and `switch_stack`, with `PT_USP` handled through `task->thread.usp`.

## Control Flow

`arch_ptrace()` handles legacy m68k requests: `PTRACE_PEEKUSR`, `PTRACE_POKEUSR`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, FPU register get/set, and `PTRACE_GET_THREAD_AREA`, then delegates unknown requests to `ptrace_request()`. It masks writable status-register bits with `SR_MASK` so user-space cannot set privileged SR state. Single-step control sets or clears trace bits `T1_BIT`/`T0_BIT` and `TIF_DELAYED_TRACE`. Syscall tracing reports entry before seccomp, lets `secure_computing()` veto the syscall, and reports exit afterward.

## State and Persistence Behavior

The code reads and writes saved register frames in the traced task, `thread.usp`, `thread.fp`, and thread flags. It does not persist external state, but debugger writes directly affect future execution of the traced task.

## Dependencies and Integration Points

It depends on exact process stack layout from `process.c` and entry assembly, status-register semantics, FPU emulator internal format, seccomp, generic ptrace, and ELF regset infrastructure. `ptrace.h` declares the syscall trace hooks for assembly.

## Risks and Edge Cases

Offsets must remain synchronized with `struct pt_regs` and `struct switch_stack`. `stkadj` handling for SR/PC is necessary for nonstandard exception frames; missing it would expose or overwrite the wrong return state. FPU emulator long-double conversion is ABI-sensitive. Seccomp and ptrace ordering must remain compatible with generic expectations.

## Test Signals

Run debugger tests for reading/writing all GPRs, SR masking, PC changes, single-step and block-step traps, syscall trace/seccomp interactions, FPU register access, TLS get, and FDPIC core dump note generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/ptrace.h

## Purpose

`ptrace.h` is the private declaration header for m68k syscall tracing hooks used by low-level entry code.

## Important APIs, Types, and Functions

It declares `asmlinkage int syscall_trace_enter(void);` and `asmlinkage void syscall_trace_leave(void);`.

## Control Flow

There is no in-file control flow. Entry assembly calls `syscall_trace_enter()` before executing a syscall when tracing/seccomp work is pending, and calls `syscall_trace_leave()` on the way out.

## State and Persistence Behavior

The header owns no state. The declared functions operate on current task flags, pt_regs, ptrace, and seccomp state in `ptrace.c`.

## Dependencies and Integration Points

It depends on `<linux/linkage.h>` for the assembly-compatible calling convention. It integrates with `entry.S` and generic syscall tracing.

## Risks and Edge Cases

Changing return type or calling convention without matching entry assembly would corrupt syscall dispatch, especially because `syscall_trace_enter()` returns a value used to skip or continue syscall execution.

## Test Signals

Compile coverage and syscall tracing tests under `strace`, ptrace, and seccomp are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/relocate_kernel.S -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/relocate_kernel.S

## Purpose

`relocate_kernel.S` is the no-return physical-mode kexec relocation stub copied into the kexec control page by `machine_kexec.c`. It disables the current MMU mapping, copies destination pages according to the kimage indirection list, flushes caches, and jumps to the new kernel entry.

## Important APIs, Types, and Functions

The exported symbols are `relocate_new_kernel` and `relocate_new_kernel_size`. Inputs are stack arguments: relocation list pointer, new kernel start address, and packed `cpu_mmu_flags`. The file emits `.m68k_fixup` records to patch virtual-to-physical offsets for internal branch targets.

## Control Flow

The stub tests MMU flags for 68851/68030, 68040, or 68060 support. For 030-class MMUs it clears the enable bit in TC and jumps to the physical copy routine. For 040/060 it sets a temporary transparent mapping for its physical code, disables TC and transparent registers, then falls into copy. The copy loop follows kexec entries: indirection entries replace the pointer, destination entries set `a2`, source entries copy one page from `a3` to `a2`, and done entries break to cache flush. Cache flushing then uses CACR for 020/030 or `cpusha/cinva` for 040/060 before jumping to `start`.

## State and Persistence Behavior

The stub mutates CPU MMU/cache registers and destination physical memory pages. It consumes the kexec relocation list but does not return or preserve old kernel state.

## Dependencies and Integration Points

It depends on kexec indirection entry bit definitions, `PAGE_MASK`, `PAGE_SIZE`, m68k CPU/MMU boot flags, and module/fixup processing for `.m68k_fixup`. `machine_kexec.c` copies it into executable control memory and passes flags.

## Risks and Edge Cases

Wrong CPU/MMU flags can leave the old MMU enabled or disable it through the wrong instruction sequence. The copy loop assumes page-aligned source and destination entries and one-page copies. Cache flushing is essential before executing the new kernel; missing a CPU path can boot stale code.

## Test Signals

Successful kexec handoff on 030 and 040/060 builds, inspection of `relocate_new_kernel_size`, and trace or emulator checks that TC and transparent registers are cleared before jumping to the new entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/relocate_kernel.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/setup.c

## Purpose

`setup.c` is a configuration dispatcher wrapper. It includes either the MMU or no-MMU implementation of m68k setup and optionally exports the m68k beep hook.

## Important APIs, Types, and Functions

When `CONFIG_MMU` is enabled it includes `setup_mm.c`; otherwise it includes `setup_no.c`. Under `CONFIG_INPUT_M68K_BEEP`, it defines and exports `void (*mach_beep)(unsigned int, unsigned int);`.

## Control Flow

The file itself has no function bodies beyond the optional global hook. The included file supplies `setup_arch()`, `cpuinfo_op`, and related setup helpers.

## State and Persistence Behavior

The included setup implementation owns most boot state. The optional `mach_beep` function pointer persists as a machine hook for input/audio drivers.

## Dependencies and Integration Points

It depends on Kconfig selecting exactly one setup implementation. The beep hook integrates with m68k input/beeper support and platform code that may assign the function pointer.

## Risks and Edge Cases

Including `.c` files means this wrapper determines the translation-unit context. Duplicate definitions or missing config guards in the included implementations would surface here. The `mach_beep` hook is only present when the input beep option is enabled, so callers must be Kconfig-aligned.

## Test Signals

Build one MMU and one no-MMU m68k configuration. With `CONFIG_INPUT_M68K_BEEP`, confirm `mach_beep` is exported and can be assigned by platform code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/setup_mm.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/setup_mm.c

## Purpose

`setup_mm.c` is the architecture setup implementation for MMU-capable m68k. It parses bootinfo, records CPU/FPU/MMU/memory metadata, configures the selected machine family, initializes memblock/paging, exposes `/proc/cpuinfo` and optional `/proc/hardware`, and provides NVRAM operation routing.

## Important APIs, Types, and Functions

Global exports include `m68k_machtype`, `m68k_cputype`, `m68k_mmutype`, `vme_brdtype`, `m68k_is040or060`, `m68k_num_memory`, `m68k_realnum_memory`, and `m68k_memory`. Hooks include `mach_sched_init`, `mach_init_IRQ`, `mach_get_model`, `mach_get_hardware_list`, `mach_reset`, `mach_halt`, `mach_heartbeat`, and `mach_l2_flush`. Major functions are `m68k_parse_bootinfo()`, `setup_arch()`, `show_cpuinfo()`, `proc_hardware_init()`, `arch_cpu_finalize_init()`, and the NVRAM accessors behind `arch_nvram_ops`.

## Control Flow

`setup_arch()` parses bootinfo from `_end` unless on ColdFire, sets the 040/060 marker, clears FPU state when available, applies a 68060 PCR erratum workaround, initializes `init_mm`, appends U-Boot command-line data, initializes jump labels and early params, dispatches to the platform `config_*()` routine based on `m68k_machtype`, reserves initrd memory, calls `paging_init()`, maps initrd virtual addresses, initializes natfeat, reserves Atari ST-RAM, initializes Sun3x DVMA, and sets ISA compatibility metadata for supported boards.

`m68k_parse_bootinfo()` walks big-endian bootinfo records, stores memory chunks, ramdisk metadata, command line, and RNG seed data, delegates unknown records to machine parsers, saves bootinfo for later inspection, and optionally collapses to a single memory chunk.

## State and Persistence Behavior

This file owns persistent boot metadata, memory chunk arrays, platform hook pointers, command line storage, optional initrd metadata, and NVRAM operations. RNG seed bootinfo is zeroed after `add_bootloader_randomness()` to preserve forward secrecy and prevent kexec reuse.

## Dependencies and Integration Points

It depends on `head.S` for early machine/CPU globals and `availmem`, platform `config_*()` and parse helpers, memblock/paging initialization, initrd, natfeat, Atari ST-RAM, Sun3x DVMA, `/proc` seq operations, and Mac/Atari NVRAM backends.

## Risks and Edge Cases

Malformed bootinfo sizes can mis-walk records. Too many memory chunks are truncated to `NUM_MEMINFO`, and `CONFIG_SINGLE_MEMORY_CHUNK` discards all but the first. Machine dispatch panics if `m68k_machtype` lacks a configured handler. FPU type is trusted from bootloader metadata with a FIXME noting possible confusion. NVRAM operations return board-specific errors when called on unsupported machines.

## Test Signals

Boot logs should show no unknown critical bootinfo, correct `/proc/cpuinfo`, correct memory totals, reserved initrd ranges, platform config hook execution, and valid `/proc/hardware` when enabled. Check RNG seed zeroing across kexec and NVRAM read/write behavior on Mac and Atari configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/setup_mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/setup_no.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/setup_no.c

## Purpose

`setup_no.c` is the no-MMU m68k/uClinux architecture setup implementation. It establishes the flat memory model, collects board and U-Boot command-line data, initializes memblock and paging, and exposes no-MMU CPU information.

## Important APIs, Types, and Functions

It defines exported `memory_start` and `memory_end`, `command_line`, machine hooks `mach_sched_init`, `mach_reset`, and `mach_halt`, `setup_arch()`, `show_cpuinfo()`, and `cpuinfo_op`. CPU name and instruction timing are selected through Kconfig macros such as `CONFIG_M68328`, `CONFIG_M68VZ328`, and `CONFIG_COLDFIRE`.

## Control Flow

`setup_arch()` aligns `_ramstart` into `memory_start`, records `_ramend`, initializes `init_mm`, calls `config_BSP()` to let the board fill the command line and hooks, applies built-in boot parameters, appends U-Boot command-line/initrd data, prints CPU/board support messages, adds the RAM range to memblock, reserves kernel/ROMFS-used memory, exports the command line to generic boot state, sets PFN limits, reserves a U-Boot initrd when valid, and calls `paging_init()`.

## State and Persistence Behavior

Persistent state includes the flat memory bounds, command line, memblock reservations, PFN bounds, machine hooks, and optional initrd range. There is no MMU state and no bootinfo parser in this file.

## Dependencies and Integration Points

It depends on linker symbols `_ramstart`, `_ramend`, `_rambase`, `_stext`, `_etext`, `_sdata`, `_edata`, and `__bss_*`, board `config_BSP()`, `process_uboot_commandline()`, memblock, `paging_init()`, and generic `/proc/cpuinfo` seq support.

## Risks and Edge Cases

The flat memory assumptions are sensitive to linker symbols and ROMFS placement. U-Boot initrd is reserved only when inside `memory_end`; invalid ranges are silently ignored. Command-line concatenation depends on bounded copies and available buffer space. Platform hooks must be installed by `config_BSP()` before timers and reboot paths use them.

## Test Signals

Boot a no-MMU target with and without U-Boot initrd, confirm memory ranges in debug logs, verify `/proc/cpuinfo` clock/BogoMips calculations, and ensure board reset/halt/timer hooks are installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/setup_no.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/signal.c

## Purpose

`signal.c` implements m68k signal delivery and return, including legacy and realtime signal frames, exception-frame reshaping, FPU state save/restore, syscall restart handling, and user-mode resume work.

## Important APIs, Types, and Functions

Externally visible functions are `fixup_exception()` on MMU builds, `berr_040cleanup()` through trap integration, `do_sigreturn()`, `do_rt_sigreturn()`, and `do_notify_resume()`. Important internal types are `struct sigframe` and `struct rt_sigframe`. Helpers include `restore_fpu_state()`, `rt_restore_fpu_state()`, `save_fpu_state()`, `rt_save_fpu_state()`, `mangle_kernel_stack()`, `restore_sigcontext()`, `rt_restore_ucontext()`, `setup_sigcontext()`, `rt_setup_ucontext()`, `get_sigframe()`, `setup_frame()`, `setup_rt_frame()`, `handle_restart()`, and `handle_signal()`.

## Control Flow

On delivery, `do_notify_resume()` calls `do_signal()` when pending signal work exists. `do_signal()` handles syscall restart decisions, obtains a `ksignal`, and calls `handle_signal()`. `handle_signal()` builds either a legacy or realtime user frame on the normal or alt signal stack, copies any extra exception-frame words, stores register/FPU/sigmask/ucontext state, writes a small return trampoline or no-MMU return pointer, flushes the trampoline cache lines, adjusts `regs->stkadj` for complex frames, then sets USP and PC to invoke the user handler.

On signal return, `do_sigreturn()` and `do_rt_sigreturn()` validate and copy user frames, restore the blocked signal mask, restore GPRs, SR user bits, PC, USP, FPU state, altstack state, and call `mangle_kernel_stack()` to rebuild the hardware exception frame before returning to entry assembly.

## State and Persistence Behavior

The file mutates current task blocked signal mask, restart block, pt_regs, switch_stack, user stack contents, FPU hardware state, `current->thread.esp0`, and m68k exception-frame adjustment. It also clears or restores FPU state using CPU-specific instructions.

## Dependencies and Integration Points

It depends on entry assembly return paths, `struct frame` from traps, `traps.c::berr_040cleanup()`, exception table lookup, FPU emulator/hardware formats, ucontext ABI, cache flushing, altstack helpers, and generic signal core. `signal.h` exposes the entry points.

## Risks and Edge Cases

The ABI is highly sensitive: `siginfo_t` offsets are guarded by `BUILD_BUG_ON`, and frame sizes vary by CPU and exception format. User-supplied sigreturn frames can try to create invalid frame formats; `mangle_kernel_stack()` rejects negative/unknown sizes. Cache flushing is required because signal return code is written onto the user stack. Nested signals with adjusted exception frames rely on subtle `stkadj` behavior. FPU frame format validation differs for 68881/68882/040/060/ColdFire.

## Test Signals

Run signal ABI tests for legacy and realtime handlers, altstack, nested signals, syscall restart, ptrace single-step plus signals, sigreturn tampering, FPU state preservation, 040 bus-error writeback cleanup, and no-MMU return stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/signal.h -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/signal.h

## Purpose

`signal.h` is the private header that declares m68k signal resume and return entry points for assembly and sibling C files.

## Important APIs, Types, and Functions

It declares `do_notify_resume(struct pt_regs *regs)`, `do_sigreturn(struct pt_regs *regs, struct switch_stack *sw)`, and `do_rt_sigreturn(struct pt_regs *regs, struct switch_stack *sw)` with `asmlinkage`.

## Control Flow

There is no in-header control flow. The declared functions are reached from low-level return-to-user and signal-return syscall paths.

## State and Persistence Behavior

No state is owned by the header. The implementation in `signal.c` mutates current task signal state, saved registers, FPU state, and user stack frames.

## Dependencies and Integration Points

It depends on `<linux/linkage.h>` and on declarations of `struct pt_regs` and `struct switch_stack` being visible at use sites. It connects entry assembly to `signal.c`.

## Risks and Edge Cases

Calling convention drift would corrupt the stack around signal return, because `do_sigreturn()` returns an adjusted switch-stack pointer.

## Test Signals

Signal delivery and return tests, especially nested frame-size cases, validate the contract represented by these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/sun3-head.S -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/sun3-head.S

## Purpose

`sun3-head.S` is the Sun-3-specific bootstrap for the older Sun3 MMU/page-size model. It replaces the standard 4 KiB page-table startup with Sun3 context/segment-map initialization and then enters the common kernel path.

## Important APIs, Types, and Functions

The file exports `_stext`, `_start`, `kernel_pg_dir`, `swapper_pg_dir`, `pg0`, `kernel_pmd_table`, `availmem`, `m68k_pgtable_cachemode`, `bootup_user_stack`, `bootup_kernel_stack`, and `kpt`. It uses constants from `<asm/contregs.h>` and `<asm/sun3-head.h>` such as context registers, segment map entries, and control-space function codes.

## Control Flow

Startup disables interrupts, sets source/destination function codes to control space, forces context zero, disables caches, builds the early Sun3 mapping structures, initializes kernel/user boot stacks, records initial available memory, and transfers to common C setup after the Sun3 MMU state is usable. The assembly uses 8 KiB page constants and Sun3 invalid PMEG handling rather than the normal 4 KiB 68030/040 table walkers.

## State and Persistence Behavior

It statically reserves early tables in the image and persists `availmem`, page-directory/table symbols, stack symbols, and cache-mode state. It programs Sun3 control registers and segment mappings that remain active into C setup.

## Dependencies and Integration Points

It depends on Sun3-specific MMU/control-register headers, entry offsets, linker placement, and common setup code that expects `kernel_pg_dir`/`availmem` symbols. It is selected by the Sun3 build instead of the generic `head.S` path.

## Risks and Edge Cases

Sun3 uses 8 KiB pages and PMEG/context hardware, so generic MMU assumptions cannot be applied blindly. Static table reservations marked with comments as BSS candidates must remain correctly linked and aligned. Incorrect control function-code setup can make early MMU register accesses hit normal memory or fault.

## Test Signals

Sun3 boot should reach C setup, show valid memory and MMU type in `/proc/cpuinfo`, and survive early page faults. Emulator traces should show context zero and segment maps programmed before enabling normal execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/sun3-head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/sys_m68k.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/sys_m68k.c

## Purpose

`sys_m68k.c` implements m68k-specific syscalls and syscall variants with nonstandard calling conventions: `mmap2`, cache flushing, atomic compare-exchange, page size, thread pointer, and a uniprocessor atomic barrier.

## Important APIs, Types, and Functions

Important exported syscall entry points are `sys_mmap2()`, `sys_cacheflush()`, `sys_atomic_cmpxchg_32()`, `sys_getpagesize()`, `sys_get_thread_area()`, `sys_set_thread_area()`, and `sys_atomic_barrier()`. Internal MMU helpers include `cache_flush_040()`, `cache_flush_060()`, `virt_to_phys_040`, and `virt_to_phys_060`.

## Control Flow

`sys_mmap2()` forwards to `ksys_mmap_pgoff()` while noting Sun3 page-size complications. On MMU builds, `sys_cacheflush()` validates scope/cache bits, requires `CAP_SYS_ADMIN` for whole-cache flush, verifies non-global address ranges against the current VMA, then selects 020/030 CACR flush behavior or 040/060 physical-address `cpush*` loops. Long requested line/page flushes are promoted to broader scopes to prevent excessive work. On no-MMU builds it simply calls `flush_cache_all()`.

`sys_atomic_cmpxchg_32()` on MMU builds manually walks page tables under `mmap_read_lock()`, verifies the target PTE is present, dirty, and writable, then performs get/put user operations under the PTE lock. If the page is absent or copy-on-write, it synthesizes a write page fault and retries. No-MMU builds directly compare and update under the mmap read lock.

## State and Persistence Behavior

Cache flush syscalls mutate CPU cache state. Atomic compare-exchange mutates user memory when the old value matches and can fault pages into writable state. Thread-area syscalls read/write `current_thread_info()->tp_value`.

## Dependencies and Integration Points

The file depends on cache-control ABI constants, m68k CPU feature macros, page-table APIs, `do_page_fault()`, generic memory mapping, user access helpers, and syscall table generation.

## Risks and Edge Cases

`sys_cacheflush()` must avoid overflowing `addr + len` and must not flush arbitrary process memory without VMA validation. Physical address translation can skip unmapped pages, so partial ranges may be no-ops. The atomic syscall constructs a `pt_regs *` from syscall arguments to call `do_page_fault()`, a delicate ABI dependency. No-MMU direct `*mem` access assumes flat valid user memory.

## Test Signals

Run cacheflush ABI tests for line/page/all scopes, permission checks for whole-cache flush, mmaped JIT/self-modifying code tests, COW atomic compare-exchange tests, invalid pointer fault tests, and TLS get/set tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/sys_m68k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/syscalls/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/syscalls/Makefile

## Purpose

This Makefile generates m68k syscall header artifacts from `syscall.tbl` during the kernel build.

## Important APIs, Types, and Functions

It defines output roots `arch/$(SRCARCH)/include/generated/uapi/asm` and `arch/$(SRCARCH)/include/generated/asm`, input `$(src)/syscall.tbl`, and generator scripts `scripts/syscallhdr.sh` and `scripts/syscalltbl.sh`. Targets are `unistd_32.h` and `syscall_table.h`.

## Control Flow

The Makefile creates generated include directories with `$(shell mkdir -p ...)`. `$(uapi)/unistd_32.h` is produced by `syscallhdr.sh --emit-nr`, while `$(kapi)/syscall_table.h` is produced by `syscalltbl.sh`. The `all` target depends on both generated files and otherwise does nothing.

## State and Persistence Behavior

It writes generated headers under the kernel build tree. It does not affect runtime state.

## Dependencies and Integration Points

It depends on Kbuild `if_changed`, `FORCE`, `CONFIG_SHELL`, `srctree`, and the m68k `syscall.tbl`. `syscalltable.S` includes `<asm/syscall_table.h>`, and UAPI consumers include the generated syscall number header.

## Risks and Edge Cases

Directory creation at parse time can surprise highly constrained builds, but is common in syscall Makefiles. If `syscall.tbl` or generator script arguments drift, the table and syscall numbers can diverge from entry code expectations.

## Test Signals

`make arch/m68k/kernel/syscalls/` or a full m68k build should regenerate both headers. Diffs in generated headers should match intentional `syscall.tbl` changes only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/syscalltable.S -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/syscalltable.S

## Purpose

`syscalltable.S` defines the m68k `sys_call_table` object consumed by syscall entry code.

## Important APIs, Types, and Functions

It exports `ENTRY(sys_call_table)` in `.rodata`. The macro `__SYSCALL(nr, entry) .long entry` converts generated syscall-table include rows into 32-bit function pointers. On no-MMU builds it aliases `sys_mmap2` to `sys_mmap_pgoff`.

## Control Flow

There is no runtime control flow in this file. At assembly time it includes `<asm/syscall_table.h>`, generated from `syscall.tbl`, and emits one longword per syscall entry.

## State and Persistence Behavior

The table is read-only runtime dispatch state. Syscall entry assembly indexes it to call C syscall handlers.

## Dependencies and Integration Points

It depends on `kernel/syscalls/Makefile` generation of `asm/syscall_table.h`, syscall wrapper names from kernel code, and entry assembly that knows table element size and numbering.

## Risks and Edge Cases

Generated table/header mismatch would dispatch wrong syscalls. The no-MMU `sys_mmap2` alias must stay aligned with the no-MMU implementation in `sys_m68k.c`.

## Test Signals

Build should fail on missing syscall symbols. Runtime syscall ABI smoke tests for common calls, `mmap2`, `cacheflush`, and thread-area syscalls verify table alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/syscalltable.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/time.c

## Purpose

`time.c` supplies m68k-specific time initialization, machine RTC hook plumbing, optional generic RTC device registration, heartbeat LED behavior, and entropy hook export.

## Important APIs, Types, and Functions

It defines/export `mach_random_get_entropy`, `mach_hwclk`, `mach_get_rtc_pll`, and `mach_set_rtc_pll` where configured. Functions include `timer_heartbeat()`, `read_persistent_clock64()`, generic RTC callbacks `rtc_generic_get_time()`, `rtc_generic_set_time()`, `rtc_ioctl()`, `rtc_init()`, and `time_init()`.

## Control Flow

`time_init()` calls `mach_sched_init()`, which platform setup installed. `timer_heartbeat()` toggles `mach_heartbeat()` in a load-dependent double-pulse pattern. Classic m68k/Sun3 builds use `mach_hwclk()` to read persistent time or implement a `rtc-generic` platform device. RTC ioctl supports PLL get/set through machine hooks and requires `CAP_SYS_TIME` for setting. `rtc_init()` registers the generic RTC only if `mach_hwclk` exists.

## State and Persistence Behavior

The file owns machine hook pointers and heartbeat static counters. RTC set and PLL operations can persist into hardware NVRAM/RTC depending on platform implementation. `mach_random_get_entropy` exposes optional hardware entropy to other code.

## Dependencies and Integration Points

It depends on platform setup assigning scheduler, heartbeat, hardware clock, PLL, and entropy hooks. It integrates with generic RTC class, platform device registration, `/proc/loadavg` data via `avenrun`, and Linux timekeeping.

## Risks and Edge Cases

`time_init()` assumes `mach_sched_init` is non-null after setup; a missing platform hook will crash. RTC generic callbacks assume `mach_hwclk` remains valid. Heartbeat timing uses load average and static counters, so board LED callbacks must be cheap and IRQ-safe for timer context.

## Test Signals

Boot should initialize timer interrupts, `hwclock` or generic RTC reads should work when hooks exist, PLL ioctl should enforce permissions, and heartbeat LED pattern should track load without timer stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/traps.c

## Purpose

`traps.c` implements m68k exception and bus-error handling, CPU-specific page-fault decoding, 68040 writeback cleanup, diagnostic stack/register dumps, signal mapping for user traps, and fatal kernel trap handling.

## Important APIs, Types, and Functions

Externally visible functions include `buserr_c()`, `berr_040cleanup()`, `trap_c()`, `die_if_kernel()`, `set_esp0()`, `fpsp040_die()`, and optional `fpemu_signal()`. Important CPU-specific helpers are `access_error060()`, `probe040()`, `do_040writeback1()`, `do_040writebacks()`, `access_error040()`, `bus_error030()` or Sun3 variant, and `access_errorcf()` for ColdFire MMU. Diagnostic helpers include `show_registers()`, `show_stack()`, and `show_trace()`.

## Control Flow

`buserr_c()` records `esp0` for user frames, decodes ColdFire fault-status bits when applicable, then dispatches by exception frame format: 060 access error, 040 access error, 020/030 bus error, or fatal unknown format. Each CPU path computes fault address and error code, calls `do_page_fault()` when the fault is a recoverable mapping/protection event, or sends SIGBUS/SIGSEGV/SIGKILL and logs diagnostics for unrecoverable cases. 040 handling additionally processes pending writeback slots and can defer cleanup through signal delivery.

`trap_c()` handles non-bus traps. Supervisor traps try `fixup_exception()` on MMU builds, otherwise call `bad_super_trap()` and die. User traps map vectors to `SIGILL`, `SIGFPE`, `SIGBUS`, or `SIGTRAP` with detailed `si_code` and fault address selection based on frame format.

## State and Persistence Behavior

The code mutates current thread fault fields (`signo`, `faddr`, `esp0`), sends signals, performs TLB/cache operations, can rewrite 040 writeback frame slots, taints the kernel on fatal traps, and terminates tasks. It does not persist external data.

## Dependencies and Integration Points

It depends on `struct frame` layout, CPU/MMU feature macros, `do_page_fault()`, exception tables, TLB/cache helpers, signal APIs, FPU emulator/FPSP code, and entry assembly that calls `buserr_c()`/`trap_c()`. `traps.h` exposes functions used from assembly and signal code.

## Risks and Edge Cases

Exception frame formats are CPU-specific and dense. Wrong fault-address/error-code decoding can turn a recoverable page fault into a process kill or kernel oops. 040 writeback cleanup is subtle because user-space fault recovery and kernel exception fixups interact. Diagnostic code reads around PC and stack with no-fault helpers, but invalid frames can still reduce clarity.

## Test Signals

Page-fault tests for read/write/protection/COW, illegal instruction, divide by zero, breakpoint, single-step, kernel exception-table fixups, 040 writeback fault cases, 060 branch prediction/access errors, ColdFire TLB misses, and Sun3 demand mapping are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/traps.h -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/traps.h

## Purpose

`traps.h` is the private declaration header for trap and bus-error entry points shared between m68k assembly, signal code, and trap implementation.

## Important APIs, Types, and Functions

It forward-declares `struct frame` and declares `buserr_c()`, `fpemu_signal()`, `fpsp040_die()`, and `set_esp0()` with `asmlinkage`.

## Control Flow

There is no executable control flow. The header records the calling convention expected by low-level exception entry code and FPU support routines.

## State and Persistence Behavior

No state is owned here. The implementation mutates current thread trap state, signal state, and kernel diagnostic state.

## Dependencies and Integration Points

It depends on `<linux/linkage.h>`. It integrates `traps.c` with entry assembly, 040/060 FPU support packages, and signal frame cleanup.

## Risks and Edge Cases

Signature drift would corrupt exception handling. `struct frame` is opaque here, so users must include the real frame layout before dereferencing it.

## Test Signals

Build coverage plus runtime trap, bus error, FPU emulator, and signal-return tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/uboot.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/uboot.c

## Purpose

`uboot.c` extracts m68k U-Boot-passed command-line and initrd information from the initial stack and appends it to the kernel command-line buffer.

## Important APIs, Types, and Functions

The internal parser is `parse_uboot_commandline(char *commandp, int size)`. The exported init helper is `process_uboot_commandline(char *commandp, int size)`. It references external `_init_sp` and, when initrd support is enabled, writes `initrd_start`, `initrd_end`, and `ROOT_DEV`.

## Control Flow

`process_uboot_commandline()` finds the current end of the command buffer with `strnlen()`, appends one space when room remains, then calls `parse_uboot_commandline()` on the remaining buffer. The parser interprets `_init_sp` according to U-Boot's call convention, copies the command string if start/end pointers are nonzero, and records initrd bounds plus `Root_RAM0` when the initrd start/end pair is valid.

## State and Persistence Behavior

The file mutates the provided command buffer and global initrd/root-device state. It does not allocate memory. The parsed values persist into setup and initrd reservation.

## Dependencies and Integration Points

It depends on early assembly preserving `_init_sp`, U-Boot argument layout, setup code calling `process_uboot_commandline()`, and initrd/root device globals. Both MMU and no-MMU setup paths call it.

## Risks and Edge Cases

The parser trusts stack pointers supplied by firmware and assumes the referenced memory is still unmodified. `process_uboot_commandline()` writes `commandp[len - 1] = 0`; callers must pass a nonzero remaining size. Invalid initrd ranges are partially screened by start/end ordering here and by setup memory-bound checks later.

## Test Signals

Boot through U-Boot with command line only, initrd only, both, and empty arguments. Verify final `boot_command_line`, initrd log range, root device, and no buffer overrun when the command line is near maximum length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/uboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/vectors.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/vectors.c

## Purpose

`vectors.c` owns the m68k exception vector table and initializes early and full trap vector routing.

## Important APIs, Types, and Functions

It defines `e_vector vectors[256]`, declarations for low-level assembly handlers `system_call`, `buserr`, `trap`, `nmihandler`, and optional `fpu_emu`, plus `base_trap_init()` and `trap_init()`. It also defines a minimal Amiga NMI handler that immediately `rte`s.

## Control Flow

`base_trap_init()` optionally saves the Sun3x PROM VBR, sets the CPU VBR to `vectors`, installs the 68060 unimplemented-integer-instruction ISP vector if needed, and assigns early bus error, illegal instruction, and syscall vectors. `trap_init()` fills autovectors with `bad_inthandler`, fills unset privileged vectors with `trap`, fills user vectors with `bad_inthandler`, installs FPU emulator or 040/060 FPSP/IFPSP vectors when configured, and replaces Amiga level-7 NMI with the ignore handler.

## State and Persistence Behavior

The vector table is persistent runtime dispatch state. VBR is programmed to point at it, and individual entries are later modified by IRQ setup and FPU/platform logic.

## Dependencies and Integration Points

It depends on entry assembly labels, `bad_inthandler`, CPU/FPU feature macros, FPU support package labels, Sun3x PROM state, and `ints.c` for later interrupt vector updates. `vectors.h` exposes `base_trap_init()` to `head.S`.

## Risks and Edge Cases

`base_trap_init()` must run very early because 68060 or FPU emulation may trap before full trap initialization. Missing FPSP/IFPSP labels in the build would fail linking for 040/060 hardware-FPU configs. Filling user vectors with bad handlers means user interrupt ranges must be explicitly enabled later.

## Test Signals

Boot should reach `base_trap_init()` before early probe traps. Illegal instruction, syscall, bus error, FPU exception, and autovector tests should route to the expected handlers. IRQ request/free should visibly update entries initialized here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/vectors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/vectors.h -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/vectors.h

## Purpose

`vectors.h` declares the early vector-table initialization entry used by startup assembly.

## Important APIs, Types, and Functions

It declares `void base_trap_init(void);`.

## Control Flow

The header has no executable control flow. `head.S` calls `base_trap_init()` after switching to the real kernel stack and before `start_kernel()`.

## State and Persistence Behavior

No state is owned here. `vectors.c` sets VBR and fills early vector entries.

## Dependencies and Integration Points

It connects `head.S` to `vectors.c`. The function must be callable before full kernel initialization.

## Risks and Edge Cases

A declaration mismatch could break the assembly-to-C call during the earliest exception setup phase.

## Test Signals

Successful boot past early trap setup and correct handling of early bus/illegal/syscall vectors validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/vectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/vmlinux.lds.S

## Purpose

`vmlinux.lds.S` selects the m68k top-level linker script variant for the final kernel image.

## Important APIs, Types, and Functions

For MMU non-ColdFire builds it defines two loadable program headers, `text` and `data`, both with flags 7, then includes either `vmlinux-sun3.lds` or `vmlinux-std.lds`. For no-MMU or ColdFire builds it includes `vmlinux-nommu.lds`.

## Control Flow

There is no runtime flow. The preprocessor selects the linker script according to `CONFIG_MMU`, `CONFIG_COLDFIRE`, and `CONFIG_SUN3`.

## State and Persistence Behavior

It controls link-time section layout and ELF program headers. That layout determines boot symbol addresses used by `head.S`, setup code, and memory initialization.

## Dependencies and Integration Points

It depends on included linker scripts and Kconfig. `head.S` assumes symbols such as `_stext`, `_end`, and `kernel_pg_dir` are placed consistently with this selection.

## Risks and Edge Cases

Wrong script selection can place sections at addresses incompatible with early boot, especially Sun3 page-size and no-MMU flat-memory cases. PHDR flag changes can affect bootloader loading permissions.

## Test Signals

Inspect linked `vmlinux` map and program headers for MMU, Sun3, ColdFire, and no-MMU configs. Boot tests should confirm `_stext`, `_end`, and init sections match startup expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/Makefile

## Purpose

This Makefile selects m68k architecture library objects for memory routines, user access, checksums, and compiler helper arithmetic.

## Important APIs, Types, and Functions

Common objects are `checksum.o`, `muldi3.o`, `memcpy.o`, `memmove.o`, and `memset.o`. MMU or ColdFire builds also include `uaccess.o`. Non-ColdFire 68000 builds include 32-bit arithmetic helper assembly objects such as `divsi3.o`, `udivsi3.o`, `modsi3.o`, `umodsi3.o`, and `mulsi3.o`.

## Control Flow

There is no runtime flow. Kbuild expands `lib-y` according to `CONFIG_MMU`, `CONFIG_COLDFIRE`, and `CONFIG_CPU_HAS_NO_MULDIV64`.

## State and Persistence Behavior

No state is owned. The selected objects provide runtime symbols linked into the kernel or modules.

## Dependencies and Integration Points

It integrates with compiler-generated helper calls, generic string/memory APIs, networking checksum code, and user access helpers. The C files and assembly files in this subset are selected here.

## Risks and Edge Cases

Omitting compiler helper objects can produce unresolved symbols on CPU/toolchain combinations without native multiply/divide support. Selecting `uaccess.o` for the wrong memory model would expose inappropriate copy semantics.

## Test Signals

Build matrix coverage for MMU, no-MMU, ColdFire, and 68000 targets should show no unresolved `__divsi3`, `__modsi3`, `__mulsi3`, memory, checksum, or uaccess symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/checksum.c -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/checksum.c

## Purpose

`checksum.c` implements optimized m68k Internet checksum routines used by networking and copy/checksum paths.

## Important APIs, Types, and Functions

The important functions are `csum_partial()`, `csum_and_copy_from_user()`, and `csum_partial_copy_nocheck()`. `csum_partial()` and `csum_partial_copy_nocheck()` are exported. The code uses inline m68k assembly to accumulate 16-bit one's-complement sums while handling alignment and carries.

## Control Flow

`csum_partial()` folds an initial sum with data from a kernel buffer, handling odd alignment and longword loops for speed. `csum_and_copy_from_user()` copies from user memory while accumulating the checksum and uses exception-table fixups that return checksum value zero if a source access faults. `csum_partial_copy_nocheck()` performs the same copy/checksum operation for trusted kernel buffers without user fault reporting.

## State and Persistence Behavior

The routines do not keep global state. They read source memory, optionally write destination buffers, and return an accumulated checksum value.

## Dependencies and Integration Points

They integrate with IP/TCP/UDP checksum helpers and socket/network copy paths. The user-copy variant depends on m68k exception table/uaccess behavior to recover from faults.

## Risks and Edge Cases

Checksum correctness is sensitive to odd byte starts/ends, carry propagation, endian assumptions, and copy fault behavior. Inline assembly must preserve compiler constraints and not clobber unexpected registers. User faults collapse the checksum result to zero rather than reporting a residual byte count, so callers must follow the checksum helper contract rather than normal uaccess residual semantics.

## Test Signals

Compare checksums against generic C implementations for aligned and unaligned buffers, odd lengths, nonzero initial sums, copied data correctness, and injected user-fault cases. Networking selftests and packet checksum validation are practical integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/divsi3.S -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/divsi3.S

## Purpose

`divsi3.S` implements the compiler runtime helper `__divsi3` for signed 32-bit division on m68k targets that need software arithmetic support.

## Important APIs, Types, and Functions

The exported symbol is `__divsi3`. The file defines portability macros for user label prefixes, register prefixes, immediate prefixes, and symbolic register names so the same helper style can work across assembler conventions.

## Control Flow

The routine receives numerator and denominator in the ABI-defined registers/stack convention used by compiler helper calls, normalizes signs, performs unsigned division through shifts/subtracts or m68k division instructions where available in the helper body, applies the final sign, and returns the quotient.

## State and Persistence Behavior

No global state is used. Only registers and stack according to the ABI are mutated for the duration of the helper call.

## Dependencies and Integration Points

It is selected by `arch/m68k/lib/Makefile` for non-ColdFire 68000-oriented builds and satisfies compiler-generated calls when the target lacks native 32-bit signed division.

## Risks and Edge Cases

Division by zero behavior must match the compiler/libgcc expectation for the target. Signed overflow such as `INT_MIN / -1` is ABI/compiler-sensitive. Register preservation must match the m68k calling convention or arbitrary C code can be corrupted.

## Test Signals

Compile code that forces signed 32-bit division and compare results for positive, negative, mixed-sign, zero numerator, large values, and edge values against a reference implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/divsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/memcpy.c -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/memcpy.c

## Purpose

`memcpy.c` provides the m68k implementation of `memcpy()` for non-overlapping memory copies.

## Important APIs, Types, and Functions

It defines and exports `void *memcpy(void *to, const void *from, size_t n)`. The implementation uses m68k inline assembly and alignment-aware loops to copy bytes, words, or longwords efficiently.

## Control Flow

The function saves the original destination pointer for return, handles small or unaligned leading bytes as needed, copies larger aligned chunks using wider operations, then copies trailing bytes. It assumes the source and destination do not overlap, as required by `memcpy()`.

## State and Persistence Behavior

The only persistent effect is writing `n` bytes into the destination buffer. No global state is used.

## Dependencies and Integration Points

It satisfies generic kernel `memcpy()` calls and module references through `EXPORT_SYMBOL`. It is selected by `arch/m68k/lib/Makefile`.

## Risks and Edge Cases

Overlapping ranges are undefined and must use `memmove()`. Assembly constraints and alignment handling must be correct for all CPU variants selected by this library. Very small copies and odd addresses are common edge cases.

## Test Signals

Run memory selftests comparing byte-for-byte results for sizes 0 through large buffers, all source/destination alignments, and ensure overlapping tests are routed to `memmove()` rather than relying on `memcpy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/memmove.c -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/memmove.c

## Purpose

`memmove.c` provides the m68k implementation of `memmove()`, supporting overlapping memory ranges safely.

## Important APIs, Types, and Functions

It defines and exports `void *memmove(void *dest, const void *src, size_t n)`. The implementation chooses forward or backward copying based on relative source/destination addresses.

## Control Flow

If the destination is before the source or outside the overlapping forward hazard, the routine copies forward much like `memcpy()`. If the destination lies inside the source range at a higher address, it starts from the end and copies backward to prevent overwriting bytes that have not yet been read. Alignment and chunk loops optimize larger transfers.

## State and Persistence Behavior

The only persistent effect is updating the destination memory range. No global state is used.

## Dependencies and Integration Points

It satisfies generic kernel and module `memmove()` references through `EXPORT_SYMBOL`. Signal frame code and many core subsystems rely on correct overlap behavior.

## Risks and Edge Cases

The overlap decision must be exact for adjacent, identical, and partially overlapping ranges. Backward-copy alignment handling is more error-prone than forward copy. Zero-length copies must return immediately without touching memory.

## Test Signals

Test all small sizes, all alignments, exact same source/destination, destination before source, destination after source, adjacent ranges, and large aligned ranges against a reference memmove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/memmove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/memset.c -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/memset.c

## Purpose

`memset.c` provides the m68k implementation of `memset()` for filling memory with a repeated byte.

## Important APIs, Types, and Functions

It defines and exports `void *memset(void *s, int c, size_t count)`. The implementation expands the byte value into wider word/longword patterns and uses alignment-aware loops.

## Control Flow

The function saves the original pointer, handles unaligned leading bytes, fills larger aligned chunks with repeated wider stores, and writes any trailing bytes. It returns the original destination pointer.

## State and Persistence Behavior

The only persistent effect is writing `count` bytes into the target memory. No global state is used.

## Dependencies and Integration Points

It is selected by the m68k library Makefile and exported for modules. It is used across boot, memory management, drivers, and task setup.

## Risks and Edge Cases

Incorrect byte expansion can write the wrong pattern for values outside 0..255 if not masked properly. Alignment and tail handling must cover zero length, one byte, odd addresses, and large buffers.

## Test Signals

Compare against generic memset for all byte values, sizes 0 through large ranges, and every destination alignment. KASAN-style redzone tests are useful for overrun detection where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/memset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/modsi3.S -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/modsi3.S

## Purpose

`modsi3.S` implements the compiler runtime helper `__modsi3` for signed 32-bit remainder on m68k targets requiring software arithmetic.

## Important APIs, Types, and Functions

The exported symbol is `__modsi3`. Like the related helper files, it defines assembler portability macros for symbol, register, and immediate syntax.

## Control Flow

The routine follows signed remainder semantics: it records operand signs, derives an unsigned quotient/remainder through division logic, then applies the dividend sign to the remainder before returning it.

## State and Persistence Behavior

It uses only call-local registers and stack state. No global state persists.

## Dependencies and Integration Points

It is selected by the m68k library Makefile and satisfies compiler-generated `%` operations for signed 32-bit integers on targets without a suitable hardware instruction sequence.

## Risks and Edge Cases

Remainder sign must follow C semantics for signed division. Division by zero and `INT_MIN % -1` behavior must align with the compiler runtime contract. Register clobbers must match ABI expectations.

## Test Signals

Compile and run signed modulo tests for positive/negative dividends and divisors, zero dividend, large values, and edge cases against compiler or generic C results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/modsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/mulsi3.S -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/mulsi3.S

## Purpose

`mulsi3.S` implements the compiler runtime helper `__mulsi3` for 32-bit integer multiplication on m68k targets that need software support.

## Important APIs, Types, and Functions

The exported symbol is `__mulsi3`. The file uses the same assembler portability macros as the division/remainder helpers.

## Control Flow

The helper multiplies two 32-bit operands using a shift/add algorithm or available partial multiply instructions in the helper body, accumulating the low 32-bit product returned according to the compiler ABI.

## State and Persistence Behavior

No persistent state is used. Only volatile helper registers are mutated during the call.

## Dependencies and Integration Points

It is selected by `arch/m68k/lib/Makefile` for CPU/toolchain combinations that require software 32-bit multiplication. It satisfies compiler-generated `__mulsi3` calls from arbitrary C code.

## Risks and Edge Cases

The low 32-bit wraparound result must match C unsigned/signed two's-complement multiplication behavior. Register preservation is critical because the helper may be inserted into any compiled code path.

## Test Signals

Exercise multiplication for zero, one, negative values, high-bit operands, and overflow wraparound. Build logs should show no unresolved `__mulsi3`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/mulsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/uaccess.c -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/uaccess.c

## Purpose

`uaccess.c` implements generic m68k user-memory copy and clear helpers used when inline or CPU-specific uaccess paths fall back to C routines.

## Important APIs, Types, and Functions

It defines and exports `__generic_copy_from_user()`, `__generic_copy_to_user()`, and `__clear_user()`. These functions use byte loops with exception-table annotations around user memory accesses.

## Control Flow

`__generic_copy_from_user()` copies from a user pointer to kernel memory one byte at a time, with inline assembly labels and exception-table fixups that branch to a failure path and return the remaining byte count. `__generic_copy_to_user()` mirrors that direction from kernel to user. `__clear_user()` writes zero bytes to user memory with the same remaining-count convention.

## State and Persistence Behavior

Successful operations mutate destination memory. On user faults, the functions return a nonzero remaining count and may leave a partially copied or cleared range. No global state is used.

## Dependencies and Integration Points

They depend on m68k exception table handling, user pointer annotations, and callers that interpret Linux uaccess residual counts. The file is selected for MMU or ColdFire builds by the library Makefile.

## Risks and Edge Cases

Fault fixup labels must preserve the correct residual byte count. Partial copies are expected and callers must check return values. Byte-at-a-time behavior is simple but slower than optimized copy paths. Incorrect exception-table entries could turn user faults into kernel oopses.

## Test Signals

Test valid copies, boundary-crossing user buffers, unmapped source/destination pages, partial faults, zero-length operations, and clear-user behavior. Fault-injection with `copy_from_user()` wrappers should report exact residual counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/uaccess.c -->
