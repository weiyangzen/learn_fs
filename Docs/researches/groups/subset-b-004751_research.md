# subset-b-004751 research

Grouped research for the Wi-Fi 7 ath12k HAL, hardware, MHI, PCI, and WMI files under `sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7`. Each section preserves the original source path for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx.h

## Purpose

`hal_rx.h` is the Wi-Fi 7 receive-side HAL interface header. It defines RX monitor TLV structures, PPDU/user statistics layouts, PHY signal bitfields for HT/VHT/HE/EHT/USIG parsing, REO status APIs, RX buffer address helpers, and queue-descriptor setup entry points used by the Wi-Fi 7 DP RX path. The file is mostly hardware ABI: packed structures and bit masks must match firmware and descriptor ring formats.

## Important APIs, Types, And Constants

Key exported types include `struct hal_rx_wbm_rel_info`, monitor TLV status headers, `struct hal_rx_ppdu_start`, `struct hal_rx_ppdu_end_user_stats`, HE/EHT/USIG signal structures, `struct hal_receive_user_info`, and `struct hal_rx_msdu_list`. The REO/RX helper prototypes include `ath12k_wifi7_hal_reo_status_queue_stats`, `ath12k_wifi7_hal_reo_flush_queue_status`, `ath12k_wifi7_hal_reo_flush_cache_status`, `ath12k_wifi7_hal_reo_unblk_cache_status`, `ath12k_wifi7_hal_reo_update_rx_reo_queue_status`, `ath12k_wifi7_hal_rx_msdu_link_info_get`, `ath12k_wifi7_hal_wbm_desc_parse_err`, `ath12k_wifi7_hal_desc_reo_parse_err`, `ath12k_wifi7_hal_rx_msdu_list_get`, `ath12k_wifi7_hal_reo_hw_setup`, and `ath12k_wifi7_hal_reo_qdesc_setup`.

The header also defines radiotap-related HE fields, RX MPDU error bits, EHT RU encodings, MRU composition macros for 80/160/320 MHz layouts, and status values such as `HAL_TLV_STATUS_PPDU_DONE` and `HAL_RX_MON_STATUS_*`.

## Control Flow And Integration

This header does not implement control flow directly, but it describes the contracts consumed by `wifi7/hal_rx.c`, `wifi7/dp_rx.c`, and `wifi7/dp_mon.c`. Monitor parsing code reads the PPDU, HE, EHT, USIG, and per-user structures to populate radiotap and RX status. DP RX uses the WBM/REO helper prototypes to recover buffer addresses, parse error release descriptors, return link descriptors, and build REO queue descriptors for per-peer/TID reorder state. HAL ops in chip files, such as WCN7850, point back to functions declared here.

## State And Persistence Behavior

The file defines transient on-ring and on-buffer state rather than persistent software state. REO queue descriptors and RX link descriptors represent durable hardware-owned DMA state while packets are in flight; fields such as PN, peer metadata, TID, PPDU ID, RSSI, RU allocation, and descriptor cookies are carried across ring transitions. Software persistence is indirect: queue descriptor setup and REO status parsing update DP peer/TID state elsewhere.

## Dependencies

It includes `hal_desc.h` and depends on common ath12k HAL types such as `struct ath12k_base`, `struct ath12k_dp`, `struct ath12k`, `struct hal_srng`, `struct hal_reo_status`, `struct hal_wbm_release_ring`, `struct ath12k_buffer_addr`, `enum hal_reo_cmd_type`, and Linux bitfield helpers (`GENMASK`, `BIT`, `le32_get_bits`). It is tightly coupled to `hal_rx_desc.h` for descriptor field masks and to monitor parsing in `dp_mon.c`.

## Risks And Edge Cases

Descriptor ABI drift is the primary risk: any field mask, packing, or TLV length mismatch can corrupt RX parsing, buffer recycling, monitor status, or REO commands. EHT and 320 MHz RU macros are dense and easy to mis-index. One visible risk is `HAL_RX_EHT_SIG_OFDMA_EB2_MCS` using `GNEMASK_ULL` instead of `GENMASK_ULL`, which would break compilation if that macro is compiled or referenced. Another risk is duplicate naming (`HE_TXBF_SHIFT`) in separate radiotap contexts; consumers must use the intended field context.

## Test Signals

Build coverage should compile all monitor and DP RX users with `W=1` to catch bad masks and missing symbols. Runtime signals include successful RX data traffic, monitor-mode radiotap correctness for HE/EHT frames, REO status processing under BA session setup/teardown, RX error path handling for FCS/decrypt/TKIP/fragment errors, and no DMA leak warnings when WBM/REO descriptors are recycled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx_desc.h

