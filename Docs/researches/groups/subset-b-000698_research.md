# subset-b-000698 LoongArch Kernel/KVM/Lib Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unaligned.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unaligned.c

Purpose: emulates LoongArch unaligned load/store faults for integer and floating-point accesses that the hardware or current CPU mode did not complete directly. It is the C policy layer above the byte-wise helpers in `arch/loongarch/lib/unaligned.S`.

Important APIs, types, and functions: `emulate_load_store_insn(struct pt_regs *regs, void __user *addr, unsigned int *pc)` is the external entry point. `read_fpr()` and `write_fpr()` use inline assembly to move values between GPRs and FPRs, with 32-bit and 64-bit variants. It depends on `union loongarch_instruction`, opcode helpers from `asm/inst.h`, `unaligned_read()`, `unaligned_write()`, `compute_return_era()`, `fixup_exception()`, and FPU ownership helpers.

Control flow: the handler records a software emulation perf event, fetches the trapped instruction via `__get_inst()`, decodes supported immediate, pointer, indexed, and FP load/store opcodes, validates access size and user `access_ok()`, then either reads bytes into the destination register or writes the register value back to memory. Successful emulation advances ERA with `compute_return_era()`. Memory helper faults first try exception-table fixup, then kill kernel faults or signal userspace with `SIGSEGV`; unsupported instructions signal `SIGBUS`.

State and persistence: under `CONFIG_DEBUG_FS`, it increments `unaligned_instructions_user` or `unaligned_instructions_kernel` and exposes both counters through `arch_debugfs_dir`. FP state may be written either to live hardware FPRs or `current->thread.fpu` depending on `is_fpu_owner()`.

Dependencies and integration points: integrated with the LoongArch exception path for ALE handling, Linux perf software events, debugfs, signal delivery, exception tables, and the architecture FPU save area. It relies on the assembly helper returning zero or `-EFAULT`-style failure.

Risks: decoder coverage must exactly match the ISA encodings that can fault on unaligned access; missing an opcode becomes `SIGBUS`. FP handling is sensitive to FPU ownership and register width. Kernel-mode faults depend on valid exception-table fixups; otherwise the kernel dies. The `sign` flag is meaningful for reads but harmlessly set on stores.

Test signals: unaligned user integer and FP load/store tests should verify sign extension, unsigned loads, indexed loads, and PC advancement. Kernel selftests or fault injection should cover exception-table recovery. Debugfs counters and `PERF_COUNT_SW_EMULATION_FAULTS` provide runtime observability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unaligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind.c

Purpose: provides the generic fallback stack-scanning unwinder used by LoongArch unwinder implementations when no stronger metadata is available.

Important APIs, types, and functions: `default_next_frame(struct unwind_state *state)` scans `state->stack_info` for kernel-text return addresses. It uses `unwind_done()`, `get_stack_info()`, `unwind_graph_addr()`, and `__kernel_text_address()`.

Control flow: starting one word above the current stack pointer, it walks each stack segment until `info->end`, treats each word as a possible return address, translates function-graph tracer return addresses, and accepts the first kernel text address as the next PC. If the segment ends, it jumps to `info->next_sp` and asks `get_stack_info()` for the next stack segment.

State and persistence: mutates only the passed `unwind_state` by advancing `sp`, updating `pc`, and consuming stack segment metadata. It has no global state.

Dependencies and integration points: called by `unwind_guess.c` directly and by `unwind_prologue.c` when prologue analysis cannot operate. It is part of stacktrace, dump, warning, and live debugging paths.

Risks: this is heuristic and can report false positives from stack data that looks like a kernel address. It should be treated as less reliable than ORC or prologue unwinding.

Test signals: stacktrace output under deep call chains, IRQ stacks, and function graph tracing should continue to make progress without crossing invalid stack bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_guess.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_guess.c

Purpose: implements the LoongArch "guess" unwinder, exporting the standard unwinder interface while delegating frame traversal to `default_next_frame()`.

Important APIs, types, and functions: exports `unwind_get_return_address()`, `unwind_start()`, and `unwind_next_frame()`. It relies on `__unwind_start()`, `__unwind_get_return_address()`, `unwind_done()`, and `default_next_frame()`.

Control flow: `unwind_start()` initializes the state and, if the initial PC is not kernel text, immediately advances to the next guessed frame. `unwind_next_frame()` calls the stack-scanning fallback each time.

State and persistence: no persistent state. It mutates only `struct unwind_state` supplied by callers.

Dependencies and integration points: used when the kernel is configured for the guess unwinder or when prologue unwinding downgrades to `UNWINDER_GUESS`. Exported GPL symbols feed stacktrace users.

Risks: inherits all heuristic risks from `default_next_frame()` and lacks metadata validation. It can miss frames or include spurious frames when stack contents are ambiguous.

Test signals: boot-time stack dumps, WARN/OOPS traces, and forced stacktrace tests should produce bounded traces without invalid memory accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_guess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_orc.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_orc.c

Purpose: implements the LoongArch ORC unwinder, including table lookup, module ORC registration, ftrace trampoline mapping, stack safety checks, and frame-step logic.

Important APIs, types, and functions: exported interfaces are `unwind_get_return_address()`, `unwind_start()`, and `unwind_next_frame()`. `unwind_init()` validates and initializes vmlinux ORC tables and lookup blocks. `unwind_module_init()` sorts module ORC tables and attaches them to `struct module`. Internal helpers include `orc_find()`, `__orc_find()`, `orc_module_find()`, `orc_ftrace_find()`, `stack_access_ok()`, and `bt_address()`.

Control flow: lookup first handles `ip == 0`, then uses the fast `orc_lookup` block table for core text, a full binary search for init text, module tables when enabled, and dynamic ftrace fallback if needed. `unwind_next_frame()` obtains an ORC entry under RCU protection, falls back to a fake frame-pointer entry for generated code, computes the previous SP/FP/RA according to the ORC entry, handles saved `pt_regs` frames, translates exception-vector addresses via `bt_address()`, and marks the trace done or errored on invalid state.

State and persistence: persistent state includes `orc_init`, `lookup_num_blocks`, mutable lookup table entries, module ORC pointers, and module sort scratch globals protected by `sort_mutex`. The unwinder mutates per-call `unwind_state` fields `sp`, `fp`, `ra`, `pc`, `stack_info`, and `error`.

Dependencies and integration points: depends on objtool-generated `.orc_unwind`/`.orc_unwind_ip` sections, linker `ORC_UNWIND_TABLE`, module loader ORC plumbing, dynamic ftrace trampolines, exception handlers, stack metadata, RCU, and function graph return address translation.

Risks: corrupt or unsorted ORC tables can disable unwinding or produce bad stack walks. The module sort swap must keep relative IP encodings aligned with entries. Stack access validation is critical for crash safety. Fallback frame-pointer unwinding intentionally marks `state->error`.

Test signals: ORC table validation warnings at boot, stacktrace correctness through modules, ftrace-enabled traces, NULL function pointer crash unwinding, IRQ/exception stack traces, and objtool/sorttable build checks are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_orc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_prologue.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_prologue.c

Purpose: implements prologue-analysis stack unwinding for LoongArch by scanning function prologues for stack allocation and RA-save instructions.

Important APIs, types, and functions: exports `unwind_get_return_address()`, `unwind_start()`, and `unwind_next_frame()`. Core helpers are `unwind_by_prologue()`, `next_frame()`, `scan_handlers()`, `fix_exception()`, `fix_ftrace()`, and `unwind_state_fixup()`.

