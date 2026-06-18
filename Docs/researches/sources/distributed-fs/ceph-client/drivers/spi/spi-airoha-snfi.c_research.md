# sources/distributed-fs/ceph-client/drivers/spi/spi-airoha-snfi.c

## Purpose

`spi-airoha-snfi.c` is a SPI-MEM controller driver for the Airoha SPI NAND Flash Interface. It provides manual FIFO command execution for generic SPI-MEM operations and optional NFI DMA direct-mapping paths for SPI NAND cache read/write operations.

The controller is split into a SPI control register block and an NFI-to-SPI register block. The driver exposes the hardware as a SPI controller with memory operations, not as a generic full-duplex SPI bus.

## Important APIs, types, and functions

- `struct airoha_snand_ctrl` stores the device, SPI control regmap, NFI regmap, and SPI clock.
- `airoha_snand_set_fifo_op()`, `*_write_data_to_fifo()`, and `*_read_data_from_fifo()` implement manual FIFO command and byte-data transfers with poll timeouts.
- `airoha_snand_set_mode()` switches between manual, DMA, and auto-ish controller modes by programming control registers.
- `airoha_snand_supports_op()` validates bus widths and distinguishes page-cache operations from generic single-lane commands.
- `airoha_snand_dirmap_create()` accepts direct maps up to `SPI_NAND_CACHE_SIZE` and only for supported op templates.
- `airoha_snand_dirmap_read()` and `airoha_snand_dirmap_write()` use the NFI DMA engine to transfer rounded cache data to/from a per-device cache buffer.
- `airoha_snand_exec_op()` sends opcode, address, dummy bytes, and data through manual FIFO mode.
- `airoha_snand_setup()` allocates a per-SPI-device `SPI_NAND_CACHE_SIZE` buffer and stores it with `spi_set_ctldata()`.

## Control flow

Probe maps two resources, creates regmaps, enables the SPI clock, optionally disables DMA on a known bad EN7523 boot strap, sets a 32-bit DMA mask, fills controller properties, initializes the NFI block, and registers the controller.

Manual operation flow switches to manual mode, lowers chip select through FIFO command, writes opcode/address/dummy segments, transfers data in chunks capped at `SPI_MAX_TRANSFER_SIZE`, and raises chip select. Direct-map read/write switches to DMA mode, resets and configures the NFI block, maps the per-device cache buffer, programs DMA address/length/opcode/mode/address registers, triggers the read or write, polls completion bits, unmaps, returns to manual mode, and copies the requested subrange.

## State and persistence behavior

The driver maintains little mutable software state beyond the regmaps, clock, and per-device cache buffer. Hardware mode persists in controller registers; both success and error paths try to return to manual mode after DMA. The direct-map buffer is device-managed and lives as long as the SPI device.

## Dependencies and integration points

The driver depends on platform resources for the two MMIO regions, a `"spi"` clock, regmap-mmio, DMA mapping, OF compatibles, and SPI-MEM. It integrates with SPI NAND through SPI-MEM direct mapping and supports cache opcodes such as read-from-cache and program-load variants.

## Risks and edge cases

- `airoha_snand_set_cs()` contains a duplicated unreachable `return`; behavior is unaffected, but it signals a cleanup opportunity.
- Direct-map reads round `offs + len` up to 64 bytes and use a fixed 4 KiB+256 cache buffer; bounds are guarded by dirmap length but should be kept aligned with SPI NAND geometry.
- EN7523 reserved boot mode disables DMA due to known data-damage risk. Tests must cover both DMA and no-DMA mem-op tables.
- DMA paths manually toggle controller modes and completion bits; error paths must always restore manual mode.
- Bus-width support is intentionally narrow for page operations and single-lane for generic commands.
- The OF match table only lists `airoha,en7581-snand`, while probe also checks `airoha,en7523-snand`; this mismatch may make the EN7523-specific branch unreachable unless matched through another compatible string.

## Test signals

Build with `CONFIG_SPI_AIROHA_SNFI`. Runtime tests should cover reset/read-id/get-feature/set-feature via manual FIFO, cache read/write through direct-map DMA, PIO fallback/no-DMA mode, dual and quad read/program-load opcodes, DMA timeout/error handling, and EN7523 strap behavior. SPI NAND MTD tests should verify data integrity across page and OOB boundaries.
