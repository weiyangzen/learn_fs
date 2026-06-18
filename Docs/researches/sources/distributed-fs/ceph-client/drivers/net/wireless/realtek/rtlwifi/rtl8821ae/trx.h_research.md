# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/trx.h

## Purpose
Defines RTL8821AE descriptor sizes, descriptor bitfield accessors, PHY status structures, early-mode setters, packed TX/RX descriptor layouts, and the TX/RX descriptor API used by the chip-specific HAL operations.

## Important APIs, Types, And Functions
Important constants are `TX_DESC_SIZE`, `RX_DESC_SIZE`, `RX_DRV_INFO_SIZE_UNIT`, `TX_DESC_NEXT_DESC_OFFSET`, `USB_HWDESC_HEADER_LEN`, and `CRCLENGTH`. Inline setters and getters cover TX packet size, offset, BMC/HTC/segment/OWN, MAC ID, queue, rate ID, security, aggregation, RDG, fragmentation, sequence, RTS/CTS, bandwidth, SGI, buffer size/address, next descriptor address, RX length/errors/driver info/shift/PHY status/OWN/MAC ID/rate/bandwidth/timestamp/buffer address, TX report 2 masks, and early-mode lengths. Data types include `struct phy_rx_agc_info_t`, `struct phy_status_rpt`, `struct rx_fwinfo_8821ae`, `struct tx_desc_8821ae`, and `struct rx_desc_8821ae`.

## Control Flow
The header itself has inline register/descriptor field manipulation only. Runtime control flow is in `trx.c`, which calls these accessors while parsing RX descriptors and filling TX descriptors.

## State And Persistence
The accessors mutate little-endian descriptor memory supplied by ring or skb code. Packed structures describe hardware-owned memory layouts and do not allocate persistent state.

## Dependencies And Integration Points
Relies on Linux bit helpers such as `le32p_replace_bits`, `le32_get_bits`, `GENMASK`, `BIT`, and endian conversion helpers. It is included by `rtl8821ae/trx.c` and referenced through HAL ops registered in `sw.c`. The descriptor layout must match PCI hardware and firmware TX report expectations.

## Risks And Edge Cases
The packed bitfield structs are documentation-like and compiler-layout-sensitive; the inline little-endian accessors are the safer operational interface. Some names are USB-derived, such as `USB_HWDESC_HEADER_LEN`, even though this is the PCI chip path. Address setters/getters use 32-bit values, so they require compatible DMA constraints. Clearing a descriptor intentionally preserves bytes beyond `TX_DESC_NEXT_DESC_OFFSET` when a larger structure is passed, protecting next-descriptor pointers but requiring callers to understand the boundary.

## Test Signals
Compile tests catch accessor signature issues. Runtime signals include correct descriptor ownership transitions, valid TX DMA addresses, RX rate/bandwidth extraction, TX report 2 parsing, early-mode aggregation behavior, and successful traffic across all queues and bandwidths.