## Purpose

`hal_rx_desc.h` defines concrete Wi-Fi 7 RX descriptor layouts for QCN9274-compatible compact descriptors, WCN7850 full descriptors, and QCC2072 descriptors. It maps hardware `RX_MPDU_START` and `RX_MSDU_END` TLV fields into packed C structures and bit masks used by RX data, RX error, monitor, crypto, and checksum handling.

## Important APIs, Types, And Constants

The main exported data model includes `enum rx_desc_decrypt_status_code`, `struct rx_mpdu_start_qcn9274`, `struct rx_mpdu_start_qcn9274_compact`, `struct rx_msdu_end_qcn9274`, `struct rx_msdu_end_qcn9274_compact`, `struct hal_rx_desc_qcn9274_compact`, `struct hal_rx_desc_wcn7850`, `struct hal_rx_desc_qcc2072`, and the wrapper `struct hal_rx_desc`.

Important masks cover MPDU routing, PN/encryption metadata, AST lookup, frame-control validity, QoS/TID, sequence number, VDEV/service-code data, source/destination address lookup, checksum status, flow/FISA metadata, VLAN stripping, decap format, packet type, MCS/SGI/BW/NSS, RSSI, error bitmap bits, decrypt status, and `MSDU_DONE`. The `QCN9274_*_SELECT_*` and `*_WMASK` constants define compact descriptor subscription masks and explicitly tie the compact C struct layout to selected TLV fields.

## Control Flow And Integration

This header is data-only, but it is on the hot path for descriptor interpretation. WCN7850 HAL code dereferences `desc->u.wcn7850.msdu_end` and `desc->u.wcn7850.mpdu_start` to extract payload location, crypto header, 802.11 header, rate information, checksum status, peer ID, and RX errors. DP RX uses the same wrapper to process normal RX, WBM error releases, REO error releases, fragment reassembly, and null-queue cases. The flexible `msdu_payload[]` member anchors where packet bytes begin after metadata.

## State And Persistence Behavior

The structures describe DMA-backed packet state provided by firmware/hardware. Fields such as PN, peer metadata, AST index, sequence control, timestamps, checksum metadata, flow hashes, and RX errors persist only for the lifetime of a received descriptor, but their values drive longer-lived software state such as reorder queues, PN validation, peer statistics, and skb checksum annotations. Compact descriptors persist fewer fields by construction, so mask/layout consistency is essential.

## Dependencies

The file depends on Linux packed structure semantics, endian types (`__le16`, `__le32`, `__le64`), `ETH_ALEN`, and bitfield macros. Consumers include `hal_wcn7850.c`, `hal_qcn9274.c`, `dp_rx.c`, and any monitor or RX helper that needs descriptor offsets or payload starts. It shares semantic constants with `hal_rx.h`, especially MPDU error and decrypt status handling.

## Risks And Edge Cases

The largest risk is layout mismatch. Changing `QCN9274_MPDU_START_WMASK` or `QCN9274_MSDU_END_WMASK` without updating the compact structures would shift every subsequent field. WCN7850 and QCC2072 differ in TLV tag width (`__le64` versus `__le32`), so using the wrong union arm would produce bad offsets and payload corruption. Error masks include two MPDU length/error concepts and many first-MSDU-only fields; callers must check validity bits before trusting frame-control, sequence, address, or encryption metadata.

## Test Signals

Compile-time signals include `sizeof`/`offsetof` expectations in HAL users and no packed-structure warnings. Runtime validation should cover normal native-WiFi RX, encrypted RX for all supported ciphers, checksum offload, multicast/broadcast detection, monitor frames, WBM/REO error releases, fragmented traffic, and device-specific WCN7850/QCC2072 payload offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_tx.c

## Purpose

`hal_tx.c` implements Wi-Fi 7 transmit HAL helpers for TCL data command descriptor setup and DSCP-to-TID table programming. It is the bridge between software TX metadata (`struct hal_tx_info`) and the little-endian TCL command words consumed by hardware.

## Important APIs And Functions

`ath12k_wifi7_hal_tx_cmd_desc_setup()` fills a `struct hal_tcl_data_cmd` with DMA buffer address, return buffer manager, software cookie, descriptor type, bank ID, command metadata, packet length, packet offset, TID, PMAC/LMAC ID, VDEV ID, and AST search information. `ath12k_wifi7_hal_tx_set_dscp_tid_map()` programs a hardware DSCP/TID table for a selected map ID. The internal `dscp2tid()` helper maps DSCP classes to TIDs with `dscp >> 3`.

## Control Flow

