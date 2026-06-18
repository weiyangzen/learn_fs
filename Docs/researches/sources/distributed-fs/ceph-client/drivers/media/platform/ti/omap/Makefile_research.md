<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Makefile

## Purpose

This Makefile builds the OMAP2/3 V4L2 output driver objects and conditionally includes VRFB support.

## Important APIs, types, and functions

- `omap-vout-y += omap_vout.o omap_voutlib.o`
- `omap-vout-$(CONFIG_VIDEO_OMAP2_VOUT_VRFB) += omap_vout_vrfb.o`
- `obj-$(CONFIG_VIDEO_OMAP2_VOUT) += omap-vout.o`

## Control flow

There is no runtime control flow. The build system combines the base OMAP vout objects and optional VRFB object into `omap-vout.o` when the main Kconfig symbol is enabled.

## State and persistence behavior

No runtime state exists here. The selected object list affects build artifacts only.

## Dependencies and integration points

It depends on `VIDEO_OMAP2_VOUT` and `VIDEO_OMAP2_VOUT_VRFB` from the adjacent Kconfig and on the implementation files in the same directory.

## Risks and edge cases

If VRFB-related source references are not properly guarded, builds with `VIDEO_OMAP2_VOUT_VRFB=n` can fail at link or compile time. Object naming must stay synchronized with module aliases and source file names.

## Test signals

Compile with and without `CONFIG_VIDEO_OMAP2_VOUT_VRFB`, as module and built-in, and verify `omap_vout_vrfb.o` only appears in VRFB-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Makefile -->
