# sources/distributed-fs/ceph-client/arch/x86/events/intel/cstate.c

## Purpose

This file exposes Intel C-state residency MSRs as perf PMUs. It creates separate logical PMUs for core-scope, package/die-scope, and module/cluster-scope residency counters so perf users can count residency alongside ordinary events without special MSR tooling. The counters are read-only, free-running residency counters, so the implementation supports system-wide counting only and explicitly rejects sampling.

## Important APIs, Types, And Data

- `struct cstate_model` is the per-CPU-model capability table. It lists supported core, package, and module event bitmasks plus quirk flags.
- `core_msr[]`, `pkg_msr[]`, and `module_msr[]` map perf event IDs to concrete residency MSRs and sysfs event groups.
- `cstate_core_pmu`, `cstate_pkg_pmu`, and `cstate_module_pmu` are `struct pmu` instances registered with `PERF_PMU_SCOPE_CORE`, `PERF_PMU_SCOPE_PKG` or `PERF_PMU_SCOPE_DIE`, and `PERF_PMU_SCOPE_CLUSTER`.
- `intel_cstates_match[]` maps Intel VFM identifiers to `struct cstate_model` instances covering Nehalem through recent Atom/Core/Xeon families.
- `DEFINE_CSTATE_FORMAT_ATTR()` and `PMU_EVENT_ATTR_STRING()` define perf sysfs format and event aliases such as `c1-residency`, `c6-residency`, and `c10-residency`.

## Control Flow

Module initialization enters `cstate_pmu_init()`, rejects hypervisors, matches the boot CPU against `intel_cstates_match[]`, probes MSR availability in `cstate_probe()`, then registers the PMUs in `cstate_init()`. Probing uses `perf_msr_probe()` with the model bitmasks, so the advertised event set is the intersection of model knowledge and readable MSRs.

Event setup goes through `cstate_pmu_event_init()`. It validates the PMU type, rejects sampling and task events, bounds-checks `attr.config` with `array_index_nospec()`, verifies the probed MSR mask, and stores the selected MSR in `event->hw.event_base`. Add/start snapshots the current MSR value into `prev_count`; stop/read calls `cstate_pmu_event_update()`, which atomically advances `prev_count` and accumulates the delta into `event->count`.

## State And Persistence

Global state is limited to probed MSR masks and booleans tracking whether each PMU was registered. Per-event state is the selected MSR address, the event ID in `hw.config`, and `prev_count`. There is no persistent storage beyond live kernel PMU registration and no hardware programming other than `rdmsrq()`.

## Dependencies And Integration Points

The file depends on perf core PMU registration, x86 CPU model matching, topology scope helpers, MSR accessors, and `perf_msr_probe()`. Sysfs integration is through perf PMU event and format groups. Multi-die packages are exposed as `cstate_die` by changing the PMU scope/name during registration.

## Risks And Edge Cases

- Counter deltas assume unsigned free-running MSR behavior; wrap handling relies on natural unsigned subtraction.
- The PMUs reject per-task and sampling usage, so callers expecting interrupt-driven samples receive `-EINVAL`.
- Probe correctness depends on model tables staying aligned with Intel MSR availability.
- The KNL quirk block assigns `MSR_KNL_CORE_C6_RESIDENCY` through `pkg_msr[PERF_CSTATE_CORE_C6_RES]`, while core event initialization later reads `core_msr[]`; this is a notable audit point because it appears inconsistent with the comment and enum domain.
- Hypervisor environments are rejected entirely, avoiding virtualized MSR ambiguity at the cost of no guest exposure.

## Test Signals

Useful validation includes boot/module load on supported and unsupported Intel models, sysfs presence under `/sys/bus/event_source/devices/cstate_*`, `perf stat -a -e cstate_core/c6-residency/` style counts, rejection of sampling/per-task events, and model-specific checks for renamed `cstate_die` on multi-die systems. KNL/SLM quirk tests should verify the actual MSR selected for the affected residency event.
