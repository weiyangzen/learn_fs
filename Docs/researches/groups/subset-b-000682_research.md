# subset-b-000682 Research

Grouped source research for subset B work item `subset-b-000682`. Each source file section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sleep.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/sleep.S

### Purpose
`sleep.S` provides the low-level ARM64 CPU suspend/resume assembly path. It saves callee-saved registers and the stack pointer into `struct sleep_stack_data`, records the per-CPU context pointer in `sleep_save_stash`, and restores CPU state after firmware or platform code resumes the core.

### Important APIs, Types, And Functions
`__cpu_suspend_enter`, `cpu_resume`, `_cpu_resume`, and the local `compute_mpidr_hash` macro are the important entry points. The code depends on `mpidr_hash`, `sleep_save_stash`, `cpu_do_suspend`, `cpu_do_resume`, `init_kernel_el`, `__cpu_setup`, `__enable_mmu`, `finalise_el2`, and optional KASAN stack unpoisoning.

### Control Flow
Suspend enters with `x0` pointing at the sleep stack data, stores frame/callee registers, saves `sp`, hashes `MPIDR_EL1` to select the current CPU stash slot, publishes the context pointer, calls `cpu_do_suspend`, and returns nonzero to tell C code to run the finisher. Resume starts in `.idmap.text`, initializes exception level state, rebuilds early CPU setup, enables the MMU using the idmap and swapper page tables, branches to `_cpu_resume`, restores EL2, recomputes the MPIDR hash, loads the stashed context, restores `sp`, calls `cpu_do_resume`, reloads saved registers, and returns zero to the suspended C frame.

### State, Persistence, And Dependencies
Persistent state is CPU register context in `sleep_stack_data`, per-CPU context addresses in `sleep_save_stash`, and hardware state restored by `cpu_do_resume`. There is no filesystem persistence. Correctness depends on the MPIDR hash matching the C-side topology setup and on the stash memory being visible before firmware powers the CPU down.

### Integration Points
This file is called by `suspend.c` through `__cpu_suspend_enter` and returns into `cpu_suspend()`. It also integrates with boot/idmap code, KASAN, EL2 finalization, CPU feature setup, and the linker-script placement of `.idmap.text` and `.mmuoff` data.

### Risks
The main risks are corrupt stack/context offsets, MPIDR hash mismatches on systems with unusual affinity topology, stale cache visibility across power loss, returning through the wrong path, and breaking early-MMU/idmap assumptions. Assembly register constraints are tight because the hash macro mutates its inputs.

### Test Signals
Exercise CPU idle, suspend-to-RAM, CPU hotplug-style resume paths, KASAN stack builds, EL1/EL2 boot combinations, and systems with sparse MPIDR affinities. Disassembly should confirm context offsets match `asm-offsets.h`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/smccc-call.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/smccc-call.S

### Purpose
`smccc-call.S` implements the assembly call shims for ARM SMCCC SMC/HVC calls, including the classic result structure ABI and the SMCCC 1.2 register-block ABI.

### Important APIs, Types, And Functions
It exports `__arm_smccc_smc`, `__arm_smccc_hvc`, `arm_smccc_1_2_hvc`, and `arm_smccc_1_2_smc`. The `SMCCC` macro stores `x0`-`x3` into `struct arm_smccc_res` and handles the Qualcomm A6 quirk by saving `x6`. The `SMCCC_1_2` macro loads and stores `x0`-`x17` through `struct arm_smccc_1_2_regs`.

### Control Flow
The classic path executes `smc #0` or `hvc #0`, reads the result pointer from the stack, writes result registers, optionally records quirk state, and returns. The 1.2 path saves the result pointer and `x19`, loads argument registers from the caller-provided block, executes the conduit instruction, stores all result registers back, restores `x19`, and returns.

### State, Persistence, And Dependencies
The only persistent state is what the secure monitor, hypervisor, or firmware changes and what the shim writes into caller-owned result structures. There is no kernel global state here.

### Integration Points
The exports are used by firmware, PSCI, hypervisor, errata, secure service, and paravirtualization code needing SMCCC conduits. The file relies on offsets generated from `linux/arm-smccc.h` structures.

### Risks
Register save/restore mistakes corrupt caller state or SMCCC results. Stack argument layout must remain ABI-compatible with the C prototypes. Quirk handling must not clobber normal callers, and firmware may have conduit-specific calling convention constraints.

### Test Signals
Build and boot PSCI/SMCCC users on both SMC and HVC platforms; run firmware feature detection, KVM hypercalls, and Qualcomm quirk coverage; compare generated offsets against structure layout changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/smccc-call.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/smp.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/smp.c

### Purpose
`smp.c` is the ARM64 SMP bring-up, CPU hotplug, IPI, panic-stop, and CPU enumeration implementation. It maps firmware-described CPUs to logical IDs, starts secondary CPUs through `cpu_operations`, enables per-CPU interrupt/timer state, and implements architecture callbacks used by generic scheduler, hotplug, IRQ, kgdb, kexec, and watchdog code.

### Important APIs, Types, And Functions
Important exported or architecture entry points include `__cpu_up`, `secondary_start_kernel`, `__cpu_disable`, `arch_cpuhp_cleanup_dead_cpu`, `cpu_die`, `cpu_die_early`, `smp_cpus_done`, `smp_prepare_boot_cpu`, `arch_register_cpu`, `acpi_cpu_get_madt_gicc`, `smp_init_cpus`, `smp_prepare_cpus`, `arch_show_interrupts`, IPI send helpers, `set_smp_ipi_range_percpu`, `smp_send_stop`, `crash_smp_send_stop`, `smp_crash_stop_failed`, and `cpus_are_stuck_in_kernel`.

### Control Flow
Boot CPU setup records boot CPU features and per-CPU offset. Early enumeration walks DT or ACPI MADT, rejects invalid or duplicate MPIDRs, initializes `cpu_ops`, and marks possible CPUs. Preparation calls each CPU's `cpu_prepare` and marks present CPUs. `__cpu_up` publishes the idle task in `secondary_data`, asks firmware/platform `cpu_boot` to release the CPU, and waits for `cpu_running`. `secondary_start_kernel` switches to `init_mm`, uninstalls the idmap, validates capabilities, runs `cpu_postboot`, stores CPU info/topology, starts per-CPU IRQ/timer notifiers, sets online, completes the boot waiter, restores DAIF, and enters idle. Hot-unplug validates `cpu_die`, removes topology/NUMA state, tears down IPIs, migrates IRQs, reports dead, and calls firmware to power down.

### State, Persistence, And Dependencies
State includes `secondary_data`, `cpu_logical_map`, possible/present/online masks, `cpu_madt_gicc`, `cpu_count`, `bootcpu_valid`, per-CPU IPI descriptors, `ipi_irq_base`, `nr_ipi`, `percpu_ipi_descs`, `crash_stop`, `cpus_stuck_in_kernel`, topology and NUMA data. There is no filesystem persistence; state is CPU masks, firmware-visible release protocol state, interrupt descriptors, and boot status words.

### Integration Points
The file connects generic SMP and CPU hotplug core to ARM64 `cpu_ops`, DT/ACPI CPU description, GIC SGI/LPI IPIs, pseudo-NMI support, irq_work, scheduler IPIs, tick broadcast, kgdb roundup, kexec crash saving, SDEI masking, KVM hyp layout setup, topology, NUMA, and feature finalization.

### Risks
CPU bring-up can fail silently if boot status, MPIDR mapping, cache visibility, or firmware release methods drift. IPI setup must match SGI versus per-CPU LPI delivery and pseudo-NMI state. Panic stop paths intentionally run with limited locking and can race CPU hotplug. Hotplug shutdown relies on firmware actually leaving kernel text before resources are reused.