TX descriptor setup is straightforward field packing: address low and high words are encoded first, then descriptor identity and command metadata are encoded into `info0` through `info5`. The DSCP/TID setup path reads the TCL common control register, sets `HAL_TCL1_RING_CMN_CTRL_DSCP_TID_MAP_PROG_EN`, builds the 64-entry DSCP table as packed 3-bit TID values, writes it four bytes at a time to `HAL_TCL1_RING_DSCP_TID_MAP` plus the selected table offset, then clears the programming-enable bit.

## State And Persistence Behavior

`ath12k_wifi7_hal_tx_cmd_desc_setup()` only initializes transient ring descriptors. `ath12k_wifi7_hal_tx_set_dscp_tid_map()` persists state in TCL hardware registers until reset or reprogramming, affecting later hardware classification for the selected DSCP/TID map ID. There is no file-local persistent software state.

## Dependencies And Integration

The file includes Wi-Fi 7 HAL TX definitions, generic HAL/HIF headers, and uses `ath12k_hif_read32()`/`ath12k_hif_write32()` for MMIO. It is referenced through `hal_ops.tx_set_dscp_tid_map` in chip HAL ops and by DP TX code that prepares TCL descriptors. The command format depends on `hal_desc.h` bit masks and the `hal_tcl_data_cmd` ABI.

## Risks And Edge Cases

The DSCP packing loop stores 8 three-bit mappings into three bytes by copying from a host-endian `u32` into a byte array, then writing as `u32`; this is conventional for the target layout but endian-sensitive and should be treated as hardware ABI. The table `id` is not range-checked in this helper, so callers must pass a valid hardware table index. Descriptor setup trusts `hal_tx_info` fields; invalid DMA addresses, lengths, offsets, bank IDs, or RBM IDs will be sent directly to hardware.

## Test Signals

Build coverage should catch field-mask drift. Runtime signals include successful TCP/UDP TX on all TCL rings, correct WMM/TID behavior for DSCP-marked traffic, no stuck TCL rings, no WBM release cookie mismatches, and correct packet completion routing across all configured TX banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_tx.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_wcn7850.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_wcn7850.c

## Purpose

`hal_wcn7850.c` is the WCN7850-specific HAL binding for Wi-Fi 7 ath12k. It provides SRNG configuration templates, WCN7850 register offsets, RX descriptor accessor functions, TCL-to-WBM RBM mapping, HAL parameter defaults, and the `hal_wcn7850_ops` table that plugs chip-specific operations into the common HAL layer.

## Important APIs, Types, And Data

The static `hw_srng_config_template` defines ring IDs, ring counts, entry sizes, directions, MAC types, and maximum sizes for REO, TCL, CE, WBM, RXDMA, monitor, PPE, and TX monitor rings. `wcn7850_regs` maps UMAC/TCL/WBM/REO/CE/PCIe/PPE register offsets. RX descriptor helpers extract first/last MSDU, L3 padding, encryption type, decap type, mesh control, sequence validity, frame-control validity, sequence number, MSDU length, SGI/MCS/BW/frequency, packet type, NSS bitmap, TID, peer ID, checksum failures, decrypt status, MPDU errors, 802.11 header, crypto header, payload pointer, and descriptor offsets.

Exported data includes `ath12k_hal_tcl_to_wbm_rbm_map_wcn7850`, `ath12k_hw_hal_params_wcn7850`, and `hal_wcn7850_ops`. `ath12k_hal_srng_create_config_wcn7850()` allocates and customizes the per-HAL SRNG config.

## Control Flow

Initialization flows through `ath12k_wifi7_hal_init()` in `hal.c`, which selects WCN7850 HAL ops and registers for the WCN7850 hardware revision. `ath12k_hal_srng_create_config_wcn7850()` duplicates the template, then patches ring register starts/sizes and disables unused rings for this device. RX processing calls `hal_wcn7850_ops.extract_rx_desc_data`, which gathers fields from the first and last descriptors into `struct hal_rx_desc_data`. Crypto header reconstruction switches on `enum hal_encrypt_type` to build CCMP/GCMP/TKIP-style headers from PN and key ID fields.

## State And Persistence Behavior

The file owns no mutable global state except allocated `hal->srng_config` created per device. Register offset tables and ops tables are immutable. SRNG configuration persists in `struct ath12k_hal` after initialization and drives later ring setup. RX descriptor helpers read transient DMA descriptors, while `ath12k_hal_rx_desc_set_msdu_len_wcn7850()` mutates descriptor metadata during packet processing.

## Dependencies And Integration

