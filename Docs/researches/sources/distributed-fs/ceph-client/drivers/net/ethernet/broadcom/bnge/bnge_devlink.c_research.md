# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_devlink.c

Purpose: Provides devlink allocation, registration, and `devlink info` reporting for the `bnge` PCI driver.

Important APIs/functions: `bnge_devlink_alloc()` creates a devlink instance with `bnge_dev` as private data, stores PCI drvdata, records device pointers, reads PCI DSN, and caches VPD board part/serial via `bnge_vpd_read_info()`. `bnge_devlink_info_get()` reports serial, board id, ASIC id/revision, running firmware package/management API/NCSI/RoCE versions, and stored firmware versions from NVM. `bnge_dl_info_put()` routes fixed/running/stored version keys and suppresses NCSI/RoCE version strings. `bnge_devlink_register/unregister/free()` wrap devlink lifecycle.

Control flow: Core probe allocates devlink before BAR/HWRM setup, registers it after firmware registration populates version data, and unregisters/frees during removal or probe unwind. The info callback reads `bd->ver_resp`, `bd->nvm_cfg_ver`, VPD strings, and HWRM NVM data at request time.

State/persistence: `board_partno`, `board_serialno`, DSN, firmware version fields, and HWRM version response are cached in `bnge_dev`. VPD data is temporary and freed after parsing.

Dependencies/integration: Uses PCI VPD helpers, devlink API, unaligned DSN formatting, firmware HSI structures, and `bnge_hwrm_nvm_dev_info()`.

Risks/test signals: Risks include devlink info before firmware fields are initialized, VPD string termination/length assumptions, suppressed NCSI/RoCE output despite computed versions, and unhandled HWRM NVM errors before checking flags. Test `devlink dev info`, missing VPD, zero DSN, older/newer firmware version formats, stored firmware invalid flag, and probe unwind after devlink allocation.
