# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_av.c

## Purpose
`rxe_av.c` converts RDMA address-handle attributes into RXE address vectors, validates address attributes, fills IP addressing metadata, and resolves the address vector used for outgoing packets.

## Important APIs, types, and functions
Functions include `rxe_init_av()`, `rxe_av_chk_attr()`, `rxe_ah_chk_attr()`, `rxe_av_from_attr()`, `rxe_av_to_attr()`, `rxe_av_fill_ip_info()`, and `rxe_get_av()`. Core state is `struct rxe_av`, `struct rdma_ah_attr`, `struct ib_global_route`, `struct rxe_ah`, `struct rxe_qp`, and `struct rxe_pkt_info`.

## Control flow
AH/QP attribute validation calls `chk_attr()`, which verifies GRH SGID index and network type for RXE when GRH is set. Initialization copies GRH fields, port number, source/destination IP addresses, network type, and destination MAC. Connected QPs use `qp->pri_av`. UD sends use either a new-provider AH number looked up from the AH pool with PD validation, or an embedded legacy AV in the WQE.

## State and persistence
Address vectors persist inside AH objects, QP primary AVs, or WQEs. `rxe_get_av()` may return a referenced AH through `ahp`; callers must drop that reference. It also populates transient packet routing data used by the network transmit path.

## Dependencies and integration points
The file depends on RDMA AH/GID helpers, RXE object pools, QP/PD/AH state, and network address type definitions. It feeds `rxe_req.c` and `rxe_net.c` transmit paths.

## Risks
SGID index validation uses `>` rather than `>=` against `gid_tbl_len`, so boundary expectations should be checked against RDMA core conventions. AH pool lookup and PD matching are critical to avoid using another PD's AH. Legacy embedded AV support must remain compatible with older userspace providers.

## Test signals
Test AH creation and QP modify with IPv4/IPv6 GIDs, invalid SGID indexes and network types, connected QP sends, UD sends with AH numbers, legacy UD embedded AVs, PD mismatch rejection, and AH reference release.
