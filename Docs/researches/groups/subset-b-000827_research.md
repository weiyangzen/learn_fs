# subset-b-000827 research

Grouped source-tree-aligned research for the requested s390 kernel and KVM files. Each section is bounded by reconciliation markers so it can be split into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/smp.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/smp.c

Purpose: Implements s390 SMP CPU discovery, CPU hotplug, logical-to-physical CPU-address mapping, SIGP-based inter-CPU signaling, and external-call interrupt dispatch. It is the central owner of `per_cpu(struct pcpu, pcpu_devices)`, CPU state transitions between standby/configured, lowcore allocation for secondary CPUs, SMT setup, and sysfs controls under the CPU bus.

Important APIs and functions: `smp_detect_cpus()`, `smp_fill_possible_mask()`, `smp_prepare_boot_cpu()`, `__cpu_up()`, `__cpu_disable()`, `__cpu_die()`, `smp_rescan_cpus()`, `arch_send_call_function_ipi_mask()`, `arch_smp_send_reschedule()`, `smp_send_stop()`, `smp_emergency_stop()`, `smp_store_status()`, `smp_save_dump_*()`, and CPU attribute handlers for `configure`, `address`, `rescan`, idle stats, and topology initialization. Helper paths include `pcpu_sigp_retry()`, `pcpu_alloc_lowcore()`, `pcpu_prepare_secondary()`, `pcpu_start_fn()`, `pcpu_delegate()`, and `pcpu_set_smt()`.

Control flow: Early boot records CPU address 0, detects SCLP core information, chooses the boot core type, enables SMT with SIGP SET_MULTI_THREADING, builds possible/present masks, and registers external-call/emergency-signal interrupt handlers. Hotplug-up resets the target CPU, allocates and prefixes a lowcore, copies control/access state, attaches the idle task, restarts the CPU into `smp_start_secondary()`, and waits for it to publish itself online. Hotplug-down removes online masks, disables interrupt sources and pfault, then waits for the target to stop before freeing lowcore resources. External calls atomically consume `pcpu_devices.ec_mask` bits and fan out to scheduler, generic call-single, machine-check, stop, and irq-work handlers.

State and persistence: Persistent state is per-CPU `pcpu_devices`, `lowcore_ptr[]`, `cpu_setup_mask`, `smp_cpu_mtid`, `smp_cpu_mt_shift`, CPU masks, and sysfs registration state. The file protects pcpu state and polarization/capacity changes with `smp_cpu_state_mutex` plus CPU hotplug locks. Crash-dump support temporarily manipulates SMT and gathers old CPU status into save areas.

Dependencies and integration: Depends on SCLP core/configure APIs, SIGP, lowcore/prefixing, topology, vtime, vdso getcpu, pfault, IRQ subsystem, CPU hotplug state machine, scheduler IPIs, crash dump save-area code, and proc/sysfs CPU registration. It exports CPU address, capacity, polarization, SMT thread metadata, preemption/yield helpers, and dump status helpers used elsewhere in s390.

Risks and test signals: Highest risk is ordering around lowcore prefix changes, CPU state mutation while hotplugging, SMT address mapping, SIGP busy retries, and stop/restart delegation for the IPL CPU. Test signals include CPU online/offline cycles, sysfs configure/deconfigure and rescan, scheduler IPI stress, crash dump/kdump CPU register capture, SMT boot parameters (`smt=`, `possible_cpus=`), topology updates after configure changes, and negative paths when SCLP or SIGP reports unavailable CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/stackprotector.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/stackprotector.c

Purpose: Patches compiler-generated stack canary loads so s390 code reads the task or lowcore stack canary instead of a single global `__stack_chk_guard`. It supports both decompressor-time physical patching and normal kernel virtual-address patching.

Important APIs and functions: Exports `__stack_chk_guard` and provides `__stack_protector_apply()` plus decompressor-only `__stack_protector_apply_early()`. Local helpers translate virtual/physical instruction addresses, stringify RIL instructions, verify expected `larl`/`lgrl` opcodes, dump patches when `stack_protector_debug` is enabled, and write replacement instructions with `s390_kernel_write()`.

Control flow: The linker provides a stack-protector relocation table. For each location, the code resolves the real instruction address, verifies that the instruction is an expected RIL form, rewrites it to an `llilf`-style load of `__LC_STACK_CANARY` plus lowcore relocation adjustment, optionally logs the before/after bytes, and writes the patched instruction.

State and persistence: State consists of `__stack_chk_guard`, boot-preserved `stack_protector_debug`, and the patched text image. Once applied, the change is persistent for the running kernel image.

Dependencies and integration: Depends on linker-provided stack protector tables in `vmlinux.lds.S`, lowcore constants, relocated-lowcore detection, decompressor address translation, and safe kernel text patching.

Risks and test signals: A wrong opcode pattern panics in the decompressor and reports an emergency error later, making linker/compiler instruction drift the key risk. Test signals are boot with `CONFIG_STACKPROTECTOR`, decompressor and post-relocation patch success, `stack_protector_debug` patch logs, and deliberate build checks that stack protector references land in the expected section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/stackprotector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/stacktrace.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/stacktrace.c

Purpose: Provides s390 stack walking for generic stacktrace and perf callchain users, including reliable kernel unwinds and user-space stack walks that understand s390 ABI frames and special vDSO wrapper frames.

Important APIs and functions: `arch_stack_walk()`, `arch_stack_walk_reliable()`, `arch_stack_walk_user_common()`, and `arch_stack_walk_user()`. Helpers store entries either through `perf_callchain_store()` or a generic consumer, reject invalid user IPs, and detect IPs within the vDSO text range.

Control flow: Kernel walks use `unwind_for_each_frame()` and consume `unwind_get_return_address()`. Reliable walks reject non-task stacks, trap-frame frames, missing return addresses, rethook trampolines, and any unwind error. User walks start with the register IP, then follow the user backchain with page faults disabled. If a frame has no backchain while executing inside vDSO, the vDSO wrapper frame layout is decoded to recover the saved return address.

State and persistence: No persistent state is owned here. The walker observes current task `mm`, `vdso_base`, register state, stack contents, and unwind state.

Dependencies and integration: Depends on `unwind_bc.c`, s390 ABI stack-frame definitions, `mmap_min_addr`, mm context ASCE limit, vDSO sizing, perf events, rethook/kprobes, and generic stacktrace consumers.

Risks and test signals: Risks are false reliable stack traces, user memory faults while pagefaults are disabled, and vDSO wrapper layout changes. Test signals include perf callchains, livepatch/reliable-stacktrace validation, user stack unwinds across vDSO calls, bad stack pointer/IP rejection, and rethook-enabled traces being marked unreliable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/sthyi.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/sthyi.c

