
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/trx.h

Purpose: Defines RTL8192CU USB TRX constants, RX PHY-info layout, descriptor bit accessors, and public USB TX/RX helper prototypes.

Important APIs/types: Constants include `RTL92C_NUM_RX_URBS` 8, `RTL92C_NUM_TX_URBS` 32, `RTL92C_SIZE_MAX_RX_BUFFER` 15360, USB RX aggregation modes, endpoint selection bits, USB TX/RX aggregation tuning, and `RX_DRV_INFO_SIZE_UNIT`. `struct rx_drv_info_92c` mirrors PHY status. RX getters parse packet length, CRC/ICV, driver info size, shift, PHY status, software decrypt, aggregation flags, MCS/HT/short preamble/bandwidth, and TSF. TX setters fill packet size, offset, BMC/HTC/segment/OWN, MAC ID, aggregation/RDG/QSEL/rate/security, sequence, RTS/CTS, bandwidth/subcarrier, fallback limits, aggregation count, and descriptor checksum. Prototypes expose endpoint mapping, queue mapping, RX query/handler, TX hooks, and descriptor fill functions.

Control flow: Header only. It is the descriptor access layer used by `trx.c` and HAL ops.

State and persistence: Inline setters write USB TX descriptor memory that is transmitted with the skb. RX getters parse device-provided little-endian descriptor memory. Constants configure persistent USB core behavior through `sw.c`.

Dependencies/integration: Used by `trx.c`, `sw.c`, and hardware init. Depends on kernel bit helpers and rtlwifi/mac80211 types.

Risks: Descriptor offset/mask errors are hardware-fatal. `RTL92C_SIZE_MAX_RX_BUFFER` comment says `8192` while value is `15360`, so buffer sizing assumptions need care. Because setters operate on `__le32 *`, callers must pass correctly aligned descriptor memory with enough dwords.

Test signals: Descriptor bitfield unit checks, USB RX buffer stress, TX checksum verification, queue selector mapping checks, and compile coverage for all prototypes used by `rtl_hal_ops` and `rtl_hal_usbint_cfg`.