### Test Signals
Run DT and ACPI boots, maxcpus/nosmp, CPU online/offline loops, IPI stress, irq_work and tick broadcast tests, kgdb roundup, panic/kexec crash paths, pseudo-NMI stop retry paths, and KVM-enabled EL1/EL2 boots.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/smp_spin_table.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/smp_spin_table.c

### Purpose
`smp_spin_table.c` implements the legacy spin-table CPU enable method for ARM64 systems whose secondary CPUs poll a release address instead of using PSCI.

### Important APIs, Types, And Functions
The file defines `secondary_holding_pen_release`, `cpu_release_addr[]`, helpers `write_pen_release`, `smp_spin_table_cpu_init`, `smp_spin_table_cpu_prepare`, `smp_spin_table_cpu_boot`, and the exported `smp_spin_table_ops` `cpu_operations` structure.

### Control Flow
`cpu_init` reads each CPU node's `cpu-release-addr`. `cpu_prepare` maps that address as normal cached memory, writes the physical address of `secondary_holding_pen` in little-endian form, cleans/invalidates the cache line, sends `sev`, and unmaps it. `cpu_boot` writes the target MPIDR into the holding-pen release variable and sends another `sev` so the secondary can leave its polling loop.

### State, Persistence, And Dependencies
Persistent state is the firmware-provided release address array and the `.mmuoff.data.read` holding-pen release word. Cache maintenance is part of the state contract because secondaries may be outside coherency while polling.

### Integration Points
The operations are selected by the CPU enable-method parser and then called by `smp.c`. It depends on DT CPU nodes, `secondary_holding_pen` assembly, physical address translation, I/O remapping, cache maintenance, and ARM `sev` events.

### Risks
Bad or missing `cpu-release-addr` prevents boot. Endianness, cacheability, or missing cache maintenance can strand CPUs. Spin-table platforms often lack reliable hot-unplug `cpu_die`, which feeds into `cpus_are_stuck_in_kernel` risk handling.

### Test Signals
Boot spin-table device-tree systems, test secondary bring-up under cold and warm reset, validate release-address endianness, and run cache-coherency-sensitive CPU online/offline or reboot tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/smp_spin_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/stacktrace.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/stacktrace.c

### Purpose
`stacktrace.c` implements ARM64 kernel and userspace stack unwinding using frame records, pt_regs metadata, per-CPU stack descriptors, ftrace graph recovery, kretprobe recovery, pointer-auth stripping, and compat frame-tail handling.

### Important APIs, Types, And Functions
Key APIs are `arch_stack_walk`, `arch_stack_walk_reliable`, `arch_bpf_stack_walk`, `dump_backtrace`, `show_stack`, and `arch_stack_walk_user`. Internals include `struct kunwind_state`, `kunwind_init_*`, `kunwind_next_frame_record`, `kunwind_next_regs_pc`, `kunwind_recover_return_address`, and consume callbacks.

### Control Flow
An unwind starts from pt_regs, the current caller, or a blocked task's saved frame pointer and PC. The walker validates each frame against known task, IRQ, overflow, SDEI, and EFI stacks, consumes the current PC, advances through the frame record, handles pt_regs frame metadata, strips PAC bits, and recovers original return addresses for fgraph/kretprobe trampolines. Reliable unwinding stops at exception boundaries. User unwinding reads AArch64 or compat frame tails from userspace with page faults disabled and requires frame pointers to progress upward.

### State, Persistence, And Dependencies
State is per-walk stack metadata, current frame pointer/PC, ftrace graph index, optional kretprobe cursor, source flags, and temporary userspace frame copies. It persists no data beyond emitted stack entries.

### Integration Points
Consumers include oops reporting, lockdep/perf/BPF stack capture, scheduler diagnostics, ftrace, kprobes, EFI and SDEI paths, and generic stacktrace APIs. It relies on frame-pointer ABI and ARM64 `stack_info` helpers.

### Risks
Malformed frame records, missing frame pointers, exception boundaries, fgraph/kretprobe trampolines, PAC, inaccessible per-CPU stacks, and concurrent blocked-task execution can make unwinds incomplete or unreliable. User unwinding is best-effort and can fault or stop on nonmonotonic frame chains.

### Test Signals
Validate normal oops traces, reliable livepatch-style checks, BPF stack collection, ftrace graph and kretprobe stacks, EFI/SDEI/NMI stack paths, pointer-auth builds, compat user stacks, and blocked task stack dumps.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/static_call.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/static_call.c

### Purpose
`static_call.c` provides the ARM64 architecture hook for updating static-call trampolines by patching the literal target used by generated trampoline code.

### Important APIs, Types, And Functions
It exports `arch_static_call_transform(void *site, void *tramp, void *func, bool tail)`. It uses `__static_call_return0`, `aarch64_insn_adrp_get_offset`, `aarch64_insn_decode_immediate`, and `aarch64_insn_write_literal_u64`.

### Control Flow
If the replacement function is null, the hook targets `__static_call_return0`. It decodes the `adrp` plus immediate sequence in the trampoline to find the literal slot, then writes the new 64-bit function pointer into that slot and warns if patching fails.

### State, Persistence, And Dependencies
The persistent state is patched kernel text or literal data associated with static-call trampolines. There is no runtime allocation and no filesystem state.

### Integration Points
The hook is called by the generic static-call framework and depends on ARM64 text patching and the exact trampoline instruction layout emitted elsewhere in the kernel.

### Risks
Any trampoline layout change breaks literal address decoding. Incorrect patching can redirect indirect calls to invalid code. Instruction endianness, alignment, and text-patching serialization must be respected.

### Test Signals
Enable static calls, exercise call-site updates during boot and module/static-key changes, run objdump checks of trampoline layout, and monitor `WARN_ON_ONCE` from patch failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/static_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/suspend.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/suspend.c

### Purpose
`suspend.c` is the C half of ARM64 CPU suspend/resume. It wraps the assembly context save/restore path, manages suspend-only architectural state, restores feature bits after resume from reset, and allocates the MPIDR-indexed resume stash.

### Important APIs, Types, And Functions
Important APIs are `cpu_suspend_set_dbg_restorer`, `__cpu_suspend_exit`, `cpu_suspend`, and `cpu_suspend_init`. It consumes `__cpu_suspend_enter` from `sleep.S` and publishes `sleep_save_stash`.

### Control Flow
`cpu_suspend()` validates finalized CPU capabilities, reports async MTE faults, saves DAIF, pauses graph tracing, switches cpuidle IRQ context, enters context tracking idle, and calls `__cpu_suspend_enter`. A nonzero return calls the platform finisher and treats a normal return as failure. A zero return is the resume path: it exits idle context and runs `__cpu_suspend_exit`, which uninstalls the idmap, restores CnP, DIT, PAN, HW breakpoints, Spectre v4 mitigation, SME, MTE, and pointer authentication state before DAIF restoration.

### State, Persistence, And Dependencies
State includes the stack-local `sleep_stack_data`, allocated `sleep_save_stash`, optional `hw_breakpoint_restore` hook, DAIF flags, cpuidle IRQ context, and architectural feature registers reset by firmware. No filesystem persistence exists.

### Integration Points
The file connects cpuidle, CPU PM/suspend finishers, `sleep.S`, MTE, SME, ptrauth, debug monitors, uaccess/PAN, Spectre mitigations, alternatives, CnP, ftrace graph tracing, and context tracking.

### Risks
Suspend before alternatives finalize can lose required PSTATE setup. Resume ordering is delicate: idmap removal, debug restoration, and mitigation state must occur before normal execution. A finisher returning zero is treated as unsupported because successful suspend resumes through a different path.

### Test Signals
Run idle and system suspend cycles with MTE, SME, ptrauth, HW breakpoints, pseudo-NMI/PMR, graph tracing, and Spectre-v4 policy variations; fault-inject finisher failure returns.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sys.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/sys.c

