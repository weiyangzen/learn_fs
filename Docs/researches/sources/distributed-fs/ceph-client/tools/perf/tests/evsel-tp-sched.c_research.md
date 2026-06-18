# sources/distributed-fs/ceph-client/tools/perf/tests/evsel-tp-sched.c

Purpose: `evsel-tp-sched.c` validates parsed field metadata for the `sched:sched_switch` tracepoint.

Important APIs and state: `evsel__test_field` looks up a field by name in the tracepoint format and checks size and signedness. `test__perf_evsel__tp_sched_test` opens the sched tracepoint evsel and validates key fields. The suite object is `suite__perf_evsel__tp_sched_test`.

Control flow: the test parses or creates the sched switch tracepoint evsel, verifies it has trace-event format data, then checks fields such as previous and next comm, pid, prio, and state for expected sizes/sign flags.

State and persistence: all state is evsel/trace-event metadata allocated during the test and cleaned with normal suite ownership. No files are written.

Dependencies, integration, risks, and tests: it depends on libtraceevent, sched tracepoint format availability, and kernel field definitions. The suite is compiled only when traceevent support is available. Risks include kernel tracepoint format changes and unavailable tracing files. Test signals are exact field lookup, size, and signedness matches.
