<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.h

## Purpose

This header defines the minimal Freescale TCON register contract and public API used by the DCU DRM driver.

## Important APIs, Types, And Macros

It defines `FSL_TCON_CTRL1` and `FSL_TCON_CTRL1_TCON_BYPASS` bit 29. `struct fsl_tcon` stores the TCON regmap and IPG clock. The public functions are `fsl_tcon_init()`, `fsl_tcon_free()`, `fsl_tcon_bypass_disable()`, and `fsl_tcon_bypass_enable()`.

## Control Flow

No runtime control flow exists in the header. Consumers call `fsl_tcon_init()` during DCU probe, then use bypass helpers during encoder setup/resume.

## State And Persistence

The struct stores the driver handle to the TCON register block and clock. The bypass bit is persistent hardware state until changed, reset, or power-cycled.

## Dependencies And Integration Points

It includes Linux bitops for `BIT()` and forward-relies on consumers providing `struct device`, `struct regmap`, and `struct clk` definitions. Integration is limited to FSL DCU RGB/LVDS output routing.

## Risks And Test Signals

Risks are small but hardware-facing: a wrong bypass bit prevents panel output, and missing forward declarations could break isolated include use. Test by compiling the FSL DCU driver, enabling/disabling bypass on TCON-capable hardware, and verifying display output after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.h -->