It depends on `hal_desc.h`, `hal_rx.h`, `hal_rx_desc.h` through included HAL headers, `hw.h`, and shared Wi-Fi 7 HAL functions from `hal.c`/`hal_rx.c`/`hal_tx.c`. It integrates with DP RX via descriptor accessors, with ring setup via `create_srng_config`, with DP TX via DSCP/TID and bank operations, and with REO setup/status via common Wi-Fi 7 helpers.

## Risks And Edge Cases

The code assumes WCN7850 descriptor layout, especially `desc->u.wcn7850`; using it for QCC2072 or compact QCN9274 descriptors would corrupt parsing. `ath12k_hal_rx_desc_get_msdu_src_link_wcn7850()` currently returns zero, so multi-link source-link extraction is not implemented for this path. `ath12k_hal_srng_create_config_wcn7850()` contains a duplicate `HAL_PPE2TCL` disable block, harmless but noisy. Crypto header generation returns early for WEP/WAPI/open and must remain aligned with mac80211 expectations.

## Test Signals

Probe should allocate SRNG config without leaks, initialize all active rings, and leave unused rings disabled. RX tests should validate descriptor offsets, payload pointer, native Wi-Fi decap, encrypted CCMP/GCMP/TKIP frames, checksum offload, multicast detection, and monitor status. Suspend/resume and ASPM-capable WCN7850 paths should verify MHI wake/release and no ring pointer corruption after power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_wcn7850.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_wcn7850.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_wcn7850.h

## Purpose

`hal_wcn7850.h` declares the public WCN7850 HAL symbols used by the Wi-Fi 7 ath12k hardware mapping and common HAL code. It is the contract between `hal_wcn7850.c`, hardware revision selection in `hal.c`, and users that need WCN7850 RX descriptor helpers.

## Important APIs And Data

The header exports immutable chip binding data: `hal_wcn7850_ops`, `wcn7850_regs`, `ath12k_hal_tcl_to_wbm_rbm_map_wcn7850`, and `ath12k_hw_hal_params_wcn7850`. It also declares RX descriptor accessor and mutator functions, including L3 padding, end-TLV copy, MPDU start tag, PPDU ID, MSDU length set, payload pointer, MPDU/MSDU offset helpers, RX descriptor size, source link ID, crypto header extraction, 802.11 header extraction, aggregate RX descriptor data extraction, and SRNG config creation.

## Control Flow And Integration

The header is included by WCN7850-specific and common Wi-Fi 7 HAL files. `hal.c` uses the exported ops/register/parameter symbols when `ab->hw_rev` matches WCN7850 or related client-chip variants. DP RX reaches these functions indirectly through `struct hal_ops`, while some code can call declared helpers directly for descriptor sizing or offsets.

## State And Persistence Behavior

The header owns no state. It exposes immutable tables and functions that operate on per-device state (`struct ath12k_hal`) or transient RX descriptors (`struct hal_rx_desc`). `ath12k_hal_srng_create_config_wcn7850()` is the only declared function that allocates persistent per-device HAL configuration.

## Dependencies

It includes `../hal.h`, `hal_rx.h`, and local `hal.h`, requiring common ath12k HAL structures, `struct hal_rx_desc`, `struct hal_rx_desc_data`, `struct ieee80211_hdr`, and `enum hal_encrypt_type`. The exported tables depend on declarations for `struct hal_ops`, `struct ath12k_hw_regs`, `struct ath12k_hal_tcl_to_wbm_rbm_map`, and `struct ath12k_hw_hal_params`.

## Risks And Edge Cases

Because this is a cross-file ABI header, prototype drift from `hal_wcn7850.c` will break builds or function pointer assignments. The header exports WCN7850-specific descriptor helpers; callers must not apply them to non-WCN7850 descriptor union arms unless the selected `hal_ops` guarantees the layout. Include layering is somewhat dense (`../hal.h`, `hal_rx.h`, and local `hal.h`), so circular include changes could surface here.

## Test Signals

Build coverage is the main signal: all symbols should resolve when WCN7850 support is compiled, and no duplicate or missing prototypes should appear. Runtime validation comes indirectly through WCN7850 probe, SRNG setup, RX data path, and HAL ops dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_wcn7850.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hw.c

## Purpose

`hw.c` is the Wi-Fi 7 hardware-variant registry and mac80211 ops binding for ath12k. It maps hardware revisions to firmware directories, CE/MHI/WMI/HAL capabilities, ring masks, feature flags, MLO limits, interface modes, and hardware operation callbacks. It also supplies the Wi-Fi 7 `ieee80211_ops` table and TX entry point.

## Important APIs, Types, And Data

