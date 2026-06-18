<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.h

Purpose: defines the common ring data structures and function prototypes for TX, RX, XDP, and PTP hardware timestamp rings.

Important APIs/types: `struct aq_rxpage` stores page/DMA/page-offset information. Packed `struct aq_ring_buff_s` stores per-descriptor metadata for RX, TX, EOP, and TX context descriptors. Stats structs track RX/TX counters. `enum atl_ring_type`, `struct aq_ring_s`, and `struct aq_ring_param_s` define ring identity, DMA descriptor state, queue pointers, XDP RXQ metadata, and IRQ affinity inputs.

Control flow: hardware and generic code share `aq_ring_next_dx` and `aq_ring_avail_dx` for circular descriptor management. Public functions allocate/init/fill/clean/deinit/free rings and expose stats.

State and persistence: ring state is runtime memory plus coherent DMA descriptor memory visible to hardware. The header declares no global persistent state.

Dependencies and integration: includes common definitions and vector declarations; used by NIC, vector, PTP, and A0/B0 hardware files. It also includes Linux XDP-facing layout constants for headroom/tailroom.

Risks: `aq_ring_buff_s` is packed for cache layout and shared assumptions; bitfields and unions must stay consistent with generic mapping and hardware descriptor programming; circular queue arithmetic reserves one descriptor for empty/full distinction. Test signals include descriptor wraparound, fragment limits, XDP multi-buffer use, stats reads on 32-bit, and queue availability thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.h -->
