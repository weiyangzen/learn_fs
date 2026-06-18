<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.h

## Purpose
Defines RTL8723BE TX/RX descriptor sizes, bitfield accessors, early-mode metadata accessors, PHY status structures, descriptor structures, and TRX function prototypes.

## Important APIs, Types, And Functions
- Size constants: `TX_DESC_SIZE`, `TX_DESC_AGGR_SUBFRAME_SIZE`, `RX_DESC_SIZE`, `RX_DRV_INFO_SIZE_UNIT`, `TX_DESC_NEXT_DESC_OFFSET`, `USB_HWDESC_HEADER_LEN`, and `CRCLENGTH`.
- TX descriptor setters cover packet size, offset, BMC, HTC, segment flags, OWN, MAC ID, queue select, rate ID, security type, aggregation, RDG, fragmentation, AMPDU density, hardware sequence, rate/fallback, RTS/CTS, bandwidth, SGI, DMA buffer size/address, and next descriptor address.
- RX descriptor getters/setters cover packet length, CRC/ICV, driver-info size, shift, PHY status, software decrypt flag, OWN, MAC ID, aggregation, C2H report select, rate/MCS, HT, wake matches, SPLCP, bandwidth, TSF, buffer address, and TX report 2 bitmaps.
- Early-mode setters encode packet count and five length fields.
- Structures include `phy_rx_agc_info_t`, `phy_status_rpt`, `rx_fwinfo_8723be`, `tx_desc_8723be`, and `rx_desc_8723be`.
- Prototypes expose `rtl8723be_tx_fill_desc`, `rtl8723be_rx_query_desc`, descriptor get/set helpers, TX close check, polling, and command descriptor fill.

## Control Flow
The inline helpers perform little-endian bit extraction and replacement using `le32_get_bits`, `le32p_replace_bits`, `cpu_to_le32`, and `le32_to_cpu`. `clear_pci_tx_desc_content` clears only the first descriptor area up to `TX_DESC_NEXT_DESC_OFFSET`, preserving possible extended fields outside that range.

## State And Persistence
The helpers directly mutate or read descriptor memory shared with hardware. The packed descriptor and PHY status structures document hardware-provided memory layouts. Because descriptor rings are persistent DMA-visible structures, field correctness persists across queue ownership handoff until the ring entry is reused.

## Dependencies And Integration Points
Consumed by `trx.c` and rtlwifi PCI descriptor ring code. It depends on Linux endian helpers, bit macros, mac80211-facing TRX prototypes, and RTL8723BE hardware descriptor format. The structures also anchor RX PHY parsing and TX descriptor programming in the HAL ops table.

## Risks And Edge Cases
Bitfield C structures are for documentation and typed access only; portable behavior relies on the inline endian helpers. Any bit offset or mask change can break DMA descriptors. `USB_HWDESC_HEADER_LEN` is reused as a descriptor offset in this PCI driver, so renaming or changing it carelessly can affect TX layout. 64-bit DMA address fields exist in the structure but the helpers here set 32-bit addresses, so DMA mask assumptions matter.

## Test Signals
Compile coverage, descriptor dumps matching hardware documentation, TX/RX traffic, AMPDU and fragmented frames, 32-bit DMA address operation, RX PHY status parsing, and no endian or sparse warnings around packed/bitfield structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/trx.h -->