### Purpose
`sys.c` implements ARM64-native syscall glue that needs architecture-specific behavior and builds the AArch64 syscall dispatch table.

### Important APIs, Types, And Functions
It defines `sys_mmap`, `sys_arm64_personality`, `__arm64_sys_ni_syscall`, the `__arm64_*` syscall wrappers generated from `asm/syscall_table_64.h`, and `sys_call_table`.

### Control Flow
The mmap syscall rejects byte offsets that are not page-aligned, then delegates to `ksys_mmap_pgoff`. The personality syscall rejects `PER_LINUX32` if the system cannot run 32-bit EL0, then delegates to `ksys_personality`. The table is initialized to `__arm64_sys_ni_syscall` and then populated by the syscall table include.

### State, Persistence, And Dependencies
No durable state is owned here. The file reads CPU capability state for 32-bit EL0 support and affects process personality and VM mappings via generic syscall helpers.

### Integration Points
It is reached from `syscall.c`'s EL0 SVC path and integrates with generic fs/mm/personality syscalls, generated syscall metadata, and CPU feature detection.

### Risks
ABI mistakes in offset validation or table generation affect all userspace. The 32-bit personality guard must match actual compat support to avoid unusable process modes.

### Test Signals
Run native syscall ABI tests, mmap offset alignment tests, personality tests with and without `CONFIG_COMPAT` or 32-bit EL0 support, and syscall table coverage for unimplemented entries.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sys32.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/sys32.c

### Purpose
`sys32.c` implements AArch32 compat syscall wrappers and builds the compat syscall table used when 32-bit tasks issue SVC on ARM64.

### Important APIs, Types, And Functions
It defines compat wrappers for `aarch32_statfs64`, `aarch32_fstatfs64`, `aarch32_mmap2`, `aarch32_pread64`, `aarch32_pwrite64`, `aarch32_truncate64`, `aarch32_ftruncate64`, `aarch32_readahead`, `aarch32_fadvise64_64`, `aarch32_sync_file_range2`, `aarch32_fallocate`, and `compat_sys_call_table`.

### Control Flow
The wrappers normalize ARM OABI-compatible statfs64 sizes, convert `mmap2` 4 KiB units to page units after alignment validation, reconstruct split 64-bit arguments according to kernel endianness, and delegate to generic `ksys_*` or `kcompat_*` helpers. The table maps compat syscall numbers to `__arm64_*` wrappers, defaulting to `__arm64_sys_ni_syscall`.

### State, Persistence, And Dependencies
State changes are delegated to generic file, VM, and filesystem syscalls. This file itself owns only table initialization.

### Integration Points
It is used by `do_el0_svc_compat` in `syscall.c`, generic compat syscall helpers, AArch32 signal-return entries, and generated `asm/syscall_table_32.h`.

### Risks
Endian-sensitive split-argument reconstruction can corrupt offsets or lengths. The ARM statfs64 ABI quirk is compatibility-sensitive. `mmap2` page-shift handling must be correct for non-4K kernels.

### Test Signals
Run 32-bit userspace syscall suites on 4K/16K/64K page kernels, big- and little-endian builds where applicable, large-file I/O tests, statfs64 ABI compatibility tests, and compat signal-return tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sys32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sys_compat.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/sys_compat.c

### Purpose
`sys_compat.c` handles ARM-private compat syscalls that are not ordinary table entries, chiefly cache flush and TLS setup for AArch32 tasks.

### Important APIs, Types, And Functions
Important functions are `compat_arm_syscall`, `do_compat_cache_op`, and `__do_compat_cache_op`. It handles `__ARM_NR_compat_cacheflush`, `__ARM_NR_compat_set_tls`, and private syscall-number fallback.

### Control Flow
Cache flush validates range ordering, flags, and userspace accessibility, then cleans/invalidates user cache lines in page-sized chunks with rescheduling and fatal-signal checks. If erratum 1542419 applies, it performs an inner-shareable TLB invalidation using a reserved ASID before cache maintenance. TLS setup records the value in `current->thread.uw.tp_value`, uses a barrier against context-switch corruption, and writes `TPIDRRO_EL0`. Unknown private calls below the compat private end return `-ENOSYS`; others are treated as illegal instructions.

### State, Persistence, And Dependencies
State includes current task TLS fields, `TPIDRRO_EL0`, cache/TLB effects, and current fault/signal state. There is no persistent storage.

### Integration Points
Called by `syscall.c` when compat syscall numbers fall outside the table. It depends on cache maintenance, TLB flush, uaccess, scheduler rescheduling, and ARM compat ABI definitions.

### Risks
Cache maintenance over user ranges can fault, be interrupted, or interact with errata. Incorrect TLS ordering can corrupt AArch32 thread-local storage. Private syscall handling must preserve old ARM behavior.

### Test Signals
Run 32-bit cacheflush/TLS ABI tests, JIT self-modifying-code tests, fatal-signal interruption, invalid range/flags tests, and erratum-enabled builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sys_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/syscall.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/syscall.c

### Purpose
`syscall.c` is the common EL0 SVC dispatcher for native and compat ARM64 syscalls. It handles syscall work flags, tracing, MTE async faults, stack randomization, nospec table indexing, fallback private compat syscalls, and return-value storage.

### Important APIs, Types, And Functions
Key functions are `do_el0_svc`, `do_el0_svc_compat`, `el0_svc_common`, `invoke_syscall`, `do_ni_syscall`, `has_syscall_work`, and `__invoke_syscall`.

### Control Flow
The dispatcher stores the original first argument and syscall number, checks for pending asynchronous MTE faults and returns restart state before executing the syscall, handles ptrace/audit/seccomp-style entry work, calls the selected syscall from the native or compat table with `array_index_nospec`, writes the return value into pt_regs, and conditionally performs exit tracing or single-step work.

### State, Persistence, And Dependencies
State is current thread flags, pt_regs syscall fields, randomized kernel stack offset, trace/audit state, and returned register values. It has no independent persistence.

### Integration Points
It connects exception entry assembly to `sys.c`, `sys32.c`, `sys_compat.c`, generic syscall tracing, seccomp/ptrace/audit, MTE, debug monitors, and rseq debug handling.

### Risks
Skipping or tracing syscall numbers must preserve ABI expectations around `NO_SYSCALL` and `x0`. Missing nospec indexing would expose table speculation risk. MTE async fault ordering intentionally prevents the syscall from executing.

### Test Signals
Run syscall ABI and ptrace/seccomp/audit tests, compat SVC tests, out-of-range syscall tests, MTE async fault tests, single-step syscall tests, and kstack offset hardening coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/time.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/time.c

### Purpose
`time.c` initializes ARM64 timer infrastructure and implements `profile_pc` support for timer-based profiling.

### Important APIs, Types, And Functions
It exports `profile_pc` and defines `time_init`. The helper `profile_pc_cb` skips lock functions while walking the stack.

### Control Flow
`profile_pc` walks the current stack from the supplied regs until it finds a non-lock-function PC and returns it for profiling. `time_init` initializes clocks from firmware, probes timers, sets up hrtimer tick broadcast, verifies the architected timer rate, calibrates `lpj_fine`, and initializes paravirtual time.

### State, Persistence, And Dependencies
State includes global clocksource/clockevent registration, tick broadcast setup, `lpj_fine`, and paravirtual time state. The file itself does not persist data.

### Integration Points
It depends on OF clock setup, ACPI/DT timer probing, generic clocksource/clockevents, stack unwinding, profiling, and ARM64 paravirtual time.

### Risks
A missing architected timer rate panics the kernel. Bad stack unwinding can skew profiling. Timer initialization order affects scheduler ticks, delay calibration, and vDSO timekeeping.

