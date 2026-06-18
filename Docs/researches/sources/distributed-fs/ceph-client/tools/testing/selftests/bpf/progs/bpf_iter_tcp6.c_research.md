<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tcp6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tcp6.c

## Purpose

BPF iterator selftest program that attaches to an iterator target and validates seq output, typed iterator context access, map/object traversal, or socket/task state handling.

## Important APIs, Types, and Functions

- BPF sections: `license`, `iter/tcp`
- Important functions/callbacks: `hlist_unhashed_lockless`, `timer_pending`, `sock_i_ino`, `inet_csk_in_pingpong_mode`, `tcp_in_initial_slowstart`, `dump_tcp6_sock`, `dump_tw_sock`, `dump_req_sock`, `dump_tcp6`
- BPF helpers/kfunc-like calls: `bpf_jiffies64`, `bpf_ntohs`, `bpf_probe_read_kernel`, `bpf_skc_to_tcp6_sock`, `bpf_skc_to_tcp_request_sock`, `bpf_skc_to_tcp_timewait_sock`

## Control Flow and Data Flow

The iterator framework calls the program once per object and once with a NULL element at end-of-iteration. Programs either write seq data, sum keys/values, mutate/delete map entries, or validate typed context pointers while respecting sleepable versus non-sleepable section rules.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`. Depends on kernel BPF iterator targets, typed BTF context definitions from `vmlinux.h`, and seq-file output helpers where used.

## Risks and Edge Cases

Iterator contexts may pass NULL end markers and expose mutable kernel/map state; programs must handle NULLs, sleepability, and deletion while iterating. Helper availability and license restrictions matter for `bpf_jiffies64`, `bpf_ntohs`, `bpf_probe_read_kernel`, `bpf_skc_to_tcp6_sock`, `bpf_skc_to_tcp_request_sock`, `bpf_skc_to_tcp_timewait_sock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Iterator file output, accumulated sums, deletion side effects, and NULL terminal calls should match the userspace expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_iter_tcp6.c -->