Control flow: `unwind_start()` initializes state as `UNWINDER_PROLOGUE`, or downgrades to guess mode if the initial PC is not kernel text. `unwind_by_prologue()` looks up the current symbol, scans from symbol start to current PC for stack allocation, then scans for RA save before branches. It computes caller SP/PC, handles first-frame leaf functions via saved RA, and resets from `pt_regs` when it recognizes exception/ftrace handler hints. `next_frame()` also handles IRQ stack transitions and falls back through stack segments.

State and persistence: persistent inputs are exception unwind hint symbols and per-CPU exception handlers. Runtime state is held in `unwind_state` flags `type`, `first`, and `reset` plus SP/RA/PC and stack info.

Dependencies and integration points: depends on instruction recognizers from `asm/inst.h`, kallsyms size/offset lookup, exception vector layout, dynamic ftrace, function graph tracing, and stack metadata. It integrates with stacktrace and dump paths through exported GPL symbols.

Risks: compiler prologue variations, hand-written assembly, unusual control flow, or missing kallsyms data can break analysis. Leaf-function handling is necessarily approximate. Exception-vector hint offsets must stay synchronized with low-level exception assembly.

Test signals: compare traces under normal C call chains, leaf functions, ftrace, exceptions, IRQ stacks, and NUMA per-CPU handlers. Build changes affecting prologues should be validated with stacktrace and unwinder tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_prologue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/uprobes.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/uprobes.c

Purpose: provides LoongArch architecture hooks for uprobes and uretprobes, including instruction validation, execute-out-of-line setup, simulation, and return address hijacking.

Important APIs, types, and functions: implements `arch_uprobe_analyze_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_abort_xol()`, `arch_uprobe_skip_sstep()`, `arch_uretprobe_hijack_return_addr()`, `arch_uretprobe_is_alive()`, `uprobe_breakpoint_handler()`, `uprobe_singlestep_handler()`, `uprobe_get_swbp_addr()`, and `arch_uprobe_copy_ixol()`.

Control flow: instruction analysis rejects unaligned probe addresses and unsupported instructions. Instructions needing simulation install a NOP into the XOL slot and set `simulate`; otherwise the original instruction is copied followed by the XOL breakpoint. Pre-XOL saves `trap_nr`, tags the task with `UPROBE_TRAP_NR`, and redirects PC to the XOL slot. Post-XOL restores trap state and advances PC by one instruction; abort restores the original probe address. Simulated instructions are interpreted by `arch_simulate_insn()`.

State and persistence: per-task uprobe state lives in `current->utask` and `current->thread.trap_nr`. Uretprobes replace GPR1/RA with the trampoline and compare saved stack values for liveness.

Dependencies and integration points: depends on generic uprobes, LoongArch instruction analysis/simulation, cache flushing, highmem page mapping, and ptrace PC helpers.

Risks: instruction classification is critical because non-simulatable PC-relative or control-flow instructions cannot safely execute out of line. Cache flushing must cover copied XOL bytes. Return-probe liveness depends on LoongArch stack direction and SP conventions.

Test signals: kernel uprobe selftests, perf probe on LoongArch user binaries, uretprobe nested calls, unsupported instruction rejection, and XOL cache-coherency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/vdso.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/vdso.c

Purpose: initializes and maps the LoongArch vDSO image into user processes and tracks the per-mm vDSO base.

Important APIs, types, and functions: `vdso_info` is the global `struct loongarch_vdso_info`. `init_vdso()` allocates the page array for the linked vDSO image. `vdso_mremap()` updates `mm->context.vdso`. `vdso_base()` chooses a randomized base near `STACK_TOP`. The file also contains the architecture `arch_setup_additional_pages()` path, which maps `[vdso]` with `vm_special_mapping`.

Control flow: at `subsys_initcall`, the code verifies page alignment, records NUMA node IDs in `vdso_k_arch_data`, computes vDSO size, allocates `code_mapping.pages`, and maps each PFN from `vdso_start`. Per-process setup picks a randomized base when `PF_RANDOMIZE` is set, obtains `mmap_write_lock()`, uses `get_unmapped_area()`, calls `_install_special_mapping()`, and records the base in `mm->context.vdso`.

State and persistence: persistent kernel state is `vdso_info` and its allocated page array. Per-mm state is `mm->context.vdso`; per-CPU vDSO data gets node IDs. No on-disk state exists.

Dependencies and integration points: depends on generated vDSO offsets, the vDSO linker image, special mappings, randomization, ELF binfmt process setup, and vDSO data pages.

Risks: incorrect page alignment or size calculation breaks process startup mappings. Randomization must still leave a valid unmapped area. `vdso_mremap()` must keep `mm->context.vdso` accurate after remap.

