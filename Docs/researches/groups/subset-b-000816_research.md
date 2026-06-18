<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.c

Purpose: Simulates selected RISC-V branch and PC-relative instructions when kprobes single-step cannot execute the original instruction in place. It updates `pt_regs` as if the probed instruction ran, allowing probes on control-flow instructions.

Important APIs/types/functions: Implements `simulate_jal()`, `simulate_jalr()`, `simulate_auipc()`, `simulate_branch()`, `simulate_c_j()`, `simulate_c_jr()`, `simulate_c_jalr()`, `simulate_c_bnez()`, and `simulate_c_beqz()`. Internal helpers `rv_insn_reg_get_val()` and `rv_insn_reg_set_val()` bridge decoded register numbers to `pt_regs`.

Control flow: Each simulator decodes immediates and register operands with `riscv_insn_*` helpers, validates source/destination registers, writes link or AUIPC results when required, and advances or redirects `regs->epc`. Conditional branches compare decoded register values and choose `addr + offset` or the next instruction length.

State and persistence: The only persistent state is the interrupted register file. The code mutates `regs->epc`, optional destination GPRs, and link registers; it has no global state and returns false when an instruction form or register access is rejected.

Dependencies and integration points: Used by RISC-V kprobe decode tables through `simulate-insn.h`; depends on `<asm/insn.h>`, probe `decode-insn.h`, and the architecture `pt_regs` layout. KUnit kprobe assembly in this subset provides direct behavior coverage for these simulators.

Risks: Wrong immediate sign extension, compressed instruction length, or x0 handling can corrupt the probed control flow. JALR target masking, link address selection, and branch compare signedness are ABI-visible under probes.

Test signals: Probe `jal`, `jalr`, `auipc`, all conditional branch variants, compressed jump/register/branch instructions, x0 destinations, and rejected forms under `CONFIG_RISCV_KPROBES_KUNIT`.

Source read size: 239 lines, 6033 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.h

Purpose: Declares the RISC-V probe instruction simulation interface and macros used to bind decoded instruction patterns to simulator callbacks or explicit rejections.

Important APIs/types/functions: Defines `RISCV_INSN_REJECTED()` and `RISCV_INSN_SET_SIMULATE()` initializer macros, and prototypes for `simulate_auipc()`, `simulate_branch()`, `simulate_jal()`, `simulate_jalr()`, `simulate_c_j()`, `simulate_c_jr()`, `simulate_c_jalr()`, `simulate_c_bnez()`, and `simulate_c_beqz()`.

Control flow: This header has no runtime flow. Its macros generate decode-table entries whose `handler` points to a simulation function and whose `type` marks the instruction as rejected or simulated.

State and persistence: It owns no state; consumers provide opcode, instruction address, and `pt_regs` state to the declared simulator functions.

Dependencies and integration points: Included by RISC-V kprobe decode logic and the simulator C file. It depends on `struct pt_regs`, `struct riscv_probe_insn`, and `INSN_*` probe type constants from neighboring probe headers.

Risks: Macro field names must stay synchronized with the decode-table structure. Missing prototypes or wrong signatures break kprobe simulation at build time.

Test signals: Compile kprobes with compressed and non-compressed ISA configs and run RISC-V kprobe KUnit coverage for every simulator declared here.

Source read size: 33 lines, 1238 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/uprobes.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/uprobes.c

Purpose: Implements RISC-V uprobes architecture hooks: breakpoint recognition, XOL preparation/restoration, single-step completion, return-probe liveness checks, exception notification, and instruction-cache maintenance for copied instruction slots.

Important APIs/types/functions: Provides `is_swbp_insn()`, `is_trap_insn()`, `arch_uprobe_analyze_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_skip_sstep()`, `arch_uprobe_abort_xol()`, `arch_uretprobe_is_alive()`, `arch_uprobe_exception_notify()`, `uprobe_breakpoint_handler()`, `uprobe_single_step_handler()`, and `arch_uprobe_copy_ixol()`.

Control flow: Analyze validates that the instruction can be probed, rejects unsupported compressed/illegal probe cases, stores the original opcode, and sets up the architecture slot. Pre-XOL redirects `epc` to the execute-out-of-line copy while saving the original PC; post-XOL adjusts `epc` back to the probed instruction stream unless a trap was recorded. Exception notifiers route breakpoint and single-step traps to the generic uprobes core.

State and persistence: Per-probe state lives in `struct arch_uprobe`; per-task transient state is stored in `current->utask`, including saved PC and trap number. No global persistent state is introduced.

Dependencies and integration points: Integrates Linux uprobes with RISC-V trap handling (`handle_break()`/single-step paths), `riscv_insn` decoding, copied instruction pages, and instruction-cache flushing.

Risks: Incorrect PC reconstruction after XOL can skip or re-execute user instructions. Return-probe stack checks must handle signal and syscall contexts without resurrecting dead return instances. Cache flush omissions can execute stale copied instructions.

Test signals: User-space uprobes on normal, compressed, branch, and trap instructions; return probes through nested calls; signal delivery during XOL; breakpoint and single-step exception paths; and instruction-cache coherency stress.

Source read size: 182 lines, 3780 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/process.c

Purpose: Supplies RISC-V process and thread lifecycle support: idle, register display, ELF/compat setup, user-thread start state, fork/clone register construction, vector and shadow-stack cleanup, tagged-address controls, and sysctl/init hooks.

Important APIs/types/functions: Key functions include `arch_cpu_idle()`, `set_unalign_ctl()`, `get_unalign_ctl()`, `__show_regs()`, `show_regs()`, `arch_align_stack()`, `compat_elf_check_arch()`, `start_thread()`, `flush_thread()`, `arch_release_task_struct()`, `arch_dup_task_struct()`, `ret_from_fork_kernel()`, `ret_from_fork_user()`, `copy_thread()`, `arch_task_cache_init()`, `set_tagged_addr_ctrl()`, `get_tagged_addr_ctrl()`, and tagged-address sysctl init.

Control flow: New execs clear and initialize pt_regs, status bits, FP/vector/CFI state, and ABI mode before jumping to the user PC/SP. Fork copies architecture thread state, clears child return registers, picks kernel or user fork trampolines, handles `CLONE_SETTLS`, optionally allocates a separate shadow stack, and initializes vector control inheritance. Tagged-address control validates PR flags, PMLEN support, and global disable state before changing per-thread environment configuration.

State and persistence: Persistent state is in `thread_struct`, `thread_info`, pt_regs, vector datap buffers, shadow-stack metadata, `envcfg`, and static tagged-address capability flags. Boot/init code records compat support and tagged-address PMLEN availability.

Dependencies and integration points: Ties scheduler fork/exit, ELF loader, ptrace-visible registers, vector context caches, user CFI shadow stacks, unaligned control, and PR_SET_TAGGED_ADDR_CTRL/PR_GET_TAGGED_ADDR_CTRL ABI together.

Risks: Fork/exec state must not leak FP/vector/CFI state across tasks. Tagged address controls are security-sensitive because they alter accepted user pointer ranges. Shadow-stack allocation failure during clone must unwind correctly.

Test signals: 32-bit compat exec on RV64, clone/fork/vfork with TLS and shadow stacks, vector first-use after fork/exec, tagged-address PRCTL combinations and sysctl disable, register dumps after traps, and unaligned-control PRCTL tests.

Source read size: 446 lines, 11883 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/ptrace.c

Purpose: Implements RISC-V ptrace register access, regset views, kernel stack register queries, vector and CFI regsets, compat regsets, and architecture ptrace request dispatch.

Important APIs/types/functions: Provides GPR/FPR/vector regset get/set helpers, `tagged_addr_ctrl_get/set()`, `riscv_cfi_get/set()`, `riscv_user_regset`, `update_regset_vector_info()`, `regs_query_register_offset()`, `regs_get_kernel_stack_nth()`, `ptrace_disable()`, `arch_ptrace()`, compat GPR regsets, `compat_arch_ptrace()`, and `task_user_regset_view()`.

Control flow: Generic ptrace requests are routed to user-regset helpers. GPR/FPR paths copy `pt_regs` and FP state. Vector access validates vector availability, allocates/copies vstate including datap, rejects invalid vector CSR combinations, and reports active size dynamically. CFI and tagged-address regsets delegate to per-task control helpers.

State and persistence: Ptrace mutates `pt_regs`, `thread.fstate`, `thread.vstate`, tagged-address controls, and user CFI state. Regset metadata is read-mostly but vector size is updated once after hardware VLEN discovery.

Dependencies and integration points: Integrates with ELF core dumps, GDB, signal frame state, vector code, user CFI, compat task mode, and generic `user_regset` infrastructure.

Risks: User-supplied vector CSR state can be inconsistent with hardware constraints; the validation path protects against bad `vtype`, `vl`, `vstart`, and `vcsr`. Regset offsets must match `pt_regs` or debuggers and crash dumps misread state.

Test signals: PTRACE_GETREGSET/SETREGSET for GPR/FPR/vector/CFI/tagged controls, compat tracing, core dump note inspection, invalid vector CSR injection, and ptrace detach clearing single-step state.

Source read size: 637 lines, 16743 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/reset.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/reset.c

Purpose: Provides architecture reset, halt, and power-off entry points for RISC-V and a weak default power-off loop.

Important APIs/types/functions: Defines exported `pm_power_off`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, and internal `default_power_off()`.

Control flow: Restart, halt, and poweroff call `do_kernel_restart()`, `pm_power_off()` when registered, and finally fall back to an infinite wait loop. Firmware-specific reset/poweroff providers, such as SBI SRST, install `pm_power_off` or reboot notifiers elsewhere.

State and persistence: The only global state is the `pm_power_off` function pointer. These paths are terminal and do not persist data.

Dependencies and integration points: Hooks generic kernel reboot/poweroff paths and is completed by platform firmware code in `sbi.c` or board drivers.

Risks: If no firmware power-off implementation registers, halt/poweroff spins forever. Late replacement of `pm_power_off` must be safe for shutdown ordering.

