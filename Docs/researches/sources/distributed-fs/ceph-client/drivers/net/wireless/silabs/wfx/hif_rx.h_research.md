# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_rx.h

Purpose: Declares the HIF RX dispatcher entry point.

Important APIs and types: Exports `void wfx_handle_rx(struct wfx_dev *wdev, struct sk_buff *skb)`.

Control flow and integration: `bh.c` calls this after validating a received HIF message and putting the firmware length into the SKB. The dispatcher owns SKB lifetime after the call.

State and persistence: No state is declared here; implementation updates command completions, stats, scan/PM state, and mac80211 callbacks.

Dependencies: Depends on `struct wfx_dev`, SKB ownership, and HIF message layout.

Risks and test signals: Test callers must not free SKBs after handing them to `wfx_handle_rx()` and should cover RX data indications separately because they retain SKB ownership until `wfx_rx_cb()`.

Test signals: Source read size: 17 lines, 407 bytes.
