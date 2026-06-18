# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcma_nand.c

Purpose: adapts the shared brcmnand core to BCMA ChipCommon NAND blocks on chips other than BCM4706. It provides non-MMIO register access and cache-address preparation.

Important APIs/types/functions: `struct brcmnand_bcma_soc` embeds `brcmnand_soc` and stores `struct bcma_drv_cc *`. `brcmnand_bcma_read_reg`/`write_reg` translate offsets and endian-swap selected spare/devid registers. `brcmnand_bcma_prepare_data_bus` resets `BCMA_CC_NAND_CACHE_ADDR`. `brcmnand_bcma_nand_probe` wires hooks and calls `brcmnand_probe`.

Control flow: probe retrieves `struct bcma_nflash` platform data, finds its containing ChipCommon driver, rejects BCM4706 for `bcm47xxnflash`, installs custom IO/data hooks, and delegates setup to the core. The core uses a static key when SoC IO ops are present.

State and persistence: persistent state is the ChipCommon pointer and hook table. Data-bus preparation changes hardware cache address before sub-page transfers.

Dependencies/integration: BCMA, `BCMA_NFLASH`, ChipCommon registers, and brcmnand exported APIs. Platform driver name is `bcma_brcmnand`.

Risks/test signals: offset translation, endian swapping, accidental BCM4706 binding, and cache address reset. Test BCMA non-4706 probe, READID/parameter pages, OOB endianness, flash-cache data, and MTD I/O through the core.