### Test Signals
Boot DT and ACPI platforms, verify timer frequency and delay calibration, run high-resolution timer/tick broadcast tests, paravirtual time tests, and profiling samples inside lock-heavy paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/topology.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/topology.c

### Purpose
`topology.c` supplies ARM64 CPU frequency invariance and ACPI CPPC fast-channel counter reads using Activity Monitor Unit counters when available.

### Important APIs, Types, And Functions
Important APIs are `update_freq_counters_refs`, `freq_inv_set_max_ratio`, `arch_cpu_idle_enter`, `arch_freq_get_on_cpu`, `cpc_ffh_supported`, `cpc_read_ffh`, and `cpc_write_ffh`. It also registers cpufreq and CPU hotplug callbacks through `init_amu_fie`.

### Control Flow
Per-CPU AMU samples track previous core and constant cycle counts. Cpufreq policy creation validates AMU support for all CPUs in a policy, allocates/updates `amu_fie_cpus`, and registers `amu_scale_freq_tick` as the frequency scale source. Each tick or idle entry reads AMU deltas, applies a precomputed max-frequency/reference-frequency ratio, clamps to scheduler capacity scale, and stores `arch_freq_scale`. `arch_freq_get_on_cpu` may select an active housekeeping CPU in the same cpufreq policy if the requested CPU lacks a fresh tick. CPPC FFH reads call onto the target CPU unless IRQs are disabled and the target is local.

### State, Persistence, And Dependencies
State includes per-CPU `arch_max_freq_scale`, `cpu_amu_samples`, `arch_freq_scale`, the allocated `amu_fie_cpus` mask, cpufreq notifier registration, and topology scale source registration. No filesystem state is used.

### Integration Points
The file integrates scheduler capacity scaling, cpufreq policy lifecycle, CPU hotplug, housekeeping/nohz isolation, ACPI CPPC FFH, AMU CPU feature detection, erratum 2457168 handling, and the architected timer rate.

### Risks
AMU counters can be absent, disabled, reset, or affected by errata. Mixing CPUs with and without valid counters inside one policy can produce inconsistent scheduler scaling. Remote counter reads are unsafe with IRQs disabled. Stale nohz samples require careful fallback behavior.

### Test Signals
Run cpufreq policy creation/removal, CPU hotplug, nohz full housekeeping fallback, AMU-enabled and AMU-disabled systems, CPPC FFH reads, erratum builds, and scheduler frequency invariance validation under load.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/trace-events-emulation.h -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/trace-events-emulation.h

### Purpose
`trace-events-emulation.h` defines the ARM64 `emulation:instruction_emulation` tracepoint used when the kernel emulates trapped userspace instructions.

### Important APIs, Types, And Functions
It declares `TRACE_SYSTEM emulation` and `TRACE_EVENT(instruction_emulation)` with fields `instr` and `addr`, then includes `trace/define_trace.h` with `TRACE_INCLUDE_FILE` set to `trace-events-emulation`.

### Control Flow
Callers emit the tracepoint with an instruction name and address. The trace infrastructure records a string copy and address and formats them as `instr="..." addr=0x...`.

### State, Persistence, And Dependencies
Trace state is owned by ftrace/perf tracepoint infrastructure. This header contributes generated trace code when included with the normal trace-event pattern.

### Integration Points
It is used by ARM64 instruction emulation paths such as deprecated instruction or system-register emulation, and integrates with Linux trace events.

### Risks
Tracepoint name or field changes break user tooling. The include guard and `TRACE_INCLUDE_PATH` must remain compatible with generated trace code.

### Test Signals
Build with tracing enabled, enable the emulation tracepoint, trigger instruction emulation from userspace, and validate recorded fields with tracefs/perf.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/trace-events-emulation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/traps.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/traps.c

### Purpose
`traps.c` handles ARM64 synchronous exception fallout, undefined instruction emulation, user signal injection, kernel oops processing, system-register traps, stack-overflow panic, SError severity handling, BUG/CFI/KASAN/UBSAN breakpoints, and ESR class reporting.

### Important APIs, Types, And Functions
Important APIs include `aarch32_opcode_cond_checks`, `dump_kernel_instr`, `die`, `arm64_force_sig_fault`, `arm64_force_sig_fault_pkey`, `arm64_force_sig_mceerr`, `arm64_force_sig_ptrace_errno_trap`, `arm64_notify_die`, `arm64_skip_faulting_instruction`, `force_signal_inject`, `arm64_notify_segfault`, `do_el0_undef`, `do_el1_undef`, `do_el0_sys`, `do_el0_cp15`, `esr_get_class_string`, `bad_el0_sync`, `panic_bad_stack`, `arm64_serror_panic`, `arm64_is_fatal_ras_serror`, `do_serror`, and debug breakpoint handlers.

### Control Flow
Kernel fatal paths serialize through `die_lock`, enter oops state, notify die chains, print modules/registers/code bytes, optionally kexec crash, taint, and kill or panic. User fault paths record fault code/address and send appropriate SIGILL/SIGSEGV/SIGBUS/SIGTRAP. Undefined EL0 instructions first try AArch32 breakpoints, MRS emulation, and deprecated instruction emulation before SIGILL. System-register traps match ESR masks against hook tables for cache maintenance, CTR, CNTVCT/CNTFRQ, CPUID MRS, and WFI, then advance PC or signal. Compat CP15 traps validate condition codes and emulate timer reads. SError paths panic for non-RAS or fatal RAS errors. BRK handlers classify BUG, CFI, KASAN, and UBSAN traps.

### State, Persistence, And Dependencies
State includes `show_unhandled_signals`, static die and ratelimit counters, current task fault fields, per-CPU overflow stacks, ESR-derived state, signal queues, taint/oops flags, and architecture feature/erratum state. There is no filesystem persistence.

### Integration Points
The file sits behind exception entry assembly, debug monitors, signal delivery, kprobes, kexec crash, EFI fixups, MTE/KASAN/UBSAN/CFI, timer and cache emulation, CPU feature registers, stacktrace dumping, and compat AArch32 support.

### Risks
Signal-vs-oops classification must be exact to avoid killing the kernel for user faults or resuming after fatal kernel faults. Emulation must advance PC and IT/BTYPE state correctly. Cache maintenance and counter emulation interact with errata and userspace ABI. Oops paths are reentrancy-sensitive.

### Test Signals
Run undefined-instruction, trapped MRS, cache maintenance, WFI, CNTVCT/CNTFRQ, compat CP15, BTI/GCS/FPAC/MOPS, BUG/WARN, CFI, KASAN, UBSAN, stack overflow, SError, EFI fixup, and kexec crash tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso-wrap.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso-wrap.S

### Purpose
`vdso-wrap.S` embeds the built AArch64 `vdso.so` binary into the kernel image as page-aligned read-only data and exposes its bounds.

### Important APIs, Types, And Functions
It defines global symbols `vdso_start` and `vdso_end`, includes `arch/arm64/kernel/vdso/vdso.so` with `.incbin`, page-aligns both ends, and emits the AArch64 feature note macro.

### Control Flow
At link time the VDSO shared object is copied into `.rodata`. Runtime C code treats the symbol range as an ELF image and maps those pages into user processes.

### State, Persistence, And Dependencies
The embedded VDSO bytes are immutable kernel image data. No dynamic state or persistence is owned here.

### Integration Points
Consumed by `vdso.c` during `vdso_init`; depends on the VDSO Makefile building `vdso.so` before this object is linked and on page alignment for mapping.

### Risks
If the included file is missing, unaligned, or not a valid ELF object, VDSO initialization fails. Feature-note emission must match BTI/property expectations.

### Test Signals
Build VDSO, verify `vdso_start`/`vdso_end` alignment, boot and inspect `[vdso]` mappings, and run VDSO time/getrandom calls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso-wrap.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso.c

