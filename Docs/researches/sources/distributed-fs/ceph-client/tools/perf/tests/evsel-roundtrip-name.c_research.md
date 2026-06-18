# sources/distributed-fs/ceph-client/tools/perf/tests/evsel-roundtrip-name.c

Purpose: `evsel-roundtrip-name.c` validates that parsed events round-trip back to their canonical evsel names.

Important APIs and state: cache-name tests use `__evsel__hw_cache_type_op_res_name`, `parse_event`, and `evsel__name_is`. Generic name-array tests parse lists of event names and compare every resulting evsel. The suite is `"Roundtrip evsel->name"`.

Control flow: cache testing iterates every hardware cache type, op, and result, skipping invalid cache operations and parse failures for unsupported PMUs. Name-array testing parses known hardware/software/tracepoint names, then verifies each evsel reports the same name expected from the input array.

State and persistence: evlists are allocated and deleted per case. No external state persists.

Dependencies, integration, risks, and tests: it depends on parser support, PMU availability, and canonical name formatting. Risks include platform-specific unsupported events and strict string matching when display names intentionally change. Test signals are no mismatches for supported parsed events and graceful skips for unsupported cache events.
