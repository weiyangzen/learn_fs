# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/Kconfig

## Purpose
Defines the AM437x VPFE video capture driver configuration symbol.

## Important APIs, Types, And Functions
`VIDEO_AM437X_VPFE` is a tristate for the TI AM437x Video Processing Front End capture driver. It depends on V4L2 platform drivers, video device support, and `SOC_AM43XX` or compile-test. It selects media controller, V4L2 subdev API, vb2 DMA-contig, and V4L2 fwnode helpers.

## Control Flow
When enabled, the AM437x Makefile builds `am437x-vpfe.o`. Runtime behavior is in `am437x-vpfe.c`.

## State And Persistence
Only build configuration state is persisted.

## Dependencies And Integration Points
Integrates the driver with AM43xx SoC support, V4L2 media graph/subdev APIs, fwnode endpoint parsing, and contiguous DMA buffers.

## Risks
Compile-test builds can expose missing generic dependencies. Runtime use still requires an AM437x-compatible device tree endpoint and a remote camera/decoder subdevice.

## Test Signals
Build as module and builtin, plus boot/probe tests on AM437x hardware or compile-test configurations.
