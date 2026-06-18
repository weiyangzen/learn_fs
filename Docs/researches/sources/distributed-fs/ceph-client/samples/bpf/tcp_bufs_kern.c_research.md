<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_bufs_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_bufs_kern.c

## Purpose
`tcp_bufs_kern.c` demonstrates sock_ops control of initial receive window and socket buffer sizes for selected TCP connections.

## Important APIs, Types, And Functions
`bpf_bufs()` handles `BPF_SOCK_OPS_RWND_INIT`, `BPF_SOCK_OPS_TCP_CONNECT_CB`, `BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB`, and `BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB`. It uses `bpf_setsockopt()` for `SO_SNDBUF` and `SO_RCVBUF`, `bpf_ntohl()`, and `skops->reply`.

## Control Flow
The program gates behavior to connections where either local or remote port is `55601`. It returns an initial receive window of `40` packets on `RWND_INIT`, sets send and receive buffers to 1.5 MB on active connect and passive established callbacks, does nothing for active established, and returns `-1` for unsupported operations.

## State And Persistence
No BPF maps are used. Persistent effects are socket option changes applied to each matched TCP socket.

## Dependencies And Integration Points
It attaches as a cgroup sock_ops program and integrates with TCP socket option handling. The sample assumes caller traffic uses port `55601` for test selection.

## Risks And Edge Cases
The port guard comment says "neither" but the logic actually runs when either side is port `55601`. Summing two setsockopt return codes can obscure which option failed. Applying large buffers without real RTT checks can waste memory.

## Test Signals
Use TCP traffic involving port `55601` and verify initial receive window and socket buffers. Non-matching ports should receive `reply = -1` and unchanged buffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_bufs_kern.c -->
