# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/plat_nand.c

Purpose: this is a generic platform-data NAND wrapper. It lets board code provide legacy NAND control callbacks, chip options, partition data, and optional probe/remove hooks while the driver supplies resource mapping, controller initialization, optional READY GPIO support, scanning, and MTD registration.

Important APIs, types, and functions: `struct plat_nand_data` contains the controller, chip, mapped IO base, and optional ready GPIO. `plat_nand_gpio_dev_ready()` reads the `ready` GPIO when present. `plat_nand_attach_chip()` selects Hamming when software ECC was requested without an explicit algorithm. `plat_nand_probe()` and `plat_nand_remove()` are the main lifecycle functions.

Control flow: probe requires `platform_nand_data` and at least one chip, allocates state, obtains an optional `ready` GPIO, initializes the raw NAND controller, maps resource 0, copies platform callbacks/options into `chip->legacy`, runs the platform-specific `ctrl.probe()` hook, defaults the ECC engine to software, scans `nr_chips`, and registers partitions through `mtd_device_parse_register()`. On error or remove it calls `nand_cleanup()` and the platform `ctrl.remove()` hook when provided.

State and persistence: driver state is the mapped IO base, optional GPIO descriptor, NAND core state, and platform-provided chip/BBT options. Partition and BBT persistence are delegated to the MTD/NAND core and board-supplied options.

Dependencies and integration points: this driver depends on legacy board-provided `struct platform_nand_data`, GPIO descriptors, raw NAND legacy callbacks, and compatible `gen_nand`. It is a bridge for older non-discoverable NAND wiring rather than a hardware-specific controller.

Risks: correctness depends almost entirely on platform callbacks and options. Missing platform data fails probe even with a matching OF compatible. If no READY GPIO is supplied, readiness behavior falls back to platform code, which may be null depending on board setup. Platform `probe()` side effects must be undone by `remove()` on both normal and error paths.

Test signals: valid and invalid platform data, optional READY GPIO behavior, board callback invocation order, multi-chip scan based on `nr_chips`, partition parsing from platform and probe types, software Hamming defaulting, and cleanup hook execution after scan/register failures.
