# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/base.h

## Purpose
`base.h` declares the shared `rtlwifi` base-layer API implemented primarily by `base.c` and consumed by core, transport, and chip-specific modules. It also defines common rate limits, TX descriptor sizing, 802.11 header offsets, helper macros for frame/header/descriptor fields, and AP peer-vendor identifiers.

## Important APIs, Types, And Functions
`enum ap_peer` classifies recognized AP vendors (`PEER_RTL`, Broadcom, Ralink, Atheros, Cisco, Marvell, and others). Constants include TX descriptor/header sizing, maximum HT/VHT bitrate values for capability advertisement, frame offset constants, listen interval and retry limits. Header mutation macros fill PS-Poll and 802.11 address fields, while `SET_TX_DESC_SPE_RPT()` and `SET_TX_DESC_SW_DEFINE()` set TX report descriptor bits through little-endian bit replacement.

Declared lifecycle and configuration APIs include `rtl_init_core()`, `rtl_deinit_core()`, `rtl_init_rx_config()`, rfkill init/deinit, watchdog/deferred-work cleanup, and scan-operation backup. TX/rate/report APIs include `rtl_get_tcb_desc()`, `rtlwifi_rate_mapping()`, `rtl_tx_mgmt_proc()`, `rtl_is_special_data()`, `rtl_tx_ackqueue()`, `rtl_is_tx_report_skb()`, `rtl_set_tx_report()`, `rtl_tx_report_handler()`, `rtl_check_tx_report_acked()`, `rtl_wait_tx_report_acked()`, `rtl_get_hal_edca_param()`, `rtl_mrate_idx_to_arfr_id()`, and `rtl_tid_to_ac()`. Aggregation and frame APIs include TX/RX AMPDU start/stop/operational helpers, `rtl_rx_ampdu_apply()`, `rtl_action_proc()`, `rtl_find_ie()`, `rtl_send_smps_action()`, `rtl_collect_scan_list()`, `rtl_scan_list_expire()`, and `rtl_recognize_peer()`.

## Control Flow
There is no executable control flow in the header. It establishes the call graph used by `core.c`, transport files, and per-chip drivers: initialization enters through `rtl_init_core()`, transmit paths request TCB descriptors and special-packet decisions, RX paths update beacon/scan/peer state, mac80211 aggregation callbacks delegate to declared AMPDU helpers, and firmware-event paths invoke C2H queue/launcher functions.

## State And Persistence
The header does not store state directly. Its macros mutate caller-provided frame or descriptor buffers, and its function prototypes operate on persistent `struct ieee80211_hw`, `struct rtl_priv`, `struct rtl_tcb_desc`, station, vif, SKB, and driver-private state declared elsewhere. Constants in this file shape persistent advertised capability state, TX descriptor layout, retry behavior, and AP vendor classification values.

## Dependencies And Integration Points
`base.h` depends on mac80211 types, rtlwifi private types from surrounding headers, endian bit helpers, and Ethernet address helpers. It is a shared integration point between `base.c`, `core.c`, `pci.c`, `usb.c`, chip modules, power-save code, Bluetooth coexistence, rate control, security/CAM code, and regulatory/channel handling.

## Risks
Macros cast raw pointers to unaligned integer pointers or descriptor offsets, so callers must provide correctly sized and aligned buffers. Descriptor bit positions must remain synchronized with per-chip descriptor formats. Any prototype drift breaks exported-symbol users across modules. Constants used in capability advertisement must stay consistent with actual chip support to avoid mac80211 enabling unsupported modes.

## Test Signals
Signals include clean builds of all rtlwifi modules, no modpost unresolved symbols, TX descriptor report bits appearing in firmware TX reports, correct PS-Poll/header construction, successful aggregation callbacks, correct EDCA register values, and runtime coverage of peer recognition and special-packet paths.