### Purpose
`vdso.c` validates, initializes, and maps ARM64 VDSO/VVAR pages for native AArch64 tasks and optional AArch32 compat tasks, including compat signal and kuser helper pages.

### Important APIs, Types, And Functions
Key APIs are `arch_setup_additional_pages`, `aarch32_setup_additional_pages`, `vdso_init`, `aarch32_alloc_vdso_pages`, `__vdso_init`, and `__setup_additional_pages`. It defines `struct vdso_abi_info`, AArch64 and AArch32 `vm_special_mapping` descriptors, and mremap callbacks.

### Control Flow
Boot-time init checks the embedded VDSO ELF magic, computes page count, allocates a page-list array, translates embedded PFNs to pages, and installs them into the mapping descriptor. Exec-time setup takes the mmap write lock, reserves a contiguous VVAR plus VDSO region, installs VVAR, records `mm->context.vdso`, and installs executable sealed special mapping with BTI flags when supported. Compat setup may also install kuser helper vectors, a poisoned sigreturn page, optional compat VDSO, and `mm->context.sigpage`.

### State, Persistence, And Dependencies
State includes `vdso_info`, special mapping page lists, `aarch32_vectors_page`, `aarch32_sig_page`, `mm->context.vdso`, and `mm->context.sigpage`. Mapping state persists for the life of each process mm.

### Integration Points
The file connects exec, mmap, VVAR data pages, VDSO binaries from `vdso-wrap.S` and `vdso32-wrap.S`, compat signal handling, kuser helpers, BTI, and generic special mapping logic.

### Risks
Mapping order and lengths are ABI-visible. Missing ELF validation, wrong page counts, or bad mremap updates can leave userspace with broken VDSO pointers. Compat vectors intentionally avoid writable mappings for ARM ABI safety, while sigpage permits COW for debuggers.

### Test Signals
Run native and compat process exec tests, VDSO symbol calls, ASLR/mremap of `[vdso]` and `[sigpage]`, BTI-enabled execution, kuser-helper compatibility, and failure injection for page allocations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/Makefile

### Purpose
`vdso/Makefile` builds the native AArch64 VDSO shared object, strips it, checks it, and generates kernel offsets for exported VDSO symbols.

### Important APIs, Types, And Functions
It defines `obj-vdso` objects for time, note, sigreturn, getrandom, and ChaCha, VDSO linker flags, VDSO-specific C flags, `vdso.so.dbg`, stripped `vdso.so`, and `include/generated/vdso-offsets.h` generation through `gen_vdso_offsets.sh`.

### Control Flow
Kbuild compiles VDSO C/assembly with profiling, stack protector, LTO, CFI, randstruct, SCS, and incompatible warning flags removed, links with the VDSO linker script as a shared object, runs generic VDSO checks, strips debug data for the embedded image, and extracts `VDSO_*` symbol offsets from `nm` output.

### State, Persistence, And Dependencies
Build outputs are object files, `vdso.lds`, `vdso.so.dbg`, stripped `vdso.so`, and generated offsets. No runtime state is created by the Makefile.

### Integration Points
It depends on `lib/vdso/Makefile.include`, compiler support for tiny code model, optional generated gettimeofday/getrandom include files, BTI linker flags, and `vdso-wrap.S` including the final `vdso.so`.

### Risks
Global kernel flags can break freestanding VDSO builds if not removed. Linker orphan handling and exported symbol versions are ABI-sensitive. Missing generated offsets breaks kernel references to VDSO symbols.

### Test Signals
Run ARM64 builds with GCC/Clang, LLD/BFD, BTI on/off, WERROR on, VDSO check output, and inspect exported symbol versions and generated offsets.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/gen_vdso_offsets.sh -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/gen_vdso_offsets.sh

### Purpose
`gen_vdso_offsets.sh` converts `nm` output for the native VDSO into C preprocessor defines for symbols named `VDSO_*`.

### Important APIs, Types, And Functions
The script sets `LC_ALL=C` and uses one `sed` expression to emit lines like `#define vdso_offset_name 0xoffset`.

### Control Flow
It normalizes leading zeroes in symbol addresses, matches text/data symbol lines whose name starts with `VDSO_`, strips that prefix for the define suffix, and prints hexadecimal offsets for later sorting by the Makefile.

### State, Persistence, And Dependencies
The only output is generated header text on stdout. There is no persistent state unless the Makefile redirects it to `include/generated/vdso-offsets.h`.

### Integration Points
Called by `vdso/Makefile` as part of the `VDSOSYM` rule. It relies on stable `nm` output and VDSO symbol naming conventions.

### Risks
Changes in `nm` format or symbol naming can silently omit offsets. Locale must stay deterministic, hence `LC_ALL=C`.

### Test Signals
Feed representative `nm` output with and without leading zeroes, verify generated defines, and ensure the VDSO offset header changes when VDSO symbols move.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/gen_vdso_offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/note.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/note.S

### Purpose
`vdso/note.S` supplies ELF note sections embedded in the native VDSO so userspace can identify Linux version/build metadata and AArch64 feature properties.

### Important APIs, Types, And Functions
It emits a Linux note containing `LINUX_VERSION_CODE`, `BUILD_SALT`, and `emit_aarch64_feature_1_and`.

### Control Flow
The assembler creates `.note.*` input sections that the VDSO linker script collects into a PT_NOTE segment.

### State, Persistence, And Dependencies
All state is static note data in the VDSO ELF image.

### Integration Points
Used by the native VDSO Makefile and `vdso.lds.S`; consumed by loaders, debuggers, and tooling inspecting ELF notes.

### Risks
Incorrect note alignment or missing build salt can affect reproducibility, loader feature handling, or tooling expectations.

### Test Signals
Inspect `readelf -n` output for the VDSO and verify Linux version, build salt, and AArch64 feature notes across BTI configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/sigreturn.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/sigreturn.S

### Purpose
`vdso/sigreturn.S` provides the native AArch64 VDSO signal-return trampoline `__kernel_rt_sigreturn` used when userspace does not provide `SA_RESTORER`.

### Important APIs, Types, And Functions
It defines `__kernel_rt_sigreturn`, issues `mov x8,#__NR_rt_sigreturn` followed by `svc #0`, includes a deliberate leading `nop`, and emits AArch64 feature notes. CFI directives are intentionally disabled.

### Control Flow
Signal-handler return branches to the trampoline, the trampoline loads the rt_sigreturn syscall number into `x8`, enters the kernel with SVC, and never returns normally because the kernel restores the interrupted context.

### State, Persistence, And Dependencies
No writable state exists. The code sequence is ABI-visible to unwinders and debuggers.

### Integration Points
Mapped by `vdso.c`, exported by `vdso.lds.S`, and relied on by glibc/libgcc/libunwind/GDB signal unwinding heuristics and kernel signal delivery.

### Risks
Changing the instruction sequence, adding BTI through normal function macros, or re-enabling incomplete CFI can break unwinding or signal return. The leading NOP exists for unwinders that subtract one from return IP.

### Test Signals
Run signal handling and unwinding tests with GDB, libgcc, libunwind, pthread cancellation, BTI builds, and VDSO symbol inspection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/sigreturn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vdso.lds.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vdso.lds.S

### Purpose
`vdso.lds.S` is the linker script for the native AArch64 VDSO ELF image, defining section layout, program headers, discarded sections, exported symbol versions, and VVAR symbols.

### Important APIs, Types, And Functions
It emits `OUTPUT_FORMAT/OUTPUT_ARCH`, `VDSO_VVAR_SYMS`, text/dynamic/note PHDRs, exported `LINUX_2.6.39` symbols, and `VDSO_sigtramp = __kernel_rt_sigreturn`.

### Control Flow
The linker places ELF headers, hash/dynamic symbol tables, notes, executable text, alternatives, dynamic relocation metadata, rodata/GOT/PLT-like sections, debug details, and discards data/BSS/eh_frame. Program headers produce one read-exec PT_LOAD plus read-only PT_DYNAMIC and PT_NOTE.

