# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_tx.h

## Purpose

`hal_tx.h` declares the Wi-Fi 7 TX HAL data model and descriptor field constants. It defines the software input structure used to build TCL data commands, the parsed TX status structure, TX PHY/FES monitor TLV layouts, queue extension fields, PPDU setup/status fields, bank configuration masks, and exported TX/REO helper prototypes.

## Important APIs, Types, And Constants

`struct hal_tx_info` is the key input for TX descriptor setup, carrying metadata flags, ring/RBM IDs, descriptor ID, TCL descriptor type, encap/encrypt type, DMA address, length, packet offset, flag words, address-search controls, TID, LMAC/VDEV IDs, DSCP table index, mesh enablement, and bank ID. `struct hal_tx_status` represents parsed WBM TX completion data, including release source, status reason, RSSI, PPDU ID, retry count, TID, peer ID, packet type, GI, bandwidth, MCS, tones, and OFDMA state.

The file also defines TLV structures such as `hal_tx_phy_desc`, `hal_tx_fes_status_prot`, `hal_tx_fes_status_user_ppdu`, `hal_tx_fes_status_start`, `hal_tx_queue_exten`, `hal_tx_fes_setup`, `hal_tx_pcu_ppdu_setup_init`, and `hal_tx_fes_status_end`. Exported functions include `ath12k_wifi7_hal_tx_set_dscp_tid_map()`, `ath12k_wifi7_hal_tx_cmd_desc_setup()`, `ath12k_wifi7_hal_reo_cmd_send()`, and `ath12k_wifi7_hal_tx_configure_bank_register()`.

## Control Flow And Integration

The header's structures are consumed by `hal_tx.c`, common Wi-Fi 7 `hal.c`, DP TX, WBM completion parsing, and monitor/status handling. TX control flow starts with DP TX populating `hal_tx_info`, calls the HAL descriptor setup helper, submits the command into a TCL SRNG, and later decodes WBM release/TX status fields using the status constants. Bank configuration masks are used when per-vdev/per-bank TX behavior is programmed.

## State And Persistence Behavior

Most definitions describe transient ring entries and TX completion state. Bank configuration bits and DSCP/TID table IDs represent hardware programming that persists across packets. `hal_tx_status` is a parsed software snapshot and should not outlive the completion event without being copied into statistics.

## Dependencies

The header includes `../mac.h` and `hal_desc.h`, and it relies on ath12k enums such as `enum hal_tcl_desc_type`, `enum hal_tcl_encap_type`, `enum hal_encrypt_type`, `enum hal_wbm_rel_src_module`, `enum hal_wbm_tqm_rel_reason`, `enum hal_tx_rate_stats_pkt_type`, `enum hal_tx_rate_stats_sgi`, and `enum ath12k_supported_bw`.

## Risks And Edge Cases

Comments note TODOs around reusing actual descriptor macros and possibly folding data into `ath12k_tx_desc_info`, signaling that some fields may duplicate broader driver state. ABI risk is high because mask names and comments must match firmware descriptors. The bank config field `HAL_TX_BANK_CONFIG_DSCP_TIP_MAP_ID` appears to spell `TIP` rather than `TID`; callers must use the exact macro name, but the spelling is a maintainability hazard.

## Test Signals

Compile tests should cover all TX users and monitor/TX status parsing. Runtime validation should include encrypted and unencrypted TX, mesh mode when enabled, DSCP/TID mapping, all supported bandwidth/rate completion stats, multicast and unicast completion, bank programming, and REO command submission through the declared helper.
