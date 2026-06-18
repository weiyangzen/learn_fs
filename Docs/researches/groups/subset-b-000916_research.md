# Research: subset-b-000916

Grouped research for Xen x86 paravirtual/HVM support files and Xtensa architecture build, boot, MMU, ABI, atomic, cache, memory, IRQ, PCI, and low-level header contracts. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/pmu.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/pmu.c

## Purpose
Implements Xen PV virtual PMU integration for x86 guests. It maps Xen's per-vCPU PMU shared page into Linux perf handling, emulates PMU MSR reads/writes while a Xen PMU interrupt is being processed, exposes PMC reads, updates the PMU LAPIC LVT state through Xen, and registers perf guest callbacks so dom0 can attribute samples to guest contexts.

## Important APIs, Types, And Functions
Key state is `struct xenpmu` in `xenpmu_shared`, plus `is_xen_pmu`. CPU-family setup is in `xen_pmu_arch_init`. MSR dispatch is handled by `is_amd_pmu_msr`, `is_intel_pmu_msr`, `xen_amd_pmu_emulate`, `xen_intel_pmu_emulate`, and exported `pmu_msr_chk_emulated`. Runtime hooks are `xen_read_pmc`, `pmu_apic_update`, `xen_pmu_irq_handler`, `xen_pmu_init`, and `xen_pmu_finish`.

## Control Flow
`xen_pmu_init` allocates one zeroed page per CPU, passes its MFN to `XENPMU_init`, stores it in percpu state, and on the first success registers perf guest callbacks and initializes vendor PMU register layout. During `VIRQ_XENPMU`, the handler marks `XENPMU_IRQ_PROCESSING`, converts Xen register state into `pt_regs`, invokes `x86_pmu.handle_irq`, flushes changed PMU state with `XENPMU_flush`, and clears the flag. PMU MSR access only redirects to shared-page state while that flag is active; otherwise PMC reads fall back to native MSR reads.

## State And Persistence
State is per-CPU shared pages, per-CPU IRQ-processing flags, read-mostly vendor PMU register layout, and perf callback registration. There is no durable persistence, but hypervisor PMU registration persists until `XENPMU_finish`, CPU hotplug teardown, suspend, or shutdown.

## Dependencies And Integration Points
Depends on Xen `xenpmu_op`, `xen_pmu_data` layout, x86 vendor/CPUID MSR definitions, Linux perf x86 PMU hooks, Xen event IRQ binding in SMP code, and `xen-ops.h` declarations. It integrates with suspend/resume through `xen_arch_suspend` and `xen_arch_resume`, and with SMP PV interrupt setup through `VIRQ_XENPMU`.

## Risks And Edge Cases
High-risk areas are vendor-specific MSR range detection, AMD family 15h K7 mirror handling, Intel fixed/general/alias counter indexing, shared-page offset arithmetic, and only treating MSRs as emulated while IRQ processing is active. Hypercall failures disable or degrade PMU support. Incorrect guest-state attribution can mislead perf in dom0. HVM domains intentionally return early.

## Test Signals
Useful signals are x86 Xen PV boots with perf enabled, successful `VIRQ_XENPMU` binding, perf sampling inside dom0 and guests, MSR emulation tests for Intel fixed/general counters and AMD family 10h/15h counters, CPU hotplug PMU init/finish, and suspend/resume with PMU active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/setup.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/setup.c

## Purpose
Provides Xen PV x86 machine setup: memory map ingestion, E820 conflict handling, p2m/m2p remapping, initial extra-memory accounting, Xen callback registration, PV MMU setup, syscall callback setup, command-line import, idle policy, and ACPI/NUMA restrictions for PV guests.

## Important APIs, Types, And Functions
Major entry points are `xen_memory_setup`, `xen_remap_memory`, `xen_inv_extra_mem`, `xen_chk_extra_mem`, `xen_chk_is_e820_usable`, `xen_find_free_area`, `xen_enable_syscall`, and `xen_arch_setup`. Important internal helpers include `xen_set_identity_and_remap_chunk`, `xen_do_set_identity_and_remap_chunk`, `xen_update_mem_tables`, `xen_e820_resolve_conflicts`, `xen_e820_swap_entry_with_ram`, `xen_reserve_xen_mfnlist`, and `register_callback`.

## Control Flow
Boot parses the optional `xen_512gb_limit` command-line flag, derives the initial page count, asks Xen for the machine or guest memory map, normalizes it, checks kernel/start_info/page-table/initrd conflicts, computes extra pages needed for remapping, builds the kernel E820 table, identity maps non-RAM regions, reserves or relocates the Xen MFN list and initrd, then records remap work in a linked list stored inside pages being remapped. Later `xen_remap_memory` walks that list, updates p2m/m2p/VA mappings, releases consumed extra memory, and applies non-RAM remaps.

## State And Persistence
Boot-only state includes `xen_e820_table`, `ini_nr_pages`, `xen_remap_buf`, `xen_remap_mfn`, and `xen_512gb_limit`. Persistent runtime effects include modified p2m/m2p mappings, E820 entries, memblock reservations, `xen_extra_mem`, `xen_pv_pci_possible`, callback registration with Xen, disabled cpuidle/cpufreq, and copied boot command line.

## Dependencies And Integration Points
Depends on Xen memory, callback, physdev, feature, and console interfaces; x86 E820, memblock, boot params, fixmaps, NUMA, ACPI, and paravirt idle hooks; p2m code declared in `xen-ops.h`; and syscall entry assembly in `xen-asm.S`.

## Risks And Edge Cases
The most delicate logic is moving non-RAM E820 entries while preserving MFNs, remapping identity-mapped holes without allocating early memory, zapping stale VA mappings, and relocating initrd/p2m data when Xen placed them in E820-reserved ranges. Several failure paths call `BUG()`, making bad hypervisor maps fatal. The 512 GiB domU limit, extra-memory ratio, and hotplug `max_mem_size` interactions can restrict visible memory.

## Test Signals
Test with PV domU and dom0 boots across memory maps containing RAM, reserved, NVS, unusable, initrd conflicts, and high memory; verify E820 logs, p2m consistency, PCI passthrough identity mappings, syscall callback registration, and suspend/resume or balloon activity after remap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/smp.c

## Purpose
Provides Xen-common x86 SMP interrupt and IPI plumbing shared by PV and HVM guests. It binds Xen event-channel IPIs for reschedule and function-call vectors, optionally binds debug VIRQ, maps native x86 vectors to Xen synthetic vectors, and implements the SMP send hooks used by `smp_ops`.

## Important APIs, Types, And Functions
Per-CPU IRQ holders are `xen_resched_irq`, `xen_callfunc_irq`, `xen_callfuncsingle_irq`, and `xen_debug_irq`. Public hooks are `xen_smp_intr_init`, `xen_smp_intr_free`, `xen_smp_cpus_done`, `xen_smp_send_reschedule`, `xen_smp_send_call_function_ipi`, `xen_smp_send_call_function_single_ipi`, `xen_send_IPI_mask`, `xen_send_IPI_all`, `xen_send_IPI_self`, `xen_send_IPI_mask_allbutself`, and `xen_send_IPI_allbutself`.

## Control Flow
CPU bringup calls `xen_smp_intr_init`, which allocates names and binds per-CPU Xen IPI handlers for reschedule, call-function, and single-call-function vectors; non-FIFO event mode also binds `VIRQ_DEBUG`. IPI send helpers translate APIC vectors through `xen_map_vector` and iterate online CPUs with `xen_send_IPI_one`. Function-call IPIs yield to Xen if a target vCPU is stolen so the target can run promptly.

## State And Persistence
State is per-CPU IRQ numbers and allocated name strings. Bindings persist until CPU hotplug cleanup calls `xen_smp_intr_free`.

## Dependencies And Integration Points
Depends on Xen event APIs, Linux generic SMP IPI handlers, x86 vector constants, stolen-time detection, and `smp_ops` assignments in `smp_pv.c` and `smp_hvm.c`.

## Risks And Edge Cases
Binding failures must free all partially initialized IRQs. Unsupported vectors log an error and are dropped. `xen_smp_send_call_function_ipi` iterates the original mask for stolen vCPUs, so masks must describe valid CPUs. Debug VIRQ handling differs for FIFO events.

## Test Signals
Signals include successful CPU hotplug cycles, `/proc/interrupts` Xen IPI lines, scheduler and function-call IPI counters, no leaks after offline/online, and stress tests using `smp_call_function*`, rescheduling, NMI/debug paths, and HVM/PV boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp_hvm.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/smp_hvm.c

## Purpose
Adapts native x86 SMP operations for Xen HVM/PVHVM guests. It sets up Xen vCPU info placement, Xen time operations, spinlock paravirt alternatives, Xen IPI handlers, and CPU hotplug cleanup when Xen vector callbacks are available.

## Important APIs, Types, And Functions
Key functions are `xen_hvm_smp_prepare_boot_cpu`, `xen_hvm_smp_prepare_cpus`, `xen_hvm_cleanup_dead_cpu`, and `xen_hvm_smp_init`.

## Control Flow
Initialization overwrites selected members of the existing `smp_ops`. Boot CPU preparation calls native setup, installs vCPU info for CPU0, retries Xen HVM time initialization for high vCPU IDs, and initializes PV spinlocks. CPU preparation delegates to native SMP setup, then binds Xen IPI/lock IRQs for CPU0 only if vector callbacks exist and marks secondary vCPU IDs invalid until Xen CPU-up code assigns them. Without vector callbacks, PV spinlocks are disabled and IPI send hooks remain native.

## State And Persistence
Persistent state is the modified `smp_ops`, per-CPU `xen_vcpu_id` defaults, and event-channel IRQ state allocated by common SMP and spinlock code.

## Dependencies And Integration Points
Depends on native x86 SMP setup, Xen vector callback support, HVM vCPU setup, Xen time initialization, common Xen SMP IPI code, and paravirt spinlock globals.

## Risks And Edge Cases
The vector-callback gate is central: enabling Xen IPI hooks without callback delivery would break secondary CPU interrupts, while disabling them loses PV spinlock benefits. Booting on vCPU IDs outside embedded shared-info slots requires delayed time init. Hotplug cleanup without `CONFIG_HOTPLUG_CPU` intentionally bugs.

## Test Signals
Use HVM/PVHVM boots with and without vector callbacks, CPU hotplug, SMP function-call IPI stress, PV spinlock enable/disable logs, and timer setup on boot CPU and secondary CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp_hvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp_pv.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/smp_pv.c

## Purpose
Implements Xen PV `smp_ops` for x86. It prepares PV CPU topology, initializes per-CPU vCPU state and event channels, builds the Xen vCPU guest context for secondary CPUs, brings CPUs up/down through Xen `VCPUOP_*`, and wires PV-specific IRQ-work and PMU interrupts.

## Important APIs, Types, And Functions
Important state is `xen_cpu_initialized_map`, `xen_irq_work`, and `xen_pmu_irq`. Key functions include `cpu_bringup_and_idle`, `xen_smp_intr_init_pv`, `xen_smp_intr_free_pv`, `xen_pv_smp_prepare_boot_cpu`, `xen_pv_smp_prepare_cpus`, `cpu_initialize_context`, `xen_pv_kick_ap`, CPU hotplug callbacks, `xen_smp_count_cpus`, and `xen_smp_init`.

## Control Flow
Early setup installs PV `smp_ops` and suppresses BIOS MP table parsing. Boot CPU preparation makes the old GDT writable if needed, places vCPU info, and enables PV spinlock patching. CPU preparation initializes CPU0 locks, common SMP state, speculative-store-bypass topology, PMU, common/PV interrupts, and the initialized CPU mask. Secondary bringup runs `common_cpu_up`, sets runstate info, masks event upcalls, builds a `vcpu_guest_context` with GDT, trap callbacks, stack, CR3, and per-CPU base, calls `VCPUOP_initialise`, initializes PMU, then calls `VCPUOP_up`.

## State And Persistence
State includes CPU-present/possible masks, Xen initialized CPU mask, per-CPU IRQ bindings, readonly GDT pages, per-CPU CR3, per-CPU PMU pages, and vCPU runstate/timer/event-channel state. CPU teardown frees IRQs, locks, timers, and PMU pages.

## Dependencies And Integration Points
Depends on Xen vCPU, event, PMU, and page APIs; x86 descriptor, CPU, APIC, paravirt, and speculation setup; common Xen SMP code; Xen time code; and assembly entry points `asm_cpu_bringup_and_idle` and `xen_cpu_bringup_again`.

