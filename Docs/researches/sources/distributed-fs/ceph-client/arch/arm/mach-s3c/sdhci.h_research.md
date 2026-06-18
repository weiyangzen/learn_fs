<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sdhci.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sdhci.h

### Purpose
Declares Samsung SDHCI platform-data setters and S3C64xx default GPIO/platform setup helpers.

### Important APIs, Types, And Functions
Exports `s3c_sdhci[0-3]_set_platdata()`, `s3c64xx_setup_sdhci[0-2]_cfg_gpio()`, default setup helpers for S3C6400/S3C6410, and `s3c_sdhci_setname()`.

### Control Flow
CPU init sets default SDHCI data; board init can override host capabilities, card-detect type, and GPIO config through setters. SDHCI driver consumes platform data at probe.

### State, Persistence, And Dependencies
Copied platform data persists on platform devices. Depends on `linux/platform_data/mmc-sdhci-s3c.h` and board/SoC GPIO setup functions.

### Integration Points
`s3c6410.c` applies defaults, `mach-crag6410.c` overrides hosts 0 and 2, and `setup-sdhci-gpio-s3c64xx.c` implements GPIO muxing.

### Risks
Card-detect, bus width, and pinmux must match hardware. Wrong device names break driver matching.

### Test Signals
MMC enumeration, bus-width negotiation, card-detect behavior, and suspend/resume with `MMC_CAP_POWER_OFF_CARD` validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sdhci.h -->