### State, Persistence, And Dependencies
The output is the immutable VDSO ELF layout. No runtime state is created directly by the script.

### Integration Points
Used by `vdso/Makefile`, `vdso.c`, generic VDSO data-page macros, and userspace dynamic loader symbol lookup.

### Risks
Exported symbol names and version nodes are ABI. Accidentally retaining writable data, BSS, unsupported notes, or extra load segments breaks VDSO safety or loader assumptions. Text fill and BTI/property handling must remain compatible.

### Test Signals
Run `readelf -lSWsV`, generic VDSO checks, symbol-version tests, and runtime calls to `clock_gettime`, `gettimeofday`, `clock_getres`, `getrandom`, and signal return.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgetrandom-chacha.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgetrandom-chacha.S

### Purpose
`vgetrandom-chacha.S` implements a stackless NEON ChaCha20 block function for the ARM64 VDSO getrandom fast path.

### Important APIs, Types, And Functions
It defines `__arch_chacha20_blocks_nostack(uint8_t *dst, const uint8_t *key, uint32_t *counter, size_t nblocks)`. The routine uses vector registers `v0`-`v7` and `v16`-`v18`, deliberately avoiding callee-saved `d8`-`d15`.

### Control Flow
The function loads the ChaCha constant, 256-bit key, and 64-bit counter with zero nonce, runs 20 rounds per 64-byte block using NEON add/xor/rotate/shuffle operations, adds the original state, stores one block to the destination, increments the counter, loops for all blocks, writes back the counter, zeroes sensitive vector registers, and returns without stack spills.

### State, Persistence, And Dependencies
State is caller-provided output, key, and counter memory plus transient SIMD registers. There is no kernel global state or stack state.

### Integration Points
Called by the generic VDSO getrandom implementation when ARM64 FPSIMD is available. It is built into the native VDSO and paired with `vgetrandom.c`.

### Risks
Cryptographic correctness, counter update, register clobbering, and stackless behavior are critical. Using callee-saved SIMD registers or failing to clear sensitive registers would violate userspace ABI or leak material.

### Test Signals
Compare against ChaCha20 test vectors, run VDSO getrandom stress tests, inspect disassembly for no stack access and no `d8`-`d15` clobbering, and test FPSIMD and non-FPSIMD fallback behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgetrandom-chacha.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgetrandom.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgetrandom.c

### Purpose
`vgetrandom.c` is the native VDSO wrapper for `__kernel_getrandom`, selecting the fast generic VDSO implementation when FPSIMD is available and falling back to the real syscall otherwise.

### Important APIs, Types, And Functions
It defines `__kernel_getrandom` with the same type as `__cvdso_getrandom` and uses `alternative_has_cap_likely(ARM64_HAS_FPSIMD)`, `getrandom_syscall`, and a special probe case returning `-ENOSYS`.

### Control Flow
On CPUs with finalized FPSIMD support, the wrapper calls `__cvdso_getrandom`. Without FPSIMD it returns `-ENOSYS` for the opaque-state probe convention or invokes the kernel syscall fallback for normal requests.

### State, Persistence, And Dependencies
It owns no persistent state. The generic VDSO random code and kernel RNG state provide data and opaque state semantics.

### Integration Points
Built into the native VDSO, exported by the linker script, and tied to `vgetrandom-chacha.S` and generic `vdso/getrandom` support.

### Risks
Incorrect capability gating can execute SIMD code when unavailable or miss the fast path. The probe ABI must return `-ENOSYS` exactly for unsupported VDSO operation.

### Test Signals
Run getrandom VDSO tests on FPSIMD-capable and capability-disabled configurations, verify syscall fallback and probe behavior, and compare output/error handling with the syscall ABI.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgetrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgettimeofday.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgettimeofday.c

### Purpose
`vgettimeofday.c` provides native AArch64 VDSO exported wrappers for time queries.

### Important APIs, Types, And Functions
It defines `__kernel_clock_gettime`, `__kernel_gettimeofday`, and `__kernel_clock_getres`, delegating to `__cvdso_clock_gettime`, `__cvdso_gettimeofday`, and `__cvdso_clock_getres`.

### Control Flow
Userspace resolves the VDSO symbol and calls the wrapper; the wrapper immediately calls the generic C VDSO implementation using the shared VVAR data page and returns its result.

### State, Persistence, And Dependencies
The file owns no state. Timekeeping data is read from the VVAR mapping maintained by generic timekeeping code.

### Integration Points
Built by the native VDSO Makefile and exported by `vdso.lds.S`; used by libc for fast time calls.

### Risks
Prototype or symbol-name drift breaks libc lookup. Generic VDSO include selection must match architecture data-page layout.

### Test Signals
Run clock_gettime/gettimeofday/clock_getres VDSO tests across clock ids, compare with syscalls, and validate behavior across time namespace or clocksource changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32-wrap.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32-wrap.S

### Purpose
`vdso32-wrap.S` embeds the built AArch32 compat VDSO into the ARM64 kernel image and exposes page-aligned bounds.

### Important APIs, Types, And Functions
It defines `vdso32_start` and `vdso32_end`, and includes `arch/arm64/kernel/vdso32/vdso.so` with `.incbin`.

### Control Flow
At link time the compat VDSO ELF image becomes read-only kernel data. `vdso.c` later validates and maps that image for compat tasks when `CONFIG_COMPAT_VDSO` is enabled.

### State, Persistence, And Dependencies
The embedded VDSO bytes are immutable. No writable runtime state is owned here.

### Integration Points
Used by `vdso.c` and produced by `vdso32/Makefile`. It depends on page alignment and a successful 32-bit VDSO build.

### Risks
Missing or invalid compat VDSO breaks AArch32 fast time mappings. Alignment mistakes affect special mapping page lists.

### Test Signals
Build with compat VDSO enabled, inspect `vdso32_start/end`, run 32-bit userspace VDSO calls, and validate `[vdso]` mapping in compat processes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32-wrap.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/Makefile

### Purpose
`vdso32/Makefile` builds the AArch32 compat VDSO using a 32-bit compiler/linker toolchain from the ARM64 tree.

### Important APIs, Types, And Functions
It defines `CC_COMPAT`, `LD_COMPAT`, `cc32-option`, VDSO CPP/C/assembly/linker flags, objects `note.o` and `vgettimeofday.o`, optional generated gettimeofday include flags, `vdso.so.raw`, `vdso32.so.dbg`, stripped `vdso.so`, and the borrowed ARM `vdsomunge` host tool.

### Control Flow
Kbuild selects a compat compiler target, builds freestanding 32-bit objects with ARM ABI, soft-float, endian, ARM/Thumb2 options, links a raw shared object with the compat linker script and VDSO checks, runs `vdsomunge`, then strips the final `vdso.so` embedded by `vdso32-wrap.S`.

### State, Persistence, And Dependencies
State is build artifacts and generated dependency files. There is no runtime state.

### Integration Points
It uses generic VDSO build checks, top-level include paths, ARM vDSO munge tooling, compat cross-compile variables, and `vdso.c` mapping support.

### Risks
A missing or incompatible 32-bit toolchain breaks compat VDSO builds. Global ARM64 flags cannot be reused blindly. Thumb2 unwinding limitations require frame-pointer handling choices. Linker orphan behavior and symbol versions are ABI-sensitive.

### Test Signals
Cross-build with GCC/Clang and BFD/LLD, little/big endian and Thumb2 options, inspect `readelf` output, and run 32-bit libc time calls on ARM64 compat kernels.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/note.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/note.c

### Purpose
`vdso32/note.c` emits 32-bit ELF note metadata for the compat VDSO.

### Important APIs, Types, And Functions
It uses `ELFNOTE32("Linux", 0, LINUX_VERSION_CODE)` and `BUILD_SALT`.

