# sources/distributed-fs/ceph-client/drivers/perf/apple_m1_cpu_pmu.c

Purpose: Provides an ARM PMU backend for Apple M1/M2 CPU PMUs, whose counters and events are non-architectural implementation registers rather than standard PMUv3 counters.

Important APIs and functions: `m1_pmu_init()` fills an `arm_pmu` with backend callbacks. Low-level helpers read/write counters `PMC0..PMC9`, enable counters and interrupts through Apple PMCR registers, configure EL0/EL1 host/guest filters, and program event selectors in PMESR0/PMESR1. `m1_pmu_handle_irq()` handles overflows. `m1_pmu_get_event_idx()` enforces event-to-counter affinity from `m1_pmu_event_affinity`. OF init callbacks name Icestorm, Firestorm, Avalanche, and Blizzard PMUs.

Control flow: Platform probe calls `arm_pmu_device_probe()` with Apple compatible data. The selected init callback sets PMU name and counter width mode: M1 cores use advertised 47-bit overflow behavior, M2 cores 63-bit. Event mapping translates generic perf hardware events and selected PMUv3 common events to Apple event IDs. When an event starts, the driver configures filters/event select, enables the counter and PMI, and relies on the shared ARM PMU framework for period management. IRQ handling reads Apple PMSR overflow state, stops the PMU, updates each active event, resets periods, calls perf overflow handling, and restarts.

State and persistence: Counter values, enable bits, interrupt bits, filter bits, event selectors, PMU mode, and overflow state live in Apple system registers per CPU. Software stores event mappings, counter masks, and per-CPU `arm_pmu` state in the ARM PMU framework. No data is persistent across CPU reset.

Dependencies and integration points: Depends on `linux/perf/arm_pmu.h`, `arm_pmuv3.h`, Apple implementation sysreg definitions, IRQ register helpers, and OF platform probing. It integrates with generic ARM PMU event allocation, filtering, reset, and perf sysfs groups.

Risks: The event table is partly experimental and has strict counter affinity; wrong affinity causes unavailable or incorrect counts. Counters 0 and 1 are fixed cycles/instructions, while programmable counters start at 2. Guest filtering is only supported when kernel runs in hyp mode; otherwise non-excluded guest events are rejected. Spurious interrupt handling clears `PMCR0_IACT`; changes must preserve that path.

Test signals: OF probe on each compatible, sysfs events/format, generic cycles/instructions/branch events, PMUv3 event mapping bitmap, counter allocation under constrained events, overflow interrupts, exclude_user/exclude_kernel/exclude_host/exclude_guest combinations, reset on CPU bring-up, and M1 versus M2 counter-width behavior.