Important local callbacks translate MAC/PDEV/SRNG IDs for QCN9274 and WCN7850-style devices, choose TX rings (`smp_processor_id()` for QCN9274 and skb queue mapping for WCN7850), identify TX completion rings, and decide whether management frames are link-agnostic for MLO. The WCN7850 link-agnostic decision checks peer presence and MLO state under DP locks and excludes selected station/AP management frames such as probe/auth/deauth/association and ADDBA response.

Static ring masks describe IRQ/service masks for TX, RX, RX monitor, RX error, WBM release, REO status, host-to-RXDMA, and TX monitor rings. `ath12k_wifi7_hw_params[]` contains entries for QCN9274 hw1.0/hw2.0, WCN7850 hw2.0, QCC2072 hw1.0, IPQ5332 hw1.0, and IPQ5424 hw1.0. `ath12k_wifi7_mac_op_tx()` is the custom TX path installed in `ath12k_ops_wifi7`. `ath12k_wifi7_hw_init()` selects the matching params, assigns `ab->ath12k_ops`, initializes HAL, and logs the hardware name.

## Control Flow

Probe code in PCI/AHB sets `ab->hw_rev`, then calls `ath12k_wifi7_hw_init()`. Hardware init scans `ath12k_wifi7_hw_params[]`, fails with `-EINVAL` on an unsupported revision, stores the selected params, installs Wi-Fi 7 mac80211 ops, and calls `ath12k_wifi7_hal_init()`. TX flow enters `ath12k_wifi7_mac_op_tx()`, rejects monitor vdev TX, chooses an MLO link, handles management frames through `ath12k_mac_mgmt_tx()`, applies P2P NoA when needed, and sends normal unicast or special cases to `ath12k_wifi7_dp_tx()`. MLO multicast is copied per active link, link addresses are updated, multicast keys are looked up, protected bit is set when needed, and each copy is queued with a shared multicast GSN.

## State And Persistence Behavior

Hardware params are immutable global tables. Runtime state is stored in `ab->hw_params`, `ab->ath12k_ops`, per-vif link maps, skb control blocks, per-vif multicast sequence (`mcbc_gsn`), peer/key state, and DP locks. TX does not persist packet data beyond queued skbs, but multicast fanout creates per-link skb copies and may update frame protection bits.

## Dependencies And Integration

The file integrates mac80211/cfg80211 ops, ath12k core/CE/HAL/MHI/WMI/DP/peer/debugfs/testmode/wow layers, Wi-Fi 7 DP RX/TX helpers, and hardware-specific CE maps. Hardware params reference MHI configs from `mhi.c`, WMI init functions from `wmi.c`, ring selection functions from DP RX config files, and HAL init from local `hal.c`.

## Risks And Edge Cases

`ath12k_wifi7_mac_op_tx()` is high-risk because it runs in the TX hot path under RCU constraints. MLO link selection failure drops skbs; multicast fanout can partially fail if `skb_copy()` or per-link peer lookup fails. Lock ordering around `dp_lock` and `dp_hw.peer_lock` must remain stable. The WCN7850 link-agnostic check depends on peer lookup correctness and excludes some management frames to avoid sending them over the wrong link. Hardware parameter mismatches can manifest as wrong firmware path, CE count, MHI config, ring masks, or feature flags.

## Test Signals

Probe each supported revision and verify selected `hw_params->name`, firmware directory, CE/MHI/WMI config, and HAL register mapping. Runtime tests should cover station/AP/P2P modes, MLO unicast and multicast, encrypted multicast, probe/auth/assoc/ADDBA management frames, suspend/resume on WCN7850/QCC2072, monitor support on capable devices, and unsupported `hw_rev` failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hw.h

## Purpose

`hw.h` is the minimal public header for Wi-Fi 7 ath12k hardware initialization. It forward-declares `struct ath12k_base` and exposes `ath12k_wifi7_hw_init()`.

## Important API

`int ath12k_wifi7_hw_init(struct ath12k_base *ab);` is called after the bus-specific probe path has identified the hardware revision. It selects the matching Wi-Fi 7 hardware parameter table, installs Wi-Fi 7 mac80211 ops, initializes HAL, and returns an error for unsupported revisions.

## Control Flow And Integration

PCI probe in `wifi7/pci.c` and AHB probe in the wider Wi-Fi 7 folder include this header and call the init function after setting fields such as `ab->hw_rev`, memory mode, bus-specific ops, and window-register state. The implementation lives in `hw.c`.

## State And Persistence Behavior

The header owns no state. The declared function mutates the passed `ath12k_base` by assigning hardware params and ops and by invoking HAL initialization.

## Dependencies

The only compile-time dependency is the forward declaration of `struct ath12k_base`, keeping this header lightweight for bus drivers.

