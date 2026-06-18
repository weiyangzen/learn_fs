# sources/distributed-fs/ceph-client/arch/alpha/kernel/perf_event.c

## Purpose
`perf_event.c` provides Linux perf hardware counter support for Alpha EV67-class CPUs and later compatible EV6/EV7 variants. It maps perf event types onto the Alpha PAL `wrperfmon` interface, schedules up to two EV67 PMCs under hardware pairing constraints, handles overflow interrupts, and registers a CPU PMU named `cpu`.

## Important APIs, Types, And Functions
- `struct cpu_hw_events` is per-CPU scheduling state: enabled flag, scheduled events, event types, current PMC indices, aggregate config, and active index mask.
- `struct alpha_pmu_t` describes a CPU PMU: event map, number of PMCs, bit shifts/masks, max periods, minimum counter-left values, constraint checker, and raw event validator.
- EV67-specific event identifiers include cycles, instructions, Bcache misses, and Mbox replay traps. `ev67_perfmon_event_map` maps Linux hardware events to these IDs; cache references are unsupported.
- `ev67_check_constraints()` validates one- or two-event combinations and assigns PMC indices/configs. Hardware only supports specific pairings such as instructions+cycles, instructions+Bcache misses, and cycles+Mbox replay.
- `alpha_write_pmc()` and `alpha_read_pmc()` isolate PMC bitfields inside the PCTR register via `wrperfmon`.
- `alpha_perf_event_set_period()` reloads a counter while respecting hardware limits near max period.
- `alpha_perf_event_update()` calculates deltas, including explicit overflow correction from the interrupt handler.
- `collect_events()` and `alpha_check_constraints()` validate perf groups.
- PMU callbacks `alpha_pmu_add`, `del`, `read`, `stop`, `start`, `enable`, `disable`, and `event_init` implement Linux perf operations.
- `alpha_perf_event_irq_handler()` services PMI overflows and calls `perf_event_overflow()`.
- `init_hw_perf_events()` detects supported CPUs, installs `perf_irq`, sets `alpha_pmu`, and registers the PMU at `early_initcall`.

## Control Flow
At early init, `supported_cpu()` reads CPU type from HWRPB and enables PMU support only for EV67 through EV69-compatible types. Event initialization validates event type, maps to Alpha event ID, checks group constraints, and leaves hardware config/PMC index unresolved until scheduling. Adding an event disables the PMU, disables interrupts, appends it if constraints allow, marks start/stop state, and reenables. PMU enable recomputes configuration when events were added, programs logging options and desired events, then enables the active PMC mask.

On overflow, the handler disables PMCs to avoid nested overflows, validates the overflow index from `la_ptr`, finds the matching scheduled event, updates its count with one full-period correction, reloads the period, reports overflow when needed, and reenables active counters.

## State And Persistence
PMU state is per-CPU in `cpu_hw_events`; event state lives in each `perf_event->hw`, including `event_base`, `config_base`, `idx`, `prev_count`, `period_left`, and state flags. Global `alpha_pmu` is set once at boot. Counts persist in perf event objects until deleted. No disk persistence exists.

## Dependencies And Integration Points
The file depends on Linux perf core, PAL `wrperfmon`, HWRPB CPU descriptors, Alpha interrupt plumbing through global `perf_irq`, per-CPU IRQ counters such as `irq_pmi_count`, and perf group APIs. It does not arbitrate PMU ownership with any other subsystem.

## Risks
- Counter overflow handling is inherently race-prone; the code compensates for negative deltas but depends on PMI timing and hardware period size.
- Only a narrow EV67 PMU model is supported. Later or earlier CPUs with subtly different counters may be misdetected or unsupported.
- Constraint logic assumes at most two events for EV67 and uses `BUG_ON(n_ev != 2)` in the multi-event path.
- `PERF_PMU_CAP_NO_EXCLUDE` means exclude-user/kernel settings are not honored.
- Raw event validation accepts only internal event IDs, not arbitrary PAL configurations.

## Test Signals
- Boot logs should show either unsupported CPU or supported CPU perf registration.
- `perf stat -e cycles,instructions` should work on supported Alpha hardware.
- Unsupported cache events should return `-EOPNOTSUPP` or `-EINVAL`.
- Group scheduling tests should accept valid EV67 pairings and reject invalid pairs.
- Sampling workloads should increment counts and handle overflow without `PMI: silly index` or `No event at index` warnings.
