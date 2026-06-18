# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/Kconfig

Purpose: defines build-time configuration for the Marvell 88SE64XX/88SE94XX SAS/SATA `mvsas` driver.

Important APIs/types/functions: `SCSI_MVSAS` is a tristate depending on `PCI && HAS_IOPORT` and selecting `SCSI_SAS_LIBSAS` plus `FW_LOADER`. `SCSI_MVSAS_DEBUG` adds debug prints and defaults to enabled when the driver is enabled. `SCSI_MVSAS_TASKLET` optionally defers interrupt work to a tasklet and defaults off.

Control flow: no runtime control flow. Kconfig determines whether the driver is absent, built-in, or modular, and whether `MV_DEBUG` and `CONFIG_SCSI_MVSAS_TASKLET` paths compile.

State and persistence: generated kernel configuration is the only state. No runtime persistence.

Dependencies and integration points: sourced from the main SCSI Kconfig. The selected libsas dependency is required by `mv_init.c` and `mv_sas.c`; firmware loader support is used by broader mvsas firmware/HBA-info code.

Risks and test signals: dependency mistakes surface as missing libsas, PCI, I/O port, or firmware-loader symbols. Build tests should cover `SCSI_MVSAS=m/y`, debug on/off, tasklet on/off, and non-PCI or `HAS_IOPORT=n` configurations.
