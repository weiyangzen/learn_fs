<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lru_bug.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lru_bug.c

Purpose: regression test for LRU map preallocation/value-initialization behavior.

Important APIs and functions: `test_lru_bug()` opens and loads `lru_bug`, attaches it, then checks `skel->data->result`.

Control flow: open/load, attach, inspect the result field, destroy. The attach path triggers the BPF-side logic.

State and persistence: state is a single skeleton data result and the BPF maps inside the fixture. All state is transient.

Dependencies and integration: depends on `lru_bug.skel.h` and the BPF-side program that detects whether preallocated LRU pop incorrectly calls value initialization.

Risks and test signals: `result == 0` is expected by `ASSERT_OK`; a nonzero result means the regression was observed. Risk is low in the harness, concentrated in the companion BPF logic and attach trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lru_bug.c -->
