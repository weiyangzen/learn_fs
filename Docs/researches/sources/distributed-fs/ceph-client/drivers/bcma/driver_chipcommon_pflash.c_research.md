# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_pflash.c

Purpose: this file prepares platform data and resources for ChipCommon-attached parallel flash on BCMA SoCs.

Important APIs, types, and functions: it defines `bcma_pflash_data` with `bcm47xxpart` partition probing, `bcma_pflash_resource` for memory-mapped flash, global platform device `bcma_pflash_dev` named `physmap-flash`, and init function `bcma_pflash_init`.

Control flow: init marks `cc->pflash.present`, reads `BCMA_CC_FLASH_CFG` to choose flash bus width 1 or 2, and sets the memory resource to `BCMA_SOC_FLASH2` through `BCMA_SOC_FLASH2 + BCMA_SOC_FLASH2_SZ`. Device registration is deferred to later BCMA code.

State and persistence: state is stored in `cc->pflash`, static `bcma_pflash_data.width`, and static resource start/end fields. Hardware state is not modified except for reading flash configuration.

Dependencies and integration points: it integrates with the MTD physmap flash driver, Broadcom partition parser, platform devices, and ChipCommon flash capability detection.

Risks: static platform data/resource objects limit clean multi-instance support. Resource end calculation appears inclusive-style but uses base plus size; if consumers expect inclusive end, this may represent one byte beyond the range depending on kernel convention in surrounding code. Width detection relies on `BCMA_CC_FLASH_CFG_DS`.

Test signals: successful registration of a `physmap-flash` platform device and MTD partitions from `bcm47xxpart` validate the path. Hardware tests should verify correct bus width and flash address range.
