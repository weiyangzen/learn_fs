## sources/distributed-fs/ceph-client/arch/loongarch/kernel/perf_event.c

### Purpose
`perf_event.c` implements LoongArch hardware PMU support and perf callchains. It maps generic and cache perf events to Loongson PMU event IDs, allocates per-CPU counters, handles overflows, exposes a `cpu` PMU, and supplies kernel/user callchain walkers.

### Important APIs, Types, And Functions
Key types are `struct cpu_hw_events`, `struct loongarch_perf_event`, and `struct loongarch_pmu`. The PMU callbacks are `loongarch_pmu_event_init`, `add`, `del`, `start`, `stop`, `read`, `enable`, and `disable`, registered through `perf_pmu_register`. Counter/control CSR helpers operate on four CSR pairs, while initialization derives counter count and bit width from `LOONGARCH_CPUCFG6`. Callchain APIs are `perf_callchain_user` and `perf_callchain_kernel`.

### Control Flow
Event init rejects branch-stack sampling, checks event type and target CPU, requests the per-CPU `INT_PCOV` IRQ on first active event, maps the event, sets privilege filters, period state, and group validation. Add allocates a free counter in `used_mask`, disables it, stores the event pointer, and optionally starts it. Start programs the period and saved control state; PMU enable writes saved controls to hardware. Overflow IRQ pauses counters, scans used counters for the overflow bit, updates counts, reloads periods, calls `perf_event_overflow`, resumes counters, and runs irq work.

### State, Persistence, And Dependencies
Per-CPU event arrays, used masks, saved control registers, active event count, and raw-event mutex are runtime state. PMU CSR state persists while events are active. Dependencies include LoongArch PMU CSRs, interrupt mapping, generic perf core, stack unwinder, user access helpers, and CPU feature `cpu_has_pmp`.

### Integration Points
Generic perf opens the registered `"cpu"` PMU. `traps.c`/IRQ routing must deliver `INT_PCOV`. Stack unwinding integrates with ORC/prologue unwinder code. `perf_regs.c` provides register sampling support.

### Risks
The implementation defines `LOONGARCH_MAX_HWEVENTS` as 32 but CSR helpers only handle counters 0-3; if CPUCFG reports more than four counters, later reads/writes warn and return zero. Overflow uses bit 63 with `max_period = 2^63-1`, so counter width assumptions must match hardware. Group validation is a simple counter-count model and does not model event-specific counter constraints if future PMUs add them. Raw events share a global `raw_event` protected only during init.

### Test Signals
Run `perf stat` for cycles, instructions, cache refs/misses, branch events, raw events, and grouped events up to and beyond available counters. Run sampling to force overflow IRQs, user and kernel callchain collection, CPU hotplug, and concurrent perf opens/closes. Check dmesg for PMU counter count and invalid counter warnings.
