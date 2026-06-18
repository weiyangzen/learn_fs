<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-sdhci-gpio-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-sdhci-gpio-s3c64xx.c

### Purpose
Configures S3C64xx GPIO pins for SDHCI hosts 0, 1, and 2.

### Important APIs, Types, And Functions
`s3c64xx_setup_sdhci0_cfg_gpio()`, `s3c64xx_setup_sdhci1_cfg_gpio()`, and `s3c64xx_setup_sdhci2_cfg_gpio()` configure command/clock/data pins according to the requested bus width.

### Control Flow
SDHCI platform data references these callbacks. The SDHCI driver calls the host-specific function before enabling a host.

### State, Persistence, And Dependencies
State is GPIO mux and pull configuration. Depends on S3C64xx GPIO bank layout and SDHCI platform data.

### Integration Points
S3C6410 defaults and Cragganmore overrides use these callbacks.

### Risks
Width-dependent ranges must be correct for 1-bit/4-bit/8-bit cases. Misconfigured pulls can break card detect or signal integrity.

### Test Signals
Card enumeration, data transfer at configured width, and host-specific GPIO inspection validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-sdhci-gpio-s3c64xx.c -->