## Risks And Edge Cases

Because this header hides the full `ath12k_base` definition, callers must include the right core headers in their own C files before dereferencing `ab`. The main behavioral risk is caller ordering: `ab->hw_rev` must be valid before calling `ath12k_wifi7_hw_init()`.

## Test Signals

Build coverage should confirm all bus drivers see the prototype. Probe tests should verify PCI/AHB paths call the function after hardware revision selection and handle nonzero returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/mhi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/mhi.c

## Purpose

`mhi.c` defines MHI controller configurations for Wi-Fi 7 PCIe ath12k devices. It provides channel and event-ring descriptions for QCN9274 and WCN7850-style devices so firmware/QMI IPC can run over MHI.

## Important APIs And Data

The file exports `ath12k_wifi7_mhi_config_qcn9274` and `ath12k_wifi7_mhi_config_wcn7850`. Each config uses two `IPCR` channels: channel 20 for host-to-device (`DMA_TO_DEVICE`) and channel 21 for device-to-host (`DMA_FROM_DEVICE`). Both use event ring 1, execution environment mask `0x4`, disabled doorbell burst mode, and no low-power/offload notifications. QCN9274 uses 32 channel elements, `max_channels = 30`, and `timeout_ms = 10000`. WCN7850 uses 64 channel elements, `max_channels = 128`, `timeout_ms = 2000`, and `buf_len = 8192`.

Event configs define a control event ring with 32 elements on IRQ 1 and a data event ring with 256 elements on IRQ 2, one millisecond moderation for the second event ring, disabled doorbell burst mode, and priority 1 on the data ring.

## Control Flow And Integration

`hw.c` references these exported configs in `ath12k_wifi7_hw_params[]`. The PCI/core MHI setup layer consumes the selected `mhi_controller_config` during device bring-up, creates MHI channels/events, and later uses MHI for firmware communication and bus power management. WCN7850 PCI bus wake/release helpers in `pci.c` call into MHI device get/put paths around bus access.

## State And Persistence Behavior

The channel and event tables are static configuration, not runtime state. Once selected, the MHI core creates runtime controller/channel/event state from these descriptors. The descriptors persist for the lifetime of the module.

## Dependencies

The file includes generic ath12k MHI definitions and its local header. It depends on Linux MHI types (`struct mhi_channel_config`, `struct mhi_event_config`, `struct mhi_controller_config`), DMA direction constants, and MHI doorbell/event enums.

## Risks And Edge Cases

Timeout and buffer-length differences between QCN9274 and WCN7850 are intentional; assigning the wrong config in `hw.c` can break firmware boot or IPC. Channel numbers are hard-coded to IPCR 20/21; firmware ABI changes would require synchronized updates. WCN7850's shorter timeout may expose slow firmware boot or resume issues more readily than QCN9274.

## Test Signals

Probe should create MHI channels/events without errors, firmware boot should complete, QMI/IPCR traffic should work in both directions, suspend/resume should not strand MHI references, and timeout logs should be absent during normal boot and recovery. Device-specific tests should confirm QCN9274 and WCN7850 select their intended config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/mhi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/mhi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/mhi.h

## Purpose

`mhi.h` declares the Wi-Fi 7 ath12k MHI controller configuration objects for use by hardware parameter tables.

## Important API/Data

It exports `ath12k_wifi7_mhi_config_qcn9274` and `ath12k_wifi7_mhi_config_wcn7850`, both typed as `const struct mhi_controller_config`. The definitions live in `mhi.c`.

## Control Flow And Integration

`hw.c` includes this header and assigns the exported configs to `ath12k_hw_params.mhi_config` for PCIe-capable Wi-Fi 7 chips. The selected config is later consumed by shared ath12k PCI/MHI setup code during device initialization.

## State And Persistence Behavior

The header owns no state; it only exposes immutable configuration descriptors.

## Dependencies

It depends on `struct mhi_controller_config` being visible to includers through their existing MHI/core includes. The header itself is intentionally small and guarded by `_ATH12K_WIFI7_MHI_H`.

## Risks And Edge Cases

Missing or stale extern declarations would break hardware parameter builds. If a hardware table references `NULL` for non-PCI/remoteproc devices, consumers must tolerate that separately; this header only covers the exported PCIe configs.

## Test Signals

Build tests should ensure both externs resolve and no hardware table points to an undeclared config. Runtime probe verifies the configs indirectly through successful MHI initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/mhi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/pci.c

## Purpose