## Risks And Edge Cases
`cpu_initialize_context` is sensitive to descriptor alignment, readonly GDT handling, stack pointer placement, callback EIPs, and pfn-to-cr3 conversion. `nosmp` and `noapic` are fatal under PV. CPU0 cannot be hot-unplugged. PMU IRQ setup depends on global `is_xen_pmu`. Several hypercall failures are `BUG_ON`.

## Test Signals
Signals include PV boot with multiple vCPUs, CPU online/offline stress, `/proc/interrupts` for IRQ_WORK and PMU, successful function-call IPIs, PMU sampling, stop-other-CPUs behavior on shutdown, and boot tests with dom0/domU topology differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp_pv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/spinlock.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/spinlock.c

## Purpose
Provides Xen PV queued-spinlock hooks. It lets a vCPU blocked on a queued spinlock yield to Xen and wait for a disabled per-CPU event-channel IRQ, and lets unlock paths kick the target vCPU through a Xen synthetic IPI.

## Important APIs, Types, And Functions
State is `lock_kicker_irq`, `irq_name`, and `xen_qlock_wait_nest`. Main functions are `xen_qlock_kick`, `xen_qlock_wait`, `xen_init_lock_cpu`, `xen_uninit_lock_cpu`, and `xen_init_spinlocks`. It installs `pv_ops_lock.queued_spin_lock_slowpath`, `queued_spin_unlock`, `wait`, `kick`, and `vcpu_is_preempted`.

## Control Flow
`xen_init_spinlocks` disables PV spinlocks for one-vCPU or `nopvspin` configurations; otherwise it initializes the lock hash and patches PV qspinlock hooks. For each CPU, `xen_init_lock_cpu` binds `XEN_SPIN_UNLOCK_VECTOR`, disables the Linux IRQ so it is used as a pollable Xen event, and records its IRQ. Waiters clear a pending event on first-level entry or poll the IRQ if the lock byte still matches the expected value. Unlockers kick the owner CPU if its kicker IRQ exists.

## State And Persistence
Persistent state is per-CPU disabled IRQ bindings and names, plus global paravirt lock hook replacement. It has no durable persistence.

## Dependencies And Integration Points
Depends on Xen events, x86 qspinlock paravirt support, `virt_spin_lock_key`, `nopvspin`, and stolen-vCPU detection.

## Risks And Edge Cases
Waiting is skipped in NMI or before IRQ initialization, so paths fall back to spinning. Nested waits must avoid consuming another waiter's event. The dummy handler should never run because IRQs are disabled; delivery would trigger `BUG()`. CPU hotplug must unbind initialized IRQs only.

## Test Signals
Use lock-stress workloads on multi-vCPU Xen, CPU hotplug, boot with `mitigations=auto,nosmt`, `nopvspin`/single-vCPU configurations, and IRQ leak checks after offline/online.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/spinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/suspend.c

## Purpose
Provides architecture-level Xen suspend/resume coordination common to PV and HVM x86 guests. It saves and restores Xen time-memory areas, delegates PV/HVM domain-specific suspend hooks, preserves SPEC_CTRL state for PV, suspends/resumes local ticks, and restarts PMU state around suspend.

## Important APIs, Types, And Functions
Entry points are `xen_arch_pre_suspend`, `xen_arch_post_suspend`, `xen_arch_suspend`, and `xen_arch_resume`. Per-CPU state is `spec_ctrl`. Internal cross-CPU callbacks are `xen_vcpu_notify_suspend` and `xen_vcpu_notify_restore`.

## Control Flow
Pre-suspend saves Xen secondary time info and calls PV pre-suspend when needed. The suspend phase finishes PMU for all online CPUs, then runs a blocking callback on each CPU to suspend local ticks and, for PV SPEC_CTRL-capable CPUs, save and clear `MSR_IA32_SPEC_CTRL`. Post-suspend calls either PV or HVM restoration, restores Xen time-memory areas, then resume callbacks restore SPEC_CTRL and resume local ticks on non-boot CPUs. PMU pages are reinitialized after resume.

## State And Persistence
State is per-CPU saved `SPEC_CTRL`, Xen PMU registration state, tick state, and time-memory registration state. Effects are transient across Xen save/restore or migration.

## Dependencies And Integration Points
Depends on PV and HVM suspend helpers, Xen PMU init/finish, Xen time save/restore, Linux tick suspend/resume, CPU feature flags, and MSR accessors.

## Risks And Edge Cases
SPEC_CTRL clearing is PV-only and conditional on CPU feature support. Boot CPU tick handling is left to generic timekeeping resume. PMU finish/init ordering must match event-channel and CPU online state. Missing time restore can break sched_clock continuity.

## Test Signals
Exercise Xen save/restore and migration for PV and HVM guests with multiple CPUs, PMU enabled, SPEC_CTRL-capable CPUs, and active timers; verify monotonic time, no lost ticks, and no PMU registration leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend_hvm.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/suspend_hvm.c

## Purpose
Restores Xen HVM guest state after suspend or migration. It rebuilds shared-info and vCPU state when suspend was not cancelled, reinstalls upcall delivery, and re-runs emulated-device unplug logic.

## Important APIs, Types, And Functions
The sole exported function is `xen_hvm_post_suspend`.

## Control Flow
If the suspend completed, the function calls `xen_hvm_init_shared_info` and `xen_vcpu_restore`. It then either sets a per-CPU upcall vector for every online CPU when `xen_percpu_upcall` is enabled, or sets the global callback vector otherwise. Finally it calls `xen_unplug_emulated_devices` to restore the preferred PV device model state.

## State And Persistence
Persistent effects are reinitialized shared info mapping, restored vCPU info/callback vectors, and emulated-device unplug state. No filesystem persistence is involved.

## Dependencies And Integration Points
Depends on Xen HVM shared-info setup, upcall-vector support, online CPU iteration, and Xen feature/event helpers. It is invoked from `xen_arch_post_suspend`.

## Risks And Edge Cases
Per-CPU upcall setup is `BUG_ON` failure, so vector restore problems are fatal. Cancelled suspend skips shared-info/vCPU rebuild but still refreshes callback delivery and unplug state.

## Test Signals
Test HVM migration/save-restore with per-CPU and global callback modes, multiple online CPUs, and PV drivers loaded; inspect interrupt delivery and device enumeration after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend_hvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend_pv.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/suspend_pv.c

## Purpose
Handles Xen PV-specific pre/post suspend transitions. It pins/unpins MMU pages, converts start-info MFNs to PFNs before suspend, disconnects shared-info mapping, rebuilds MFN-list structures afterward, restores shared info, and handles cancelled versus completed suspend differently.

## Important APIs, Types, And Functions
Exports `xen_pv_pre_suspend` and `xen_pv_post_suspend`.

## Control Flow
Pre-suspend pins all MMU state, converts store and console MFNs in `xen_start_info` to PFNs, requires interrupts disabled, switches `HYPERVISOR_shared_info` to `xen_dummy_shared_info`, and clears the boot fixmap mapping. Post-suspend rebuilds MFN list metadata, restores the shared-info fixmap, and either converts saved PFNs back to MFNs on cancelled suspend or resets `xen_cpu_initialized_map` and calls `xen_vcpu_restore` on real resume. It then unpins MMU state.

## State And Persistence
State touched includes `xen_start_info`, `HYPERVISOR_shared_info`, fixmap entries, p2m/MFN list structures, MMU pinning, and SMP initialized CPU masks. Effects are transient across suspend.

## Dependencies And Integration Points
Depends on Xen p2m and MMU helpers, fixmaps, shared-info mapping, SMP mask state, and `xen_arch_pre_suspend`/`post_suspend`.

## Risks And Edge Cases
MFN/PFN conversion must be paired correctly, especially for cancelled suspend. Interrupts must be disabled before shared-info is detached. SMP resume requires `xen_cpu_initialized_map` to exist. Fixmap update failures are fatal.

## Test Signals
Use PV suspend cancel and complete paths, console/store channel functionality after resume, multi-vCPU resume, and p2m consistency checks after migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend_pv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/time.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/time.c

## Purpose
Implements Xen x86 clocksource, sched_clock, wallclock, clockevent, timer IRQ, VDSO pvclock, stolen-time, and suspend/resume time-memory handling for PV and HVM guests.

## Important APIs, Types, And Functions
Core functions include `xen_clocksource_read`, `xen_sched_clock`, `xen_read_wallclock`, `xen_pvclock_gtod_notify`, `xen_setup_timer`, `xen_teardown_timer`, `xen_setup_cpu_clockevents`, `xen_timer_resume`, `xen_save_time_memory_area`, `xen_restore_time_memory_area`, `xen_setup_vsyscall_time_info`, `xen_time_init`, `xen_init_time_ops`, and `xen_hvm_init_time_ops`. Major state includes `xen_clocksource`, timer-op/vcpu-op `clock_event_device` templates, per-CPU `xen_clock_events`, `xen_clock`, and `xen_sched_clock_offset`.

## Control Flow
Initialization registers the Xen clocksource, tries to disable the old periodic tick to select the newer vCPU single-shot timer interface, sets wallclock time from Xen, enables TSC capability, configures pvclock VDSO data when stable, sets runstate info, binds the per-CPU timer VIRQ, and registers clockevents. HVM initialization is gated by vector callbacks, safe pvclock feature support, and available per-CPU vCPU info. Suspend saves secondary time memory and sched_clock baseline; resume re-registers time memory and recalculates the offset.

## State And Persistence
State is per-CPU timer IRQs and clockevents, global clocksource rating/mode, VDSO pvclock page, wallclock notifier state, and sched_clock offset. No durable persistence exists, but hypervisor time-memory registration and VIRQ bindings persist during runtime.

## Dependencies And Integration Points
Depends on Xen shared info, vCPU ops, platform ops, event channels, pvclock, x86 time platform hooks, VDSO clock mode, stolen-time static calls, and SMP CPU hotplug timer setup.

## Risks And Edge Cases
HVM boot on vCPU IDs outside embedded shared-info slots delays initialization. VDSO pvclock is usable only with stable TSC flags and successful secondary time registration; fallback is syscall time. Clocksource rating must avoid overriding safe TSC unnecessarily. Timer slop can be tuned through `xen_timer_slop`. Many timer hypercall failures are fatal.

## Test Signals
Validate PV/HVM boot timekeeping, clocksource selection, VDSO pvclock mode, wallclock set from dom0, single-shot timer accuracy, CPU hotplug timer setup/teardown, suspend/resume monotonicity, and `xen_timer_slop` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/trace.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/trace.c

## Purpose
Defines Xen tracepoint support and hypercall-name resolution for ftrace/perf trace events.

## Important APIs, Types, And Functions
The file builds `xen_hypercall_names[]` from `asm/xen-hypercalls.h`, provides `xen_hypercall_name`, defines `CREATE_TRACE_POINTS`, and includes `trace/events/xen.h`.

## Control Flow
At compile time, the `HYPERCALL` macro turns hypercall op numbers into an indexed string table. Trace event code can call `xen_hypercall_name` to render a known hypercall or an empty string for unknown/out-of-range values.

## State And Persistence
State is a static read-only string table and generated tracepoint definitions. Runtime persistence is only tracepoint registration by the tracing subsystem.

## Dependencies And Integration Points
Depends on Linux ftrace, Xen public hypercall definitions, MCA definitions used by trace events, and `trace/events/xen.h`.

## Risks And Edge Cases
The string table must remain aligned with `__HYPERVISOR_*` numbering. Unknown ops intentionally return an empty string, so tooling should not assume every trace record has a name.

## Test Signals
Build with Xen tracepoints enabled and inspect `/sys/kernel/tracing/events/xen`; run workloads issuing hypercalls and verify trace output names known operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/vga.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/vga.c

## Purpose
Translates Xen dom0 VGA console metadata into Linux `screen_info` so early console and framebuffer setup can use text, VESA LFB, or EFI LFB details supplied by Xen.

## Important APIs, Types, And Functions
The entry point is `xen_init_vga(const struct dom0_vga_console_info *info, size_t size, struct screen_info *screen_info)`.

## Control Flow
The function initializes conservative VGA text defaults, then switches on `info->video_type`. Text mode updates rows, columns, cursor, and font height after validating the structure size. VESA/EFI LFB updates dimensions, depth, framebuffer base/size, line length, color masks, 64-bit base capability, and optional VESA mode attributes; EFI LFB sets `VIDEO_TYPE_EFI`.

## State And Persistence
It only mutates the caller-provided `screen_info`, which persists as boot/video configuration. No durable storage is touched.

## Dependencies And Integration Points
Depends on Xen `dom0_vga_console_info`, Linux `screen_info`, and x86 setup video constants. It is called from Xen x86 boot setup paths for initial domain console discovery.

