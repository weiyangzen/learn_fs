# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/Kconfig

## Purpose
Adds the Kconfig option for the Imagination E5010 JPEG encoder V4L2 mem2mem driver.

## Important APIs, Types, and Functions
Defines `CONFIG_VIDEO_E5010_JPEG_ENC` as a tristate with prompt "Imagination E5010 JPEG Encoder Driver". It depends on `VIDEO_DEV` and `ARCH_K3 || COMPILE_TEST`, and selects `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, and `V4L2_JPEG_HELPER`.

## Control Flow
No runtime flow. Build-system selection controls whether the E5010 module is compiled.

## State and Persistence
No runtime state. The selected config persists in kernel `.config`.

## Dependencies and Integration Points
Integrates the Imagination platform directory into the media Kconfig tree and ensures vb2/mem2mem/JPEG helper dependencies are enabled.

## Risks
Missing dependency selections cause link failures. The hardware dependency is K3-oriented but compile-testable. The help text states module name `e5010_jpeg_enc`, matching the Makefile object.

## Test Signals
`make menuconfig` visibility, `allyesconfig`/`allmodconfig`/`COMPILE_TEST` builds, and module load on K3 device-tree systems.
