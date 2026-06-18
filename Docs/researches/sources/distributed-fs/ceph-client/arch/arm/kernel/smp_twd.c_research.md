# sources/distributed-fs/ceph-client/arch/arm/kernel/smp_twd.c

Purpose: implements the ARM local TWD timer as a per-CPU clock event device for SMP systems.

Important APIs/types/functions: timer mode callbacks `twd_shutdown`, `twd_set_oneshot`, `twd_set_periodic`, `twd_set_next_event`; interrupt handler `twd_handler`; registration paths `twd_local_timer_common_register` and OF match declarations.

Control flow: registration maps the timer, parses PPI IRQ, allocates per-CPU clockevent devices, requests percpu IRQ, installs CPU hotplug callbacks, obtains/calibrates clock rate, and sets up the boot CPU immediately or through `late_time_init`. Per-CPU setup initializes the clockevent device, registers it, and enables the PPI. Clock-rate notifier updates all CPUs after rate changes.

State and persistence: `twd_base`, `twd_clk`, `twd_timer_rate`, `twd_evt`, `twd_ppi`, feature flags, and per-CPU setup flags.

Dependencies and integration: clockevents, percpu IRQs, cpuhp, OF IRQ/address/clock APIs, jiffies calibration, and local timer hardware.

Risks: absent/incorrect clock leads to calibration dependence; rate changes must update all per-CPU devices; hotplug must disable PPIs. Test signals include timer interrupts on all CPUs, CPU hotplug, cpufreq/clock-rate changes, NOHZ/oneshot mode, and DT binding probes.