Test signals: Reboot, halt, and poweroff under SBI SRST and under minimal firmware without SRST; confirm registered notifiers run before fallback loops.

Source read size: 34 lines, 529 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/return_address.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/return_address.c

Purpose: Implements `return_address()` for RISC-V by walking stack frames until the requested call depth is reached.

Important APIs/types/functions: Uses `struct return_address_data`, callback `save_return_addr()`, and exported `return_address()`.

Control flow: `return_address()` seeds a skip counter, invokes `walk_stackframe()` on the current task, and the callback records the PC when the requested level is reached.

State and persistence: No persistent state; the result is computed from live frame-pointer stack state.

Dependencies and integration points: Depends on `stacktrace.c` frame walking and is used by generic debugging, tracing, and diagnostics that need caller return PCs.

Risks: Results are only as reliable as frame pointers/unwinder data. Interrupt, exception, and optimized frames can limit depth or return NULL.

Test signals: Build with frame pointers, compare `return_address()` levels against known call chains, and exercise through interrupt and scheduler contexts.

Source read size: 48 lines, 847 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/return_address.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/riscv_ksyms.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/riscv_ksyms.c

Purpose: Exports RISC-V memory helper symbols for modules.

Important APIs/types/functions: Exports `memset`, `memcpy`, `memmove`, `__memset`, `__memcpy`, and `__memmove`.

Control flow: No runtime control flow beyond symbol export table generation.

State and persistence: No state. The file affects module link-time symbol visibility.

Dependencies and integration points: Integrates architecture-provided optimized memory routines with loadable modules and module relocation/linking.

Risks: Exporting the wrong symbol variant can break module resolution or bypass intended optimized implementations.

Test signals: Build/load modules that call standard memory routines and verify kallsyms/module symbol resolution.

Source read size: 17 lines, 362 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/riscv_ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi-ipi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi-ipi.c

Purpose: Connects SBI IPI delivery to the Linux IRQ/IPI framework and advertises when SBI is used for remote fence operations.

Important APIs/types/functions: Defines static key `riscv_sbi_for_rfence`, `sbi_ipi_handle()`, CPU hotplug callback `sbi_ipi_starting_cpu()`, and init entry `sbi_ipi_init()`.

Control flow: Init creates an IPI irq domain/range, registers the SBI IPI handler, and installs a CPUHP startup callback. Incoming SBI IPI interrupts dispatch through `ipi_mux_process()`, while startup enables the per-CPU virq.

State and persistence: Stores the SBI IPI virq and static key. Per-CPU IRQ enablement follows CPU hotplug state.

Dependencies and integration points: Depends on SBI send-IPI support from `sbi.c`, the generic RISC-V IPI multiplexer in `smp.c`, irqdomain descriptors, and CPU hotplug.

Risks: Incorrect virq range setup loses IPIs or remote fences. CPU hotplug ordering must enable the interrupt before the CPU is targeted.

Test signals: SMP boot with SBI IPIs, CPU hotplug, call-function IPIs, reschedule/tick broadcast, remote fence traffic, and interrupt statistics under `/proc/interrupts`.

Source read size: 86 lines, 1974 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi-ipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi.c

Purpose: Implements the RISC-V Supervisor Binary Interface client layer for timers, IPIs, remote fences, firmware features, reset/poweroff, debug console, base extension probing, and legacy v0.1 compatibility.

Important APIs/types/functions: Exposes `sbi_console_putchar/getchar()`, `sbi_shutdown()`, `sbi_set_timer()`, `sbi_send_ipi()`, all `sbi_remote_*fence*()` helpers, `sbi_fwft_set*()`, SRST reboot/poweroff helpers, `sbi_probe_extension()`, firmware ID/version and machine ID getters, `sbi_debug_console_write/read()`, and `sbi_init()`.

Control flow: Initialization probes the SBI spec version, chooses v0.1 or v0.2+ operation tables, discovers supported extensions, installs reset/poweroff hooks, and enables debug console and firmware-feature paths. Runtime helpers translate Linux CPU masks to hart masks, batch remote fence calls over hartmask chunks, and route all work through `__sbi_ecall()`.

State and persistence: Maintains read-mostly spec/implementation metadata, function pointers for timer/IPI/rfence implementations, extension support flags, FWFT availability, and reboot notifier state. Per-call state is in stack-local hart masks and `sbiret` results.

Dependencies and integration points: Central dependency for timer init, SMP/IPI, TLB shootdown, KVM hypervisor fences, suspend/HSM, reset, debug console, and hwprobe machine identifiers.

Risks: v0.1 and v0.2 calling conventions differ sharply; wrong selection breaks early boot. CPU-to-hart mapping and hartmask chunking must not skip offline/large hart IDs. Reset and poweroff behavior is firmware-dependent.

Test signals: Boot on legacy and modern SBI firmware, timer interrupts, SMP IPI/fence stress, SRST reboot/poweroff, DBGC read/write, FWFT feature calls, and KVM HFENCE helpers.

Source read size: 709 lines, 19144 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi_ecall.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi_ecall.c

Purpose: Provides the low-level SBI ecall wrappers used by the higher-level SBI client code and tracepoints.

Important APIs/types/functions: Defines exported `__sbi_base_ecall()` and `__sbi_ecall()`.

Control flow: The wrappers load SBI extension/function IDs and up to six arguments into the RISC-V calling convention, execute `ecall`, collect error/value return registers, and emit SBI tracepoints around the call.

State and persistence: No global state; all state is passed through registers and returned as `long` or `struct sbiret`.

Dependencies and integration points: Used by `sbi.c` for every SBI operation; depends on `<asm/sbi.h>` ABI definitions and `trace/events/sbi.h`.

Risks: Register constraint mistakes corrupt firmware calls. Tracepoint arguments must not perturb call ABI or clobbers.

Test signals: SBI base probe at boot, tracepoint-enabled boot, all higher-level SBI operations, and compiler build coverage across RV32/RV64.

Source read size: 48 lines, 1319 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi_ecall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/setup.c

Purpose: Performs RISC-V architecture setup: memory/resource reservation, DTB parsing, spinlock/static-key policy, command line setup, boot CPU state, initrd/elfcore handling, and late init-memory release.

Important APIs/types/functions: Key functions include `add_resource()`, `add_kernel_resources()`, `init_resources()`, `reserve_memblock_reserved_regions()`, `parse_dtb()`, `riscv_spinlock_init()`, `setup_arch()`, `arch_cpu_is_hotpluggable()`, `free_initmem()`, and kernel-offset panic notifier registration.

Control flow: `setup_arch()` parses firmware tables, initializes CPU features and SBI, sets boot command line, reserves kernel/initrd/crashkernel resources, initializes paging/memblock resources, sets up SMP and signal environment, and finalizes architecture knobs. Resource helpers create standard kernel resource regions and reserve memblock areas in iomem.

State and persistence: Establishes `boot_cpu_hartid`, kernel image/code/data/rodata/bss resources, standard resource arrays, qspinlock static key, command-line memory state, and boot-time notifier registrations.

Dependencies and integration points: Integrates firmware DT/ACPI, memblock, resource tree, paging, SBI, SMP, CPU feature discovery, signal frame sizing, initrd, crash dump metadata, and generic setup.

Risks: Resource overlaps or missed memblock reservations can expose kernel memory as RAM. Spinlock static-key selection must match CPU extension support. DTB parsing errors are early-boot fatal.

Test signals: Boot with DT and ACPI, initrd, crashkernel/elfcorehdr, KASLR offset dumps on panic, qspinlock config combinations, NUMA/memblock layouts, and hotplug-capability checks.

Source read size: 410 lines, 10394 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/signal.c

Purpose: Implements RISC-V signal delivery and `rt_sigreturn`, including FP, vector, and Zicfiss shadow-stack extension records in the user signal frame.

Important APIs/types/functions: Defines `struct rt_sigframe`, FP save/restore helpers, vector and CFI extension save/restore helpers, `restore_sigcontext()`, `get_rt_frame_size()`, `SYSCALL_DEFINE0(rt_sigreturn)`, `setup_sigcontext()`, `setup_rt_frame()`, `handle_signal()`, `arch_do_signal_or_restart()`, `init_rt_signal_env()`, and `sigaltstack_size_valid()`.

Control flow: Signal setup chooses a frame location, copies siginfo/ucontext/mask, saves scalar registers plus optional FP/vector/shadow-stack records, points RA to vDSO `rt_sigreturn`, and redirects EPC to the handler. `rt_sigreturn` validates frame size, restores mask, registers, FP/vector/CFI state, altstack, and returns the restored `a0`. Syscall restart handling rewinds EPC before delivery and finalizes restart/no-restart on return to user mode.

State and persistence: Per-task state touched includes blocked signal mask, pt_regs, FP state, vector datap, active shadow-stack pointer, altstack, and restart block. Read-mostly sizes `riscv_v_sc_size`, `riscv_zicfiss_sc_size`, and `signal_minsigstksz` are initialized at boot.

Dependencies and integration points: Couples generic signal code with vDSO, vector context management, FP save/restore, user CFI shadow stacks, compat signal handling, and syscall restart ABI.

Risks: Signal frame extension parsing is ABI-critical; wrong magic/size validation can corrupt user state or leak kernel data. Shadow-stack token save/restore failures turn into bad frames. Dynamic vector length changes are unsupported and reflected in fixed frame sizing.

Test signals: Signal delivery/return with FP, vector, Zicfiss shadow stacks, altstack minimum sizing, syscall restart under ptrace, malformed frame fuzzing, compat signal frames, and no-MMU sigreturn code flushing.

Source read size: 589 lines, 16802 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/smp.c

Purpose: Implements RISC-V SMP IPI routing, CPU stop/crash coordination, reschedule/call-function/tick broadcast IPIs, backtrace IPIs, and IPI statistics.

Important APIs/types/functions: Defines IPI message types, `__cpuid_to_hartid_map`, `smp_setup_processor_id()`, `riscv_hartid_to_cpuid()`, `send_ipi_mask()`, `handle_IPI()`, `riscv_ipi_enable/disable()`, `riscv_ipi_set_virq_range()`, `show_ipi_stats()`, `arch_send_call_function_ipi_mask()`, `smp_send_stop()`, `crash_smp_send_stop()`, `arch_smp_send_reschedule()`, `arch_trigger_cpumask_backtrace()`, and `kgdb_roundup_cpus()`.

