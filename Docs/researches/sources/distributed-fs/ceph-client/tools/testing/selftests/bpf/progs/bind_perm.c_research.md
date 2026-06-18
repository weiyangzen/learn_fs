<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_perm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_perm.c

## Purpose

Small cgroup bind permission program that allows only bind requests targeting the selftest port for both IPv4 and IPv6.

## Important APIs, Types, and Functions

- BPF sections: `cgroup/bind4`, `cgroup/bind6`, `license`
- Important functions/callbacks: `bind_prog`, `bind_v4_prog`, `bind_v6_prog`
- BPF helpers/kfunc-like calls: `bpf_htons`

## Control Flow and Data Flow

Control starts at the cgroup bind hook. The program inspects `bpf_sock_addr`, optionally rewrites `user_ip*` and `user_port`, sets or reads socket options, and returns 1 to allow or 0 to deny. There is no loop or persistent per-socket state beyond socket option effects.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `linux/stddef.h`, `linux/bpf.h`, `sys/types.h`, `sys/socket.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`. Integrates with cgroup bind4/bind6 attach points and socket option helpers.

## Risks and Edge Cases

Socket option rewrites must preserve endian handling and address family layout; deny hooks can make tests fail by blocking unrelated binds if attached too broadly. Helper availability and license restrictions matter for `bpf_htons`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Bind/connect attempts on allowed, rewritten, device-bound, reuseport, and denied cases should match expected errno and socket address results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind_perm.c -->
