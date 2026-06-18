<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.h

## Purpose
`mtk_eth_soc.h` is the shared contract for the MediaTek SoC Ethernet driver family. It defines register offsets, descriptor layouts, SoC capability bits, per-SoC data, core device state, MAC state, and exported helper prototypes used by the frame engine, GMAC, QDMA/PDMA, PPE flow offload, WED, phylink, XDP, and stats code. This header is not a passive constant bucket: the version-aware inline helpers here decide how PPE FOE bitfields are interpreted on NETSYS v1 versus v2/v3 hardware.

## Important APIs, Types, And Constants
The first major block describes hardware limits and register layouts: QDMA queue sizes, RX/TX DMA buffer sizes, LRO parameters, frame-engine interrupt bits, GDMA controls, PSE queue registers, PDMA/QDMA control bits, MAC registers, SGMII/TRGMII/XGMII controls, reset bits, and PSE port IDs. The descriptor structs `mtk_rx_dma`, `mtk_rx_dma_v2`, `mtk_tx_dma`, and `mtk_tx_dma_v2` encode the 4-word and 8-word DMA formats consumed by the data path. `TX_DMA_*` and `RX_DMA_*` macros expose owner, length, checksum, VLAN, port, PPE reason, and 64-bit address fields.

The central state structures are `struct mtk_eth`, `struct mtk_mac`, `struct mtk_tx_ring`, `struct mtk_rx_ring`, `struct mtk_hw_stats`, and `struct mtk_soc_data`. `mtk_soc_data` carries register map selection, capability flags, required clocks, offload/PPE versioning, hash offset, FOE entry size, DMA descriptor metadata, accounting support, and feature flags. `mtk_eth` aggregates MMIO, DMA device selection, netdev/MAC arrays, IRQs, regmaps, phylink PCS, rings, NAPI instances, DIM counters, DSA metadata, PPE instances, the flow rhashtable, XDP program pointer, and reset-monitor state. `mtk_mac` binds a netdev to a hardware MAC and stores phylink, stats, HWR LRO IPs, and device notifier state.

## Control Flow And Version Selection
The header's inline helpers are used throughout PPE and WED code to choose correct bitfields. `mtk_is_netsys_v1`, `mtk_is_netsys_v2_or_greater`, and `mtk_is_netsys_v3_or_greater` branch on `eth->soc->version`. `mtk_foe_get_entry` computes a FOE entry pointer from `ppe->foe_table`, the hash index, and `soc->foe_entry_size`, making correct SoC metadata mandatory. The `mtk_get_ib1_*`, `mtk_prep_ib1_vlan_layer`, `mtk_get_ib1_pkt_type`, and `mtk_get_ib2_multicast_mask` helpers abstract the incompatible FOE bitfield positions between v1 and later NETSYS layouts. `mtk_interface_mode_is_xgmii` limits internal/USXGMII/10G/5G handling to NETSYS v3 or newer.

## State And Persistence
All state described here is kernel runtime state. Persistent hardware state is represented through register offsets and DMA descriptors, but the header itself stores no data. `mtk_eth` owns long-lived driver allocations for rings, DMA scratch areas, clock handles, PPE objects, and the global flow table for TC flower offload. `mtk_hw_stats` accumulates hardware counters under synchronization. `mtk_rx_ring` keeps page-pool and XDP receive queue state; `mtk_tx_ring` tracks DMA descriptors and free counts. Reset state is tracked in `mtk_eth.reset` with delayed work and hang counters.

## Dependencies And Integration Points
The header depends on kernel DMA, netdevice, phylink, page pool, DIM, rhashtable, BPF/XDP, and bitfield APIs. It includes `mtk_ppe.h`, creating a tight dependency between the Ethernet core and flow offload data formats. Exported prototypes connect to implementation files for stats, register IO, GMAC path setup, TC setup, offload initialization, flow offload commands, flow cleanup, and DMA device switching. WED code depends on `struct mtk_eth`, PPE arrays, `mtk_eth_set_dma_device`, SoC version/capability helpers, PSE port constants, and descriptor address helpers.

## Risks
The dominant risk is version drift: a wrong `soc->version`, `offload_version`, `hash_offset`, or `foe_entry_size` causes PPE hashes, FOE entries, and DMA descriptors to be interpreted incorrectly. DMA length and 64-bit address macros are used directly in hot paths and must match descriptor layout. Capability bit combinations define valid mux/path setups, so new SoCs must update these carefully. Since `mtk_eth` contains shared data used by NAPI, reset work, offload callbacks, and WED attach/detach, locking and lifetime rules in implementation files must align with this structure.

## Test Signals
Useful signals include successful probe for each SoC match data, correct clock acquisition from `required_clks`, traffic through every GMAC path in the capability set, TX/RX checksum/TSO/VLAN feature tests, XDP pass/drop/tx/redirect counters, phylink mode changes, TC flower offload add/delete/stats, WED attach on supported SoCs, and reset-monitor recovery. Hardware register dumps and ethtool stats should reflect descriptor counters without DMA hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.h -->
