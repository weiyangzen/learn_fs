# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/Makefile

## Purpose
Builds the TPO TJ032MD01BW MMP panel driver.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_MMP_PANEL_TPOHVGA) += tpo_tj032md01bw.o`.

## Control Flow
Kbuild compiles the panel driver when the Kconfig option is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects the MMP SPI panel source into the kernel build.

## Risks
None beyond config dependency correctness.

## Test Signals
Build with `CONFIG_MMP_PANEL_TPOHVGA=y` and verify object inclusion.
