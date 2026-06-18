# subset-b-000744 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/signal.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/signal.c` is the native MIPS signal delivery and return implementation. It builds traditional and realtime signal frames, saves and restores integer, DSP, FPU, MSA, and extended context state, selects ABI-specific frame builders through `struct mips_abi`, and handles signal work on return to user mode.

### Important APIs, Types, And Functions
Key frame types are `struct sigframe` and `struct rt_sigframe`. The FPU/MSA path is split between `copy_fp_to_sigcontext()`, `copy_fp_from_sigcontext()`, `save_hw_fp_context()`, `restore_hw_fp_context()`, `save_msa_extcontext()`, `restore_msa_extcontext()`, `save_extcontext()`, and `restore_extcontext()`. Exported or externally used helpers include `protected_save_fp_context()`, `protected_restore_fp_context()`, `setup_sigcontext()`, `restore_sigcontext()`, `fpcsr_pending()`, and `get_sigframe()`. Syscall entry points include legacy `sigsuspend`, legacy `sigaction`, `sys_sigreturn()`, and `sys_rt_sigreturn()`. `handle_signal()`, `do_signal()`, and `do_notify_resume()` are the runtime signal dispatch path.

### Control Flow
Signal delivery starts from `do_notify_resume()` when `_TIF_SIGPENDING` or `_TIF_NOTIFY_SIGNAL` is set. `do_signal()` either restarts an interrupted syscall or obtains a `ksignal`, then `handle_signal()` rolls back delay-slot emulation, rewrites restart state, calls `rseq_signal_deliver()`, and dispatches through the current thread ABI's `setup_frame` or `setup_rt_frame`. Frame setup chooses a user stack via `get_sigframe()`, copies siginfo/ucontext/sigmask, writes handler arguments into `$a0-$a2`, sets `$sp`, `$ra`, `$25`, and `cp0_epc`, then calls `signal_setup_done()`. Signal return validates the user frame, restores the blocked mask and altstack, calls `restore_sigcontext()`, possibly forces a pending FP signal, and jumps to `syscall_exit`.

### State, Persistence, And Dependencies
State is per-task and architectural: `current->thread.abi`, `current->thread.fpu`, FPU owner state, thread flags such as `TIF_32BIT_FPREGS`, `TIF_HYBRID_FPREGS`, MSA live flags, `current->restart_block`, saved signal masks, and user stack frame contents. Persistent user-visible ABI is the exact signal frame layout, `sigcontext` offsets, VDSO return stub offsets, syscall restart semantics, and FP/MSA extended context format. Dependencies include `asm/abi.h`, `asm/fpu.h`, `asm/msa.h`, `asm/dsp.h`, `linux/uaccess.h`, uprobes, rseq, alternate signal stacks, and the MIPS VDSO images.

### Integration Points
This file provides native ABI hooks through `mips_abi`, consumed by thread ABI selection and compat signal files. It integrates with `vdso.c` via `vdso_image` offsets, with `traps.c` through FPU/MSA state and FP exception behavior, with delay-slot emulation through `dsemul_thread_rollback()`, with uprobes through `_TIF_UPROBE`, and with generic signal core functions such as `get_signal()`, `set_current_blocked()`, and `restore_saved_sigmask()`.

### Risks
The highest risk is ABI breakage in frame size, alignment, register offsets, or VDSO return addresses. FPU/MSA save and restore races are subtle because live hardware state, preemption, EVA limitations, and task-owned context may differ. Syscall restart handling must preserve MIPS register conventions, especially `$v0`, `$a3`, and EPC rewind. Bad user pointers must reliably produce `SIGSEGV`, and extended-context parsing must reject malformed sizes or unknown magic values.

### Test Signals
Useful signals are native `sigaction`, `rt_sigaction`, alternate signal stack overflow, interrupted syscall restart with and without `SA_RESTART`, FPU and MSA register preservation across handlers, handler-created FCSR exceptions, malformed sigreturn frames, VDSO sigreturn stubs, uprobes resumption, rseq abort delivery, and 32-bit FP register model cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal32.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/signal32.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/signal32.c` implements small 32-bit compatibility wrappers for classic signal syscalls on a 64-bit MIPS kernel. It translates compat signal action structures and delegates mask suspension to the generic compat realtime implementation.

### Important APIs, Types, And Functions
The file defines the 32-bit handler typedefs `__sighandler32_t` and `vfptr_t`. Runtime entry points are `sys32_sigsuspend()` and `SYSCALL_DEFINE3(32_sigaction, ...)`. The sigaction path uses `struct compat_sigaction`, `struct k_sigaction`, `old_sigset_t`, `do_sigaction()`, and compat-safe handler pointer conversion.

### Control Flow
`sys32_sigsuspend()` directly calls `compat_sys_rt_sigsuspend()` with a compat signal set size. `32_sigaction` validates and copies a 32-bit user action, sign-extends the handler through `s32` to a kernel pointer, converts the one-word legacy mask with `siginitset()`, calls `do_sigaction()`, and if requested writes the old action back in compat layout while zeroing unused mask words.

### State, Persistence, And Dependencies
No durable state is stored in this file. It mutates the current task's signal disposition through the generic signal core. The stable interface is the legacy 32-bit `sigaction` ABI layout and handler pointer representation. Dependencies include `linux/compat.h`, `asm/compat-signal.h`, `asm/syscalls.h`, `linux/uaccess.h`, and `signal-common.h`.

### Integration Points
This file complements `signal_o32.c`, which builds o32 signal frames and implements sigreturn. It plugs compat syscalls into the MIPS syscall table and relies on generic signal action storage for cross-ABI behavior.

### Risks
Pointer sign extension and mask copying are the main compatibility risks. Failing to zero unused mask words can expose stale data or confuse old user programs. Incorrect `access_ok()` coverage would turn user faults into kernel faults.

### Test Signals
Exercise compat `sigaction` install/query, NULL `act` and `oact` combinations, bad user pointers, high-bit handler addresses, legacy one-word masks, and `sigsuspend` interruption on o32/n32 compat tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal_n32.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/signal_n32.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/signal_n32.c` implements realtime signal frame setup and return for the MIPS n32 ABI. n32 uses 32-bit user pointers and compat signal sets with the native 64-bit `struct sigcontext` register representation.

### Important APIs, Types, And Functions
Important types are `struct ucontextn32` and `struct rt_sigframe_n32`. Entry points are `sysn32_rt_sigreturn()` and `setup_rt_frame_n32()`. The exported ABI descriptor is `struct mips_abi mips_abi_n32`, with `restart` set to `__NR_N32_restart_syscall`, native sigcontext offsets, and `vdso_image_n32`.

### Control Flow
Delivery uses `get_sigframe()` from the native signal core, writes compat siginfo through `copy_siginfo_to_user32()`, stores a compat altstack and signal mask, and delegates register/FPU/MSA save to `setup_sigcontext()`. Return reads the frame from the user stack, converts the compat signal mask, restores the blocked mask, restores native sigcontext, restores the compat altstack, and jumps through `syscall_exit`.

### State, Persistence, And Dependencies
The persistent ABI is the n32 realtime frame layout, including 32-bit `uc_link`, `compat_stack_t`, native `struct sigcontext`, and compat sigset placement. Runtime state is per-task signal mask, altstack, current register state, and current ABI descriptor. Dependencies include `asm/abi.h`, `asm/compat-signal.h`, `asm/ucontext.h`, `asm/fpu.h`, VDSO image declarations, and generic compat siginfo conversion.

### Integration Points
`mips_abi_n32` is selected for n32 tasks by the MIPS ABI layer and consumed by `handle_signal()` in `signal.c`. It shares native FP/MSA save and restore helpers with `signal.c` and shares compat sigset conversion conventions with `signal_o32.c`.

