<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/pmu-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/pmu-events.h
Purpose: Declares perf's generated PMU event and metric table interface. It is the C contract consumed by generated code from `jevents.py` and by perf runtime callers.

Important APIs/types/functions: Defines `enum aggr_mode_class`, `enum metric_event_groups`, `struct pmu_event`, `struct pmu_metric`, opaque table structs, iterator callback typedefs, lookup-not-found constants, event/metric iteration and find APIs, table lookup APIs for current/default/core/sys PMUs, and `describe_metricgroup`.

Control flow: This header has no executable control flow; it establishes function signatures that generated C implements. Iterator callbacks return 0 to continue or non-zero to terminate, while special not-found constants allow table-local misses to continue across other tables.

State and persistence: No state is stored here. The struct field layout is persistent ABI-like build contract between generated compact records and C decompression routines.

Dependencies and integration points: Includes `stdbool.h` and `stddef.h` and forward-declares `struct perf_pmu`. The generated C includes this header and fills these structures; perf list/stat/metric code calls the declared functions.

Risks: Field-order drift between `struct pmu_event`/`struct pmu_metric` and `jevents.py`'s `_json_event_attributes`/`_json_metric_attributes` would corrupt decompression. Enum value changes must stay synchronized with JSON conversion in `jevents.py` and grouping behavior in perf.

Test signals: Build failures catch signature mismatches; runtime PMU event tests and `perf list`/`perf stat -M` catch lookup and decompression mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/pmu-events.h -->
