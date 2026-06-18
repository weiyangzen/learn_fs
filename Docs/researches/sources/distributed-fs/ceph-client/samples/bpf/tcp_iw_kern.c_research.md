<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_iw_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_iw_kern.c

## Purpose
`tcp_iw_kern.c` demonstrates sock_ops control of initial congestion window, initial receive window, and socket buffers for selected TCP traffic.

## Important APIs, Types, And Functions
`bpf_iw()` handles `BPF_SOCK_OPS_RWND_INIT`, `BPF_SOCK_OPS_TCP_CONNECT_CB`, `BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB`, and `BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB`. It sets `SO_SNDBUF`, `SO_RCVBUF`, and `TCP_BPF_IW`.

## Control Flow
For connections involving port `55601`, the program returns receive window `40`, sets 1.5 MB buffers during active connect and passive established callbacks, and sets initial congestion window `40` on active established. Other callbacks return `-1`.

## State And Persistence
No BPF maps are used. Socket options persist on the affected TCP socket.

## Dependencies And Integration Points
It integrates with TCP cgroup sock_ops and depends on kernel support for `TCP_BPF_IW` setsockopt.

## Risks And Edge Cases
The sample lacks the real distance/RTT policy its comments describe. Port gating is test-specific. Over-large initial windows and buffers can hurt congestion behavior if deployed blindly.

## Test Signals
For port `55601`, inspect TCP socket buffers and initial congestion/receive window behavior. Non-matching ports should not be modified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_iw_kern.c -->