Test signals: process startup, `getauxval(AT_SYSINFO_EHDR)`, vDSO symbol calls such as time functions, ASLR variance, mremap behavior, and page table inspection for `[vdso]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/vmlinux.lds.S

Purpose: defines the LoongArch kernel linker script, including load address, text/init/data/BSS layout, EFI PE/COFF alignment metadata, ORC unwind tables, and discarded sections.

Important APIs, types, and symbols: establishes `OUTPUT_ARCH(loongarch)`, `ENTRY(kernel_entry)`, PHDRs, `_text`, `_stext`, `_etext`, `__init_begin`, `__init_end`, `_sdata`, `_edata`, `_end`, relocation bounds, optional RELR bounds, optional EFI header symbols, and `jiffies = jiffies_64`.

Control flow: the script orders head text, executable text groups, fixups, init/exit text and data, alternatives, optional percpu, rodata, GOT/PLT, writable data, relocations, ORC tables, small data, BSS, debug metadata, modinfo, ELF details, and discard rules. It aligns major segments to `PECOFF_SEGMENT_ALIGN` and pads writable data to `PECOFF_FILE_ALIGN`.

State and persistence: the output binary layout is persistent build state consumed by boot loaders, runtime symbol ranges, exception tables, ORC unwinding, relocation code, and EFI stub metadata.

Dependencies and integration points: includes generic `vmlinux.lds.h`, architecture offsets, ORC lookup definitions, and `image-vars.h`. It integrates with build tools, EFI stub, relocation processing, objtool ORC emission, exception fixups, and module/debug metadata.

Risks: alignment or section ordering errors can break boot, early page tables, ORC lookup, alternatives, exception fixups, or EFI loading. Discarding the wrong metadata can hide needed runtime sections.

Test signals: successful kernel link, boot under EFI and non-EFI paths, ORC unwinder boot validation, relocation tests, section layout inspection with `readelf`, and early boot page table stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/Kconfig

Purpose: declares LoongArch virtualization configuration and exposes `CONFIG_KVM` under the `VIRTUALIZATION` menu.

Important APIs, types, and functions: selects generic KVM features including dirty ring acquire/release, IRQ routing, IRQ chip, MSI, readonly memory, common KVM, dirtylog read-protect, hardware enabling, MMIO, guest-mode work transfer, scheduler info, and guest perf events when `PERF_EVENTS` is enabled.

Control flow: sources `virt/kvm/Kconfig`, presents `menuconfig VIRTUALIZATION`, and defines `config KVM` as a tristate depending on assembler LVZ support and `64BIT`.

State and persistence: affects the kernel `.config` and thereby object inclusion, exported interfaces, and runtime KVM availability.

Dependencies and integration points: tied to LoongArch LVZ hardware virtualization, 64-bit builds, generic KVM infrastructure, irqfd/ioeventfd/dirty logging capabilities, and scheduler statistics for steal time.

Risks: missing selects cause compile-time or runtime feature gaps; too-broad enables could advertise unsupported KVM capabilities. The LVZ assembler dependency must match actual toolchain support.

Test signals: Kconfig dependency resolution, allmodconfig/defconfig builds, `modprobe kvm`, and userspace KVM capability probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/Makefile -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/Makefile

Purpose: defines the object composition of the LoongArch KVM module/built-in support.

Important APIs, types, and functions: includes `virt/kvm/Makefile.kvm`, builds `kvm.o` under `CONFIG_KVM`, always includes `switch.o` in this directory's object list, and aggregates `exit.o`, `interrupt.o`, `main.o`, `mmu.o`, `timer.o`, `tlb.o`, `vcpu.o`, `vm.o`, interrupt-controller objects, and `irqfd.o` into `kvm-y`.

Control flow: Kbuild compiles `switch.S` plus the C implementation units and suppresses `override-init` warnings for `exit.o`.

State and persistence: build metadata only; it determines which runtime KVM code is linked.

Dependencies and integration points: integrates with generic KVM build rules, LoongArch assembly world-switch code, and intc subdirectory sources.

Risks: object ordering and omissions can cause missing symbols, unregistered device types, or unavailable world-switch entry points. The warning suppression hints at designated initializer ranges in exit dispatch tables.

Test signals: `CONFIG_KVM=y/m` builds, module symbol resolution, and boot/module load tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/exit.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/exit.c

Purpose: decodes and handles guest exits for LoongArch KVM, covering CPUCFG/CSR/IOCSR emulation, MMIO fallback, page faults, auxiliary-unit traps, hypercalls, and exception dispatch.

Important APIs, types, and functions: key entry points are `kvm_handle_fault()`, `kvm_emu_iocsr()`, `kvm_complete_iocsr_read()`, `kvm_emu_mmio_read()`, `kvm_complete_mmio_read()`, `kvm_emu_mmio_write()`, and `kvm_complete_user_service()`. It uses `larch_inst`, `struct kvm_run`, `struct kvm_vcpu`, emulation result constants, `kvm_fault_tables[]`, and tracepoints.

Control flow: GSPR exits fetch `vcpu->arch.badi`, advance PC optimistically, decode CPUCFG, CSR, cache, idle, and IOCSR operations, then either resume guest, exit to userspace, or inject illegal instruction. GPA read/write faults first call `kvm_handle_mm_fault()`; failures are decoded as MMIO reads/writes and either handled in-kernel via KVM I/O buses or returned to userspace. Auxiliary-unit disabled exits request FPU/LSX/LASX/LBT loading. Hypercalls implement PV IPI, PV steal-time notification, user-service exits, and software debug.

State and persistence: mutates GPRs, guest PC, CSR state, `run->mmio`, `run->iocsr_io`, `run->hypercall`, `vcpu->mmio_needed`, `io_gpr`, stats counters, pending requests, and PV steal-time address state. No storage persists beyond VM/vCPU state.

Dependencies and integration points: integrates with `mmu.c` for GPA mappings, KVM MMIO/IOCSR buses, interrupt injection, CSR helpers, PMU request handling, timer/idle halt logic, PV feature flags, userspace `KVM_EXIT_MMIO`, `KVM_EXIT_LOONGARCH_IOCSR`, `KVM_EXIT_HYPERCALL`, and trace events.

Risks: PC update/rollback rules are subtle for emulation failures and userspace completions. Signed versus unsigned MMIO reads depend on `mmio_needed`. Unsupported CSR behavior must match architecture expectations. MMIO instruction decoder coverage affects device emulation correctness. Hypercall feature checks gate ABI exposure.

Test signals: KVM unit tests for CPUCFG/CSR, userspace MMIO and IOCSR exits, in-kernel irqchip accesses, dirty memory faults, FPU/LSX/LASX traps, PV IPI and steal time, and tracepoint coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/dmsintc.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/dmsintc.c

Purpose: emulates the LoongArch direct MSI interrupt controller used with message-signaled interrupts and AVEC delivery.

Important APIs, types, and functions: `dmsintc_inject_irq()`, `dmsintc_deliver_msi_to_vcpu()`, `dmsintc_set_irq()`, device ops `kvm_dmsintc_create()`, `kvm_dmsintc_destroy()`, `kvm_dmsintc_set_attr()`, and registration `kvm_loongarch_register_dmsintc_device()`.

Control flow: MSI address/data decode chooses a target CPU and vector. Delivery sets the vector bit in the target vCPU `dmsintc_state.vector_map`, injects `INT_AVEC`, and kicks the vCPU. On guest interrupt delivery, `dmsintc_inject_irq()` atomically drains vector maps into guest ISR0-ISR3 CSRs. Device attributes initialize the message address base and size once, deriving the CPU mask from the base address encoding.

State and persistence: per-VM state is `struct loongarch_dmsintc` with message base, size, CPU mask, and KVM pointer. Per-vCPU vector bitmap state is stored atomically in `vcpu->arch.dmsintc_state`.

Dependencies and integration points: used by PCH-PIC MSI routing when `cpu_has_msgint` and the MSI address falls inside the DMSINTC window; registered as a KVM device type during KVM environment initialization; integrated with `interrupt.c` AVEC injection.

Risks: `dmsintc_inject_irq()` declares `vector[4]` without explicit zero initialization before conditional writes, so empty vector slots must be handled carefully. Duplicate attribute setting returns errors. CPU and vector decoding must match the ABI used by userspace VMMs.

Test signals: KVM device create/set-attr tests, MSI injection to all vectors, AVEC interrupt visibility in guest ISR CSRs, invalid CPU/vector rejection, and migration save/restore through attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/dmsintc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/eiointc.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/eiointc.c

Purpose: emulates the LoongArch extended I/O interrupt controller, including IOCSR register access, routing, virtual-extension registers, and migration attributes.

Important APIs, types, and functions: external entry is `eiointc_set_irq()`. Device creation/registration flows through `kvm_eiointc_create()`, `kvm_eiointc_destroy()`, `kvm_eiointc_get_attr()`, `kvm_eiointc_set_attr()`, and `kvm_loongarch_register_eiointc_device()`. Internal helpers update `sw_coreisr`, `sw_coremap`, IRQ lines, and register banks.

Control flow: asserted IRQs update `isr`, map guest IRQ to an IP line and target vCPU, update per-core ISR bitmaps, and raise/lower `INT_HWI0..INT_HWI3` parent interrupts only when the first/last child on that line changes. IOCSR reads/writes expose nodetype, ipmap, enable, bounce, coreisr, and coremap registers. Enable and coremap writes recalculate delivery. Virtual-extension registers expose feature/status bits. Attribute groups handle initialization, migration register state, and software status.

State and persistence: `struct loongarch_eiointc` persists per VM with feature/status bits, num CPU, ipmap, enable, bounce, ISR/coreISR/coremap arrays, software maps, KVM pointer, I/O devices, and spinlock. Migration state is exposed through KVM device attrs.

Dependencies and integration points: registered on the `KVM_IOCSR_BUS` at EIOINTC base ranges, receives routed interrupts from PCH-PIC/MSI paths, targets vCPUs by CPUID or vCPU ID, and injects CPU interrupt lines through `kvm_vcpu_ioctl_interrupt()`.

Risks: routing semantics depend on encoded versus bitmap CPU/IP modes. Locking must cover all bitmap updates. Partial-width IOCSR accesses use masks and offsets, so endian/size behavior must match hardware. Migration restore must call load-finished logic to rebuild software maps.

Test signals: guest irqchip driver boot, enable/disable and clear paths, coremap migration, virtual extension feature negotiation, MSI routing through PCH-PIC, and concurrent IRQ injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/eiointc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/ipi.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/ipi.c

Purpose: emulates LoongArch IOCSR IPI registers, per-vCPU IPI status/enables, mailbox buffers, and cross-vCPU send operations.

Important APIs, types, and functions: device callbacks `kvm_ipi_read()` and `kvm_ipi_write()` wrap `loongarch_ipi_readl()` and `loongarch_ipi_writel()`. Helpers include `ipi_set()`, `ipi_clear()`, `ipi_send()`, `mail_send()`, `any_send()`, `send_ipi_data()`, `read_mailbox()`, `write_mailbox()`, and KVM device attr accessors.

Control flow: IOCSR reads expose status, enable, and mailbox registers. Writes can enable IPI bits, set/clear local pending status, send an IPI bit to another CPUID, update a target mailbox, or write arbitrary IOCSR data to another vCPU. `ipi_set()` injects `LARCH_INT_IPI` only on transition from no pending status to pending; `ipi_clear()` deasserts when status reaches zero.

State and persistence: per-vCPU state lives in `vcpu->arch.ipi_state` with `status`, `en`, mailbox `buf`, and a spinlock. Per-VM state is `struct loongarch_ipi` registered on `KVM_IOCSR_BUS`. Migration-visible state is exposed through KVM device attrs.

Dependencies and integration points: relies on CPUID mapping from `vcpu.c`, generic KVM I/O bus, `kvm_vcpu_ioctl_interrupt()`, SRCU-protected IOCSR bus access, and KVM device infrastructure.

Risks: register access lengths and offsets must match hardware. The mailbox byte-mask semantics in `mail_send()` and `send_ipi_data()` are easy to regress. Invalid CPUID handling logs but often returns zero to the emulated access path, matching device-emulation tolerance.

Test signals: guest SMP IPI tests, mailbox read/write width tests, migration save/restore of IPI regs, invalid target handling, and KVM stats counters for IPI exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/ipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/pch_pic.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/pch_pic.c

Purpose: emulates the LoongArch PCH PIC, routes legacy IRQ pins and MSI vectors toward EIOINTC or DMSINTC, and exposes MMIO/KVM-device state.

Important APIs, types, and functions: external IRQ APIs are `pch_pic_set_irq()` and `pch_msi_set_irq()`. Device paths include `kvm_pch_pic_create()`, `kvm_pch_pic_destroy()`, `kvm_pch_pic_get_attr()`, `kvm_pch_pic_set_attr()`, `kvm_pch_pic_init()`, and `kvm_loongarch_register_pch_pic_device()`.

Control flow: line assertion updates IRR, honors edge-triggered behavior, and calls `pch_pic_update_irq()` to move unmasked requests into ISR and route through `htmsi_vector` to EIOINTC. Deassertion clears level-triggered IRR/ISR. Mask writes raise newly unmasked pending IRQs and lower newly masked active IRQs. MSI delivery uses DMSINTC when the message address falls inside its window on message-interrupt hardware, otherwise it injects into EIOINTC using MSI data as vector.

State and persistence: per-VM `loongarch_pch_pic` stores masks, edge, polarity, IRR/ISR, route entries, HTMSI vectors/enables, base address, device object, and lock. Default IRQ routing maps each GSI to the same PCH-PIC pin.

Dependencies and integration points: registered on `KVM_MMIO_BUS` after userspace initializes the base address; integrates with KVM IRQ routing, irqfd/MSI, EIOINTC, optional DMSINTC, and userspace migration attrs.

Risks: edge-triggered clear semantics differ from level lines. Attribute writes directly copy state and may bypass side effects, so migration ordering matters. The model implements fixed routing only for some route registers.

Test signals: guest legacy IRQs, MSI routing, irqfd injection, mask/clear/polarity behavior, MMIO width accesses, migration restore, and default IRQ routing validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/pch_pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/interrupt.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/interrupt.c

Purpose: handles pending virtual interrupt and exception delivery into LoongArch guest CSR state.

Important APIs, types, and functions: `kvm_deliver_intr()`, `kvm_pending_timer()`, `kvm_deliver_exception()`, and internal `kvm_irq_deliver()`, `kvm_irq_clear()`, `_kvm_deliver_exception()`. `priority_to_irq[]` maps KVM priorities to CPU interrupt bits.

Control flow: clear bits are processed before pending bits. Timer/IPI/SWI/AVEC lines update ESTAT, while HWI lines update root GINTC. AVEC invokes `dmsintc_inject_irq()` when message interrupts are available. Exception delivery writes BADV/BADI/PRMD/CRMD/ERA/ESTAT and redirects PC to `EENTRY + code * vector_size`.

State and persistence: consumes and clears `vcpu->arch.irq_pending`, `irq_clear`, `exception_pending`, and `esubcode`; writes guest hardware CSRs. Timer delivery checks for TVAL inversion and preserves timer interrupt state.

Dependencies and integration points: called by `vcpu.c` immediately before guest entry. Integrated with DMSINTC, CSR helpers, timer emulation, and `kvm_queue_exception()` users in exit handling.

Risks: interrupt bit mapping and CSR side effects must match hardware. Exception and interrupt simultaneous delivery relies on ESTAT encoding. Timer inversion handling is subtle.

Test signals: guest interrupt-controller driver tests, timer interrupt delivery, queued exception injection for MMIO/ADE/INE, AVEC vectors, and migration of ESTAT/GINTC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/irqfd.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/irqfd.c

Purpose: implements architecture-specific KVM IRQ routing and irqfd/MSI injection hooks for LoongArch.

Important APIs, types, and functions: `kvm_set_msi()`, `kvm_set_routing_entry()`, `kvm_arch_set_irq_inatomic()`, `kvm_arch_intc_initialized()`, and internal `kvm_set_pic_irq()`.

Control flow: userspace IRQCHIP routes are converted to PCH-PIC pin callbacks after bounds checking; MSI routes copy address/data and dispatch through `pch_msi_set_irq()`. Atomic injection supports asserted IRQCHIP and MSI routes, returning `-EWOULDBLOCK` for deassertion or unsupported routes.

State and persistence: does not own state; it reads `kvm->arch.pch_pic` and routes into PCH-PIC/EIOINTC/DMSINTC state.

Dependencies and integration points: used by generic KVM irq routing, irqfd, ioeventfd-style injections, and `KVM_IRQ_LINE`. Requires in-kernel irqchip presence from `vm.c`.

Risks: deasserted MSI returns failure by design; callers must tolerate edge-only MSI. Invalid routing pins must be rejected to avoid corrupting PCH state.

Test signals: irqfd tests, userspace `KVM_SET_GSI_ROUTING`, MSI injection, in-atomic injection paths, and `kvm_arch_intc_initialized()` before/after irqchip creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/irqfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/main.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/main.c

Purpose: owns LoongArch KVM global initialization, virtual CPU ID/VPID management, guest CSR classification, per-CPU VMCS context allocation, hardware enable/disable, and device registration.

Important APIs, types, and functions: globals include `vpid_mask`, `kvm_loongarch_ops`, `gcsr_flag[]`, and per-CPU `vmcs`. Entry points include `get_gcsr_flag()`, `kvm_check_vpid()`, `kvm_init_vmcs()`, `kvm_arch_enable_virtualization_cpu()`, `kvm_arch_disable_virtualization_cpu()`, module init/exit, and internal `kvm_init_gcsr_flag()`, `kvm_update_vpid()`, `kvm_loongarch_env_init()`.

Control flow: environment init allocates per-CPU contexts and world-switch ops, reads GID/VPID width, initializes per-CPU VPID caches, classifies hardware versus software guest CSRs, registers perf callbacks and LoongArch KVM device types. CPU enable programs GCFG/GSTAT/GINTC/GTLBC and flushes TLBs. VPID checks allocate a fresh VPID on CPU migration or version change, flush all TLBs on wrap, clear stale GPA flush requests, and update GSTAT.GID.

State and persistence: persistent module state includes per-CPU `struct kvm_context`, the world-switch operation table, CSR classification flags, and VPID caches. Per-vCPU `arch.vpid` and `cpu` are updated on entry.

Dependencies and integration points: ties together `switch.S` entry points, `vcpu.c` load/run paths, CSR helpers, TLB flushing, perf callbacks, and IPI/EIOINTC/PCH-PIC/DMSINTC device registration.

Risks: CSR classification errors can cause unsupported hardware accesses or missed software emulation. VPID wrap/migration logic is central to TLB correctness. Environment init error paths after partial device registration should be watched.

Test signals: module load/unload, per-CPU hardware enabling around CPU hotplug/suspend, guest TLB isolation, VPID tracepoints, and KVM device type availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/mmu.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/mmu.c

Purpose: implements LoongArch KVM second-stage GPA-to-host-physical page tables, dirty/access tracking, hugepage support, memslot invalidation, and guest page fault handling.

Important APIs, types, and functions: exports `kvm_pgd_alloc()`, `kvm_arch_prepare_memory_region()`, `kvm_arch_commit_memory_region()`, `kvm_arch_flush_shadow_all()`, `kvm_arch_flush_shadow_memslot()`, `kvm_unmap_gfn_range()`, `kvm_age_gfn()`, `kvm_test_age_gfn()`, `kvm_handle_mm_fault()`, `kvm_arch_mmu_enable_log_dirty_pt_masked()`, and `kvm_arch_flush_remote_tlbs_memslot()`. Core internals include `kvm_populate_gpa()`, page-table walkers, `kvm_map_page_fast()`, `kvm_map_page()`, `host_pfn_mapping_level()`, and `kvm_split_huge()`.

Control flow: fast faults update existing young/dirty bits under `mmu_lock`. Slow faults resolve the memslot/HVA/PFN under SRCU, top up MMU page-cache pages, guard against MMU notifier invalidations, choose cacheability and permissions, optionally install PMD-sized mappings, split hugepages on write faults under dirty logging, install PTEs, and mark dirty pages. Flush walkers clear mappings, update stats, collect freed page-table pages, and request remote TLB flushes.

State and persistence: per-VM state includes `arch.pgd`, root level, invalid PTE tables, pte shifts, stats for pages/hugepages, memslot arch flags, and shadow page-table pages. Per-vCPU state includes the MMU page cache and `flush_gpa` request.

Dependencies and integration points: depends on generic KVM memory slots, MMU notifier sequencing, PFN fault-in helpers, dirty logging, memslot flags, LoongArch PTE helpers, TLB flush requests, and exit handling for GPA faults.

Risks: races with host MMU invalidation are guarded but complex. Hugepage alignment, dirty logging, and split behavior are high risk. `kvm_unmap_gfn_range()` initializes a free list but caller-side freeing must be considered with walker behavior. Cache attributes differ for valid RAM PFNs versus device PFNs.

Test signals: guest memory stress, dirty-log migration, hugepage mapping/splitting, MMU notifier invalidation during COW/unmap, readonly memslots, MMIO fallback, access aging, and remote TLB shootdown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/switch.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/switch.S

Purpose: provides the low-level LoongArch KVM world switch, guest exception entry, and FPU/LSX/LASX save/restore assembly routines.

Important APIs, types, and functions: exported symbols include `kvm_exc_entry`, `kvm_enter_guest`, `kvm_save_fpu()`, `kvm_restore_fpu()`, optional `kvm_save_lsx()`, `kvm_restore_lsx()`, `kvm_save_lasx()`, and `kvm_restore_lasx()`. Macros save/restore host and guest GPRs and implement `kvm_switch_to_guest`.

Control flow: `kvm_enter_guest()` saves host callee state, stores host SP/TP/per-CPU register in vCPU arch state, writes the vCPU pointer to scratch CSR, and branches into `kvm_switch_to_guest`. The switch macro programs ECFG/EENTRY/ERA/PGDL/GTLBC/PRMD/GSTAT, restores guest GPRs, and executes `ertn`. `kvm_exc_entry` saves guest GPR/CSR exit state, restores host exception state and PGD, clears guest mode/TGID, calls the C exit handler, and either resumes guest or returns to host.

State and persistence: moves state between hardware CSRs/GPRs and `struct kvm_vcpu_arch` fields. Scratch CSRs hold the vCPU pointer and temporary A2 during exception entry.

Dependencies and integration points: tightly coupled to `asm-offsets.h`, CSR definitions, `vcpu.c` run/load paths, `main.c` world-switch ops, exception entry placement, unwind hints, and aux state functions called by `vcpu.c`.

Risks: register offset mismatch or missing save/restore corrupts host or guest state. World-switch code must avoid TLB-dependent paths while PGD/context are transient. Interrupt and PRMD/GSTAT sequencing affects host interrupt responsiveness and guest entry correctness.

Test signals: booting guests, stress with interrupts and exits, register preservation tests, FPU/LSX/LASX context tests, lockdep/noinstr validation, and unwinder behavior through nonstandard frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/switch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/timer.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/timer.c

Purpose: virtualizes the LoongArch stable timer for KVM guests, switching between hardware guest timer state while running and hrtimer-backed software state while blocked/outside guest.

Important APIs, types, and functions: `kvm_init_timer()`, `kvm_restore_timer()`, `kvm_save_timer()`, `kvm_swtimer_wakeup()`, and helpers `ktime_to_tick()`, `tick_to_ns()`, `_kvm_save_timer()`.

Control flow: timer init records a MHz-scale frequency and clears TVAL. Restore disables the hardware timer, restores ESTAT/TCFG, handles disabled timers, oneshot fired state, blocked vCPU soft timer cancellation, and recalculates remaining ticks or periodic expiry. Save reads TCFG/TVAL/ESTAT, computes a future hrtimer expiry, and starts a pinned hard hrtimer if the vCPU is blocking. The hrtimer callback queues `INT_TI` and wakes the vCPU waitqueue.

State and persistence: per-vCPU timer fields include `timer_mhz`, `expire`, `swtimer`, and saved timer CSRs in `vcpu->arch.csr`. Pending timer interrupts are represented in `irq_pending` and guest ESTAT.

Dependencies and integration points: called by vCPU create/load/put paths; uses CSR timer helpers, hrtimer, rcuwait, delay loops for hardware interrupt settling, and interrupt delivery.

Risks: oneshot fired handling and TVAL `-1` semantics are subtle. Frequency conversion uses `timer_hz >> 20`; precision and zero risks should be considered for unusual clocks. PREEMPT_RT expectations drive hard pinned timer mode.

Test signals: guest clocksource/timer tests, vCPU halt/wakeup, periodic and oneshot timers, migration/save-restore timer state, and blocked vCPU timer expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/tlb.c

Purpose: provides LoongArch KVM TLB invalidation helpers for all guest entries or a single guest physical address.

Important APIs, types, and functions: `kvm_flush_tlb_all()` and `kvm_flush_tlb_gpa(struct kvm_vcpu *vcpu, unsigned long gpa)`.

Control flow: all-entry flush disables local IRQs, issues `invtlb_all(INVTLB_ALLGID)`, and restores IRQ state. GPA flush requires IRQs disabled, masks the GPA to the architecture granularity, and issues `invtlb(INVTLB_GID_ADDR, current GSTAT.GID, gpa)`.

State and persistence: changes processor TLB state only; does not mutate KVM structures.

Dependencies and integration points: used by VPID cycling, CPU virtualization enable/disable, MMU mapping changes, and late vCPU requests.

Risks: wrong GID or address masking can leave stale translations. Caller must satisfy IRQ-disabled assertion for GPA flush.

Test signals: memory remap/dirty-log tests, VPID wrap tests, guest TLB stale mapping stress, and lockdep assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/trace.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/trace.h

Purpose: defines LoongArch KVM tracepoints for guest transitions, exits, GSPR instructions, auxiliary FPU/vector state, IOCSR accesses, and VPID changes.

Important APIs, types, and functions: event classes `kvm_transition` and `kvm_exit`; events `kvm_enter`, `kvm_reenter`, `kvm_out`, `kvm_exit_idle`, `kvm_exit_cache`, `kvm_exit_cpucfg`, `kvm_exit_csr`, `kvm_exit`, `kvm_exit_gspr`, `kvm_aux`, `kvm_iocsr`, and `kvm_vpid_change`. It sets `TRACE_SYSTEM kvm` and includes `trace/define_trace.h`.

Control flow: tracepoint macros define payload fields, fast assignment, symbolic printers, and trace include path/file. `vcpu.c` creates tracepoints by defining `CREATE_TRACE_POINTS` before including this header.

State and persistence: no runtime state beyond trace buffers when enabled. Tracepoint ABI names and fields are observable by tracing tools.

Dependencies and integration points: consumed by `exit.c`, `main.c`, and `vcpu.c`; integrates with Linux ftrace/perf trace infrastructure and generic KVM event namespace.

Risks: tracepoint field or name changes can break tooling. Include guards and `TRACE_HEADER_MULTI_READ` placement must remain compatible with trace generation.

Test signals: successful trace header generation, `tracefs` event availability, and trace output during guest run, exits, IOCSR operations, and VPID changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/vcpu.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/vcpu.c

Purpose: implements the LoongArch KVM vCPU lifecycle, run loop, ioctl register ABI, CPUID mapping, guest/host CSR save/restore, auxiliary FPU/vector/LBT/PMU ownership, PV time, interrupts, and statistics.

Important APIs, types, and functions: public KVM arch hooks include `kvm_arch_vcpu_create()`, `kvm_arch_vcpu_destroy()`, `kvm_arch_vcpu_load()`, `kvm_arch_vcpu_put()`, `kvm_arch_vcpu_ioctl_run()`, `kvm_arch_vcpu_ioctl()`, `kvm_arch_vcpu_unlocked_ioctl()`, reg/FPU/mpstate/debug ioctl helpers, `kvm_arch_vcpu_runnable()`, `kvm_get_vcpu_by_cpuid()`, `kvm_own_fpu()`, `kvm_lose_fpu()`, optional LSX/LASX/LBT ownership, and stats descriptors.

Control flow: the run path completes outstanding MMIO/IOCSR/hypercall exits, loads vCPU state, checks signals and KVM requests, delivers interrupts/exceptions, checks VPID, performs late aux/TLB requests with IRQs disabled, enters guest via `kvm_loongarch_ops->enter_guest()`, and handles exits through the assembly/C loop. ioctl paths read/write GPRs, CSRs, CPUCFG, LBT, KVM counter/debug/reset registers, PV feature attributes, and PV time GPA. Load/put restore/save large sets of guest hardware CSRs and timer state and handle per-CPU `last_vcpu` caching.

State and persistence: per-vCPU state includes GPRs, PC, CSR array, CPUID map entry, FPU/vector/LBT state, PMU state, timer, MMU cache, pending IRQ/exception bitmaps, PV steal-time cache, last CPU, VPID, and aux flags. Per-VM CPUID map and PV feature flags are also mutated.

Dependencies and integration points: integrates with `switch.S`, `exit.c`, `interrupt.c`, `timer.c`, `tlb.c`, `main.c`, generic KVM ioctls, dirty ring, xfer-to-guest work, scheduler steal-time accounting, CPUID/CPUCFG hardware feature probes, and tracepoints.

Risks: CSR save/restore completeness is critical for migration and correctness. Aux ownership must not leak host FPU/vector/LBT/PMU state. CPUID uniqueness is protected by a spinlock and rejects runtime changes. PV feature consistency is enforced VM-wide. The run loop has delicate IRQ/preempt state transitions.

Test signals: KVM API selftests for one-reg/CPUCFG/CSR/FPU/mpstate/debug/interrupt ioctls, guest boot and migration, FPU/LSX/LASX/LBT workloads, PMU passthrough, PV time/preempt tests, dirty ring exits, and CPU hotplug/migration stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/vcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/vm.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kvm/vm.c

Purpose: implements LoongArch VM-level KVM lifecycle, feature discovery, capability reporting, IRQ line handling, and VM statistics.

Important APIs, types, and functions: `kvm_arch_init_vm()`, `kvm_arch_destroy_vm()`, `kvm_vm_ioctl_check_extension()`, `kvm_arch_vm_ioctl()`, `kvm_vm_ioctl_irq_line()`, `kvm_arch_irqchip_in_kernel()`, stats descriptors, and internal `kvm_vm_init_features()`.

Control flow: VM init allocates the GPA shadow PGD, allocates the physical CPUID map, initializes VMCS pointer and feature bitmaps, computes GPA size from `cpu_vabits`, and initializes page-table metadata. VM ioctl reports common LoongArch KVM capabilities and handles `KVM_CREATE_IRQCHIP` as a no-op plus feature attribute probing. IRQ line ioctls route through generic KVM IRQ routing when in-kernel irqchips are present.

State and persistence: per-VM state includes `arch.pgd`, `phyid_map`, feature masks, PV features, GPA size, page-table levels/shifts, invalid PTE tables, and stats counters.

Dependencies and integration points: relies on `mmu.c` for PGD allocation, `main.c` for VMCS initialization, CPU feature probes, generic KVM caps/ioctls, IRQ routing, and in-kernel IPI/EIOINTC/PCH-PIC devices.

Risks: capability reporting must match implemented behavior. GPA size derived from user VA bits constrains memslot creation. Destroy path must release vCPUs before page tables and CPUID map.

Test signals: VM create/destroy, KVM_CHECK_EXTENSION, feature attributes, memslot bounds tests, IRQCHIP creation order, and stats reading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kvm/vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/Makefile

Purpose: selects LoongArch architecture library objects for low-level delay, user access, TLB dump, unaligned helpers, memory/string routines, checksum, int128 shifts, and error injection.

Important APIs, types, and functions: `lib-y` includes `delay.o`, `clear_user.o`, `copy_user.o`, `dump_tlb.o`, and `unaligned.o`; 32-bit builds add byte-swap helpers; 64-bit builds add `memset.o`, `memcpy.o`, `memmove.o`, and `csum.o`; optional objects are `tishift.o` and `error-inject.o`.

Control flow: Kbuild includes objects based on architecture width and config symbols.

State and persistence: build metadata only; it determines which low-level symbols are linked/exported.

Dependencies and integration points: used by generic kernel code, compiler runtime helper references, networking checksum paths, usercopy, and fault/debug infrastructure.

Risks: missing architecture helpers cause link failures or fallback to unsuitable generic routines. Width-specific object selection must match ABI.

Test signals: allnoconfig/defconfig/allmodconfig builds, usercopy tests, networking checksum tests, and compiler-generated int128/bswap references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/bswapdi.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/bswapdi.c

Purpose: supplies the compiler runtime helper `__bswapdi2()` for 64-bit byte swaps on LoongArch 32-bit builds.

Important APIs, types, and functions: `unsigned long long notrace __bswapdi2(unsigned long long u)` returns `___constant_swab64(u)` and is exported.

Control flow: direct pure computation with no branches.

State and persistence: no state.

Dependencies and integration points: used when compiler emits `__bswapdi2` rather than inline byte-swap instructions; exported for modules.

Risks: ABI signature must exactly match compiler expectations. `notrace` avoids tracing recursion in low-level runtime helpers.

Test signals: 32-bit build/link coverage and byte-order unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/bswapdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/bswapsi.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/bswapsi.c

Purpose: supplies the compiler runtime helper `__bswapsi2()` for 32-bit byte swaps.

Important APIs, types, and functions: `unsigned int notrace __bswapsi2(unsigned int u)` returns `___constant_swab32(u)` and is exported.

Control flow: direct pure computation.

State and persistence: no state.

Dependencies and integration points: used for compiler-emitted byte-swap helper calls and exported to modules.

Risks: ABI mismatch would break links or corrupt byte-order conversions. `notrace` prevents instrumentation in a compiler helper.

Test signals: 32-bit builds, module link tests, and byte-swap correctness checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/bswapsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/clear_user.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/clear_user.S

Purpose: implements `__clear_user()` for zeroing user memory with fault recovery and optional fast unaligned 64-bit stores.

Important APIs, types, and functions: exported `__clear_user`, generic byte loop `__clear_user_generic`, and 64-bit `__clear_user_fast` selected through `ALTERNATIVE` when `CPU_FEATURE_UAL` is present.

Control flow: 32-bit or CPUs without unaligned support use byte stores with exception-table recovery. The fast path handles small sizes through a jump table and larger sizes by zeroing the first word, aligning upward, then storing 64/32/16/8-byte chunks plus tail. Exception table entries route faults to fixups that finish byte-wise where possible and return bytes not cleared.

State and persistence: no global state; returns remaining byte count in `a0`.

Dependencies and integration points: called by generic usercopy APIs; depends on alternative patching, exception tables, CPU feature `UAL`, and unwind hints for nonstandard assembly.

Risks: fixup return counts must be exact for usercopy semantics. Fast unaligned stores require CPU support. Jump-table offsets and exception labels are fragile.

Test signals: LKDTM/usercopy tests, fault injection with inaccessible user pages, KASAN/usercopy checks, and CPU feature alternative coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/clear_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/copy_user.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/copy_user.S

Purpose: implements `__copy_user()` for copying between kernel and user memory with exception recovery and optimized 64-bit unaligned copy.

Important APIs, types, and functions: exported `__copy_user`, generic byte implementation `__copy_user_generic`, and 64-bit `__copy_user_fast` selected by `CPU_FEATURE_UAL`.

Control flow: generic path copies byte by byte and returns remaining bytes on fault. Fast path handles sub-9-byte sizes through a jump table, otherwise copies initial and final words, aligns destination, copies 64/32/16/8-byte chunks, and has exception-table fixups for every load/store label. Large fixup computes the remaining destination span and falls back to byte copy until another fault or completion.

State and persistence: no global state; return value is remaining byte count.

Dependencies and integration points: used by generic `copy_{to,from}_user` machinery; depends on exception-table fixups, alternative patching, CPU unaligned support, and ABI register conventions.

Risks: overlapping ranges are not `memmove`; callers must use it as usercopy. Remaining-byte accounting and load/store fault distinction are correctness-critical. Fast path assumes hardware unaligned access.

Test signals: usercopy selftests, page-boundary fault tests, short-size jump-table coverage, and copy_to/from_user stress under SMAP-like protections if applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/copy_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/csum.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/csum.c

Purpose: provides optimized Internet checksum routines for LoongArch, including generic buffer checksum and IPv6 pseudo-header checksum.

Important APIs, types, and functions: `do_csum(const unsigned char *buff, int len)` is marked `__no_sanitize_address`; `csum_ipv6_magic()` is exported. `accumulate()` performs 64-bit one's-complement accumulation with carry.

Control flow: `do_csum()` performs an explicit KASAN read check, rounds the pointer down to an aligned 64-bit boundary, masks leading bytes, accumulates 64-byte chunks using `__uint128_t`, processes remaining 16/8-byte chunks, masks the tail over-read, folds to 16 bits, and swaps for odd alignment. `csum_ipv6_magic()` sums source/destination IPv6 addresses, length, protocol, and input checksum before folding.

State and persistence: no persistent state; pure computations over input buffers.

Dependencies and integration points: used by networking stack checksum paths; depends on KASAN explicit checks, endian helpers, `csum_fold()`, and int128 compiler support.

Risks: intentional over-read is safe only within same cache line/page assumptions and explicit KASAN coverage. Odd-alignment byte order and carry folding are subtle. Compiler codegen for int128 affects performance.

Test signals: networking checksum selftests, IPv4/IPv6 packet checksum validation, KASAN runs, odd/even alignment tests, and fuzzing against generic checksum implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/csum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/delay.c

Purpose: implements busy-wait delay primitives for LoongArch.

Important APIs, types, and functions: exported `__delay(unsigned long cycles)`, `__udelay(unsigned long us)`, and `__ndelay(unsigned long ns)`.

Control flow: `__delay()` snapshots `get_cycles()` and loops with `cpu_relax()` until the requested cycle delta has elapsed. Microsecond and nanosecond helpers scale arguments by constants, `HZ`, and `lpj_fine`, then call `__delay()`.

State and persistence: no owned state; depends on global calibrated `lpj_fine` and cycle counter behavior.

Dependencies and integration points: used by generic delay APIs and low-level timing paths, including KVM timer restore settling.

Risks: busy waits depend on stable cycle counters and calibration. Very short delays are sensitive to multiplication overhead; long delays waste CPU.

Test signals: boot calibration sanity, delay accuracy tests, driver timing behavior, and KVM timer paths that use `__delay()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/dump_tlb.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/dump_tlb.c

