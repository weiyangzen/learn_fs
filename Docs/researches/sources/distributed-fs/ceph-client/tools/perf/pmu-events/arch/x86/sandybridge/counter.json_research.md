## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/counter.json

### Purpose
`counter.json` declares the Sandy Bridge PMU counter inventory. It is a small metadata file that tells perf the `core` PMU has four generic programmable counters and three fixed counters.

### Important APIs, Types, And Data Fields
The file is a JSON array of three objects using the counter metadata schema:

- `Unit: "core"` identifies the PMU unit.
- `CountersNumGeneric: "4"` records the number of programmable core counters.
- `CountersNumFixed: "3"` records the number of fixed counters.

There are no event names, formulas, functions, or classes in this file. Its API is the counter-capability record consumed by the PMU events tooling.

### Control Flow And Data Flow
During PMU table generation, perf reads this file alongside the event tables. The counter counts inform event scheduling and metadata display. Runtime perf can then understand why events in sibling files refer to programmable counters `0,1,2,3` and fixed counters such as `Fixed counter 0`, `Fixed counter 1`, and `Fixed counter 2` in `pipeline.json`.

### State And Persistence
The file persists static hardware capability metadata only. There is no mutable state. Build output may embed these counts in generated perf data tables.

### Dependencies And Integration Points
The values must match Sandy Bridge PMU hardware. The file integrates with all sibling event files by giving context for their `Counter` fields, especially `pipeline.json` fixed-counter events like `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC`.

### Risks
Incorrect generic or fixed counter counts can cause perf to schedule impossible events, reject valid events, or present misleading capability information. Because this file is tiny, formatting or schema errors are also high-impact: a malformed counter table can break PMU table generation for the whole Sandy Bridge event set.

### Test Signals
Validation should parse the JSON, check that the `core` unit has four generic and three fixed counters, verify generated perf metadata, and run `perf list`/event scheduling tests that include both programmable and fixed events.