Purpose: Implements native or emulated Store Hypervisor Information (`STHYI`) support and the `s390_sthyi` syscall. It returns a one-page machine/partition capacity report for CP and IFL processors, using firmware instructions directly when facility 74 exists or synthesizing the data from STSI, DIAG 204, and DIAG 224 otherwise.

Important APIs and functions: `sthyi_fill()` is exported for in-kernel users; `SYSCALL_DEFINE4(s390_sthyi)` exposes the syscall. Internal builders include `fill_hdr()`, `fill_stsi_*()`, `diag204_get_data()`, `fill_diag()`, `lpar_cpu_inf()`, `fill_diag_mac()`, `sthyi()`, and cache helpers.

Control flow: `sthyi_fill()` serializes callers with `sthyi_mutex`, initializes a page cache, refreshes it when older than one second, and copies cached content to the caller. Native mode zeroes the page and issues the STHYI instruction. Emulated mode reads DIAG 204 extended data, allocates a DIAG 224 CPU-type page, fills header, machine, and partition sections, sets validity/unavailable flags, scales caps, and caches the result. The syscall validates function code and flags, copies the page and optional return code to user space.

State and persistence: The file owns `sthyi_cache`, valid for `HZ` jiffies, and protects it with `sthyi_mutex`. Output validity is represented by bit fields in the generated STHYI sections rather than by failing every partial data source.

Dependencies and integration: Uses SCLP CPC names, STSI sysinfo blocks, DIAG 204/224 hypervisor data, EBCDIC constants for CP/IFL, facility probing, syscall/user-copy helpers, and exported kernel API consumers.

Risks and test signals: Risks include stale cached topology/capacity data, DIAG 204 busy handling, integer scaling of caps/weights, and partial validity-bit semantics. Test signals include syscall return values for unsupported function codes, native versus emulated hosts, cache behavior under DIAG busy, z/VM/LPAR partition data correctness, and user-copy fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/sthyi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/syscall.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/syscall.c

Purpose: Builds the s390 syscall dispatch table and implements s390-specific syscall entry handling plus a few syscall wrappers with non-standard ABI behavior.

Important APIs and functions: `sys_call_table[]`, `__do_syscall()`, `s390_ipc`, `s390_personality`, and `ni_syscall`. The syscall table is generated by including `asm/syscall_table.h` twice with different `__SYSCALL` definitions.

Control flow: `__do_syscall()` enters from user mode, randomizes kernel stack offset, copies SVC old PSW/int-code from lowcore, updates virtual time, enables interrupts, saves original GPR2, flags PER traps, decodes the syscall number from SVC immediate or GPR1, handles restart-syscall arch data, runs generic entry work, honors ptrace skip via `PIF_SYSCALL_RET_SET`, dispatches through `sys_call_table` with `array_index_nospec()`, and exits through generic syscall-exit work.

State and persistence: State updates happen in `pt_regs`, current thread fields such as last break/PER flags, restart block arch data, and virtual-time accounting. The dispatch table is static read-mostly kernel data.

Dependencies and integration: Depends on generated syscall headers, lowcore SVC fields, generic entry-common syscall hooks, nospec array indexing, ptrace flags, vtime, SysV IPC, personalities, and s390 register ABI.

Risks and test signals: Risks include incorrect syscall-number decoding, ptrace syscall skipping, restart syscall PSW rewrites, and ABI preservation for 31-bit personality. Test signals are syscall tracing/seccomp/ptrace, SysV IPC subcalls, restartable syscalls, syscall number in SVC immediate versus GPR1, and `ni_syscall` fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/syscalls/Makefile -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/syscalls/Makefile

Purpose: Kbuild fragment that generates s390 syscall UAPI and kernel syscall-table headers from `syscall.tbl`.

Important targets and variables: Defines generated UAPI directory `arch/$(SRCARCH)/include/generated/uapi/asm`, kernel API directory `arch/$(SRCARCH)/include/generated/asm`, input `syscall.tbl`, scripts `syscallhdr.sh` and `syscalltbl.sh`, pattern target `unistd_%.h`, target `syscall_table.h`, and `all`.

Control flow: Kbuild creates generated directories, runs `syscallhdr.sh --emit-nr --abis common,$*` for UAPI unistd headers, runs `syscalltbl.sh --abis common,$*` for `syscall_table.h`, adds generated files to `targets`, and makes `all` depend on both output sets.

State and persistence: Persistent build outputs are generated headers under the architecture generated include directories. The makefile itself has no runtime state.

Dependencies and integration: Integrated with the top-level syscall generation scripts and `arch/s390/kernel/syscall.c`, which includes `asm/syscall_table.h`.

