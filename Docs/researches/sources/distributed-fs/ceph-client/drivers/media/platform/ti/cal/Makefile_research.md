# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/Makefile

## Purpose
Builds the TI CAL driver composite object.

## Important APIs, Types, And Functions
`obj-$(CONFIG_VIDEO_TI_CAL) += ti-cal.o` emits the driver when enabled. `ti-cal-y := cal.o cal-camerarx.o cal-video.o` combines the core CAL device, CameraRx subdevice/PHY code, and video-node code.

## Control Flow
No runtime flow. Kbuild composes the CAL module from three source files.

## State And Persistence
No state beyond kernel build outputs.

## Dependencies And Integration Points
Connects the top-level TI Kconfig `VIDEO_TI_CAL` to the CAL implementation units.

## Risks
The CameraRx file is always part of the CAL object, so changes there affect all CAL builds. Missing one object would break either core, subdev, or video-node functionality.

## Test Signals
Build with `CONFIG_VIDEO_TI_CAL=m` and `=y` and confirm `ti-cal` includes `cal-camerarx.o`.
