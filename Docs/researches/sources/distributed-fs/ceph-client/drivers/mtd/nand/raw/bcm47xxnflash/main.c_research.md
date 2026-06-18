# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/main.c

Purpose: BCMA platform driver entry point for the older BCM47xx NAND path. It allocates state, selects BCM4706 operations, registers MTD with BCM47xx partition probing, and cleans up on remove.

Important APIs/types/functions: platform driver name is `bcma_nflash`. `bcm47xxnflash_probe` consumes `struct bcma_nflash` platform data, obtains containing `bcma_drv_cc`, calls `bcm47xxnflash_ops_bcm4706_init`, and registers MTD with probe type `bcm47xxpart`. `bcm47xxnflash_remove` unregisters MTD and calls `nand_cleanup`.

Control flow: probe allocates `struct bcm47xxnflash`, binds it as NAND controller data, sets MTD parent, accepts only `BCMA_CHIP_ID_BCM4706`, runs initializer/scan, stores driver data, then parses/registers partitions.

State and persistence: devm-managed private state plus NAND/MTD registration. Remove tears down MTD/NAND; memory is device-managed.

Dependencies/integration: BCMA ChipCommon platform data, raw NAND core, `bcm47xxpart`, and the BCM4706 operation file. This path rejects chips handled by generic brcmnand BCMA glue.

Risks/test signals: missing platform data, unsupported chips, partition parser expectations, and cleanup after scan failures. Test supported/unsupported probe, partition discovery, read/write/erase, and remove.