Control flow: IPI senders map logical CPUs to IPI message bits and call the irqchip/SBI-backed send operation. The shared IPI interrupt handler drains pending message bits and dispatches reschedule, call-function, CPU stop, CPU crash-stop, IRQ work, and timer broadcast actions. Stop/crash paths send IPIs, wait for acknowledgements, and report failures.

State and persistence: Keeps CPU-to-hart mapping, per-IPI virq descriptors, per-CPU dummy devices, and crash-stop atomic counters. Pending message bits live in generic IPI mux state.

Dependencies and integration points: Works with `sbi-ipi.c`, irqchip-provided IPI ranges, scheduler reschedule, generic SMP call functions, tick broadcast, crash/kdump, KGDB, and stack backtrace infrastructure.

Risks: Missing IPI virq setup or wrong CPU mask filtering can hang SMP boot, stop_machine, or TLB shootdowns. Crash-stop paths run in fragile contexts and must avoid waiting forever.

Test signals: SMP boot, CPU hotplug, reschedule and call-function stress, tick broadcast, panic/kdump CPU stopping, KGDB roundup, and `/proc/interrupts` IPI counters.

Source read size: 367 lines, 7913 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/smpboot.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/smpboot.c

Purpose: Discovers and starts secondary RISC-V CPUs from device tree or ACPI, prepares SMP boot, and handles secondary CPU entry into the scheduler.

Important APIs/types/functions: Provides `smp_prepare_cpus()`, ACPI RINTC parser, DT CPU parser, `setup_smp()`, `start_secondary_cpu()`, `arch_cpuhp_kick_ap_alive()`, `__cpu_up()`, `smp_cpus_done()`, and `smp_callin()`.

Control flow: Boot parses CPU topology, records hart IDs, skips disabled or invalid CPUs, and initializes CPU operations. CPU bring-up starts the target hart through its CPU ops, waits for `cpu_running`, and secondary entry initializes traps, timers, vector size, MMU/cache state, interrupt handling, and CPU online state before idle.

State and persistence: Maintains `cpu_running` completion, `cpu_count`, CPU maps, and per-CPU hart mappings created during enumeration.

Dependencies and integration points: Depends on firmware CPU ops, SBI/HSM or platform boot methods, DT/ACPI topology, `smp.c` IPI mapping, CPU hotplug, and per-CPU architecture init.

Risks: Duplicate or missing hart IDs break logical CPU mapping. Bring-up timeout leaves CPUs offline. Secondary initialization ordering must install traps/timers before enabling normal scheduling.

Test signals: DT and ACPI SMP boot, disabled CPU nodes, CPU hotplug online/offline, systems with non-contiguous hart IDs, and failure injection in CPU start ops.

Source read size: 264 lines, 5663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/smpboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/soc.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/soc.c

Purpose: Runs early SoC-specific initialization hooks for RISC-V platforms.

Important APIs/types/functions: Provides `soc_early_init()`.

Control flow: Iterates registered `riscv_soc_early_init` callbacks from linker tables and calls each during early boot.

State and persistence: No local state; platform callbacks may initialize SoC-global state.

Dependencies and integration points: Depends on linker-table symbols and platform code that registers early SoC hooks.

Risks: Hook ordering and early-boot constraints are strict; callbacks run before many kernel subsystems are available.

Test signals: Boot platforms with registered SoC hooks and verify early errata/workaround state is installed before CPU feature and driver use.

Source read size: 28 lines, 738 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/stacktrace.c

Purpose: Implements RISC-V kernel and user stack walking, stack display, wait-channel lookup, and user-stack unwinding callbacks.

Important APIs/types/functions: Provides `walk_stackframe()`, `show_stack()`, `get_wchan()` support via `save_wchan()`, `unwind_user_frame()`, and `arch_stack_walk_user()`.

Control flow: Kernel walking starts from pt_regs, current frame pointer, or blocked task frame state, validates each frame pointer against stack bounds, consumes return addresses, and stops on invalid frames or callback termination. User walking validates user frame records with `access_ok()` and copies frame/return PCs from user memory.

State and persistence: No persistent state; it reads task stacks, pt_regs, and frame records. It treats exception-entry ranges specially to avoid reporting internal trampoline PCs.

Dependencies and integration points: Used by `return_address.c`, stack dumps, perf/ftrace-style walkers, scheduler wait-channel reporting, and user stack unwinding.

Risks: Frame-pointer assumptions make unwinding unreliable without proper compiler options. Bad stack validation can read outside task stacks or loop forever; user unwind must handle faults gracefully.

Test signals: Kernel backtraces through normal, interrupt, and exception contexts; blocked-task `wchan`; user stack walking with valid and invalid frame chains; and ORC/fp config variants.

Source read size: 226 lines, 5474 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend.c

Purpose: Implements RISC-V CPU and system suspend support, including CSR save/restore, non-local suspend entry, SBI system suspend, SBI hart suspend, and HSM capability checks.

Important APIs/types/functions: Provides `suspend_save_csrs()`, `suspend_restore_csrs()`, `cpu_suspend()`, SBI system suspend platform ops, `riscv_sbi_hart_suspend()`, `riscv_sbi_suspend_state_is_valid()`, and `riscv_sbi_hsm_is_supported()`.

Control flow: `cpu_suspend()` saves live CPU context, executes a finisher such as SBI hart/system suspend with physical resume address, and restores CSRs/context when firmware returns. System suspend registers platform suspend ops when SBI SUSP is available. Hart suspend validates state IDs and invokes HSM suspend.

State and persistence: Suspend context stores CSRs such as status, envcfg, tvec, ie, scratch, epc, cause, tval, counteren, and sscratch. Global platform ops persist after init.

Dependencies and integration points: Depends on `suspend_entry.S`, SBI HSM/SUSP extensions, CPU context save helpers, PM core, MMU physical address translation, and per-CPU CSR state.

Risks: Missing CSR save/restore can corrupt resumed execution or user feature state. Firmware may not preserve memory/cache state as expected. Resume address must be physical and correctly aligned.

Test signals: CPU idle/suspend-to-RAM on SBI SUSP systems, per-hart suspend states, vector/CFI/envcfg state across suspend, CPU hotplug with HSM, and negative tests for invalid suspend state IDs.

Source read size: 198 lines, 4865 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend_entry.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend_entry.S

Purpose: Provides the low-level RISC-V suspend entry/resume assembly that saves callee-saved registers, switches to the resume path, and restores execution after firmware returns.

Important APIs/types/functions: Defines assembly entry points used by `cpu_suspend()` and the resume path, including register save/restore sequences for `struct suspend_context`.

Control flow: The entry stores stack pointer, return address, and callee-saved registers into the suspend context, calls the supplied finisher, and on resume restores the saved registers and returns to C with the firmware result.

State and persistence: Persists integer register state in the caller-provided suspend context. CSR state is handled by `suspend.c`.

Dependencies and integration points: Paired tightly with C structure offsets from generated asm headers, SBI suspend finishers, and CPU context save/restore rules.

Risks: Offset drift or missing register saves corrupts resumed kernel execution. The code runs with low-level context assumptions where stack and MMU state may be constrained.

Test signals: Suspend/resume cycles with register corruption checks, objdump offset review after structure changes, and RV32/RV64 build coverage.

Source read size: 93 lines, 2489 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/suspend_entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_hwprobe.c

Purpose: Implements the `riscv_hwprobe` syscall and vDSO data cache population so userspace can discover CPU IDs, ISA extensions, cache block sizes, unaligned-access behavior, timebase, virtual-address limits, and vendor extensions across CPU masks.

Important APIs/types/functions: Key helpers include `hwprobe_arch_id()`, `hwprobe_isa_ext0()`, `hwprobe_isa_ext1()`, `hwprobe_misaligned()`, `hwprobe_vec_misaligned()`, `hwprobe_one_pair()`, `hwprobe_get_values()`, `hwprobe_get_cpus()`, async probe registration/completion, `complete_hwprobe_vdso_data()`, `do_riscv_hwprobe()`, and `SYSCALL_DEFINE5(riscv_hwprobe)`.

Control flow: Syscall entry waits once for asynchronous boot probes, then either fills key/value pairs for a CPU mask or filters a CPU mask to CPUs matching requested pairs. Key dispatch computes homogeneous values across online CPUs, clears unsupported or non-common extension bits, and marks unknown keys with `key = -1`. The vDSO cache is filled for all online CPUs and published with a write barrier.

State and persistence: Uses boot-probe completion/atomic state, per-CPU misaligned speed values, global CPU feature bitmaps, `riscv_timebase`, cache block sizes, and vDSO `vdso_arch_data` readiness/homogeneity flags.

Dependencies and integration points: Integrates cpufeature discovery, unaligned-speed probing, vector support, vendor-extension hwprobe files, `vdso/hwprobe.c`, and the userspace syscall ABI documented for RISC-V.

Risks: Reporting an extension without kernel enablement can break userspace. CPU-mask semantics must handle heterogeneous systems, hotplug, invalid keys, and empty masks. vDSO publication ordering is subtle.

Test signals: `riscv_hwprobe` syscall tests for all keys, WHICH_CPUS filtering, heterogeneous CPU masks, unknown keys, vDSO fast path versus syscall fallback, async probe completion, and vendor extension bits.

Source read size: 612 lines, 16448 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_hwprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_riscv.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_riscv.c

Purpose: Implements RISC-V-specific syscalls for `mmap`, `mmap2`, instruction-cache flushing, and the architecture no-syscall wrapper.

Important APIs/types/functions: Provides `riscv_sys_mmap()`, `SYSCALL_DEFINE6(mmap)`, `SYSCALL_DEFINE6(mmap2)`, `SYSCALL_DEFINE3(riscv_flush_icache)`, and `__riscv_sys_ni_syscall()`.

