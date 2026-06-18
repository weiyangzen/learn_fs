# sources/distributed-fs/ceph-client/arch/x86/events/intel/knc.c

## Purpose

This file provides the x86 perf PMU backend for Intel Xeon Phi Knights Corner. KNC has a small non-architectural PMU with two programmable counters, custom global control/status MSRs, a KNC-specific event map, and cache-event encodings.

## Important APIs, Types, And Data

- `knc_perfmon_event_map[]` maps generic perf hardware events to KNC event selectors.
- `knc_hw_cache_event_ids` maps perf cache triplets to KNC encodings, including special handling for valid event zero via `ARCH_PERFMON_EVENTSEL_INT`.
- `knc_event_constraints[]` pins a set of L2/snoop/prefetch events to counter 0.
- KNC global MSR constants define status, overflow acknowledge, and global counter control registers.
- `knc_pmu` is the `struct x86_pmu` installed by `knc_pmu_init()`.

## Control Flow

`knc_pmu_init()` copies the static `knc_pmu` into the global `x86_pmu` and installs KNC cache-event IDs. Generic perf setup uses `knc_pmu_event_map()` for predefined events and `x86_pmu_hw_config()` for normal event configuration. Enable/disable operations write the per-counter event select MSR with or without `ARCH_PERFMON_EVENTSEL_ENABLE`; global enable/disable flips the two KNC global enable bits.

Interrupt handling is local to `knc_pmu_handle_irq()`. It disables all counters, reads global overflow status, acknowledges pending bits, loops up to 100 times while status remains set, updates/restarts active events with `intel_pmu_save_and_restart()`, emits `perf_event_overflow()`, then restores global enable only if the PMU was enabled before the interrupt path.

## State And Persistence

State is held in the common per-CPU `cpu_hw_events` event array and active mask, with hardware state in KNC MSRs. There is no private persistent state beyond the selected `x86_pmu` callbacks and copied cache-event map.

## Dependencies And Integration Points

The file integrates with generic x86 perf scheduling, event constraints, APIC perf IRQ accounting, safe MSR writes, and perf overflow delivery. It relies on common Intel helpers for save/restart and x86 event setup while substituting KNC-specific global control and status handling.

## Risks And Edge Cases

- Only counters 0 and 1 are globally enabled; constraints and masks must stay consistent with this limit.
- The IRQ loop has a 100-iteration stuck guard; repeated status bits trigger warning and debug dump.
- The event map contains unsupported cache combinations as zero or `-1`; callers depend on generic validation to reject unsupported encodings.
- Safe MSR writes ignore return values in enable/disable paths, so hardware write failures are not propagated.

## Test Signals

Validation should include KNC boot selection, `perf stat` for cycles/instructions/cache/branches, constrained L2 events, overflow interrupt delivery, no stuck IRQ loop warnings, and sysfs format attributes for `event`, `umask`, `edge`, `inv`, and `cmask`.
