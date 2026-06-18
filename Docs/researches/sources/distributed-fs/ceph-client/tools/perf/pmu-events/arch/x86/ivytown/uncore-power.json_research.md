# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-power.json

## Purpose
This JSON file defines Ivy Town PCU uncore power-management PMU events for perf. It covers package clockticks, per-core C-state transition cycles, delayed C-state aborts, demotions, frequency-band residency, max/min frequency limit causes, package C-state residency and exit latency, power-state occupancy, PROCHOT, voltage transitions, memory phase shedding, and VR hot cycles. These aliases support diagnosis of platform power policy and frequency throttling behavior.

## Important APIs, Types, And Functions
The file is declarative metadata. Important fields are `EventName`, `EventCode`, `Counter`, `PerPkg`, `Unit`, `BriefDescription`, `PublicDescription`, and for occupancy selectors, `Filter`. All 74 entries use `Unit: PCU`, `PerPkg: 1`, and counters `0,1,2,3`. Per-core families enumerate cores 0 through 14 for transition, delayed C-state abort, and demotion events. `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6` use filters `occ_sel=1`, `occ_sel=2`, and `occ_sel=3`.

## Control Flow
The file has no executable path. Perf loads the descriptors for Ivy Town, exposes the aliases, and programs the PCU uncore PMU when an event is requested. The per-core entries are explicit rows rather than parameterized aliases, so model changes in core count require separate metadata. The filter-backed occupancy rows demonstrate how the perf event table passes additional PMU filter terms beyond event code and counter selection.

## State And Persistence
Only static alias metadata is persisted. The JSON does not track current power state, residency, or throttling; those values are sampled from hardware counters at runtime. `PerPkg` indicates package-level accounting, which matters because PCU measurements are not per logical CPU. Counter constraints permit all four PCU generic counters, so multiplexing behavior is controlled by perf when users request more events than hardware can count concurrently.

## Dependencies And Integration Points
The file integrates with perf's Ivy Town `pmu-events` table and the kernel PCU uncore PMU driver. It is closely related to CPU idle, P-state, thermal, and power-limit analysis workflows, and its aliases can be referenced from perf metrics or user scripts. The `Filter` field depends on parser support for passing PCU-specific filter syntax through to the PMU event selector.

## Risks And Edge Cases
The per-core rows assume the Ivy Town PCU event layout and core index set; an incorrect row can make one core's state appear under another alias. Frequency and throttling counters are easy to misinterpret without package topology and policy context. Filter typos for occupancy selectors can produce rejected events or valid events that count the wrong C-state bucket. Package-level counters should not be treated as per-thread measurements in metrics.

## Test Signals
Test signals include JSON syntax validation, successful perf event-table generation, `perf list` exposing PCU aliases, and ability to open representative events such as package clockticks, C-state residency, and frequency limit cycles on supported hardware. Runtime sanity checks include higher C-state residency while idle, increased PROCHOT or limit-cause counters under thermal or power stress, and stable parser handling of the `occ_sel` filters.