Purpose: prints LoongArch TLB register state and active TLB entries for debugging.

Important APIs, types, and functions: `dump_tlb_regs()` prints current TLB-related CSRs. `dump_tlb_all()` calls internal `dump_tlb(first,last)` across `current_cpu_data.tlbsize`.

Control flow: `dump_tlb()` saves current EntryHi/TLBIDX/ASID, iterates indexes, reads each TLB entry, skips invalid or nonmatching ASID entries unless global, prints page size, VA, ASID, physical halves, cache mode, dirty/valid/global, PLV, and 64-bit NR/NX flags, then restores saved CSRs.

State and persistence: temporarily changes TLB index and ASID-related CSRs while dumping, restoring them before return. No persistent state.

Dependencies and integration points: used by architecture debug paths; depends on CSR read/write helpers, `tlb_read()`, current CPU data, and printk.

Risks: dumping changes CPU CSRs transiently and must restore accurately. The local `pa` variable is conditionally initialized for 64-bit paths; build coverage matters. Output under concurrent TLB changes is diagnostic, not atomic.

Test signals: manual debug invocation, build tests for 32/64-bit configs, and verifying CSR state is preserved after dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/dump_tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/error-inject.c

Purpose: implements the LoongArch architecture hook for function error injection by forcing a probed function to return immediately.

