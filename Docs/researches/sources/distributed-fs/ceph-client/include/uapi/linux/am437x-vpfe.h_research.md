<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/am437x-vpfe.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/am437x-vpfe.h

## Purpose
Defines private V4L2 configuration ABI for the TI AM437x VPFE CCDC raw capture block.

## Important APIs, Types, And Functions
Exports enums for CCDC data size, black-clamp sample length/line count, and A-law gamma width. Structures include `vpfe_ccdc_a_law`, `vpfe_ccdc_black_clamp`, `vpfe_ccdc_black_compensation`, and `vpfe_ccdc_config_params_raw`. `VIDIOC_AM437X_CCDC_CFG` is a private `_IOW` V4L2 ioctl.

## Control Flow
Capture applications configure raw-mode CCDC parameters through the private ioctl, then use normal V4L2 buffer/streaming operations for capture. Optional A-law, black clamp, and black compensation settings are interpreted by the driver.

## State And Persistence
Settings are live device configuration for the VPFE hardware and persist only until changed, stream stopped, or device reset.

## Dependencies And Integration Points
Depends on `<linux/videodev2.h>`. Integrates with V4L2 device nodes, TI VPFE/CCDC driver internals, sensor pipelines, and raw Bayer capture applications.

## Risks And Edge Cases
The ioctl is explicitly experimental. Enum ranges, unsigned/char field limits, disabled black-clamp interpretation, and hardware register constraints must be validated by the driver.

## Test Signals
V4L2 compliance plus raw capture tests with each data width, A-law enable/disable, clamp enabled/disabled, invalid enum rejection, and image black-level verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/am437x-vpfe.h -->
