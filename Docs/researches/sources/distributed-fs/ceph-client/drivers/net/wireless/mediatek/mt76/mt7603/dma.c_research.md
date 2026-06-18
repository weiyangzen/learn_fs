# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/dma.c

## Purpose
MT7603 DMA ring setup, RX packet dispatch, TX completion NAPI, power-save loopback buffering, and DMA cleanup.

## Important APIs, Types, And Functions
- `wmm_queue_map` maps mac80211 access categories to hardware TX ring indices.
- `mt7603_rx_loopback_skb()` handles MCU/RX loopback packets used for station power-save buffering, rewrites queue indices, marks mac80211 buffered state, and stores frames in per-station `psq`.
- `mt7603_queue_rx_skb()` classifies RX descriptors as TX status, MCU event, normal frame, or loopback frame and dispatches to `mt7603_mac_add_txs()`, `mt76_mcu_rx_event()`, `mt7603_mac_fill_rx()`, or free.
- `mt7603_init_rx_queue()` allocates an RX ring and enables the matching RX-done IRQ.
- `mt7603_poll_tx()` cleans MCU and data TX queues, re-enables TX-done interrupts, polls station airtime, and schedules the common TX worker.
- `mt7603_dma_init()` attaches mt76 DMA, resets WPDMA indices, resets PSE client, allocates data/PSD/MCU/beacon/CAB TX queues and MCU/main RX queues, initializes mt76 queues, and enables TX NAPI.
- `mt7603_dma_cleanup()` disables DMA and calls common cleanup.

## Control Flow
Hardware init calls `mt7603_dma_init()`. RX NAPI dequeues DMA buffers and calls this file's RX callback. MCU ring frames that are events enter the common MCU response queue; normal data frames are parsed in `mac.c` and delivered to shared mt76 RX. TX-done interrupts schedule `mt7603_poll_tx()`, which performs cleanup twice around `napi_complete_done()` to catch completions racing with IRQ re-enable.

## State And Persistence
State includes hardware queues in `dev->mphy.q_tx[]`, `dev->mt76.q_mcu[]`, `dev->mt76.q_rx[]`, NAPI state, station PS queues, `dev->tx_dma_check`, and `dev->rx_pse_check`. No durable persistence exists.

## Dependencies And Integration Points
Depends on common mt76 DMA helpers, mt7603 descriptors from `mac.h`, queue ops from `../dma.h`, MCU response handling, and MAC RX/TX status parsers. Power-save queueing integrates with `main.c` station PS callbacks.

## Risks
Descriptor type parsing must reject malformed lengths before dereference. Loopback buffering caps per-station `psq` at 64 by dropping oldest frames; traffic loss is expected under excessive sleeping-station backlog. IRQ/NAPI re-enable ordering is critical to avoid stuck queues. DMA reset/cleanup must coordinate with watchdog reset logic.

## Test Signals
Run bidirectional traffic across all ACs, firmware command traffic, TX status reporting, sleeping STA buffered frames, RX malformed/FCS frames, and driver remove. Check queue debugfs, TX/RX NAPI counters, PS frame release, and absence of IRQ storms or disabled-ring stalls.
