<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-fiu.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-fiu.c

## Purpose

`spi-npcm-fiu.c` is the Nuvoton NPCM Flash Interface Unit SPI-MEM controller driver. It supports FIU instances with multiple chip selects, direct memory-mapped reads and writes through reserved flash windows, and UMA register transactions for commands that cannot use direct mapping. It handles both standard FIU and SPIX mode.

## Important APIs, Types, and Functions

`struct npcm_fiu_info` describes FIU instance name, id, maximum mapping size, and chip-select count. `struct fiu_data` groups per-SoC FIU arrays for NPCM7xx and NPCM8xx. `struct npcm_fiu_chip` stores per-CS mapped flash pointer and clock rate. `struct npcm_fiu_spi` stores chips, selected info, cached direct-read op, memory resource, regmap, clock, and SPIX mode flag.

Direct-map helpers are `npcm_fiu_set_drd()`, `npcm_fiu_direct_read()`, `npcm_fiu_direct_write()`, `npcm_fiux_set_direct_rd()`, `npcm_fiux_set_direct_wr()`, and `npcm_fiu_dirmap_create()`. UMA helpers are `npcm_fiu_uma_read()`, `npcm_fiu_uma_write()`, `npcm_fiu_manualwrite()`, `npcm_fiu_read()`, and `npcm_fiu_exec_op()`. `npcm_fiu_setup()` records per-device clock rate and chip-select metadata.

## Control Flow

Probe allocates a SPI controller, reads SoC match data, derives FIU id from the `fiu` OF alias, selects FIU instance limits, maps the control resource through regmap, records optional memory resource, enables the FIU clock, reads SPIX mode, fills SPI-MEM callbacks, and registers the controller with the instance-specific chip-select count.

`dirmap_create` verifies that reserved memory exists and that the operation is suitable for direct mapping. It maps the per-chipselect aperture at `memory.start + max_map_size * cs`, applies an NPCM750 GCR FIU fix or local FIU fix bit, and programs direct read/write configuration. Direct reads either copy from IO memory or byte-read in SPIX mode; direct writes copy to IO memory or byte-write in SPIX mode.

`exec_op` rejects SPIX mode and addresses over four bytes, updates the FIU clock to the selected chip rate, then dispatches to UMA read/write variants. Reads with an address are chunked in 16-byte UMA reads. Writes without data, address-only writes, data-only writes, and address-plus-data writes use different UMA command sequences; manual writes hold software CS across command/address setup and 16-byte data chunks.

## State and Persistence Behavior

Cached direct-read operation fields avoid reprogramming DRD registers when direct-map reads repeat the same opcode/address width/dummy configuration. Per-chip `flash_region_mapped_ptr` persists once a direct-map aperture is mapped. Per-chip `clkrate` is learned from `spi->max_speed_hz` and applied in `exec_op`.

The driver stores no host data persistently. Direct and UMA writes modify attached flash devices.

## Dependencies and Integration Points

The driver integrates with SPI-MEM, platform/OF matching for `nuvoton,npcm750-fiu` and `nuvoton,npcm845-fiu`, regmap MMIO, optional syscon GCR fixups, clock framework, IO memory resources named `control` and optional `memory`, and device-tree aliases.

## Risks and Edge Cases

No `supports_op` callback is provided, so unsupported operations fail from `exec_op` rather than being rejected earlier. UMA read/write data registers are limited to 16 bytes, making chunking essential. `npcm_fiu_read()` subtracts 16 from `currlen` even when the last `readlen` is smaller; the loop still terminates but the bookkeeping is non-intuitive. Direct mapping silently disables itself by setting `nodirmap` when resources or fixups are unavailable.

SPIX mode bypasses UMA `exec_op` entirely and uses byte-wise direct IO, so coverage must include both modes.

## Test Signals

Tests should cover FIU0/FIU1/FIU3/FIUX instance selection, invalid aliases, per-chipselect mapping offsets, direct read opcode/dummy/address-width changes, direct writes in SPIX mode, UMA command-only/address-only/data-only/address-plus-data operations, 16-byte chunk boundaries, clock-rate switching, absent memory resource fallback, NPCM750 GCR fixup absence, and regmap polling timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-fiu.c -->
