<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi-avmm.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi-avmm.c

Purpose: Implements a regmap bus for SPI slaves containing an SPI-to-Avalon-MM bridge, translating regmap reads/writes through transaction, packet, and physical protocol layers.

Important APIs/types/functions: `struct spi_avmm_bridge` holds the SPI device, word length, transaction/physical buffers, and optional word-swap callback. `br_trans_tx_prepare()`, `br_pkt_phy_tx_prepare()`, `br_do_tx()`, `br_do_rx_and_pkt_phy_parse()`, `br_rd_trans_rx_parse()`, `br_wr_trans_rx_parse()`, and `do_reg_access()` form the protocol pipeline. `regmap_spi_avmm_write/read/gather_write()` expose regmap callbacks. Exported wrappers are `__regmap_init_spi_avmm()` and `__devm_regmap_init_spi_avmm()`.

Control flow: Access begins by formatting a transaction header with operation code, byte size, and 32-bit address. Writes append little-endian 32-bit values. Packet/physical preparation wraps data in SOP/channel/EOP framing, escapes reserved bytes, pads to SPI word length, and moves EOP toward the aligned tail to avoid losing early slave responses. TX sends the prepared buffer. RX repeatedly reads one SPI word, swaps if using 32-bit words, skips idle bytes, parses SOP/channel/escape/EOP, times out after sustained invalid data, and fills the transaction buffer. Read responses are raw little-endian values; write responses are validated transaction headers.

State and persistence behavior: Bridge context is allocated per regmap and freed by the bus. Buffers are reused per access and invalidated by resetting lengths before each operation. SPI mode and bits-per-word are configured during context generation, trying 32-bit then falling back to 8-bit.

Dependencies and integration points: Depends on SPI sync read/write APIs, byte swapping, regmap raw bus callbacks, and the Intel SPI slave to Avalon bridge protocol. Regmap max raw read/write are capped by protocol constants.

Risks: This is protocol-heavy and sensitive to byte escaping, alignment, timeout policy, channel number, and 8-vs-32-bit SPI word ordering. Only one write value is supported (`MAX_WRITE_CNT == 1`) while reads allow up to 256 values. Parser errors return `-EFAULT`; sustained idle returns `-ETIMEDOUT`. The code mutates SPI mode/bits-per-word during setup, which may conflict with board expectations if shared assumptions exist.

Test signals: Strong tests should encode/decode reserved bytes, EOP padding with 32-bit words, timeout and last-try behavior, invalid channel/error cases, read count validation, write response validation, SPI setup fallback, and raw length caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi-avmm.c -->
