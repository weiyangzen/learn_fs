# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/dma.c

## Purpose
Implements the MT7601U-specific USB DMA datapath. It allocates RX/TX URBs, wraps TX SKBs with MT7601U DMA headers, submits bulk URBs, parses RX DMA aggregation segments into mac80211 SKBs, and completes TX/RX work through tasklets.

## Important APIs, Types, And Functions
Exports `mt7601u_dma_enqueue_tx()`, `mt7601u_dma_init()`, and `mt7601u_dma_cleanup()`. Key internal functions include RX parsing (`mt7601u_rx_next_seg_len()`, `mt7601u_rx_process_seg()`, `mt7601u_rx_skb_from_seg()`), URB callbacks (`mt7601u_complete_rx()`, `mt7601u_complete_tx()`), tasklets (`mt7601u_rx_tasklet()`, `mt7601u_tx_tasklet()`), TX submission (`mt7601u_dma_submit_tx()`), and queue allocation/free helpers.

## Control Flow
RX init allocates pages and URBs, submits all RX URBs, and completions add pending entries then schedule the RX tasklet. The tasklet parses one or more DMA segments from the page, handles RXWI/FCE metadata, builds SKBs with optional page frags, delivers them through `ieee80211_rx_list()`, resubmits the URB, and batches `netif_receive_skb_list()`. TX wraps the SKB with DMA info/padding, submits a bulk URB to the mapped endpoint, and completion queues the SKB for TX status processing and wakes mac80211 queues when near-full thresholds clear.

## State And Persistence
State includes RX ring `start/end/pending`, TX per-endpoint `start/end/used`, URB pointers, RX pages, queued SKBs, tasklets, `tx_skb_done`, and driver state bits for removed/initialized/stat reading. Hardware-visible state is the DMA header prepended to transmitted SKBs.

## Dependencies And Integration Points
Depends on Linux USB bulk APIs, tasklets, mac80211 RX/TX status, MT7601U DMA format from `dma.h`, RXWI processing in `mac.c`, USB endpoint discovery in `usb.c`, and statistics work scheduling.

## Risks
RX aggregation parsing must reject invalid lengths without overrunning the page. Page-frag ownership is subtle when replacing large RX pages. TX URB completion after removal must not touch freed queues. Queue stop/wake thresholds must avoid deadlock. Cleanup poisons RX URBs before killing tasklets and freeing pages.

## Test Signals
RX with single and aggregated segments, malformed frame rejection, TX queue full/wake behavior, unplug during RX/TX, DMA cleanup on init failure, TX status delivery after completion, and no page/URB leaks under USB fault injection.