Control flow: `mmap` and `mmap2` normalize page offsets and delegate to `ksys_mmap_pgoff()` after alignment checks. `riscv_flush_icache` validates flags and calls `flush_icache_mm()` for the current mm over the requested range.

State and persistence: Affects VMAs through generic mmap and updates instruction-cache visibility for the current address space; no local persistent state.

Dependencies and integration points: Used by syscall table, vDSO `__vdso_flush_icache`, JIT/self-modifying-code userspace, and generic MM.

Risks: Offset overflow or misalignment must be rejected. I-cache flushing semantics are ABI-visible for JITs and cross-thread execution.

Test signals: mmap/mmap2 ABI tests on RV32/RV64, invalid offset cases, JIT icache flush across threads, and seccomp/syscall-table coverage.

Source read size: 85 lines, 2906 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sys_riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/syscall_table.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/syscall_table.c

Purpose: Builds the RISC-V syscall dispatch table from generated syscall number headers.

Important APIs/types/functions: Defines syscall prototypes through `__SYSCALL` and initializes `sys_call_table[__NR_syscalls]`.

Control flow: No dynamic control flow; compile-time inclusion of `asm/unistd.h` expands native and compat syscall entries into table slots.

State and persistence: Produces the read-only syscall table used by trap/syscall entry.

Dependencies and integration points: Consumed by `do_trap_ecall_u()` in `traps.c` and generated syscall ABI headers.

Risks: Missing or wrong macro expansion breaks syscall numbering or dispatch. Compat/native wrapper naming must match architecture wrappers.

Test signals: Syscall ABI smoke tests, strace table validation, unimplemented syscall behavior, and allmodconfig build coverage.

Source read size: 24 lines, 687 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/syscall_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/Makefile

Purpose: Selects RISC-V kernel self-test subdirectories for module-linking and kprobes KUnit tests.

Important APIs/types/functions: Uses `obj-$(CONFIG_RISCV_MODULE_LINKING_KUNIT)` and `obj-$(CONFIG_RISCV_KPROBES_KUNIT)`.

Control flow: Kbuild descends into enabled test subdirectories based on config.

State and persistence: No runtime state; affects test build composition.

Dependencies and integration points: Integrates RISC-V architecture KUnit tests into the kernel build.

Risks: Wrong config guards silently omit architecture tests.

Test signals: KUnit builds with either or both configs enabled and confirms subdirectory objects are linked.

Source read size: 2 lines, 104 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/Makefile

Purpose: Builds the RISC-V kprobes KUnit module from C and assembly test objects.

Important APIs/types/functions: Defines `kprobes_riscv_kunit-objs := test-kprobes.o test-kprobes-asm.o`.

Control flow: Kbuild links the C test harness and assembly probe target functions when `CONFIG_RISCV_KPROBES_KUNIT` is enabled.

State and persistence: No runtime state in the Makefile itself.

Dependencies and integration points: Ties the kprobes simulator tests to KUnit and the architecture test build.

Risks: Object list drift can produce a test module without probe targets or without the harness.

Test signals: Build and run `kprobes_riscv` KUnit suite.

Source read size: 3 lines, 122 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes-asm.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes-asm.S

Purpose: Provides assembly functions and address tables used to verify that RISC-V kprobes can instrument control-flow and arithmetic instructions without changing architectural results.

Important APIs/types/functions: Defines test functions for add, `jal`, `jalr`, `auipc`, conditional branches, and compressed `c.j`, `c.jr`, `c.jalr`, `c.bnez`, `c.beqz`; also exports address arrays consumed by the KUnit C harness.

Control flow: Each function computes `KPROBE_TEST_MAGIC` only if probed instructions execute or are simulated correctly. Labeled instruction addresses identify probe sites; compressed tests are built only under `CONFIG_RISCV_ISA_C`.

State and persistence: No persistent state; functions return deterministic values in registers.

Dependencies and integration points: Exercises `simulate-insn.c`, kprobe registration, instruction decoding, and compressed instruction support.

Risks: Label drift or assembler relaxation could move probe sites away from intended instructions; `.option norvc` sections guard full-width instruction tests.

Test signals: `kprobes_riscv` KUnit pass across ISA_C on/off, RV32/RV64, and with kprobes placed at every exported address.

Source read size: 231 lines, 4761 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.c

Purpose: Implements the KUnit harness that registers kprobes on the assembly test sites and verifies each target function still returns the magic result.

Important APIs/types/functions: Defines `kprobe_dummy_handler()`, `test_kprobe_riscv()`, KUnit case array, and suite `kprobes_riscv`.

Control flow: The test counts address entries, allocates matching `struct kprobe` objects, registers probes with a dummy pre-handler, calls each assembly function, asserts the expected return value, then unregisters probes and frees memory.

State and persistence: Test-local allocations and registered kprobes are cleaned up before return.

Dependencies and integration points: Depends on KUnit, generic kprobes, and assembly symbols from `test-kprobes-asm.S`.

Risks: Registration failure can leave later expectations noisy; cleanup must unregister every successfully registered probe. The test assumes probe sites are safe for current simulator coverage.

Test signals: KUnit suite result, kprobe registration errors, and function-specific failure messages indicating the broken instruction class.

Source read size: 59 lines, 1252 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.h

Purpose: Declares shared constants and symbols for the RISC-V kprobes KUnit assembly and C harness.

Important APIs/types/functions: Defines `KPROBE_TEST_MAGIC`, lower/upper halves, and extern arrays `test_kprobes_addresses` and `test_kprobes_functions`.

Control flow: No runtime flow; it synchronizes constants between assembly targets and C assertions.

State and persistence: No state.

Dependencies and integration points: Included by both `test-kprobes-asm.S` and `test-kprobes.c`.

Risks: Constant mismatches or missing externs break deterministic test validation.

Test signals: Successful assembly/C compile and KUnit magic-value assertions.

Source read size: 24 lines, 704 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/Makefile

Purpose: Builds the RISC-V module-linking KUnit test module from relocation-specific assembly objects and a C KUnit harness.

Important APIs/types/functions: Defines `test_sub` and `test_set` object groups, optional `test_uleb128.o`, and `test_module_linking-objs`.

Control flow: Kbuild links relocation test objects into one loadable module; ULEB128 tests are included only when assembler support is available.

State and persistence: No runtime state in the Makefile.

Dependencies and integration points: Exercises module loader relocation support for RISC-V-specific relocations.

Risks: Config or object-list errors reduce relocation coverage without obvious runtime failures.

Test signals: Build/load the test module with `CONFIG_RISCV_MODULE_LINKING_KUNIT` and `CONFIG_AS_HAS_ULEB128` variations.

Source read size: 15 lines, 392 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_module_linking_main.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_module_linking_main.c

Purpose: Provides the KUnit harness for RISC-V module relocation/linking tests.

Important APIs/types/functions: Declares relocation test functions, defines `run_test_set()`, `run_test_sub()`, optional `run_test_uleb()`, and suite `riscv_checksum`.

Control flow: Each KUnit case calls assembly helpers that return zero only when the module loader applied the tested relocation correctly, then asserts equality with zero.

State and persistence: The module has no persistent state beyond KUnit registration.

Dependencies and integration points: Integrates architecture relocation assembly with KUnit and module loader relocation code.

Risks: The suite name is generic, and failures map to relocation class only through the helper function name. Optional ULEB coverage depends on assembler capability.

Test signals: KUnit pass/fail per SET, SUB, and ULEB relocation family on RV32/RV64 module loads.

Source read size: 88 lines, 1890 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_module_linking_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set16.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set16.S

Purpose: Tests `R_RISCV_SET16` module relocation handling.

Important APIs/types/functions: Defines global `test_set16`.

Control flow: Loads a relocated 16-bit value from data, computes the low 16 bits of the symbol address, subtracts, and returns zero on correct relocation.

State and persistence: Contains one data word labeled `set16` with a `.reloc` directive.

Dependencies and integration points: Used by the module-linking KUnit harness and RISC-V module loader relocation code.

Risks: RV32/RV64 masking differs; incorrect sign/zero extension can hide relocation errors.

Test signals: `run_test_set()` expects zero from `test_set16()`.

Source read size: 23 lines, 325 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set16.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set32.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set32.S

Purpose: Tests `R_RISCV_SET32` module relocation handling.

Important APIs/types/functions: Defines global `test_set32`.

Control flow: Reads the relocated word, masks the symbol address to 32 bits on RV64, subtracts, and returns zero if relocation was applied correctly.

State and persistence: Contains data label `set32` patched by `.reloc set32, R_RISCV_SET32, set32`.

Dependencies and integration points: Linked into the module relocation KUnit test.

Risks: Width handling must match ELF relocation semantics on RV32 and RV64.

Test signals: `run_test_set()` zero-return assertion.

Source read size: 20 lines, 286 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set6.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set6.S

Purpose: Tests `R_RISCV_SET6` relocation handling for small encoded fields.

Important APIs/types/functions: Defines global `test_set6`.

Control flow: Reads the relocated byte/word value, masks the symbol address down to six bits, subtracts, and returns zero on correct relocation.

State and persistence: Data label `set6` is patched with `R_RISCV_SET6`.

Dependencies and integration points: Exercises module loader support for narrow RISC-V relocation fields.

Risks: Six-bit masking is easy to mishandle across XLEN sizes.

Test signals: `run_test_set()` expects `test_set6()` to return zero.

Source read size: 23 lines, 317 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set6.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set8.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set8.S

Purpose: Tests `R_RISCV_SET8` module relocation handling.

Important APIs/types/functions: Defines global `test_set8`.

Control flow: Reads the relocated data, masks the symbol address to eight bits, subtracts, and returns zero if the loader wrote the expected value.

State and persistence: Data label `set8` carries an `R_RISCV_SET8` relocation.

Dependencies and integration points: Used by the module-linking KUnit suite.

Risks: Byte-width relocation truncation must not sign-extend unexpectedly.

Test signals: `run_test_set()` zero-return assertion.

Source read size: 23 lines, 317 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set8.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub16.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub16.S

