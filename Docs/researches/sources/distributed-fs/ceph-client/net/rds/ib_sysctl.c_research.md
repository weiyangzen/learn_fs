# sources/distributed-fs/ceph-client/net/rds/ib_sysctl.c

## Purpose
`ib_sysctl.c` registers runtime tunables for the RDS/IB transport under `net/rds/ib`. These tunables bound send and receive WR counts, the maximum unsignaled WR batch size, the receive allocation cap, and a legacy flow-control knob.

## Important APIs, Types, and Functions
Global tunables are `rds_ib_sysctl_max_send_wr`, `rds_ib_sysctl_max_recv_wr`, `rds_ib_sysctl_max_recv_allocation`, `rds_ib_sysctl_max_unsig_wrs`, and `rds_ib_sysctl_flow_control`. Lifecycle functions are `rds_ib_sysctl_init()` and `rds_ib_sysctl_exit()`. The registration state is held in `rds_ib_sysctl_hdr`.

## Control Flow
Initialization registers `rds_ib_sysctl_table` with `register_net_sysctl(&init_net, "net/rds/ib", ...)`. Exit unregisters the table if present. Min/max handlers constrain WR counts to at least 1 and unsignaled WRs to 1..64. `flow_control` is exposed but documented as functionally inert due to protocol compatibility with RDS 3.0 initial credit negotiation.

## State and Persistence
Sysctl values are mutable runtime kernel state scoped to the initial network namespace registration in this file. They are not persisted by the module itself; system sysctl configuration may restore them externally. Receive initialization may adjust `rds_ib_sysctl_max_recv_allocation` based on system RAM.

## Dependencies and Integration Points
`ib_send.c` reads `rds_ib_sysctl_max_unsig_wrs` for signaled completion batching. Connection setup uses max send/receive WR values through wider IB setup code. `ib_recv.c` uses `rds_ib_sysctl_max_recv_allocation` to cap incoming allocations.

## Risks
Oversized WR limits can make QP/CQ creation fail later at hardware boundaries. Too-large receive allocation allows significant pinned/page memory pressure; too-small values cause receive starvation. The `flow_control` knob appears writable but does not enable the documented behavior, so operational tooling should not rely on it.

## Test Signals
Validate sysctl registration/unregistration, min/max enforcement, connection setup with small and large WR limits, receive allocation limit behavior, and unsignaled WR completion cadence under load.
