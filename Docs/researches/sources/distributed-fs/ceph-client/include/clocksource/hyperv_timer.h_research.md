# sources/distributed-fs/ceph-client/include/clocksource/hyperv_timer.h

Purpose: Hyper-V clocksource and synthetic timer interface for guest VMs.

Important APIs/types/functions: `HV_MAX_MAX_DELTA_TICKS`, `HV_MIN_DELTA_TICKS`, `hv_stimer_alloc`, cleanup/init ISR helpers, `hv_init_clocksource`, `hv_remap_tsc_clocksource`, `hv_get_tsc_pfn`, `hv_get_tsc_page`, `hv_adj_sched_clock_offset`, and `hv_read_tsc_page_tsc`.

Control flow: under `CONFIG_HYPERV_TIMER`, callers use Hyper-V timer routines and `hv_read_tsc_page_tsc()` loops over the TSC page sequence: read sequence, reject zero, read scale/offset/raw TSC with memory barriers, then retry if the sequence changed. Disabled builds provide safe null/zero stubs.

State and persistence: reads shared hypervisor `ms_hyperv_tsc_page` state and manages synthetic timer allocations in implementation code. This header itself stores none.

Dependencies and integration points: depends on `linux/clocksource.h`, `math64.h`, Hyper-V HVDK definitions, and architecture raw timer access through `<asm/hyperv_timer.h>`.

Risks: sequence/barrier protocol is correctness-critical for monotonic reference time. CPU hotplug cleanup and legacy synthetic interrupt routing must match VMbus behavior. Disabled stubs must not be treated as a usable clocksource.

Test signals: Hyper-V guest boot/timekeeping tests, CPU hotplug with synthetic timers, TSC-page fallback tests, and clocksource watchdog validation.
