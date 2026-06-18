# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/dma.c

Purpose: DMA ring configuration, queue allocation, interrupt enablement, WED integration, and reset/cleanup for MT7915-family devices.

Important APIs: `mt7915_dma_prefetch`, `mt7915_dma_start`, `mt7915_dma_init`, `mt7915_dma_reset`, and `mt7915_dma_cleanup`. Internal helpers configure queue IDs/interrupt masks, initialize TX queues, poll TX completion NAPI, disable/enable DMA, and set prefetch windows.

Control flow: `mt7915_dma_config` maps logical RX/TX/MCU queues to chip-specific WFDMA engines, interrupts, and hardware ring ids. Init attaches DMA, disables/reset WFDMA, configures WED if active, allocates main/ext phy TX rings, MCU WM/WA/FWDL rings, MCU event RX rings, data RX rings, txfree RX rings, initializes NAPI/queues, and enables DMA. Start enables global WFDMA bits, computes interrupt masks by band/DBDC/WED state, optionally starts WED and RX stats, then enables interrupts. Reset drains TX/RX/MCU queues, optionally resets WFSYS, resets WED/DMA queues/tokens, restarts RX queues, and re-enables DMA.

State and persistence: mutable state includes `wfdma_mask`, `q_int_mask`, `q_id`, queue descriptors, rx token size, WED queue flags/pointers, NAPI state, and interrupt masks.

Dependencies and integration: depends on mt76 DMA core, mt76_connac queue helpers, MediaTek WED offload APIs, chip predicates, register definitions, and reset code in `init.c`/`mac.c`.

Risks: chip-specific queue mappings are dense and easy to break. WED paths alter ring bases, queue IDs, token sizing, and interrupts. Reset must avoid resetting WED txfree queues incorrectly and must preserve NAPI ordering.

Test signals: boot and traffic on MT7915, MT7916, MT7981/7986, DBDC with hif2, WED on/off and RX-capable WED, DMA reset during traffic, txfree accounting, interrupt storm/idle behavior, and NAPI cleanup on unload.
