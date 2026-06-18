# sources/distributed-fs/ceph-client/drivers/ata/pata_ixp4xx_cf.c

`pata_ixp4xx_cf.c` drives CompactFlash cards wired to the Intel IXP4xx expansion bus in TrueIDE mode. It is a PIO-only OF platform driver that configures expansion-bus chip-select timing through a parent syscon/regmap and switches bus width during data transfers.

`struct ixp4xx_pata` stores the libata host, regmap, command chip-select timing register, and mapped command/control windows. `ixp4xx_set_8bit_timing()` and `ixp4xx_set_16bit_timing()` write timing constants and bus-width bits for PIO0-4. `ixp4xx_mmio_data_xfer()` locks the ATA port, switches to 16-bit timing, transfers words with `readw()`/`writew()`, handles an odd trailing byte, restores 8-bit timing, and unlocks. `ixp4xx_setup_port()` maps SFF addresses and XOR-swizzles them on little-endian systems.

Probe obtains the parent syscon regmap, derives the command chip select from the first `reg` cell, allocates a one-port host, maps command/control resources, gets an IRQ, sets it edge-rising, configures the port, and activates with `ata_sff_interrupt()`. Removal is `ata_platform_remove_one()`.

State is the regmap/timing register and MMIO windows. Dependencies are OF, syscon/regmap, IRQ configuration, MMIO, and libata SFF. Risks include DT chip-select mistakes, failing to restore 8-bit timing, little-endian address swizzling errors, and IRQ polarity. Tests should cover endian mappings, odd-byte transfers, PIO0-4 timing writes, syscon/resource failures, no-ATAPI behavior, and interrupt delivery.
