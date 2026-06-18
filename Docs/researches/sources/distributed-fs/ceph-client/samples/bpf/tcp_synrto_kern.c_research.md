<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_synrto_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_synrto_kern.c

## Purpose
`tcp_synrto_kern.c` demonstrates using sock_ops to set SYN and SYN-ACK initial RTO to 10 ms for same-datacenter IPv6 TCP connections.

## Important APIs, Types, And Functions
The single entry point `bpf_synrto()` handles `BPF_SOCK_OPS_TIMEOUT_INIT`, IPv6 address fields, `bpf_ntohl()`, and `skops->reply`.

## Control Flow
After filtering to port `55601`, it checks for `TIMEOUT_INIT` and IPv6. If the first 5.5 bytes of local and remote IPv6 addresses match, it returns `10`; otherwise it leaves `rv = -1`.

## State And Persistence
There is no persistent BPF state. The callback reply influences TCP handshake timeout initialization.

## Dependencies And Integration Points
It depends on cgroup sock_ops and TCP timeout initialization callbacks.

## Risks And Edge Cases
The 10 ms timeout is environment-specific and can trigger unnecessary retransmits outside low-latency domains. The sample ignores IPv4 and uses a fixed prefix heuristic.

## Test Signals
Same-prefix IPv6 port `55601` connections should report timeout init `10`; other connections should use default timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_synrto_kern.c -->
