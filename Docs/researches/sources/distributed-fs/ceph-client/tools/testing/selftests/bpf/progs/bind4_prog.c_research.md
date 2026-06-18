<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind4_prog.c

## Purpose

Cgroup IPv4 bind selftest program that rewrites bind addresses/ports, exercises SO_BINDTODEVICE and SO_REUSEPORT manipulation, and provides an explicit deny hook.

## Important APIs, Types, and Functions

- BPF sections: `cgroup/bind4`, `cgroup/bind4`, `license`
- Important functions/callbacks: `bind_v4_prog`, `bind_v4_deny_prog`
- BPF helpers/kfunc-like calls: `bpf_getsockopt`, `bpf_htonl`, `bpf_htons`, `bpf_setsockopt`

## Control Flow and Data Flow

Control starts at the cgroup bind hook. The program inspects `bpf_sock_addr`, optionally rewrites `user_ip*` and `user_port`, sets or reads socket options, and returns 1 to allow or 0 to deny. There is no loop or persistent per-socket state beyond socket option effects.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `string.h`, `linux/stddef.h`, `linux/bpf.h`, `linux/in.h`, `linux/in6.h`, `linux/if.h`, `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`, `bind_prog.h`. Integrates with cgroup bind4/bind6 attach points and socket option helpers.

## Risks and Edge Cases

Socket option rewrites must preserve endian handling and address family layout; deny hooks can make tests fail by blocking unrelated binds if attached too broadly. Helper availability and license restrictions matter for `bpf_getsockopt`, `bpf_htonl`, `bpf_htons`, `bpf_setsockopt`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Bind/connect attempts on allowed, rewritten, device-bound, reuseport, and denied cases should match expected errno and socket address results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bind4_prog.c -->