### Risks
The main risk is mixing native and compat layout assumptions: sigcontext offsets are native, while siginfo, stack, links, and masks are compat. Wrong restart syscall numbers or VDSO image offsets would break interrupted syscall restart and sigreturn. Bad frame validation must reliably force `SIGSEGV`.

### Test Signals
Test n32 realtime signal delivery, altstack save/restore, interrupted syscall restart, FPU/MSA context preservation, siginfo conversion, invalid frame pointers, and VDSO n32 `rt_sigreturn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal_n32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal_o32.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/signal_o32.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/signal_o32.c` implements legacy and realtime signal frames for the MIPS o32 ABI on 64-bit kernels. It uses `struct sigcontext32` and compat user structures while sharing the common FP save/restore machinery through ABI-specific offsets.

### Important APIs, Types, And Functions
Frame types are `struct sigframe32`, `struct ucontext32`, and `struct rt_sigframe32`. Core helpers are `setup_sigcontext32()`, `restore_sigcontext32()`, `setup_frame_32()`, `setup_rt_frame_32()`, `sys32_sigreturn()`, and `sys32_rt_sigreturn()`. The ABI descriptor is `mips_abi_32`, with `__NR_O32_restart_syscall`, compat sigcontext offsets, and `vdso_image_o32`.

### Control Flow
Frame setup obtains an aligned user frame with `get_sigframe()`, copies GPRs, HI/LO, optional DSP accumulators, protected FP context, compat sigmask, and optional compat siginfo/ucontext. It then places handler arguments in `$a0-$a2`, sets `$sp`, `$ra`, `$25`, and EPC. Return paths validate the frame on `$sp`, copy back the compat mask, restore registers and FP state with `restore_sigcontext32()`, restore altstack for realtime frames, and transfer to `syscall_exit`.

### State, Persistence, And Dependencies
State is the user-visible o32 signal ABI: frame padding, argument-save slots, compat signal mask conversion, `struct sigcontext32` offsets, and o32 VDSO sigreturn locations. Runtime state includes the current thread register frame, DSP registers, FPU/MSA context, blocked mask, and altstack. Dependencies include `asm/compat-signal.h`, `asm/dsp.h`, `asm/sim.h`, `asm/syscalls.h`, `signal-common.h`, and native protected FP helpers from `signal.c`.

### Integration Points
The ABI descriptor is used by native `signal.c` dispatch for o32 tasks. This file pairs with `signal32.c` for compat sigaction/sigsuspend and with `vdso.c` for the o32 VDSO image. It also integrates with DSP and FPU context management in `traps.c`.

### Risks
o32 layout is especially sensitive because old user programs depend on the legacy frame and argument-save area. DSP fields must only be touched when the CPU supports DSP. Compat mask conversion and handler pointer sizes must remain exact. `restore_sigcontext32()` changes control registers from user memory, so malformed frames must be caught before returning to user mode.

### Test Signals
Exercise legacy and realtime o32 handlers, `sigreturn` and `rt_sigreturn`, alternate stacks, DSP register preservation, FPU/MSA preservation through compat offsets, bad sigreturn frames, old one-word signal masks, and restart syscall number behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal_o32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp-bmips.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/smp-bmips.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/smp-bmips.c` provides SMP, hotplug, IPI, reset-vector relocation, and CPU setup support for Broadcom BMIPS processors. It handles BMIPS43xx race-prone software interrupts, BMIPS5000 raceless action-register IPIs, warm restart, and platform vector relocation used by secondary CPU boot.

### Important APIs, Types, And Functions
Platform globals include `bmips_smp_enabled`, `bmips_cpu_offset`, `bmips_booted_mask`, `bmips_tp1_irqs`, `bmips_smp_boot_sp`, and `bmips_smp_boot_gp`. Core functions include `bmips_smp_setup()`, `bmips_prepare_cpus()`, `bmips_boot_secondary()`, `bmips_init_secondary()`, `bmips_smp_finish()`, `bmips_cpu_disable()`, `play_dead()`, `bmips_ebase_setup()`, `bmips_cpu_setup()`, and reset vector helpers. Published `plat_smp_ops` are `bmips43xx_smp_ops` and `bmips5000_smp_ops`.

### Control Flow
Setup detects CPU type, configures CMT or BMIPS5000 mode registers, computes logical CPU maps, sets `board_ebase_setup`, and marks CPUs possible/present. CPU preparation requests two per-CPU software IRQs. Booting a secondary writes the idle task stack and thread_info GP to global handoff variables, programs reset vectors to KSEG0 or KSEG1 paths depending on first boot versus warm boot, and triggers reset or IPI action. The secondary clears pending IPIs, performs BMIPS CPU setup, enables interrupts in `bmips_smp_finish()`, and joins generic `start_secondary()`. Hotplug disables the CPU, migrates IRQs, flushes TLB/icache, enters `play_dead()`, waits for an IPI, and jumps through `bmips_secondary_reentry`.

### State, Persistence, And Dependencies
State is CP0 Broadcom registers, CBR memory-mapped registers, per-CPU IPI action masks, reset vector slots, boot stack globals, and CPU online/present maps. Nothing is persisted outside hardware register state and kernel topology. Dependencies include `asm/bmips.h`, `asm/traps.h`, `asm/cacheflush.h`, `asm/tlbflush.h`, `linux/irq.h`, hotplug, kexec, and assembly vectors such as `bmips_reset_nmi_vec` and `bmips_smp_int_vec`.

### Integration Points
This file registers platform SMP operations consumed by generic `smp.c`. It hooks board exception base setup via `board_ebase_setup`, NMI setup via `board_nmi_handler_setup`, and kexec through `kexec_nonboot_cpu_jump`. It shares interrupt actions with generic scheduler and call-function IPI handlers.

### Risks
Race-prone BMIPS43xx IPI handling depends on `ipi_lock` covering CP0 Cause writes and action masks. Reset vector writes must happen on CPU0 for BMIPS5000 and must use hazards/syncs. Boot stack handoff requires memory barriers. Hotplug must not leave active interrupts or stale cache/TLB state. CPU type conditionals are hardware-specific and easy to regress on older BMIPS variants.

### Test Signals
Test BMIPS43xx and BMIPS5000 boot, repeated CPU offline/online, IPI reschedule and call-function delivery, warm restart after hotplug, kexec nonboot CPU paths, relocated exception vectors, RAC setup, and systems booting on TP0 versus TP1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp-bmips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp-cps.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/smp-cps.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/smp-cps.c` implements SMP support for MIPS Coherent Processing System machines. It discovers cluster/core/VPE topology, allocates and installs reset vectors, boots cores and VPEs through CM/CPC/GIC hardware, maintains per-cluster boot configuration, and supports hotplug and kexec shutdown.

### Important APIs, Types, And Functions
Important state includes `core_entry_reg`, `cps_vec_pa`, and `mips_cps_cluster_bootcfg`. Setup functions include `power_up_other_cluster()`, `core_vpe_count()`, `mips_cps_build_core_entry()`, `check_64bit_reset()`, `allocate_cps_vecs()`, `setup_cps_vecs()`, `cps_smp_setup()`, and `cps_prepare_cpus()`. Boot and runtime functions include `init_cluster_l2()`, `boot_core()`, `remote_vpe_boot()`, `cps_boot_secondary()`, `cps_init_secondary()`, and `cps_smp_finish()`. Hotplug/kexec functions include `cps_cpu_disable()`, `play_dead()`, `wait_for_sibling_halt()`, `cps_cleanup_dead_cpu()`, and `cps_kexec_nonboot_cpu()`. Registration is via `register_cps_smp_ops()` and `mips_cps_smp_in_use()`.

