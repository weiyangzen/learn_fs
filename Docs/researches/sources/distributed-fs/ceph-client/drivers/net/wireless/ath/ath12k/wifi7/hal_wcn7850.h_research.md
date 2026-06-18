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
