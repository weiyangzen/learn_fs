<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_key.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_key.c

Purpose: validates map key lookup behavior from BPF programs, especially helper semantics around locating current keys and reporting expected values.

Important APIs and functions: the harness loads the companion skeleton/object, initializes maps or inputs, runs BPF programs through attach or test-run paths, and reads BSS/map outputs for pass/fail.

Control flow: setup creates the BPF fixture, triggers the selected program path, and checks that lookup-key results match expected keys and error cases. Cleanup destroys skeleton state.

State and persistence: state is transient map content and BSS status fields. No state persists after the object closes.

Dependencies and integration: depends on the BPF fixture for lookup-key helper coverage, libbpf skeleton APIs, and `test_progs.h` assertions.

Risks and test signals: signals are exact returned keys/status values. Risks include changes to helper availability, map type behavior, or BPF-side fixture layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_key.c -->
