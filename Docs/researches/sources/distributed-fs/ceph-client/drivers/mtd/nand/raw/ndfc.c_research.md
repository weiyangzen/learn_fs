# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ndfc.c

Purpose: this is the Open Firmware platform driver for IBM/AMCC NDFC NAND Flash Controller hardware integrated in EP440-era cores. It supports one NAND chip per controller instance, maps NDFC command/address/data registers, and uses the controller's simple hardware Hamming ECC.

Important APIs, types, and functions: `struct ndfc_controller` stores the platform device, MMIO base, embedded `nand_chip`, chip select, and `nand_controller`. Legacy hooks include `ndfc_select_chip()`, `ndfc_hwcontrol()`, `ndfc_ready()`, `ndfc_read_buf()`, and `ndfc_write_buf()`. ECC hooks are `ndfc_enable_hwecc()` and `ndfc_calculate_ecc()`.

Control flow: probe reads the `reg` property to select one of four static controller slots, maps MMIO, programs the controller configuration register and optional bank settings, then initializes the child flash node. Chip init wires legacy callbacks, ON_HOST Hamming ECC over 256-byte steps with three ECC bytes, sets the flash node and MTD name, runs `nand_scan(chip, 1)`, and registers the MTD device.

State and persistence: state lives in the static `ndfc_ctrl[]` array and hardware registers. Remove unregisters MTD, calls `nand_cleanup()`, and frees the allocated MTD name, but the MMIO mapping is manually established in probe.

Dependencies and integration points: the driver depends on OF address/property helpers, `linux/mtd/ndfc.h` register definitions, raw NAND legacy core hooks, big-endian register accessors, MTD registration, and software Hamming correction (`rawnand_sw_hamming_correct`).

Risks: the driver is legacy-callback based and only supports one chip despite hardware multichip capability. Static controller slots and manual `of_iomap()` cleanup increase lifecycle sensitivity. Buffer I/O assumes page-aligned multiples of four. ECC byte ordering is NDFC/SmartMedia-specific.

Test signals: validate DT `reg`, `ccr`, and `bank-settings`, chip-select switching, ready bit polling, command/address cycles, 32-bit buffer transfers, hardware ECC calculation and correction, MTD registration/removal, and behavior on each supported chip select.
