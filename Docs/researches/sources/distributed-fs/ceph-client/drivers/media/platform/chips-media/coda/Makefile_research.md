# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/Makefile

## Purpose
This Makefile builds the Chips&Media Coda VPU codec driver from multiple implementation objects and optionally builds the i.MX VDOA helper.

## Important APIs, Types, and Functions
`coda-vpu-objs` aggregates `coda-common.o`, `coda-bit.o`, `coda-gdi.o`, `coda-h264.o`, `coda-mpeg2.o`, `coda-mpeg4.o`, and `coda-jpeg.o`. `obj-$(CONFIG_VIDEO_CODA) += coda-vpu.o` builds the linked driver. `obj-$(CONFIG_VIDEO_IMX_VDOA) += imx-vdoa.o` builds the auxiliary helper.

## Control Flow
Kbuild links the listed Coda component objects into `coda-vpu.o` when `VIDEO_CODA` is enabled, and independently includes `imx-vdoa.o` according to `VIDEO_IMX_VDOA`.

## State and Persistence
No runtime state exists here. Its persistent effect is object composition and module naming.

## Dependencies and Integration Points
The aggregate object must match the Coda source decomposition and the Kconfig symbols in the same directory.

## Risks and Edge Cases
Omitting a component object can remove codec support or shared helpers while still producing a module. Stale object names break builds. VDOA must remain separately gated because it is platform-specific.

## Test Signals
Enable `VIDEO_CODA` and verify all codec component objects link into `coda-vpu.ko`; enable `VIDEO_IMX_VDOA` and confirm `imx-vdoa.ko` or built-in object output appears.
