<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_tos_reflect_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_tos_reflect_kern.c

## Purpose
`tcp_tos_reflect_kern.c` is a sock_ops sample that saves the incoming SYN and reflects its IPv4 TOS or IPv6 traffic class onto the accepted socket.

## Important APIs, Types, And Functions
`bpf_basertt()` handles `BPF_SOCK_OPS_TCP_LISTEN_CB` and `BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB`. It uses `bpf_setsockopt()` for `TCP_SAVE_SYN`, `IP_TOS`, and `IPV6_TCLASS`, and `bpf_getsockopt()` for `TCP_SAVED_SYN`.

## Control Flow
On listen callback, it enables SYN saving. On passive established callback, it chooses IPv4 or IPv6 header size, reads the saved SYN header, extracts TOS/traffic class, and sets the corresponding IP option when nonzero. Unsupported operations return `-1`.

## State And Persistence
No maps are used. The kernel stores saved SYN data due to `TCP_SAVE_SYN`; the accepted socket persists the reflected TOS or traffic-class option.

## Dependencies And Integration Points
It depends on cgroup sock_ops callbacks and TCP saved SYN support. It integrates with passive TCP accept paths and IP/IPv6 socket option handling.

## Risks And Edge Cases
It assumes the saved SYN header layout matches the address family and does not inspect option lengths beyond fixed IP headers. Nonzero traffic class is reflected without policy validation. Failure from the final setsockopt is not always assigned back to `rv`.

## Test Signals
Create a listening socket under the cgroup, connect with IPv4 TOS or IPv6 traffic class set, and verify the accepted socket inherits the value. Zero TOS should leave defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_tos_reflect_kern.c -->
