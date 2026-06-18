<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.c

Purpose: implements the Atlantic A0 chip-specific hardware operation table and capability records for early AQC100/AQC107/AQC108/AQC109 devices.

Important APIs/functions: exports A0 capability constants and `hw_atl_ops_a0`. Static functions handle reset, QoS, RSS key/table programming, offloads, TX/RX path initialization, MAC address programming, hardware init/start/stop, descriptor programming, IRQ masking/readback, packet/multicast filters, interrupt moderation, and L3/L4 filters.

Control flow: generic NIC init calls `hw_reset`/`hw_init`; A0 init programs TX/RX paths, MAC, link speed, firmware MPI state, QoS, RSS, initial stats, interrupt mapping, and offloads. Ring init writes descriptor base/length/interrupt/CPU registers. TX xmit converts generic buffer metadata into A0 TX/context descriptors and advances hardware tail. RX receive parses writeback descriptors into generic buffer flags, checksum/RSS metadata, packet length, EOP, and jumbo chains.

State and persistence: programs MMIO registers, firmware state, descriptor rings, multicast filter slots, interrupt moderation registers, and hardware stats. Runtime state remains in `aq_hw_s`, `aq_nic_cfg_s`, and rings.

Dependencies and integration: depends on `aq_hw`, `aq_hw_utils`, `aq_ring`, `aq_nic`, low-level `hw_atl_llh`, and A0 constants. It supplies ops selected by PCI board revision matching.

Risks: A0 has limited TC/offload capability; RX receive contains hardware workarounds for descriptor status anomalies and small checksum packets; descriptor bit packing must match hardware; interrupt moderation table depends on link speed index. Test signals include A0 probe, link speed programming, checksum/TSO, RSS distribution, jumbo RX, multicast/promisc modes, L3/L4 filters, and interrupt moderation modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.c -->