## Risks And Edge Cases
Size checks prevent reading missing union members, but unsupported or truncated records leave defaults. Incorrect Xen-provided LFB base, color masks, or line length can break early framebuffer output. Extended LFB base is used only when present and nonzero.

## Test Signals
Boot dom0 with text VGA, VESA LFB, and EFI LFB; verify `screen_info`, early console, fbcon/efifb handoff, 64-bit framebuffer base handling, and truncated metadata fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/vga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-asm.S -->
# sources/distributed-fs/ceph-client/arch/x86/xen/xen-asm.S

## Purpose
Provides low-level Xen PV x86 assembly entry points for hypercalls, interrupt enable/disable/save flags, CR2 reads, trap stubs, early IDT handlers, IRET, syscall/sysenter callbacks, and return-to-usermode paths.

## Important APIs, Types, And Functions
Important symbols include `xen_hypercall_pv`, `xen_irq_disable_direct`, `xen_irq_enable_direct`, `xen_save_fl_direct`, `xen_read_cr2`, `xen_read_cr2_direct`, generated `xen_asm_exc_*` trap labels, `xen_early_idt_handler_array`, `xen_iret`, `xenpv_restore_regs_and_return_to_usermode`, `xen_entry_SYSCALL_64`, `xen_entry_SYSCALL_compat`, and `xen_entry_SYSENTER_compat`.

## Control Flow
The IRQ helpers directly manipulate Xen vCPU event masks and call `check_events` to force callback processing when unmasking reveals pending events. Trap stubs push vector/error-code shape expected by common x86 handlers. `xen_iret` and syscall entry wrappers use the Xen `iret` hypercall path rather than native return where PV privilege rules require it. Compatibility entry points normalize `%rsp` and branch into common x86 syscall handling.

## State And Persistence
No C-visible data persists, but the assembly reads/writes per-CPU Xen vCPU info fields, CR2, and CPU registers. The symbols become callback targets registered in `setup.c` and SMP bringup.

## Dependencies And Integration Points
Depends on x86 calling conventions, Xen PV ABI, IDT entry macros, paravirt patching, syscall entry code, and callback registration in `xen_enable_syscall`/`xen_pvmmu_arch_setup`.

## Risks And Edge Cases
Register save/restore, stack shape, flags semantics, event-mask pending checks, and 32/64-bit conditional code are extremely sensitive. Missing callback processing after enabling events can lose interrupts. Callback targets must match Xen's expected code segment and privilege model.

## Test Signals
Signals include PV boot, syscall and compat-syscall tests, exception/fault handling, interrupt storm tests, preemption/return-to-user stress, and objtool/unwind validation where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-head.S -->
# sources/distributed-fs/ceph-client/arch/x86/xen/xen-head.S

## Purpose
Contains Xen x86 early entry and hypercall-page assembly. It provides the PV startup symbol, secondary CPU bringup trampolines, and HVM/PV hypercall stubs including vendor-specific AMD/Intel VMCALL/VMMCALL entry points.

## Important APIs, Types, And Functions
Important symbols are `startup_xen`, `asm_cpu_bringup_and_idle`, `xen_cpu_bringup_again`, `xen_hypercall_hvm`, `xen_hypercall_amd`, `xen_hypercall_intel`, and Xen ELF notes/hypercall page definitions in the remainder of the file.

## Control Flow
`startup_xen` is the Xen-loaded entry point and transfers control into the C Xen startup path with the Xen start-info pointer. CPU bringup symbols switch stacks or jump into `cpu_bringup_and_idle` after a CPU is started or reawakened. HVM hypercall stubs provide aligned call slots used by the hypercall machinery and dispatch through the selected instruction sequence.

## State And Persistence
State is architectural register/stack setup at entry plus the compiled hypercall page. Xen ELF notes persist in the kernel image and inform the hypervisor loader.

## Dependencies And Integration Points
Depends on Xen loader ABI, Linux compressed/uncompressed x86 entry conventions, C functions declared in `xen-ops.h`, and runtime hypercall patch/selection code.

## Risks And Edge Cases
Wrong ELF notes or entry register assumptions prevent Xen from booting the image. Hypercall stubs must match Xen ABI register clobbers and alignment. Secondary bringup stack handling must align with `smp_pv.c`.

## Test Signals
Boot PV and HVM Xen kernels, bring secondary CPUs online/offline, verify hypercall execution on Intel and AMD hosts, and inspect built image notes with ELF tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-ops.h -->
# sources/distributed-fs/ceph-client/arch/x86/xen/xen-ops.h

## Purpose
Central private header for x86 Xen implementation files. It declares PV/HVM setup, memory, time, vCPU, SMP, spinlock, VGA, EFI, suspend, multicall, PMU, hypercall, and low-level assembly interfaces, with stubs for disabled configuration blocks.

## Important APIs, Types, And Functions
Major declarations include Xen start/shared-info globals, memory/p2m helpers, `xen_arch_setup`, time hooks, vCPU placement/restoration, SMP hooks, spinlock setup, VGA setup, EFI setup, suspend hooks, `struct multicall_space` and batching helpers, PMU hooks, CPU bringup assembly, IPI functions, and hypercall stubs.

## Control Flow
This header does not execute control flow directly. Its inline helpers route multicall batching through `xen_mc_batch`, `xen_mc_entry`, and `xen_mc_issue`, and compile-time stubs collapse optional features such as SMP, spinlocks, VGA, EFI, PMU, and HVM/PV suspend when configuration symbols are absent.

## State And Persistence
It exposes shared globals and structs but owns no independent state. Its inline multicall helpers affect per-CPU multicall batching state maintained elsewhere.

## Dependencies And Integration Points
Integrates nearly all files in `arch/x86/xen`, x86 page/table types, Xen public interfaces, event/IPI constants, and paravirt/hypercall assembly.

## Risks And Edge Cases
Header drift causes link failures or, worse, mismatched assumptions across low-level C and assembly. Optional stub behavior must preserve valid builds for configurations without SMP, PMU, VGA, EFI, or suspend variants. Multicall issue modes must be used with the correct batching lifecycle.

## Test Signals
All Xen x86 defconfig combinations are relevant: PV, HVM/PVHVM, SMP/non-SMP, PMU enabled/disabled, EFI, VGA, suspend, and paravirt spinlock configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Kbuild -->
# sources/distributed-fs/ceph-client/arch/xtensa/Kbuild

## Purpose
Top-level Kbuild include list for Xtensa architecture directories.

## Important APIs, Types, And Functions
It defines `obj-y += kernel/ mm/ platforms/`.

## Control Flow
During Kbuild evaluation, Xtensa always descends into architecture kernel, memory-management, and platform support directories for the selected configuration.

## State And Persistence
No runtime state. Build state is the object-directory traversal graph.

## Dependencies And Integration Points
Integrates Xtensa architecture code with the global kernel build system. The selected subdirectories depend on Kconfig and Makefiles beneath them.

## Risks And Edge Cases
Omitting one of these directories would produce missing core symbols. Adding platform or MM code elsewhere requires this traversal to remain complete.

## Test Signals
Build any Xtensa defconfig and verify Kbuild descends into `arch/xtensa/kernel`, `arch/xtensa/mm`, and `arch/xtensa/platforms`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Kconfig -->
# sources/distributed-fs/ceph-client/arch/xtensa/Kconfig

## Purpose
Defines the Xtensa architecture feature matrix and user-visible configuration: processor variant, MMU support, ABI choices, SMP, platform selection, boot parameters, semihosting, simulated disks, XIP, memory layout, vectors, highmem, and hibernation.

## Important APIs, Types, And Functions
Important symbols include `XTENSA`, `MMU`, `XTENSA_VARIANT_*`, `XTENSA_VARIANT_NAME`, `XTENSA_VARIANT_MMU`, `XTENSA_VARIANT_HAVE_PERF_EVENTS`, `XTENSA_FAKE_NMI`, `PFAULT`, `HAVE_SMP`, `SMP`, `NR_CPUS`, `KERNEL_ABI_*`, `USER_ABI_*`, `XTENSA_PLATFORM_*`, `USE_OF`, `PARSE_BOOTPARAM`, `INITIALIZE_XTENSA_MMU_INSIDE_VMLINUX`, `XIP_KERNEL`, `MEMMAP_CACHEATTR`, `KSEG_PADDR`, `KERNEL_LOAD_ADDRESS`, `XTENSA_VECTORS_*`, `HIGHMEM`, and `ARCH_FORCE_MAX_ORDER`.

## Control Flow
Kconfig selects generic kernel capabilities, chooses endianness from the compiler, selects a core variant directory, optionally enables MMU and perf features, controls ABI compiler flags through the Makefile, chooses one board platform, and derives memory layout constants consumed by headers and linker scripts.

## State And Persistence
The persistent output is `.config`, generated autoconf headers, and build-time feature selection. Runtime state is indirect through compiled code paths and memory layout constants.

## Dependencies And Integration Points
Feeds `arch/xtensa/Makefile`, `kmem_layout.h`, `initialize_mmu.h`, `page.h`, boot linker scripts, platform code, OF DTB builds, and generic kernel feature gates.

## Risks And Edge Cases
Incorrect variant names break include paths. ABI mismatches can make user signal delivery or kernel assembly invalid. KSEG and load-address misalignment can prevent boot. `MEMMAP_CACHEATTR` values are MMU-type specific. `XTENSA_FAKE_NMI` is safe only under strict interrupt-level constraints.

## Test Signals
Run `allyesconfig`/defconfig-style compile coverage for FSF, DC232B, DC233C, custom MMU/noMMU, ISS/XTFPGA/XT2000, call0/windowed ABI, SMP, highmem, OF, and XIP combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/Makefile

## Purpose
Defines Xtensa architecture build flags, variant/platform include paths, linker emulation, default cross-compiler prefix, boot targets, syscall header generation, and user-facing build help.

## Important APIs, Types, And Functions
Key variables are `variant-y`, `VARIANT`, `platform-*`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `KBUILD_LDFLAGS`, `CHECKFLAGS`, `vardirs`, `plfdirs`, `KBUILD_CPPFLAGS`, `KBUILD_DEFCONFIG`, `libs-y`, and `boot`.

## Control Flow
Kbuild derives the variant from `CONFIG_XTENSA_VARIANT_NAME`, optionally sets `CROSS_COMPILE`, selects a platform directory from `CONFIG_XTENSA_PLATFORM_*`, adds Xtensa-specific compiler flags such as `-mlongcalls` and `-mtext-section-literals`, enables call0 ABI flags when requested, adds variant/platform include paths, and forwards `Image`, `zImage`, `uImage`, or `xipImage` to `arch/xtensa/boot`.

## State And Persistence
No runtime state. It controls object code ABI, include resolution, generated boot artifacts, and sparse endianness defines.

## Dependencies And Integration Points
Depends on Kconfig symbols, Xtensa toolchain support, variant/platform directories, `arch/xtensa/lib`, boot Makefiles, and syscall-generation make targets.

## Risks And Edge Cases
Wrong ABI flags break assembly/C linkage. Missing variant include directories fail builds. `--no-relax` and PIC/FDPIC flags depend on toolchain behavior. Boot target forwarding must match files produced by boot subdirectories.

## Test Signals
Build representative Xtensa defconfigs with windowed and call0 ABI, big/little endian toolchains, all boot targets, and custom variant/platform paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/Makefile

## Purpose
Coordinates Xtensa boot image generation: raw `Image`, compressed `zImage`, U-Boot `uImage`, and XIP image outputs.

## Important APIs, Types, And Functions
Important targets and variables are `vmlinux.bin`, `vmlinux.bin.gz`, `boot-*`, `Image`, `zImage`, `uImage`, `xipImage`, `OBJCOPYFLAGS`, `UIMAGE_LOADADDR`, and `UIMAGE_COMPRESSION`.

## Control Flow
Kbuild strips `vmlinux` into a flat binary, gzips it for compressed images, selects boot loaders by platform, descends into `boot-elf` for `Image` and `boot-redboot` for `zImage`, wraps `vmlinux.bin.gz` as a U-Boot image, and objcopies `vmlinux` directly for XIP.

## State And Persistence
Build artifacts persist under `arch/xtensa/boot`: binary, gzip, ELF, redboot, U-Boot, and XIP images. No runtime state exists.

## Dependencies And Integration Points
Depends on boot subdirectories, boot lib archive, `uimage` command support, and `CONFIG_KERNEL_LOAD_ADDRESS`.

## Risks And Edge Cases
Wrong platform-to-target mapping yields unsupported images. U-Boot load address must match memory layout. XIP image must not be compressed.