Purpose: Tests paired `R_RISCV_ADD16` and `R_RISCV_SUB16` relocations.

Important APIs/types/functions: Defines global `test_sub16`.

Control flow: Two text labels are separated by 32 bytes; the data halfword is relocated as `second - first`. The function subtracts 32 and returns zero on correct relocation.

State and persistence: Contains relocation-patched data label `sub16`.

Dependencies and integration points: Exercises module loader arithmetic relocation handling.

Risks: Signed halfword loads and relocation overflow/truncation can affect results.

Test signals: `run_test_sub()` expects zero from `test_sub16()`.

Source read size: 20 lines, 279 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub16.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub32.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub32.S

Purpose: Tests paired `R_RISCV_ADD32` and `R_RISCV_SUB32` relocations.

Important APIs/types/functions: Defines global `test_sub32`.

Control flow: Relocation data should become the 32-byte distance between `second` and `first`; the function subtracts 32 and returns zero.

State and persistence: Contains word data patched by ADD32/SUB32 relocations.

Dependencies and integration points: Module loader relocation arithmetic.

Risks: Incorrect add/sub ordering or width truncation produces non-zero return.

Test signals: `run_test_sub()` zero-return assertion.

Source read size: 20 lines, 279 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub6.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub6.S

Purpose: Tests `R_RISCV_SET6` plus `R_RISCV_SUB6` relocation behavior for a six-bit field.

Important APIs/types/functions: Defines global `test_sub6`.

Control flow: The relocation sequence writes a six-bit difference between labels spaced by 32 bytes; the function subtracts 32 and returns zero.

State and persistence: Contains byte data label `sub6` patched by paired relocations.

Dependencies and integration points: RISC-V module relocation handler for narrow subtraction forms.

Risks: Narrow relocation ranges and sign extension are fragile.

Test signals: `run_test_sub()` expects zero from `test_sub6()`.

Source read size: 20 lines, 271 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub6.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub64.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub64.S

Purpose: Tests paired `R_RISCV_ADD64` and `R_RISCV_SUB64` relocations.

Important APIs/types/functions: Defines global `test_sub64`.

Control flow: Loads a relocated 64-bit value on RV64 or low word on RV32, subtracts the known 32-byte label distance, and returns zero on correct relocation.

State and persistence: Data label `sub64` is two words patched by ADD64/SUB64.

Dependencies and integration points: Module loader 64-bit relocation arithmetic.

Risks: RV32 handling of a 64-bit relocation test must match what the loader emits and what the test loads.

Test signals: `run_test_sub()` zero-return assertion on both XLEN variants.

Source read size: 25 lines, 336 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub8.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub8.S

Purpose: Tests paired `R_RISCV_ADD8` and `R_RISCV_SUB8` relocations.

Important APIs/types/functions: Defines global `test_sub8`.

Control flow: Relocates a byte with `second - first`, subtracts 32 in the function, and returns zero when relocation is correct.

State and persistence: Contains byte data label `sub8`.

Dependencies and integration points: Module loader support for byte-sized arithmetic relocations.

Risks: Sign extension from `lb` and byte overflow can expose relocation mistakes.

Test signals: `run_test_sub()` expects zero from `test_sub8()`.

Source read size: 20 lines, 271 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub8.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_uleb128.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_uleb128.S

Purpose: Tests RISC-V ULEB128 relocation pairs in modules.

Important APIs/types/functions: Defines `test_uleb_basic()` and `test_uleb_large()`.

Control flow: Two data labels use `R_RISCV_SET_ULEB128` and `R_RISCV_SUB_ULEB128` to encode label distances of 127 and 0x7e8; functions subtract those expected distances and return zero.

State and persistence: Contains relocation-patched data words and padding regions that establish known distances.

Dependencies and integration points: Included only when `CONFIG_AS_HAS_ULEB128` is true and validates module loader ULEB relocation support.

Risks: Variable-length encodings can overflow or be applied with wrong byte counts; assembler support gating is required.

Test signals: Optional `run_test_uleb()` KUnit case passing both basic and large distances.

Source read size: 31 lines, 504 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_uleb128.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/time.c

Purpose: Initializes RISC-V timekeeping from firmware-provided timer frequency.

Important APIs/types/functions: Exports `riscv_timebase` and implements `time_init()`.

Control flow: During boot, `time_init()` reads the `timebase-frequency` from DT/ACPI helpers, stores it in `riscv_timebase`, registers the clocksource, and initializes the timer.

State and persistence: `riscv_timebase` becomes the persistent frequency used by timers and hwprobe.

Dependencies and integration points: Used by clocksource/timer init, SBI timer programming, and `sys_hwprobe.c` time CSR frequency reporting.

Risks: Wrong timebase causes broken scheduler ticks, timers, and userspace time calculations.

Test signals: Boot-time timer frequency logs, clocksource registration, timer interrupt operation, and hwprobe `TIME_CSR_FREQ` consistency.

Source read size: 51 lines, 1213 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/traps.c

Purpose: Handles RISC-V traps, exceptions, breakpoints, syscalls, page faults, IRQ entry, BUG validation, and bad kernel stacks.

Important APIs/types/functions: Key functions include `die()`, `do_trap()`, generated `DO_ERROR_INFO` handlers, `do_trap_insn_illegal()`, misaligned trap dispatchers, `handle_break()`, `do_trap_break()`, `do_trap_ecall_u()`, `handle_user_cfi_violation()`, `do_trap_software_check()`, `do_page_fault()`, `do_irq()`, `is_valid_bugaddr()`, and `handle_bad_stack()`.

Control flow: Synchronous exceptions enter specific handlers that either fix up kernel faults, emulate supported user faults, deliver signals, or die. Illegal instruction traps try vector first-use handling before SIGILL. User ecall advances EPC, dispatches through `sys_call_table`, and enters syscall tracing/audit hooks. Breakpoints route kprobes/uprobes/BPF before SIGTRAP. IRQ entry switches through generic IRQ handling.

State and persistence: Mutates pt_regs, syscall return registers, signal state, probe state, per-CPU overflow stacks, and global `show_unhandled_signals`. It has no durable storage beyond diagnostics.

Dependencies and integration points: Central integration for page fault code, syscall table, kprobes/uprobes, vector first-use, misaligned emulation, user CFI, BPF breakpoints, IRQ subsystem, and oops/panic machinery.

Risks: Trap handlers run in sensitive contexts; wrong EPC advancement can replay or skip instructions. CFI and probe breakpoints must be ordered correctly. Kernel/user mode classification controls whether faults are fixed up or fatal.

Test signals: Syscall tracing, illegal vector first-use, breakpoints with kprobes/uprobes/BPF, misaligned load/store behavior, page fault tests, BUG/oops decoding, bad-stack overflow handling, and CFI violation signals.

Source read size: 486 lines, 12279 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/traps_misaligned.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/traps_misaligned.c

Purpose: Emulates or delegates RISC-V misaligned load/store traps, including scalar, floating-point, vector misalignment probes, unaligned-control availability, and SBI FWFT delegation setup.

Important APIs/types/functions: Provides `handle_misaligned_load()`, `handle_misaligned_store()`, vector/scalar helpers, `check_vector_unaligned_access_emulated*()`, `check_unaligned_access_emulated_all_cpus()`, `unaligned_ctl_available()`, `unaligned_access_init()`, `cpu_online_unaligned_access_init()`, and exported `misaligned_traps_can_delegate()`.

Control flow: Trap handlers decode the faulting instruction, fetch or store bytes with user/kernel access helpers, update integer or FP destination registers, and advance EPC. Boot-time probes intentionally trigger misaligned accesses on CPUs to classify whether traps are emulated. SBI FWFT setup can request firmware delegation of misaligned exceptions per CPU.

State and persistence: Maintains `unaligned_enabled`, `unaligned_ctl`, `misaligned_traps_delegated`, per-CPU scalar/vector misaligned classifications through sibling files, and CPU hotplug setup state.

Dependencies and integration points: Called by `traps.c`, feeds hwprobe and unaligned PRCTL behavior, uses FP access helpers, vector support, SBI FWFT, CPU hotplug, and exception tables.

Risks: Instruction decode coverage is broad and security-sensitive because bad emulation changes user-visible memory/registers. Kernel-mode misaligned faults must not be silently mishandled. Delegation policy differs across firmware.

Test signals: Misaligned scalar/floating/vector load/store tests, PR_UNALIGN controls, hwprobe misaligned reporting, CPU hotplug, SBI FWFT delegation, and fault-injection for inaccessible user memory.

Source read size: 648 lines, 15882 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/traps_misaligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/unaligned_access_speed.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/unaligned_access_speed.c

Purpose: Measures and records scalar and vector unaligned access performance so the kernel and hwprobe can distinguish fast, slow, emulated, unsupported, and unknown behavior.

Important APIs/types/functions: Defines per-CPU `misaligned_access_speed` and `vector_misaligned_access`, boot parameters `unaligned_scalar_speed=` and `unaligned_vector_speed=`, static key `fast_unaligned_access_speed_key`, measurement helpers, CPU hotplug callbacks, and late init `check_unaligned_access_all_cpus()`.

Control flow: Boot or parameter handling sets fixed classifications or schedules per-CPU measurement. Scalar measurement compares aligned versus unaligned copy cycle counts and updates static branches. Vector measurement schedules work per CPU when vector support exists. Hotplug callbacks classify late CPUs and maintain the fast-access static key.

State and persistence: Per-CPU classification variables, `fast_misaligned_access` cpumask, static branch state, and boot-parameter overrides persist after probing.

Dependencies and integration points: Feeds `sys_hwprobe.c`, interacts with `traps_misaligned.c`, vector assembly copy helpers, CPU hotplug, alternatives/static keys, and boot command line.

Risks: Microbenchmarks can be noisy and affect ABI-reported performance. Static key changes must account for heterogeneous CPUs. Vector probing must avoid unsupported traps on CPUs without V.

Test signals: Boot with/without override parameters, heterogeneous CPU hotplug, hwprobe misaligned keys, static-key state inspection, and workloads using optimized unaligned copy branches.

