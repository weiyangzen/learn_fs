# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-io.json

## Purpose

This file is the Skylake Xeon x86 perf PMU event topic table for IIO, the Integrated I/O uncore block. It gives perf symbolic aliases for PCIe and VT-d traffic events so users can request names such as `UNC_IIO_DATA_REQ_OF_CPU.MEM_READ.PART0`, `UNC_IIO_COMP_BUF_OCCUPANCY.CMPD.PART3`, or the derived metrics `LLC_MISSES.PCIE_READ` and `LLC_MISSES.PCIE_WRITE` instead of manually assembling raw uncore event encodings.

The table is data, not executable code. Its behavior is realized by the perf PMU event generator in `tools/perf/pmu-events/jevents.py`, which reads JSON objects, converts them into generated C `struct pmu_event` and `struct pmu_metric` tables, and links those tables into perf. The topic is `uncore-io` by file name, and all entries use `Unit: "IIO"`, which `jevents.py` maps to the uncore PMU name `uncore_iio`.

## Schema and Important Fields

The source is a JSON array with 394 event objects and 394 unique `EventName` values. Every object has `BriefDescription`, `Counter`, `EventName`, `PerPkg`, and `Unit`. Most objects also carry raw hardware selector fields:

- `EventCode`: main event selector. One placeholder-style entry, `UNC_IIO_NOTHING`, omits this field; `jevents.py` defaults missing `EventCode` to zero.
- `UMask`: unit mask, present on 387 entries.
- `FCMask`: flow-control mask, present on 367 entries and emitted as `fc_mask=...`.
- `PortMask`: part/port selector, present on 362 entries and emitted by `jevents.py` as `ch_mask=...`.
- `Filter`: additional raw filter string; used only by the two derived PCIe read/write metrics here.
- `Counter`: allowed IIO counter lanes, commonly `0,1`, `2,3`, or `0,1,2,3`.
- `PerPkg`: always `1`, so generated events set package-level aggregation behavior.
- `Deprecated`: present on 175 entries, mostly older payload/transaction naming that points to newer `DATA_REQ_*` events.
- `Experimental`: present on 309 entries, marking most IIO aliases as less stable.
- `PublicDescription`: present on 192 entries and used as long description output.
- `MetricExpr`, `MetricName`, and `ScaleUnit`: present only on `LLC_MISSES.PCIE_READ` and `LLC_MISSES.PCIE_WRITE`; each sums the four matching `UNC_IIO_DATA_REQ_OF_CPU.MEM_*` part events and reports 4-byte scaling.

The event family layout is regular. Major groups include completion-buffer insert and occupancy events, CPU-to-device and device-to-CPU data request counters, payload byte aliases, transaction counters, transaction-request counters, mask-match helpers, link retry/error counters, VT-d access/occupancy counters, and the IIO clock tick event.

## Integration Points

Perf discovers this file through `tools/perf/pmu-events/arch/x86/skylakex/`, which is selected by x86 `mapfile.csv` entries for the Skylake Xeon model family. During the build, `jevents.py` recursively reads JSON event files under the architecture/model directory, including this topic file, and emits generated PMU tables into `pmu-events.c`.

`jevents.py` is the main consumer:

- `JsonEvent.__init__` lowercases `EventName`, normalizes descriptions, maps `Unit: "IIO"` to `uncore_iio`, carries `PerPkg` and `Deprecated`, and parses `MetricExpr` through the perf metric parser.
- The raw event string is built from `event=...` plus translated fields such as `PortMask -> ch_mask=`, `FCMask -> fc_mask=`, and `UMask -> umask=`.
- `read_json_events()` assigns the topic, collects metric definitions, and rewrites metrics in terms of other metrics where possible.
- `add_events_table_entries()` adds entries with names to the event table and entries with metric names to the metric table.

At runtime, perf looks up generated tables through the APIs declared in `pmu-events.h`, including `perf_pmu__find_events_table()`, `pmu_events_table__for_each_event()`, `pmu_events_table__find_event()`, `pmu_metrics_table__for_each_metric()`, and `pmu_metrics_table__find_metric()`. User-facing output paths include `perf list`, whose JSON printer emits `Deprecated`, `BriefDescription`, `PublicDescription`, `MetricName`, `MetricExpr`, `ScaleUnit`, and `Unit` fields.

