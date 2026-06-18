<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/mana.h -->
# sources/distributed-fs/ceph-client/include/net/mana/mana.h

## Purpose
`mana.h` defines the Microsoft Azure Network Adapter Ethernet-facing data structures, hardware command ABI, queue objects, statistics, XDP hooks, RSS state, and public driver function declarations built on GDMA/HWC.

## Important APIs, types, and functions
Core types are `struct mana_context`, `struct mana_port_context`, `struct mana_txq`, `struct mana_rxq`, `struct mana_cq`, `struct mana_tx_qp`, TX/RX OOB and completion structs, ethtool hardware/PHY stats, queue object specs, and hardware command request/response structs. Declared APIs cover transmit, attach/detach/probe/remove, queue allocation, RSS config, vport config, XDP, stats queries, bandwidth clamp/shaper support, RX buffer preallocation, skb unmapping, and WQ object management.

## Control flow
Probe queries device config and vPort config, allocates EQ/CQ/SQ/RQ queues, configures vPorts, registers filters, and publishes netdevices. TX builds short or long OOB descriptors and GDMA SGLs, posts to SQs, and reclaims via TX CQEs. RX posts page-backed buffers, processes RX CQEs including coalesced completions, runs XDP, updates RSS/indirection state, and fences/destroys RQs during teardown. Management commands use GDMA request headers through the HWC path.

## State and persistence
State spans per-adapter ports, per-port vport handles, queue objects, RX object tables, RSS hash key and indirection table, XDP programs and page pools, preallocated RX buffers, vport use counts, link state work, debugfs nodes, software stats, queried hardware/PHY counters, and net shaper handles. Hardware-visible state includes queue regions, WQ objects, filters, vPort configuration, CQ moderation, and bandwidth clamp settings.

## Dependencies and integration points
It depends on GDMA/HWC, netdevice core, XDP/page_pool, ethtool, debugfs, workqueues, u64 stats sync, net shaper UAPI, and Linux DMA/skb APIs. It integrates Ethernet and RDMA personalities through common GDMA devices.

## Risks and test signals
Risks include hardware bitfield ABI mismatch, queue size and RX/TX buffer limits, short-form vport offset overflow, XDP/page-pool lifetime bugs, DMA unmap leaks, RSS table size constraints, stats count drift when structs change, CQE type handling gaps, queue reset races, and partial teardown after HWC timeout. Tests should cover probe/remove, attach/detach, multi-queue RSS, XDP drop/tx/redirect, TX GSO/checksum formats, RX coalesced CQEs, link changes, shaper bandwidth clamp, and suspend/resume recovery.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/mana.h` completely for this pass (1041 lines, 25117 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/mana.h -->