## Test Signals
Run `make Image`, `zImage`, `uImage`, and `xipImage` for ISS, XT2000, and XTFPGA configurations and verify artifact names and headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/Makefile

## Purpose
Builds the uncompressed Xtensa ELF boot image with reset-vector bootstrap code and an embedded raw kernel binary section.

## Important APIs, Types, And Functions
Key variables and targets are `OBJCOPY_ARGS`, `CPPFLAGS_boot.lds`, `boot-y := bootstrap.o`, `boot.lds`, `Image.o`, and `Image.elf`.

## Control Flow
The Makefile objcopies `vmlinux.bin` into a new `image` section attached to `bootstrap.o`, then links it with `boot.lds` using Xtensa linker flags and no build ID to produce `Image.elf`.

## State And Persistence
Persistent outputs are `Image.o`, generated `boot.lds`, and `../Image.elf`.

## Dependencies And Integration Points
Depends on endian-specific Xtensa ELF objcopy format, `bootstrap.S`, `boot.lds.S`, and the parent boot Makefile's `vmlinux.bin`.

## Risks And Edge Cases
The embedded section flags and linker placement must match the reset vector and kernel load address. Endianness mismatch produces an unusable image.

## Test Signals
Build `make Image`, inspect `Image.elf` sections and entry point, and boot on ISS or hardware using the ELF loader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/boot.lds.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/boot.lds.S

## Purpose
Linker script for the Xtensa uncompressed ELF boot image. It places the reset vector, embedded kernel image, and bootstrap BSS at the addresses required by the Xtensa loader and kernel memory layout.

## Important APIs, Types, And Functions
Defines `OUTPUT_ARCH(xtensa)`, `ENTRY(_ResetVector)`, `.ResetVector.text`, `.image`, `_image_start`, `_image_end`, `.bss`, `__bss_start`, and `__bss_end`.

## Control Flow
At link time, reset-vector code is located at `XCHAL_RESET_VECTOR_VADDR`; the embedded `image` section is linked at `KERNELOFFSET` but loaded at `CONFIG_KERNEL_LOAD_ADDRESS`; BSS follows the loaded image aligned to four bytes.

## State And Persistence
It creates image-layout symbols consumed by bootstrap assembly. No runtime state beyond linker-defined addresses.

## Dependencies And Integration Points
Depends on `asm/vectors.h`, `CONFIG_KERNEL_LOAD_ADDRESS`, `KERNELOFFSET`, and `bootstrap.S`.

## Risks And Edge Cases
Wrong load or virtual address breaks early jump into the kernel. BSS placement must not overlap the embedded image. Reset vector address must match the core configuration.

## Test Signals
Inspect linked `Image.elf` with `readelf`, verify `_ResetVector` entry and section addresses, and boot under the chosen Xtensa platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/boot.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/bootstrap.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/bootstrap.S

## Purpose
Reset-vector bootstrap for uncompressed Xtensa ELF images. It establishes a known processor state, optionally initializes the MMU before `vmlinux`, prepares a bootparam block, and jumps into the kernel image.

## Important APIs, Types, And Functions
Key labels are `_ResetVector`, `_bootparam`, `_SetupMMU`, and `reset`. It uses `initialize_mmu` from `asm/initialize_mmu.h` and constants from `asm/bootparam.h` and `asm/vectors.h`.

## Control Flow
The reset vector jumps to `_SetupMMU`, clears windowbase/windowstart for windowed cores, sets processor status, optionally invokes `initialize_mmu` when MMU initialization is not inside `vmlinux`, lowers interrupt level below debug, loads the kernel entry address (`CONFIG_KERNEL_LOAD_ADDRESS` for selected MMUv3 inside-vmlinux cases or `KERNELOFFSET` otherwise), sets bootparam pointer in `a2` when enabled, clears `a3/a4`, and jumps to the kernel.

## State And Persistence
State changes are CPU special registers and optional bootparam data embedded in the image. No durable persistence.

## Dependencies And Integration Points
Depends on Xtensa reset-vector semantics, ABI registers, MMU initialization macros, boot parameter parser, and kernel startup entry expectations.

## Risks And Edge Cases
Windowed register state, PS value, interrupt level, and MMU mapping must be correct before the jump. Wrong entry address selection breaks MMUv3 and U-Boot/KEXEC layouts.

## Test Signals
Boot uncompressed `Image.elf` with and without `CONFIG_PARSE_BOOTPARAM`, with inside-vmlinux and bootstrap MMU initialization, and verify early kernel entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/bootstrap.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/Makefile

## Purpose
Builds the compressed RedBoot-style Xtensa `zImage.redboot` image from bootstrap code, the gzipped kernel image, and boot decompression libraries.

## Important APIs, Types, And Functions
Key variables and targets are `OBJCOPY_ARGS`, `boot-y := bootstrap.o`, `LIBS := arch/xtensa/boot/lib/lib.a arch/xtensa/lib/lib.a`, `zImage.o`, `zImage.elf`, and `zImage.redboot`.

## Control Flow
The Makefile embeds `vmlinux.bin.gz` as an `image` section in `bootstrap.o`, links it with `boot.ld` and decompression libraries into `zImage.elf`, then strips it to a raw binary `zImage.redboot`.

## State And Persistence
Build outputs are `zImage.o`, `zImage.elf`, and `../zImage.redboot`.

## Dependencies And Integration Points
Depends on RedBoot bootstrap assembly, parent boot gzip output, boot lib zlib objects, architecture lib helpers, and Xtensa endian-specific objcopy format.

## Risks And Edge Cases
Linker script, embedded section, and decompressor memory assumptions must agree. Endianness mismatch or missing zlib copy objects breaks the boot image.

## Test Signals
Build and boot `zImage.redboot`, inspect embedded image section and final binary size, and validate decompression path on target platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/bootstrap.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/bootstrap.S

## Purpose
RedBoot compressed-image loader for Xtensa. It relocates itself, clears BSS, allocates stack/heap, decompresses the embedded gzip kernel into its destination, flushes/invalidate caches, and jumps to the uncompressed kernel.

## Important APIs, Types, And Functions
Important labels and symbols are `__start`, `__start_a0`, `_start`, `_reloc`, `avail_ram`, `end_avail`, `_stack`, `_heap`, and `complen`. It calls external `gunzip` when available and uses cache macros from `cacheasm.h`.

## Control Flow
Entry resets PS/window state, computes the runtime load address, copies the loader to its linked address, flushes writeback dcache and invalidates icache, jumps to `_reloc`, clears BSS, aligns stack, computes the compressed image source from the embedded `image` section, initializes gzip length, and calls `gunzip`. If `gunzip` is not linked it falls back to raw copy. It then flushes/invalidate caches again, restores the boot argument register in call0 ABI, and jumps to `_image_start`.

## State And Persistence
State is loader BSS, stack, heap allocator bounds for zlib, compressed length, and CPU cache state. No durable persistence.

## Dependencies And Integration Points
Depends on Xtensa ABI macros, RedBoot load convention, boot linker script symbols, zlib boot library, cache operation macros, and kernel entry conventions.

## Risks And Edge Cases
Self-relocation assumes limited overlap and that the kernel image is out of the way. Heap size must fit zlib workspace. Cache flush/invalidate is mandatory before executing relocated/decompressed code. ABI register preservation differs between windowed and call0.

## Test Signals
Boot compressed images with windowed and call0 ABI, verify decompression length, run on writeback and non-writeback cache variants, and test failure handling for oversized images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/bootstrap.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/dts/Makefile

## Purpose
Builds Xtensa device-tree blobs for configurations that use Open Firmware flattened device trees.

## Important APIs, Types, And Functions
Defines `dtb-$(CONFIG_OF) += $(addsuffix .dtb, $(CONFIG_BUILTIN_DTB_NAME))` and `dtb-` for `CONFIG_OF_ALL_DTBS` wildcard coverage.

## Control Flow
When OF is enabled, the configured built-in DTB name is converted to a `.dtb` target. The wildcard `dtb-` list supports all-DTB test builds without selecting a specific built-in DTB.

## State And Persistence
No runtime state. Build output is DTB artifacts.

## Dependencies And Integration Points
Depends on `CONFIG_OF`, `CONFIG_BUILTIN_DTB_NAME`, DTS files in the directory, and generic dtc rules.

## Risks And Edge Cases
An empty or wrong built-in DTB name yields missing DTB artifacts. Wildcard coverage only sees local `.dts` files.

## Test Signals
Build with `CONFIG_USE_OF=y` and a real built-in DTB name, and run all-DTB build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/Makefile

## Purpose
Builds the minimal decompression library used by Xtensa compressed boot images.

## Important APIs, Types, And Functions
Key variables are `zlib := inffast.c inflate.c inftrees.c`, `lib-y`, `ccflags-y`, instrumentation disable flags, stack-protector removal flags, and `cmd_copy_zlib`.

## Control Flow
Kbuild copies selected zlib inflate sources from `lib/zlib_inflate`, builds them plus `zmem.o` into `arch/xtensa/boot/lib/lib.a`, removes function tracing and sanitizers, and disables stack protector for these early-boot objects.

## State And Persistence
Build output is a boot-only static archive and copied zlib source files in the object tree.

## Dependencies And Integration Points
Depends on generic zlib inflate sources, `zmem.c`, the boot-redboot linker, and early boot constraints where normal kernel instrumentation is unavailable.

## Risks And Edge Cases
Instrumentation or stack protector would introduce unavailable runtime dependencies. Zlib source copy rules must track upstream filenames. The library assumes the boot loader supplies heap bounds.

## Test Signals
Build `zImage`, inspect that sanitizer/ftrace/stack-protector instrumentation is absent, and boot a compressed image through decompression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/zmem.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/zmem.c

## Purpose
Provides a tiny gzip decompressor wrapper and bump allocator for Xtensa compressed boot images.

## Important APIs, Types, And Functions
Exports `gunzip(void *dst, int dstlen, unsigned char *src, int *lenp)`. Internal helpers and state are external `avail_ram`/`end_avail`, `exit`, `zalloc`, gzip flag constants, and zlib `z_stream`.

## Control Flow
`gunzip` parses the gzip header, rejects non-deflate or reserved flags, skips optional extra/name/comment/header-CRC fields, allocates zlib workspace with `zalloc`, initializes raw inflate with `zlib_inflateInit2(..., -MAX_WBITS)`, inflates into the destination buffer, stores output length back through `lenp`, and ends the stream. Error paths spin forever in `exit`.

## State And Persistence
State is the boot heap pointer `avail_ram`, bounded by `end_avail`, and temporary zlib stream state. No persistence after kernel jump.

## Dependencies And Integration Points
Depends on boot-redboot `avail_ram`/`end_avail` symbols, zlib inflate sources, and the compressed bootstrap's call convention.

## Risks And Edge Cases
There is no recovery or console output on malformed input or heap exhaustion. Header parsing trusts NUL terminators within `lenp` bounds only after optional scans. Destination size is fixed by caller.