Source read size: 446 lines, 12999 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/unaligned_access_speed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/usercfi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/usercfi.c

Purpose: Implements RISC-V user control-flow integrity management for Zicfiss shadow stacks and Zicfilp landing-pad enforcement.

Important APIs/types/functions: Provides shadow-stack status helpers, active/base setters/getters, `save_user_shstk()`, `restore_user_shstk()`, `SYSCALL_DEFINE3(map_shadow_stack)`, `shstk_alloc_thread_stack()`, `shstk_release()`, `arch_get/set/lock_shadow_stack_status()`, branch landing-pad get/set/lock prctls, `is_user_shstk_enabled()`, `is_user_lpad_enabled()`, and `riscv_nousercfi=` setup.

Control flow: PRCTL paths validate support, lock bits, and requested flags, allocate or release shadow-stack VMAs, update per-thread CFI state, and toggle ENVCFG bits. Signal code saves/restores shadow-stack tokens via AMO operations. Clone allocates separate stacks for CLONE_VM threads while vfork shares parent state.

State and persistence: Per-task `user_cfi_state`, `thread.envcfg`, shadow-stack VMAs, active SSP, lock bits, and global `riscv_nousercfi` command-line mask persist across task operations.

Dependencies and integration points: Integrated with process fork/exit, signal frames, ptrace CFI regset, VM shadow-stack mappings, CSR/ENVCFG handling, and RISC-V CFI CPU feature detection.

Risks: Shadow-stack token writes use privileged user access and must handle faults exactly. Double-unmap and clone/vfork edge cases can corrupt VMAs if state tracking is wrong. Lock semantics are ABI/security sensitive.

Test signals: `map_shadow_stack`, PR_SET/GET/LOCK shadow-stack and landing-pad controls, signal delivery with shadow stacks, clone/vfork/exec/exit cleanup, ptrace CFI regset, command-line disable modes, and faulted token writes.

Source read size: 532 lines, 14725 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/usercfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso.c

Purpose: Maps the RISC-V vDSO and VVAR pages into new user address spaces and initializes native/compat vDSO metadata.

Important APIs/types/functions: Defines `struct __vdso_info`, `vdso_mremap()`, `__vdso_init()`, `vdso_init()`, `__setup_additional_pages()`, `compat_arch_setup_additional_pages()`, and `arch_setup_additional_pages()`.

Control flow: Boot init validates vDSO ELF images, records text/data page counts and offsets, and sets up special mappings. Exec-time setup maps VVAR then vDSO text at randomized addresses, records `mm->context.vdso`, and supports compat mapping when applicable.

State and persistence: Stores read-only vDSO metadata and per-mm vDSO base. VVAR/vDSO mappings persist in each process mm.

Dependencies and integration points: Depends on linker symbols from `vdso.S`/compat images, generic vDSO special mappings, signal code for `rt_sigreturn`, hwprobe vDSO data, and ELF exec.

Risks: Mapping order, offsets, and page permissions are ABI/security sensitive. Remap restrictions must prevent moving special mappings into invalid layouts.

Test signals: Process startup auxv/vDSO presence, `clock_gettime`, `getcpu`, `riscv_hwprobe`, `rt_sigreturn`, compat tasks, ASLR, and mremap rejection tests.

Source read size: 187 lines, 4344 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/Makefile

Purpose: Builds the RISC-V vDSO shared object, debug image, offset header, and wrapper object for native or CFI vDSO variants.

Important APIs/types/functions: Defines `vdso-syms`, C/assembly object lists, `vdso_offsets`, `vdso_o`, `vdso_so`, `vdso_so_dbg`, custom `vdsosym` and `vdsold_and_check` rules, and flags that disable profiling/sanitizers.

Control flow: Kbuild compiles selected vDSO C and assembly with freestanding flags, links `vdso.so.dbg` using `vdso.lds`, strips/debug-links the runtime image, generates offset headers, and embeds the binary through `vdso.S`.

State and persistence: No runtime state; outputs build artifacts consumed by `vdso.c`.

Dependencies and integration points: Works with `gen_vdso_offsets.sh`, vDSO linker script, CFI variant Makefile, getrandom support, compat/nonnative configs, and the top-level architecture build.

Risks: Toolchain flags must prevent instrumentation unsupported in vDSO. Missing offset generation or symbol filtering breaks kernel references to vDSO symbols.

Test signals: vDSO build under RV32/RV64, compat and CFI variants, symbol table inspection, and runtime libc vDSO calls.

Source read size: 105 lines, 3202 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/flush_icache.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/flush_icache.S

Purpose: Provides the vDSO implementation of `__vdso_flush_icache`.

Important APIs/types/functions: Defines `__vdso_flush_icache`.

Control flow: Loads the RISC-V flush-icache syscall number and executes `ecall`, returning the kernel result to userspace.

State and persistence: No local state; it affects instruction-cache coherency through the syscall.

Dependencies and integration points: Exported through vDSO symbol versioning and wraps `riscv_flush_icache` in `sys_riscv.c`.

Risks: Register argument preservation and syscall number must match ABI.

Test signals: Userspace JIT cache flush via vDSO and fallback syscall equivalence.

Source read size: 26 lines, 474 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/flush_icache.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/gen_vdso_offsets.sh -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/gen_vdso_offsets.sh

Purpose: Generates C preprocessor offset macros for symbols in the RISC-V vDSO debug image.

Important APIs/types/functions: Shell script reads `nm` output and emits `#define vdso{suffix}_offset_<symbol> 0x<addr>`.

Control flow: Optional suffix argument changes macro names, then the script filters text/data symbols from stdin/object argument via `${NM}`.

State and persistence: Produces generated header content used at build time; no runtime state.

Dependencies and integration points: Invoked by the vDSO Makefile for native and CFI suffix variants.

Risks: Symbol filtering or suffix changes can break kernel references to vDSO offsets.

Test signals: Generated `include/generated/vdso*-offsets.h` contains expected symbols for vDSO build variants.

Source read size: 7 lines, 175 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/gen_vdso_offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getcpu.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getcpu.S

Purpose: Provides the vDSO `__vdso_getcpu` entry point.

Important APIs/types/functions: Defines `__vdso_getcpu`.

Control flow: Executes the `getcpu` syscall through `ecall` using the architecture syscall number and returns the kernel result.

State and persistence: No local state.

Dependencies and integration points: Exported by vDSO to libc and userspace; kernel side dispatch comes from generic getcpu syscall support.

Risks: vDSO register ABI mismatch causes userspace-visible wrong CPU/node values.

Test signals: libc `sched_getcpu()`/getcpu tests and syscall fallback comparison.

Source read size: 22 lines, 431 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getcpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getrandom.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getrandom.c

Purpose: Includes generic vDSO getrandom implementation for RISC-V.

Important APIs/types/functions: Pulls in `../../../../lib/vdso/getrandom.c`, which defines the vDSO getrandom fast path around VVAR random state.

Control flow: Runtime flow is supplied by the shared implementation: try vDSO random state and fall back to the syscall when unavailable or reseed is needed.

State and persistence: Uses generic vDSO/VVAR random state, not local state in this wrapper.

Dependencies and integration points: Built when `CONFIG_VDSO_GETRANDOM` is enabled and paired with RISC-V ChaCha assembly in `vgetrandom-chacha.S`.

Risks: Architecture wrapper must compile with vDSO restrictions and expose the expected arch ChaCha helper.

Test signals: vDSO getrandom selftests, entropy reseed fallback, and symbol export checks.

Source read size: 10 lines, 336 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/getrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/hwprobe.c

Purpose: Implements the RISC-V vDSO fast path for `riscv_hwprobe` using cached all-CPU values when safe.

Important APIs/types/functions: Defines syscall wrapper `riscv_hwprobe`, helpers `riscv_vdso_get_values()`, `riscv_vdso_get_cpus()`, and `__vdso_riscv_hwprobe()`.

Control flow: The vDSO checks VVAR readiness and homogeneous CPU flags, answers all-CPU value queries from cached `vdso_arch_data`, handles WHICH_CPUS for homogeneous systems, and falls back to the real syscall for unsupported masks, not-ready data, invalid flags, or heterogeneity.

State and persistence: Reads VVAR architecture data populated by `sys_hwprobe.c`; does not mutate persistent state.

Dependencies and integration points: Coupled to `complete_hwprobe_vdso_data()`, hwprobe key layout, VVAR mapping, and vDSO syscall stubs.

Risks: Cached values must be published with correct barriers and invalidated by not-ready flags. Returning cached data for heterogeneous masks would mislead userspace.

Test signals: hwprobe syscall/vDSO parity tests, heterogeneous CPU fallback, invalid key/flag behavior, and VVAR readiness at early process startup.

Source read size: 114 lines, 2909 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/hwprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/note.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/note.S

Purpose: Emits ELF note metadata for the RISC-V vDSO image.

Important APIs/types/functions: Uses `ELFNOTE_START/END` style macros from included headers to describe the Linux vDSO.

Control flow: No runtime control flow; the assembler contributes note sections at build time.

State and persistence: Produces ELF metadata in the vDSO binary.

Dependencies and integration points: Consumed by loaders, debuggers, and vDSO build/link rules.

Risks: Malformed notes can confuse tooling or validation.

Test signals: `readelf -n` on `vdso.so.dbg` and runtime loader acceptance.

Source read size: 15 lines, 369 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/rt_sigreturn.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/rt_sigreturn.S

Purpose: Provides the vDSO `__vdso_rt_sigreturn` trampoline.

Important APIs/types/functions: Defines `__vdso_rt_sigreturn`.

Control flow: Loads the `rt_sigreturn` syscall number and executes `ecall`; normal control does not return except through restored signal context.

State and persistence: Operates on the user signal frame through the kernel syscall path; no local state.

Dependencies and integration points: Signal setup writes this symbol address into user RA for MMU systems.

Risks: The trampoline address and instruction sequence are ABI-critical for signal return, unwinders, and CFI shadow-stack handling.