Important APIs, types, and functions: `override_function_with_return(struct pt_regs *regs)` sets the instruction pointer to `regs->regs[1]` (return address) and is marked `NOKPROBE_SYMBOL`.

Control flow: when invoked by the error-injection framework, it overwrites PC with RA so execution resumes at the caller.

State and persistence: mutates only the supplied pt_regs PC.

Dependencies and integration points: integrated with Linux error injection and kprobes; depends on LoongArch RA in GPR1 and generic `instruction_pointer_set()`.

Risks: incorrect RA convention would redirect control flow badly. Must not itself be probed to avoid recursion.

Test signals: function error injection selftests and kprobe blacklist validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/memcpy.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/memcpy.S

Purpose: implements optimized LoongArch `memcpy`/`__memcpy` in noinstr text.

Important APIs, types, and functions: exported `memcpy` and alias `__memcpy`; internal `__memcpy_generic`, `__memcpy_small`, and `__memcpy_fast`; all marked not probeable.

Control flow: alternative patching chooses generic byte copy or fast unaligned-capable path. Fast path handles sizes under nine bytes through a jump table, otherwise preloads first/last dwords, aligns destination upward, copies 64/32/16/8-byte chunks, writes first and last dwords, and returns the original destination.

State and persistence: no global state; copies memory only.

