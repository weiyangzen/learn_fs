# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/transaction.json

## Purpose
This JSON file is a metric table for `cf_z13` under the `s390` perf PMU event tree. It provides derived perf metrics for s390 cf_z13; formulas reference event names and use `has_event(...)` guards. It contains 15 entries and belongs to the `transaction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, MetricExpr, MetricName`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, memp, finite_cpi.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `MetricExpr` is parsed by `metric.py` and may reference raw event names plus helper predicates such as `has_event(...)`.

## Content Notes
- The transaction file contains derived metrics such as transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, each represented by `MetricName` plus `MetricExpr` rather than raw `EventCode`.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is metric parsing: expressions are simplified during generation and evaluated later against runtime counter values only when their dependency events exist.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `tools/perf/pmu-events/metric.py` parses `MetricExpr`; formulas depend on referenced event aliases being present in the same CPU table

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Metric expressions are brittle against event renames; `has_event(...)` guards avoid lookup failures but can yield zero-valued metrics when dependency events are absent.
- Several formulas divide by instruction or miss counters; perf metric evaluation must handle zero denominators as defined by the metric parser/runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Run `tools/perf/tests/parse-metric` or metric parser coverage for each `MetricExpr`, including `has_event(...)` fallback behavior.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
