# sources/distributed-fs/ceph-client/include/linux/platform_data/brcmnand.h

Purpose: defines platform data for Broadcom NAND controller/chip setup.

Important APIs and types: `struct brcmnand_platform_data` contains `chip_select`, partition parser names `part_probe_types`, and ECC geometry fields `ecc_stepsize` and `ecc_strength`.

Control flow: platform code passes this struct to the NAND driver; probe selects the chip, chooses partition parsers, and configures ECC layout/strength before registering MTD devices.

State and persistence: static flash topology and ECC policy. Persistent data is on NAND flash, but this header only describes how the driver should access and protect it.

Dependencies and integration points: integrates Broadcom platform devices, raw NAND/MTD registration, partition parsing, and ECC configuration.

Risks and test signals: risks include wrong chip-select accessing the wrong device, ECC settings incompatible with existing flash data, and partition parser mismatch. Test NAND probe/read/write, ECC correction stats, bad-block handling, partition discovery, and boot compatibility with existing images.
