# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/Kconfig

## Purpose

`rkvdec/Kconfig` declares the kernel configuration option for the Rockchip video decoder driver. It controls whether the mem2mem V4L2 decoder for Rockchip decoder IP is built into the kernel, built as a module, or omitted.

## Important APIs, Types, And Symbols

The only symbol defined is `VIDEO_ROCKCHIP_VDEC`, a tristate named "Rockchip Video Decoder driver". It depends on `ARCH_ROCKCHIP || COMPILE_TEST` and `VIDEO_DEV`. It selects `MEDIA_CONTROLLER`, `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, `V4L2_H264`, and `V4L2_VP9`.

## Control Flow

Kconfig evaluation exposes the option when the architecture or compile-test condition is satisfied and video-device support is enabled. If selected as module, the help text states that the module name is `rockchip-vdec`. The Makefile then consumes `CONFIG_VIDEO_ROCKCHIP_VDEC` to build the object list.

## State And Persistence

The file has no runtime state. The selected tristate value persists only in the kernel build configuration and determines which objects are compiled and linked.

## Dependencies And Integration Points

The option integrates with the Linux media subsystem, V4L2 mem2mem framework, videobuf2 memory allocators, codec control helpers for H.264 and VP9, and Rockchip architecture builds. It is consumed directly by the adjacent `Makefile`.

## Risks

Missing selects can cause link failures or unusable decoder registration. Over-selecting codec helpers can increase build surface. The config currently selects H.264 and VP9 helpers while the Makefile also builds HEVC-specific objects; HEVC support may rely on common media infrastructure not selected here or on symbols selected elsewhere.

## Test Signals

Useful signals include `allyesconfig`, `allmodconfig`, `COMPILE_TEST` builds on non-Rockchip architectures, module build verification for `rockchip-vdec`, and boot-time/media-device registration tests on Rockchip hardware.
