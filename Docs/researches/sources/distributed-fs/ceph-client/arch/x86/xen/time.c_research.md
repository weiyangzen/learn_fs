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
