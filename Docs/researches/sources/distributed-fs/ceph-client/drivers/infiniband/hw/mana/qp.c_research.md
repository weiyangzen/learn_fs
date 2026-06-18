# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/qp.c

## Purpose
`qp.c` implements MANA QP creation, modification, destruction, RSS/raw Ethernet queue setup, RNIC RC QPs, and kernel UD/GSI QPs with shadow queues.

## Important APIs, Types, And Functions
`mana_ib_create_qp()` dispatches by QP type to raw packet, RSS, RC, UD, or GSI creation. `mana_ib_create_qp_raw()` configures a vport, creates a userspace SQ, creates a MANA Ethernet WQ object, and returns SQ/CQ IDs. `mana_ib_create_qp_rss()` creates receive WQ objects from an indirection table and configures vport RX steering. `mana_ib_create_rc_qp()` creates user queues and a firmware RNIC RC QP. `mana_ib_create_ud_qp()` creates kernel SQ/RQ queues, shadow queues, and a firmware UD/GSI QP. `mana_ib_modify_qp()` sends RNIC state transitions and AH/path data. `mana_ib_destroy_qp()` dispatches to matching teardown paths. QP table helpers store and remove QPs in an xarray keyed by RC QPN or UD queue IDs.

## Control Flow
Raw/RSS packet QPs are userspace-oriented and use MANA Ethernet vport/WQ APIs. RC QPs read user queue buffers, skip the FMR queue for user-level RC, pass DMA regions to firmware, set QPN from responder RQ ID, return queue IDs to userspace, and insert into the QP table. UD/GSI QPs are kernel-only, allocate hardware queues and shadow queues, create the firmware QP, set kernel queue IDs, store QP references, and add the QP to send/recv CQ lists. Modify QP builds `MANA_IB_SET_QP_STATE`, copies path attributes when `IB_QP_AV` is set, and submits the command.

## State And Persistence
`struct mana_ib_qp` holds firmware handle, raw/RC/UD queues, port, CQ list nodes, shadow queues, refcount, and completion. Packet QPs also configure PD vport use state. RSS state is primarily in WQ objects and vport steering. All state is runtime-only and is removed through destroy paths.

## Dependencies And Integration Points
The file integrates RDMA QP ops, MANA Ethernet WQ/vport steering APIs, GDMA queue creation, firmware RNIC QP commands in `main.c`, CQ callback installation, CQ list polling in `cq.c`, shadow queues, netdev MTU/MAC state, and GID/AV helpers.

## Risks
Error unwinds are complex and must distinguish locally owned DMA regions from firmware-owned regions. `mana_ib_create_qp_rss()` failure after several WQs must remove CQ callbacks and WQ objects consistently. Destroy RSS disables vport RX best-effort because no kernel fence can wait for userspace-polled CQs; failures may leave traffic routing stale. `mana_ib_create_ud_qp()` has a cleanup bug risk: if SQ shadow queue creation fails, the label destroys both shadow queues even though SQ may not have been created. Modify QP assumes GRH `sgid_attr` is present when `IB_QP_AV` is supplied.

## Test Signals
Test raw packet QP creation/destroy, RSS indirection sizes and hash validation, vport config refcounting, RC user queue creation and udata responses, UD/GSI kernel post/poll cycles, QP xarray lookup under completions, modify QP state transitions with IPv4/IPv6 AVs, every error label, and destroy while completions are in flight.
