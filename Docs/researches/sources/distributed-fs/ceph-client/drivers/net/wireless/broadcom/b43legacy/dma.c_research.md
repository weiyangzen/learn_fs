# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/dma.c

## Purpose
Implements b43legacy DMA ring allocation, controller setup/reset, TX descriptor submission, TX status completion, RX buffer recycling, DMA error handling support, and queue suspend/resume. It is the high-throughput transfer backend selected unless PIO is forced or DMA mask setup fails.

## Important APIs, Types, and Functions
Public APIs are `b43legacy_dma_init`, `b43legacy_dma_free`, `b43legacy_dma_tx`, `b43legacy_dma_handle_txstatus`, `b43legacy_dma_rx`, `b43legacy_dma_tx_suspend`, and `b43legacy_dma_tx_resume`. Important internal helpers include `op32_fill_descriptor`, `request_slot`, `b43legacy_dmacontroller_rx_reset`, `b43legacy_dmacontroller_tx_reset`, `b43legacy_dma_mapping_error`, `setup_rx_descbuffer`, `dmacontroller_setup`, `b43legacy_setup_dmaring`, `generate_cookie`, `parse_cookie`, and `dma_tx_fragment`.

## Control Flow
Initialization probes 30-bit versus 32-bit address-extension support, sets DMA masks, obtains SSB translation bits, creates six TX rings and one or two RX rings, allocates coherent descriptor pages, preallocates RX skbs, and enables controller registers. TX maps each skb into two descriptors: a cached firmware TX header descriptor and a payload descriptor, with bounce-buffer fallback for unsupported DMA addresses. When free slots fall below two descriptors, the corresponding mac80211 queue is stopped. TX status parses the cookie back to ring/slot, validates in-order completion, unmaps descriptors, fills mac80211 retry/ACK status, frees ownership via `ieee80211_tx_status_irqsafe`, updates ring counters, and wakes queues/work. RX walks from software `current_slot` to hardware slot, handles RX-ring 3 TX-status packets on older cores, swaps in a fresh skb before unmapping the completed one, strips frame offset, and calls `b43legacy_rx`.

## State and Persistence
State is in `struct b43legacy_dmaring`: coherent descriptor memory, metadata array, TX header cache, DMA base, current/used slots, stopped flags, queue priority, and debug high-water marks. DMA mappings persist only until completion or ring teardown. RX descriptors persist for the ring lifetime and are recycled.

## Dependencies and Integration Points
Depends on Linux DMA mapping APIs, SSB DMA translation, skb allocation, mac80211 queue/status APIs, b43legacy xmit header generation, debugfs dynamic toggles, and main IRQ dispatch. It integrates with `b43legacy_wldev->dma` and `b43legacy_using_pio` fallback logic.

## Risks
The current `priority_to_txring` returns `tx_ring1` unconditionally before its detailed mapping, so queue priority/ring-priority behavior is effectively disabled. TX completion assumes in-order status per ring; out-of-order firmware reports can leak descriptors and stall DMA. Mapping failure rollback must restore ring counters exactly. RX buffer replacement failure drops frames but must keep descriptor ownership coherent. Queue wake logic around `tx_queue_stopped` is subtle.

## Test Signals
Exercise sustained TX/RX, DMA mask fallback to PIO, queue stop/wake under ring pressure, debug DMA overflow injection, RX on both ring 0 and ring 3 for older cores, encrypted TX drops with missing keys, suspend/resume DMA suspend, and module unload after traffic. DMA API debug and lockdep are valuable.
