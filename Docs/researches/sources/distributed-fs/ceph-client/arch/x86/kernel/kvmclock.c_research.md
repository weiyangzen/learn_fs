# sources/distributed-fs/ceph-client/arch/x86/kernel/kvmclock.c

Purpose: Provides the KVM paravirtual clocksource, sched clock, wallclock, TSC calibration, and VDSO pvclock time-info setup for x86 guests.

Important APIs/types/functions: main entry is `kvmclock_init()`. Other APIs are `kvm_check_and_clear_guest_paused()`, `kvmclock_disable()`, per-CPU exported `hv_clock_per_cpu`, and early init `kvm_setup_vsyscall_timeinfo()`. Important helpers include `kvm_register_clock()`, `kvm_clock_read()`, `kvm_sched_clock_init()`, `kvm_get_wallclock()`, `kvm_get_tsc_khz()`, and `kvmclock_setup_percpu()`.

Control flow: early parameters can disable kvmclock or VDSO pvclock. Early vsyscall setup allocates extra pvclock pages if more possible CPUs exist than fit in the boot page and marks them decrypted for encrypted guests. Init selects old or new KVM clock MSRs, registers a CPU hotplug prepare callback for per-CPU pvti assignment, writes CPU0 system-time MSR, sets stable TSC flags if advertised, installs sched clock and x86 platform calibration/wallclock hooks, lowers clocksource rating below TSC when invariant TSC is good, and registers the clocksource.

State and persistence: KVM writes time into shared `pvclock_vsyscall_time_info` structures in `hv_clock_boot` or allocated `hvclock_mem`, and wallclock into `wall_clock`. Per-CPU pointers persist for the boot. `kvm_sched_clock_offset` normalizes sched-clock start.

Dependencies and integration points: depends on KVM paravirt feature detection from `kvm.c`, pvclock library, clocksource framework, x86 platform hooks, CPU hotplug, VDSO clock mode registration, memory encryption decryption APIs, and KVM system-time/wall-clock MSRs.

Risks: shared clock memory must be decrypted under guest memory encryption. VDSO pvclock is enabled only when the stable TSC bit is present. CPU hotplug setup must avoid CPU0 pointer duplication from percpu replication. Disabling clock must zero the system-time MSR to stop host writes.

Test signals: KVM guests should register `kvm-clock`, expose stable VDSO pvclock only with stable flags, calibrate TSC and loops-per-jiffy from pvclock, survive CPU hotplug, clear guest-paused flags and touch watchdogs, and allocate/decrypt extra pvclock memory for large CPU counts under SEV.
