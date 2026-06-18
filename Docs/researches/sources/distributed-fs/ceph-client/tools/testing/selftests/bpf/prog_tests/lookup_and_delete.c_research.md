<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_and_delete.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_and_delete.c

Purpose: tests lookup-and-delete semantics across supported map types, including element removal, return values, batch behavior, and unsupported map handling.

Important APIs and functions: the test creates maps, populates keys/values, calls `bpf_map_lookup_and_delete_elem()` and batch variants, and compares values and follow-up lookups. It uses selftest helpers for map fd creation and assertions.

Control flow: subtests build a map fixture, insert elements, run lookup-delete operations, then verify that successful lookups return the original value and delete the element. Unsupported or invalid combinations assert expected error codes.

State and persistence: all state is in temporary map fds. Deletion behavior is the state under test; maps are closed at the end.

Dependencies and integration: depends on kernel map implementations and libbpf/syscall wrappers. It integrates with the BPF selftest harness as a pure userspace map syscall test.

Risks and test signals: expected values, missing keys after delete, and expected `errno` values are the main signals. Risks include map-type support expansion changing which operations are rejected, and batch ordering/count semantics differing by map implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_and_delete.c -->
