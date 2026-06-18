<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_percpu_hash_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_percpu_hash_map.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `iter/bpf_map_elem`
- Maps: `hashmap1`
- Important functions/callbacks: `dump_bpf_percpu_hash_map`
- Mutable globals/test result fields: `key_sum_a`, `val_sum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `hashmap1` Globals are used as userspace-visible configuration/results: `key_sum_a`, `val_sum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `key_sum_a`, `val_sum` to confirm the exercised path ran. Map contents/counts for `hashmap1` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_bpf_percpu_hash_map.c -->
