<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_basertt_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_basertt_kern.c

## Purpose
`tcp_basertt_kern.c` is a sock_ops sample that supplies a custom base RTT value for TCP-NV when local and remote IPv6 addresses appear to be in the same datacenter.

## Important APIs, Types, And Functions
The sole BPF entry point is `bpf_basertt()` in section `sockops`. It uses `struct bpf_sock_ops`, `BPF_SOCK_OPS_BASE_RTT`, `bpf_getsockopt()` for `TCP_CONGESTION`, `bpf_ntohl()`, `bpf_printk()`, and `skops->reply`.

## Control Flow
The program checks the sock_ops operation and IPv6 prefix relationship. On `BPF_SOCK_OPS_BASE_RTT`, it reads the TCP congestion control name and returns `80` microseconds only when it matches `nv`; otherwise it returns the helper error or `-1`. Unsupported operations and non-matching address families/prefixes return `-1`.

## State And Persistence
No maps are used. The only state change is the per-callback `skops->reply` value consumed by TCP sock_ops.

## Dependencies And Integration Points
It depends on cgroup sock_ops attachment via bpftool, TCP-NV availability, and kernel support for `TCP_CONGESTION` getsockopt from sock_ops. It integrates with TCP connection setup and base RTT callbacks.

## Risks And Edge Cases
The datacenter heuristic is hard-coded to the first 5.5 bytes of IPv6 addresses and ignores IPv4. String comparison uses the fixed `nv` array size. Debug printing can be noisy.

## Test Signals
Attach to a cgroup and establish IPv6 TCP-NV connections with matching and non-matching prefixes. Confirm `skops->reply` becomes `80` only for the matching TCP-NV case and `-1` otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_basertt_kern.c -->
