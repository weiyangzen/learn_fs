# sources/distributed-fs/ceph-client/tools/perf/util/events_stats.h

Purpose: Defines aggregate counters for perf event stream health and histogram sample accounting.

Important types/APIs: `struct events_stats` tracks lost events, lost samples, BPF-dropped samples, aux lost/partial/collision counts, invalid callchains, counts per perf record type, unknown/unprocessable samples, auxtrace errors, and proc-map timeouts. `struct hists_stats` tracks total/non-filtered periods, latency, sample counts, lost samples, and dropped samples. Declares `events_stats__inc` and `events_stats__fprintf`.

Control flow and state: Header is declarative. State is accumulated by event processing and reporting code; arrays are indexed by perf record and auxtrace error enums.

Dependencies and integration: Includes libperf event ABI, Linux types, stdio, and auxtrace definitions. Embedded in `struct evlist` for stream-wide accounting.

Risks: Array sizes must remain compatible with `PERF_RECORD_HEADER_MAX` and `PERF_AUXTRACE_ERROR_MAX`. Counters distinguish kernel-lost samples from BPF-dropped samples via record misc flags, so processing code must update the correct field.

Test signals: Counter increment/printing tests, lost/lost-samples/BPF-dropped sample classification, auxtrace error indexing, and report summary regression tests.
