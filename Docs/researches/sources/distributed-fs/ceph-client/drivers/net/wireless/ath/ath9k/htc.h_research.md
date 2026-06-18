# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc.h

Purpose: Central private header for the ath9k_htc USB driver, defining target command payloads, driver state, queue/rate/beacon/BTCOEX/LED/debug structures, feature constants, and cross-file function prototypes.

Important APIs and types: Target-facing wire structs include `tx_frame_hdr`, `tx_mgmt_hdr`, `tx_beacon_header`, target VIF/STA/aggr/rate/rate-mask structs, and target stats structs. Runtime state includes `ath9k_htc_vif`, `ath9k_htc_sta`, `ath9k_htc_rx`, `ath9k_htc_tx`, `ath9k_htc_tx_ctl`, `htc_beacon`, `ath_btcoex`, and the main `ath9k_htc_priv`. `HTC_SKB_CB()` maps mac80211 SKB driver data to HTC TX metadata. The header declares beacon, RX, TX, ANI, power-save, rfkill, LED, probe/disconnect, PM, and debug functions.

Control flow: Most ath9k_htc source files include this header to share the same private state layout. TX paths fill `ath9k_htc_tx_ctl` before `htc_send()`, RX/USB paths update debug counters through macros, beacon paths use `htc_beacon`, and mac80211 callbacks operate on `ath9k_htc_priv`.

State and persistence: State is runtime-only and spans HTC endpoint IDs, firmware version, VIF/STA slots, TX/RX queues, beacon slots, calibration data, power-save counters, work/tasklets, LED state, BTCOEX work, debugfs counters, and channel-switch state. Target command structures are transient host/firmware ABI payloads.

Dependencies and integration points: Includes Linux module/USB/firmware/SKB/netdevice/LED/mac80211 APIs plus ath9k common, HTC host, USB HIF, and WMI headers. It is the integration point between mac80211, the HTC firmware protocol, USB transport, hardware ops, and debugfs/ethtool.

Risks: This high-fanout header makes structure layout and lock ownership changes broad in impact. `HTC_SKB_CB()` relies on mac80211 driver-data size. VIF/STA limits are firmware constraints. Conditional debug/LED/BTCOEX stubs must preserve call-site behavior across configs.

Test signals: Build with combinations of HTC debugfs, LEDs, BTCOEX, and PM; run mac80211 VIF/STA lifecycle, TX/RX queueing, beaconing, power-save transitions, firmware capability update, debug stats, and suspend/resume.
