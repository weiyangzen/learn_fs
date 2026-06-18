# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/pio.c

## Purpose
`pio.c` implements Programmed I/O data transfer support for the B43 driver. It is the non-DMA transmit and receive path used when PIO is forced or DMA is unavailable/fails. It allocates PIO queues, maps mac80211 traffic priorities to hardware queues, writes TX headers and frames into PIO FIFOs, receives frames from the direct FIFO RX path, handles TX status cookies, applies queue backpressure, and suspends/resumes TX queues around power-management events.

## Important APIs And Functions
- `b43_pio_init(struct b43_wldev *dev)`: disables big-endian MAC mode, clears the shared RX padding offset, allocates four QoS TX queues plus multicast and one RX queue, and enables direct FIFO RX through the DMA helper.
- `b43_pio_free(struct b43_wldev *dev)`: frees allocated PIO queues when PIO is active and drops any queued SKBs through `ieee80211_free_txskb()`.
- `b43_pio_tx(struct b43_wldev *dev, struct sk_buff *skb)`: public TX entry. Selects the target queue, validates queue capacity, applies mac80211 queue stop on overflow, generates a TX header, writes data to hardware, and handles `-ENOKEY` by dropping the frame without unencrypted transmission.
- `b43_pio_handle_txstatus(struct b43_wldev *dev, const struct b43_txstatus *status)`: maps firmware TX status cookies back to a PIO queue/packet slot, fills mac80211 status, accounts buffer usage and packet slots, returns the slot to the free list, and wakes a previously stopped queue.
- `b43_pio_rx(struct b43_pio_rxqueue *q)`: drains available RX frames until the hardware has no ready frame or a safety cap trips.
- `b43_pio_tx_suspend()` / `b43_pio_tx_resume()`: set and clear PIO TX suspend request bits on all queues, wrapped with power-saving control.
- Internal helpers include cookie generation/parsing, queue base selection, setup/destroy routines, priority queue selection, 2-byte/4-byte queue writers, frame TX/RX workers, and per-queue suspend/resume helpers.

## Control Flow
Initialization starts in `b43_pio_init()`. It programs MAC/shared-memory PIO settings, creates TX queues for AC_BK, AC_BE, AC_VI, AC_VO, and multicast, then creates RX queue 0 and enables direct FIFO RX. Error handling unwinds already-created queues in reverse order.

TX flow begins at `b43_pio_tx()`. Multicast frames marked `IEEE80211_TX_CTL_SEND_AFTER_DTIM` are routed to the multicast queue and get `IEEE80211_FCTL_MOREDATA`; other frames use QoS priority mapping when QoS is enabled or AC_BE otherwise. The function checks total rounded header plus frame size against `q->buffer_size`, checks packet slots, may stop the corresponding mac80211 queue with `b43_stop_queue()`, and calls `pio_tx_frame()`. `pio_tx_frame()` chooses the first free metadata slot, generates a nonzero cookie with queue ID in the high nibble and packet index in the low 12 bits, builds the B43 TX header in `wl->pio_scratchspace`, stores multicast cookie state in shared memory when needed, writes the header and SKB payload to the PIO FIFO, removes the slot from the free list, and updates buffer accounting.

Hardware write width depends on core revision. Revisions before 8 use 16-bit PIO TXCTL/TXDATA and mask high/low byte lanes for odd tails. Revisions 8 and newer use 32-bit TXCTL/TXDATA and byte-lane masks for 1-3 byte tails. Both paths set frame-ready, stream header then payload, and finish by setting EOF.

TX completion enters through `b43_pio_handle_txstatus()`, normally dispatched from `xmit.c` when PIO is active. The cookie is parsed back to a queue and packet slot. The SKB status is filled, buffer usage and free slots are restored, `ieee80211_tx_status_skb()` returns the SKB to mac80211, and a stopped queue is woken.

