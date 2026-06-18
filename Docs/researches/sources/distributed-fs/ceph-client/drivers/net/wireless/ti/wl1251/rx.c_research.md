# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/rx.c

Purpose: Implements wl1251 receive processing from firmware double buffers into mac80211 SKBs.

Important APIs and functions: `wl1251_rx()` is the entry from IRQ work. Internal helpers are `wl1251_rx_header()`, `wl1251_rx_body()`, `wl1251_rx_status()`, and `wl1251_rx_ack()`.

Control flow: `wl1251_rx()` checks device state, reads the RX descriptor from the current double-buffer slot, reads the frame body after descriptor and padding, builds `ieee80211_rx_status`, submits the SKB through `ieee80211_rx_ni()`, then acknowledges the consumed buffer by writing the appropriate RX_PROC trigger and toggling `wl->rx_current_buffer`.

State and persistence: Uses `wl->data_path` for firmware RX addresses, `wl->rx_current_buffer` for double-buffer selection, `wl->rx_last_id` for packet sequence sanity, `wl->noise` for survey reporting, and `wl->bss_type`/`monitor_present` for status behavior. No persistent storage.

Dependencies and integration points: Depends on IO helpers, ACX TSF interrogation for IBSS beacons, mac80211 RX status conventions, and rate constants from `reg.h`. Called by `wl1251_irq_work()` when RX interrupt bits are active.

Risks: Descriptor `length` is trusted enough to allocate/read after subtracting `PLCP_HEADER_LENGTH`; malformed firmware descriptors could underflow or oversize reads. For IBSS beacons, status construction can sleep through ACX TSF interrogation, so it is intentionally not in atomic context. Rate mapping has ambiguous 1/12 Mbps handling based on modulation bits.

Test signals: RX packet delivery, beacon reception in STA/IBSS, monitor mode decrypt flags, FCS failure reporting, noise survey values, and logs for out-of-sequence RX packet IDs.
