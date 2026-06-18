<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_ipv6_route.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_ipv6_route.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/ipv6_route`
- Important functions/callbacks: `dump_ipv6_route`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_ipv6_route.c -->