RX flow is interrupt-driven through `b43_pio_rx(dev->pio.rx_queue)` in `main.c` when PIO transfers are active. `pio_rx_frame()` checks FRAMERDY, acknowledges it, waits briefly for DATARDY, reads the firmware RX header into `wl->pio_scratchspace`, validates length and FCS policy, allocates an SKB with expected two-byte alignment padding plus optional hardware padding, reads the payload with 16-bit or 32-bit block I/O and tail handling, and hands the frame to `b43_rx()`. Errors acknowledge DATARDY to discard the frame and continue draining.

## State And Persistence
Queue objects persist in `dev->pio` and hold `mmio_base`, `buffer_size`, `buffer_used`, `free_packet_slots`, `stopped`, `queue_prio`, revision shortcut, fixed packet metadata array, and free-list head. Packet slots persist until TX status arrives. Each active `struct b43_pio_txpacket` owns the SKB pointer and index that the firmware cookie later resolves. Queue backpressure state persists through `q->stopped`; status completion wakes the last stored `queue_prio`.

`wl->pio_scratchspace` and `wl->pio_tailspace` are shared PIO staging buffers protected by the broader `wl->mutex` contract described in `b43.h`. Multicast DTIM state persists via `B43_SHM_SH_MCASTCOOKIE`, allowing firmware to clear the more-data bit on the last multicast frame. RX does not persist SKBs internally; successful frames are immediately passed to the normal B43 RX path.

## Dependencies And Integration Points
- Uses hardware accessors from `b43.h`: MMIO reads/writes, shared memory writes, block I/O, MAC control, PIO base constants, and `b43_using_pio_transfers()`.
- Uses DMA helper `b43_dma_direct_fifo_rx()` to enable direct FIFO RX even though normal DMA structures are not used.
- Uses TX/RX framing helpers from `xmit.h` and main driver paths: `b43_txhdr_size()`, `b43_generate_txhdr()`, `b43_fill_txstatus_report()`, and `b43_rx()`.
- Integrates with mac80211 through SKBs, `IEEE80211_SKB_CB`, queue mappings, TX control flags, `ieee80211_tx_status_skb()`, and `ieee80211_free_txskb()`.
- Called from `main.c` for device init/free, RX draining, and TX path selection; `xmit.c` forwards TX status and suspend/resume events when PIO is active.

## Risks
- The rev >= 8 TX path ends `pio_tx_frame_4byte_queue()` with `b43_piotx_write32(q, B43_PIO_TXCTL, ctl)` instead of the rev8 symbolic offset `B43_PIO8_TXCTL`. Both are currently zero, but the mixed symbolic name is fragile and can mislead future edits.
- `q->buffer_size = 1920` for rev >= 8 is explicitly marked `FIXME this constant is wrong`; wrong sizing can cause false backpressure or hardware FIFO overflow.
- Cookie parsing assumes queue index plus one maps exactly to 0x1000..0x5000 and that the packet index remains below 32. Corruption or firmware bugs can drop statuses and leak queue accounting.
- TX status handling dereferences `pack->skb` without a null guard after cookie parsing. Duplicate or stale statuses would risk a null dereference or bad accounting.
- RX length validation only rejects `len > 0x700` and zero; malformed headers that pass those checks rely on downstream parsing.
- Queue stopping stores a single `queue_prio` per PIO queue. If mappings or QoS behavior change, waking the wrong mac80211 queue is possible.
- PIO uses shared scratch and tail buffers; callers must maintain serialization.

## Test Signals
- Build with PIO enabled (`B43_PIO` / `B43_BCMA_PIO`) and with DMA enabled to catch integration drift.
- Runtime smoke tests should include forced PIO via module parameter, DMA-fallback-to-PIO paths, association, ping/throughput, multicast buffered traffic after DTIM, and traffic across all QoS access categories.
- Fault-oriented signals: `PIO: TX packet longer than queue`, `PIO: TX packet overflow`, `PIO transmission failure`, `PIO RX timed out`, and `PIO RX error` logs.
- Stress tests should watch for queue stop/wake balance, no SKB leaks on init failure/free, no underflow in `buffer_used`, and no RX drain loops hitting the `count > 10000` warning.
