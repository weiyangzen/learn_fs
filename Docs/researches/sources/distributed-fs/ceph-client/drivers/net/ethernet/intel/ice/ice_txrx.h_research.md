# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx.h

Purpose: defines the ice TX/RX datapath ABI used across the driver. It contains descriptor sizing constants, TX flag bits, XDP result bits, buffer ownership types, offload parameter storage, ring stats, ring state enums, interrupt moderation helpers, ring structures, iterators, and public datapath prototypes.

Important APIs and types: `enum ice_tx_buf_type` defines cleanup ownership for SKB, dummy Flow Director buffers, XDP_TX, XDP_XMIT, XSK, and fragments. `struct ice_tx_buf` stores descriptor watch/RS index, buffer pointer, byte/segment accounting, flags, VLAN ID, and DMA mapping. `struct ice_tx_offload_params` carries context/data descriptor fields while building TX. `struct ice_rx_ring`, `struct ice_tx_ring`, and `struct ice_tstamp_ring` are the core queue structures. `struct ice_ring_container` groups rings per q_vector and holds DIM/ITR state.

Control flow role: macros such as `ICE_DESC_UNUSED()`, `DESC_NEEDED`, and `ICE_GLINT_DYN_CTL_WB_ON_ITR()` directly guide queue stop/wake, refill, and interrupt writeback behavior in `ice_txrx.c`. `ice_for_each_rx_ring` and `ice_for_each_tx_ring` drive NAPI loops. Prototypes expose setup, cleanup, NAPI, xmit, queue selection, Flow Director, and timestamp cleanup to the wider driver.

State and persistence: the ring structures cache hardware descriptor DMA addresses, tail MMIO pointers, queue indices, register indices, backreferences to VSI/q_vector/netdev, XDP and XSK resources, page-pool/fill-queue state, per-ring stats, and channel/scheduler identifiers. Ring stats use `u64_stats_sync` so readers can safely sample 64-bit counters.

Dependencies and integration: includes libeth types and `ice_type.h`, and references netdev, BPF/XDP, page pool, PTP, channel, q_vector, and VSI types defined elsewhere. The layout uses cacheline grouping macros because these structures are touched in high-frequency NAPI and transmit paths.

Risks: structure layout and flag semantics are performance and correctness sensitive. Changing descriptor constants can break hardware limits. Ring fields have implicit concurrency expectations between NAPI, xmit, teardown, XDP, and stats readers. The timestamp ring pointer is RCU-managed and must be paired with ordering in the implementation.

Test signals: build all datapath users, run traffic with varying ring sizes, XDP/XSK enablement, TX timestamp enable/disable, queue stop/wake, interrupt moderation settings, stats reads under load, and teardown/reset while traffic is active.
