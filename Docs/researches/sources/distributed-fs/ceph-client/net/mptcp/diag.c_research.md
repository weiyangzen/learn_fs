<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/diag.c -->
# sources/distributed-fs/ceph-client/net/mptcp/diag.c

## Purpose
Adds MPTCP subflow-specific diagnostic data to TCP ULP inet-diag output.

## Important APIs, Types, and Functions
`subflow_get_info()` emits nested `INET_ULP_INFO_MPTCP` attributes for a subflow. `subflow_get_info_size()` computes the required netlink size. `mptcp_diag_subflow_init()` installs these callbacks into `tcp_ulp_ops`.

## Control Flow
For non-listening sockets, the get-info path starts a netlink nest, locks the socket with `lock_sock_fast()`, reads the MPTCP subflow context through RCU, builds a flag word from MP_CAPABLE, MP_JOIN, backup, establishment, connected, and mapping-valid states, then emits tokens, flags, and local/remote IDs. CAP_NET_ADMIN callers additionally receive relative write sequence and mapping sequence/counters. Errors cancel the nest and unwind locks.

## State and Persistence
No state is owned. The file reads live subflow context fields and TCP socket state. Exported diagnostics are snapshots.

## Dependencies and Integration Points
Depends on inet diag netlink attributes, MPTCP subflow context, TCP ULP registration, RCU, and socket locking. It integrates with the larger inet diag path and with `mptcp_diag.c`, which handles whole MPTCP socket diagnostics.

## Risks
Diagnostic size calculation must match emitted attributes or dumps can fail with `-EMSGSIZE`. Sequence-related fields are intentionally gated by `CAP_NET_ADMIN`; leaking them to unprivileged users would be a security regression. The callback must tolerate missing ULP data while sockets transition.

## Test Signals
Use `ss -M -i` or inet_diag requests against established/listening/plain TCP sockets, with and without CAP_NET_ADMIN. Verify flags and IDs for MP_CAPABLE and MP_JOIN subflows and that size estimates avoid truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/diag.c -->
