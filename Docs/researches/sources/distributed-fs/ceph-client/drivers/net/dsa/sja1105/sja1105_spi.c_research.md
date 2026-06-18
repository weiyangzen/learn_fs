# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_spi.c

## Purpose

This file provides the SPI transport, reset/static-config upload logic, register maps, and chip capability descriptors for the SJA1105/SJA1110 driver. It is the hardware access foundation used by dynamic config, MDIO, PTP, ethtool stats, clocking, and main DSA operations.

## Important APIs, Types, and Data

- `sja1105_xfer_buf()`, `sja1105_xfer_u64()`, and `sja1105_xfer_u32()` are exported SPI helpers for raw buffers and native-endian 64/32-bit register values.
- `sja1105_spi_message_pack()` builds the 4-byte SPI message header with access mode, read count, and address.
- `sja1105_xfer()` chunks large transfers according to `priv->max_xfer_len` and optionally asks the SPI core for system timestamps around PTP-sensitive transfers.
- Reset helpers `sja1105et_reset_cmd()`, `sja1105pqrs_reset_cmd()`, and `sja1110_reset_cmd()` implement generation-specific reset register writes.
- `sja1105_inhibit_tx()` toggles per-port TX inhibition through the port control register.
- `static_config_buf_prepare_for_upload()` validates, packs, and CRC-finalizes the static configuration image.
- `sja1105_static_config_upload()` inhibits TX, resets the switch, uploads the static config, checks status bits, and retries.
- `sja1105et_regs`, `sja1105pqrs_regs`, and `sja1110_regs` define per-generation register addresses.
- `sja1105e_info`, `sja1105t_info`, `sja1105p_info`, `sja1105q_info`, `sja1105r_info`, `sja1105s_info`, and `sja1110[a-d]_info` describe chip capabilities, callbacks, table ops, dynamic ops, tag protocol, PTP widths, port modes, internal PHYs, and register maps.

## Control Flow

All SPI transfers go through `sja1105_xfer()`. It splits a logical transfer into chunks, packs a header for the current register address, configures a two-transfer SPI message for header plus payload, chooses RX or TX buffer depending on access mode, attaches optional PTP system timestamp capture to the header for reads or data for writes, advances the buffer/register address, and calls `spi_sync_transfer()` for each chunk.

The typed helpers pack/unpack 32-bit and 64-bit values with the driver packing API so callers can use CPU-endian integers. The static upload path allocates a packed image, validates table constraints, packs all tables, recalculates final CRC, inhibits TX on all ports, waits for drain, resets into programming mode, writes the config area, reads status, checks device ID and CRC/config-valid bits, and retries up to ten times.

Chip info structures bind together the rest of the driver. Probe selects an initial info table from OF match data, verifies hardware identity in `sja1105_main.c`, and all later operations dispatch through callbacks and register maps from that selected info.

## State and Persistence Behavior

This file does not own high-level networking state, but it writes persistent hardware state during static config upload and reset. `priv->max_xfer_len` is computed at probe from SPI controller limits and controls all future chunking. Chip info structs are immutable capability tables. Register writes through SPI immediately affect hardware; static upload replaces the switch configuration and resets hardware state, so callers must maintain software mirrors for runtime changes.

## Dependencies and Integration Points

The code depends on Linux SPI APIs, the packing API, static config validation/packing/CRC helpers, DSA switch state for port counts, and chip-specific helper functions implemented in other files: dynamic ops, static table ops, FDB add/del, PTP command packers, timestamp functions, clocking setup, RGMII delay setup, SJA1110 microcontroller disable, and MDIO PCS callbacks. `sja1105_main.c` uses the info structures for device matching and DSA behavior.

## Risks and Edge Cases

- SPI master max transfer/message limits are runtime constraints. Probe ensures at least one 64-bit payload fits, and `sja1105_xfer()` chunks longer buffers; incorrect `max_xfer_len` would break static config upload and dynamic table operations.
- Read count is expressed in 32-bit words, so buffer lengths should be word-aligned for hardware register reads.
- Static upload retries but returns `-EIO` after repeated reset/upload/status failures. Status bit interpretation is critical for distinguishing device ID mismatch, local CRC, global CRC, and invalid config.
- TX inhibit before reset reduces PHY jabber risk; skipping it can generate malformed packets during reset.
- SJA1110 reset intentionally avoids a full cold reset to keep the microcontroller disabled; changing reset semantics can re-enable firmware that interferes with driver-owned config.
- Chip info tables are dense and generation-specific. Wrong callbacks or capability flags can misroute FDB algorithms, timestamp behavior, PCS access, port mode validation, or dynamic table packing.

## Test Signals

Probe should calculate an acceptable transfer size, verify device ID/part number, and report the detected chip. Static config upload should succeed without CRC/config status errors, including with SPI controllers that force chunking. Reset/reload paths should inhibit TX and recover. Register read/write users such as ethtool stats, MDIO, PTP, dynamic config, and clocking should work across E/T, P/Q/R/S, and SJA1110 variants. Device-tree compatible mismatches should warn and switch to the detected info table.
