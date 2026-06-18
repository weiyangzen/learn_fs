## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sharpsl.c

Purpose: this is the Sharp SL-C7xx NAND platform driver. It provides board-specific legacy NAND control-line handling, ready polling, hardware Hamming ECC access, bad-block/OOB layout handoff from platform data, and MTD partition registration.

Important APIs, types, and functions: `struct sharpsl_nand` embeds a `nand_controller`, one `nand_chip`, and an MMIO base. `sharpsl_nand_hwcontrol()` maps NAND CLE/ALE/NCE bits into the Sharp FLASHCTL register. `sharpsl_nand_dev_ready()` reads `FLRYBY`, while `sharpsl_nand_enable_hwecc()` and `sharpsl_nand_calculate_ecc()` operate the ECC registers. `sharpsl_attach_chip()` installs 256-byte, 3-byte, 1-bit host ECC using `rawnand_sw_hamming_correct()`. Probe/remove own allocation, mapping, scan, partition registration, and cleanup.

Control flow: probe requires `struct sharpsl_nand_platform_data`, allocates the controller object, maps the single IO resource, initializes the NAND controller ops, links the MTD parent, applies the platform OOB layout and bad-block pattern, enables flash write protect control, installs legacy IO callbacks, scans one chip, names it `sharpsl-nand`, and registers parser/static partitions. Commands then go through the generic legacy NAND core, which calls the driver’s `cmd_ctrl`, `dev_ready`, read/write IO addresses, and ECC callbacks.

State and persistence: driver state is limited to the mapped register window and embedded chip/controller. Hardware state includes FLASHCTL chip enable/CLE/ALE/WP bits and ECC latch/counter registers reset per ECC operation. Persistent media behavior comes from platform-supplied partitions, ECC layout, and bad-block pattern.

Dependencies and integration points: it integrates with the legacy raw NAND API, MTD partition parsers, `linux/mtd/sharpsl.h` platform data, PXA/Sharp board resources, and host-side Hamming correction. It is not DT-oriented and fails probe without platform data.

Risks: the control-line bit mapping is inverted and duplicates CE into two FLASHCTL bits, so regressions are board-specific and easy to miss. ECC calculation returns a nonzero value when `ECCCNTR` is nonzero, which depends on old raw NAND callback expectations. Platform data must provide correct OOB layout and bad-block pattern. The driver uses manual `ioremap()`/`kfree()` rather than devm cleanup.

Test signals: successful platform probe, chip readiness transitions through `FLRYBY`, correct partition table, successful 256-byte ECC calculation/correction, stable bad-block detection with platform pattern, and clean unregister/remove without mapped IO leaks.
