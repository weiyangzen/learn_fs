# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_nflash.c

Purpose: this file prepares BCMA ChipCommon NAND flash support and platform data for Broadcom NAND drivers.

Important APIs, types, and functions: it defines global platform device `bcma_nflash_dev`, alternate driver name `bcma_brcmnand`, partition probe list `bcm47xxpart`, and init function `bcma_nflash_init`.

Control flow: init first rejects unsupported chip/revision combinations, then verifies `BCMA_CC_CAP_NFLASH`. It marks NAND present, detects a booting NAND configuration for ChipCommon revision 38 with `BCMA_CC_CHIPST_5357_NAND_BOOT`, reads chip-select information from `BCMA_CC_NAND_CS_NAND_SELECT`, fills `brcmnand_info` with chip select, partition probe, ECC step size, and ECC strength, and renames the platform device to the alternate name. Finally it stores `&cc->nflash` as platform data without registering the platform device yet.

State and persistence: NAND state persists in `cc->nflash` and the global `bcma_nflash_dev.dev.platform_data`. The platform device object is static and later registration is expected elsewhere.

Dependencies and integration points: it integrates with `linux/platform_data/brcmnand.h`, Broadcom partition probing, BCMA ChipCommon status/capability registers, and later platform-device registration from BCMA host code.

Risks: static global platform device state can only represent one active BCMA NAND instance cleanly. Unsupported chips return errors; callers must not assume NAND exists from flash capability alone. Chip-select calculation uses `ffs(reg) - 1`, so a zero register would produce `-1` if reached.

Test signals: boot logs and MTD/NAND device registration are primary signals. Tests should cover unsupported board rejection, missing capability rejection, and correct platform data for NAND-booting rev-38 devices.
