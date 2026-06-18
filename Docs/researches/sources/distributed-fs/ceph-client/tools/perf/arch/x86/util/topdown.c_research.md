# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/topdown.c

Purpose: implements x86 support for Intel topdown metric events and synthesized slots insertion.

Important APIs/types/functions: `topdown_sys_has_perf_metrics()` detects core PMU support for `slots`. `arch_is_topdown_slots()` recognizes the raw slots encoding. `arch_is_topdown_metrics()` recognizes PMU type `PERF_TYPE_RAW` with `PERF_SAMPLE_READ` sampling. `arch_topdown_sample_read()` sets grouped read format for sampled metric leaders. `topdown_insert_slots_event()` creates and inserts the `slots` event before a metric event.

Control flow: capability detection is cached after the first raw PMU lookup. Slots recognition compares event type and config to `TOPDOWN_SLOTS`. Inserting slots allocates an evsel from the string `"slots"`, assigns index, inserts before the metric event, and increments the metric event index to preserve ordering.

State and persistence: two static booleans cache feature detection. The evlist is mutated by inserting an evsel. No files are written.

Dependencies and integration: depends on perf PMU discovery, evlist/evsel list management, parse-events through `evsel__newtp_idx("slots", idx)`, and generic topdown interfaces in `util/topdown.h`.

Risks: assumes raw PMU type represents the core PMU and `slots` event availability implies perf metrics. Failure to allocate/parse slots returns `-ENOMEM`. Index mutation must match caller expectations for metric grouping.

Test signals: `perf stat` topdown metrics on Intel systems, missing `slots` event behavior, sampled topdown metrics requiring `PERF_FORMAT_GROUP`, and event list ordering tests.