`pci.c` registers the Wi-Fi 7 ath12k PCI family driver and performs device-specific PCI probe setup for QCN9274, WCN7850, and QCC2072. It selects MSI layout, window-register behavior, PCI ops, board search mode, target memory mode, hardware revision, and then hands control to common Wi-Fi 7 hardware initialization.

## Important APIs, Types, And Data

The PCI ID table matches Qualcomm device IDs `0x1109` (QCN9274), `0x1107` (WCN7850), and `0x1112` (QCC2072). `ath12k_wifi7_msi_config` allocates 16 vectors across MHI (3), CE (5), and DP (8). QCN9274 PCI ops have no wake/release callbacks, while WCN7850/QCC2072 use `ath12k_wifi7_pci_bus_wake_up()` and `ath12k_wifi7_pci_bus_release()` to call `mhi_device_get_sync()` and `mhi_device_put()`.

`ath12k_wifi7_pci_read_hw_version()` reads `TCSR_SOC_HW_VERSION` and extracts major/minor fields. `ath12k_wifi7_pci_probe()` is the main bus-specific setup function. `ath12k_wifi7_pci_init()` and `ath12k_wifi7_pci_exit()` register and unregister the driver for `ATH12K_DEVICE_FAMILY_WIFI7`.

## Control Flow

Registration passes `ath12k_wifi7_pci_driver` to shared PCI registration with arch init/deinit hooks. Probe retrieves `ath12k_base` from `pci_get_drvdata()`, validates PCI private state, switches on device ID, sets bus/hardware fields, optionally reads SoC hardware version through the configured window register, selects `ab->hw_rev`, and calls `ath12k_wifi7_hw_init()`. Unknown device IDs or unsupported hardware major versions return `-EOPNOTSUPP`; missing driver data returns `-EINVAL`.

## State And Persistence Behavior

Probe mutates `ab`, `ab_pci`, and board-identification state. Persistent settings include `ab_pci->msi_config`, `ab_pci->pci_ops`, `ab_pci->window_reg_addr`, `ab->static_window_map`, `ab->target_mem_mode`, `ab->id.bdf_search`, and `ab->hw_rev`. These settings remain active for the lifetime of the PCI device and influence later HAL/MHI/firmware setup.

## Dependencies And Integration

The file depends on Linux PCI matching, shared ath12k PCI/HIF/MHI/core/HAL layers, local Wi-Fi 7 hardware init, DP/core HAL headers, and common PCI register base definitions. It integrates with `hw.c` for revision-specific params and with `mhi.c` through bus wake/release and selected hardware MHI configs.

## Risks And Edge Cases

Hardware version reading depends on setting `window_reg_addr` before reading `TCSR_SOC_HW_VERSION`; wrong ordering would read the wrong window. QCC2072 uses a different window register address and does not read a version, assuming one current revision. WCN7850/QCC2072 call MHI get/put on bus wake/release, so missing `mhi_ctrl` or `mhi_dev` would be fatal if those paths run too early. Unsupported major versions intentionally fail probe.

## Test Signals

