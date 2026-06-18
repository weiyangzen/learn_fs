# sources/distributed-fs/ceph-client/tools/perf/util/python.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/python.c` implements the `perf` Python extension module. It exposes perf events, CPU/thread maps, PMUs, counter values, event selectors, event lists, event parsing, metric parsing, metric metadata, and tracepoint lookup to Python scripts.

## Important APIs, Types, and Functions

The module initializer is `PyInit_perf`. Event wrapper state is `struct pyrf_event`, with Python types for mmap, task, comm, throttle, lost, read, sample, and context-switch events. Map wrappers are `struct pyrf_cpu_map` and `struct pyrf_thread_map`. PMU wrappers are `struct pyrf_pmu` and `struct pyrf_pmu_iterator`. Counter values use `struct pyrf_counts_values`. Event selector/list wrappers are `struct pyrf_evsel` and `struct pyrf_evlist`.

Important methods include event `repr` functions, tracepoint field dynamic lookup for sample events when libtraceevent is available, CPU/thread sequence operations, PMU iteration and event enumeration, `evsel.open`, `evsel.cpus`, `evsel.threads`, `evsel.read`, `evlist.all_cpus`, `evlist.metrics`, `evlist.compute_metric`, `evlist.mmap`, `evlist.poll`, `evlist.get_pollfd`, `evlist.add`, `evlist.read_on_cpu`, `evlist.open`, `evlist.close`, `evlist.config`, `evlist.disable`, `evlist.enable`, module functions `tracepoint`, `parse_events`, `parse_metrics`, `metrics`, and `pmus`.

## Control Flow

Module initialization creates the Python module, readies all Python types, sets `page_size`, registers the exposed classes, and inserts `PERF_*` constants into the module dictionary. Event reading flows through `evlist.read_on_cpu`: find the mmap for a CPU, initialize mmap read, create a Python event object from the raw event, map the event to an evsel, consume the mmap entry, parse sample data into `perf_sample`, and return the event object.

`evsel` construction builds a `perf_event_attr` from Python keyword arguments, normalizes sample frequency/period union fields, assigns bitfields, and initializes a perf evsel. `evlist` construction wraps CPU/thread maps; adding an evsel inserts its embedded C evsel into the list. Default config builds a `record_opts` structure and calls `evlist__config`.

Metric parsing builds a temporary C evlist with `metricgroup__parse_groups`, clones it into Python-owned evlist/evsel objects, and fixes group leaders, metric leaders, and metric event references to point at cloned evsels. Metric computation finds the requested metric expression for a CPU/thread, reads backing counter deltas, scales by enabled/running time, evaluates the expression, and returns a float.

With libtraceevent, sample-event attribute lookup first checks tracepoint format fields and decodes numeric, string, dynamic array, and byte-array fields from raw sample data. If no tracepoint field matches, generic Python attribute lookup is used.

## State and Persistence Behavior

Python objects own or reference embedded perf structures. CPU and thread maps are reference-counted with `perf_cpu_map__get/put` and `perf_thread_map__put`. PMU objects reference globally owned PMUs and do not free them. `pyrf_event` stores a bounded copy of `union perf_event` plus parsed `perf_sample`; sample events free lazily allocated sample internals on deallocation. `evsel.read` persists previous raw counts in `prev_raw_counts` so it can return deltas across calls. No file-backed persistence is written, but opening/mmaping evlists creates perf event fds and mmaps.

## Dependencies and Integration Points

The module integrates Python C API, perf evlist/evsel/counts/mmap/cpumap/thread-map APIs, traceevent decoding, PMU scanning, metricgroup and expression parsing, record configuration defaults, and perf event parsing. It is consumed by Python perf scripting and tests that import `perf`.

## Risks and Edge Cases

`pyrf_event__new` copies raw events into a fixed `union perf_event` and rejects larger events, with a FIXME noting dynamic parsing would be better. Several error paths return without decrementing newly allocated Python objects, especially after type or argument validation failures. `pyrf_counts_values_set_values` does not cap list length against the backing fixed values array. `evlist.add` increments the Python evsel reference and embeds the evsel into the evlist, making ownership/lifetime subtle. `pyrf_evlist__item` returns a borrowed container object constructed from an embedded evsel address assumption. Tracepoint dynamic field access mutates `field->flags` by clearing `TEP_FIELD_IS_STRING` for non-printable arrays. The `overwrite` argument to `evlist.mmap` is parsed but not used. Import initialization returns a partially created module on setup failure, then sets ImportError only if a Python error is already pending.

## Test Signals

Tests should import the extension, validate constants and type registration, construct CPU/thread maps and sequence access, create/open/read evsels where permissions allow, parse simple events and metrics, clone metric evlists and compute metric deltas with mocked counts, exercise `read_on_cpu` with sample events, decode tracepoint dynamic string and byte-array fields, iterate PMUs and PMU events, and run reference-count/leak checks around evlist/evsel ownership.
