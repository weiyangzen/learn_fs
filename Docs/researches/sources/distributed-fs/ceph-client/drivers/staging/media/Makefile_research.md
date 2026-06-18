# sources/distributed-fs/ceph-client/drivers/staging/media/Makefile

## Purpose
Routes selected staging media Kconfig symbols to their subdirectories.

## Important Entries and Integration
It descends into deprecated atmel, atomisp, imx, max96712, meson/vdec, sunxi, tegra-video, ipu3, ipu7, and av7110 based on their config symbols. For this work item, `CONFIG_INTEL_ATOMISP` builds `atomisp/`.

## Risks and Test Signals
Risks are stale symbol/path mappings and deprecated directory gating. Build tests with selected media symbols should ensure only intended subdirectories are visited.
