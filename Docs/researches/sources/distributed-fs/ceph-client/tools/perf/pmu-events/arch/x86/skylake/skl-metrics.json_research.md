
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/skl-metrics.json

## Purpose

This file defines the Skylake client metric catalog used by Linux perf for symbolic `perf stat -M ...` style analysis. It is a JSON array of 222 metric objects. Every object has `MetricName`, `MetricExpr`, `MetricGroup`, and `BriefDescription`; optional fields add display units, public descriptions, metric constraints, threshold expressions, and grouping suppressors.

The catalog covers package and core C-state residency, uncore frequency, SMI accounting, TSX transaction ratios, and a large Intel topdown microarchitecture-analysis hierarchy. The dominant metric namespace is `tma_*`, with level/group tags such as `TopdownL1`, `TopdownL2`, `TopdownL3`, `TopdownL4`, `TopdownL5`, `TopdownL6`, `tma_L*_group`, and domain tags including `Backend`, `Frontend`, `BadSpec`, `Retire`, `Mem`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Flops`, `Pipeline`, `PortsUtil`, `Power`, `Summary`, `SMT`, `OS`, and `transaction`.

## Important Schema Fields and APIs

The main external API is the perf PMU JSON schema parsed by `tools/perf/pmu-events/jevents.py`. For metric rows, `jevents.py` reads `MetricName`, `MetricGroup`, `MetricgroupNoGroup`, `MetricConstraint`, `MetricExpr`, `MetricThreshold`, `BriefDescription`, `PublicDescription`, and `ScaleUnit`. `MetricExpr` is parsed through `metric.ParsePerfJson(...).Simplify()`, so formulas must use perf's metric-expression grammar and event aliases visible to the selected CPU model.

Important fields:

- `MetricName`: public symbolic metric identifier, for example `tma_backend_bound`, `tma_info_thread_ipc`, `tma_mem_latency`, `UNCORE_FREQ`, and `tsx_transactional_cycles`.
- `MetricExpr`: expression over raw events, other metrics, constants, helper functions, and scaling terms. This is the behavioral core of the file.
- `MetricGroup`: semicolon-delimited group membership used by perf list/stat filtering and topdown presentation.
- `ScaleUnit`: optional rendering unit such as percentages, cycles, bandwidth, IPC-like ratios, or time/power units.
- `MetricConstraint`: optional grouping/scheduling constraint. Present on 53 rows and used by `jevents.py` as `event_grouping`.
- `MetricThreshold`: optional display threshold string. Present on 139 rows; unlike `MetricExpr`, `jevents.py` keeps thresholds as strings because boolean operator precedence is not parsed the same way.
- `MetricgroupNoGroup`: optional flag present on 12 rows to avoid automatic grouping behavior.

## Control Flow and Data Flow

There is no imperative control flow in this file. Build-time control flow is:

1. The perf build scans `tools/perf/pmu-events/arch/x86/skylake/` as the model directory selected by `arch/x86/mapfile.csv`.
2. `jevents.py` loads this JSON array, validates each object as either an event or a metric row, and parses each `MetricExpr`.
3. The generator emits C tables in generated `pmu-events.c`, with metric names, expressions, groups, descriptions, units, and constraints embedded in `struct pmu_event`/metric metadata.
4. At runtime, perf matches the running CPU to the Skylake map entry, exposes the metric aliases, and evaluates formulas by scheduling the referenced PMU events.

Data dependencies flow from metric names to lower-level event names in neighboring Skylake JSON files such as `cache.json`, `frontend.json`, `memory.json`, `pipeline.json`, `virtual-memory.json`, and uncore event files. Some metrics also depend on common perf aliases, fixed counters, topdown slot events, package C-state events, RAPL/power events, and synthetic perf helper terms.

## State and Persistence

The file is static source metadata. Its only persistent effect is through generated perf build artifacts: generated `pmu-events.c`, compiled `pmu-events.o`, and the resulting perf binary's embedded PMU tables. It does not store runtime state. Runtime metric values are computed from current PMU counter samples; no sampled state is persisted back into this JSON.

## Dependencies and Integration Points

This file integrates with:

- `tools/perf/pmu-events/Build`, which regenerates Intel metric files and then drives `jevents.py`.
- `tools/perf/pmu-events/jevents.py`, which parses the JSON and emits generated C.
- `tools/perf/pmu-events/metric.py` and `metric_test.py`, which parse and test metric-expression syntax.
- `tools/perf/builtin-list.c`, which can print metric metadata back out for `perf list` JSON/text views.
- The x86 mapfile, which controls when the Skylake directory is selected.
- Adjacent raw event JSON files whose `EventName` values are referenced by `MetricExpr`.

Because this is a client Skylake metric set, it should not be mixed with Skylake-X server metrics unless the mapfile explicitly maps a CPU model to that directory. The formulas encode microarchitecture-specific topdown assumptions, counter availability, and event meanings.

## Risks

The highest risk is expression drift: a renamed, removed, or architecture-mismatched raw event breaks metric evaluation even when the JSON remains syntactically valid. Metric formulas are also sensitive to counter multiplexing, SMT assumptions, frequency scaling, offcore response encodings, and kernel/perf support for fixed counters and topdown slots.

Threshold strings are not parsed by the same path as `MetricExpr`, so syntax problems may evade expression-parser coverage. `MetricConstraint` rows can reduce schedulability; incorrect constraints may produce inaccurate multiplexed values or prevent metric groups from running together. Scale-unit mistakes are presentation bugs but can lead users to misread ratios as percentages or bandwidth as counts.

## Test Signals

Useful validation signals include `jq` parsing, `metric_test.py` coverage for expression grammar, perf build regeneration of `pmu-events.c`, and perf tests under `tools/perf/tests/pmu-events.c` and `tools/perf/tests/parse-metric.c`. Runtime smoke tests should include `perf list --json` for representative `MetricName` values and `perf stat -M` for topdown, memory, power, TSX, and SMI metrics on actual Skylake client hardware or a compatible perf test fixture.
