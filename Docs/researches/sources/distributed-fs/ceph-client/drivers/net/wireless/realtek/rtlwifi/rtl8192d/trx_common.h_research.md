# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/trx_common.h

Purpose: Defines RTL8192D TX/RX descriptor bitfield helpers, RX PHY info layout, encryption enum, early-mode helpers, and shared descriptor API prototypes.

Important APIs/types: Provides `set_tx_desc_*`, `get_tx_desc_*`, `get_rx_desc_*`, `set_rx_desc_*`, and `set_earlymode_*` inline helpers using little-endian bitfield accessors. Defines `enum rtl92d_rx_desc_enc` and packed `struct rx_fwinfo_92d` containing gain, PWDB, CFO, EVM, SNR, CSI, SGI, RXSC, and interference fields.

Control flow: Header helpers are invoked by shared RX parsing and bus-specific TX descriptor fill code to set DMA ownership, queue selection, rate, security, RTS/CTS, aggregation, buffer addresses, and status extraction.

State and persistence: No header-owned state. The helpers read/write DMA descriptors shared with hardware, so their effects persist in descriptor rings until overwritten.

Dependencies and integration: Requires kernel little-endian bit helpers and rtlwifi descriptor names from surrounding code. Used by common TRX parsing and rtl8192de TX path.

Risks: Bit positions must match hardware exactly. Packed PHY layout depends on endianness bitfields. Missing barriers in callers would make ownership changes unsafe; this header only supplies primitives.

Test signals: Descriptor dump comparison, TX/RX DMA correctness, HT/SGI/bandwidth flags, encryption status, early-mode aggregation, and sparse/endian build coverage.