Risks and test signals: Risks are stale generated headers, ABI filter mistakes, and missing dependency tracking. Test signals are clean and incremental kernel builds, syscall-number diffs after `syscall.tbl` edits, and compile-time table references in `syscall.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/sysinfo.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/sysinfo.c

Purpose: Exposes s390 STSI machine, CPU, LPAR, topology, and VM information through `/proc/sysinfo`, `/proc/service_levels`, debugfs raw STSI files, and delay-loop calibration.

Important APIs and functions: Proc renderers `stsi_1_1_1()`, `stsi_15_1_x()`, `stsi_1_2_2()`, `stsi_2_2_2()`, `stsi_3_2_2()`, `sysinfo_show()`, service-level registration APIs `register_service_level()` and `unregister_service_level()`, `s390_adjust_jiffies()`, `calibrate_delay()`, and debugfs `STSI_FILE()` wrappers.

Control flow: `/proc/sysinfo` allocates one page, queries maximum STSI level, and conditionally emits machine, topology, CPU, LPAR, and VM blocks, translating EBCDIC/UTF-8 names as needed. Service levels are protected by an rwsem-backed list and, on z/VM, include `QUERY CPLEVEL` output. Delay calibration reads CPU capability with STSI and performs FPU conversion for the special capability encoding. Debugfs allocates a page on open, fills it with one STSI block, and exposes raw bytes.

State and persistence: Owns `topology_max_mnest`, `service_level_list`, `service_level_sem`, the optional VM service-level item, and debugfs/proc registrations. Runtime output reflects firmware/hypervisor STSI state.

Dependencies and integration: Uses STSI instruction wrappers, EBCDIC conversion, topology storage, CPCMD for z/VM, kernel FPU helpers, procfs/debugfs, and exported service-level APIs for other s390 components.

Risks and test signals: Risks include encoding conversion errors, capability arithmetic, raw STSI access permissions, and list lifetime around service-level unregister. Test signals include `/proc/sysinfo`, `/proc/service_levels`, debugfs `stsi/*`, z/VM service output, topology fields, and BogoMIPS recalculation after capacity changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/sysinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/text_amode31.S -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/text_amode31.S

Purpose: Provides assembly routines that must execute below 2 GB in 31-bit addressing mode, mainly DIAG helpers and a reset path used by firmware/hypervisor interfaces.

Important symbols: `_diag14_amode31`, `_diag210_amode31`, `_diag8c_amode31`, `_diag26c_amode31`, `_diag0c_amode31`, `_diag308_reset_amode31`, local low-memory state such as `ctlregs`, `fpctl`, `prefix`, `continue_psw`, and `restart_diag308_psw`.

Control flow: Each helper switches from 64-bit to 31-bit mode with `sam31`, issues the relevant DIAG instruction, captures condition code or fallback errno, switches back with `sam64`, and returns through a local expoline-style branch macro. The DIAG 308 reset path saves control registers, FPC, prefix, and PSW, clears lowcore protection, installs a restart PSW at absolute zero, performs reset, switches architecture/mode back, restores state, and returns.

State and persistence: Uses `.amode31.data` scratch storage below 2 GB and temporarily changes addressing mode, prefix register, control registers, and PSW state. Exception-table entries recover faults back into 64-bit mode with error returns.

Dependencies and integration: Relies on linker placement of `.amode31.*` in `vmlinux.lds.S`, s390 DIAG/SIGP semantics, exception-table macros, and callers in diag/IPL/dump paths that require low-address callable code.

Risks and test signals: Risks are failure to restore machine state, exception handling while in 31-bit mode, and linker placement above 2 GB. Test signals are DIAG helper return codes, dump/reset flows, exception-table recovery, and linker symbols `_samode31`/`_eamode31` in vmcore info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/text_amode31.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/time.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/time.c

Purpose: Owns s390 TOD-based timekeeping, clocksource registration, per-CPU clock comparator event devices, persistent clock reads, Server Time Protocol synchronization, and STP sysfs controls.

Important APIs and functions: `time_early_init()`, `sched_clock_noinstr()`, `sched_clock()`, `clock_comparator_work()`, `init_cpu_timer()`, `read_persistent_clock64()`, `read_persistent_wall_and_boot_offset()`, `clocksource_default_clock()`, `time_init()`, `get_phys_clock()`, `stp_enabled()`, `stp_sync_check()`, `stp_island_check()`, `stp_queue_work()`, and STP sysfs attribute handlers.

Control flow: Early init records TOD delta for vDSO, queries PTFF for LPAR offset/leap seconds, and later `time_init()` resets STP, registers external interrupts, registers the TOD clocksource, and initializes boot CPU timers. Per-CPU comparator setup registers a one-shot clockevent and enables control-register bits. STP timing alerts and machine checks queue work; the worker controls STP attachment, reads STP info, and uses `stop_machine()` to disable/enable per-CPU sync bits, apply global TOD deltas under vDSO update protection, adjust per-CPU comparator/last-update timestamps, and retry on failure.

State and persistence: Boot-preserved `tod_clock_base` and `clock_comparator_max`, per-CPU `comparators` and sync words, global `clock_sync_flags`, `lpar_offset`, `initial_leap_seconds`, `stp_info`, `stp_page`, `stp_online`, timers/workqueue, and the exported epoch-delta notifier chain are persistent runtime state.

Dependencies and integration: Integrates with vDSO time data, clocksource/clockevents, external IRQ registry, CHSC STP calls, PTFF, vtime, CIO/STP machine checks, sysfs bus registration, and atomic notifier users that react to TOD epoch changes.

Risks and test signals: Risks include clock jumps without matching vDSO updates, comparator adjustment races during STP sync, STP state changes under hotplug, and sysfs returning stale or invalid STP fields. Test signals include clocksource registration, clockevent interrupts, `get_phys_clock()` return codes under synced/unsynced modes, STP sysfs values, timing-alert interrupt handling, leap-second reporting, and monotonic sched-clock stability after STP sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/topology.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/topology.c

Purpose: Converts s390 hardware topology and polarization information into scheduler topology masks, CPU sysfs attributes, hiperdispatch state, and sysctl/sysfs controls.

Important APIs and functions: `topology_init_early()`, `arch_update_cpu_topology()`, `update_cpu_masks()`, `store_topology()`, `topology_schedule_update()`, `topology_expect_change()`, `topology_cpu_init()`, `cpu_coregroup_mask()`, `topology_set_cpu_management()`, and sysctl handlers for `s390/topology` and `s390/polarization`.

Control flow: Early init chooses hardware, package, or single topology mode, allocates mask linked lists based on STSI magnitudes, stores STSI 15.1.x data, detects polarization, seeds CPU 0 setup, and updates scheduler masks. Updates parse topology entries into drawer/book/socket masks, set per-CPU IDs, polarization, capacity, thread/core/book/drawer masks, booted-core counts, and hiperdispatch core state. A timer polls PTF change indications, schedules rebuilds, and uses a faster polling window after expected configuration changes.

State and persistence: Owns `topology_mode`, `cpu_management`, `tl_info`, linked lists of socket/book/drawer `mask_info`, exported `cpu_topology[]`, a deferrable timer, work item, and polling counter. State changes are protected by `smp_cpu_state_mutex` and scheduler-domain synchronization.

Dependencies and integration: Uses STSI topology blocks, PTF horizontal/vertical/check operations, s390 SMP CPU address lookup, CPU hotplug setup mask, scheduler topology levels, sysfs CPU devices, sysctl, and hiperdispatch helpers.

Risks and test signals: Risks include malformed topology entries, stale masks after CPU hotplug/configure, mismatch between hardware topology and scheduler domains, and polarization changes racing with CPU state changes. Test signals include `/sys/devices/system/cpu/dispatching`, per-CPU `polarization` and `dedicated`, sysctl toggles, scheduler-domain rebuilds, STSI topology debug output, and hotplug/configure events triggering `topology_expect_change()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/trace.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/trace.c

Purpose: Defines and exports the s390 diagnose tracepoint and provides a no-recursion helper for tracing DIAG calls from low-level code.

Important APIs and functions: `CREATE_TRACE_POINTS` for `<asm/trace/diag.h>`, exported `s390_diagnose` tracepoint, and `trace_s390_diagnose_norecursion(int diag_nr)`.

Control flow: The norecursion helper avoids lockdep recursion by returning immediately when lockdep is enabled. Otherwise it disables local IRQs, checks a per-CPU recursion depth, emits `trace_s390_diagnose()`, and restores IRQ state.

State and persistence: Per-CPU `diagnose_trace_depth` tracks recursion. The tracepoint is globally registered through the tracing subsystem.

Dependencies and integration: Used by DIAG helper code and tracing users; depends on per-CPU operations, IRQ save/restore, and tracepoint infrastructure.

Risks and test signals: Risks are recursion in low-level tracing paths and missing events under lockdep. Test signals include ftrace/perf tracepoint visibility, DIAG call tracing with lockdep disabled, and no recursion warnings or IRQ-state imbalance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/traps.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/traps.c

Purpose: Handles s390 program-check exceptions, maps them to signals or kernel fixups/panics, integrates kprobes/uprobes/PER events, validates monitor-call BUG support, and initializes trap lowcore state.

Important APIs and functions: `trap_init()`, `__do_pgm_check()`, `do_report_trap()`, `do_per_trap()`, `kernel_stack_invalid()`, `is_valid_bugaddr()`, `__warn_args()`, and the `pgm_check_table[128]`. Trap handlers cover illegal, privileged, execute, protection/DAT, addressing, specification, data, floating-point/vector, transaction, monitor event, secure-storage, and default exceptions.

Control flow: Program-check entry copies lowcore interruption fields into `pt_regs`, short-circuits guest faults for KVM by storing `gmap_teid`/`gmap_int_code`, enters irqentry state, updates timers and last-break for user mode, captures transaction diagnostic block, records user PER events or dispatches kernel PER to kprobes, restores interrupt state according to interrupted PSW, indexes `pgm_check_table`, then disables IRQs and exits irqentry. Individual handlers notify die chains, signal users, run exception-table fixups, or die/panic in kernel mode.

State and persistence: Updates current thread trap/PER fields, `pt_regs`, lowcore program-check data, BUG report state, and control-register/PSW machine-check enablement during `trap_init()`.

Dependencies and integration: Integrates with fault handlers, kprobes, uprobes, generic BUG, ptrace/PER, entry-common IRQ accounting, KMSAN entry-register handling, exception tables, FPU state saving, and KVM guest-fault handling.

Risks and test signals: Risks are wrong signal codes, lost PER events, incorrect guest fault bypass, re-enabling wrong PSW bits, and BUG/monitor-call decoding. Test signals include user SIGILL/SIGFPE/SIGSEGV cases, kprobe/uprobe breakpoints, hardware single-step/PER, kernel exception-table fixups, KVM SIE guest faults, and boot-time monitor-call self-test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/unwind_bc.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/unwind_bc.c

Purpose: Implements s390 backchain-based kernel unwinding for stacktrace, perf, livepatch reliability checks, and diagnostics.

Important APIs and functions: `unwind_get_return_address()`, `unwind_next_frame()`, and `__unwind_start()` are exported. Helpers validate stack bounds, move between stack types with `get_stack_info()`, identify final `pt_regs`, and recover return addresses.

Control flow: Start initializes the state from supplied kernel `pt_regs`, current frame address, or saved task kernel stack pointer; user-mode regs are rejected. Each next-frame step either consumes a pending `pt_regs` frame, follows a nonzero backchain, or interprets no-backchain as a possible `pt_regs` structure. It checks stack range transitions, 8-byte alignment, kernel text return addresses, final user/kernel-thread regs, and marks errors before stopping.

State and persistence: State is all in `struct unwind_state`: task, current stack info, mask, SP, IP, regs pointer, reliability flag, and error flag. No global state is modified.

Dependencies and integration: Depends on s390 stack-frame ABI, `get_stack_info()`, `task_pt_regs()`, kernel text address validation, scheduler task stacks, and stacktrace consumers in `stacktrace.c`.

Risks and test signals: Risks include interpreting corrupted backchains, false reliability on interrupt stacks, and KMSAN false positives from uninitialized frame reads. Test signals include reliable stacktrace validation, stack dumps across IRQ and task stacks, corrupted-stack detection, and unwinding stopped cleanly at user-mode `pt_regs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/unwind_bc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/uprobes.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/uprobes.c

Purpose: Implements s390 architecture support for uprobes and uretprobes, including out-of-line execution setup, post-single-step fixups, PER interaction, and emulation of PC-relative RIL instructions that cannot safely execute from the XOL area.

Important APIs and functions: `arch_uprobe_analyze_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_exception_notify()`, `arch_uprobe_abort_xol()`, `arch_uretprobe_hijack_return_addr()`, `arch_uretprobe_is_alive()`, and `arch_uprobe_skip_sstep()`. Key helpers include `check_per_event()`, `sim_stor_event()`, and `handle_insn_ril()`.

Control flow: Pre-XOL rejects 24/31-bit address modes, clears PER trap state, saves PSW PER and int-code, marks the regs with a synthetic trap number, redirects PSW to the XOL slot, sets `TIF_UPROBE_SINGLESTEP`, and updates control registers. Post-XOL restores flags, fixes PSW or return-register addresses based on decoded probe fixup bits, handles branch-not-taken correction, and re-triggers PER events if emulated execution matched user PER controls. Exception notifier maps breakpoint/singlestep die events into uprobe pre/post handlers. RIL emulation computes the original PC-relative target, performs aligned user loads/stores/compares, simulates storage alteration PER, advances PSW, and reports appropriate synthetic traps on faults.

State and persistence: Uses per-task `current->utask`, thread PER fields, saved state in `struct arch_uprobe`, register state, and task flags. No persistent storage is kept beyond probe/task lifecycle.

Dependencies and integration: Depends on generic uprobes, die notifier chain from traps, s390 disassembler/probe opcode classification, ptrace/PER control registers, user access helpers, and return-probe stack semantics.

Risks and test signals: Highest risk is address fixup/emulation correctness for PC-relative instructions, PER event reproduction, and abort paths restoring PSW/int-code. Test signals include uprobes on loads/stores/branches, RIL instructions near range limits, 24/31-bit mode rejection, uretprobe return hijacking, ptrace PER single-step interactions, and fault injection for unaligned or inaccessible user operands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/uv.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/uv.c

Purpose: Provides common s390 Ultravisor support for protected virtualization host/guest state, UV initialization, secure/shared page transitions, protected guest memory accessibility, UV capability/key sysfs exposure, and secret lookup/retrieval helpers.

Important APIs and functions: Exported state `prot_virt_guest`, `prot_virt_host`, `uv_info`; setup `setup_uv()`; page APIs `uv_pin_shared()`, `uv_destroy_folio()`, `uv_destroy_pte()`, `uv_convert_from_secure()`, `uv_convert_from_secure_folio()`, `uv_convert_from_secure_pte()`, `__make_folio_secure()`, `s390_wiggle_split_folio()`, `arch_make_folio_accessible()`; sysfs init `uv_sysfs_init()`; and secret APIs `uv_find_secret()` and `uv_retrieve_secret()`.

Control flow: Host setup reserves below-2GB UV base storage with memblock, issues `INIT_UV`, and disables host PV support on failure. Secure-page conversion functions iterate each base page in a folio and clear `PG_arch_1` on successful destroy/export. `__make_folio_secure()` verifies writeback/reference conditions, freezes expected references, sets `PG_arch_1`, issues a single UV call, unfreezes references, and maps UV condition codes to errno. `arch_make_folio_accessible()` treats `PG_arch_1` as a maybe-secure hint, first tries pin-shared, then convert-from-secure. Sysfs creates `/sys/firmware/uv` attributes for PV state, query data, optional key hashes, and secret capability information. Secret lookup pages through UV list results and retrieval maps return codes to stable Linux errors.

State and persistence: Boot-preserved UV state and `uv_info` are global. Folio `PG_arch_1` marks possible secure memory. Sysfs kobjects/ksets persist after device init. Secret buffers are caller-provided and ephemeral.

Dependencies and integration: Integrates with UV call ABI, memblock, folio/mm/pagewalk infrastructure, swap/writeback, KVM PV code, firmware sysfs, protected guest dump metadata, and s390 page-state/storage ownership rules.

Risks and test signals: Risks include folio reference-freeze races, large folio splitting/writeback retry behavior, stale `PG_arch_1` overindication, UV firmware return-code compatibility, and sysfs exposure only when facility 158 is present. Test signals include PV host boot with UV base allocation, KVM protected guest page import/export, swap/writeback of secure pages, sysfs `firmware/uv/*`, UV key query availability, and secret lookup/retrieve error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/uv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso.c

Purpose: Maps the s390 vDSO and vvar pages into new user address spaces, records the vDSO base for stack walking, initializes the TOD programmable field used by vDSO getcpu, and applies vDSO alternatives at boot.

Important APIs and functions: `vdso_getcpu_init()`, `arch_setup_additional_pages()`, `vdso_text_size()`, `vdso_size()`, `vdso_init()`, `map_vdso()`, `vdso_addr()`, `vdso_setup_pages()`, and `vdso_apply_alternatives()`.

Control flow: Early init writes the current CPU number into the TOD programmable field before SMP init. During exec, `arch_setup_additional_pages()` picks a randomized address below `VDSO_BASE` when ASLR is enabled, maps vvar pages first with `vdso_install_vvar_mapping()`, then maps the sealed executable vDSO special mapping. `mremap` updates `mm->context.vdso_base`. Boot-time vDSO init scans the embedded ELF for `.altinstructions`, applies alternatives, and creates the page list for the special mapping.

State and persistence: Stores `mm->context.vdso_base` per process and a global `vdso_mapping.pages` list. The embedded vDSO image is patched once during boot.

Dependencies and integration: Depends on linked symbols `vdso_start`/`vdso_end`, vDSO datastore/vvar helpers, ELF section scanning, alternatives, random address selection, mmap locking, and stacktrace user unwinder knowledge of vDSO layout.

Risks and test signals: Risks include failed vvar/vDSO partial mapping cleanup, wrong ASLR bounds, stale `vdso_base` after mremap, and alternatives corrupting the DSO image. Test signals include process exec vDSO mappings, `getauxval(AT_SYSINFO_EHDR)`, vDSO time/getcpu calls, gdb breakpoints using `VM_MAYWRITE`, mremap behavior, and boot alternative patch logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/Makefile -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/Makefile

Purpose: Builds the s390 vDSO shared object, wrapper object, stripped DSO, debug DSO, and generated vDSO offset header.

Important targets and variables: `obj-vdso`, `obj-cvdso`, `VDSO_CFLAGS_REMOVE`, `KBUILD_AFLAGS_VDSO`, `KBUILD_CFLAGS_VDSO`, `ldflags-y`, `vdso.so.dbg`, `vdso.so`, `vdso_wrapper.o`, `vdso.lds`, and `include/generated/vdso-offsets.h`.

Control flow: The makefile removes kernel-only instrumentation flags from vDSO objects, adds PIC/no-stack-protector/vDSO-specific flags, links `vdso.so.dbg` with `vdso.lds` first, runs the generic vDSO checker, strips to `vdso.so`, compiles assembly and C vDSO objects with special commands, forces wrapper rebuild after `vdso.so`, and generates offset defines by piping `nm` through `gen_vdso_offsets.sh`.

State and persistence: Persistent build outputs are the vDSO objects, debug/stripped DSOs, wrapper object, linker script output, and generated offset header.

Dependencies and integration: Uses `lib/vdso/Makefile.include`, optional generated getrandom include, s390 vDSO source files, linker script, `NM`, `OBJCOPY`, and the kernel object that incbins `vdso.so`.

Risks and test signals: Risks are accidentally retaining tracing/profiling flags, DSO ABI/check failures, stale offsets, and dependency misses around incbin. Test signals include clean/incremental kernel builds, `cmd_vdso_check`, generated `vdso-offsets.h`, and runtime vDSO symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/gen_vdso_offsets.sh -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/gen_vdso_offsets.sh

Purpose: Converts `nm` output for the vDSO debug shared object into C preprocessor defines containing offsets of exported `__kernel_*` symbols.

Important behavior: The script sets `LC_ALL=C` and runs a single `sed` expression that matches hexadecimal addresses followed by a symbol type and `__kernel_` name, emitting `#define vdso_offset_<name> 0x<addr>`.

Control flow: Kbuild pipes `$(NM) vdso.so.dbg` into this script and sorts the output. No files are opened directly by the script.

State and persistence: Stateless; generated persistence is handled by the Makefile target `include/generated/vdso-offsets.h`.

Dependencies and integration: Depends on stable `nm` output format, exported vDSO symbol naming, POSIX shell, and sed. Used by the vDSO Makefile.

Risks and test signals: Risks are symbol-name pattern drift or locale-sensitive sorting if `LC_ALL` were not set. Test signals are correct defines for all `__kernel_*` symbols and rebuild stability when vDSO inputs do not change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/gen_vdso_offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/getcpu.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/getcpu.c

Purpose: Implements the s390 vDSO `getcpu` fast path.

Important API: `__s390_vdso_getcpu(unsigned *cpu, unsigned *node, void *unused)`.

Control flow: Stores the extended TOD clock into a local `union tod_clock`, reads the programmable field as the current CPU number, writes it to `*cpu` when provided, writes NUMA node zero when `node` is provided, and returns success.

State and persistence: Reads hardware TOD programmable field maintained by kernel CPU initialization. It owns no persistent state.

Dependencies and integration: Depends on `store_tod_clock_ext()`, `vdso_getcpu_init()` in `vdso.c`, and s390 convention that NUMA node is always zero for this vDSO API.

Risks and test signals: Risk is stale programmable field after CPU migration or hotplug if CPU init does not update it. Test signals include vDSO `getcpu()` compared with syscall/getcpu, CPU migration stress, and null pointer arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/getcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/note.S -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/note.S

Purpose: Supplies ELF note metadata for the s390 vDSO PT_NOTE segment.

Important symbols and macros: Uses `ELFNOTE_START(Linux, 0, "a")`, emits `LINUX_VERSION_CODE`, then closes with `ELFNOTE_END`.

Control flow: Assembled into a `.note.*` section and collected by the vDSO linker script into PT_NOTE.

State and persistence: The kernel version note is persistent in the vDSO image mapped into user processes.

Dependencies and integration: Depends on Linux ELF note macros, `linux/version.h`, and `vdso.lds.S` note placement.

Risks and test signals: Risks are malformed note alignment or missing PT_NOTE. Test signals include `readelf -n` on `vdso.so.dbg` and runtime vDSO note inspection by user-space tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso.h -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso.h

Purpose: Declares internal s390 vDSO C entry points and the getrandom ABI wrapper.

Important declarations: `__s390_vdso_getcpu()`, `__s390_vdso_gettimeofday()`, `__s390_vdso_clock_gettime()`, `__s390_vdso_clock_getres()`, and `__kernel_getrandom()`.

Control flow: Header-only contract shared by vDSO C files and assembly wrappers.

State and persistence: No state.

Dependencies and integration: Includes `vdso/datapage.h` for vDSO time data types and is included by getcpu, generic time wrappers, and getrandom implementation.

Risks and test signals: Risks are prototype mismatches with assembly-exported names or user ABI expectations. Test signals are vDSO build warnings/errors and symbol ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso.lds.S -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso.lds.S

Purpose: Linker script for the 64-bit s390 vDSO shared object.

Important sections and controls: Defines ELF64 s390 output, `VDSO_VVAR_SYMS`, dynamic/hash/symbol/version sections, PT_NOTE, executable text, rodata, alternatives, dynamic table, eh-frame metadata, GOT, debug sections, discard rules, explicit PHDRs, and exported versioned symbols.

Control flow: The linker lays out a single read-execute PT_LOAD segment plus read-only dynamic/note/eh-frame headers. The script discards data/bss and unwanted notes, keeps unwind metadata, and exports only `__kernel_gettimeofday`, `__kernel_clock_gettime`, `__kernel_clock_getres`, `__kernel_getcpu`, restart/sigreturn trampolines, and `__kernel_getrandom`.

State and persistence: Produces the persistent vDSO ELF image that is incbined into the kernel and mapped into every process that receives vDSO pages.

Dependencies and integration: Depends on vDSO ABI macros, generic vmlinux linker macros, vvar symbol definitions, and the Makefile's shared-object link.

Risks and test signals: Risks are accidentally exporting extra symbols, adding writable data, breaking program headers, or losing unwind info needed by stack walkers. Test signals include vDSO checker, `readelf -l/-S/-s`, exported symbol version tests, and user unwinding across vDSO frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_generic.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_generic.c

Purpose: Thin s390 wrappers around generic vDSO time implementations.

Important APIs: `__s390_vdso_gettimeofday()`, `__s390_vdso_clock_gettime()`, and `__s390_vdso_clock_getres()`.

Control flow: Includes `lib/vdso/gettimeofday.c` and forwards each s390-named wrapper to the corresponding `__cvdso_*` implementation.

State and persistence: Uses generic vDSO data page state through included code; this file owns no state.

Dependencies and integration: Depends on common vDSO time code, vDSO datapage, and assembly wrappers that export `__kernel_*` symbols calling these `__s390_vdso_*` functions.

Risks and test signals: Risks are ABI/type mismatch and architecture data setup errors outside this file. Test signals include vDSO clock/gettimeofday correctness versus syscalls and clocksource mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_user_wrapper.S -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_user_wrapper.S

Purpose: Exports user-visible vDSO entry symbols and supplies ABI-compatible stack frames for older glibc callers, plus syscall trampolines for restart and signal return.

Important symbols: `__kernel_gettimeofday`, `__kernel_clock_getres`, `__kernel_clock_gettime`, `__kernel_getcpu`, `__kernel_restart_syscall`, `__kernel_sigreturn`, and `__kernel_rt_sigreturn`.

Control flow: The `vdso_func` macro allocates a special vDSO stack frame, saves `%r14`, clears the user backchain, calls the matching `__s390_vdso_*` function with `brasl`, restores return state, and branches back. The `vdso_syscall` macro issues `svc` for trampolines and places an illegal word afterward to catch unexpected returns.

State and persistence: Manipulates only the user stack/register frame for each call. Frame layout is persistent ABI and is consumed by `stacktrace.c`.

Dependencies and integration: Depends on s390 stack-frame offsets, DWARF CFI, syscall numbers, vDSO C entry points, and user stack walking special cases.

Risks and test signals: Risks are stack-frame layout drift, broken CFI/unwind data, and trampolines returning unexpectedly. Test signals include old and current glibc vDSO calls, user stack traces through vDSO, signal return paths, and `readelf --debug-dump=frames`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_user_wrapper.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_wrapper.S -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_wrapper.S

Purpose: Embeds the built `vdso.so` binary into the kernel image as page-aligned data.

Important symbols: Global `vdso_start` and `vdso_end`.

Control flow: Switches to page-aligned data, aligns to `PAGE_SIZE`, incbins `arch/s390/kernel/vdso/vdso.so`, aligns again, and returns to the previous section.

State and persistence: The incbined vDSO image is persistent kernel data used by `vdso.c` to build the special mapping page list.

Dependencies and integration: Depends on the Makefile forcing `vdso_wrapper.o` to depend on `vdso.so`, linker page alignment, and runtime vDSO mapping code.

Risks and test signals: Risks are stale incbin dependency, misalignment, or missing symbols. Test signals are vDSO mapping page count, `vdso_start`/`vdso_end` symbols, and clean rebuild after vDSO source changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_wrapper.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vgetrandom-chacha.S -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vgetrandom-chacha.S

Purpose: Provides a no-stack s390 vector implementation of ChaCha20 blocks for the vDSO getrandom fast path.

Important symbol: `__arch_chacha20_blocks_nostack(uint8_t *dst_bytes, const uint8_t *key, uint32_t *counter, size_t nblocks)`.

Control flow: Loads ChaCha constants and byte-permutation data, loads the key, builds the counter/zero nonce state, runs ten double rounds per block with vector add/xor/rotate/shuffle operations, adds original state, stores little-endian output using a facility-148 alternative path, increments and stores the counter, advances output, loops by block count, then zeroes sensitive vector registers before returning.

State and persistence: Reads key and counter from caller memory, writes output and updated counter, and avoids stack spills. Sensitive vector state is explicitly cleared before return.

Dependencies and integration: Depends on s390 vector/facility instructions, alternatives, DWARF CFI, and generic vDSO getrandom code that calls the architecture ChaCha provider.

Risks and test signals: Risks are endian conversion errors, counter carry handling, facility alternative mismatch, and register clobber/secret leakage. Test signals include ChaCha20 known-answer tests through vDSO getrandom, facility-148 and non-148 paths, multi-block counter rollover behavior, and objtool/CFI sanity where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vgetrandom-chacha.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vgetrandom.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vgetrandom.c

Purpose: Implements the s390 vDSO-visible `__kernel_getrandom` wrapper.

Important API: `__kernel_getrandom(void *buffer, size_t len, unsigned int flags, void *opaque_state, size_t opaque_len)`.

Control flow: If facility 129 is available, forwards to generic `__cvdso_getrandom()`. If called with the special probe signature of all-zero arguments except `opaque_len == ~0UL`, returns `-ENOSYS`. Otherwise falls back to the `getrandom` syscall wrapper.

State and persistence: No owned state; uses generic vDSO getrandom opaque state when supported.

Dependencies and integration: Depends on facility probing, generic vDSO getrandom include selected by the Makefile, and syscall fallback helper.

Risks and test signals: Risks include incorrect support probing and probe-call semantics. Test signals are vDSO getrandom on machines with and without facility 129, fallback syscall behavior, special probe return, and flag/length edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vgetrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vmcore_info.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vmcore_info.c

Purpose: Adds s390-specific metadata to vmcore notes for crash dump consumers and records the physical vmcore-info note address in absolute lowcore.

Important API: `arch_crash_save_vmcoreinfo()`.

Control flow: Emits symbols and lengths for `lowcore_ptr` and `high_memory`, appends s390 address-mode and relocation values (`SAMODE31`, `EAMODE31`, `IDENTITYBASE`, `KERNELOFFSET`, `KERNELOFFPHYS`), writes the physical note address into absolute lowcore `vmcore_info`, and releases the lowcore mapping.

State and persistence: Persists data in the vmcoreinfo note and absolute lowcore for dump tools/firmware.

Dependencies and integration: Depends on vmcore info helpers, absolute lowcore access, linker symbols for AMODE31, setup/KASLR state, and crash dump tooling expectations.

Risks and test signals: Risks are stale/missing relocation metadata and incorrect absolute lowcore update. Test signals include kdump vmcoreinfo contents, crash tool lookup of lowcore and AMODE31 ranges, and KASLR offset correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vmcore_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vmlinux.lds.S -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vmlinux.lds.S

Purpose: Linker script for the s390 kernel image, defining executable/data/init/percpu/BSS layout, special low-memory AMODE31 sections, stack-protector/nospec patch tables, boot-data metadata, and relocation assertions.

Important sections and symbols: `_stext`, `_etext`, `_sdata`, `__start_ro_after_init`, `__end_ro_after_init`, `.skey_region_table`, `BOOT_DATA_PRESERVED`, `.amode31.refs`, `__init_begin/end`, `.altinstructions`, `.stack_prot_table`, `.nospec_*_table`, `_samode31`, `_eamode31`, `.vmlinux.info`, and assertions for `.got.plt`, `.plt`, and `.rela.dyn`.

Control flow: The linker starts at `TEXT_OFFSET`, lays out text/rodata/data, separates ro-after-init, includes runtime data and boot-preserved blocks, emits init/exit/alternative tables, reserves fixed-size AMODE31 text/ex-table/data below the required range, emits init/percpu/BSS, includes debug/modinfo metadata, asserts absence of runtime PLT/relocations, and emits a zero-based `.vmlinux.info` structure consumed by the decompressor.

State and persistence: Produces the persistent kernel image layout and many symbols consumed by boot, decompressor, crash dump, stack protector, alternatives, KASAN, and AMODE31 code.

Dependencies and integration: Includes generic and s390 linker macros, ftrace linker fragments, page/thread constants, stack protector code, `text_amode31.S`, decompressor `vmlinux_info`, vmcore metadata, and build-time assertions.

Risks and test signals: Risks include section misalignment, AMODE31 overflow, unexpected relocations/PLT entries, missing stack protector/nospec tables, and decompressor metadata drift. Test signals are link-time assertions, `readelf` layout checks, boot success, stack protector patching, AMODE31 DIAG helpers, and vmcore info address ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vtime.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/vtime.c

Purpose: Implements s390 virtual CPU timer accounting, steal-time calculation, multi-threading scaling, and exported virtual timer list APIs.

Important APIs and functions: `vtime_task_switch()`, `vtime_flush()`, `vtime_account_kernel()`, `vtime_account_softirq()`, `vtime_account_hardirq()`, `init_virt_timer()`, `add_virt_timer()`, `add_virt_timer_periodic()`, `mod_virt_timer()`, `mod_virt_timer_periodic()`, `del_virt_timer()`, and `vtime_init()`.

Control flow: Low-level timer reads update lowcore last-update fields, classify elapsed CPU-timer deltas into user, guest, system, hardirq, softirq, and steal buckets, scale user/system times for SMT utilization when needed, and push accounting to generic kernel time accounting. `vtime_flush()` also expires virtual timers when accumulated elapsed CPU time reaches the current virtual timer deadline. Virtual timers are kept in a sorted list protected by `virt_timer_lock`; expired callbacks run outside the lock and periodic timers are reinserted.

State and persistence: Owns global virtual timer list/lock, atomic current and elapsed virtual timer counters, per-CPU MT cycle arrays/scaling factors, and lowcore timer fields mirrored in task thread timer fields during context switch.

Dependencies and integration: Integrates with entry code lowcore timer updates, generic CPU/accounting APIs, CPU measurement facility `stcctm`, SMP SMT metadata, lowcore CPU timer instructions, and exported vtimer users.

Risks and test signals: Risks include accounting drift, steal-time underflow/overflow, timer-list races, callbacks modifying timers, and SMT scaling arithmetic. Test signals include `/proc/stat` user/system/irq/softirq/steal accounting, guest time for `PF_VCPU`, vtimer add/mod/del behavior, CPU hotplug vtime initialization, and SMT utilization scaling changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/vtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/wti.c -->
## sources/distributed-fs/ceph-client/arch/s390/kernel/wti.c

Purpose: Supports s390 warning-track interruption, where a real-time per-CPU thread acknowledges hypervisor warning-track events and temporarily suppresses I/O interrupts during the grace period.

Important APIs and functions: Init `wti_init()`, external IRQ handler `wti_interrupt()`, per-CPU thread callback `wti_thread_fn()`, debugfs show `wti_show()`, and helpers `wti_irq_disable()`, `wti_irq_enable()`, `store_debug_data()`, and `wti_dbf_grace_period()`.

Control flow: Late init checks SCLP WTI support, registers per-CPU smpboot threads, raises their scheduler policy to near-max `SCHED_FIFO`, registers the warning-track external interrupt and IRQ subclass, registers with DIAG 49C, and creates debugfs/s390dbf reporting. On interrupt, it increments IRQ stats, disables I/O interrupts in CR6, records current PID/kernel PSW address, marks per-CPU pending, and wakes the CPU thread. The thread clears pending, acknowledges with DIAG 49C, records missed grace periods if needed, and re-enables I/O interrupts.

State and persistence: Per-CPU `wti_state` stores debug data, thread pointer, and pending flag. Global `wti_dbg` stores s390dbf state. Debugfs `wti/stat` exposes missed counts.

Dependencies and integration: Depends on SCLP feature discovery, DIAG 49C, external IRQ registration, irq subclassing, smpboot per-CPU threads, scheduler RT policy, debugfs, kallsyms `%pS`, and s390 debug feature.

Risks and test signals: Risks include leaving I/O interrupts disabled after error paths, thread scheduling delays, init cleanup leaks, and debug data from user-mode regs. Test signals include WTI interrupt counts, per-CPU `cpuwti/%u` thread wakeups, debugfs missed counters, s390dbf records, DIAG 49C registration/ack failures, and CPU hotplug behavior of smpboot threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/wti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/Kconfig -->
## sources/distributed-fs/ceph-client/arch/s390/kvm/Kconfig

Purpose: Defines s390 virtualization and KVM configuration options.

Important symbols: `VIRTUALIZATION`, `KVM`, and `KVM_S390_UCONTROL`. `KVM` selects common KVM support, async page fault variants, IRQ chip/routing capabilities, invalid wakeup/no-poll behavior, VFIO integration, guest-work transfer, and lockless aging.

Control flow: Sources common `virt/kvm/Kconfig`, presents the `KVM` menu, enables `KVM` by default when virtualization is enabled, and gates userspace-controlled VMs behind `KVM`.

State and persistence: Build-time Kconfig state determines whether s390 KVM objects are built and whether userspace-controlled VM support is available.

Dependencies and integration: Integrates with common KVM infrastructure, SIE virtualization hardware support, `/dev/kvm`, VFIO, async PF, and s390 KVM source Makefile.

Risks and test signals: Risks are missing `select` dependencies causing build or runtime feature gaps, and default-y behavior enabling unexpected code. Test signals include Kconfig dependency resolution, modular and built-in KVM builds, `/dev/kvm` availability, and userspace-controlled VM option visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/Makefile -->
## sources/distributed-fs/ceph-client/arch/s390/kvm/Makefile

Purpose: Builds the s390 KVM module/object composition.

Important variables: Includes `virt/kvm/Makefile.kvm`, sets include flags for common and s390 KVM headers, builds `kvm-y` from `kvm-s390.o`, intercept/interrupt/priv/sigp, diag/gaccess/guestdbg/vsie/pv, `dat.o`, `gmap.o`, `faultin.o`, optional PCI zdev support, and links `kvm.o` under `CONFIG_KVM`.

Control flow: Kbuild aggregates architecture-specific objects into the KVM composite object and adds optional `pci.o` when VFIO PCI zdev KVM support is enabled.

State and persistence: Build output is `kvm.o` or module `kvm`. No runtime state is owned by the Makefile.

Dependencies and integration: Connects common KVM build logic with s390 implementation files including `dat.c`, gmap, SIE intercepts, protected virtualization, and VFIO PCI device support.

Risks and test signals: Risks are object ordering/dependency omissions and missing include paths. Test signals are built-in/module KVM builds, optional PCI config builds, and link resolution for s390 KVM symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/dat.c -->
## sources/distributed-fs/ceph-client/arch/s390/kvm/dat.c

Purpose: Implements KVM s390 dynamic address translation table management for guest address spaces: allocation caches, ASCE resizing, CRST/PTE walking and splitting, atomic entry exchange with invalidation, storage-key handling, memory-slot token insertion, CMMA/ESSA state, aging, and prefix notification bits.

Important APIs and functions: `kvm_s390_mmu_cache_topup()`, `dat_alloc_crst_sleepable()`, `dat_free_level()`, `dat_set_asce_limit()`, `dat_crstep_xchg_atomic()`, `__dat_ptep_xchg()`, `dat_entry_walk()`, `_dat_walk_gfn_range()`, `dat_get_storage_key()`, `dat_set_storage_key()`, `dat_cond_set_storage_key()`, `dat_reset_reference_bit()`, `dat_reset_skeys()`, `dat_set_slot()`, `dat_get_ptval()`, `dat_set_ptval()`, `dat_test_age_gfn()`, `dat_set_prefix_notif_bit()`, `dat_perform_essa()`, `dat_reset_cmma()`, `dat_peek_cmma()`, `dat_get_cmma()`, and `dat_set_cmma_bits()`.

Control flow: The MMU cache preallocates CRST tables, page tables, and reverse-map objects. ASCE limit changes wrap or unwrap the top table levels. Table walking validates ASCE coverage, descends region/segment/page levels, handles holes and PIC tokens, optionally allocates missing tables, splits large entries into smaller tables, and returns either a CRSTE or PTE pointer. Atomic CRSTE/PTE replacement uses compare-exchange, CRDTE/CSPG/IPTE invalidation depending on CPU features and guest TLB support. Storage-key helpers move hardware keys into PGSTE on invalidation, restore them on validation, or update physical keys directly for large entries. Range walkers apply callbacks over CRST and PTE ranges and power slot tokenization, skey reset, aging, CMMA, and prefix-notification logic.

State and persistence: Persistent state is the guest DAT tree rooted at an ASCE, allocated page/CRST tables with architecture DAT page state, PGSTEs paired with PTEs, physical storage keys, CMMA dirty/usage/nodat bits, prefix/vSIE notification bits, and memory-slot hole tokens. Callers are expected to hold the KVM MMU lock for mutation paths; PTE PGSTE fields use per-entry locks.

Dependencies and integration: Integrates with s390 KVM `gmap`, SIE translation, memory slots, storage keys, ESSA/CMMA virtualization, page-state helpers, TLB invalidation primitives (`IPTE`, `CRDTE`, `CSPG`), common KVM aging APIs, host mm folio/page tables, and protected virtualization page ownership indirectly through memory-state handling.

Risks and test signals: Highest risks are incorrect invalidation when replacing valid guest entries, storage-key loss across valid/invalid transitions, splitting large entries while preserving PGSTE state, ASCE limit shrink/grow leaks, range-walk hole semantics, and CMMA dirty accounting. Test signals include KVM guest boot/memory hotplug, storage-key instructions, ESSA/CMMA migration ioctls, dirty/young page aging, large-page split paths, prefix-page notification, memory-slot add/remove, guest TLB invalidation stress, and lockdep around `kvm->mmu_lock` plus PGSTE locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/dat.c -->
