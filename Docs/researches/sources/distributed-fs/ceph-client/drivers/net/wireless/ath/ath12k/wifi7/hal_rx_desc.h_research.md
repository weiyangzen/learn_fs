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
