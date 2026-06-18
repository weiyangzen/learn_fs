<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_sockmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_sockmap.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `.maps`, `iter/sockmap`
- Maps: `sockmap`, `sockhash`, `dst`
- Important functions/callbacks: `copy`
- BPF helpers/kfunc-like calls: `bpf_map_delete_elem`, `bpf_map_update_elem`
- Mutable globals/test result fields: `elems`, `socks`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `sockmap`, `sockhash`, `dst` Globals are used as userspace-visible configuration/results: `elems`, `socks`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `errno.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_map_delete_elem`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `elems`, `socks` to confirm the exercised path ran. Map contents/counts for `sockmap`, `sockhash`, `dst` provide state validation. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_sockmap.c -->
