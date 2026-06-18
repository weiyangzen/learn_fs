# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ams-delta.c

## Purpose
`ams-delta.c` is a GPIO-driven raw NAND controller driver for the Amstrad E3/Delta platform. It implements the modern raw NAND `exec_op` interface by bit-banging command, address, data, read-enable, write-enable, chip-enable, ready, and write-protect GPIOs.

## Important APIs, Types, and Functions
`struct gpio_nand` embeds `struct nand_controller` and `struct nand_chip`, GPIO descriptors for control lines, an optional data GPIO array, data direction state, timing fields `tRP`/`tWP`, and byte I/O callbacks. Key functions are `gpio_nand_probe()`, `gpio_nand_remove()`, `gpio_nand_exec_op()`, `gpio_nand_setup_interface()`, `gpio_nand_attach_chip()`, `gpio_nand_io_read()`, `gpio_nand_io_write()`, `gpio_nand_dir_input()`, `gpio_nand_dir_output()`, `gpio_nand_read_buf()`, and `gpio_nand_write_buf()`.

## Control Flow
Probe allocates the private structure, wires MTD parent/OF node, obtains optional RDY/NWP/NCE/NRE/NWE GPIOs and required ALE/CLE GPIOs, optionally obtains the data GPIO array, installs byte I/O callbacks, runs any platform/OF match-data probe hook, initializes the embedded controller with `gpio_nand_ops`, releases write protection, defaults ECC engine type to software, calls `nand_scan()`, and registers partitions. `gpio_nand_exec_op()` asserts chip select, walks NAND operation instructions, toggles CLE/ALE around command/address writes, performs data reads/writes through GPIO bytes, waits ready via RDY GPIO or soft wait, then deasserts chip select.

## State and Persistence
Runtime state is GPIO direction (`data_in`), timing pulse widths derived from NAND SDR timings, and write-protect/chip-enable line levels. Persistent flash state comes from NAND commands issued through `exec_op`. Remove reapplies write protection before unregistering and cleaning up NAND state.

## Dependencies and Integration Points
It depends on gpiolib, `linux/mtd/rawnand.h`, `linux/mtd/nand-gpio.h`, platform data (`struct gpio_nand_platdata`) or DT GPIO descriptors, and MTD partition registration. Kconfig builds it under `CONFIG_MTD_NAND_AMS_DELTA`.

## Risks
The driver is timing-sensitive and slow because it bit-bangs every byte. Optional GPIOs allow multiple hardware descriptions, but missing required ALE/CLE or incomplete I/O callbacks abort probe. The FIXME notes write protection is released before `nand_scan()` due to missing core WP control. Direction changes and raw GPIO array ordering must match board wiring exactly.

## Test Signals
Probe should succeed with complete GPIO descriptors and fail clearly with incomplete configuration. Tests should exercise command/address/data instruction sequences, RDY GPIO and soft-wait paths, setup-interface timing updates, software Hamming ECC defaulting, write-protect assertion on remove, and partition registration.
