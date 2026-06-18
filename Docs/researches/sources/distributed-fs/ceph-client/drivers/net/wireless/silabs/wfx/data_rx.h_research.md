# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_rx.h

Purpose: Declares the WFx RX data callback used by the HIF indication dispatcher.

Important APIs and types: Forward declarations for `struct wfx_vif`, `struct sk_buff`, and `struct wfx_hif_ind_rx`; exported function `wfx_rx_cb()`.

Control flow and integration: `hif_rx.c` calls `wfx_rx_cb()` when handling `HIF_IND_ID_RX`, after mapping the HIF interface to a vif and pulling protocol headers from the SKB.

State and persistence: No state is declared here.

Dependencies: Depends on HIF RX indication definitions from `hif_api_cmd.h` at implementation sites and mac80211 SKB semantics.

Risks and test signals: Build tests should confirm the callback signature stays aligned with `hif_rx.c` and `data_rx.c`; runtime tests should exercise RX indications for existing and missing vifs.

Test signals: Source read size: 17 lines, 380 bytes.
