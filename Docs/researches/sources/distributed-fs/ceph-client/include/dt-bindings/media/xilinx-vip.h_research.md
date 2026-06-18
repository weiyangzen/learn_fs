<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/xilinx-vip.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/media/xilinx-vip.h

## Purpose
This header defines Xilinx Video IP AXI4-Stream video format codes for device-tree media bindings.

## Important APIs, types, and functions
It exports `XVIP_VF_*` format constants from `XVIP_VF_YUV_422` through `XVIP_VF_CUSTOM4`, including RGB/RGBA, YUV/YUVA/YUVD variants, mono sensor, and custom formats. `XVIP_VF_RBG` is spelled as present in the binding.

## Control flow
Xilinx VIP DTS nodes use these constants to describe stream formats. The Xilinx video pipeline drivers parse the numeric value and configure format negotiation or hardware register programming.

## State and persistence
No state exists in the header. Format selections persist in DTBs and affect runtime media pipeline configuration.

## Dependencies and integration points
It integrates with Xilinx V4L2/video IP drivers, AXI4-Stream video components, media graph endpoint configuration, and format negotiation.

## Risks and test signals
Risks include format-code mismatch with Xilinx IP documentation, the `RBG` spelling causing user confusion, and selecting custom formats without driver support. Test signals include `dtbs_check`, media pipeline enumeration, format negotiation, stream-on tests, and pixel format validation on captured or generated frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/xilinx-vip.h -->