### Control Flow
The C source compiles into note sections that the compat VDSO linker script places into the PT_NOTE segment.

### State, Persistence, And Dependencies
All state is static metadata inside the compat VDSO ELF image.

### Integration Points
Built by `vdso32/Makefile`; inspected by loaders, debuggers, and reproducibility tooling.

### Risks
Incorrect note format or missing build salt can break ELF note consumers or reproducible build expectations.

### Test Signals
Inspect compat VDSO `readelf -n` output and verify note presence after vdsomunge/strip.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/note.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/vdso.lds.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/vdso.lds.S

### Purpose
`vdso32/vdso.lds.S` is the linker script for the AArch32 compat VDSO image.

### Important APIs, Types, And Functions
It defines ELF32 ARM output format, VVAR symbols, section layout, text/dynamic/note PHDRs, and the `LINUX_2.6` symbol version exporting `__vdso_clock_gettime`, `__vdso_gettimeofday`, `__vdso_clock_getres`, `__vdso_clock_gettime64`, and `__vdso_clock_getres_time64`.

### Control Flow
The linker places hash/dynsym/dynstr/version sections, notes, dynamic metadata, rodata/GOT/PLT-like inputs, ARM/Thumb text and veneers, relocations, ARM unwind index, debug details, and attributes, while discarding writable data, BSS, and GNU stack notes. Program headers describe one read-exec load segment plus dynamic and note segments.

### State, Persistence, And Dependencies
The script creates static ELF layout only.

### Integration Points
Used by `vdso32/Makefile`, generic VDSO data-page macros, vdsomunge, and compat VDSO mapping in `vdso.c`.

### Risks
Exported symbols and versions are compat ABI. Incorrect relocation, ARM veneer, or unwind section handling can break 32-bit loaders and unwinders. Writable sections must not enter the runtime VDSO.

### Test Signals
Run `readelf -lSWsV`, generic VDSO checks, 32-bit time ABI tests, and linker orphan warning builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/vgettimeofday.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/vgettimeofday.c

### Purpose
`vdso32/vgettimeofday.c` provides compat VDSO wrappers for 32-bit and time64 time queries.

### Important APIs, Types, And Functions
It defines `__vdso_clock_gettime`, `__vdso_clock_gettime64`, `__vdso_gettimeofday`, `__vdso_clock_getres`, `__vdso_clock_getres_time64`, and empty `__aeabi_unwind_cpp_pr0/pr1/pr2` stubs.

### Control Flow
Compat userspace calls the exported symbols, which delegate to generic C VDSO helpers for 32-bit or 64-bit timespec layouts. The AEABI stubs satisfy references emitted by the compiler without pulling runtime support into the VDSO.

### State, Persistence, And Dependencies
No owned state; the VVAR data page supplies timekeeping data.

### Integration Points
Built into the compat VDSO by `vdso32/Makefile` and exported by `vdso32/vdso.lds.S`; used by 32-bit libc.

### Risks
Type/layout mismatches break old and time64 compat ABIs. Unresolved AEABI references would fail the no-undefined VDSO link.

### Test Signals
Run 32-bit `clock_gettime`, time64, `gettimeofday`, and `clock_getres` tests, compare to syscalls, and link-check no unresolved AEABI or libc dependencies.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/vgettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vmcore_info.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vmcore_info.c

### Purpose
`vmcore_info.c` exports ARM64 crash-dump metadata needed by makedumpfile/crash tooling to interpret a vmcore.

### Important APIs, Types, And Functions
It defines `arch_crash_save_vmcoreinfo` and helper `get_tcr_el1_t1sz`.

### Control Flow
During crash vmcoreinfo collection, the function records VA bits, module/vmalloc/vmemmap ranges, `kimage_voffset`, `PHYS_OFFSET`, current `TCR_EL1.T1SZ`, KASLR offset, and the kernel pointer-auth PAC mask when address authentication is supported.

### State, Persistence, And Dependencies
The output is appended to the vmcoreinfo note captured with the crash dump. It reads live system registers and architecture constants but owns no normal runtime state.

### Integration Points
Used by kexec/crash dump infrastructure, ARM64 memory layout code, pointer authentication helpers, and userspace crash analysis tools.

### Risks
Incorrect metadata makes vmcore virtual-to-physical translation, module lookup, vmemmap decoding, or PAC stripping fail. Format details such as hex string output are consumed by external tools.

### Test Signals
Trigger kdump, inspect vmcoreinfo notes, verify crash/makedumpfile can resolve kernel symbols and memory with KASLR, different VA sizes, and pointer-auth enabled builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vmcore_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vmlinux.lds.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/vmlinux.lds.S

### Purpose
`vmlinux.lds.S` is the ARM64 kernel linker script defining the final kernel image layout, special text/data sections, page tables, hypervisor sections, init/exit regions, relocation records, BSS, early stack, debug metadata, and layout assertions.

### Important APIs, Types, And Functions
It defines symbols such as `_text`, `_stext`, `_etext`, `__init_begin`, `__init_end`, `_data`, `_edata`, `_end`, idmap/tramp/reserved/swapper page directories, hypervisor section bounds, relocation bounds, and many config-dependent section macros.

### Control Flow
The linker starts at `KIMAGE_VADDR`, places head text, main text including IRQ/entry/scheduler/lock/kprobe/hypervisor/static-call text, read-only data, optional hypervisor rodata, GOT checks, trampoline/hibernate/kexec/idmap text, early page tables, init text/data, alternatives, unwind tables, percpu and hypervisor percpu/data, dynamic relocations, writable data, MMU-off data split by cache-maintenance requirements, PE/COFF padding, BSS, init page tables, early stack, and debug/modinfo/ELF details. Assertions validate size, alignment, PLT/GOT emptiness, page-table offsets, kexec/hibernate bounds, and hypervisor BSS alignment.

### State, Persistence, And Dependencies
The output is the static kernel image layout and linker-defined symbols consumed at boot and runtime. It controls memory placement rather than mutable state.

### Integration Points
It integrates KVM nVHE/hyp sections, EFI PE/COFF metadata, KASLR/relocation support, idmap and trampoline mappings, hibernation, kexec, alternatives, static calls, percpu data, MMU-off data used by boot/suspend paths, and generic linker-script macros.

### Risks
Layout mistakes can break early boot, virtual/physical conversion, KVM hyp mappings, kexec, hibernation, KPTI trampolines, or runtime text patching. Assertions are critical guardrails for image invariants.

### Test Signals
Build broad configs with KVM, EFI, KASLR, KEXEC, HIBERNATION, UNMAP_KERNEL_AT_EL0, UNWIND_TABLES, and NVHE tracing; inspect map files; boot-test and validate linker assertions and absence of unexpected PLT/GOT entries.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/watchdog_hld.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/watchdog_hld.c

### Purpose
`watchdog_hld.c` provides ARM64 hard-lockup detector integration using perf/NMI PMU events and cpufreq-aware period adjustment.

### Important APIs, Types, And Functions
It defines `hw_nmi_get_sample_period`, `arch_perf_nmi_is_available`, `watchdog_perf_update_period`, `watchdog_freq_notifier_callback`, and `init_watchdog_freq_notifier`.

### Control Flow
The sample period is computed from the CPU hardware max frequency times `watchdog_thresh`, falling back to a safe 5 GHz estimate when cpufreq data is unavailable. Initialization only advertises perf NMI availability if ARM PMU interrupts are true NMIs. When a cpufreq policy appears, each online CPU in the policy updates its perf watchdog period through `smp_call_on_cpu`.

### State, Persistence, And Dependencies
State is cpufreq notifier registration and perf hardlockup event period updates. No persistent storage is used.

