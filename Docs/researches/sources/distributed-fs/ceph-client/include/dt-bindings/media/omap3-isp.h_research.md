<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/omap3-isp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/media/omap3-isp.h

## Purpose
This header defines OMAP3 ISP PHY type constants for camera/media device-tree bindings.

## Important APIs, types, and functions
It exports `OMAP3ISP_PHY_TYPE_COMPLEX_IO` and `OMAP3ISP_PHY_TYPE_CSIPHY`.

## Control flow
OMAP3 camera endpoint or ISP nodes use these macros to describe the physical receiver type. The OMAP3 ISP driver reads the numeric property and configures the correct PHY path.

## State and persistence
The header has no state. The selected PHY type persists in board DTBs and affects runtime ISP configuration.

## Dependencies and integration points
It integrates with OMAP3 ISP media driver, V4L2 async endpoint parsing, CSI/CCP2 receiver configuration, and camera sensor graph bindings.

## Risks and test signals
Risks include selecting the wrong PHY type for the board wiring, leading to no camera stream or bad lane setup. Test signals include `dtbs_check`, media graph enumeration, sensor stream-on, and captured frame validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/omap3-isp.h -->
