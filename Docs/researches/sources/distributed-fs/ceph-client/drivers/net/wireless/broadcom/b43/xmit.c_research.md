# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/xmit.c

## Purpose
Implements modern `b43` transmit and receive framing helpers. It translates mac80211 TX metadata into Broadcom firmware TX headers, decodes RX firmware headers into `ieee80211_rx_status`, parses PLCP rate information, maps encryption key indexes between raw and firmware formats, and routes TX completion to either DMA or PIO backends.

## Important APIs, Types, and Functions
Key exported functions are `b43_generate_txhdr`, `b43_generate_plcp_hdr`, `b43_rx`, `b43_handle_txstatus`, `b43_fill_txstatus_report`, `b43_tx_suspend`, and `b43_tx_resume`. Internal helpers include CCK/OFDM PLCP rate-code conversion, `b43_generate_tx_phy_ctl1`, `b43_calc_fallback_rate`, and `b43_rssi_postprocess`. It depends on `struct b43_txhdr`, `struct b43_rxhdr_fw4`, `struct b43_txstatus`, and key-index helpers declared in `xmit.h`.

## Control Flow
TX starts in `b43_generate_txhdr`: choose the main and fallback rates from mac80211, populate PLCP and PHY/MAC control words, copy receiver address and frame control, optionally attach hardware crypto metadata, generate RTS/CTS templates, encode firmware-format cookie fields for the active firmware header layout, and return an error only for invalid/missing keys or mapping assumptions. RX starts in `b43_rx`: decode status fields based on firmware header format, reject decrypt errors and undersized frames, remove PLCP/padding, calculate signal and rate index, fill band/frequency/timestamp metadata, and deliver the skb with `ieee80211_rx_ni`. TX status handling logs debugfs state, updates dot11 counters, dispatches to PIO or DMA completion, and triggers a TX power check.

## State and Persistence
The file does not persist data on disk. It mutates live driver and mac80211 state: `dev->wl->ieee_stats`, per-key state in `dev->key`, RX counters under debug builds, skb control blocks, and mac80211 TX retry status arrays. Firmware revision and header-format state controls which union fields are read or written.

## Dependencies and Integration Points
Integrates with mac80211 (`ieee80211_get_tx_rate`, RTS/CTS generation, RX/TX status APIs), b43 PHY helpers, b43 DMA/PIO backends, firmware header contracts, and Linux skb handling. Hardware crypto integration depends on mac80211 key configuration and b43 key-table semantics.

## Risks
The code contains several firmware-version assumptions: header-format unions, key-index API transition around firmware revision 351, and G-PHY channel encoding before/after firmware 508. Missing key configuration intentionally drops encrypted frames to avoid plaintext leaks. RX timestamp reconstruction assumes processing within roughly 65 ms of the received mactime. Rate table ordering must stay synchronized with mac80211 band tables.

## Test Signals
Useful signals are successful association and traffic over CCK/OFDM rates, encrypted TX with WEP/TKIP/AES keys, RTS/CTS protection traffic, monitor-mode radiotap timestamps, FCS/PLCP failure counters under injected bad frames, and correct TX retry accounting from rate-control traces. Suspend/resume should not transmit encrypted frames before keys are restored.
