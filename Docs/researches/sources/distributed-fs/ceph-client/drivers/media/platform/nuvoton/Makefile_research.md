# sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/Makefile

## Purpose
This Makefile connects the Nuvoton NPCM VCD/ECE Kconfig symbol to its driver object.

## Important APIs, Types, and Functions
`obj-$(CONFIG_VIDEO_NPCM_VCD_ECE) += npcm-video.o` is the only build rule.

## Control Flow
Kbuild compiles and links `npcm-video.o` when `VIDEO_NPCM_VCD_ECE` is enabled. No multi-object module composition occurs.

## State and Persistence
This file has build-time effect only and no runtime state.

## Dependencies and Integration Points
It integrates with `drivers/media/platform/nuvoton/Kconfig` and the kernel media platform build.

## Risks and Edge Cases
The direct one-object mapping means any future split of register, V4L2, or ECE logic would require Makefile updates or unresolved symbols.

## Test Signals
Confirm `npcm-video.ko` is produced for module builds and no object is built when the Kconfig option is disabled.
