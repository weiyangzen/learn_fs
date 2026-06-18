<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-video.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-video.h

## Purpose
Defines ASPEED video capture input identifiers and private V4L2 controls for high-quality JPEG mode and quality.

## Important APIs, Types, And Functions
`enum aspeed_video_input` distinguishes VGA and graphics input. `V4L2_CID_ASPEED_HQ_MODE` and `V4L2_CID_ASPEED_HQ_JPEG_QUALITY` are controls under `V4L2_CID_USER_ASPEED_BASE`.

## Control Flow
Userspace configures ASPEED video capture through V4L2, selects input, adjusts HQ mode/quality controls, and streams frames through standard V4L2 APIs.

## State And Persistence
Control values are live device settings for the ASPEED video engine and persist only while configured by the driver/device.

## Dependencies And Integration Points
Depends on `<linux/v4l2-controls.h>`. Integrates with V4L2 control enumeration, BMC remote console capture, and ASPEED video hardware.

## Risks And Edge Cases
Control range/defaults are driver-defined; unsupported input/control combinations and JPEG quality extremes should be handled.

## Test Signals
V4L2 control query/set/get tests, capture on VGA/GFX inputs, JPEG quality visual/size validation, and invalid control value rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-video.h -->