## Test Signals
Boot valid gzip images, test malformed gzip headers under emulator, verify heap sizing against `zlib_inflate_workspacesize`, and compare decompressed bytes to `vmlinux.bin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/lib/zmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/Kbuild

## Purpose
Declares generated and generic asm headers for Xtensa.

## Important APIs, Types, And Functions
Generates `syscall_table.h` and maps generic headers for `extable.h`, `kvm_para.h`, `mcs_spinlock.h`, `parport.h`, `qrwlock.h`, `qspinlock.h`, `user.h`, and `text-patching.h`.

## Control Flow
Kbuild installs or generates these headers during `headers_install` and internal arch header preparation, using generic implementations where Xtensa has no custom header.

## State And Persistence
Persistent build outputs are generated header files. No runtime state.

## Dependencies And Integration Points
Integrates Xtensa with generic spinlock, extable, parport, KVM paravirt, user, and text patching header contracts.

## Risks And Edge Cases
If Xtensa later needs custom behavior, leaving a generic mapping may hide missing architecture semantics. Missing syscall table generation breaks syscall dispatch builds.

## Test Signals
Run `make archheaders`, headers install, and normal Xtensa builds using qspinlock/qrwlock and syscall table users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-offsets.h

## Purpose
Thin include wrapper exposing generated assembly offsets to Xtensa assembly headers.

## Important APIs, Types, And Functions
Includes `<generated/asm-offsets.h>`.

## Control Flow
At compile time, assembly sources include this file to consume constants generated from C structure layouts.

## State And Persistence
No runtime state. Persistent build artifact is the generated offsets header.

## Dependencies And Integration Points
Depends on the kernel's asm-offset generation step and is used by assembly macros such as user access and current-task lookup.

## Risks And Edge Cases
Build ordering must ensure generated offsets exist before assembly preprocessing. Stale offsets would corrupt low-level structure access.

## Test Signals
Clean Xtensa builds and changes to thread/task structures that regenerate offsets successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-prototypes.h

## Purpose
Provides C prototypes for functions referenced from assembly or generated by compiler helper calls so modversions and symbol checking can see them.

## Important APIs, Types, And Functions
Includes architecture headers for cacheflush, checksum, ftrace, page, string, and uaccess, then declares helper functions such as `__ashrdi3`, `__ashldi3`, `__bswapdi2`, `__bswapsi2`, `__lshrdi3`, `__divsi3`, `__modsi3`, `__mulsi3`, `__udivsi3`, `__umodsi3`, and `__umulsidi3`.

## Control Flow
No runtime control flow. The header informs builds about callable symbols.

## State And Persistence
No state. It affects symbol metadata and compile/link validation.

## Dependencies And Integration Points
Depends on Xtensa libgcc-style helpers and generic asm prototype infrastructure.

## Risks And Edge Cases
Prototype mismatches can break module CRCs or cause ABI mismatches between assembly/lib routines and C callers.

## Test Signals
Build modules with `CONFIG_MODVERSIONS`, compile code that triggers 64-bit math helpers, and link architecture library symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-uaccess.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-uaccess.h

## Purpose
Defines assembly macros for validating user-space memory access ranges on Xtensa.

## Important APIs, Types, And Functions
Macros are `user_ok aa, as, at, error` and `access_ok aa, as, at, sp, error`.

## Control Flow
`user_ok` compares the requested size against `TASK_SIZE`, subtracts size from the task limit, and branches to the supplied error label if the range is too large or starts beyond the last valid address. `access_ok` currently wraps `user_ok` and falls through on success.

## State And Persistence
No persistent state. It only uses registers supplied by assembly callers.

## Dependencies And Integration Points
Depends on `TASK_SIZE`, generated offsets, current/thread headers, and assembly uaccess routines that use exception tables.

## Risks And Edge Cases
Range arithmetic must avoid overflow and preserve documented registers. The macro is optimized for fall-through success; callers must provide correct error labels and scratch registers.

## Test Signals
Run uaccess selftests, fault-injection tests for boundary addresses near `TASK_SIZE`, and build assembly callers with both MMU/noMMU layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asmmacro.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asmmacro.h

## Purpose
Provides common Xtensa assembly macros for loops, exception-table annotations, unaligned word extraction, bit-scan/absolute-value fallbacks, ABI-neutral call/argument names, and exception-text section placement.

## Important APIs, Types, And Functions
Key macros include `__loopi`, `__loops`, `__loopt`, `__loop`, `__endl`, `__endla`, `EX`, `__src_b`, `__ssa8`, `do_nsau`, `do_abs`, `abi_entry`, `abi_ret`, `abi_call`, `abi_callx`, `abi_arg*`, `abi_saved*`, `KABI_*`, `UABI_*`, and `__XTENSA_HANDLER`.

## Control Flow
Loop macros choose zero-overhead `loop` instructions when available and branch-based loops otherwise. ABI macros map the same assembly source to windowed or call0 register conventions. `EX` emits exception-table entries for faultable instructions.

## State And Persistence
No runtime data is owned; macros shape generated assembly and exception table contents.

## Dependencies And Integration Points
Depends on Xtensa core feature macros and is used across low-level string, cache, boot, trap, and syscall assembly.

## Risks And Edge Cases
ABI register mappings must match compiler flags. Loop fallbacks must preserve end labels and scratch registers. Endianness-sensitive unaligned extraction must match memory layout. Exception-table entries must reference the right faulting label.

## Test Signals
Build both windowed and call0 kernels, run string/uaccess/cache routines, verify exception fixups, and test cores with and without zero-overhead loops, NSA, and ABS instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asmmacro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/atomic.h

## Purpose
Implements Xtensa 32-bit atomic integer operations used by the generic atomic API.

## Important APIs, Types, And Functions
Defines `arch_atomic_read`, `arch_atomic_set`, and generated `arch_atomic_add/sub/and/or/xor`, return variants for add/sub, and fetch variants. Implementations select `l32ex/s32ex`, `s32c1i`, or interrupt-level critical sections depending on core features.

## Control Flow
For exclusive-load cores, operations loop on `l32ex`, compute, `s32ex`, and `getex` until success. For `s32c1i`, they set `scompare1`, attempt conditional store, and retry on mismatch. For older cores, they raise interrupt level to `TOPLEVEL`, perform load/modify/store, restore PS, and `rsync`.

## State And Persistence
Only modifies target `atomic_t` values and CPU special registers transiently. No durable state.

## Dependencies And Integration Points
Depends on Xtensa core feature macros, barriers, cmpxchg, processor interrupt levels, and the generic atomic wrapper layer.

## Risks And Edge Cases
The interrupt-disabled fallback uses `a14` to avoid window overflow hazards and must not be interrupted by register-window traps. Memory clobbers and barriers must satisfy SMP semantics. S32C1I behavior depends on AtomCtl/cache configuration.

## Test Signals
Run atomic and locking selftests on exclusive, S32C1I, and fallback cores; stress SMP counters, qspinlocks, refcounts, and KCSAN/lockdep builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/barrier.h

## Purpose
Defines Xtensa memory barrier primitives and connects them to generic barrier APIs.

## Important APIs, Types, And Functions
Defines `__mb()` as `memw`, `__rmb()` as compiler `barrier()`, `__wmb()` as `__mb()`, SMP barrier aliases, and atomic barrier hooks for S32C1I cores.

## Control Flow
No runtime control beyond inline assembly barriers. On SMP, generic macros use these definitions for inter-CPU ordering.

## State And Persistence
No state. It enforces ordering of memory operations.

## Dependencies And Integration Points
Depends on Xtensa `memw` semantics, core feature macros, and `asm-generic/barrier.h`.

## Risks And Edge Cases
Using compiler-only read barriers assumes Xtensa read ordering is sufficient. Atomic barrier hooks for S32C1I are compiler barriers, so cache/AtomCtl behavior must make atomic ordering correct.

## Test Signals
Run LKMM litmus-style tests where possible, SMP stress tests, lock/atomic tests, and driver DMA ordering tests on real Xtensa SMP hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bitops.h

## Purpose
Provides Xtensa bit operations, including optimized find-first/last bit support when the NSA instruction exists, plus generic non-atomic and little-endian helpers.

## Important APIs, Types, And Functions
Important definitions include `__cntlz`, `ffz`, `__ffs`, `fls`, `fls64`, architecture find-bit macros, and includes for generic bitops variants.

## Control Flow
Feature-dependent inline functions use `nsau` for count-leading-zero operations when present; otherwise generic helpers provide portable behavior. Atomic bit operations are mostly delegated through generic or other architecture primitives.

## State And Persistence
No persistent state; functions inspect integer words or bitmaps.

## Dependencies And Integration Points
Depends on `<linux/bitops.h>` include discipline, Xtensa core features, byteorder, barriers, and generic bitops headers.

## Risks And Edge Cases
Incorrect endianness or bit numbering would break filesystem, scheduler, and memory-management bitmaps. `ffz` is undefined for all-ones input, matching generic expectations.

## Test Signals
Build with and without `XCHAL_HAVE_NSA`, run bitmap/bitops selftests, and stress page allocator, cpumasks, and filesystem bitmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bootparam.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bootparam.h

## Purpose
Defines the Xtensa boot parameter tag format passed from boot loaders to the kernel.

## Important APIs, Types, And Functions
Key items are bootparam tag constants such as `BP_TAG_FIRST`, `BP_TAG_LAST`, `BP_TAG_COMMAND_LINE`, `BP_TAG_INITRD`, `BP_TAG_MEMORY`, `BP_TAG_SERIAL_BAUDRATE`, `BP_TAG_SERIAL_PORT`, `BP_TAG_FDT`, `BP_VERSION`, and structures for typed tag payloads.

## Control Flow
The header has no executable flow. Boot loaders and early kernel parsers use the tag IDs and struct layouts to walk a parameter list.

## State And Persistence
State is the boot-time parameter block in memory. It does not persist after early boot except through parsed kernel globals.

## Dependencies And Integration Points
Used by `boot-elf/bootstrap.S`, platform boot code, command-line/initrd/memory/FDT parsing, and user-provided boot loaders.

## Risks And Edge Cases
Tag size/alignment mismatches break parser traversal. Boot loaders must terminate with `BP_TAG_LAST`. Version drift can cause ignored or misread parameters.

## Test Signals
Boot with command line, initrd, memory, serial, and FDT tags; test malformed/short tag lists and no-bootparam configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bootparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cache.h

## Purpose
Defines Xtensa cache geometry constants and cache-alignment attributes used across memory management and DMA code.

## Important APIs, Types, And Functions
Key macros are `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `SMP_CACHE_BYTES`, `DCACHE_WAY_SIZE`, `ICACHE_WAY_SIZE`, `DCACHE_WAY_SHIFT`, `ICACHE_WAY_SHIFT`, `ARCH_DMA_MINALIGN`, and Xtensa's `__ro_after_init` mapping.

## Control Flow
No executable flow; constants are computed from variant `XCHAL_*` core definitions.

## State And Persistence
No state. It affects structure alignment, cache flush ranges, page coloring, and DMA buffer alignment.

## Dependencies And Integration Points
Depends on `asm/core.h` and variant cache geometry. Used by `page.h`, `cacheflush.h`, DMA, highmem, and allocator alignment logic.

## Risks And Edge Cases
Wrong cache line or way-size values cause aliasing bugs, data corruption, or inefficient flushing. `ARCH_DMA_MINALIGN` must be large enough for noncoherent DMA.

## Test Signals
Compile against multiple variants, run cache aliasing tests, DMA tests, and highmem/page-coloring paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheasm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheasm.h

## Purpose
Defines assembly macros for Xtensa cache maintenance: invalidate, flush, and flush-invalidate operations over all cache, pages, or address ranges.

## Important APIs, Types, And Functions
Macros include low-level variants such as `___invalidate_icache_all`, `___invalidate_dcache_all`, `___flush_dcache_all`, `___flush_invalidate_dcache_all`, page/range operations, and feature-conditional cache instruction sequences.

## Control Flow
Macros expand to loops over cache ways/sets or address ranges using Xtensa cache instructions selected by core cache features. They often rely on loop helpers from `asmmacro.h` and are used before executing relocated code or after modifying memory visible to instruction fetch.

## State And Persistence
They mutate CPU cache state only. No persistent software state is owned.

## Dependencies And Integration Points
Depends on variant cache geometry, Xtensa cache instruction availability, and assembly users in boot, cacheflush implementation, and low-level memory code.

## Risks And Edge Cases
Wrong way/set iteration or missing `isync`/ordering can execute stale code or lose dirty data. Writeback versus non-writeback cache variants require different behavior. Range alignment must cover entire cache lines.

## Test Signals
Boot compressed images, run self-modifying/ftrace/module code paths, execute cache aliasing tests, and test variants with writeback and non-writeback caches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheflush.h

## Purpose
Declares and maps Xtensa cache flush APIs required by Linux MM, DMA, highmem, vmalloc, user-page copying, and instruction-cache coherency.

## Important APIs, Types, And Functions
Declares low-level functions like `__invalidate_*`, `__flush_*`, alias flush helpers, SMP/non-SMP `flush_cache_all`, `flush_cache_range`, `flush_icache_range`, `flush_cache_page`, `flush_dcache_folio`, `flush_dcache_page`, `copy_to_user_page`, and `copy_from_user_page`.

## Control Flow
Preprocessor feature checks choose real externs or inline no-ops depending on writeback caches, MMU, aliasing way size, and SMP. Generic cacheflush hooks are included after Xtensa-specific definitions.

## State And Persistence
No software state; functions mutate data and instruction caches and sometimes alias mappings.

## Dependencies And Integration Points
Depends on cache geometry, MMU state, page and folio types, SMP broadcast implementations, and generic cacheflush contracts.

## Risks And Edge Cases
VIPT aliasing when way size exceeds page size is the main hazard. Missing icache invalidation after user or module writes causes stale instruction execution. SMP requires cross-CPU coherency where local-only macros are insufficient.

## Test Signals
Run module loading, ftrace/kprobes, `mprotect` executable transitions, highmem user-page copy, page-cache writeback, and cache alias stress tests on SMP and UP variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cachetype.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cachetype.h

## Purpose
Minimal cache-type header for Xtensa.

## Important APIs, Types, And Functions
This file only provides the include guard and does not define runtime APIs.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Exists to satisfy generic code that includes `<asm/cachetype.h>`.

