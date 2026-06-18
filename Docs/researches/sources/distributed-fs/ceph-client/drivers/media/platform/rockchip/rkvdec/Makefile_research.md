# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/Makefile

## Purpose

`rkvdec/Makefile` maps `CONFIG_VIDEO_ROCKCHIP_VDEC` to the Rockchip video decoder module object and lists the compilation units that make up the driver. It is the build-system counterpart to `rkvdec/Kconfig`.

## Important APIs, Types, And Symbols

`obj-$(CONFIG_VIDEO_ROCKCHIP_VDEC) += rockchip-vdec.o` declares the top-level module/object. `rockchip-vdec-y` aggregates `rkvdec.o`, `rkvdec-cabac.o`, `rkvdec-h264.o`, `rkvdec-h264-common.o`, `rkvdec-hevc.o`, `rkvdec-hevc-common.o`, `rkvdec-rcb.o`, `rkvdec-vdpu381-h264.o`, `rkvdec-vdpu381-hevc.o`, `rkvdec-vdpu383-h264.o`, `rkvdec-vdpu383-hevc.o`, and `rkvdec-vp9.o`.

## Control Flow

There is no runtime control flow. During kbuild evaluation, the selected config value decides whether `rockchip-vdec.o` is built. The `rockchip-vdec-y` list causes kbuild to compile and link the core decoder, CABAC table/support code, codec-specific H.264/HEVC/VP9 code, reference-compressed-buffer support, and VDPU381/VDPU383 variant implementations into one driver object.

## State And Persistence

The Makefile has no runtime state. Build state is represented by generated object files and the final built-in or module artifact.

## Dependencies And Integration Points

It integrates with the Linux kbuild composite-object convention, the adjacent Kconfig symbol, and all source files in the `rkvdec` directory. The object names imply integration across a common decoder core, codec common layers, per-codec operations, and hardware-generation-specific backends.

## Risks

Adding or removing source files without updating this list can create unresolved symbols or dead code. Codec support is built as one composite object rather than independently toggled, so compile failures in any codec or hardware variant can break the whole driver. The object list must stay in dependency order where link ordering matters for built-in initialization or weak/common symbol resolution.

## Test Signals

Useful signals include incremental builds after touching any listed source file, module builds with `CONFIG_VIDEO_ROCKCHIP_VDEC=m`, built-in builds with `=y`, `COMPILE_TEST` builds, and link checks that cover all H.264, HEVC, VP9, VDPU381, and VDPU383 object references.
