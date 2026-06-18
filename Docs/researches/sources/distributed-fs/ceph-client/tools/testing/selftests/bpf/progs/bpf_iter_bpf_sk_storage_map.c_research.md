<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_map.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `iter/bpf_sk_storage_map`, `iter/bpf_sk_storage_map`
- Maps: `sk_stg_map`
- Important functions/callbacks: `rw_bpf_sk_storage_map`, `oob_write_bpf_sk_storage_map`
- Mutable globals/test result fields: `val_sum`, `ipv6_sk_count`, `to_add_val`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `sk_stg_map` Globals are used as userspace-visible configuration/results: `val_sum`, `ipv6_sk_count`, `to_add_val`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `val_sum`, `ipv6_sk_count`, `to_add_val` to confirm the exercised path ran. Map contents/counts for `sk_stg_map` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_sk_storage_map.c -->