## Control Flow

There is no local control flow in the JSON itself. The effective flow is:

1. Build scripts run `jevents.py` for the x86 PMU event tree.
2. The JSON parser instantiates a `JsonEvent` for each object in this file.
3. `JsonEvent` constructs a generated perf event encoding from `EventCode`, `UMask`, `FCMask`, `PortMask`, `Filter`, and related fields.
4. Named events are appended to the pending event table; the two named metrics are appended to the pending metric table.
5. Pending event and metric tables are sorted and emitted as compact generated C data.
6. Perf links the generated data, matches it to the active CPU/PMU at runtime, and exposes aliases and metrics through `perf stat`, `perf list`, and metric lookup paths.

## State and Persistence Behavior

The file is persistent static metadata. It does not write state, open files, allocate runtime resources, or maintain counters itself. Persistence happens indirectly when the build converts it into generated C tables and compiled perf objects. Runtime counter state lives in the kernel PMU subsystem and the uncore IIO hardware counters; this file only defines how perf names and encodes those counters.

Because every entry is `PerPkg: "1"`, consumers should expect package-scoped readings. Multi-socket systems and systems with multiple IIO instances need careful interpretation of per-package aliases and source counts. The `Counter` field constrains which hardware counter lanes can schedule each event, so metric grouping can fail or multiplex if a command requests incompatible IIO events at the same time.

## Dependencies

Direct data dependencies are the perf PMU JSON schema and the Skylake Xeon PMU directory layout. Build-time dependencies include Python JSON parsing, `tools/perf/pmu-events/metric.py` for `MetricExpr`, and the generated C declarations in `pmu-events.h`.

Hardware dependencies are Intel Skylake Xeon IIO uncore PMUs with the event encodings represented here. The part selectors (`PART0` to `PART3`), VT-d selectors (`VTD0`, `VTD1`), and port masks encode topology assumptions about PCIe lanes, slots, risers, and IIO partitions. Several public descriptions explicitly tie parts to PCIe slot/lane placement.

## Risks and Edge Cases

The main correctness risk is metadata drift from Intel hardware documentation. A wrong `EventCode`, `UMask`, `FCMask`, `PortMask`, or `Counter` silently creates a valid-looking perf alias that counts the wrong signal or cannot be scheduled.

The `PortMask` translation is easy to misread: `jevents.py` emits it as `ch_mask=...`, while this file also has two explicit `Filter: "ch_mask=0x1f"` values. The two derived PCIe read/write metrics therefore combine generated `ch_mask` from `PortMask` with an explicit filter. Any future edits need to preserve the intended distinction between part selection and broad channel filtering.

`UNC_IIO_NOTHING` lacks `EventCode`, so it is encoded as event zero by generator default. That is probably deliberate as an experimental placeholder, but it should not be treated like a normal documented counter.

Most aliases are marked experimental, and many are deprecated. Tooling that filters or hides these fields can materially change what users see in `perf list`. Deprecated payload and transaction aliases remain in the file for compatibility, but their descriptions point users to newer `UNC_IIO_DATA_REQ_*` names.

The two `LLC_MISSES.PCIE_*` metric names are semantically surprising because they are derived from IIO data-request events rather than LLC core events. Users may assume cache-miss semantics unless descriptions and units are shown.

## Test Signals

Useful validation for this file includes:

- JSON parse validity and array shape: `jq -e 'type == "array"'`.
- Required field checks for `EventName`, `BriefDescription`, `Counter`, `Unit`, and `PerPkg`.
- Uniqueness of `EventName`; the current file has 394 unique names across 394 entries.
- Expected anomaly checks: exactly one missing `EventCode` (`UNC_IIO_NOTHING`), two metric entries, two scale-unit entries, 309 experimental entries, and 175 deprecated entries.
- Generator coverage: building perf with jevents enabled should produce uncore IIO aliases and metric table entries without parse failures.
- Runtime/listing smoke tests on matching hardware: `perf list --json` should expose the aliases with `Unit`/PMU information, descriptions, deprecated flags, and metric expressions.
- Existing perf PMU event tests in `tools/perf/tests/pmu-events.c` exercise generated table iteration and comparisons; similar expectations could be added for uncore IIO if this file is changed.
