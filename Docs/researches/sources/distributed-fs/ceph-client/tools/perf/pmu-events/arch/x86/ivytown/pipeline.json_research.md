# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/pipeline.json

## Purpose

`pipeline.json` is a perf PMU event-description table for the Intel x86 `ivytown` model family. It contributes the pipeline, execution, branch, retirement, and stall-related event aliases that `tools/perf` exposes through symbolic event names instead of requiring users to type raw event-select encodings.

The file is declarative JSON: it contains 126 event objects. Each object names one hardware performance event or event variant and supplies the encoding fields needed by perf, such as `EventCode`, `UMask`, `CounterMask`, `Invert`, `EdgeDetect`, `AnyThread`, `PEBS`, `Counter`, and `SampleAfterValue`. The event set is focused on pipeline behavior: divide activity, branch execution and misprediction, unhalted clocks, cycle activity stalls, instruction retirement, recovery/machine clears, load blocking, loop stream detector delivery, resource stalls, reservation-station state, dispatch ports, executed uops, issued uops, and retired uops.

## Data Shape And Important Fields

The file is a top-level JSON array of event records. Important record fields are:

- `EventName`: the stable symbolic alias shown to perf users, for example `BR_INST_EXEC.ALL_BRANCHES`, `CYCLE_ACTIVITY.STALLS_TOTAL`, or `UOPS_RETIRED.RETIRE_SLOTS`.
- `EventCode`: the raw event-select value used for programmable counters. Some fixed-counter aliases, such as `INST_RETIRED.ANY`, omit this because they bind to a fixed counter.
- `UMask`: the unit-mask selector that refines the base event.
- `Counter`: counter-placement constraints, commonly `0,1,2,3`, but sometimes a single programmable counter or a fixed counter such as `Fixed counter 0`, `Fixed counter 1`, or `Fixed counter 2`.
- `CounterMask`: the cmask qualifier used for thresholded cycle counting, such as cycles with at least N uops or cycles matching a stall condition.
- `Invert`: requests inverted cmask semantics for events such as no-uop or stall-cycle aliases.
- `EdgeDetect`: counts transitions/occurrences rather than every qualifying cycle for events such as divide count, recovery stall count, machine-clear count, and reservation-station empty-end.
- `AnyThread`: switches selected aliases from thread scope to physical-core scope.
- `PEBS`: marks precise-capable events. `PEBS: "1"` is a precise event and `PEBS: "2"` is treated by the generator as requiring precise sampling.
- `BriefDescription` and `PublicDescription`: short and long user-facing descriptions copied into generated perf metadata.
- `SampleAfterValue`: default sampling period emitted as `period=...` in the generated event string.

The event families and counts in this file are:

| Family | Count | Role |
| --- | ---: | --- |
| `ARITH` | 2 | Divider execution and divider-active cycles. |
| `BR_INST_EXEC` | 13 | Speculative/executed branch categories. |
| `BR_INST_RETIRED` | 9 | Retired branch categories, including PEBS variants. |
| `BR_MISP_EXEC` | 9 | Speculative/executed mispredicted branch categories. |
| `BR_MISP_RETIRED` | 4 | Retired mispredicted branch categories. |
| `CPU_CLK_THREAD_UNHALTED` | 3 | Thread/core reference-clock variants. |
| `CPU_CLK_UNHALTED` | 8 | Fixed and programmable unhalted-clock aliases. |
| `CYCLE_ACTIVITY` | 14 | Pending-load, cache-miss, memory, no-execute, and stall-cycle events. |
| `ILD_STALL` | 2 | Instruction length decoder stalls. |
| `INST_RETIRED` | 3 | Fixed, programmable, and precise instruction-retired aliases. |
| `INT_MISC` | 3 | Recovery-cycle and recovery-stall aliases. |
| `LD_BLOCKS` | 2 | Split-load resource and store-forwarding blocks. |
| `LD_BLOCKS_PARTIAL` | 1 | Partial-address aliasing false dependency. |
| `LOAD_HIT_PRE` | 2 | Loads hitting hardware/software prefetch fill buffers. |
| `LSD` | 3 | Loop stream detector cycles and delivered uops. |
| `MACHINE_CLEARS` | 3 | Machine-clear count, AVX maskmov, and self-modifying-code clears. |
| `MOVE_ELIMINATION` | 2 | Integer move-elimination success/failure. |
| `OTHER_ASSISTS` | 1 | Writeback microcode assists. |
| `RESOURCE_STALLS` | 4 | Allocator, ROB, RS, and store-buffer resource stalls. |
| `ROB_MISC_EVENTS` | 1 | Last branch record inserts. |
| `RS_EVENTS` | 2 | Reservation-station empty cycles and empty-period endings. |
| `UOPS_DISPATCHED_PORT` | 12 | Per-thread and per-core dispatch activity for ports 0 through 5. |
| `UOPS_EXECUTED` | 12 | Core/thread uop execution counts and cycle-threshold aliases. |
| `UOPS_ISSUED` | 6 | RAT-to-RS issue, allocation stalls, and special uop classes. |
| `UOPS_RETIRED` | 5 | Retired uops, retire slots, and no-retirement cycle aliases. |

## Generated APIs And Integration Points

This JSON file is not included directly by C code. It is consumed by the perf PMU event generation pipeline:

