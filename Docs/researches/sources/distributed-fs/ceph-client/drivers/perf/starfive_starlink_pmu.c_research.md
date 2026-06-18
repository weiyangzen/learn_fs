# sources/distributed-fs/ceph-client/drivers/perf/starfive_starlink_pmu.c

Purpose: StarFive StarLink uncore PMU driver for JH8100-style interconnect/cache performance counters. It exposes named StarLink events and a cycle counter as a perf PMU backed by MMIO counters and one overflow IRQ.

Important APIs, types, and functions: `struct starlink_pmu` embeds `struct pmu`, per-CPU `starlink_hw_events`, hotplug node, CPU PM notifier, MMIO base, cpumask, and IRQ. `struct starlink_hw_events` contains event slots and used bitmap for 64 possible counter indexes, with 16 programmable event counters and index 63 reserved for cycles. Perf callbacks include `starlink_pmu_event_init`, `add`, `del`, `start`, `stop`, `update`; IRQ and power paths are `starlink_pmu_handle_irq` and `starlink_pmu_pm_notify`.

Control flow: probe allocates the PMU and per-CPU state, maps resource 0, requests IRQ, registers CPU hotplug and CPU PM callbacks, fills `struct pmu`, and registers `starfive_starlink_pmu`. Event init rejects sampling, task attach, and CPU-less events, validates groups within the same hardware PMU, stores raw config, and pins the event to the PMU cpumask CPU. Add assigns the dedicated cycle counter or the first zero programmable bit. Start programs half-range period, writes event select for non-cycle events, enables the relevant interrupt bit, and turns on global counting. IRQ scans active events, checks overflow status bits, clears them, updates software counts, and reprograms periods.

State and persistence: runtime state is per-CPU event slots/bitmap, PMU cpumask, perf `prev_count` and `event->count`, and MMIO register state. CPU PM enter stops and updates active counters; exit restarts them.

Dependencies and integration: depends on OF compatible `starfive,jh8100-starlink-pmu`, platform MMIO, perf core, IRQ, CPU hotplug, optional CPU PM, and sysfs event/format/cpumask groups.

Risks: `find_first_zero_bit` returns `n_events` when full, not a negative error, so the `idx < 0` check cannot catch exhaustion; subsequent `set_bit(idx, used_mask)` at index 16 can allocate outside the intended 0-15 programmable range though still within the 64-bit bitmap. Cycle counter deletion clears bit 63 even though add never sets it. Global enable is stopped when stopping any event, which can affect concurrent counters. Test signals include event exhaustion, cycle plus programmable events together, overflow IRQ for bit 63 and low bits, CPU hotplug IRQ affinity, and CPU PM save/restore.
