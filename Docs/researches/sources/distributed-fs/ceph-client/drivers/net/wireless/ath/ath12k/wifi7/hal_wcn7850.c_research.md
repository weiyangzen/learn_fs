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
