# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dynptr.c

## Purpose
Tests many successful BPF dynptr operations and generated failure cases across syscall-sleepable, skb, skb tracepoint, and XDP execution contexts.

## Important APIs, types, and functions
Uses `dynptr_success.skel.h`, `dynptr_fail.skel.h`, `network_helpers.h`, `bpf_prog_test_run_opts()`, `bpf_program__attach()`, `bpf_prog_test_load()` for auxiliary skb tracepoint triggering, and a table mapping program names to setup type. Success cases include dynptr read/write/data/copy/memset, skb metadata/data, ringbuf, adjust, null/readonly checks, clone, string compares, probe reads, and user-copy helpers.

## Control flow and state
For each success case, only the named program is autoloaded, BSS `pid`, `user_ptr`, `expected_str`, and data `test_len` are initialized, then the selected setup path triggers execution. XDP uses a large buffer, with size adjusted for 64K page systems. After trigger, BSS `err` must be zero. Negative cases are delegated to `RUN_TESTS(dynptr_fail)`.

## Dependencies and integration points
Depends on dynptr helper/kfunc support, generated success/fail BPF objects, packet fixtures, test-run support for XDP and skb programs, and auxiliary `test_pkt_access.bpf.o`.

## Risks and test signals
Risks include page-size-specific XDP bounds and context-specific helper availability. Passing signal is zero BSS error for all success programs and expected verifier rejection in failure skeleton tests.