## Risks And Edge Cases
If generic code starts requiring cache-type queries, this empty header may need real definitions.

## Test Signals
Compile coverage for generic code including cache-type headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cachetype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/checksum.h

## Purpose
Implements Xtensa IP/TCP/UDP checksum helpers, including copy-and-checksum hooks for networking and user access.

## Important APIs, Types, And Functions
Defines or declares `csum_partial`, `csum_partial_copy_nocheck`, `csum_partial_copy_from_user`, `csum_fold`, `ip_fast_csum`, `csum_tcpudp_nofold`, `csum_tcpudp_magic`, `ip_compute_csum`, `csum_ipv6_magic`, and `csum_and_copy_to_user`.

## Control Flow
Inline assembly folds carries, handles endianness-specific pseudo-header layout, uses loop instructions when available for IP header checksum, and delegates bulk partial checksum routines to architecture implementations or generic wrappers.

## State And Persistence
No persistent state; routines compute checksums and may copy to/from user buffers with fault handling in callees.

## Dependencies And Integration Points
Depends on Linux networking checksum types, uaccess, Xtensa core loop features, and generic network stack checksum contracts.

## Risks And Edge Cases
Carry folding, odd lengths, endian-specific pseudo-header addition, user-copy faults, and IPv6 length/protocol accumulation are correctness-sensitive. Bad checksums cause silent network data loss.

## Test Signals
Run network checksum selftests, IPv4/IPv6 TCP/UDP traffic, odd-length payloads, checksum offload fallback paths, and user-copy fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cmpxchg.h

## Purpose
Implements Xtensa compare-exchange and exchange primitives for the generic atomic and locking APIs.

## Important APIs, Types, And Functions
Key functions/macros are `__cmpxchg_u32`, `arch_cmpxchg`, `arch_cmpxchg_local`, `arch_cmpxchg64_local`, `arch_cmpxchg64`, `xchg_u32`, `xchg_small`, `__arch_xchg`, and `arch_xchg`.

## Control Flow
For exclusive cores, compare/exchange loops use `l32ex/s32ex/getex`. For S32C1I cores they use `scompare1` and `s32c1i`. Fallback paths disable interrupts to `TOPLEVEL`. Small 1/2-byte exchanges update the containing word with a cmpxchg loop and endian-aware bit offsets.

## State And Persistence
Only target memory words and transient CPU special registers are modified.

## Dependencies And Integration Points
Depends on core feature macros, interrupt levels, generic cmpxchg-local helpers, and `READ_ONCE`.

## Risks And Edge Cases
S32C1I atomicity depends on AtomCtl/cache setup. Small exchange bit masks must match endianness. 64-bit cmpxchg is local/generic rather than truly inter-CPU atomic, so callers must respect API semantics.

## Test Signals
Run atomic/locking/futex selftests, stress byte and halfword xchg users, and test variants with exclusive, S32C1I, and interrupt-disabled fallback implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/coprocessor.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/coprocessor.h

## Purpose
Defines Xtensa optional register and coprocessor save-area types plus assembly macros for saving/restoring configured TIE/coprocessor state.

## Important APIs, Types, And Functions
Important macros include `XTENSA_HAVE_COPROCESSOR`, `XTENSA_HAVE_COPROCESSORS`, `XTENSA_HAVE_IO_PORT`, `save_xtregs_opt`, `load_xtregs_opt`, `save_xtregs_user`, and `load_xtregs_user`. Types include `xtregs_opt_t`, `xtregs_user_t`, `xtregs_cp0_t` through `xtregs_cp7_t`. Functions include `coprocessor_flush`, `coprocessor_release_all`, `coprocessor_flush_all`, `coprocessor_flush_release_all`, and `local_coprocessors_flush_release_all`.

## Control Flow
The header expands variant-provided `XCHAL_*_SA_LIST` macros into aligned C structs and assembly save/load sequences. Coprocessor management code uses the declared functions to lazily save, flush, or release per-thread coprocessor state.

## State And Persistence
State is per-thread optional/coprocessor register save areas. Hardware CPENABLE and coprocessor registers are managed elsewhere.

## Dependencies And Integration Points
Depends on variant `tie.h` and `tie-asm.h`, Xtensa core definitions, thread-info code, ptrace/ELF core dumps, and context-switch code.

## Risks And Edge Cases
Variant save-area metadata must be exact; wrong sizes/alignments corrupt task state or core dumps. Assembly and C struct generation must stay consistent.

## Test Signals
Run context-switch, signal, ptrace, and core-dump tests on variants with optional registers and coprocessors; verify lazy coprocessor flush/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/coprocessor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/core.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/core.h

## Purpose
Normalizes Xtensa variant core feature macros and derives ABI/support constants used throughout architecture code.

## Important APIs, Types, And Functions
Defines defaults for `XCHAL_HAVE_DIV32`, `XCHAL_HAVE_EXCLUSIVE`, `XCHAL_HAVE_EXTERN_REGS`, `XCHAL_HAVE_MPU`, `XCHAL_HAVE_VECBASE`, `XCHAL_SPANNING_WAY`, `XCHAL_HAVE_TRAX`, and `XCHAL_NUM_PERF_COUNTERS`; derives `USER_SUPPORT_WINDOWED`, `SUPPORT_WINDOWED`, `XTENSA_STACK_ALIGNMENT`, and `XCHAL_HW_MIN_VERSION`.

## Control Flow
No executable control; preprocessor logic converts variant capabilities and Kconfig ABI choices into common macros.

## State And Persistence
No runtime state. Constants persist in compiled code.

## Dependencies And Integration Points
Depends on `<variant/core.h>` and is included by most Xtensa low-level headers.

## Risks And Edge Cases
Incorrect defaults can silently compile unsupported code paths. ABI support macros must match Kconfig and compiler ABI. Stack alignment must satisfy Xtensa ABI and data width.

## Test Signals
Compile many variant headers, especially custom variants lacking newer `XCHAL_*` definitions, and boot both windowed and call0 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/current.h

## Purpose
Defines how Xtensa obtains the current task pointer in C and assembly.

## Important APIs, Types, And Functions
Provides `get_current()`, `current`, `current_stack_pointer` bound to register `a1`, and assembly macro `GET_CURRENT(reg, sp)`.

## Control Flow
C callers obtain `current_thread_info()->task`. Assembly callers derive thread info from the stack pointer via `GET_THREAD_INFO` and load `TI_TASK`.

## State And Persistence
No owned state; reads stack/thread-info state maintained by scheduler and entry code.

## Dependencies And Integration Points
Depends on `thread_info.h`, generated thread-info offsets, and Xtensa stack pointer register conventions.

## Risks And Edge Cases
Stack alignment and thread-info placement must match `GET_THREAD_INFO`. Binding `current_stack_pointer` to `a1` relies on compiler/register ABI correctness.

## Test Signals
Scheduler/context-switch tests, assembly exception-entry tests, and compile coverage for C and assembly users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/delay.h

## Purpose
Provides busy-wait delay primitives for Xtensa using simple instruction loops and the cycle counter.

## Important APIs, Types, And Functions
Defines `__delay`, `__udelay`, `udelay`, `__ndelay`, `ndelay`, `__bad_udelay`, `__bad_ndelay`, and uses `loops_per_jiffy`, `get_ccount`, and `ccount_freq`.

## Control Flow
`__delay` emits a nop for tiny constant delays or decrements by two cycles per loop. `__udelay` computes cycle count from microseconds and spins on `ccount` with wraparound-safe subtraction. `__ndelay` scales nanoseconds to cycles and delegates to `__delay`. Compile-time too-large constants call undefined symbols to trigger build errors.

## State And Persistence
No persistent state; reads the cycle counter and clock frequency.

## Dependencies And Integration Points
Depends on Xtensa timer/cycle-counter setup and generic delay API users.

## Risks And Edge Cases
Correctness depends on calibrated `ccount_freq`, wraparound arithmetic, and interrupt/preemption effects. Large delay constants intentionally fail at link time.

## Test Signals
Timer calibration tests, driver delay smoke tests, and measurements of udelay/ndelay accuracy across CPU frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/dma.h

## Purpose
Provides legacy DMA constants and declarations for Xtensa, mainly for generic driver compatibility.

## Important APIs, Types, And Functions
Defines `MAX_DMA_CHANNELS`, `MAX_DMA_ADDRESS`, and declares `request_dma` and `free_dma`.

## Control Flow
No inline runtime flow; platform or generic code supplies channel allocation behavior.

## State And Persistence
No owned state. DMA channel state is managed by implementations elsewhere.

## Dependencies And Integration Points
Depends on `asm/io.h`, page/memory layout, and legacy drivers that still probe ISA/PC-style DMA APIs.

## Risks And Edge Cases
`MAX_DMA_ADDRESS` is platform-sensitive and assumes DMA can target the statically mapped kernel segment. Incorrect value causes bad bounce-buffer decisions or inaccessible DMA memory.

## Test Signals
Build legacy DMA users, run DMA-capable platform tests, and verify `MAX_DMA_ADDRESS` against board memory maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/elf.h

## Purpose
Defines Xtensa ELF ABI constants, relocation IDs, register-set types, binary compatibility checks, process startup register initialization, FDPIC handling, and core-dump optional register layout.

## Important APIs, Types, And Functions
Key definitions include `EM_XTENSA_OLD`, `R_XTENSA_*`, `elf_greg_t`, `xtensa_gregset_t`, `ELF_NGREG`, `elf_check_arch`, `elf_check_fdpic`, `ELF_DATA`, `ELF_CLASS`, `ELF_ARCH`, `ELF_ET_DYN_BASE`, `ELF_PLAT_INIT`, `ELF_FDPIC_PLAT_INIT`, `elf_xtregs_t`, and `SET_PERSONALITY`.

## Control Flow
Exec-time macros validate architecture and initialize user registers. Core-dump code uses register-set typedefs and optional/coprocessor state aggregates. Endianness selects ELF data encoding.

## State And Persistence
State is user register initialization at exec and data emitted into ELF core files. No filesystem persistence except generated core dumps.

## Dependencies And Integration Points
Depends on ptrace registers, coprocessor save-area types, Linux ELF loader, FDPIC loader, and personality handling.

## Risks And Edge Cases
Register clearing must preserve stack pointer while avoiding stale state. FDPIC register conventions must match userspace ABI. Optional register core layout must match coprocessor definitions.

## Test Signals
Run ELF exec tests, dynamic loader tests, FDPIC if supported, core dumps with optional registers, ptrace register-set tests, and big/little endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/fixmap.h

## Purpose
Defines Xtensa fixed virtual mapping slots for highmem temporary mappings.

## Important APIs, Types, And Functions
Under `CONFIG_HIGHMEM`, defines `enum fixed_addresses` with `FIX_KMAP_BEGIN` and `FIX_KMAP_END`, plus `FIXADDR_END`, `FIXADDR_SIZE`, `FIXADDR_START`, and `FIXADDR_TOP`.

## Control Flow
No runtime flow. The preprocessor sizes fixed mapping space using `KM_MAX_IDX`, `NR_CPUS`, and `DCACHE_N_COLORS`, then includes generic fixmap support.

## State And Persistence
Controls virtual address layout for kmap local/atomic mappings. Runtime PTE state is managed elsewhere.

## Dependencies And Integration Points
Depends on highmem, page tables, cache coloring, and generic fixmap APIs.

## Risks And Edge Cases
Address layout must be PMD-aligned to handle cache aliasing. Incorrect slot count breaks highmem mappings on SMP or colored-cache systems.

## Test Signals
Build and boot highmem configurations, stress kmap local/atomic users, and run highmem filesystem/page-cache workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/flat.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/flat.h

## Purpose
Provides FLAT binary relocation access helpers for noMMU Xtensa.

## Important APIs, Types, And Functions
Defines `flat_get_addr_from_rp` and `flat_put_addr_at_rp`.

## Control Flow
The helpers use unaligned loads/stores to read or write 32-bit relocation addresses at the relocation pointer and return success.

## State And Persistence
State is the relocated binary image in memory. No durable persistence.

## Dependencies And Integration Points
Depends on `linux/unaligned.h` and the generic binfmt_flat loader.

## Risks And Edge Cases
The helpers ignore `relval` and flags, which is correct only for this FLAT relocation format. User pointer casts are forced and rely on loader-controlled memory.

## Test Signals
Run noMMU FLAT binary load/relocation tests, including unaligned relocation pointer cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/flat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/ftrace.h

## Purpose
Defines Xtensa ftrace entry metadata and return-address hook.

## Important APIs, Types, And Functions
Declares `return_address`, defines `ftrace_return_address(n)`, and under `CONFIG_FUNCTION_TRACER` defines `MCOUNT_ADDR`, `MCOUNT_INSN_SIZE`, `_mcount`, and `mcount`.

