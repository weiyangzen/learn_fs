# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/tx.c

Purpose: Implements wl1251 transmit queue processing, firmware TX descriptor construction, double-buffer submission, TX completion processing, mac80211 status reporting, and TX flush.

Important APIs and functions: Public driver entry points are `wl1251_tx_work()`, `wl1251_tx_complete()`, and `wl1251_tx_flush()`. Internal helpers include `wl1251_tx_path_status()`, `wl1251_tx_id()`, `wl1251_tx_fill_hdr()`, `wl1251_tx_send_packet()`, `wl1251_tx_trigger()`, `wl1251_tx_packet_cb()`, and `enable_tx_for_packet_injection()`.

Control flow: mac80211 queues SKBs in `main.c`; `wl1251_tx_work()` wakes ELP once, drains the software queue, checks firmware double-buffer availability, assigns a completion ID, prepends a TX descriptor, handles TKIP IV space and DMA alignment, writes the packet into the selected firmware TX ring chunk, triggers firmware, and reschedules/backs off on `-EBUSY`. TX completion reads the cyclic result ring, walks entries owned by host (`done_1` and `done_2`), restores the SKB by removing private headers/TKIP space, reports status to mac80211, clears result entries back to firmware, updates `next_tx_complete`, and wakes queues if low-watermark is reached.

State and persistence: Uses and mutates `wl->data_in_count`, `wl->tx_queue`, `wl->tx_queue_stopped`, `wl->tx_frames[]`, `wl->next_tx_complete`, retry stats, `wl->joined`, and `wl->default_key`. All state is volatile and reset on stop.

Dependencies and integration points: Depends on `io.c` memory/register writes, power-save wake/sleep, command/event join for injection, mac80211 TX APIs, ACX default key programming, and firmware data path addresses from `init.c`.

Risks: TX SKB ownership is subtle. Error paths after ID assignment must not leak or double-free; alignment replacement updates `wl->tx_frames[id]`. `wl1251_tx_flush()` skips status and freeing for SKBs without requested status in some paths, which deserves leak-focused testing. Static status parser buffer is not reentrant, though used under serialized context. Hardware queue fullness depends on modulo counters.

Test signals: Sustained TX under queue pressure, queue stop/wake transitions, TKIP and CCMP encrypted TX, injected monitor TX, TX retry/excessive retry stats, completion ring wraparound, and stop-time flush.
