
# sources/distributed-fs/ceph-client/tools/perf/util/metricgroup.h

Purpose: declares the public metric-group interface and the in-memory data structures that connect parsed `evsel`s to metric expressions for perf stat output.

Important APIs/types/functions: `struct metric_event` is an rbtree node keyed by `evsel`, with `is_default` and a `head` list of `metric_expr`. `struct metric_ref` stores referenced metric name/expression pairs for recursive expression evaluation. `struct metric_expr` stores the expression string, display name, optional threshold, scale/unit, default group name, null-terminated event pointer array, null-terminated referenced metric array, and runtime value substituted for `?`. Declared functions cover metric lookup, parsing metric groups into an evlist, test parsing, iteration over metrics, presence checks, topdown max-level discovery, runtime parameter hook, rblist lifecycle, and cgroup/copy support.

Control flow: this header has no executable flow, but its ownership rules drive `metricgroup.c`: the evlist owns a metric-events rblist, each rblist node owns its expression list, and each expression points at evsels that must remain valid for the evlist lifetime.

State and persistence: all types describe transient in-memory state. String fields often point to generated PMU metric table storage, while `metric_name`, `metric_refs`, and `metric_events` may be heap-owned by the metricgroup layer. No on-disk state is defined.

Dependencies: includes Linux list/rbtree primitives, booleans, and generated `pmu-events.h`. It forward-declares perf core types (`evlist`, `evsel`, `rblist`, `cgroup`) to keep callers decoupled from implementation headers.

Integration points: used by evlist/stat code that initializes metric rblists, looks up metric expressions by evsel, parses user metric requests, and clones metric metadata across cgroup evlists.

Risks: the structures expose ownership-sensitive pointers rather than opaque handles, so callers must preserve evsel lifetime and use the rblist lifecycle helpers. Typo risk exists in user-visible comments (`meric`). Test signals are compile coverage, metricgroup unit tests, and memory/leak checks around metric parse/free/copy cycles.