1. `tools/perf/pmu-events/Build` includes all JSON files under the selected architecture/model tree as dependencies for generated `pmu-events.c`.
2. `tools/perf/pmu-events/jevents.py` parses each JSON object. Its event conversion lowers `EventName`, maps `BriefDescription`/`PublicDescription` into descriptions, and converts encoding fields into an event string such as `event=0xa3,umask=0x4,cmask=0x4,period=2000003`.
3. Generated `pmu-events.c` exposes `struct pmu_events_table` instances and lookup helpers declared in `tools/perf/pmu-events/pmu-events.h`, including `pmu_events_table__for_each_event`, `pmu_events_table__find_event`, `perf_pmu__find_events_table`, and `find_core_events_table`.
4. Runtime perf code in `tools/perf/util/pmu.c` attaches generated CPU JSON events to a `struct perf_pmu` by iterating the selected table and calling `perf_pmu__new_alias`. After that, command-line parsing can resolve aliases like `uops_retired.retire_slots` to the encoded event string.

The source-tree integration depends on the x86 model mapping outside this file. The `ivytown` directory is selected when the generated map matches the running CPU's architecture/model identifiers. This file therefore only supplies the pipeline-topic event rows; it relies on sibling JSON files and map metadata for complete model coverage.

## Control Flow

There is no imperative control flow inside `pipeline.json`. The relevant control flow is the data flow through the perf build and runtime:

1. Build discovers the JSON as part of the `pmu-events/arch/x86/ivytown` input set.
2. `jevents.py` reads the array, one record at a time.
3. For each record, it builds a `JsonEvent`-style normalized event:
   - `EventName` becomes the generated `struct pmu_event.name`.
   - `EventCode` becomes `event=...` unless another config field is present.
   - `AnyThread`, `CounterMask`, `EdgeDetect`, `Invert`, `SampleAfterValue`, and `UMask` append `any=`, `cmask=`, `edge=`, `inv=`, `period=`, and `umask=` fragments when present and nonzero.
   - `PEBS` augments descriptions so precise sampling requirements are visible to users.
4. The generated table is compiled into perf.
5. At runtime, perf locates the CPU event table for the active PMU and registers these entries as aliases.
6. User-facing commands such as `perf list`, `perf stat -e <alias>`, and `perf record -e <alias>` can display or open these events, subject to kernel PMU support and counter constraints.

## State And Persistence Behavior

The JSON file is persistent source metadata. It does not maintain runtime state and does not mutate repository files by itself.

Generated state appears during builds:

- `pmu-events/pmu-events.c` is generated or copied into the build output.
- `pmu-events/metric_test.log`, `empty-pmu-events.log`, and generated test files may be created under the perf output directory.
- Generated event tables embed the normalized values derived from this JSON, so changing a field here changes compiled perf behavior after regeneration.

Runtime state is managed elsewhere by perf and the kernel PMU subsystem. This file only influences alias resolution and event attribute construction.

## Dependencies

Direct dependencies are schema-level rather than import-level:

- The perf PMU JSON schema recognized by `jevents.py`.
- x86 Ivytown hardware event definitions and counter semantics.
- `pmu-events/Build`, which wires JSON inputs to generated C output.
- `pmu-events/pmu-events.h`, which declares the generated event-table API.
- `util/pmu.c`, which consumes generated tables and creates perf aliases.
- Kernel PMU support for the encoded events, fixed counters, PEBS, any-thread counting, edge detection, inversion, and cmask behavior.

The file also depends on consistency with sibling Ivytown event-category JSON files and x86 map metadata so the complete CPU model table is selected correctly.

## Risks And Maintenance Concerns

- Encoding mistakes are silent until runtime. A wrong `EventCode`, `UMask`, `CounterMask`, `Invert`, or `EdgeDetect` can produce valid-looking aliases that count the wrong hardware condition.
- Counter constraints matter. Rows that require fixed counters or a specific programmable counter can fail to schedule, multiplex unexpectedly, or conflict with other events if the `Counter` field is inaccurate.
- Some aliases are semantically close but not identical. For example, executed/speculative branch events differ from retired branch events, and per-thread aliases differ from `AnyThread` core-scope aliases. Documentation drift can mislead users even when encodings are valid.
- PEBS precision flags affect sampling expectations. Incorrect `PEBS` values can cause perf to advertise precise events incorrectly or omit precision requirements from descriptions.
- `SampleAfterValue` defaults affect profiling overhead and signal density. Extremely low or high periods would alter user experience for `perf record`.
- JSON syntax or schema mistakes break `jevents.py` generation. Because this is data consumed at build time, schema regressions surface as build failures or missing aliases rather than compiler errors in this file.
- Hardware documentation and errata can change recommended aliases. This table should remain aligned with Intel Ivytown PMU documentation and any perf-side compatibility decisions.

## Test Signals

Useful validation signals for changes to this file include:

- `jq` parses the file and reports the expected array size: this source currently contains 126 event records.
- `jq -r 'map(keys[]) | unique[]'` shows only schema keys recognized by the perf event generator for this file: `AnyThread`, `BriefDescription`, `Counter`, `CounterMask`, `EdgeDetect`, `EventCode`, `EventName`, `Invert`, `PEBS`, `PublicDescription`, `SampleAfterValue`, and `UMask`.
- Building `tools/perf` regenerates `pmu-events.c` without `jevents.py` errors.
- The perf PMU event tests wired by `pmu-events/Build`, including metric parser tests and empty-event generation comparison, still pass.
- `perf list` on an Ivytown-mapped build includes representative aliases such as `arith.fpu_div`, `cycle_activity.stalls_total`, `uops_dispatched_port.port_0`, and `uops_retired.retire_slots`.
- Runtime smoke tests on suitable hardware can open representative event classes with `perf stat -e`, especially fixed-counter aliases, PEBS aliases, cmask/invert cycle aliases, and AnyThread variants.

## Research Notes

This file is source-tree-aligned model metadata, not Ceph-specific distributed-filesystem logic. It lives under the vendored or mirrored Linux perf tooling in the Ceph client source tree. Its main engineering importance is that small data edits have broad user-facing effects in perf alias lookup and hardware counter programming.