### Integration Points
Connects generic hardlockup detector, cpufreq policy notifications, ARM PMU NMI capability, and per-CPU smp calls.

### Risks
If PMU interrupts are not NMIs, the detector cannot catch hard IRQ-disabled lockups. Missing cpufreq data makes the fallback period conservative and may delay detection on slow CPUs. Policy creation races with event creation are handled by per-CPU updates but remain timing-sensitive.

### Test Signals
Boot with pseudo-NMI PMU support on/off, verify watchdog availability, create cpufreq policies after watchdog start, test CPU hotplug, and inject hard lockups to confirm NMI delivery and expected timeout.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/watchdog_hld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/Kconfig -->
## sources/distributed-fs/ceph-client/arch/arm64/kvm/Kconfig

### Purpose
`arch/arm64/kvm/Kconfig` defines ARM64 virtualization configuration entries for KVM, stage-2 page-table debugging, and nVHE/pKVM debug features.

### Important APIs, Types, And Functions
It sources `virt/kvm/Kconfig`, defines `VIRTUALIZATION`, `KVM`, `PTDUMP_STAGE2_DEBUGFS`, `NVHE_EL2_DEBUG`, `NVHE_EL2_TRACING`, `PKVM_DISABLE_STAGE2_ON_PANIC`, and `PKVM_STACKTRACE`, and selects many generic KVM capability symbols.

### Control Flow
Enabling `VIRTUALIZATION` exposes the KVM submenu. Enabling `KVM` selects generic KVM infrastructure, MMIO, irqchip, dirty logging/ring, MSI/routing/bypass, guest memory, perf event, and scheduling support. Debug-only options gate stage-2 ptdump, nVHE tracing, host stage-2 relaxation on panic, and protected KVM stacktraces.

### State, Persistence, And Dependencies
The file contributes build-time configuration state only. No runtime state exists here.

### Integration Points
It controls compilation of `arch/arm64/kvm/Makefile`, generic `virt/kvm`, debugfs ptdump, tracing, pKVM, and related architecture capabilities.

### Risks
Incorrect selects can produce incomplete KVM builds or expose unsafe debug behavior. Panic-time pKVM debug options explicitly weaken isolation and should not be production defaults.

### Test Signals
Run `olddefconfig`/`randconfig` builds for KVM on/off, debug options, protected KVM options, tracing dependencies, and boot KVM selftests under selected configs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/kvm/Makefile

### Purpose
`arch/arm64/kvm/Makefile` builds the ARM64 KVM host module/core objects, hyp subdirectory, generated hyp constants, VGIC implementation, and optional feature objects.

### Important APIs, Types, And Functions
It adds include flags, includes `virt/kvm/Makefile.kvm`, builds `kvm.o` and `hyp/`, lists `kvm-y` objects such as `arm.o`, `mmu.o`, `psci.o`, `arch_timer.o`, VGIC files, nested virtualization files, TRNG/VMID/PV time, and optional PMU, pointer-auth, ptdump, and hyp tracing objects. It also defines rules for `hyp_constants.h` from `hyp-constants.c`.

### Control Flow
Kbuild compiles hyp constants to assembly, extracts offsets into `hyp_constants.h`, then makes KVM objects depend on that generated header. The final KVM object aggregates core ARM64 KVM and VGIC objects based on configuration.

### State, Persistence, And Dependencies
State is build artifacts and generated `hyp_constants.h`. Runtime state is owned by the compiled objects, not this Makefile.

### Integration Points
It connects ARM64 KVM source files to generic KVM build logic, hyp include paths, VGIC subdirectory objects, PMU, pointer authentication, stage-2 ptdump, and nVHE tracing.

### Risks
Missing generated constants break host/hyp ABI assumptions. Object ordering and conditional inclusion must match config dependencies. Warning suppressions for generated sys-reg initializers are intentional.

### Test Signals
Build KVM with PMU, pointer-auth, ptdump, nested virtualization, VGICv5, and nVHE tracing variations; verify generated hyp constants update when hyp structures change.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/arch_timer.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kvm/arch_timer.c

### Purpose
`arch_timer.c` implements ARM64 KVM virtual and physical architected timer emulation/direct injection for guests, including VHE/nVHE differences, nested virtualization timers, userspace irqchip support, background hrtimers, IRQ-domain wrapping, counter offsets, and timer device attributes.

### Important APIs, Types, And Functions
Important APIs include `timer_get_ctl`, `timer_get_cval`, `kvm_phys_timer_read`, `get_timer_map`, `kvm_cpu_has_pending_timer`, `kvm_timer_update_run`, `kvm_timer_vcpu_load`, `kvm_timer_should_notify_user`, `kvm_timer_vcpu_put`, `kvm_timer_sync_nested`, `kvm_timer_sync_user`, `kvm_timer_vcpu_reset`, `kvm_timer_vcpu_init`, `kvm_timer_init_vm`, `kvm_timer_cpu_up/down`, `kvm_arm_timer_read_sysreg`, `kvm_arm_timer_write_sysreg`, `kvm_timer_hyp_init`, `kvm_timer_vcpu_terminate`, `kvm_timer_enable`, `kvm_timer_init_vhe`, `kvm_arm_timer_set_attr/get_attr/has_attr`, and `kvm_vm_ioctl_set_counter_offset`.

### Control Flow
Initialization obtains architected timer info, records the timecounter and host PPIs, wraps IRQ domains when active-state handling or GICv5 requires it, requests per-CPU virtual/physical timer IRQs, sets vcpu affinity, and enables erratum handling for broken CNTVOFF when needed. Each VCPU initializes four timer contexts, maps guest timer roles depending on VHE/nVHE/nested state, and sets default PPIs. On VCPU load, KVM updates IRQ output, manages physical active state or userspace irq masking, maps/unmaps direct timer PPIs for nested switches, restores direct hardware timer registers and offsets, and emulates non-direct timers with hrtimers. On put, it saves direct hardware state, cancels hrtimers, updates userspace notification state, and emulates timers whose backing registers may have changed. Blocking VCPUs get a background hrtimer for the earliest guest expiration or WFIT deadline. Sysreg reads/writes either operate on emulated context or temporarily save/restore loaded hardware state.

### State, Persistence, And Dependencies
Global state includes `timecounter`, host virtual/physical timer IRQ numbers and flags, `has_gic_active_state`, and `broken_cntvoff_key`. Per-VM state includes timer PPI assignments, virtual and physical counter offsets, immutable-PPI and counter-offset flags. Per-VCPU state includes `arch_timer_cpu`, four `arch_timer_context` structures, hrtimers, loaded/enabled flags, IRQ level, host timer IRQ, `ns_frac`, and vcpu offset pointers. State is in memory only but is ABI-visible through KVM device attributes and run structure fields.

### Integration Points
The file connects KVM run/put/load, VGIC IRQ injection and physical IRQ mapping, GICv5 direct injection, irqchip-in-kernel and userspace irqchip modes, architected timer clocksource data, hrtimer core, nested virtualization, protected VM restrictions, WFIT, ECV/CNTPOFF, Qualcomm CNTVOFF erratum handling, CPU hotplug, and KVM device ioctls.

### Risks
Timer correctness is highly timing-sensitive. Offset mistakes break guest time. Loaded-state save/restore must be preemption/IRQ safe. Userspace irqchip masking can lose or storm interrupts if active state is wrong. Nested timer mapping changes can inject on the wrong PPI. Broken CNTVOFF mitigation trades performance for correctness and depends on feature detection. Timer PPI configuration becomes immutable after first validation.

### Test Signals
Run KVM selftests for arch timers, timer migration, userspace irqchip, in-kernel VGIC, GICv5 if available, VHE/nVHE, nested virtualization, WFIT, counter-offset ioctl, CPU hotplug, live migration style sysreg save/restore, timer interrupt latency, and erratum-enabled builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/arch_timer.c -->
