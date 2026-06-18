<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern4.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/bpf_map`
- Important functions/callbacks: `dump_bpf_map`
- BPF helpers/kfunc-like calls: `bpf_seq_write`
- Mutable globals/test result fields: `map1_id`, `map1_accessed`, `map1_seqnum`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `map1_id`, `map1_accessed`, `map1_seqnum`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_seq_write`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `map1_id`, `map1_accessed`, `map1_seqnum` to confirm the exercised path ran. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_test_kern4.c -->
