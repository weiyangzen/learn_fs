# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/trx.h

`trx.h` defines the RTL8188EE TX/RX descriptor ABI. It provides descriptor sizes, early-mode helpers, little-endian bitfield accessors, packed documentation structs for TX/RX/PHY status layouts, CCK-rate detection, and exported descriptor function prototypes.

Important helpers include `set_tx_desc_*()` for packet size, offset, ownership, MAC ID, queue, security, aggregation, sequence, RTS/CTS, bandwidth, rate, fallback, antenna selection, buffer size/address, and next descriptor address; and `get_rx_desc_*()` for packet length, CRC/ICV, driver-info size, shift, PHY status, decryption, ownership, MAC ID, aggregation, sequence, rate, HT, bandwidth, report selection, wake matches, TSF, and buffer address. Packed structs document `phy_status_rpt`, `rx_fwinfo_88e`, `tx_desc_88e`, and `rx_desc_88e`.

The inline helpers mutate or read `__le32` descriptor words shared with DMA hardware. The header depends on Linux bit/endian helpers and rate constants. It is consumed by `trx.c`, PCI ring code, and HAL callbacks.

Risks include bit-position mistakes, endian regressions, packed bitfield portability assumptions, 32-bit DMA address helper limits, and confusing USB-named descriptor constants in PCI code. Test signals are descriptor dumps, TX/RX DMA success, ownership transitions, RX report parsing, WoWLAN wake fields, and early-mode aggregation.
