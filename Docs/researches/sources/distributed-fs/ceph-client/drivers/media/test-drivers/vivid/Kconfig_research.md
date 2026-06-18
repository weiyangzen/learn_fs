# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/Kconfig

## Purpose
`vivid/Kconfig` defines build-time configuration options for the VIVID virtual video test driver.

## Important APIs, types, and functions
`VIDEO_VIVID` is a tristate driver option depending on `VIDEO_DEV`, non-SPARC architectures, and `HAS_DMA`. It selects font support, `FONT_8x16`, vmalloc and dma-contig vb2 allocators, the V4L2 TPG, and media-controller support. `VIDEO_VIVID_CEC` enables HDMI CEC emulation and selects `CEC_CORE`. `VIDEO_VIVID_OSD` enables framebuffer support for output overlay testing and selects framebuffer I/O-memory helpers. `VIDEO_VIVID_MAX_DEVS` configures the maximum number of instances, defaulting to 64.

## Control flow
These options decide which source files are built by the Makefile and which fields/code paths are compiled in VIVID core and CEC/OSD support.

## State and persistence
Kconfig state persists in the kernel configuration. It affects module shape, selected dependencies, and maximum instance array sizes.

## Dependencies and integration points
It integrates VIVID with kernel media, CEC, framebuffer, font, and vb2 subsystems. The configured symbols are consumed by the Makefile and conditional code in `vivid-core.c`, `vivid-core.h`, and `vivid-cec.h`.

## Risks and test signals
Risks include unmet selected dependency combinations, overly large `VIDEO_VIVID_MAX_DEVS`, and missing coverage for optional CEC/OSD builds. Test signals are kernel config/build combinations for base, CEC, and OSD variants.
