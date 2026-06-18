# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_roce_cm.c

## Purpose
`qedr_roce_cm.c` implements the RoCE GSI/QP1 path for QEDR using the QED LL2 interface. It creates and destroys the special GSI QP, builds UD/RoCE packet headers, posts receive buffers through LL2, transmits send WRs through LL2, and synthesizes CQ completions for GSI traffic.

## Important APIs, Types, And Functions
Exported functions are `qedr_inc_sw_gsi_cons`, `qedr_store_gsi_qp_cq`, `qedr_create_gsi_qp`, `qedr_destroy_gsi_qp`, `qedr_gsi_post_send`, `qedr_gsi_post_recv`, and `qedr_gsi_poll_cq`. Internal LL2 callbacks are `qedr_ll2_complete_tx_packet`, `qedr_ll2_complete_rx_packet`, and `qedr_ll2_release_rx_packet`. Internal helpers include `qedr_ll2_start`, `qedr_ll2_stop`, `qedr_ll2_post_tx`, `qedr_gsi_build_header`, and `qedr_gsi_build_packet`.

## Control Flow
Creating a GSI QP validates max WR/SGE limits, starts an LL2 RoCE connection with RX/TX callbacks and MAC filter, assigns QP number 1, allocates SQ/RQ shadow arrays, stores global GSI QP/CQ pointers, records the MAC address, destroys the firmware CQs because GSI completions are driver-synthesized, and marks the receive CQ as `QEDR_CQ_TYPE_GSI`. Destroying stops LL2, removes the MAC filter, terminates and releases the LL2 connection.

Posting send accepts only one `IB_WR_SEND` at a time and only in RTS. It builds an Ethernet/VLAN/GRH-or-IP/UDP/BTH/DETH header based on SGID type, packs it into coherent DMA memory, attaches payload SGEs by DMA address, posts it to LL2, records the WR ID, and advances SQ producer. TX completion frees header DMA memory and packet metadata, advances `gsi_cons`, and calls the CQ completion handler. Posting receive accepts only one receive SGE per WR, posts the buffer to LL2, stores the WR ID and SGE, and advances RQ producer. RX completion records status, VLAN, payload length, source MAC, advances RQ `gsi_cons`, and signals the CQ. Polling first drains RX completions into receive WCs with GRH, checksum, SMAC, and optional VLAN flags, then drains TX completions as send WCs.

## State And Persistence Behavior
State is runtime-only: `dev->gsi_ll2_handle`, `gsi_qp_created`, `gsi_sqcq`, `gsi_rqcq`, `gsi_qp`, `gsi_ll2_mac_address`, QP SQ/RQ producers/consumers/GSI consumers, and shadow WR arrays. Packet header DMA allocations persist from post-send until LL2 TX completion or release callback.

## Dependencies And Integration Points
The file depends on RDMA UD header helpers, `ib_cache` GID attributes, net/IP/IPv6/UDP headers, Linux DMA APIs, QED LL2 operations, QED RoCE packet structs, QEDR AH/QP/CQ state, and RoCE constants. It integrates with verbs QP creation for `IB_QPT_GSI` and with MAC-change notification in `main.c`, which updates the LL2 filter and GID event.

## Risks And Test Signals
Risks include GSI global pointer lifetime during destroy, partial LL2 TX failures where payload posting fails after header posting, unchecked receive WR with zero SGEs despite later using `sg_list[0]`, single-WR send limitation surprises, and header correctness for VLAN/RoCEv1/RoCEv2 IPv4/IPv6. Test signals include SA/CM traffic over QP1, RoCE v1 and v2 IPv4/IPv6 GID types, VLAN-tagged GSI traffic, MAC address changes, LL2 start/stop failure injection, send completion memory leak checks, and CQ polling order with concurrent RX/TX completions.
