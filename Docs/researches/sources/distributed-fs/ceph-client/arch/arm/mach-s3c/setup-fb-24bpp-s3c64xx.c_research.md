<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-fb-24bpp-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-fb-24bpp-s3c64xx.c

### Purpose
Configures S3C64xx GPIO pins for a 24-bit framebuffer/LCD interface.

### Important APIs, Types, And Functions
`s3c64xx_fb_gpio_setup_24bpp()` applies special-function modes to the relevant LCD data/control GPIO ranges.

### Control Flow
Framebuffer platform data references this setup function; the framebuffer driver calls it during probe or initialization.

### State, Persistence, And Dependencies
State is GPIO mux/pull configuration in hardware. Depends on S3C64xx GPIO numbering and `s3c_gpio_cfgrange_nopull()`.

### Integration Points
Used by Cragganmore LCD platform data.

### Risks
Incorrect pin ranges produce blank display, color lane swaps, or bus contention.

### Test Signals
Framebuffer probe, visible 24 bpp output, and GPIO mux inspection validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-fb-24bpp-s3c64xx.c -->
