# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/Kconfig

Purpose: declares build-time configuration for the Adaptec AIC94xx SAS/SATA 3Gb/s PCI-X driver.

Important APIs/types/functions: `SCSI_AIC94XX` is a tristate driver symbol depending on `PCI` and `HAS_IOPORT`; it selects `SCSI_SAS_LIBSAS` and `FW_LOADER`. `AIC94XX_DEBUG` is a boolean depending on the driver and defaults to enabled.

Control flow: no runtime flow. Kconfig selects whether the driver is built in, modular, or omitted and whether debug instrumentation is compiled.

State and persistence: state is persisted in the kernel `.config`. Enabling debug changes compile flags through the Makefile and exposes extra console logging/dump code.

Dependencies and integration: integrates the driver with PCI, libsas, and firmware loading infrastructure. The selected firmware loader is required for BIOS/sequence-related firmware paths in the driver.

Risks and test signals: missing dependencies show as link/build failures in libsas or firmware APIs. Debug defaulting to `y` increases kernel log verbosity. Build tests should cover `SCSI_AIC94XX=m/y`, `PCI=n`, `HAS_IOPORT=n`, `FW_LOADER` availability, and debug on/off.
