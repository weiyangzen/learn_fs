# sources/distributed-fs/ceph-client/drivers/ufs/host/Kconfig

## Purpose
Defines kernel configuration switches for UFS host controller transport glue and vendor-specific platform drivers. It decides which UFS host modules are buildable and records architecture, bus, PM, reset, and crypto feature dependencies.

## Important symbols and APIs
Key symbols in this subset are `SCSI_UFS_DWC_TC_PCI`, `SCSI_UFS_DWC_TC_PLATFORM`, `SCSI_UFS_CDNS_PLATFORM`, `SCSI_UFS_TI_J721E`, `SCSI_UFS_EXYNOS`, `SCSI_UFS_VARIABLE_SG_ENTRY_SIZE`, `SCSI_UFS_HISI`, `SCSI_UFS_MEDIATEK`, and `SCSI_UFS_AMD_VERSAL2`. Base dependencies are `SCSI_UFSHCD_PCI` for PCI controllers and `SCSI_UFSHCD_PLATFORM` for MMIO/platform controllers.

## Control flow and state
There is no runtime control flow or persistence. The file contributes build-time state through Kconfig dependency resolution. Selecting a vendor option enables the corresponding Makefile object and therefore registers platform or PCI drivers at module load.

## Dependencies and integration points
The symbols integrate with `drivers/ufs/host/Makefile`, the Linux UFSHCD core, device tree match tables, and arch configuration. Some symbols intentionally restrict to real SoC families unless `COMPILE_TEST` is allowed. MediaTek selects `PHY_MTK_UFS` and `RESET_TI_SYSCON`; Qualcomm selects inline crypto engine support when UFS crypto is enabled.

## Risks and test signals
Main risks are missing dependency declarations that allow unusable compile combinations, or too-strict arch dependencies that block compile testing. Test signals are `allyesconfig`, `allmodconfig`, and targeted builds for each selected driver, especially combinations with `SCSI_UFS_CRYPTO`, `COMPILE_TEST`, and architecture-specific reset or PHY providers.