## Control Flow
No runtime flow in the header; ftrace code patches or calls `_mcount` based on the declared instruction size and symbol address.

## State And Persistence
No owned state. Ftrace runtime state is managed by tracing core.

## Dependencies And Integration Points
Depends on Xtensa processor conventions, function tracer implementation, and return-address unwinding support.

## Risks And Edge Cases
`MCOUNT_INSN_SIZE` must match the actual call instruction size. Return address depth handling must match windowed/call0 ABI stack frames.

## Test Signals
Build with function tracer, enable ftrace function graph/function tracing, and verify return addresses for nested calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/futex.h

## Purpose
Implements Xtensa futex atomic operations on user memory, including atomic op and cmpxchg primitives with exception-table based fault handling.

## Important APIs, Types, And Functions
Defines `arch_futex_atomic_op_inuser`, `futex_atomic_cmpxchg_inatomic`, and internal `__futex_atomic_op` for exclusive or S32C1I cores.

## Control Flow
Operations first validate `access_ok`. On capable cores, inline assembly performs atomic load/modify/store loops over user memory and routes faults through `.fixup` and `__ex_table` entries to return `-EFAULT`. Unsupported atomic hardware falls back to generic local futex helpers.

## State And Persistence
Mutates user futex words and returns old values. No kernel persistent state.

## Dependencies And Integration Points
Depends on uaccess, futex generic code, Xtensa atomic instructions, exception tables, and user memory fault handling.

## Risks And Edge Cases
Fault fixups must cover every faultable load/store. S32C1I and exclusive loops must not corrupt `uval` on failed compare. Fallback local operations may not be suitable for SMP hardware lacking atomic instructions.

## Test Signals
Run futex selftests, pthread mutex/condvar stress, userfault/fault-injection around futex pages, and SMP contention tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/highmem.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/highmem.h

## Purpose
Defines highmem permanent and local mapping layout for Xtensa, including cache-color aware pkmap allocation.

## Important APIs, Types, And Functions
Key macros and functions are `PKMAP_BASE`, `LAST_PKMAP`, `PKMAP_NR`, `PKMAP_ADDR`, `kmap_prot`, `get_pkmap_color`, `get_next_pkmap_nr`, `no_more_pkmaps`, `get_pkmap_entries_count`, `get_pkmap_wait_queue_head`, `kmap_local_map_idx`, `kmap_local_unmap_idx`, `pkmap_page_table`, `flush_cache_kmaps`, `arch_kmap_local_post_unmap`, and `kmap_init`.

## Control Flow
For aliasing caches, pkmap allocation advances per-color indexes so virtual mappings match data-cache color. Local mapping index helpers select color-aware fixmap slots. Unmap flushes the kernel TLB range for the page.

## State And Persistence
Runtime state includes pkmap page tables, per-color last index arrays, and per-color wait queues declared elsewhere.

## Dependencies And Integration Points
Depends on highmem, cache aliasing constants, fixmap slots, TLB flush, and generic kmap code.

## Risks And Edge Cases
Wrong coloring can produce D-cache aliases. Slot exhaustion and wait queues must be per-color. Local unmap TLB flushing is required to avoid stale temporary mappings.

## Test Signals
Run highmem stress, kmap local nesting tests, page-cache I/O above lowmem, and cache alias workloads on highmem-capable Xtensa.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/hw_breakpoint.h

## Purpose
Declares Xtensa hardware breakpoint/watchpoint support for perf and ptrace.

## Important APIs, Types, And Functions
Defines breakpoint types `XTENSA_BREAKPOINT_EXECUTE`, `XTENSA_BREAKPOINT_LOAD`, and `XTENSA_BREAKPOINT_STORE`; `struct arch_hw_breakpoint`; and functions including `hw_breakpoint_slots`, `arch_check_bp_in_kernelspace`, `hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `hw_breakpoint_pmu_read`, `check_hw_breakpoint`, `clear_ptrace_hw_breakpoint`, and `restore_dbreak`.

## Control Flow
When `CONFIG_HAVE_HW_BREAKPOINT` is enabled, perf/ptrace code uses these declarations to parse, install, handle, and remove debug registers. Otherwise `clear_ptrace_hw_breakpoint` is a no-op stub.

## State And Persistence
State is hardware debug register programming and per-task breakpoint metadata managed elsewhere.

## Dependencies And Integration Points
Depends on perf events, ptrace, notifier chains, and Xtensa debug/breakpoint exception handling.

## Risks And Edge Cases
Breakpoint length/type parsing must match hardware capabilities. Kernel-space checks protect against invalid user breakpoints. Restore paths must reprogram debug registers after context switches.

## Test Signals
Run perf breakpoint tests, ptrace hardware watchpoint tests, kernel/user address rejection tests, and context-switch restore tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/initialize_mmu.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/initialize_mmu.h

## Purpose
Provides assembly macros to initialize Xtensa MMU/cache attributes before or during early kernel startup, including MMUv3 spanning-way remapping and noMMU cache-attribute setup.

## Important APIs, Types, And Functions
Defines `CA_BYPASS`, `CA_WRITEBACK`, `initialize_mmu`, and `initialize_cacheattr`.

## Control Flow
`initialize_mmu` optionally initializes `atomctl` for S32C1I/cache behavior, then for MMUv3 with PTP MMU and spanning way creates a temporary mapping, jumps through it, invalidates old TLB mappings, programs ITLB/DTLB configuration, installs cached and bypass KSEG mappings, optional 512M second mappings, KIO mappings, jumps to final mapping, removes the temporary mapping, and clears `ptevaddr`. `initialize_cacheattr` programs MPU or TLB cache attributes for noMMU/TLB systems from `CONFIG_MEMMAP_CACHEATTR`.

## State And Persistence
It mutates hardware TLB, MPU/cache attribute, AtomCtl, and processor state. These mappings persist into early kernel execution.

## Dependencies And Integration Points
Depends on Kconfig memory layout, page attribute bits, variant MMU features, vector relocation support, and boot/head assembly.

## Risks And Edge Cases
MMUv3 requires relocatable vectors. Temporary mapping address must not collide with the kernel load address. KSEG physical address alignment is critical. Wrong cache attributes can break atomics, instruction fetch, or device access.

## Test Signals
Boot MMUv2/MMUv3, 128M/256M/512M KSEG, noMMU MPU/TLB cacheattr configurations, S32C1I atomics, and XIP/non-XIP layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/initialize_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/io.h

## Purpose
Defines Xtensa I/O address mapping constants and MMU-aware `ioremap` shortcuts for statically mapped KIO regions.

## Important APIs, Types, And Functions
Defines `IOADDR`, `IO_SPACE_LIMIT`, `PCI_IOBASE`, `ioremap_prot`, `ioremap`, and `ioremap_cache`, then includes generic I/O accessors.

## Control Flow
On MMU builds, `ioremap` and `ioremap_cache` return direct KIO bypass/cached virtual addresses when the physical address falls inside `XCHAL_KIO_PADDR..+XCHAL_KIO_SIZE`; otherwise they call `ioremap_prot` with noncached or cached protection.

## State And Persistence
State is vmalloc/ioremap mappings managed by the MM subsystem. Direct KIO translations are fixed by MMU initialization.

## Dependencies And Integration Points
Depends on byteorder, page and KIO layout, pgtable protections, generic I/O helpers, PCI, and device drivers.

## Risks And Edge Cases
KIO physical base can be device-tree derived on some configurations, so early users must see initialized `xtensa_kio_paddr`. Cached mapping of device memory is unsafe unless the caller explicitly asks for it.

## Test Signals
Probe MMIO drivers in KIO and non-KIO ranges, PCI I/O access, `ioremap_cache` users, and OF-derived KIO base configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irq.h

## Purpose
Defines Xtensa IRQ numbering constants and declares IRQ-domain mapping helpers.

## Important APIs, Types, And Functions
Defines `PLATFORM_NR_IRQS`, `XTENSA_NR_IRQS`, `NR_IRQS`, `XTENSA_PIC_LINUX_IRQ`, `irq_canonicalize`, and declares `migrate_irqs`, `xtensa_irq_domain_xlate`, `xtensa_irq_map`, `xtensa_map_ext_irq`, and `xtensa_get_ext_irq_no`.

## Control Flow
No inline runtime flow except identity `irq_canonicalize`. IRQ-domain code elsewhere uses the declarations to translate interrupt specifiers and map internal/external IRQs.

## State And Persistence
No owned state. IRQ domains and mappings are maintained by interrupt-controller code.

## Dependencies And Integration Points
Depends on variant interrupt count, platform extra IRQ count, Linux IRQ domains, and SMP migration support.

## Risks And Edge Cases
IRQ numbering reserves Linux IRQ 0 by offsetting hardware IRQs by one. Platform IRQ count must match external controller wiring. Device-tree translation must map internal/external IRQ cells correctly.

## Test Signals
Boot with device tree IRQ mappings, inspect `/proc/interrupts`, exercise external IRQ devices, and CPU hotplug IRQ migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irqflags.h

## Purpose
Implements local IRQ flag save, disable, enable, restore, and disabled checks for Xtensa.

## Important APIs, Types, And Functions
Provides `arch_local_save_flags`, `arch_local_irq_save`, `arch_local_irq_disable`, `arch_local_irq_enable`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`, and `arch_irqs_disabled`.

## Control Flow
Functions read/write the processor status register (`ps`) and use `rsil`, `wsr`, and `rsync` to raise/lower interrupt level. `XTENSA_FAKE_NMI` configurations preserve debug-level behavior and include safety diagnostics for lock/debug levels.

## State And Persistence
State is the CPU `ps` register interrupt level and exception bits. No software persistence.

## Dependencies And Integration Points
Depends on processor level constants, fake-NMI Kconfig, lockdep/trace IRQ flags, and generic interrupt control callers.

## Risks And Edge Cases
Restoring invalid PS bits can leave interrupts masked or enable them too early. Fake-NMI configurations are sensitive to `LOCKLEVEL`, `TOPLEVEL`, and debug level overlap. `rsync` ordering is required after status writes.

## Test Signals
Run interrupt enable/disable tracing, lockdep IRQ tests, fake-NMI perf IRQ tests, and nested interrupt stress on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/jump_label.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/jump_label.h

## Purpose
Implements Xtensa static key/jump-label code generation for dynamic branch patching.

## Important APIs, Types, And Functions
Defines architecture jump-label instruction size/encoding helpers and inline `arch_static_branch` / `arch_static_branch_jump` style routines used by `jump_label.h`.

## Control Flow
The inline assembly emits a patchable branch or nop site and records metadata in the jump table. Runtime jump-label code patches the site to toggle static branches without a normal conditional load.

## State And Persistence
State is compiled jump-table metadata and runtime-patched text. No durable persistence.

## Dependencies And Integration Points
Depends on `HAVE_ARCH_JUMP_LABEL`, non-XIP kernels, Xtensa text patching, and static key users across the kernel.

## Risks And Edge Cases
Instruction size and branch range must match the emitted encoding. XIP kernels disable this feature because text may not be writable. Bad patching can corrupt executable text.

## Test Signals
Build with jump labels, run static key selftests, toggle tracepoints and scheduler static branches, and verify XIP builds exclude arch jump labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kasan.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kasan.h

## Purpose
Defines Xtensa KASAN shadow-memory layout and initialization hooks.

## Important APIs, Types, And Functions
For `CONFIG_KASAN`, defines `KASAN_START_VADDR`, `KASAN_SHADOW_START`, `KASAN_SHADOW_SIZE`, `KASAN_SHADOW_END`, `KASAN_SHADOW_OFFSET`, and declares `kasan_early_init` and `kasan_init`; otherwise provides no-op stubs.

## Control Flow
No runtime flow in the header. Early architecture setup calls the declared init functions when KASAN is enabled.

## State And Persistence
KASAN shadow mappings and memory persist during runtime when enabled.

## Dependencies And Integration Points
Depends on MMU, non-XIP KASAN support selected in Kconfig, page-table layout, and generic KASAN.

## Risks And Edge Cases
Shadow offset and range must not collide with kernel virtual layout. XIP is excluded because writable shadow/text assumptions differ.

## Test Signals
Boot KASAN-enabled Xtensa, trigger slab/page out-of-bounds tests, and inspect shadow mapping setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kmem_layout.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kmem_layout.h

## Purpose
Defines Xtensa kernel virtual memory layout: page-table region, KSEG cached/bypass mappings, KIO mappings, KSEG physical base, and kernel stack size.