Dependencies and integration points: used by core kernel, modules, and generated code. Depends on CPU feature `UAL`, alternative patching, and noinstr/kprobe constraints.

Risks: `memcpy` assumes non-overlap. Fast path intentionally uses unaligned loads/stores only when CPU supports them. Noinstr/probe restrictions protect tracing and early/low-level callers.

Test signals: lib/string selftests, KASAN/KCSAN memory tests, overlapping misuse detection elsewhere, and CPU feature alternative validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/memmove.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/memmove.S

Purpose: implements overlap-safe LoongArch `memmove`/`__memmove`, reusing forward memcpy when possible and reverse copy when necessary.

Important APIs, types, and functions: exported `memmove` and alias `__memmove`; internal `__rmemcpy`, `__rmemcpy_generic`, and `__rmemcpy_fast`.

Control flow: if destination is below source it branches to forward `__memcpy`; if source is below destination it uses reverse copy; equal pointers return. Reverse generic copies bytes from the end. Reverse fast path handles small sizes via `__memcpy_small`, preloads first/last dwords, aligns the end, copies 64/32/16/8-byte chunks backwards, and stores boundary dwords.

State and persistence: no global state.

Dependencies and integration points: used by generic kernel memory movement and depends on `memcpy.S` symbols, alternative patching, and CPU unaligned support.

