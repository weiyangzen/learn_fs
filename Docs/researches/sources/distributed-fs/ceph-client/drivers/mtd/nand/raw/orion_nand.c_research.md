# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/orion_nand.c

Purpose: this is the Marvell Orion platform NAND glue driver. It maps a simple memory-mapped NAND window into the raw NAND legacy callbacks, derives command/address latch offsets from platform data or Device Tree, and registers one NAND chip as an MTD device.

Important APIs, types, and functions: `struct orion_nand_info` contains the `nand_controller`, `nand_chip`, and optional clock. `orion_nand_cmd_ctrl()` writes command bytes through CLE/ALE-derived offsets, adjusting for 16-bit bus width. `orion_nand_read_buf()` optimizes buffer reads with 64-bit ARM `ldrd` when available, otherwise uses `readsl()` plus byte tail handling. `orion_nand_attach_chip()` defaults unspecified software ECC to Hamming.

Control flow: probe allocates private state, initializes the controller ops, maps the MMIO resource, parses OF properties `cle`, `ale`, `bank-width`, and `chip-delay` or uses `orion_nand_data`, installs legacy NAND callbacks, enables an optional clock, sets software ECC as the driver default, runs `nand_scan()`, and registers partitions with `mtd_device_register()`. Remove unregisters the MTD device and calls `nand_cleanup()`.

State and persistence: state is limited to the NAND core structures, board latch geometry, bus width flag, optional clock lifetime, and registered MTD partitions. There is no suspend/resume or persistent on-flash policy beyond what the NAND core/partition layer manages.

Dependencies and integration points: the driver depends on raw NAND legacy callback support, MTD partition registration, common clock APIs, OF matching for `marvell,orion-nand`, and legacy `mtd-orion_nand.h` platform data. It assumes one chip select and a board-supplied latch layout.

Risks: OF defaults silently choose CLE bit 0, ALE bit 1, and 8-bit bus width, so incomplete DT can appear to probe but address the wrong latch lines. The optimized ARM read path is architecture-specific and bypasses generic IO helpers. `board` is not explicitly null-checked after legacy platform-data lookup, so non-OF users must provide valid data. Widths above 16 only warn and then continue.

Test signals: probe on OF and platform-data boards, correct ID reads under default and custom CLE/ALE values, 8-bit and 16-bit bus operation, optional clock enable failure handling, partition registration, software Hamming default selection, and clean unregister/remove.
