<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/missed.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/missed.c

Purpose: tests BPF perf/ring/event missed-event accounting behavior under constrained buffers or forced overflow scenarios.

Important APIs and functions: the harness uses the companion skeleton, event-buffer setup, callback counters, and selftest assertions to compare produced events and missed counts.

Control flow: setup loads/attaches the fixture, triggers enough events to exceed the consumer capacity, polls/consumes events, then checks that missed accounting matches expectations.

State and persistence: event buffers, counters, and skeleton BSS/map state are transient. No persistent resources remain after destroy.

Dependencies and integration: depends on perf/ring buffer kernel behavior, generated BPF fixture, and selftest event polling helpers.

Risks and test signals: observed missed count is the signal. Risks are timing sensitivity, CPU count differences, buffer sizing, and event-delivery changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/missed.c -->