Risks: boundary stores in reverse fast path must preserve overlap semantics. Fast path must not be selected without unaligned hardware support.

Test signals: string/memmove overlap tests across all size classes and alignments, KASAN runs, and noinstr/probe checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/memmove.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/memset.S

Purpose: implements optimized LoongArch `memset`/`__memset` in noinstr text.

Important APIs, types, and functions: exported `memset` and alias `__memset`; internal `__memset_generic`, `__memset_fast`, and `fill_to_64` macro.

Control flow: alternative patching chooses generic byte stores or fast unaligned stores. Fast path replicates the byte across a 64-bit register, handles small sizes through a jump table, writes first dword, aligns upward, stores 64/32/16/8-byte chunks, and writes the final dword.

State and persistence: no global state; writes memory only.

Dependencies and integration points: used broadly by kernel initialization and runtime memory operations; depends on CPU feature alternatives and noinstr/kprobe annotations.

Risks: fast path uses overlapping boundary stores and unaligned stores; both require correct size handling and CPU support. Byte replication must preserve only the low byte of `c` semantics.

Test signals: lib/string memset tests for size/alignment/value combinations, KASAN, and CPU alternative coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/tishift.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/tishift.S

Purpose: supplies compiler runtime helpers for 128-bit integer shifts on LoongArch.

