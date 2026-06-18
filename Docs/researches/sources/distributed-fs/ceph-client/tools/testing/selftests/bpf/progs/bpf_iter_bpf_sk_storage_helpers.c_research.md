<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_helpers.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `iter/bpf_sk_storage_map`, `iter/task_file`, `iter/tcp`
- Maps: `sk_stg_map`
- Important functions/callbacks: `delete_bpf_sk_storage_map`, `fill_socket_owner`, `negate_socket_local_storage`
- BPF helpers/kfunc-like calls: `bpf_sk_storage_delete`, `bpf_sk_storage_get`, `bpf_sock_from_file`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `sk_stg_map`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_sk_storage_delete`, `bpf_sk_storage_get`, `bpf_sock_from_file`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `sk_stg_map` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_helpers.c -->