### Control Flow
Early setup reads CPS topology, powers up clusters when needed, records cluster/core/VPE IDs into `cpu_data`, sets coherent CCA, initializes core 0, allocates BEV reset vectors, and writes BEV base on CM3+ systems. Preparation validates coherent CCA and dcache aliasing constraints, builds vector code and exception copies, allocates per-cluster/core/VPE boot configuration, and marks boot CPU state. Booting a CPU fills `vpe_boot_config` with `smp_bootstrap`, stack, and GP, then either resets a powered-down core, asks a sibling CPU to boot a VPE, or boots a local VPE. Hotplug subtracts the VPE from the live mask, marks the CPU offline, then either halts a VPE or power-gates the whole core; cleanup waits for the observed halt or power state.

### State, Persistence, And Dependencies
State lives in CM/CPC/GIC registers, reset vector memory allocated by memblock, `cluster_boot_config` and nested core/VPE arrays, core power bitmaps, atomic VPE masks, CPU topology fields, and the `__cpu_primary_thread_mask`. Dependencies include `asm/mips-cps.h`, `asm/pm-cps.h`, `asm/uasm.h`, `asm/mips_mt.h`, `asm/bcache.h`, GIC interrupts, memblock, hotplug, and the generic MIPS SMP ops interface.

### Integration Points
The file provides `cps_smp_ops` to `register_smp_ops()`, uses generic IPI senders from `smp.c`, consumes `smp_max_threads` and topology maps from generic SMP code, and calls CPS PM support for power gating. It must align with exception-vector handling in `traps.c` because reset vectors copy TLB/cache/general exception stubs.

### Risks
Hardware sequencing is the main risk: reset vector physical address limits, 64-bit reset base support, CM/CPC locking, VP run/stop ordering, L2 state machine initialization, and cross-cluster register mirroring must be exact. Allocation failure disables SMP by clearing present CPUs, so partial allocation cleanup must be correct. Hotplug races with re-online and sibling power-down are explicitly handled but sensitive to shared globals `cpu_death` and `cpu_death_sibling`.

### Test Signals
Use CPS systems with multiple clusters, multiple cores, multiple VPEs, CM2 versus CM3/CM3.5, CPC present and absent, GIC present checks, CCA mismatch, dcache aliasing, CPU hotplug under load, kexec, FPU affinity on MT systems, and reset vector allocation above and below KSEG1 limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp-cps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp-mt.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/smp-mt.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/smp-mt.c` implements virtual SMP over MIPS MT VPEs and TCs. It configures thread contexts, maps each VPE to a logical CPU, and boots secondary VPEs by programming TC restart, stack, GP, status, and VPE activation registers.

### Important APIs, Types, And Functions
Key functions are `smvp_copy_vpe_config()`, `smvp_vpe_init()`, `smvp_tc_init()`, `vsmp_init_secondary()`, `vsmp_smp_finish()`, `vsmp_boot_secondary()`, `vsmp_smp_setup()`, and `vsmp_prepare_cpus()`. The exported platform operations object is `vsmp_smp_ops`.

### Control Flow
Setup disables VPEs and MT, enters MVP configuration state, reads `MVPConf0`, derives TC and VPE counts, sets `smp_num_siblings`, initializes each TC as halted/non-allocatable, deactivates nonboot VPEs, copies CP0 status/config/count/config7 to secondary VPEs, and records CPU maps. Booting a secondary disables VPE scheduling, selects the target TC, writes `smp_bootstrap` as restart PC, marks the TC active, unhalts it, enables the VPE, writes stack and GP, flushes the thread_info cache range, exits configuration state, and re-enables VPE execution.

### State, Persistence, And Dependencies
State is in MIPS MT CP0/VPE/TC registers, `cpu_data` VPE IDs, `__cpu_number_map`, `__cpu_logical_map`, `smp_num_siblings`, and optional `mt_fpu_cpumask`. Dependencies include `asm/mipsmtregs.h`, `asm/mips_mt.h`, generic MIPS IPI functions, GIC presence, FPU affinity support, and generic SMP startup.

### Integration Points
`vsmp_smp_ops` is registered by platform code and then consumed by generic `smp.c`. It uses `mips_mt_set_cpuoptions()` for MT user-accessible behavior, generic IPI senders for reschedule/call-function interrupts, and `start_secondary()` after `smp_bootstrap`.

### Risks
Programming MT configuration registers while interrupts or VPE scheduling are active can hang the system. CPU-to-TC/VPE one-to-one assumptions must match hardware. `smp_max_threads` limiting must not leave maps inconsistent. FPU affinity masks need correct enrollment for systems with fewer FPU contexts than VPEs.

### Test Signals
Test MT-capable Malta or similar systems with varying `smt=` and `nosmt`, secondary VPE boot, call-function IPIs, timer/performance interrupt masks with and without GIC, and workloads that trigger FPU affinity migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp-mt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp-up.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/smp-up.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/smp-up.c` provides a `plat_smp_ops` implementation for uniprocessor builds or platforms running without usable SMP. It is a stub layer that satisfies the generic SMP ops interface while making impossible IPI paths fail loudly.

### Important APIs, Types, And Functions
The file defines `up_send_ipi_single()`, `up_send_ipi_mask()`, `up_init_secondary()`, `up_smp_finish()`, `up_boot_secondary()`, `up_smp_setup()`, `up_prepare_cpus()`, optional hotplug stubs `up_cpu_disable()` and `up_cpu_die()`, and the exported `up_smp_ops` structure.

### Control Flow
Most hooks are empty. `boot_secondary()` returns success even though no secondary CPU is expected. IPI senders call `panic()` because any attempt to send an IPI in UP mode indicates broken topology or caller assumptions. Hotplug disable returns `-ENOSYS`, and `cpu_die()` bugs if reached.

### State, Persistence, And Dependencies
No state is maintained. The only dependency is the generic SMP ops contract and basic kernel headers. There is no persistence beyond the selected platform ops pointer.

### Integration Points
This object can be registered as `mp_ops` for UP-style systems so generic MIPS SMP setup code has function pointers. It deliberately prevents silent success for IPIs.

### Risks
The primary risk is accidentally selecting this ops table on a system with more than one online CPU, which would panic on IPI. Returning success from `boot_secondary()` is only acceptable because no secondary should be present.

