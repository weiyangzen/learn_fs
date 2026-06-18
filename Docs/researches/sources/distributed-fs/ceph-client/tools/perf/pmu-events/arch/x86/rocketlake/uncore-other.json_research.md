# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/uncore-other.json

## Purpose
This JSON file defines a single Rocket Lake uncore miscellaneous event alias, `UNC_CLOCK.SOCKET`. It gives perf and Rocket Lake metrics a symbolic package-level clock source for uncore/socket timing calculations.

## Data shape and important fields
The file is a JSON array with 1 object. The observed keys are `EventName`, `BriefDescription`, `EventCode`, `Counter`, `Unit`, and `PerPkg`.

The entry uses `EventName` `UNC_CLOCK.SOCKET`, `BriefDescription` `Uncore clockticks`, `EventCode` `0x00`, `Counter` `0,1,2,3`, `Unit` `cbox_0`, and `PerPkg` `1`. The `Unit` ties the event to a C-box uncore PMU instance; the `PerPkg` flag tells perf that aggregation is package-scoped.

## Control flow and integration
The JSON is parsed by `jevents.py` and emitted as one generated `pmu_event`. Runtime perf exposes the alias and programs the matching `cbox_0` uncore PMU. `rkl-metrics.json` references `UNC_CLOCK.SOCKET` for system/socket clock metrics such as socket clocks and uncore-frequency calculations.

There is no local control flow, but the event is a dependency for formula evaluation where uncore clock ticks are normalized by duration, die count, or other system-level denominators.

## State, persistence, and dependencies
The file is static and persists only through generated perf event tables. Runtime state lives in the uncore C-box counter. The definition depends on the kernel exposing a compatible `cbox_0` PMU and on perf's unit matching and package aggregation behavior.

## Risks
This file is small, but it is a single point of failure for metrics that derive uncore/socket frequency or clock totals. A wrong unit name can make the alias disappear even if the event encoding is otherwise correct. A wrong aggregation flag can skew socket-level metrics on multi-core or multi-socket systems.

Because it exposes only `cbox_0`, systems with different C-box naming or topology may need wildcard behavior from perf's PMU matching. If matching is too strict, the metric dependency may not resolve.

## Test signals
Useful checks are `jq empty uncore-other.json`, generated table inspection for `UNC_CLOCK.SOCKET`, and `perf list`/`perf stat` smoke tests against the C-box uncore PMU. Metric validation should run formulas in `rkl-metrics.json` that reference `UNC_CLOCK.SOCKET`, especially uncore frequency and socket clock metrics.
