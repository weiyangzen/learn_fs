# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/trx.h

## Purpose
Defines the RTL8723E PCI transmit and receive descriptor layout used by the rtl8723ae driver. It is a hardware contract header: descriptor sizes, bitfield setters/getters, packed descriptor structures, RX PHY status metadata, and the exported TX/RX descriptor operation prototypes used by the PCI queue layer.

## Important APIs, Types, And Functions
The inline setters populate TX descriptor words for packet size, offset, ownership, MAC id, queue selector, security type, sequence number, RTS/CTS control, fixed TX rate, bandwidth, short GI, retry fallback limits, buffer size, DMA buffer address, and next descriptor address. RX accessors decode length, CRC/ICV errors, driver-info size, PHY status, software decrypt flag, aggregation flags, MCS/rate, HT flag, short preamble, bandwidth, TSF, and DMA buffer address. `clear_pci_tx_desc_content()` zeroes descriptor content up to the hardware next-descriptor offset. `struct tx_desc_8723e`, `struct rx_desc_8723e`, and `struct rx_fwinfo_8723e` document the packed hardware bit layout. The prototypes bind to implementation functions such as `rtl8723e_tx_fill_desc()`, `rtl8723e_rx_query_desc()`, `rtl8723e_set_desc()`, `rtl8723e_get_desc()`, `rtl8723e_is_tx_desc_closed()`, `rtl8723e_tx_polling()`, and `rtl8723e_tx_fill_cmddesc()`.

## Control Flow
The file itself has no runtime control loop; callers allocate descriptors in TX/RX rings, clear or update fields through these inline helpers, and then hand ownership to or from hardware by toggling OWN bits. TX preparation fills descriptor metadata and DMA addresses before polling the queue; RX completion reads fields to build `rtl_stats` and `ieee80211_rx_status` and then returns buffers to hardware.

## State And Persistence
Descriptor state is persistent only while a DMA ring entry is live. The packed C bitfields mirror little-endian hardware words but actual safe access is through `__le32` helpers, which preserve endian correctness. Ownership bits synchronize software and NIC use of the same ring slots.

## Dependencies And Integration Points
Depends on Linux bit helpers (`GENMASK`, `BIT`, `le32_get_bits`, `le32p_replace_bits`) and rtlwifi/mac80211 data types. It integrates with rtl8723ae PCI TX/RX implementation files, the common rtlwifi queue code, and DMA-mapped skb buffers.

## Risks
The main risk is descriptor contract drift: wrong bit masks, byte order, or offsets can corrupt DMA, leak ownership, or misclassify RX frames. The packed bitfield structures are documentation-like and compiler-sensitive; the inline little-endian helpers are the safer operational API. Descriptor clearing must not erase the next descriptor pointer past `TX_DESC_NEXT_DESC_OFFSET`.

## Test Signals
Useful signals are successful TX completion without stuck OWN bits, RX frames with correct length/status/rate/bandwidth, no DMA mapping warnings, no malformed skb lengths, correct encryption status reporting, and stable operation under aggregation, RTS/CTS, fixed-rate management TX, and ring wraparound.