Tests should verify PCI ID matching, MSI vector allocation, correct hw_rev selection for QCN9274 major 1/2 and WCN7850 major 2, QCC2072 fixed revision setup, firmware board search behavior, MHI wake/release during runtime PM, and clean unregister through `ath12k_wifi7_pci_exit()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/pci.h

## Purpose

`pci.h` is the public header for Wi-Fi 7 ath12k PCI driver registration.

## Important APIs

It declares `int ath12k_wifi7_pci_init(void);` and `void ath12k_wifi7_pci_exit(void);`. These functions register and unregister the Wi-Fi 7 PCI driver with the shared ath12k PCI layer.

## Control Flow And Integration

The Wi-Fi 7 module core includes this header and calls `ath12k_wifi7_pci_init()` during module initialization and `ath12k_wifi7_pci_exit()` during module exit. The implementations live in `pci.c` and wrap `ath12k_pci_register_driver()` / `ath12k_pci_unregister_driver()` for `ATH12K_DEVICE_FAMILY_WIFI7`.

## State And Persistence Behavior

The header owns no state. The declared init/exit functions mutate global PCI driver registration state in the kernel.

## Dependencies

No external structures are needed by the prototypes. Include guards prevent duplicate declarations.

## Risks And Edge Cases

The init function can fail if shared PCI registration fails; callers must preserve module init error handling and call exit only when registration succeeded. Header/API drift would break the Wi-Fi 7 core module.

## Test Signals

Build coverage should ensure declarations match `pci.c`. Module load/unload should register and unregister the PCI family exactly once, and PCI devices should bind only after successful init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/wmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/wmi.c

## Purpose

`wmi.c` initializes firmware resource configuration for Wi-Fi 7 ath12k hardware families. It fills `struct ath12k_wmi_resource_config_arg` differently for QCN9274-style full chips and WCN7850/QCC2072-style client chips before WMI init commands are sent to firmware.

## Important APIs And Functions

`ath12k_wifi7_wmi_init_qcn9274()` sizes resources from `ab->num_radios`, target constants, and `ath12k_core_get_max_peers_per_radio()`. It configures vdevs, peers, offload peers/reorder buffers, peer keys, AST skid, chain masks, RX timeouts, decap mode (raw or native Wi-Fi depending on `ATH12K_FLAG_RAW_MODE`), scan/roam/beacon/EMA settings, multicast/WDS/DMA resources, TWT AP counts, peer map/unmap version `0x32`, and peer metadata version `ATH12K_PEER_METADATA_V1B` when supported.

`ath12k_wifi7_wmi_init_wcn7850()` uses smaller fixed client-oriented resources: four vdevs, 16 peers, 32 TIDs, native Wi-Fi decap, zero multicast-to-unicast/WDS/DMA burst values, GTK/beacon offload limits of two, `num_msdu_desc = 0x400`, peer map/unmap version `0x1`, `use_pdev_id = 1`, TDLS/WOW/multicast-filter limits, and peer metadata version V1A if supported or the firmware-reported DP peer metadata version otherwise.

## Control Flow And Integration

`hw.c` stores one of these functions in `ath12k_hw_params.wmi_init`. During firmware initialization, common WMI code calls the selected function with the device base and a resource config structure, then sends that populated configuration to firmware. The functions are pure initializers with no allocation and no return value.

## State And Persistence Behavior

The functions mutate only the supplied resource config argument. The resulting values persist in firmware after WMI init and affect target resource allocation, peer/vdev capacity, RX decapsulation, offloads, multicast behavior, TWT/EMA capabilities, peer metadata format, and WOW/TDLS support. They also read runtime state such as `ab->target_caps.num_rf_chains`, `ab->dev_flags`, `ab->wmi_ab.svc_map`, and `ab->wmi_ab.dp_peer_meta_data_ver`.

## Dependencies

The file includes `../core.h` and local `wmi.h`. It depends on many common WMI target constants, service bits, ath12k base fields, and raw-mode flags. It integrates with `hw.c` hardware parameter selection and shared WMI firmware boot code.

## Risks And Edge Cases

Wrong resource sizing can cause firmware init failures or later peer/vdev exhaustion. QCN9274 scales several values by radio count; WCN7850 uses fixed small limits, so assigning the wrong initializer to hardware would be visible quickly. Peer metadata version selection is service-bit dependent and must match DP RX peer metadata parsing. Raw mode is honored for QCN9274 but WCN7850 forces native Wi-Fi decap, which is intentional but should be tested if raw-mode support changes.

## Test Signals

Firmware boot should accept the resource config on each hardware family. Functional tests should cover max vdev/peer creation near limits, raw mode on QCN9274, native Wi-Fi RX on WCN7850, peer map/unmap events, metadata parsing, WOW filters, TDLS entries, GTK offload, beacon offload, scan/roam limits, and TWT/EMA AP behavior where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/wmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/wmi.h

## Purpose

`wmi.h` declares the Wi-Fi 7 hardware-family WMI resource initialization functions.

## Important APIs

It exports `ath12k_wifi7_wmi_init_qcn9274(struct ath12k_base *ab, struct ath12k_wmi_resource_config_arg *config)` and `ath12k_wifi7_wmi_init_wcn7850(struct ath12k_base *ab, struct ath12k_wmi_resource_config_arg *config)`. Both functions fill a caller-provided WMI resource config for firmware initialization.

## Control Flow And Integration

`hw.c` includes this header and stores the function pointers in `ath12k_hw_params`. Common WMI setup later calls the selected initializer for the active hardware revision before sending resource configuration to firmware.

## State And Persistence Behavior

The header owns no state. The declared functions mutate the resource config passed by the caller and indirectly determine persistent firmware resource allocation after boot.

## Dependencies

The header relies on declarations for `struct ath12k_base` and `struct ath12k_wmi_resource_config_arg` being available to includers. It is protected by `ATH12K_WMI_WIFI7_H`.

## Risks And Edge Cases

Prototype drift between this header and `wmi.c` would break hardware parameter assignment or common WMI calls. Callers must pass a valid, writable config structure; the functions do not report errors.

## Test Signals

Build coverage should ensure both prototypes match their definitions. Probe and firmware boot on QCN9274, WCN7850, and QCC2072 verify correct function pointer selection and valid WMI resource initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/wmi.h -->
