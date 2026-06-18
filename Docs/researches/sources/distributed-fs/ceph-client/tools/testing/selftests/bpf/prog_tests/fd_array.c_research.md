# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fd_array.c

## Purpose
Tests `BPF_PROG_LOAD` `fd_array` semantics for extra map/BTF references: normal use, duplicates, already referenced maps, BTF lifetime, invalid FDs, and too many FDs.

## Important APIs, types, and functions
Uses raw map creation (`bpf_map_create()`), raw BTF load (`bpf_btf_load()`), `bpf_prog_load()` with `bpf_prog_load_opts.fd_array`, `bpf_prog_get_info_by_fd()` map IDs, `bpf_map_get_fd_by_id()`, `bpf_btf_get_fd_by_id()`, and `kern_sync_rcu()`. Helper `__load_test_prog()` builds a tiny XDP program using one map.

## Control flow and state
Subtests create maps/BTFs, load a program with specified fd arrays, inspect bound map IDs, close original FDs, and verify kernel object lifetimes. BTF lifetime test waits for program cleanup after closing program FD. Invalid cases expect `-EBADF`, `-EINVAL`, or `-E2BIG`. State is FDs, kernel object IDs, and short-lived loaded programs.

## Dependencies and integration points
Depends on BPF syscall support for `fd_array`, map/BTF refcounting, RCU synchronization helper, and verifier acceptance of the tiny XDP program. Integrated as `test_fd_array_cnt()`.

## Risks and test signals
Lifetime checks can be timing-sensitive. Passing signals include expected map ID counts, objects staying alive while program holds refs, BTF disappearing after program cleanup, and exact errors for trash/oversized arrays.