## Important APIs, Types, And Functions
Key macros are `XCHAL_PAGE_TABLE_VADDR`, `XCHAL_PAGE_TABLE_SIZE`, `XCHAL_KSEG_CACHED_VADDR`, `XCHAL_KSEG_BYPASS_VADDR`, `XCHAL_KSEG_SIZE`, `XCHAL_KSEG_ALIGNMENT`, `XCHAL_KSEG_TLB_WAY`, `XCHAL_KIO_TLB_WAY`, `XCHAL_KSEG_PADDR`, `XCHAL_KIO_CACHED_VADDR`, `XCHAL_KIO_BYPASS_VADDR`, `XCHAL_KIO_DEFAULT_PADDR`, `XCHAL_KIO_SIZE`, `XCHAL_KIO_PADDR`, `xtensa_get_kio_paddr`, `KERNEL_STACK_SHIFT`, and `KERNEL_STACK_SIZE`.

## Control Flow
Preprocessor branches select one of the MMU KSEG layouts and enforce physical-base alignment. For some OF configurations, KIO physical base is a runtime variable exposed by `xtensa_get_kio_paddr`.

## State And Persistence
No owned state except external `xtensa_kio_paddr` in dynamic KIO configurations. Constants define persistent virtual memory layout.

## Dependencies And Integration Points
Depends on Kconfig layout choices, core MMU features, OF, page tables, `page.h`, `io.h`, and MMU initialization.

## Risks And Edge Cases
Misaligned KSEG physical base is compile-time fatal. Wrong layout breaks `__pa`/`__va`, ioremap, highmem, and TLB setup. KASAN increases stack size.

## Test Signals
Compile all KSEG layout choices, boot OF and non-OF KIO configurations, test `__pa`/`__va`, MMIO, and stack overflow/KASAN builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kmem_layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/linkage.h

## Purpose
Defines Xtensa symbol alignment for assembly linkage.

## Important APIs, Types, And Functions
Defines `__ALIGN` and `__ALIGN_STR` as `.align 4`.

## Control Flow
No runtime flow; assembler/linkage macros use these definitions when emitting functions and symbols.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by Linux linkage macros and Xtensa assembly files.

## Risks And Edge Cases
Alignment must satisfy instruction fetch and ABI expectations. Too-small alignment can hurt performance or violate entry assumptions.

## Test Signals
Compile assembly objects and inspect symbol alignment for entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu.h

## Purpose
Defines the Xtensa per-mm context type for MMU builds and delegates noMMU builds to generic context support.

## Important APIs, Types, And Functions
For MMU builds, defines `mm_context_t` with `asid[NR_CPUS]` and `cpu`. For noMMU, includes `asm-generic/mmu.h`.

## Control Flow
No runtime control in this header.

## State And Persistence
`mm_context_t` persists in each `mm_struct`, tracking per-CPU ASIDs and the last CPU using the context.

## Dependencies And Integration Points
Used by `mmu_context.h`, scheduler context switching, TLB management, and generic MM.

## Risks And Edge Cases
ASID arrays must scale with `NR_CPUS`; stale CPU tracking can miss icache flushes or ASID refresh.

## Test Signals
Run process creation/exit, context-switch stress, SMP migration, and noMMU build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu_context.h

## Purpose
Implements Xtensa MMU context and ASID management for process address-space switches.

## Important APIs, Types, And Functions
Key definitions include per-CPU `asid_cache`, `NO_CONTEXT`, `ASID_USER_FIRST`, `ASID_MASK`, `ASID_INSERT`, `init_mmu`, `init_kio`, `set_rasid_register`, `get_rasid_register`, `get_new_mmu_context`, `get_mmu_context`, `activate_context`, `init_new_context`, `switch_mm`, and `destroy_context`.

## Control Flow
New contexts initialize all per-CPU ASIDs to invalid. On switch, if the process migrated CPUs the icache is invalidated; if migrated or switching to a different `mm`, `activate_context` ensures a current ASID, writes the RASID register with reserved/kernel/user slots, and invalidates the page directory. ASID wrap flushes the local TLB and starts a new generation.

## State And Persistence
State is per-mm ASID arrays, last CPU field, per-CPU ASID cache, RASID hardware register, TLB entries, and page-directory cache state.

## Dependencies And Integration Points
Depends on MMU hardware with TLBs, cacheflush, TLB flush, page tables, percpu, scheduler, and generic MM hooks.

## Risks And Edge Cases
ASID generation wrap must flush stale TLBs. Migration requires icache invalidation for possible VIPT/instruction coherency issues. `invalidate_page_directory` must match hardware page-table cache behavior.

## Test Signals
Run fork/exec/mmap stress, SMP migration, TLB shootdown tests, icache coherency tests, and ASID wrap stress with many processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mtd-xip.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mtd-xip.h

## Purpose
Provides Xtensa hooks used by MTD execute-in-place code while running directly from flash.

## Important APIs, Types, And Functions
Defines `xip_irqpending`, `xip_currtime`, `xip_elapsed_since`, and `xip_cpu_idle`.

## Control Flow
Macros read interrupt pending/enabled and cycle counter special registers, compute elapsed time by scaled cycle difference, and idle with `waiti 0`.

## State And Persistence
No state beyond CPU special registers.

## Dependencies And Integration Points
Depends on `xtensa_get_sr`, interrupt register definitions, cycle counter availability, and MTD XIP polling/idle code.

## Risks And Edge Cases
Elapsed-time scaling assumes cycle count up to about 1 GHz as commented. `waiti 0` must be safe while executing from XIP flash and waiting for interrupts.

## Test Signals
Build and boot XIP kernels, exercise MTD XIP erase/write wait paths, and verify interrupt wakeups during XIP operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mtd-xip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mxregs.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mxregs.h

## Purpose
Defines external register offsets for the Xtensa MX interrupt distributor and multicore control block.

## Important APIs, Types, And Functions
Macros include `MIROUT`, `MIPICAUSE`, `MIPISET`, `MIENG`, `MIENGSET`, `MIASG`, `MIASGSET`, `MIPIPART`, `SYSCFGID`, `MPSCORE`, and `CCON`.

## Control Flow
No code flow; SMP and interrupt-controller code uses these offsets with external-register read/write instructions.

## State And Persistence
State resides in MX hardware registers controlling IRQ routing, IPI causes, enables, run-stall, and coherency.

## Dependencies And Integration Points
Depends on Xtensa MX hardware and code selected by `XTENSA_MX`/SMP platform support.

## Risks And Edge Cases
Wrong offsets can misroute interrupts or stall cores. IPI partition and coherency registers are hardware-version sensitive.

## Test Signals
Boot SMP MX systems, send IPIs, route external IRQs, offline/online CPUs, and verify cache coherency enable state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mxregs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/nommu_context.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/nommu_context.h

## Purpose
Provides no-op Xtensa MMU/KIO initialization for noMMU builds and includes generic noMMU context handling.

## Important APIs, Types, And Functions
Defines inline `init_mmu` and `init_kio`, then includes `<asm-generic/nommu_context.h>`.

## Control Flow
No-op initialization functions return immediately; generic noMMU context code handles the rest.

## State And Persistence
No MMU context state is owned by this header.

## Dependencies And Integration Points
Used when `CONFIG_MMU` is disabled via `mmu_context.h`.

## Risks And Edge Cases
NoMMU platforms still may need cache attribute setup elsewhere; these stubs only mean there is no full MMU context to initialize.

## Test Signals
Build and boot noMMU Xtensa, run FLAT binaries, and verify memory map/cacheattr setup occurs in the correct boot path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/nommu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/page.h

## Purpose
Defines Xtensa page, physical/virtual address, cache aliasing, and page-table base types/macros.

## Important APIs, Types, And Functions
Key macros/types include `PAGE_OFFSET`, `PHYS_OFFSET`, `MAX_LOW_PFN`, `DCACHE_ALIAS_*`, `ICACHE_ALIAS_*`, `DCACHE_N_COLORS`, `pte_t`, `pgd_t`, `pgprot_t`, `pgtable_t`, `pte_val`, `pgd_val`, `pgprot_val`, `__pte`, `__pgd`, `__pgprot`, `clear_page`, `copy_page`, alias page helpers, `ARCH_PFN_OFFSET`, `__pa`, `__va`, `virt_to_page`, `page_to_virt`, and `virt_addr_valid`.

## Control Flow
Preprocessor logic selects MMU or noMMU address bases and computes alias-coloring parameters from cache way size. `___pa` converts KSEG cached/bypass and XIP KIO virtual addresses to physical addresses.

## State And Persistence
No owned state; defines address translation and typed page-table values used throughout runtime.

## Dependencies And Integration Points
Depends on cache and memory layout headers, VDSO page constants, generic memory model, highmem/cacheflush code, and MM.

## Risks And Edge Cases
`__pa`/`__va` must match KSEG/KIO mappings exactly, especially under XIP. Cache alias calculations drive highmem and user-page copying. Wrong `MAX_LOW_PFN` hides or overstates lowmem.

## Test Signals
Run boot memory tests, page allocator stress, highmem alias tests, XIP address conversion tests, and MMU/noMMU builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci-bridge.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci-bridge.h

## Purpose
Defines legacy Xtensa PCI host-bridge data structures and helper declarations.

## Important APIs, Types, And Functions
Declares `pciauto_bus_scan`, defines `struct pci_space`, `struct pci_controller`, and inline `pcibios_init_resource`.

## Control Flow
PCI platform code fills `pci_controller` with ops, config address/data pointers, IO/memory resources, resource placement windows, and IRQ mapping callback. `pcibios_init_resource` initializes resource fields.

## State And Persistence
Runtime state is host bridge controller structures and resource windows maintained by PCI platform code.

## Dependencies And Integration Points
Depends on Linux PCI core types, OF/platform PCI setup, and architecture-specific PCI host drivers.

## Risks And Edge Cases
The controller model supports one IO range and three memory ranges; more complex host bridges need extensions. IRQ mapping callback must match board wiring.

## Test Signals
PCI enumeration on Xtensa platforms, BAR assignment, IRQ routing, and resource conflict checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci-bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci.h

## Purpose
Defines Xtensa PCI architecture constants and mmap capabilities.

## Important APIs, Types, And Functions
Defines `pcibios_assign_all_busses`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `HAVE_PCI_MMAP`, `ARCH_GENERIC_PCI_MMAP_RESOURCE`, and `arch_can_pci_mmap_io`.

## Control Flow
No runtime flow. Generic PCI code uses these constants to allocate resources and allow user mappings.

## State And Persistence
No owned state; PCI core owns resources and mappings.

## Dependencies And Integration Points
Depends on generic PCI, scatterlist, slab/string helpers, and Xtensa I/O mapping.

## Risks And Edge Cases
Minimum IO/MEM resource assumptions may be wrong for unusual boards. PCI memory is assumed to equal physical memory address space for bounce-buffer decisions.

## Test Signals
Build PCI-enabled Xtensa, enumerate devices, mmap PCI resources from userspace, and validate IO/MEM BAR allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/perf_event.h

## Purpose
Placeholder architecture perf-event header for Xtensa.

## Important APIs, Types, And Functions
Defines only the include guard.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Satisfies generic perf includes while platform-specific perf support is handled elsewhere or through Kconfig feature gates.

## Risks And Edge Cases
Generic perf code that expects arch-specific declarations would require this header to grow. Empty content is acceptable only while no such contract is needed.

## Test Signals
Build `CONFIG_PERF_EVENTS` Xtensa variants, especially custom variants with performance monitor support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pgalloc.h

## Purpose
Implements Xtensa page-table allocation helpers for MMU builds.

## Important APIs, Types, And Functions
Defines `pmd_populate_kernel`, `pmd_populate`, `pgd_alloc`, `ptes_clear`, `pte_alloc_one_kernel`, and `pte_alloc_one`, while using generic pgalloc helpers for the underlying allocation.

## Control Flow
PMD populate macros store PTE table addresses directly because the PMD is a single entry inside the PGD. PTE allocation obtains a kernel or user PTE page/table, clears every PTE with `pte_clear`, and returns the table or page.

## State And Persistence
State is allocated page-table memory and PGD/PMD/PTE contents owned by the MM subsystem.

## Dependencies And Integration Points
Depends on MMU builds, slab/highmem, generic pgalloc, Xtensa page-table layout, and `pte_clear`.

## Risks And Edge Cases
Every newly allocated PTE must be cleared to avoid stale mappings. PMD population assumes the one-entry PMD layout; page-table layout changes must update these macros.

## Test Signals
Run mmap/munmap/page-fault stress, fork/exec, page-table allocation failure injection, and MMU debug page-table tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pgalloc.h -->
