# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/tx.c

Purpose: Implements MT7601U mac80211 TX submission, TXWI construction, queue mapping, DMA enqueue handoff, TX status cleanup, retry inference, and WMM/EDCA queue configuration.

Important APIs and functions: `mt7601u_tx()` is the mac80211 `.tx` path. `mt7601u_tx_status()` strips DMA/TXWI padding and reports ACKed skb status to mac80211. `mt7601u_tx_stat()` drains hardware TX status FIFO via MAC helpers and reports rate/retry status. `mt7601u_conf_tx()` programs EDCA/WMM parameters. Internal helpers include `skb2q()`, `q2hwq()`, `mt7601u_push_txwi()`, `mt7601u_skb_rooms()`, and packet-id encode/decode helpers.

Control flow: TX starts by preserving original packet length in `status_driver_data`, ensuring skb headroom and 4-byte 802.11 header alignment, selecting WCID from station/vif/monitor context, pushing and filling a `mt76_txwi`, then enqueueing the skb to DMA. TXWI setup chooses rate control from mac80211 or cached WCID rate, sets ACK/no-sequence flags, configures AMPDU BA window/density, writes WCID, and encodes requested/probe rate in packet id. TX status work repeatedly fetches valid statuses, decodes packet id into retry/probe estimates, calls mt76 status reporting, and requeues if more statuses are likely.

State and persistence: Uses `dev->lock` for WCID rate reads, `dev->mac_lock` around mac80211 TX status callback, and `dev->tx_lock` for TX status state flags. `info->status.status_driver_data[0]` temporarily stores original skb length while DMA/TXWI overhead is present. Hardware EDCA registers persist until reconfigured.

Dependencies and integration points: Depends on mac80211 TX info/control structures, local MAC descriptor helpers from `mac.h`, DMA enqueue from `dma.c`, register definitions from `regs.h`, and tracepoints. The queue mapping uses mac80211 AC ids but reverses hardware priority order.

Risks: TX retry reporting is explicitly approximate because hardware status is limited; rate/retry accounting can be wrong for AMPDU or FIFO overflow. Header padding must be inserted and removed symmetrically or mac80211 receives corrupted skb data. Queue id validation falls back to BE, which avoids crash but can mask caller bugs. EDCA parameter conversion uses `fls()` on contention window values, so expectations must match hardware exponent encoding.

Test signals: Packet TX through all ACs, AMPDU and non-AMPDU traffic, no-ACK frames, rate-control probes, TX status traces, monitor/group/station WCID cases, and WMM parameter changes validate this file.
