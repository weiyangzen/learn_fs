# sources/distributed-fs/ceph-client/arch/x86/events/msr.c

## Purpose

This file implements the x86 perf `msr` PMU, a small software-facing PMU that exposes selected model-specific-register counters through perf. It provides count-only events for TSC, APERF, MPERF, PPERF, SMI count, PTSC, IRPERF, and CPU thermal margin when supported by the boot CPU and by direct probing.

The PMU does not program hardware counters. It reads existing architectural or vendor MSRs, stores the previous value in each perf event, and reports deltas or snapshots through perf's generic software context.

## Important APIs, Types, And Data

Key types and globals:

- `enum perf_msr_id`: stable event ids used as perf `config` values. The ids run from `PERF_MSR_TSC` through `PERF_MSR_THERM`, with `PERF_MSR_EVENT_MAX` as the upper bound.
- `static struct perf_msr msr[]`: one descriptor per event. Each entry supplies an MSR number, an optional event attribute group, and an availability test. The TSC entry has `.no_check = true` and uses a zero MSR number as a sentinel for `rdtsc_ordered()`.
- `static unsigned long msr_mask`: bitmask produced by `perf_msr_probe()` describing which enum ids are usable on this machine.
- `static struct pmu pmu_msr`: perf PMU callback table registered under the name `msr`.

Availability tests gate optional events with boot CPU feature and vendor checks: `test_aperfmperf()` checks `X86_FEATURE_APERFMPERF`, `test_ptsc()` checks `X86_FEATURE_PTSC`, `test_irperf()` checks `X86_FEATURE_IRPERF`, `test_therm_status()` checks `X86_FEATURE_DTHERM`, and `test_intel()` restricts PPERF and SMI to Intel CPUs while leaving final MSR availability to `perf_msr_probe()`.

Sysfs/perf metadata is built with `PMU_EVENT_ATTR_STRING`, `PMU_EVENT_GROUP`, `PMU_FORMAT_ATTR`, and explicit `attribute_group` arrays. The default `events` group always exposes `tsc`; `attr_update` can add supported optional event groups after probing. Thermal margin has additional `.snapshot` and `.unit` event attributes.

## Control Flow

Initialization starts at `msr_init()` via `device_initcall()`. If the boot CPU lacks TSC, it prints a continuation message and leaves the PMU unregistered. Otherwise it calls `perf_msr_probe(msr, PERF_MSR_EVENT_MAX, true, NULL)` to test the MSR table and populate `msr_mask`, then registers `pmu_msr` as `msr` with `perf_pmu_register()`.

Event creation is handled by `msr_event_init()`. It rejects events for another PMU type, rejects sampling by checking `event->attr.sample_period`, rejects out-of-range `config` values, applies `array_index_nospec()` before indexing `msr[]`, rejects unavailable events whose bit is not present in `msr_mask`, and initializes `event->hw.idx`, `event->hw.event_base`, and `event->hw.config`.

Counter reads use `msr_read_counter()`. A nonzero `event->hw.event_base` is read with `rdmsrq()`, while the TSC sentinel path uses `rdtsc_ordered()`.

Runtime callbacks are simple. `msr_event_add()` starts the event when `PERF_EF_START` is set. `msr_event_start()` records the current counter in `event->hw.prev_count`. `msr_event_stop()` and `msr_event_del()` update the event count. `msr_event_update()` reads the current value, atomically swaps `prev_count` using `local64_try_cmpxchg()`, computes a delta, and updates `event->count`.

Special update rules are important. `MSR_SMI_COUNT` deltas are sign-extended from bit 31 before being added. `MSR_IA32_THERM_STATUS` is treated as a snapshot: if bit 31 indicates a valid digital readout, bits 16-21 become the current count; otherwise the event count is set to `-1`. Other counters add the unsigned wraparound delta.

## State And Persistence Behavior

There is no persistent storage. System-wide availability state is held in `msr_mask` after boot-time probing. Each perf event stores its selected MSR in `event->hw.event_base`, the enum id in `event->hw.config`, and the previous raw value in `event->hw.prev_count`.

The PMU uses `perf_sw_context`, so events are managed in perf's software context rather than by a fixed hardware counter allocator. It also advertises `PERF_PMU_CAP_NO_INTERRUPT` and `PERF_PMU_CAP_NO_EXCLUDE`, which signals no interrupt-driven sampling and no privilege exclusion filtering. `msr_event_update()` is written to tolerate an NMI updating `prev_count` concurrently by using a compare-exchange loop around the previous count.

## Dependencies And Integration Points

The file depends on `linux/perf_event.h`, `linux/sysfs.h`, `linux/nospec.h`, `asm/msr.h`, `probe.h`, and x86 CPU feature/vendor state from `boot_cpu_has()` and `boot_cpu_data`.

Integration points include the registered perf PMU name `msr`, user-visible event names `tsc`, `aperf`, `mperf`, `pperf`, `smi`, `ptsc`, `irperf`, and `cpu_thermal_margin`, the `format/event` description as `config:0-63`, and optional event groups attached through `pmu_msr.attr_update`.

## Risks And Edge Cases

The PMU assumes boot-CPU feature checks are enough for event availability. On heterogeneous or unusual systems, a feature present on the boot CPU but not on all online CPUs could make per-CPU reads fragile.

`perf_pmu_register()` return value is ignored. If registration fails, the init path does not report or undo anything beyond the failed call.

TSC uses `event_base == 0` as a sentinel, so any future event using MSR 0 would collide with the TSC path. The PMU rejects only `sample_period` for unsupported sampling. Thermal margin is a gauge-like snapshot, not a monotonically increasing counter, and SMI count wrap handling relies on 32-bit sign extension.

## Test Signals

Useful validation signals include building the x86 perf event code, booting on Intel and AMD systems and inspecting `/sys/devices/msr/events` plus `/sys/devices/msr/format/event`, running `perf list msr`, running `perf stat -e msr/tsc/`, `msr/aperf/`, `msr/mperf/`, and other supported events, verifying unavailable or out-of-range events fail with `-EINVAL`, verifying sampling attempts are rejected, and checking `msr/cpu_thermal_margin/` reports a Celsius snapshot or `-1` when invalid.
