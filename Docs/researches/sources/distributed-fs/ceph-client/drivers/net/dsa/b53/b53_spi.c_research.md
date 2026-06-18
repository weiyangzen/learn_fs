# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_spi.c

Purpose: SPI transport for B53 managed switches.

Important APIs/types/functions: SPI command/status/page macros; `b53_prepare_reg_access()` clears status and selects page; `b53_spi_prepare_reg_read()` waits for RACK; width-specific read/write ops implement `b53_io_ops`; SPI probe/remove/shutdown register common B53.

Control flow: probe allocates B53 with SPI ops and optional platform data, registers switch, and stores driver data. Register reads clear status, select page, issue read, poll RACK, then read data. Writes clear/select page and transmit command/register/value bytes.

State and persistence behavior: only the `spi_device` pointer in `dev->priv`; common core owns switch state.

Dependencies and integration points: Linux SPI APIs, unaligned little-endian helpers, OF/SPI ID tables, B53 platform data, common B53 exports.

Risks: ten-millisecond-ish status/RACK timeout can fail on slow hardware; payloads assume little-endian layout; no explicit PHY access ops; unused fast command macro.

Test signals: probe/remove for IDs, all register widths including 48-bit, timeout injection, and DSA traffic over SPI.
