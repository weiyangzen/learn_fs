# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/wq.c

## Purpose

Harness for BPF workqueue tests, including successful workqueue execution, expected verifier/load failures, and a custom negative case for maps lacking BTF. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`RUN_TESTS(wq)`, `RUN_TESTS(wq_failures)`, `wq__open_and_load()`, `bpf_prog_test_run_opts()`, `bpf_object__prepare()`, `bpf_map_create()`, `bpf_map__reuse_fd()`, raw `bpf_prog_load()`, and verifier log substring checks.

## Control Flow

`serial_test_wq()` runs common success tests, reloads the skeleton, attaches it, test-runs a sleepable syscall-array program, waits briefly, and checks that a timer/workqueue callback updated BSS. `serial_test_failures_wq()` delegates negative tests. `test_wq_custom()` loads instructions with a reused no-BTF map and asserts verifier log text.

## State and Persistence Behavior

Transient skeletons, one manually created array map fd, verifier log buffer, and BSS `ok_sleepable`. No durable state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires BPF workqueue support and BTF-bearing map validation.

## Risks and Edge Cases

The sleep is short and depends on async callback scheduling. The negative log check is string-sensitive. The reused fd path must close through skeleton destruction.

## Test Signals

`ok_sleepable == (1 << 1)`, expected failure skeleton results, failed raw program load for no-BTF map, and log substring `has to have BTF in order to use bpf_wq`.