### Test Signals
Boot a UP kernel, confirm only CPU0 is possible/online, verify no generic IPI paths are invoked, and ensure CPU hotplug is unavailable when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp-up.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/smp.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/smp.c` is the generic MIPS SMP core. It maintains CPU topology maps, registers platform SMP operations, allocates generic IPI IRQs, runs secondary CPU startup, implements stop and hotplug glue, and provides SMP-aware TLB shootdown routines.

### Important APIs, Types, And Functions
Global maps include `__cpu_number_map`, `__cpu_logical_map`, `smp_num_siblings`, `cpu_sibling_map`, `cpu_core_map`, `cpu_foreign_map`, `cpu_coherent_mask`, and `__cpu_primary_thread_mask`. Important functions include `register_smp_ops()`, `mips_smp_send_ipi_single()`, `mips_smp_send_ipi_mask()`, `mips_smp_ipi_allocate()`, `mips_smp_ipi_free()`, `start_secondary()`, `smp_prepare_cpus()`, `smp_prepare_boot_cpu()`, `__cpu_up()` or `arch_cpuhp_kick_ap_alive()`, TLB flush entry points, and `tick_broadcast()`.

### Control Flow
Boot CPU setup records CPU0 online and possible, then `smp_prepare_cpus()` initializes boot mm context, calls platform `prepare_cpus`, builds sibling/core maps, and initializes coherent masks. `start_secondary()` probes CPU state, installs traps, initializes clockevents and MAARs, calls platform secondary hooks, calibrates delay, updates topology, synchronizes Count registers, marks the CPU online, and enters idle. Generic IPI allocation finds an IPI irqdomain and reserves call and reschedule IRQs. TLB flushes choose between MMID/GINV global invalidation, IPIs to other CPUs, ASID context invalidation, and local flushes depending on CPU capability and mm sharing.

### State, Persistence, And Dependencies
State is in global CPU maps, IRQ descriptors for call/reschedule IPIs, completions for AP startup, per-CPU call-single data for tick broadcast, and mm ASID context arrays. Dependencies include `asm/mips-cps.h`, `asm/ginvt.h`, `asm/mmu_context.h`, `asm/time.h`, `asm/maar.h`, irq domains, OF IRQ lookup, CPU hotplug, and generic TLB/cache primitives.

### Integration Points
Platform files such as `smp-cps.c`, `smp-mt.c`, `smp-bmips.c`, and `smp-up.c` register `mp_ops`. Trap initialization, timer initialization, count synchronization, scheduler IPIs, generic `smp_call_function`, CPU hotplug, and MM/TLB code all converge here.

### Risks
Topology map correctness affects scheduling, IPI fanout, and TLB shootdown. IPI domain handling must degrade safely on true UP systems and fail on broken multi-CPU configurations. Secondary startup completion ordering protects the boot CPU from proceeding before counter sync and online marking. TLB flush paths are architecture-sensitive: MMID/GINV, ASID invalidation, executable VMA icache assumptions, and preemption boundaries must remain correct.

### Test Signals
Test CPU bring-up, CPU hotplug, call-function and reschedule IPIs, `nosmt` and `smt=N`, TLB flushes for single-threaded and multithreaded mms, executable VMA invalidation, kernel range flushes, MMID-capable systems, GINV-capable systems, and tick broadcast on broadcast-clockevent configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/spinlock_test.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/spinlock_test.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/spinlock_test.c` exposes debugfs microbenchmarks for raw spinlock overhead on MIPS. It measures a single-thread lock/unlock loop and a two-thread contended lock/unlock loop.

### Important APIs, Types, And Functions
Important functions are `ss_get()`, `multi_other()`, `multi_get()`, and `spinlock_test()`. Types are `struct spin_multi_state` and `struct spin_multi_per_thread`. Debugfs attributes are `fops_ss` and `fops_multi`.

### Control Flow
Reading `spin_single` runs one million raw spinlock acquire/release iterations and returns elapsed microseconds. Reading `spin_multi` initializes shared state, spawns a kernel thread, synchronizes both participants with atomics, has both contend on one raw spinlock for one million iterations each, waits for both to exit, and returns elapsed microseconds from the common start.

### State, Persistence, And Dependencies
State is transient in stack-allocated benchmark structs and one spawned kthread. Debugfs files are registered at device init under `mips_debugfs_dir`. Dependencies include `linux/debugfs.h`, `linux/kthread.h`, `linux/hrtimer.h`, raw spinlocks, and MIPS debugfs setup.

### Integration Points
The file is a diagnostic helper only. It integrates with debugfs and can be used to compare spinlock behavior across CPU models, SMP configurations, or lock implementation changes.

### Risks
The busy-wait synchronization loops intentionally burn CPU and are unsafe as general synchronization examples. `kthread_run()` return handling is absent, and `debugfs_create_file_unsafe()` exposes benchmark callbacks that run in reader context. It should not be enabled or used as a production performance interface.

### Test Signals
Read `spin_single` and `spin_multi` from debugfs on UP and SMP systems, check for hangs under CPU hotplug, compare values before and after raw spinlock changes, and verify debugfs absence when debugfs is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/spinlock_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/spram.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/spram.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/spram.c` probes and configures MIPS instruction and data scratchpad RAM for CPUs that expose SPRAM tags through cache tag operations and ErrCtl access mode.

### Important APIs, Types, And Functions
Important helpers are `bis_c0_errctl()`, `ispram_store_tag()`, `ispram_load_tag()`, `dspram_store_tag()`, `dspram_load_tag()`, `probe_spram()`, and `spram_config()`. The code uses tag constants such as `SPRAM_TAG0_ENABLE`, `SPRAM_TAG0_PA_MASK`, and `SPRAM_TAG1_SIZE_MASK`.

### Control Flow
`spram_config()` checks CPU type and Config bits for instruction/data SPRAM. For each present SPRAM type, `probe_spram()` walks up to eight tag pairs, derives size from tag1, aligns the requested base, writes a new physical base with enable bit to tag0, rereads the tag, and logs the resulting physical address and size. DSPRAM is additionally tested by writing and reading a CKSEG1 pattern.

### State, Persistence, And Dependencies
State is hardware tag state for ISPRAM/DSPRAM and CP0 ErrCtl. The configured physical base persists for the running kernel until reset or reprogramming. Dependencies include CP0 tag registers, cache `Index_Load_Tag_*` and `Index_Store_Tag_*` operations, hazard barriers, `asm/r4kcache.h`, and CPU-type/config feature bits.

### Integration Points
This is called from MIPS platform setup paths when scratchpad RAM needs configuration. It interacts with cache/TLB address spaces and platform-specific physical map assumptions, with comments noting Malta-specific base addresses.

### Risks
Incorrect tag semantics or base alignment can misconfigure scratchpad memory. The probe loop has an arbitrary bound to avoid runaway on unsupported implementations. DSPRAM read/write testing touches physical memory via CKSEG1 and can reveal bus or mapping problems. CPU-specific assumptions are narrow.

### Test Signals
Boot CPUs with ISP/DSP Config bits, confirm log output for expected SPRAM regions, validate DSPRAM pattern writes, test unsupported CPUs for no-op behavior, and check hazard-sensitive regressions after cache/tag changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/spram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/stacktrace.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/stacktrace.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/stacktrace.c` implements the MIPS `save_stack_trace()` API. It records kernel return addresses either by raw stack scanning or by the MIPS unwinder when kallsyms and valid kernel PCs are available.

### Important APIs, Types, And Functions
Core helpers are `save_raw_context_stack()`, `save_context_stack()`, `save_stack_trace()`, and `save_stack_trace_tsk()`. It uses `struct stack_trace`, `struct pt_regs`, `prepare_frametrace()`, `unwind_stack()`, `__kernel_text_address()`, and `in_sched_functions()`.

### Control Flow
For the current task, `save_stack_trace_tsk()` synthesizes pt_regs through `prepare_frametrace()`. For another task, it reads saved stack pointer and return address from `task_struct.thread`. `save_context_stack()` either raw-scans stack words for kernel text addresses or walks frames with `unwind_stack()`, honoring `trace->skip`, `trace->max_entries`, and the `savesched` filtering flag.

### State, Persistence, And Dependencies
No durable state is changed. Output is the caller-provided `stack_trace` buffer. Dependencies include MIPS stack unwinder state, `raw_show_trace` from `traps.c`, task stack layout, `THREAD_SIZE`, and scheduler-function filtering.

### Integration Points
This file supports generic stacktrace users such as lockdep, tracing, debugging, and profiling. It shares unwind behavior with `traps.c` register dumps and respects the same raw trace mode.

### Risks
Raw scanning can miss frames or include false positives. Saved context for non-current tasks may be stale. The function warns if the caller provides a non-empty or zero-sized trace. Stack bounds checks are essential before raw scanning a task stack.

