<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0_internal.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0_internal.h

Purpose: defines B0-specific hardware constants for descriptors, filters, IRQs, buffers, RSS/TC, LRO/LSO, firmware semaphore, interrupt moderation, VLAN/L2 actions, and descriptor count limits.

Important APIs/types: constants include jumbo/default MTU, ring/descriptor sizes, unicast/multicast filter counts, interrupt masks, TX data/context descriptor masks, MPI registers, PTP buffer reservations, RSS hash/redirection sizes, TC/RSS maxima, LRO limits, LSO max segment sizes, chip revision IDs, RX writeback status bits, filter actions, moderation min/max, descriptor bounds, and RSS mode encodings.

Control flow: `hw_atl_b0.c` uses these constants to build caps, program QoS and PTP TC buffers, pack GSO/VLAN TX descriptors, parse RX checksum/VLAN/LRO status, configure filters, choose RSS mode, and program interrupt moderation.

State and persistence: no runtime state; constants encode the B0 register/descriptor ABI.

Dependencies and integration: includes `aq_common`; private to B0 hardware implementation and any closely related helper reuse.

Risks: descriptor masks are tightly coupled to hardware layout; PTP buffer sizes reduce regular TC buffer budget; LSO/LRO limits must match netdev feature exposure; RSS mode constants must match TC mode decisions in `aq_nic_cfg_update_num_vecs`. Test signals include maximum MTU/descriptor tests, LSO boundary tests, LRO chains, PTP ring operation, RSS distribution for 4TC/8TC modes, and filter-slot exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0_internal.h -->
