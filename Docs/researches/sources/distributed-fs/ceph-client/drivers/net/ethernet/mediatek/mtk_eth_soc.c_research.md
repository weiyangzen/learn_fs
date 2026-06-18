# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.c

## Purpose
`mtk_eth_soc.c` is the main MediaTek SoC Ethernet frame-engine driver. It implements platform probe/remove, SoC register maps, MDIO, phylink MAC operations, shared QDMA/PDMA ring management, RX/TX data paths, XDP, page-pool allocation, hardware LRO controls, PPE/offload integration, DSA special-tag handling, interrupt/NAPI service, DIM interrupt moderation, reset/hang recovery, ethtool operations, and SoC match data for MT2701/MT762x/MT798x/RT5350 families.

## Important APIs, Types, and Functions
Top-level data is described in `mtk_eth_soc.h`: `struct mtk_eth` is the shared frame-engine state, `struct mtk_mac` is per-netdev MAC state, and `struct mtk_soc_data` supplies per-SoC capabilities, register maps, descriptor sizes, clocks, offload version, PPE count, and DMA limits. This C file defines `mtk_reg_map`, `mt7628_reg_map`, `mt7986_reg_map`, and `mt7988_reg_map`; per-SoC `mtk_soc_data` instances; and the `of_mtk_match[]` device table.

The MMIO helpers are `mtk_w32()`, `mtk_r32()`, and `mtk_m32()`. MDIO support is implemented by `_mtk_mdio_{read,write}_c22()`, `_mtk_mdio_{read,write}_c45()`, the `mii_bus` wrappers, `mtk_mdio_config()`, `mtk_mdio_init()`, and `mtk_mdio_cleanup()`.

Phylink integration is through `mtk_phylink_ops`: `mtk_mac_select_pcs()`, `mtk_mac_prepare()`, `mtk_mac_config()`, `mtk_mac_finish()`, `mtk_mac_link_down()`, `mtk_mac_link_up()`, and EEE LPI methods. RT5350 uses stub `rt5350_phylink_ops` because that hardware lacks exposed MAC control registers.

The packet path centers on `mtk_start_xmit()`, `mtk_tx_map()`, `mtk_tx_set_dma_desc_v1/v2()`, `mtk_poll_tx_qdma()`, `mtk_poll_tx_pdma()`, `mtk_poll_rx()`, `mtk_napi_tx()`, and `mtk_napi_rx()`. Allocation and teardown are handled by `mtk_init_fq_dma()`, `mtk_tx_alloc()`, `mtk_rx_alloc()`, `mtk_dma_init()`, `mtk_dma_free()`, `mtk_tx_clean()`, and `mtk_rx_clean()`. XDP support uses `mtk_xdp_setup()`, `mtk_xdp_run()`, `mtk_xdp_submit_frame()`, and `mtk_xdp_xmit()`.

## Control Flow
Probe starts in `mtk_probe()`: allocate `struct mtk_eth`, map MMIO, configure DMA masks, initialize locks/work/DIM state, acquire syscon regmaps (`ethsys`, optional `infra`, optional `pctl`), enable coherency hooks, create SGMII PCS instances, set up SRAM pools, register WED hardware, acquire IRQs and clocks, initialize hardware, add child MAC netdevs, request IRQs, create MDIO, initialize PPE/offload, register netdevs, create a dummy NAPI device, and start the DMA hang monitor.

Opening a netdev runs `mtk_open()`: connect phylink, start shared DMA only for the first user via `dma_refcnt`, start PPE blocks, configure GDM forwarding/PPE selection for each MAC, update PPE MTU, enable NAPI and IRQs, then start phylink and TX queues. Stopping reverses that path in `mtk_stop()`, but shuts down DMA only when the last netdev user drops the refcount.

