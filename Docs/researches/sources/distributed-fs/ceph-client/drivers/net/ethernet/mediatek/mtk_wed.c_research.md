<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.c

## Purpose
`mtk_wed.c` implements MediaTek WED, the Wireless Ethernet Dispatch block that accelerates traffic between the Ethernet/PPE subsystem and MediaTek WLAN DMA engines. It registers WED hardware instances, exposes an operation table to WLAN drivers, attaches WLAN devices to available WED blocks, allocates TX/RX buffer managers and rings, configures WED/WDMA/WPDMA register mirrors, handles reset/start/stop/detach, coordinates Wi-Fi offload flow enablement, supports RRO/WOCPU paths on newer SoCs, and routes TC flower offload commands through the Ethernet PPE.

## Important APIs, Types, And Functions
Global state is `hw_list[3]` protected by `hw_lock`. SoC variants are described by `mt7622_data`, `mt7986_data`, and `mt7988_data`, which carry register offsets and descriptor sizes. Hardware registration is `mtk_wed_add_hw`; cleanup is `mtk_wed_exit`. WLAN-facing operations are assembled in `mtk_wed_add_hw` as `struct mtk_wed_ops`: attach, TX/RX ring setup, txfree ring setup, start/stop, reset DMA, register read/write, IRQ get/mask, detach, PPE check, TC setup, HW RRO start, RRO/MSDU page/IND RX ring setup, and MCU message update.

Attach/detach and lifecycle functions include `mtk_wed_assign`, `mtk_wed_attach`, `__mtk_wed_detach`, `mtk_wed_detach`, `mtk_wed_hw_init_early`, `mtk_wed_hw_init`, `mtk_wed_start`, `mtk_wed_stop`, `mtk_wed_deinit`, `mtk_wed_dma_enable`, `mtk_wed_dma_disable`, `mtk_wed_reset_dma`, `mtk_wed_rx_reset`, `mtk_wdma_rx_reset`, and `mtk_wdma_tx_reset`. Buffer/ring management includes TX buffer allocation/free, AMSDU buffer allocation/init/free, RX BM/HWRRO allocation/free/init, WDMA RX/TX ring setup, WED TX/RX ring setup, txfree ring setup, RRO and page ring setup, and indirect command ring setup. Flow accounting APIs are `mtk_wed_flow_add` and `mtk_wed_flow_remove`.

## Control Flow
`mtk_wed_add_hw` is called by the Ethernet driver with the WED DT node, `struct mtk_eth`, WDMA base/physical address, and index. It resolves the platform device, IRQ, and syscon regmap, publishes `mtk_soc_wed_ops` under RCU, creates `mtk_wed_hw`, selects SoC data by `eth->soc->version`, sets up v1 mirror/hifsys maps when needed, creates debugfs, and stores the instance in `hw_list`.

WLAN attach requires the caller to hold RCU. `mtk_wed_attach` module-pins this driver, selects a compatible unused hardware block, sets DMA mask and DMA device mapping, allocates TX buffer manager memory, allocates v3 AMSDU buffers, optionally allocates RRO resources, initializes early hardware, adjusts coherence mappings, reads revision, and initializes WOCPU support when RX acceleration is enabled. On failure it calls the detach path.

Start allocates RX buffers when RX capability exists, creates missing WDMA RX rings, initializes WED hardware once, configures interrupts, enables extension error interrupts, configures RRO through the MCU on RX-capable hardware, enables 512-WCID and AMSDU support, enables WED/WDMA/WPDMA DMA agents, and marks the device running. Ring setup redirects WLAN WPDMA rings through WED: WLAN-provided registers become WED-facing rings while WED-owned DMA rings are programmed into WPDMA/WDMA control registers. Reset paths carefully disable and poll each agent, reset indexes/FIFOs, reset buffer managers, coordinate WOCPU state, and rebuild descriptor rings.

PPE integration occurs through `mtk_wed_ppe_check`, which receives a CPU reason and FOE hash from WLAN/WED and calls `mtk_ppe_check_skb` for unbind-rate hits. TC setup on WED-backed netdevs registers flow-block callbacks that call `mtk_flow_offload_cmd` with the WED hardware index. `mtk_wed_flow_add/remove` toggle WLAN offload callbacks around a per-WED flow count and update extension interrupt masks.

## State And Persistence
`struct mtk_wed_hw` persists from `mtk_wed_add_hw` to `mtk_wed_exit`; `struct mtk_wed_device` is owned by the WLAN side but populated and zeroed by attach/detach. DMA-backed TX BM, RX BM, RRO, AMSDU, WDMA, and WED rings persist while attached. Hardware state spans WED, WDMA, WPDMA, PCIe interrupt mapping, hifsys/mirror syscons, and WOCPU reserved memory/MCU state. `num_flows` persists per WED hardware and gates WLAN offload enable/disable.

## Dependencies And Integration Points
This file depends on platform/OF/syscon/reserved-memory APIs, DMA mapping, debugfs, the public `linux/soc/mediatek/mtk_wed.h`, private `mtk_wed.h`, register definitions, `mtk_wed_wo.h`, `mtk_eth_soc.h`, `mtk_ppe.h`, flow offload, and TC. It integrates bidirectionally with WLAN drivers via `mtk_soc_wed_ops`, with Ethernet via `struct mtk_eth`, PPE arrays and DMA device switching, with WOCPU firmware through MCU messages, and with TC flower through the same offload command path as Ethernet netdevs.

## Risks
This is high-risk hardware orchestration. Resource allocation loops in TX/RX/HWRRO/AMSDU paths have partial allocation failure cases that rely on detach/free routines to clean up; leaks or double frees can occur if size fields do not match allocation counts. Reset sequencing is version-specific and depends on polling busy bits; missed busy conditions can leave DMA agents wedged. `hw_list` indexing assumes up to three instances and uses `!hw->index` in one detach coherence condition, which only reasons about two peers. `mtk_wed_flow_remove` decrements `num_flows` without an explicit underflow guard after initial checks. Raw ioremap in WO reset assumes the reset address is valid. DMA device switching for coherent WLAN paths must be balanced on detach.

## Test Signals
Test attach/detach loops for PCIe and AXI WLAN devices, v1/v2/v3 SoCs, RX-capable and TX-only configurations, HW RRO on/off, AMSDU on v3, WED start/stop/reset while traffic is active, suspend-like WLAN reset callbacks through `mtk_wed_fe_reset`, TC flower WED redirect flows, WED debugfs counters, extension interrupt errors, and fault injection for DMA allocation failures. Traffic tests should confirm PPE/WED offloaded flows enable WLAN callbacks once, disable when the last flow is removed, and recover after WED reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.c -->
