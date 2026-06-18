# sources/distributed-fs/ceph-client/net/rds/rds_single_path.h

## Purpose
`rds_single_path.h` provides compatibility macros that map legacy single-path `struct rds_connection` field names to `conn->c_path[0]` members. It lets older transport code operate on path zero without rewriting every field access.

## Important APIs, Types, and Functions
The header defines macros such as `c_xmit_rm`, `c_xmit_sg`, `c_xmit_hdr_off`, `c_lock`, `c_next_tx_seq`, `c_send_queue`, `c_retrans`, `c_next_rx_seq`, `c_transport_data`, `c_state`, `c_flags`, `c_send_w`, `c_recv_w`, `c_cm_lock`, `c_waitq`, `c_unacked_packets`, and `c_unacked_bytes`.

## Control Flow
Files that include this header access `conn->c_*` names while actually reading or writing `conn->c_path[0].cp_*`. This supports single-path transports and CM logic that are not multipath-aware.

## State and Persistence
The header owns no state; it aliases existing path-zero state in `struct rds_connection`.

## Dependencies and Integration Points
Included by loopback, IB send/receive, RDMA transport, and other single-path-oriented files. It depends on `rds.h` structure layout.

## Risks
These macros hide whether code is path-aware. Including the header in multipath-capable logic can accidentally force all operations onto path zero. Macro aliases also make code search and refactoring harder because field access is not explicit.

## Test Signals
Build coverage should catch layout mismatches. Multipath tests should ensure files using this header are either truly single-path or intentionally operate on path zero.
