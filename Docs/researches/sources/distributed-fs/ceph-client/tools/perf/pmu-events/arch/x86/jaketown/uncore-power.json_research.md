# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-power.json

## Purpose

`uncore-power.json` defines 39 Jaketown package control unit (`PCU`) uncore PMU events. These events expose package power-management behavior: PCU clockticks, per-core C-state transition cycles, demotions, frequency band residency, frequency/voltage transition cycles, maximum-frequency limit reasons, memory phase shedding, core C-state occupancy, PROCHOT cycles, and VR-hot cycles.

The file supplies perf's public `UNC_P_*` event aliases for package power and thermal diagnostics on Jaketown systems.

## Important API Surface and Data Shape

The file is a JSON array of 39 unique objects. Common keys are `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, and `Unit`. Unlike most neighboring files, none of these records use `UMask`; the core C-state occupancy records use a `Filter` field instead.

All records use `Unit: "PCU"` and `PerPkg: "1"`. Counter lists allow `0,1,2,3`.

Important event families:

- `UNC_P_CLOCKTICKS`: PCU pclk cycles.
- `UNC_P_CORE{0..7}_TRANSITION_CYCLES`: per-core C-state transition cycles.
- `UNC_P_DEMOTIONS_CORE{0..7}`: per-core demotion events.
- `UNC_P_FREQ_BAND{0..3}_CYCLES`: cycles spent in selected frequency bands.
- Max/min/frequency controls: `UNC_P_FREQ_MAX_CURRENT_CYCLES`, `MAX_LIMIT_THERMAL`, `MAX_OS`, `MAX_POWER`, `MIN_IO_P`, `MIN_PERF_P`, and `FREQ_TRANS_CYCLES`.
- Voltage controls: increase/decrease/change transition cycles.
- Package pressure indicators: memory phase shedding, internal/external PROCHOT, total transition cycles, and VR hot.
- `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6`: event code `0x80` differentiated by `Filter` values `occ_sel=1`, `occ_sel=2`, and `occ_sel=3`.

## Control Flow

No code executes inside the file. External control flow:

1. perf's pmu-events tooling parses the JSON.
2. Generated event tables include PCU event rows and filter metadata.
3. Runtime perf CPU matching selects the Jaketown table.
4. `perf list` exposes `UNC_P_*` aliases.
5. When a user selects an alias, perf encodes the event code and any filter into a PCU uncore PMU configuration.

The `Filter` field is the most notable control input. It changes the occupancy selector for the shared `0x80` event code, so generator/runtime support for filter strings is required.

## State and Persistence Behavior

The file persists static mappings from public names to PCU PMU encodings. It has no mutable state and no local persistence beyond source control.

All records are package scoped. Counts describe package/PCU power-management behavior and should not be interpreted as per-thread execution. Per-core event names identify core indexes as observed by the PCU, not local thread state.

## Dependencies and Integration Points

Dependencies include:

- perf pmu-events JSON parser support for uncore `Unit` and `Filter`.
- Jaketown PCU hardware event codes and occupancy selectors.
- Runtime uncore PCU PMU support in the kernel/perf stack.
- Adjacent memory and interconnect event catalogs for correlated power/performance analysis.

The `Filter` integration point is important: if filters are dropped during generation, all three `UNC_P_POWER_STATE_OCCUPANCY.*` aliases would collapse to the same event encoding.

## Risks and Edge Cases

- The file intentionally omits `UMask` on all 39 records. Consumers must not require `UMask` for PCU events.
- `UNC_P_CLOCKTICKS` and `UNC_P_FREQ_TRANS_CYCLES` omit `EventCode`, so defaults or special handling need validation.
- The three occupancy records share the same brief/public text saying "Number of cores in C0" even for `CORES_C3` and `CORES_C6`; the `Filter` distinguishes the actual selector, but generated help text is misleading.
- Core-indexed families must stay complete for cores 0 through 7. Missing one core or swapping event codes would skew diagnostics.
- Power/thermal events often depend on platform firmware behavior, so hardware smoke tests can be noisy or workload-dependent.

## Test Signals

- `jq` parse succeeds and reports 39 unique event names.
- Every record has `Unit == "PCU"` and `PerPkg == "1"`.
- No record requires `UMask`; tests should assert parser tolerance for PCU records without masks.
- The occupancy family should have exactly three aliases with `Filter` values `occ_sel=1`, `occ_sel=2`, and `occ_sel=3`.
- Generated pmu-events code should retain filter metadata.
- On supported hardware, `perf list` should show PCU aliases, and smoke tests should include `UNC_P_CLOCKTICKS`, a frequency-band event, and an occupancy event.