Test signals: Signal delivery/return, unwinder recognition, vDSO symbol resolution, and malformed signal frame handling.

Source read size: 20 lines, 389 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/rt_sigreturn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/sys_hwprobe.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/sys_hwprobe.S

Purpose: Provides a vDSO-local syscall wrapper symbol for `riscv_hwprobe`.

Important APIs/types/functions: Defines `riscv_hwprobe`.

Control flow: Loads the hwprobe syscall number, executes `ecall`, and returns the kernel result. `vdso/hwprobe.c` calls this when the cache fast path cannot answer.

State and persistence: No local state.

Dependencies and integration points: Tied to `__vdso_riscv_hwprobe()` fallback logic and syscall ABI.

Risks: Wrong symbol visibility or syscall number breaks vDSO fallback.

Test signals: vDSO hwprobe fallback tests for non-homogeneous masks and unsupported flags.

Source read size: 19 lines, 326 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/sys_hwprobe.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vdso.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vdso.S

Purpose: Embeds the built RISC-V vDSO shared object binary into the kernel image.

Important APIs/types/functions: Defines `vdso_start` and `vdso_end` around an `.incbin` of `arch/riscv/kernel/vdso/vdso.so`.

Control flow: No runtime flow; linker symbols bound the binary blob used by `vdso.c`.

State and persistence: The embedded binary persists in the kernel image as read-only data.

Dependencies and integration points: Consumed by `vdso.c` initialization and build rules that create `vdso.so`.

Risks: Path mismatch or missing alignment breaks vDSO initialization.

Test signals: Kernel build links `vdso_start/end`, boot validates vDSO image, and user processes map vDSO successfully.

Source read size: 23 lines, 413 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vdso.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vdso.lds.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vdso.lds.S

Purpose: Linker script for the RISC-V vDSO shared object.

Important APIs/types/functions: Defines ELF sections, dynamic symbol layout, version script inclusion, note/eh_frame/dynamic sections, and discards unsupported sections.

Control flow: Build-time only; controls how vDSO objects are laid out and which symbols are exported.

State and persistence: Produces the runtime vDSO ELF layout mapped into processes.

Dependencies and integration points: Used by vDSO Makefile, symbol versioning, loader expectations, and kernel vDSO validation.

Risks: Section ordering, alignment, and exported symbol mistakes can break dynamic linking, unwinding, or security hardening.

Test signals: `readelf`/`objdump` on vDSO, runtime libc vDSO calls, and build checks for unwanted relocations/sections.

Source read size: 88 lines, 1830 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vgetrandom-chacha.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vgetrandom-chacha.S

Purpose: Provides a no-stack RISC-V assembly implementation of ChaCha20 blocks for vDSO getrandom.

Important APIs/types/functions: Defines `__arch_chacha20_blocks_nostack` and local macros for ChaCha quarter rounds, state registers, rotations, and output stores.

Control flow: Loads ChaCha constants/key/counter, loops over requested blocks, performs 20 rounds via register-only quarter-round operations, writes keystream blocks, increments the counter, and returns without using the stack.

State and persistence: Operates only on caller-provided output, key, counter, and block count. No global state.

Dependencies and integration points: Called by generic vDSO getrandom code; built only in vDSO context with strict ABI/register constraints.

Risks: Cryptographic correctness and register preservation are critical. No-stack constraint leaves little room for spills; counter increment and endian stores must match ChaCha20 spec.

Test signals: vDSO getrandom known-answer tests, randomized output comparison with generic ChaCha, objdump stack-use inspection, and RV32/RV64 build coverage.

Source read size: 252 lines, 5624 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vgetrandom-chacha.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vgettimeofday.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vgettimeofday.c

Purpose: Provides RISC-V vDSO wrappers for time-related functions using the generic vDSO time namespace.

Important APIs/types/functions: Defines `__vdso_clock_gettime()`, `__vdso_gettimeofday()`, and `__vdso_clock_getres()`.

Control flow: Each wrapper delegates to generic `__cvdso_*` helpers that read VVAR clock data and fall back to syscalls when necessary.

State and persistence: Reads VVAR time data maintained by the kernel timekeeping core.

Dependencies and integration points: Built into vDSO and used by libc for fast time queries.

Risks: Type and namespace wrappers must match generic vDSO expectations; stale VVAR data or bad fallback harms time ABI.

Test signals: `clock_gettime`, `gettimeofday`, and `clock_getres` vDSO selftests across clock IDs and fallback paths.

Source read size: 26 lines, 601 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vgettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/Makefile

Purpose: Builds the CFI-protected RISC-V vDSO variant by reusing the normal vDSO sources with altered object/output names.

Important APIs/types/functions: Sets `VDSO_CFI_BUILD := 1`, points `src` at the normal vDSO directory, mirrors C and assembly sources, and includes the normal vDSO Makefile.

Control flow: Kbuild re-enters the vDSO rules with CFI suffixes and source/object mappings.

State and persistence: Build-time only; produces `vdso-cfi` artifacts.

Dependencies and integration points: Depends on the normal vDSO Makefile and `vdso-cfi.S` embed wrapper.

Risks: Source mirroring must stay in lockstep with normal vDSO or CFI builds miss symbols.

Test signals: Build with vDSO CFI enabled, generated offset headers with CFI suffix, and runtime CFI vDSO mapping.

Source read size: 28 lines, 1048 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/vdso-cfi.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/vdso-cfi.S

Purpose: Embeds the CFI vDSO shared object into the kernel under distinct linker symbols.

Important APIs/types/functions: Renames `vdso_start`/`vdso_end` to `vdso_cfi_start`/`vdso_cfi_end` and includes the normal `vdso.S` with path `arch/riscv/kernel/vdso_cfi/vdso-cfi.so`.

Control flow: Build-time include emits an `.incbin` for the CFI image.

State and persistence: CFI vDSO blob is stored in the kernel image.

Dependencies and integration points: Consumed by vDSO setup when mapping CFI-capable tasks.

Risks: Symbol/path mismatch prevents CFI vDSO discovery.

Test signals: CFI vDSO build/link, symbol presence, and process mapping under CFI configuration.

Source read size: 11 lines, 234 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/vdso-cfi.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vec-copy-unaligned.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vec-copy-unaligned.S

Purpose: Provides vectorized helper routines for copying unaligned words and bytes during unaligned-access performance probing.

Important APIs/types/functions: Defines `__riscv_copy_vec_words_unaligned` and `__riscv_copy_vec_bytes_unaligned`.

Control flow: Each routine enables a vector loop, uses vector loads/stores with word or byte element widths, decrements length by processed vector length, and returns after all data is copied.

State and persistence: Mutates only caller-provided destination memory and vector registers; no persistent state.

Dependencies and integration points: Used by `unaligned_access_speed.c` to benchmark vector unaligned access.

Risks: Vector state use must be bracketed by callers so kernel/user vector state is not corrupted. Loop length and element width must handle tails correctly.

Test signals: Vector unaligned speed probe, data integrity comparison, and builds with vector enabled/disabled.

Source read size: 59 lines, 1444 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vec-copy-unaligned.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vector.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vector.c

Purpose: Manages RISC-V vector extension sizing, context caches, first-use traps, per-task vector control PRCTL state, and default vector-access sysctl.

Important APIs/types/functions: Provides exported `riscv_v_vsize`, `riscv_v_setup_vsize()`, `riscv_v_setup_ctx_cache()`, `insn_is_vector()`, `riscv_v_thread_alloc/free()`, `riscv_v_vstate_ctrl_user_allowed()`, `riscv_v_first_use_handler()`, `riscv_v_vstate_ctrl_init()`, `riscv_v_vstate_ctrl_get_current()`, `riscv_v_vstate_ctrl_set_current()`, and sysctl init.

Control flow: Boot probes VLENB, verifies homogeneous vector length, creates user/kernel vector caches, and updates ptrace regset size. First-use traps identify vector instructions, allocate user vector state lazily, enable VS, and resume. PRCTL control enforces current/next/inherit vector access policy across exec/fork.

State and persistence: Keeps global vector size, kmem caches, default implicit-access sysctl, and per-task `vstate`, `kernel_vstate`, and `vstate_ctrl`.

Dependencies and integration points: Integrated with traps, signal frames, ptrace regsets, process fork/exec, T-Head vector compatibility, sysctl, and unaligned vector probing.

Risks: Heterogeneous VLEN is rejected but must be detected early. Lazy allocation failure signals SIGBUS. Incorrect control inheritance changes user ABI and can expose vector state unexpectedly.

Test signals: Vector first-use, PR_RISCV_V controls, sysctl default toggling, signal and ptrace vector state round trips, fork/exec inheritance, and T-Head vector systems.

Source read size: 332 lines, 8065 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions.c

Purpose: Aggregates configured RISC-V vendor ISA extension lists and answers vendor-extension availability queries.

Important APIs/types/functions: Defines `riscv_isa_vendor_ext_list[]` and exported `__riscv_isa_vendor_extension_available()`.

Control flow: The query validates vendor ID and bit, resolves the vendor list, and checks either a specific CPU's vendor extension bitmap or all CPUs when `cpu < 0`.

State and persistence: Uses configured vendor extension list pointers and per-CPU ISA extension bitmaps populated during CPU feature discovery.

Dependencies and integration points: Used by hwprobe vendor extension handlers and any code gating vendor-specific features.

Risks: Vendor ID/list mismatches can report unsupported instructions. All-CPU semantics must clear features absent on any CPU.

Test signals: Vendor extension hwprobe results on Andes, MIPS, SiFive, and T-Head configs; heterogeneous CPU masks; and disabled config builds.

Source read size: 86 lines, 2490 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/Makefile

Purpose: Selects vendor-extension implementation and hwprobe objects for RISC-V builds.

Important APIs/types/functions: Uses `obj-$(CONFIG_RISCV_ISA_VENDOR_EXT_*)` rules for Andes, MIPS, SiFive, and T-Head objects.

Control flow: Kbuild includes vendor extension data and hwprobe files according to enabled configs.

State and persistence: Build-time only.

