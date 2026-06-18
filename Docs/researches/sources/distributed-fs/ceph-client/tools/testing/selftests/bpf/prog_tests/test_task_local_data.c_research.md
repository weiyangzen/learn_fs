<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_local_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_local_data.c

Purpose: tests the userspace task-local-data helper library and BPF-side reads under multithreaded isolation, concurrent key creation, and variable dynamic-data capacity.

Important APIs/types/functions: `TLD_DEFINE_KEY`, `tld_create_key()`, `tld_get_data()`, `tld_free()`, internal `tld_meta_p`, `reset_tld()`, generated `test_task_local_data` skeleton, and BPF program `task_main`.

Control flow: basic subtest resets metadata, creates static/dynamic keys, verifies `E2BIG`, `EEXIST`, and `ENOSPC`, then starts 32 threads. Each thread writes thread-specific values, serializes BPF program test-run through `global_mutex`, checks BPF-observed globals, mutates values, and repeats. Race subtest repeatedly starts many threads that create valid and invalid keys concurrently, writes unique values to all keys, checks no overlap, and runs BPF. Dynamic-size subtests reset available size to 64 or 0, fill as many int keys as allowed, expect overflow, verify values, and ensure static key remains readable by BPF.

State and persistence: intentionally mutates library-global metadata `tld_meta_p`, process thread-local data, and skeleton BSS. `reset_tld()` is safe only because subtests are sequential. Allocated key arrays are freed, and `tld_free()` clears library state.

Dependencies and integration: depends on `task_local_data.h`, pthreads, BTF headers, generated skeleton, page size, and BPF map test-run support. Integrated as `test_task_local_data`.

Risks: directly modifying library internals is test-only and fragile. Thread array joins can join uninitialized entries if thread creation fails early. Race loops are timing-sensitive but repeated 100 times to amplify bugs.

Test signals: key-creation errno assertions, per-thread BPF/global value equality, no overlap checks, race return codes, `task_main` retval, dynamic overflow `-E2BIG`, and static-key readback `0xdeadbeef`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_local_data.c -->