### Test Signals
Collect stack traces from current and sleeping tasks, with and without kallsyms, with `raw_show_trace`, with scheduler-frame filtering, and with shallow `max_entries` plus nonzero `skip`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/sync-r4k.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/sync-r4k.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/sync-r4k.c` synchronizes CP0 Count registers between CPUs during secondary CPU bring-up. It detects counter time warps between CPUs and compensates a newly booted CPU when possible.

### Important APIs, Types, And Functions
Important state includes atomic `start_count`, `stop_count`, `test_runs`, raw `sync_lock`, `last_counter`, `max_warp`, `nr_warps`, and `random_warps`. Runtime functions are `check_counter_warp()`, `check_counter_sync_source()`, and `synchronise_count_slave()`.

### Control Flow
The newly booted CPU calls `synchronise_count_slave()`, which asks the first online CPU to run `check_counter_sync_source()`. Both CPUs enter synchronized loops, alternate reading Count under `sync_lock`, and detect backward movement relative to the previous CPU's read. If no warp is observed, the source reports pass. If a deterministic warp is found and retries remain, the slave adjusts its Count register by the measured warp and repeats. Finally the slave schedules a near-future compare interrupt.

### State, Persistence, And Dependencies
State is temporary synchronization counters and CP0 Count/Compare registers. The only persistent effect is a corrected Count register for the secondary CPU during boot. Dependencies include `read_c0_count()`, `write_c0_count()`, `write_c0_compare()`, `mips_hpt_frequency`, SMP function calls, raw arch spinlocks, and NMI watchdog touch calls.

### Integration Points
Generic `start_secondary()` in `smp.c` calls `synchronise_count_slave()` before marking the CPU online. Time initialization provides `mips_hpt_frequency`; clockevent code consumes the synchronized Count/Compare state.

### Risks
The code busy-waits with interrupts disabled-sensitive timing and assumes exactly two participants per sync run. Random warps cannot be compensated and only produce warnings. Incorrect frequency or broken Count registers can cause long loops, but the measurement loop has safety exits and watchdog touches.

### Test Signals
Boot SMP R4k-style systems, inspect counter synchronization logs, test CPUs with known Count skew, verify compare interrupts after secondary boot, and run hotplug cycles if Count sync occurs on re-online paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/sync-r4k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/syscall.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/syscall.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/syscall.c` implements MIPS-specific syscall wrappers and legacy `sysmips` operations. It handles unusual MIPS pipe return conventions, mmap offset validation, TLS setup, an atomic user memory operation, alignment-fixup flags, and cache flush requests.

### Important APIs, Types, And Functions
Entry points include `sysm_pipe()`, `SYSCALL_DEFINE6(mips_mmap)`, `SYSCALL_DEFINE6(mips_mmap2)`, `SYSCALL_DEFINE1(set_thread_area)`, `SYSCALL_DEFINE3(sysmips)`, and `SYSCALL_DEFINE3(cachectl)`. The internal helper `mips_atomic_set()` implements `MIPS_ATOMIC_SET`, with LL/SC assembly variants and a software fallback using `ll_bit` and `ll_task`.

### Control Flow
`sysm_pipe()` calls `do_pipe_flags()` and returns fd0 in `$v0` with fd1 in register `$v1`. mmap wrappers validate page offset alignment and call `ksys_mmap_pgoff()`. `set_thread_area()` stores TLS in `thread_info.tp_value` and writes CP0 UserLocal when available. `sysmips()` dispatches `MIPS_ATOMIC_SET`, `MIPS_FIXADE`, and `FLUSH_CACHE`; the atomic set writes the old value into `$v0`, clears error in `$a3`, and jumps to `syscall_exit`.

### State, Persistence, And Dependencies
State includes current pt_regs return registers, current thread TLS value, CP0 UserLocal, per-thread `TIF_FIXADE` and `TIF_LOGADE`, global cache state after flush, and user memory modified by `MIPS_ATOMIC_SET`. Dependencies include syscall core, user access helpers, MIPS LL/SC and EVA assembly helpers, `asm/sysmips.h`, `asm/cachectl.h`, and `ll_bit` state from trap LL/SC emulation.

### Integration Points
This file feeds MIPS syscall tables, interacts with `unaligned.c` through `TIF_FIXADE`, with `traps.c` through LL/SC emulation globals, with signal restart through saved static syscall functions, and with TLS/RDHWR support through `configure_hwrena()`.

### Risks
Inline assembly exception table entries must be correct or user faults can escape. `mips_atomic_set()` has nonstandard return control flow and must preserve static registers. Offset checks for mmap/mmap2 are ABI visible. The software atomic fallback is only a compatibility mechanism and depends on preemption and `ll_bit` semantics.

### Test Signals
Test `pipe()` return registers, `mmap` and `mmap2` invalid offsets, `set_thread_area` plus RDHWR UserLocal reads, `sysmips(MIPS_FIXADE)` behavior with unaligned accesses, `MIPS_ATOMIC_SET` success/fault/alignment cases, and cache flush dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/Makefile

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/Makefile` generates MIPS syscall UAPI headers, syscall count headers, and syscall table headers for n32, n64, and o32 ABIs from `.tbl` inputs.

### Important APIs, Types, And Functions
Important make variables are `kapi`, `uapi`, `syshdr`, `sysnr`, `systbl`, `sysnr_pfx_*`, `uapisyshdr-y`, `kapisyshdr-y`, and `targets`. Build rules generate `unistd_%.h` via `scripts/syscallhdr.sh`, `unistd_nr_%.h` via local `syscallnr.sh`, and `syscall_table_%.h` via `scripts/syscalltbl.sh`.

### Control Flow
The Makefile creates generated header directories, defines quiet commands, then maps each syscall table input to generated output through `if_changed`. The `all` target depends on UAPI and kernel generated headers for all three ABI variants.

### State, Persistence, And Dependencies
Persistent outputs are generated files under `arch/$(SRCARCH)/include/generated/uapi/asm` and `arch/$(SRCARCH)/include/generated/asm`. Dependencies include source syscall tables, kernel scripts `syscallhdr.sh` and `syscalltbl.sh`, and local `syscallnr.sh`.

### Integration Points
Generated headers are consumed by syscall dispatch code, UAPI users, and architecture build rules. Prefix variables determine ABI-specific syscall count macro names such as n32, n64, and o32.

### Risks
Incorrect prefixes or missing targets break generated syscall numbers for an ABI. Directory creation occurs at parse time through `$(shell mkdir -p ...)`, so build-system environment assumptions matter. Table changes must trigger regeneration through proper dependencies.

### Test Signals
Run MIPS header generation for n32/n64/o32, inspect generated `unistd_*.h`, `unistd_nr_*.h`, and `syscall_table_*.h`, touch a syscall table and confirm rebuild, and verify macro names match ABI expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/syscallnr.sh -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/syscallnr.sh

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/syscallnr.sh` generates a guarded header defining the number of Linux syscalls for one MIPS ABI table subset.

### Important APIs, Types, And Functions
The script consumes positional arguments `in`, `out`, ABI selector list, and prefix. It builds `my_abis` from comma-separated ABI names, creates a C header guard from the output basename, filters the syscall table with `grep -E`, sorts numerically, reads rows as `nr abi name entry compat`, and emits `#define __NR_${prefix}_Linux_syscalls`.

### Control Flow
The script filters rows matching the requested ABIs, sorts by syscall number, iterates through all rows while updating `nxt` to `nr + 1`, and writes a header containing only the guard and final syscall count macro. If there are no rows, `nxt` remains zero.

### State, Persistence, And Dependencies
Output is the generated header file. Dependencies are POSIX shell, `basename`, `sed`, `tr`, `grep`, and `sort`. The stable behavior is tied to syscall table column order and numeric sorting.