Dependencies and integration points: Feeds `vendor_extensions.c` aggregate list and `sys_hwprobe.c` vendor key dispatch.

Risks: Missing object selection can make configured extensions undiscoverable.

Test signals: Build each vendor config and query corresponding hwprobe vendor keys.

Source read size: 9 lines, 433 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/andes.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/andes.c

Purpose: Defines Andes vendor ISA extension metadata.

Important APIs/types/functions: Provides `riscv_isa_vendor_ext_andes[]` and `riscv_isa_vendor_ext_list_andes`.

Control flow: No dynamic flow; the table maps Andes extension names/bits for CPU feature discovery.

State and persistence: Static extension data list is consumed by the aggregate vendor extension layer.

Dependencies and integration points: Included when `CONFIG_RISCV_ISA_VENDOR_EXT_ANDES` is enabled.

Risks: Incorrect bit numbers or vendor IDs break extension reporting.

Test signals: Andes extension parsing and availability checks on compatible firmware descriptions.

Source read size: 18 lines, 575 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/andes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips.c

Purpose: Defines MIPS vendor ISA extension metadata for RISC-V.

Important APIs/types/functions: Provides `riscv_isa_vendor_ext_mips[]` and `riscv_isa_vendor_ext_list_mips`.

Control flow: Table-only build-time contribution.

State and persistence: Static vendor extension descriptors persist in the kernel image.

Dependencies and integration points: Used by `vendor_extensions.c` and MIPS hwprobe support.

Risks: Vendor extension bit/table mismatches yield wrong hwprobe reporting.

Test signals: MIPS vendor extension parsing and hwprobe key results.

Source read size: 22 lines, 635 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips_hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips_hwprobe.c

Purpose: Reports MIPS vendor ISA extension bits through the RISC-V hwprobe vendor key.

Important APIs/types/functions: Implements `hwprobe_isa_vendor_ext_mips_0()`.

Control flow: Initializes the hwprobe pair value, checks configured MIPS vendor extension availability over the requested CPU mask, and sets public hwprobe bits for common extensions.

State and persistence: Reads per-CPU/vendor extension state only.

Dependencies and integration points: Called by `sys_hwprobe.c` for `RISCV_HWPROBE_KEY_VENDOR_EXT_MIPS_0`.

Risks: Must expose only extensions common to all CPUs in the mask and only ABI-approved bits.

Test signals: hwprobe vendor MIPS key on systems with and without the advertised extensions.

Source read size: 23 lines, 612 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips_hwprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive.c

Purpose: Defines SiFive vendor ISA extension metadata.

Important APIs/types/functions: Provides `riscv_isa_vendor_ext_sifive[]` and `riscv_isa_vendor_ext_list_sifive`.

Control flow: Table-only metadata used by CPU feature discovery.

State and persistence: Static extension descriptors remain in kernel image.

Dependencies and integration points: Used by vendor extension aggregate and SiFive hwprobe file.

Risks: Table drift from hardware/firmware extension naming breaks discovery.

Test signals: SiFive extension parsing and hwprobe results under `CONFIG_RISCV_ISA_VENDOR_EXT_SIFIVE`.

Source read size: 21 lines, 811 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive_hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive_hwprobe.c

Purpose: Reports SiFive vendor ISA extension bits through hwprobe.

Important APIs/types/functions: Implements `hwprobe_isa_vendor_ext_sifive_0()`.

Control flow: Checks SiFive vendor extension availability across the CPU mask and sets the public hwprobe value for supported common bits.

State and persistence: Reads CPU feature/vendor extension state.

Dependencies and integration points: Dispatched by `sys_hwprobe.c` for `RISCV_HWPROBE_KEY_VENDOR_EXT_SIFIVE_0`.

Risks: Heterogeneous CPU masks must not report extensions missing on one CPU.

Test signals: hwprobe vendor SiFive key with matching and empty extension sets.

Source read size: 22 lines, 642 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive_hwprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead.c

Purpose: Defines T-Head vendor ISA extension metadata and disables T-Head vector support when requested.

Important APIs/types/functions: Provides `riscv_isa_vendor_ext_thead[]`, `riscv_isa_vendor_ext_list_thead`, and `disable_xtheadvector()`.

Control flow: The metadata table feeds discovery. `disable_xtheadvector()` clears the global T-Head vector enable state so generic vector support will not use it.

State and persistence: Static metadata and mutable T-Head vector enable state.

Dependencies and integration points: Used by vector setup, vendor extension aggregate, and T-Head hwprobe.

Risks: Disabling vector too late can leave inconsistent vector sizing/context state.

Test signals: T-Head vector-capable boot, command/config paths that disable xtheadvector, and vendor hwprobe checks.

Source read size: 29 lines, 901 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead_hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead_hwprobe.c

Purpose: Reports T-Head vendor ISA extension bits through hwprobe.

Important APIs/types/functions: Implements `hwprobe_isa_vendor_ext_thead_0()`.

Control flow: Checks T-Head vendor extension availability across requested CPUs and writes public hwprobe bits for extensions common to the mask.

State and persistence: Reads vendor extension bitmaps and T-Head feature state.

Dependencies and integration points: Called by `sys_hwprobe.c` for `RISCV_HWPROBE_KEY_VENDOR_EXT_THEAD_0`.

Risks: Must align with the T-Head extension table and avoid exposing disabled vector behavior.

Test signals: T-Head hardware/firmware hwprobe results, heterogeneous masks, and disabled xtheadvector scenarios.

Source read size: 19 lines, 537 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead_hwprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmcore_info.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vmcore_info.c

Purpose: Emits RISC-V architecture-specific vmcore metadata for crash dump tools.

Important APIs/types/functions: Defines `get_satp_value()` and `arch_crash_save_vmcoreinfo()`.

Control flow: Crash vmcore setup records the current SATP mode/value and architecture constants into VMCOREINFO notes.

State and persistence: Persists metadata in the crash kernel vmcoreinfo note for later dump analysis.

Dependencies and integration points: Used by kdump/crash tooling to interpret RISC-V page tables and memory layout.

Risks: Missing or wrong SATP/page-table metadata makes crash dumps hard or impossible to decode.

Test signals: kdump capture on Sv39/Sv48/Sv57 systems and crash utility page-table interpretation.

Source read size: 31 lines, 1056 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmcore_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux-xip.lds.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux-xip.lds.S

Purpose: Linker script for execute-in-place RISC-V kernel images.

Important APIs/types/functions: Defines XIP-specific section layout, load/virtual addresses, init sections, data/rodata/bss boundaries, exception tables, and discarded sections.

Control flow: Build-time only; the linker lays out the kernel image according to XIP constraints.

State and persistence: Determines persistent symbol addresses and section boundaries used at boot/runtime.

Dependencies and integration points: Used by the architecture build when XIP kernel support is enabled; must match head code, memory mapping, alternatives, init freeing, and module/kallsyms expectations.

Risks: Address or alignment mistakes can make XIP kernels unbootable. Section placement must preserve read-only/data permissions and init discard boundaries.

Test signals: XIP kernel link, boot on XIP-capable platforms, section map inspection, initmem freeing, and relocation checks.

Source read size: 143 lines, 2843 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux-xip.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux.lds.S

Purpose: Main linker script for RISC-V `vmlinux`.

Important APIs/types/functions: Defines kernel text/rodata/data/bss/init layout, PE/EFI and alternative sections, exception tables, percpu areas, BPF/extable metadata, and architecture-specific symbols.

Control flow: Build-time only; controls final kernel image layout consumed by boot and runtime code.

State and persistence: Establishes symbol boundaries used by setup, memory protection, alternatives, module loading, unwinding, and init cleanup.

Dependencies and integration points: Coupled to boot head code, `setup.c` resource reporting, alternatives, vDSO/linker symbols, exception handling, KASAN/KCSAN/CFI sections, and generic vmlinux linker macros.

Risks: Misplaced sections can break boot, permissions, exception fixups, alternatives, or memory freeing. Alignment changes can affect huge-page mappings and KASLR.

Test signals: Full kernel link, boot, section permission checks, exception table fixups, initmem free, kallsyms, and linker map review.

Source read size: 174 lines, 3170 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/Kconfig

Purpose: Defines RISC-V KVM configuration menu entries and dependencies.

Important APIs/types/functions: Sources generic `virt/kvm/Kconfig`, declares `VIRTUALIZATION`, and config `KVM` with dependencies on MMU, OF/ACPI interrupt controllers, SBI, H extension support, and standard KVM selects.

Control flow: Kconfig dependency resolution controls whether RISC-V KVM can be enabled and which support libraries are selected.

State and persistence: Build-time configuration only.

Dependencies and integration points: Connects RISC-V virtualization to generic KVM, perf, irqchip, SBI, AIA/IMSIC, and architecture hypervisor support.

Risks: Incomplete dependencies produce build failures or runtime KVM without required interrupt/timer/hypervisor features.

Test signals: `allyesconfig`/`allmodconfig`, KVM enabled/disabled configs, guest boot under SBI/H extension, and KVM selftests.

Source read size: 40 lines, 965 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/Makefile

Purpose: Builds the RISC-V KVM implementation and selects objects for core, vCPU, MMU, SBI emulation, timers, AIA, and nested/guest support.

Important APIs/types/functions: Defines `obj-$(CONFIG_KVM) += kvm.o` and `kvm-y` object composition for `main.o`, `vcpu.o`, `vcpu_exit.o`, `mmu.o`, `timer.o`, `vcpu_sbi*.o`, `aia*.o`, and related files depending on config.

Control flow: Kbuild links selected RISC-V KVM objects into the architecture KVM module/built-in target.

State and persistence: Build-time composition only.

Dependencies and integration points: Ties Kconfig KVM enablement to the RISC-V KVM source tree and optional AIA/IMSIC support.

Risks: Missing object entries create unresolved symbols or disabled functionality despite config support.

Test signals: KVM module/built-in build, AIA and non-AIA variants, guest boot, KVM selftests, and module load/unload.

Source read size: 44 lines, 923 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/Makefile -->
