# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/pio.c

## Purpose
Implements the optional programmed-I/O data path for b43legacy cards when DMA is not used. It manages four PIO queues, formats TX headers, writes frames into device PIO FIFOs, handles TX completion cookies, receives PIO frames and hardware TX-status reports, and freezes/thaws queues during TX suspension.

## Important APIs, Types, and Functions
Public functions are `b43legacy_pio_init()`, `b43legacy_pio_free()`, `b43legacy_pio_tx()`, `b43legacy_pio_handle_txstatus()`, `b43legacy_pio_rx()`, `b43legacy_pio_tx_suspend()`, `b43legacy_pio_tx_resume()`, `b43legacy_pio_freeze_txqueues()`, and `b43legacy_pio_thaw_txqueues()`. Internal helpers include `generate_cookie()`, `parse_cookie()`, `pio_tx_write_fragment()`, `pio_tx_packet()`, `tx_tasklet()`, queue setup/destruction, and `pio_rx_error()`.

## Control Flow, State, and Persistence
Initialization allocates one queue per PIO MMIO base, discovers each device FIFO size, applies a safety adjustment, and creates a fixed cache of `B43legacy_PIO_MAXTXPACKETS` packet descriptors. TX enqueues an skb on queue1, schedules a tasklet, checks device FIFO packet/byte capacity, generates a firmware TX header with a cookie, writes data words and odd trailing bytes, and moves descriptors from free to queued to running lists. TX status parses the cookie, decrements device FIFO accounting, maps retry counts back into `ieee80211_tx_info`, reports status to mac80211, and frees the descriptor. RX waits for the ready bit, reads a preamble/RX header, treats PIO4 as TX-status transport, allocates an skb for normal frames, reads payload words, and calls `b43legacy_rx()`. State is volatile queue state: list heads, `nr_txfree`, `tx_devq_used`, `tx_devq_packets`, frozen flags, workarounds, and tasklets.

## Dependencies and Integration Points
Depends on b43legacy MMIO accessors, `xmit.c` TX header/RX/TX-status conversion, mac80211 skb control blocks, IRQ lock serialization through `wl->irq_lock`, Linux tasklets and skbuff allocation. `xmit.c` selects PIO versus DMA for TX-status and suspend/resume.

## Risks and Test Signals
Risks include descriptor leaks, bad cookie decoding, FIFO byte accounting underflow, tasklet races with teardown, odd-length write bugs on old core revisions, and RX error recovery. Test with `pio=1`, high TX load, encrypted frames during resume, packet loss/retry reporting, RX FCS errors, teardown while traffic is queued, and queue freeze/thaw around suspend.