### Integration Points
The Makefile invokes this script for `unistd_nr_n32.h`, `unistd_nr_n64.h`, and `unistd_nr_o32.h`. The generated syscall count is used by architecture syscall table declarations and validation.

### Risks
Filtering relies on ABI field regexes and table formatting. Numeric sort with hexadecimal-looking patterns can be fragile if table numbers are not accepted by the shell arithmetic used in `nxt=$((nr+1))`. Header guard generation must remain collision-resistant enough for generated filenames.

### Test Signals
Run the script on each MIPS syscall table with ABI filters, verify final count equals last syscall number plus one, test comma-separated ABI lists, and check generated guard and macro names for n32/n64/o32.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/syscallnr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/sysrq.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/sysrq.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/sysrq.c` adds a MIPS-specific SysRq key that dumps TLB registers and entries. It supports dumping the local CPU immediately and other CPUs asynchronously on SMP systems.

### Important APIs, Types, And Functions
Key functions are `sysrq_tlbdump_single()`, `sysrq_tlbdump_othercpus()`, `sysrq_handle_tlbdump()`, and `mips_sysrq_init()`. Important state is `show_lock`, the optional `DECLARE_WORK(sysrq_tlbdump, ...)`, and `sysrq_tlbdump_op`.

### Control Flow
SysRq key `x` invokes `sysrq_handle_tlbdump()`. The local CPU takes `show_lock`, prints CPU ID, dumps TLB registers and all entries, and releases the lock. On SMP, work is scheduled to call `smp_call_function()` so other CPUs run the same dump routine without doing cross-CPU calls directly from the SysRq path.

### State, Persistence, And Dependencies
No persistent state is modified. The spinlock serializes console output. Dependencies include `linux/sysrq.h`, workqueues, SMP call functions, and MIPS TLB debug helpers `dump_tlb_regs()` and `dump_tlb_all()`.

### Integration Points
The file registers with the generic SysRq subsystem at `arch_initcall`. It provides operational diagnostics for TLB code in `traps.c`, `smp.c`, and MMU context handling.

### Risks
TLB dumping can be noisy and may run in distressed system states. Cross-CPU work must avoid deadlocks, and serialization is only for output readability. The feature depends on `SYSRQ_ENABLE_DUMP`.

### Test Signals
Trigger SysRq `x` on UP and SMP systems, verify every online CPU is represented, check output serialization, and test under high interrupt or TLB activity load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/sysrq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/time.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/time.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/time.c` provides common MIPS time initialization, cpufreq loops-per-jiffy adjustment, exported RTC/perf IRQ hooks, and R4k Count clocksource/clockevent setup decisions.

### Important APIs, Types, And Functions
Important state includes per-CPU `pcp_lpj_ref`, `pcp_lpj_ref_freq`, global `glb_lpj_ref`, `glb_lpj_ref_freq`, exported `rtc_lock`, `perf_irq`, and exported `mips_hpt_frequency`. Functions include `cpufreq_callback()`, `register_cpufreq_notifier()`, `null_perf_irq()`, `cpu_has_mfc0_count_bug()`, and `time_init()`.

### Control Flow
When CPU frequency changes, the notifier records baseline loops-per-jiffy values and rescales global and per-CPU delay calibration on pre-change or post-change depending on frequency direction. `time_init()` calls platform `plat_time_init()`, initializes the MIPS clockevent, and registers the Count clocksource unless the R4k Count read bug conflicts with reliable timer interrupt use.

### State, Persistence, And Dependencies
State includes delay calibration values, platform-set `mips_hpt_frequency`, function pointer `perf_irq`, and exported `rtc_lock`. Dependencies include CPU frequency notifiers, R4k timer code, platform time initialization, CPU type detection, and clocksource/clockevent infrastructure.

### Integration Points
Clockevent setup is used by SMP startup and Count synchronization. Platforms provide `plat_time_init()` and may set `mips_hpt_frequency`. Perf event code can override `perf_irq`. RTC drivers use `rtc_lock`.

### Risks
Incorrect frequency scaling breaks `udelay()` timing. R4000/R4400 Count read errata can break clocksource use if ignored. `mips_hpt_frequency` must be set before clockevent/clocksource init. Cpufreq notifier baseline capture must match online CPU state.

### Test Signals
Boot with R4k timer, verify clocksource registration on CPUs with and without Count bug, run cpufreq transitions and validate delay calibration, test SMP secondary timer interrupts, and exercise perf IRQ override paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/topology.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/topology.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/topology.c` registers MIPS CPU devices with the generic CPU topology/sysfs layer during subsystem initialization.

### Important APIs, Types, And Functions
The file defines per-CPU `struct cpu cpu_devices` and the `topology_init()` subsys initcall. It uses `for_each_present_cpu()` and `register_cpu()`.

### Control Flow
At `subsys_initcall`, the code iterates all present CPUs, obtains the per-CPU `struct cpu`, marks all nonzero CPU IDs as hotpluggable, registers each CPU device, and logs a warning if registration fails.

### State, Persistence, And Dependencies
State is the per-CPU `struct cpu` device object and sysfs-visible CPU registration. Dependencies include generic CPU device infrastructure, present CPU masks set by SMP setup, percpu storage, and hotplug conventions.

### Integration Points
This is the bridge from MIPS CPU discovery in SMP/platform setup to generic CPU sysfs and node topology. Hotplug policies rely on `hotpluggable` values.

### Risks
Registration failures only warn, so partial sysfs topology can occur. CPU0 is deliberately not hotpluggable. The correctness of the present CPU mask before this initcall determines which CPU devices appear.

### Test Signals
Boot UP and SMP systems, inspect `/sys/devices/system/cpu`, verify CPU0 hotplug status, hotplug nonzero CPUs where supported, and test behavior when CPU registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/traps.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/traps.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/traps.c` is the central MIPS exception, trap, vector, diagnostic, and instruction-emulation implementation. It installs exception vectors, configures CP0 status/HWREna/EBase, handles fatal and recoverable traps, reports register/stack state, emulates selected missing instructions, manages FPU/MSA enablement, and registers CPU PM restoration hooks.

### Important APIs, Types, And Functions
Important platform hooks are `board_be_init`, `board_be_handler`, `board_nmi_handler_setup`, `board_ejtag_handler_setup`, `board_bind_eic_interrupt`, `board_ebase_setup`, and `board_cache_error_setup`. Diagnostic functions include `show_stack()`, `show_regs()`, `show_registers()`, and `die()`. Exception handlers include `do_be()`, `do_ov()`, `do_fpe()`, `do_bp()`, `do_tr()`, `do_ri()`, `do_cpu()`, `do_msa_fpe()`, `do_msa()`, `do_watch()`, `do_mcheck()`, `do_mt()`, `do_dsp()`, `cache_parity_error()`, `do_ftlb()`, `do_gsexc()`, `ejtag_exception_handler()`, and `nmi_exception_handler()`. Vector setup functions are `set_except_vector()`, `set_vi_handler()`, `per_cpu_trap_init()`, `set_handler()`, `set_uncached_handler()`, and `trap_init()`.

### Control Flow
Boot calls `trap_init()`, allocates or selects EBase space, configures microMIPS mode, runs board EBase setup, performs per-CPU trap initialization, copies generic handlers, initializes default exception/VI vectors, configures cache parity, lets boards initialize bus errors, installs handlers for interrupt, TLB, address errors, syscall, break, reserved instruction, coprocessor unusable, overflow, trap, MSA/FPU, watch, machine check, thread, DSP, and cache errors, flushes icache, sorts bus-error exception tables, and registers the default CU2 notifier. Runtime exception handlers enter exception context, optionally notify die chains, decide user versus kernel handling, emulate instructions when supported, force appropriate signals, or call `die()`/`panic()`.