TX flow validates VLAN/GSO state, locks `page_lock` because multiple netdev queues share one ring, checks `MTK_RESETTING`, maps SKB head/frags into descriptors, updates QDMA/PDMA producer indexes, and stops queues when descriptor pressure is high. TX completion runs under NAPI, unmaps DMA, frees SKBs or XDP frames, updates byte/packet accounting, wakes queues when free descriptors recover, and feeds DIM samples.

RX flow chooses the normal or HWLRO ring, reads a completed descriptor, derives source MAC and PPE hash/reason, allocates a replacement buffer before handing the old buffer upward, runs XDP when page-pool backed, builds an SKB for `XDP_PASS` or non-XDP paths, sets checksum/hash/protocol metadata, handles DSA special-tag metadata for NETSYS v1, invokes PPE learning checks for selected reasons, gives packets to GRO, rewrites the descriptor with the replacement DMA address, and advances the hardware CPU index.

Reset flow is workqueue based. TX timeout and the monitor can schedule `mtk_pending_work()`, which takes RTNL, sets `MTK_RESETTING`, prepares PPE/FE/GMAC for reset, coordinates WED reset, stops running netdevs, performs warm hardware init, reopens previously running devices, restores PPE link state, clears `MTK_RESETTING`, and signals WED completion.

## State and Persistence
Runtime state is volatile and split between software structs, DMA-coherent descriptor rings, page-pool pages, syscon/MMIO registers, and hardware counters. `eth->dma_refcnt` persists shared DMA ownership across multiple netdev opens. `eth->state` tracks `MTK_HW_INIT` and `MTK_RESETTING`. `eth->prog` is the shared RCU XDP program, so enabling XDP on one netdev affects page-pool direction and shared DMA behavior. `mac->hwlro_ip[]` and `hwlro_ip_cnt` mirror ethtool-configured LRO destination IP filters into hardware registers. `mac->hw_stats` accumulates hardware counter deltas under `u64_stats_sync`. No durable storage is written.

## Dependencies and Integration Points
The driver depends on platform device probing, device tree child `mediatek,eth-mac` nodes, syscon/regmap resources, reset/clock/runtime PM frameworks, phylink and `pcs-mtk-lynxi`, MDIO, DMA mapping, page-pool, XDP/BPF, DSA, ethtool, NAPI, Net DIM, generic allocator SRAM pools, and MediaTek-specific PPE/WED modules in the same directory. Build dependencies are selected in `Kconfig`; object composition is controlled by the local Makefile.

## Risks
Shared-ring coordination is the main correctness risk: multiple netdevs, XDP frames, SKBs, QDMA linked descriptors, and PDMA compatibility descriptors all share `page_lock`, descriptor counts, and cleanup paths. Error unwinding in allocation paths can leak buffers if a later ring/page-pool allocation fails after earlier allocations. XDP is intentionally incompatible with HWLRO and limited by page-pool buffer size; MTU and feature toggles must preserve those constraints. Reset recovery races are complex because WED reset can drop RTNL and the driver reruns preliminary reset setup to compensate. SoC data mistakes in descriptor sizes, DMA limits, IRQ masks, capability bits, or register maps can cause silent ring corruption or unmapped register writes. The probe path also registers netdevice notifiers per MAC under QDMA; notifier lifecycle must stay paired with unregister/free paths.

## Test Signals
High-value tests include boot/probe on each compatible string, MDIO C22/C45 transactions, phylink mode coverage for RGMII/TRGMII/SGMII/2500BASE-X/internal/USXGMII cases, open/close sequencing with one, two, and three MACs, traffic through QDMA and PDMA SoCs, VLAN/TSO/checksum offloads, DSA special-tag paths, XDP pass/drop/redirect/tx/ndo_xmit including fragmented frames, HWLRO ethtool rule add/delete and feature toggling, MTU changes with PPE updates, WED/PPE offload init and reset, interrupt moderation changes from DIM, forced TX timeout and DMA hang monitor recovery, module remove after active traffic, and KASAN/KMEMLEAK checks for ring allocation failure paths.
