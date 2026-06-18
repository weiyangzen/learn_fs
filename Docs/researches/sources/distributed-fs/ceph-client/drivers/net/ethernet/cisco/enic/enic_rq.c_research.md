# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_rq.c

## Purpose
`enic_rq.c` implements the ENIC receive completion path and receive buffer refill. It decodes hardware CQ entries, validates RX metadata, constructs GRO frags-backed SKBs from page-pool pages, applies RSS/checksum/VLAN metadata, updates RX statistics, and advances RQ/CQ software cursors.

## Important APIs, types, and functions
- `enic_rq_alloc_buf()` fills one RQ descriptor from a page-pool page or reposts an existing buffer.
- `enic_free_rq_buf()` returns an outstanding page to the page pool.
- `enic_rq_cq_service()` polls a receive CQ up to a budget and dispatches completions.
- `enic_rq_cq_desc_dec()` decodes 16/32/64 byte CQ header variants and extracts type, color, queue number, and completed index.
- `cq_enet_rq_desc_dec()` decodes common 16-byte receive completion fields: SOP/EOP, RSS, byte count, VLAN, FCoE, checksums, protocol flags, FCS, and errors.
- `enic_rq_set_skb_flags()` maps hardware metadata to `skb_set_hash()`, `CHECKSUM_UNNECESSARY`, encapsulation checksum level, and VLAN tag insertion.
- `enic_rq_service()` walks skipped RQ buffers until the completed descriptor is reached.

## Control flow and state
Refill flow allocates a page from `erq->pool`, records offset and truesize in the current `vnic_rq_buf`, obtains the DMA address from the page pool, then queues the descriptor with `enic_queue_rq_desc()`. Completion flow starts with `vnic_cq_to_clean()`, decodes the CQ color bit, and loops while color differs from `cq->last_color`. Each CQ entry points at an RQ and completed descriptor index. The RQ service loop advances `vrq->to_clean` and returns descriptors, accounting skipped descriptors until the target index is reached.

For good single-buffer completions, `enic_rq_indicate_buf()` obtains an skb with `napi_get_frags()`, syncs DMA for CPU, appends the page as an RX frag, records the RX queue, applies checksum/RSS/VLAN flags, marks the skb for page recycling, and submits it through `napi_gro_frags()`. It then clears the buffer ownership so the page is not freed twice. Packet errors and truncation update stats and drop the buffer.

## Dependencies and integration points
This file depends on the ENIC private state, page pool, NAPI GRO, VLAN helpers, busy-poll include, `cq_enet_desc.h`, `enic_res.h`, and `vnic_rq`/`vnic_cq` cursor helpers. Adaptive RX coalescing reads packet byte categories into `vnic_cq.pkt_size_counter`.

## Risks and test signals
Critical risks include stale CQ reads without the `rmb()`, wrong extended CQ completed-index reconstruction, page reference/lifetime mistakes, checksum metadata misinterpretation for VXLAN/FCoE repurposed fields, and skipped descriptor accounting. Test with RX checksum on/off, RSS hash reporting, VLAN-stripped packets, jumbo MTU, VXLAN offload patch levels, descriptor wrap, page-pool allocation failures, and truncated/FCS-error packets.