### State, Persistence, And Dependencies
State includes `ebase`, `exception_handlers[32]`, `vi_handlers[64]`, CP0 Compare/Perf/FDC IRQ numbers, `hwrena`, `ll_bit`, `ll_task`, raw notifier chains for CU2 and NMI, cache parity knobs, and board hook pointers. It mutates CP0 Status, Cause, EBase, HWREna, IntCtl, ErrCtl, MSA/FPU state, thread trap numbers, and per-task FPU/MSA flags. Dependencies span MIPS CP0 accessors, uasm code generation, TLB handlers, FPU emulator, MSA, DSP, kprobes/uprobes/kgdb die notifiers, CPU PM, memblock, cache/TLB debug, and platform CPU feature descriptors.

### Integration Points
This file is the hub for `smp.c` secondary initialization, `signal.c` FP/MSA context behavior, `unaligned.c` fault signaling, uprobes/kprobes breakpoints, CPU PM resume state restoration, board-specific vector relocation in BMIPS/CPS code, syscall and page fault assembly handlers, and MMU/TLB exception stubs. It exports `ebase`, IRQ numbers, and HWREna for other architecture code.

### Risks
Exception-vector installation and CP0 configuration are catastrophic failure points. User versus kernel mode checks must be exact or user faults can panic the kernel, while kernel faults can be hidden. Instruction emulation changes can break LL/SC atomics, RDHWR TLS/time reads, SYNC behavior, Loongson CPUCFG, and FPU fallback. FPU/MSA enablement has security risks if old vector register contents leak. Cache parity and FTLB handling deliberately panic on conditions considered unrecoverable.

### Test Signals
Exercise break/trap instructions, reserved instruction emulation, RDHWR UserLocal/Count reads, LL/SC emulation on LL/SC-less CPUs, FPU unavailable and FPU exception paths, MSA disabled and MSA FP exceptions, watchpoints, bus-error fixups, cache parity options, vectored interrupt setup, CPU PM suspend/resume, NMI notifier handling, and boot on microMIPS, VEIC/VINT, R2/R6, Loongson, and BMIPS/CPS platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/unaligned.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/unaligned.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/unaligned.c` handles MIPS address error exceptions caused by unaligned data accesses. It can signal the task or emulate many load/store instructions for normal MIPS, microMIPS, and MIPS16e instruction encodings, with optional debugfs counters and policy control.

### Important APIs, Types, And Functions
The main handlers are `emulate_load_store_insn()`, `emulate_load_store_microMIPS()`, `emulate_load_store_MIPS16e()`, and `do_ade()`. Debugfs setup is `debugfs_unaligned()`. State includes `unaligned_instructions`, `unaligned_action`, and register recode tables `reg16to32` and `reg16to32st`. It uses access macros such as `LoadW`, `StoreW`, `LoadDW`, EVA variants, FPU emulator calls, MSA register helpers, and CU2 notifier calls.

### Control Flow
`do_ade()` enters exception context, records an alignment fault perf event, handles special 64-bit bad-address fixups, rejects instruction-fetch alignment faults, honors per-thread `TIF_FIXADE`, and applies debugfs policy. It then selects microMIPS, MIPS16e, or normal MIPS decoding based on ISA16 mode and CPU features. Emulators decode the faulting instruction, validate user access ranges, perform the unaligned load/store in software, update target registers or memory, advance EPC including branch/delay-slot behavior, and count successful emulations. Fault paths roll back EPC/RA, try `fixup_exception()`, or force `SIGSEGV`, `SIGBUS`, or `SIGILL`.

### State, Persistence, And Dependencies
Per-task state includes `TIF_FIXADE`, `TIF_LOGADE`, pt_regs, FPU/MSA state, and user memory. Global state is debugfs policy and counters. Dependencies include `asm/branch.h`, `asm/inst.h`, `asm/unaligned-emul.h`, FPU emulator, MSA, CU2 notifier chain from `traps.c`, `access-helper.h`, perf software events, and debugfs.

### Integration Points
`syscall.c` exposes `sysmips(MIPS_FIXADE)` to control per-task unaligned emulation. `traps.c` installs address error exception vectors and provides `show_registers()`, `process_fpemu_return()`, and CU2 notifier behavior. MM exception tables allow kernel unaligned user-copy faults to be fixed up.

### Risks
Instruction decoding is broad and architecture-specific. Emulating stores that cross page boundaries can partially modify memory, a TODO called out in the file. Branch delay handling must preserve original EPC/RA on faults. Unsupported LL/SC, byte operations, kernel accesses, coprocessor loads, and unsupported 64-bit instructions must signal rather than silently emulate. MSA and FPU paths must not leak register state or clobber live context.

### Test Signals
Test user unaligned halfword/word/doubleword loads and stores, disabled `TIF_FIXADE`, debugfs `unaligned_action` signal/show modes, MIPS16e and microMIPS load/store encodings, branch delay slot cases, page-crossing faults, FPU and MSA unaligned accesses, kernel fixup-table cases, and perf/debugfs counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/unaligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/uprobes.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/uprobes.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/uprobes.c` implements MIPS architecture support for uprobes. It validates probed instructions, prepares out-of-line execution slots, handles breakpoint die notifications, restores EPC after XOL, supports return probes, and copies instruction slots with icache flushing.

### Important APIs, Types, And Functions
Important functions are `arch_uprobe_analyze_insn()`, `is_trap_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_xol_was_trapped()`, `arch_uprobe_exception_notify()`, `arch_uprobe_abort_xol()`, `arch_uretprobe_hijack_return_addr()`, `arch_uprobe_copy_ixol()`, `uprobe_get_swbp_addr()`, and `arch_uprobe_skip_sstep()`.

### Control Flow
Analysis rejects unaligned addresses, effectively disallows MIPS16/microMIPS, rejects compact branches, and builds an XOL slot containing either the instruction or its delay-slot companion followed by an XOL breakpoint. Pre-XOL computes the resume EPC, including branch delay behavior, saves `thread.trap_nr`, sets a sentinel, and redirects EPC to the XOL page. Post-XOL restores trap number and EPC. Die notifier callbacks intercept uprobe and XOL breakpoints for user mode and route them to generic uprobe pre/post handlers.

### State, Persistence, And Dependencies
State is per-uprobe `arch_uprobe` data (`insn`, `ixol`, `resume_epc`) and per-task `utask->autask.saved_trap_nr`. The return probe path mutates register `$31`. Dependencies include `asm/branch.h`, MIPS trap break codes, generic uprobes, highmem page mapping, icache flushing, and die notifier values produced by `traps.c`.

### Integration Points
`traps.c` identifies `BRK_UPROBE` and `BRK_UPROBE_XOL` and emits die notifications consumed here. Generic uprobes calls these architecture hooks. Signal and fatal trap handling consult `arch_uprobe_xol_was_trapped()` and abort hooks.

### Risks
Delay-slot and branch resume computation are the highest-risk areas. Compact branches are explicitly unsupported. XOL copying must flush icache or tasks may execute stale instructions. Return probe hijacking must preserve the original RA. Misidentifying trap instructions can prevent probing or recursively trap.

