# sources/distributed-fs/ceph-client/drivers/perf/arm_v6_pmu.c

## Purpose
ARMv6 CPU PMU hardware implementation for ARM1136 and ARM1176. It maps generic perf events to ARMv6 event numbers, accesses CP15 PMU registers, handles three counters, and plugs hardware callbacks into the common ARM PMU core.

## Important APIs, Types, And Functions
- Event maps `armv6_perf_map` and `armv6_perf_cache_map` translate generic perf events to ARMv6 encodings.
- `armv6_pmcr_read()` and `armv6_pmcr_write()` access the PMCR.
- `armv6pmu_read_counter()` and `armv6pmu_write_counter()` access cycle, counter0, and counter1 registers.
- `armv6pmu_enable_event()` and `armv6pmu_disable_event()` program event select and interrupt bits.
- `armv6pmu_handle_irq()` processes overflow flags and calls common period/update helpers.
- `armv6pmu_get_event_idx()` reserves the cycle counter for CPU cycles and two event counters for other events.
- `armv6_1136_pmu_init()` and `armv6_1176_pmu_init()` install callbacks and names.

## Control Flow
The built-in platform driver matches `arm,arm1176-pmu` or `arm,arm1136-pmu` and calls `arm_pmu_device_probe()`. Hardware init fills the callback table and counter mask. Perf add chooses an index through common core; start reloads the period and calls `armv6pmu_enable_event()`. IRQ reads PMCR, writes it back to clear overflow flags, updates each overflowing active event, reloads its period, raises perf overflow, and runs pending IRQ work.

## State And Persistence
State is mostly common `arm_pmu` per-CPU event state plus PMCR event select, interrupt enable, and overflow bits. The file has no durable state. ARMv6 counters cannot be individually stopped; disabled programmable counters are switched to the NOP-like ETM external output event and their interrupts disabled.

## Dependencies And Integration Points
It depends on CP15 access, `asm/irq_regs.h`, platform/OF matching, generic perf event maps and common ARM PMU helpers from `arm_pmu.c`.

## Risks
The hardware cannot individually disable counters, so disabled counters may still physically count unless pointed at the expected inactive event. The cycle counter cannot be independently stopped, so interrupt masking and period reload are used to ignore stale counts. Cache mappings combine read/write accesses because the hardware cannot distinguish them. NMI-delivered PMU interrupts are called out as incompatible with `irq_work_run()` assumptions.

## Test Signals
On ARM1136/1176 DT systems, validate driver registration, three counters in the boot log, `perf stat` for cycles/instructions/branches/cache misses, sampling overflow, counter exhaustion with groups larger than three, and behavior after CPU hotplug or reset.
