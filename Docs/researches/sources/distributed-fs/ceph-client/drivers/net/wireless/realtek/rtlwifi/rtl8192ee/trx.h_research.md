# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/trx.h

## Purpose
This header defines the RTL8192EE TX/RX descriptor bitfield accessors, descriptor constants, PHY-status layouts, and exported TX/RX descriptor APIs. It is the low-level hardware descriptor contract used by `trx.c` and the rtlwifi PCI layer.

## Important APIs, Types, And Functions
The header defines descriptor sizes and offsets such as `TX_DESC_SIZE`, `RX_DESC_SIZE`, `RX_DRV_INFO_SIZE_UNIT`, `USB_HWDESC_HEADER_LEN`, and `MAX_RECEIVE_BUFFER_SIZE`. Inline setters/getters manipulate TX descriptor fields for packet size, offsets, BMC/HTC, first/last segment, ownership, MAC id, queue select, rate id, security type, aggregation, RTS/CTS, bandwidth, fallback limits, sequence, DMA address, and next-descriptor address.

Separate inline helpers operate on PCIe TX buffer descriptors and RX buffer descriptors, including 64-bit DMA high-address handling gated by `dma64`. RX status helpers parse packet length, CRC/ICV, driver-info size, shift, PHY status, software decryption, MAC id, aggregation, report type, MCS, WoWLAN match bits, TSF, buffer address, and TX report 2 bitmaps. `struct phy_status_rpt`, `struct rx_fwinfo`, `struct tx_desc`, and `struct rx_desc` document packed hardware layouts. Function prototypes expose the chip descriptor operations to `sw.c` HAL ops.

## Control Flow
There is no independent runtime control flow, but every TX/RX path in `trx.c` flows through these inline accessors. They perform little-endian bit replacement/extraction directly on memory shared with the device, so callers must provide correctly aligned descriptor buffers and apply ownership changes at the correct point in the ring lifecycle.

## State And Persistence
The header defines how state is stored in descriptor memory. Descriptor contents persist until the driver clears or rewrites the ring entry and until hardware consumes or produces it. Packed PHY-status structs describe transient RX metadata delivered alongside a received frame.

## Dependencies And Integration Points
It depends on Linux endian/bitfield helpers available through included rtlwifi headers and on rate constants such as `DESC_RATE1M` through `DESC_RATEMCS*`. It must match the RTL8192EE hardware manual, PCI ring allocation sizes, and `trx.c` parser/filler assumptions.

## Risks
Bitfield mistakes are severe because they directly change hardware DMA behavior. The `set_tx_desc_data_bw()` helper writes into dword 4 while its comment places it under dword 5, so maintainers must follow code and hardware spec, not comments alone. `set_tx_desc_next_desc_address()` writes `pdesc + 12` despite a dword 11 comment, reflecting the 64-byte layout and reserved fields; changing it casually would corrupt rings. Packed bitfield structs are documentation/legacy conveniences and are sensitive to endian assumptions; active code mostly uses safer le32 helpers.

## Test Signals
Build testing catches missing helpers; runtime coverage should verify descriptor ownership, DMA address recovery, ring wraparound, RX length/shift parsing, 64-bit DMA mode, WoWLAN match extraction, and TX/RX under all rates and aggregation modes. Sparse/endian checks and DMA API debug are useful companions.