### Test Signals
Probe regular instructions, branch-with-delay-slot instructions, rejected compact branches, rejected unaligned or MIPS16/microMIPS addresses, XOL breakpoint handling, XOL abort on signal, return probes, and icache coherency after installing slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/vdso.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/vdso.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/vdso.c` initializes MIPS VDSO images and maps the VDSO, VVAR data, optional GIC user page, and delay-slot emulation page into new user address spaces.

### Important APIs, Types, And Functions
Important functions are `init_vdso_image()`, `init_vdso()`, `vdso_base()`, and `arch_setup_additional_pages()`. It uses `struct mips_vdso_image`, `vdso_install_vvar_mapping()`, `_install_special_mapping()`, `io_remap_pfn_range()`, `current->thread.abi->vdso`, and `mm->context.vdso`.

### Control Flow
`init_vdso()` records page pointers for native and configured compat VDSO images. During exec, `arch_setup_additional_pages()` takes the mmap write lock, optionally maps a fixed anonymous executable delay-slot emulation page at `STACK_TOP`, sizes the VVAR/GIC/VDSO area, finds unmapped space near a randomized base, color-aligns the data mapping on aliasing-cache systems, installs VVAR, optionally maps the GIC user page uncached, installs the executable VDSO image, and stores the VDSO address in `mm->context.vdso`.

### State, Persistence, And Dependencies
Persistent per-mm state is `mm->context.vdso` and VMAs for `[vvar]`, `[gic]`, the VDSO image, and optional delay-slot page. Global image mappings point at kernel VDSO pages. Dependencies include ABI descriptors from signal code, MIPS GIC base, `vdso_k_time_data`, cache aliasing parameters, randomization, mmap locking, and generic VDSO helpers.

### Integration Points
Signal delivery uses `mm->context.vdso` plus ABI-specific offsets for sigreturn trampolines. Timekeeping VDSO data is provided through VVAR. GIC user mapping supports userspace counter reads when available. Delay-slot emulation integrates with FPU/dsemul behavior.

### Risks
Mapping addresses are ABI-sensitive. Fixed delay-slot mapping at `STACK_TOP` can collide if assumptions change. Cache color alignment is required for aliasing dcache correctness. GIC mapping must be noncached and restricted to the user counter page. Partial mapping failures must unwind by returning errors under the mmap lock.

### Test Signals
Exec native, o32, and n32 processes, inspect VDSO/VVAR mappings, verify sigreturn through VDSO, test ASLR on and off, test aliasing dcache systems, test GIC-present systems, and validate failure paths under constrained address space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/vmlinux.lds.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/vmlinux.lds.S

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/vmlinux.lds.S` is the MIPS kernel linker script. It defines ELF architecture, entry point, program headers, section order, ABI/debug metadata retention, special MIPS sections, relocation table space, appended DTB space, and discarded ABI metadata.

### Important APIs, Types, And Functions
Key linker symbols and sections include `OUTPUT_ARCH(mips)`, `ENTRY(kernel_entry)`, `PHDRS`, `jiffies`, `_text`, `_etext`, `EXCEPTION_TABLE(16)`, `__dbe_table`, `_sdata`, `RO_DATA`, `.data`, `_gp`, `.sdata`, `_edata`, `__init_begin`, `__init_end`, `.mips.machines.init`, `PERCPU_SECTION`, `.rel.dyn`, `.appended_dtb`, `.data.reloc`, `__appended_dtb`, `BSS_SECTION`, `_end`, `.mdebug.*`, debug sections, and `DISCARDS`.

### Control Flow
The script sets the kernel load address, lays out executable text and fixups in the text segment, emits exception tables and data-bus-error tables, places read-only data before writable data, aligns init and BSS sections, reserves optional machine descriptors, optional appended DTB and relocation table areas, emits per-CPU data when SMP is enabled, and discards MIPS ABI metadata not wanted in the final kernel image.

### State, Persistence, And Dependencies
This file determines the persistent kernel image layout and many symbols consumed at runtime. Dependencies include `asm-generic/vmlinux.lds.h`, `asm/asm-offsets.h`, `asm/thread_info.h`, Kconfig options such as `CONFIG_32BIT`, `CONFIG_BOOT_ELF64`, `CONFIG_MAPPED_KERNEL`, `CONFIG_SMP`, `CONFIG_RELOCATABLE`, and appended DTB options.

### Integration Points
Runtime code in `traps.c` consumes `__dbe_table` bounds. Early boot depends on `kernel_entry`, load address, BSS, init section bounds, and appended DTB symbols. Debuggers consume `.mdebug.abi32`, `.mdebug.abi64`, and `.mdebug`. Relocation tooling consumes `.data.reloc`.

### Risks
Section alignment changes can break page tables, per-CPU data, init freeing, or swapper page directory alignment. `_gp` placement affects small-data addressing. Program header changes can break bootloaders. Discarding or retaining ABI sections affects tooling. Appended DTB and relocation reservations must match configured sizes.

### Test Signals
Link 32-bit and 64-bit kernels, boot with and without Octeon PT_NOTE suppression, verify exception table and DBE table symbols, test relocatable kernels, appended DTB kernels, SMP per-CPU layout, BSS alignment, and debugger ABI metadata visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/vpe-mt.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/vpe-mt.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/vpe-mt.c` implements the MIPS MT VPE loader backend. It reserves VPE/TC resources, exposes a character device and sysfs attributes, starts and stops application/service processors on secondary VPEs, and exports module-facing VPE lifecycle helpers.

### Important APIs, Types, And Functions
Important globals are `major`, `hw_tcs`, and `hw_vpes`. Lifecycle functions are `vpe_run()`, `cleanup_tc()`, `vpe_alloc()`, `vpe_start()`, `vpe_stop()`, `vpe_free()`, `store_kill()`, `ntcs_show()`, `ntcs_store()`, `vpe_module_init()`, and `vpe_module_exit()`. Exported symbols are `vpe_alloc`, `vpe_start`, `vpe_stop`, and `vpe_free`. Sysfs attributes are `kill` and `ntcs`.

### Control Flow
Initialization checks MIPS MT capability and reserved VPE/TC limits, registers a character device and class device, disables MT/VPE execution, enters MVP configuration state, reads hardware TC/VPE counts, allocates TC/VPE descriptors for reserved TCs, halts and deactivates them, binds TCs to VPEs, copies config, and exits configuration state. `vpe_run()` verifies master VPE status, selects the first TC attached to the VPE, writes restart PC and context, marks the TC active, binds it to VPE1, configures XTC and VPE status/cause, enables the VPE, restores MT/VPE state, and sends start notifications. Stop/free/kill paths halt/deactivate TCs, release program memory, send stop notifications, and return descriptors to unused state.

### State, Persistence, And Dependencies
State spans VPE/TC descriptor lists from the VPE subsystem, VPE state fields, attached TC lists, `v->__start`, `v->ntcs`, loaded program memory, sysfs-visible device state, and CP0 MIPS MT registers. Dependencies include `asm/mipsmtregs.h`, `asm/mips_mt.h`, `asm/vpe.h`, `vpe_fops`, `get_vpe()`, `alloc_vpe()`, `alloc_tc()`, `release_vpe()`, `release_progmem()`, notifier lists, and kernel device/class/char APIs.

### Integration Points
This backend is used by the MIPS VPE loader character device and by kernel modules that allocate and control VPEs. It shares reserved TC/VPE policy with MT boot parameters such as `maxvpes` and `maxtcs`. It must coexist with SMP MT code, which may manage VPE enable state differently on SMP kernels.

### Risks
MT register programming must occur with interrupts and VPE/MT execution controlled or the system can hang. Resource cleanup on init failure is incomplete for some allocation points. Sysfs `kill` assumes a reserved VPE at `aprp_cpu_index()`. `vpe_stop()` and `vpe_free()` use list entry assumptions that require an attached TC. Notifier callbacks run during start/stop and can add side effects.

### Test Signals
Boot with and without MIPS MT, with `maxvpes` and `maxtcs` reserved, load a VPE program through the char device, start/stop/free it, write sysfs `ntcs` and `kill`, test init failure paths, and verify coexistence with SMP and VPE notifier clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/vpe-mt.c -->
