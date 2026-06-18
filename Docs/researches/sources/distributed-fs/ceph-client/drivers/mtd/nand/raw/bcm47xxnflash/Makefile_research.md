# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/Makefile

Purpose: kbuild file for the BCM47xx BCMA NAND flash driver.

Important APIs/types/functions: `bcm47xxnflash-y` aggregates `main.o` and `ops_bcm4706.o`; `obj-$(CONFIG_MTD_NAND_BCM47XXNFLASH)` links the composite `bcm47xxnflash.o`.

Control flow: build-time only. It ensures the platform driver and BCM4706 operation implementation are linked together when the Kconfig symbol is enabled.

State and persistence: no runtime state. Build state is controlled by `CONFIG_MTD_NAND_BCM47XXNFLASH`.

Dependencies/integration: integrates with kernel MTD NAND kbuild and the local source files.

Risks/test signals: future chip operation files must be added explicitly. Test by building the option as module and built-in and verifying `bcm47xxnflash_ops_bcm4706_init` resolves.
