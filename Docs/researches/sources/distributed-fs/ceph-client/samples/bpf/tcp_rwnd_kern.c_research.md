<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_rwnd_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_rwnd_kern.c

## Purpose
`tcp_rwnd_kern.c` is a sock_ops sample that increases the initial TCP receive window for IPv6 connections whose prefixes suggest they are not in the same datacenter.

## Important APIs, Types, And Functions
The entry point is `bpf_rwnd()`. It reads `struct bpf_sock_ops` fields, checks `BPF_SOCK_OPS_RWND_INIT`, uses `bpf_ntohl()`, and writes `skops->reply`.

## Control Flow
The program gates on port `55601`, then only handles `RWND_INIT` for IPv6 sockets. If the first prefix components differ, it returns `40`; otherwise the default `-1` reply is kept.

## State And Persistence
No maps or persistent state exist. The reply value influences TCP's initial advertised receive window for the connection.

## Dependencies And Integration Points
It depends on cgroup sock_ops and TCP receive-window callback support. It is intended to be loaded with `bpftool cgroup attach`.

## Risks And Edge Cases
The IPv6 prefix comparison mask differs slightly from other samples and is hard-coded. IPv4 traffic and unsupported operations are ignored. The comment typo does not affect behavior but reflects sample-only polish.

## Test Signals
Matching IPv6 remote/local prefixes that differ should produce `reply = 40`; same-prefix or non-IPv6 traffic should preserve default behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_rwnd_kern.c -->
