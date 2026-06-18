# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/data_rx.c

Purpose: Converts firmware RX indications into mac80211 RX status and delivers data frames to the stack.

Important APIs and functions: `wfx_rx_cb()` is the exported RX data callback. `wfx_rx_handle_ba()` intercepts firmware-offloaded ADDBA/DELBA action frames to start/stop mac80211 RX BA reordering for API 3.6+ firmware.

Control flow and integration: HIF RX dispatch strips the HIF and RX indication headers before calling `wfx_rx_cb()`. The callback maps firmware status to MIC/decrypt/drop handling, validates minimum frame size, fills band/frequency/rate/RSSI/decryption status, handles BA action frames locally, and otherwise calls `ieee80211_rx_irqsafe()`.

State and persistence: It updates no persistent driver state except mac80211 BA session state through offload callbacks. RX status is transient in the SKB control block.

Dependencies: Depends on WFx HIF RX indication format, `wfx_api_older_than()`, mac80211 RX APIs, and `struct wfx_vif`.

Risks and test signals: Risks include wrong rate-index conversion, missing RSSI handling, dropping action frames too broadly, malformed SKB length, and decrypt/MIC flag mismatches. Tests should cover successful RX, MIC failure reporting, nonzero firmware status drops, legacy and API 3.6 BA behavior, encrypted frames, no-RSSI frames, and invalid short frames.

Test signals: Source read size: 93 lines, 2530 bytes.