Important APIs, types, and functions: exported `__ashlti3`, `__ashrti3`, and `__lshrti3` implement arithmetic left, arithmetic right, and logical right shifts for TImode values split across two registers.

Control flow: each helper combines shifts from high and low 64-bit halves, uses mask instructions to select paths for shift counts with bit 64 set, and returns shifted low/high halves in ABI return registers.

State and persistence: no state.

Dependencies and integration points: referenced by compiler-generated code when `CONFIG_ARCH_SUPPORTS_INT128` is enabled and exported for modules.

Risks: boundary shifts around 0, 63, 64, and 127 are the critical cases. ABI register ordering must match compiler expectations.

Test signals: compiler runtime tests for `__int128` shifts, module link tests, and randomized comparison against C reference shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/tishift.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/unaligned.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/lib/unaligned.S

Purpose: provides byte-wise unaligned memory read/write helpers used by the unaligned access emulator.

Important APIs, types, and functions: `unaligned_read(void *addr, void *value, unsigned long n, bool sign)` and `unaligned_write(void *addr, unsigned long value, unsigned long n)` plus shared fault label `.L_fixup_handle_unaligned`.

Control flow: read starts at the last byte, uses signed or unsigned byte load for the highest-order byte based on `sign`, shifts bytes into an integer, stores the result to `value`, and returns zero. Write shifts the source value by 8-bit increments and stores each byte in ascending address order. Zero length returns `-EFAULT`; exception-table entries also return `-EFAULT`.

State and persistence: no global state; writes output value or target bytes.

Dependencies and integration points: called by `kernel/unaligned.c`; depends on LoongArch exception tables and register-size macros for 32/64-bit builds.

Risks: sign extension is implemented by signed loading the final byte; byte order and shifts must match little-endian LoongArch expectations. Faults during output-value store are treated as helper failure.

Test signals: unaligned access emulation tests for sizes 2/4/8, signed and unsigned loads, write byte order, and faulting source/destination addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/lib/unaligned.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/loongarch/mm/Makefile

Purpose: declares LoongArch memory-management object composition.

Important APIs, types, and functions: core objects include `init.o`, `cache.o`, `tlb.o`, `tlbex.o`, `extable.o`, `fault.o`, `ioremap.o`, `maccess.o`, `mmap.o`, `pgtable.o`, `page.o`, and `pageattr.o`; optional objects include `highmem.o`, `hugetlbpage.o`, and `kasan_init.o`. `KASAN_SANITIZE_kasan_init.o := n` disables instrumentation for KASAN bootstrap code.

Control flow: Kbuild selects objects based on `CONFIG_HIGHMEM`, `CONFIG_HUGETLB_PAGE`, and `CONFIG_KASAN`.

State and persistence: build metadata only; determines which MM implementation files are linked.

Dependencies and integration points: connects architecture MM code to generic memory management, KASAN, hugetlb, highmem, exception tables, TLB refill, and page attribute management.

Risks: omitting an object breaks architecture MM functionality or link symbols. KASAN init must remain unsanitized to avoid recursive instrumentation during sanitizer setup.

Test signals: MM config matrix builds, boot memory initialization, KASAN boot tests, hugetlb/highmem tests, page attribute and fault handling selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/Makefile -->
