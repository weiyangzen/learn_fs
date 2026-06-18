# sources/distributed-fs/ceph-client/drivers/clocksource/hyperv_timer.c

Purpose: provides Hyper-V synthetic timers as per-CPU clockevents and Hyper-V reference counters as clocksources/sched_clock for guest and root partitions.

Important APIs/types/functions: `hv_stimer_alloc()`, `hv_stimer0_isr()`, `hv_stimer_cleanup()`, legacy init/cleanup exports, `hv_stimer_global_cleanup()`, `read_hv_clock_msr()`, `read_hv_clock_tsc()`, `hv_init_clocksource()`, `hv_init_tsc_clocksource()`, and `hv_remap_tsc_clocksource()`.

Control flow: stimer allocation checks hypervisor features, allocates per-CPU clockevents, chooses direct mode or legacy VMbus-message mode, sets up IRQ/handler, and registers CPU hotplug callbacks. Clocksource init prefers the TSC reference page when available, with MSR fallback, and registers the MSR clocksource when supported.

State and persistence: per-CPU clockevent devices, direct-mode flag, stimer IRQ/message SINT, TSC reference page/PFN, sched_clock offset, and registered clocksources persist.

Dependencies and integration points: integrates with Hyper-V MSRs, VMbus legacy callbacks, ACPI GSI setup, CPU hotplug, paravirt or generic sched_clock, vDSO clock mode, TDX/paravisor feature checks, hibernation offset adjustment, and root-partition remapping.

Risks: direct versus legacy mode has different initialization timing. TSC page can be unavailable transiently and falls back to slow MSR reads. Ratings are adjusted for invariant TSC/root partition/TDX cases. Cleanup must coordinate CPU hotplug and VMbus paths.

Test signals: Hyper-V guests with and without direct mode, legacy VMbus stimer path, CPU online/offline, hibernation resume offset adjustment, root partition remap, invariant TSC rating behavior, and vDSO HVCLOCK exposure.
