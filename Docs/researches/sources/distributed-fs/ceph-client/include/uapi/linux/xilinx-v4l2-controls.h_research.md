<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xilinx-v4l2-controls.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/xilinx-v4l2-controls.h

Purpose: defines private V4L2 control IDs for Xilinx video IP, especially the test pattern generator.

Important APIs and types: `V4L2_CID_XILINX_OFFSET` and `V4L2_CID_XILINX_BASE` allocate a private control range. `V4L2_CID_XILINX_TPG` and child controls configure crosshairs, moving box, color mask, stuck pixel, noise, motion, motion speed, crosshair row/column, zplate starts/speeds, box size/color, stuck-pixel threshold, and noise gain.

Control flow, state, and persistence: userspace uses V4L2 control ioctls to configure Xilinx video IP parameters; values are applied to driver/device registers and persist while the video pipeline is active.

Dependencies and integration points: depends on generic V4L2 controls and integrates with Xilinx media drivers, pipelines, and test-pattern userspace.

Risks and test signals: risks include control ID collisions, range/default mismatch, and hardware register mapping errors. Test control enumeration, set/get for every TPG control, streaming with changing patterns, and media pipeline reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xilinx-v4l2-controls.h -->
