# sources/distributed-fs/ceph-client/drivers/perf/arm_xscale_pmu.c

## Purpose
ARMv5 XScale PMU driver for XScale PMU architecture v1 and v2. It maps perf events to XScale encodings, accesses coprocessor 14 PMU registers, handles v1 three-counter and v2 five-counter layouts, and probes by CPU ID rather than OF match data.

## Important APIs, Types, And Functions
- `xscale_perf_map` and `xscale_perf_cache_map` translate generic events.
- XScale1 callbacks include `xscale1pmu_handle_irq()`, `xscale1pmu_enable_event()`, `xscale1pmu_disable_event()`, `xscale1pmu_get_event_idx()`, and counter read/write helpers.
- XScale2 callbacks include separate PMNC, overflow flag, event select, interrupt enable, and five-counter read/write helpers.
- `xscale_map_event()` delegates to `armpmu_map_event()`.
- `xscale_pmu_probe_table` matches `ARM_CPU_XSCALE_ARCH_V1` and `ARM_CPU_XSCALE_ARCH_V2`.

## Control Flow
The built-in platform driver invokes `arm_pmu_device_probe()` with no OF table and an XScale CPU-ID probe table. `probe_current_pmu()` matches the current CPU and calls the v1 or v2 init function. Perf scheduling uses v1 allocation for cycle/counter0/counter1, while v2 reuses that logic then adds counter3 and counter2. IRQ handlers disable the PMU, read overflow status, update and reload overflowing events through common helpers, run IRQ work, and re-enable the PMU.

## State And Persistence
State is held in common per-CPU PMU structures plus XScale PMNC/event-select/interrupt/overflow registers. XScale1 stores event select fields in PMNC; XScale2 uses separate registers. No persistent state exists.

## Dependencies And Integration Points
The file depends on ARM CPU ID definitions, coprocessor 14 inline assembly, platform probing, OF-independent CPU probe tables, and common ARM PMU callbacks from `arm_pmu.c`.

## Risks
XScale1 has an A-stepping erratum where a second overflow can clear a previous overflow bit; the driver documents no workaround. Some macros for reset use names that appear inherited and must match included definitions at compile time. IRQ handlers return `IRQ_NONE` after disabling the PMU if no overflow is found, so spurious interrupts rely on later paths to re-enable only when handled. Cache mappings are limited and approximate. XScale2 counter allocation order is unusual, preferring counter3 before counter2 after v1 counters.

## Test Signals
On XScale v1/v2 hardware, validate CPU-ID probe, reported counter count, `perf stat` for cycles/instructions/cache/TLB events, overflow sampling, groups exceeding available counters, spurious interrupt behavior, and raw event masking to 8-bit values.
