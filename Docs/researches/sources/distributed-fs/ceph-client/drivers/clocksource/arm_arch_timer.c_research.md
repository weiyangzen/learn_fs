# sources/distributed-fs/ceph-client/drivers/clocksource/arm_arch_timer.c

Purpose: implements the ARM architected system timer using CP15/system-register access for clocksource, sched_clock, per-CPU clockevents, vDSO time, and KVM timestamp support.

Important APIs/types/functions: `arch_timer_read_counter`, `clocksource_counter`, `cyclecounter`, `arch_timer_register()`, `arch_counter_register()`, `arch_timer_of_init()`, `arch_timer_acpi_init()`, erratum workaround tables, CPU hotplug callbacks, and exported helpers `arch_timer_get_rate()`, `arch_timer_get_kvm_info()`, `kvm_arch_ptp_get_crosststamp()`.

Control flow: DT or ACPI GTDT probing maps PPIs, validates frequency, applies errata, selects physical/virtual/hypervisor timer access, requests per-CPU IRQs, registers CPU hotplug setup, registers the counter clocksource and sched_clock, and exposes KVM timecounter metadata.

State and persistence: global rate, selected PPI, erratum state, event-stream cpumask, per-CPU `clock_event_device`, CPU PM saved control registers, and KVM timecounter persist after init.

Dependencies and integration points: integrates with OF, ACPI GTDT, CPU PM, CPU hotplug, vDSO clock modes, arm64 capability detection, SMCCC/KVM PTP, sched_clock, and clockevents.

Risks: firmware must provide correct interrupt and frequency data. Erratum workarounds can disable vDSO fast paths and alter counter reads. PPI trigger validation repairs bad firmware with warnings. Suspend-stop behavior depends on DT/ACPI data. Incorrect PPI selection affects guests and EL2 configurations.

Test signals: DT and ACPI boot paths, virtual versus physical timer selection, erratum-specific platforms, CPU hotplug, suspend/resume, event stream enablement, vDSO clock mode, and KVM PTP cross timestamp calls.
