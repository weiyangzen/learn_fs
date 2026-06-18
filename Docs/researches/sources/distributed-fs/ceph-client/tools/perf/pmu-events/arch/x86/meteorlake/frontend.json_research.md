# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/frontend.json

## Purpose

This file is the Meteor Lake x86 frontend PMU event catalog for `perf`. It is not executable code; it is a build-time JSON data table consumed by `tools/perf/pmu-events/jevents.py` when generating `pmu-events.c`. The generated tables let users refer to symbolic frontend event names instead of raw event selectors in `perf list`, `perf stat`, metric expressions, and related PMU alias paths.

The file contains 58 event records: 45 for `cpu_core` and 13 for `cpu_atom`. The records describe branch resteers, decode penalties, Decode Stream Buffer and MITE delivery, microcode sequencer activity, instruction-cache stalls, IDQ bubbles, and retired-instruction attribution for frontend-bound behavior. Several logical event names intentionally appear in both core and atom forms or as aliases with different encodings.

## Important schema fields and generated API surface

Each array entry is a PMU event definition. The fields used here line up with `JsonEvent` parsing in `jevents.py`:

- `EventName`: canonical symbolic event name, lowercased by `jevents.py` for generated table storage.
- `EventCode` and `UMask`: raw event selector material used to build perf event config strings.
- `Unit`: maps the event to the PMU namespace, primarily `cpu_core` or `cpu_atom`.
- `Counter`, `CounterMask`, `EdgeDetect`, and `Invert`: constrain valid counters or counting mode for events such as IDQ cycle aliases and stall-period edge detection.
- `MSRIndex` and `MSRValue`: program extra model-specific selectors for PEBS/PDIST style events, especially `FRONTEND_RETIRED.*`.
- `SampleAfterValue`: default sampling period metadata surfaced through perf's generated event aliases.
- `BriefDescription` and `PublicDescription`: short and long help text surfaced by `perf list` and Python/perf utility bindings.

No functions or types are defined locally. The relevant functions are external integration points: `read_json_events`, `JsonEvent`, `preprocess_one_file`, and `process_one_file` in `jevents.py` parse this file and emit generated `struct pmu_table_entry` data; `describe_metricgroup` is unrelated to this file but shares the same generation unit.

## Content and control flow

Build flow is data driven:

1. `jevents.py` walks `tools/perf/pmu-events/arch/x86/meteorlake`.
2. `frontend.json` is accepted because it is a `.json` file and is not `metricgroups.json`.
3. The filename becomes the event topic via `get_topic(item.name)`.
4. Each JSON object is converted into a `JsonEvent`, descriptions are normalized, unit names are mapped to PMU names, event/umask/MSR fields are translated to generated strings, and entries are appended to the pending event table for the Meteor Lake model directory.
5. At build time the generated `pmu-events.c` is compiled into perf; at runtime perf selects the correct CPU table and builds aliases for the matching PMU.

The file's records cluster around these event prefixes:

- `FRONTEND_RETIRED` has 30 records, covering atom attribution categories (`ALL`, `BRANCH_DETECT`, `BRANCH_RESTEER`, `CISC`, `DECODE`, `ICACHE`, `ITLB_MISS`, `OTHER`, `PREDECODE`) and core PDIST/PEBS-like retired-instruction qualifiers (`ANY_DSB_MISS`, `DSB_MISS`, `L1I_MISS`, `L2_MISS`, `STLB_MISS`, latency thresholds from 1 to 512 cycles, unknown branches, ANT branches, and microcode flows).
- `IDQ`, `IDQ_BUBBLES`, and `IDQ_UOPS_NOT_DELIVERED` records expose DSB/MITE/MS uop delivery, frontend bubble slots, zero-uop-delivered cycles, and frontend-ok aliases.
- `ICACHE`, `ICACHE_DATA`, and `ICACHE_TAG` records cover atom line access/miss events plus core data/tag stall cycles and stall periods.
- `BACLEARS`, `DECODE`, `DSB2MITE_SWITCHES`, and `MS_DECODED` describe branch predictor correction, length-changing prefix stalls, microcode sequencer busy cycles, and DSB-to-MITE switch penalties.

## State and persistence behavior

The JSON file has no mutable state. Its persistent effect is indirect: it becomes compiled data inside generated `pmu-events.c` and ultimately `pmu-events.o`/`libperf.a`. Any change to an event name, raw code, unit, counter mask, MSR selector, or description changes the generated perf alias database. Runtime state is held by perf's PMU alias and metric machinery, not by this source file.

The ordering in the JSON is not a runtime state machine, but it is still useful for review because related variants are grouped together. Generated output may be sorted or table-packed by `jevents.py`, so consumers should not depend on source order.

## Dependencies and integration points

Primary dependencies are the perf PMU event generation pipeline:

- `tools/perf/pmu-events/README` defines the JSON contract and explains that `jevents` runs before the perf binary is built.
- `tools/perf/pmu-events/jevents.py` parses event objects, recognizes `EventName`, `BriefDescription`, `PublicDescription`, `Unit`, `EventCode`, `UMask`, `MSRIndex`, `MSRValue`, `Data_LA`, and other schema fields.
- `tools/perf/util/pmu.c`, `tools/perf/util/pmu.h`, `tools/perf/builtin-list.c`, and `tools/perf/util/metricgroup.c` consume the generated PMU tables for listing, alias creation, and metric evaluation.
- The x86 mapfile for Meteor Lake selects the generated table for matching CPU identifiers; this file is useful only when reachable through that mapping.

## Risks and maintenance notes

- `Unit` must match the actual PMU split on hybrid Meteor Lake systems. Mislabeling `cpu_core` versus `cpu_atom` can make events unavailable or incorrectly programmed.
- Reused `EventName` values across core and atom records are intentional but risky: edits must preserve the distinct `Unit`, `EventCode`, `UMask`, and optional MSR fields so perf selects the correct PMU-specific alias.
- `MSRIndex`/`MSRValue` pairs on `FRONTEND_RETIRED.*` records are fragile hardware contracts. A typo can compile cleanly while producing invalid sampling or misleading frontend attribution.
- Alias records such as `IDQ_BUBBLES.CYCLES_0_UOPS_DELIV.CORE` and `IDQ_UOPS_NOT_DELIVERED.CYCLES_0_UOPS_DELIV.CORE` share encodings and descriptions. Updating only one side creates documentation drift.
- Descriptions are user-facing. Typos or ambiguous wording propagate directly to `perf list` output and generated Python dictionaries.

## Test and validation signals

Useful checks are structural and generated-output oriented:

- `jq` parsing should confirm valid JSON and the expected 58 records.
- A perf build that runs `jevents.py` should regenerate `pmu-events.c` without schema errors.
- `perf list` on a matching Meteor Lake system or generated table test should show representative events such as `frontend_retired.dsb_miss`, `idq.dsb_uops`, `icache_data.stalls`, and `baclears.any` under the correct PMU.
- Existing perf tests under `tools/perf/tests/pmu-events.c` and metric parsing tests are the closest automated regression signals for generated PMU event tables.
- Review should compare core/atom encodings against Intel event documentation, especially all `FRONTEND_RETIRED.*` MSR selectors and IDQ counter-mask/invert combinations.
