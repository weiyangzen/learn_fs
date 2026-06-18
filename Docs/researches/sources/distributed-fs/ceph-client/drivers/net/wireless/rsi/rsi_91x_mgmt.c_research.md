# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_mgmt.c

## Purpose
This file builds and processes RSI firmware management frames. It owns the WLAN firmware initialization FSM after card-ready, programs boot/radio/baseband parameters, converts mac80211 state changes into command SKBs, handles firmware confirmations, and forwards received 802.11 management frames into mac80211.

## Important APIs, Types, and Functions
Static boot tables `boot_params_20`, `boot_params_40`, `boot_params_9116_20`, and `boot_params_9116_40` carry PLL/clock setup. Key APIs include `init_bgscan_params`, `rsi_hal_send_sta_notify_frame`, `rsi_send_aggregation_params_frame`, `rsi_set_vap_capabilities`, `rsi_hal_load_key`, `rsi_band_check`, `rsi_set_channel`, `rsi_send_radio_params_update`, `rsi_send_vap_dynamic_update`, `rsi_inform_bss_status`, `rsi_send_block_unblock_frame`, `rsi_send_rx_filter_frame`, `rsi_send_ps_request`, `rsi_set_antenna`, `rsi_send_bgscan_params`, `rsi_send_bgscan_probe_req`, `rsi_handle_card_ready`, and `rsi_mgmt_pkt_recv`.

## Control Flow
All outbound commands are allocated as SKBs, filled with RSI descriptors, queued to `MGMT_SOFT_Q` or `MGMT_BEACON_Q`, marked internal when appropriate, and signaled to the TX scheduler. Card-ready handling begins in `FSM_CARD_NOT_READY`, sends common device parameters, then on WLAN HAL ready loads 9113 or 9116 boot parameters. Confirm handling advances through boot params, EEPROM MAC/RF reads for 9113 or MAC extraction for 9116, reset-MAC, radio capabilities, optional 9116 feature enable, BB/RF programming, and finally `FSM_MAC_INIT_DONE`, at which point it attaches mac80211 or completes a hibernate reinit. Normal runtime commands cover peer add/delete, key install, aggregation, VAP add/delete/update, channel and band changes, radio power updates, block/unblock, RX filtering, power save, antenna selection, beacon transmission, WoWLAN, and background scan.

## State and Persistence Behavior
This file initializes and mutates `common->fsm_state`, band/channel/channel-width/endpoint, `mac_addr`, `num_supp_bands`, EEPROM offset/length, `usb_buffer_status_reg`, RF reset and BB/RF programming counters, default EDCA/contention weights, power-save request fields, rate tables, `rate_config`, `hw_data_qs_blocked`, `mgmt_q_block`, `eapol4_confirm`, background-scan state, WoWLAN flags, `wlan_init_completion`, and beacon counters. Hardware-visible persistence consists of commands written into firmware RAM/register state; software state is volatile.

## Dependencies and Integration Points
It integrates with `rsi_91x_main.c` TX queues, host-interface bus write paths, firmware-loading HAL code, mac80211 attach/RX delivery, power-save confirm handling, channel/regulatory data, Bluetooth/coex queues, and many descriptor structures from `rsi_mgmt.h`/`rsi_hal.h`/`rsi_boot_params.h`.

## Risks
The FSM is order-sensitive; dropped or duplicate confirms can leave the device stuck or attach mac80211 before firmware is ready. Many frame builders assume fixed descriptor sizes and little-endian fields. `rsi_hal_load_key` copies WEP data as `key_len * 2` and unconditionally copies MIC material from offsets 16/24 when `data` is present, requiring cipher/key-length discipline. Background-scan code trusts `scan_req->n_channels` against firmware array capacity. `rsi_load_9116_bootup_params` clears only `sizeof(struct rsi_boot_params)` while allocating the larger 9116 frame. BSS status and queue blocking must align with privacy/EAPOL timing or data can be released early or remain blocked.

## Test Signals
Card-ready-to-MAC-init traces, 9113 EEPROM reads, 9116 boot feature path, firmware confirm fault injection, attach completion after hibernate reinit, command SKB descriptor validation, STA/AP association and disassociation, WEP/TKIP/CCMP key loading, fixed-rate and autorate tables, HT40 band switching, PS confirmations, beacon event handling, WoWLAN wake reasons, and background-scan completion are important signals.
