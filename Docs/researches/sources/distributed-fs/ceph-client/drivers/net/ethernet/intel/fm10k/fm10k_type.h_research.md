# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_type.h

## Purpose
Defines the central fm10k hardware contract: PCI IDs, queue/vector limits, error codes, register offsets and bitfields, descriptor formats, bus/stat/fault structures, DGLORT configuration, PF/VF operation tables, VF state, IOV state, hardware identity, and the top-level `struct fm10k_hw`.

## Important APIs, Types, and Functions
Important constants include device IDs, queue and vector maxima, PCIe capability offsets, fm10k error codes, PF/VF register offsets, DMA control bits, DGLORT and VLAN constants, TQMAP/RQMAP table sizes, stats registers, interrupt moderation registers, VF control registers, reset/queue-disable timeouts, and descriptor multiple requirements. Core types include `fm10k_bus_info`, `fm10k_hw_stat`, `fm10k_hw_stats_q`, `fm10k_hw_stats`, `fm10k_dglort_cfg`, `fm10k_fault`, `fm10k_mac_ops`, `fm10k_mac_info`, `fm10k_swapi_info`, `fm10k_vf_info`, `fm10k_iov_ops`, `fm10k_iov_info`, `fm10k_info`, `fm10k_hw`, `fm10k_tx_desc`, `fm10k_tx_desc_cache`, `fm10k_rx_desc`, and `fm10k_ftag`.

## Control Flow
The header has no direct execution. It controls runtime dispatch through function-pointer tables in `fm10k_mac_ops` and `fm10k_iov_ops`, and it drives register access/control-flow decisions in PF, VF, common, mailbox, and TX/RX code through named offsets and masks.

## State and Persistence Behavior
`struct fm10k_hw` is the persistent in-memory device state for the driver instance, carrying MMIO base, OS backpointer, MAC state, bus state, IOV state, PF/VF mailbox state, switch API status, and PCI identity. `struct fm10k_vf_info` is PF-owned persistent state for each VF, including mailbox, stats, rate, GLORT, VLANs, MAC, VSI, and capability/enabled flags. Hardware-persistent state is represented by register definitions and descriptor layouts. TX/RX descriptors, FTAG, queue stats, fault records, and TLV-related structs are ABI-sensitive because hardware or firmware consumes them directly.

## Dependencies and Integration Points
Includes Linux integer, byteorder, and Ethernet helpers plus `fm10k_mbx.h`. It is included across the fm10k driver and underpins `fm10k_common`, PF/VF ops, TLV handling, mailbox setup, queue programming, interrupt moderation, stats, and netdev TX/RX paths.

## Risks
This is a high-blast-radius hardware ABI header. Changing register offsets, bit masks, descriptor layout, struct alignment, queue/vector maxima, or operation table signatures can break PF, VF, and data path behavior. The TDLEN ITR-scale software handoff between PF and VF is documented here and must remain consistent with both implementations. `struct fm10k_vf_info` requires `mbx` as the first field because PF VF handlers cast mailbox pointers back to VF info. `fm10k_hw_stats` only sizes queue stats for `FM10K_MAX_QUEUES_PF`, which matches PF max rather than absolute hardware max.

## Test Signals
Build coverage across PF and VF drivers, register programming smoke tests, descriptor size/layout checks, endian/bitfield validation, PF and VF probe, SR-IOV VF allocation, queue reset/start/stop, TX/RX descriptor handling, VLAN/RSS/RETA programming, interrupt moderation, stats aggregation and reset rebind, fault capture, TDLEN ITR-scale handoff, and mailbox handler casts are the primary signals.
