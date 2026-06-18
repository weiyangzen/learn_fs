# sources/distributed-fs/ceph-client/include/uapi/linux/matroxfb.h

Purpose: defines Matrox framebuffer userspace controls for output mode and output-to-framebuffer connection management.

Important APIs and types: `struct matroxioc_output_mode` carries an output selector and mode selector. Output IDs include primary, secondary, and DFP; modes include PAL, NTSC, and monitor. Ioctls include `MATROXFB_SET_OUTPUT_MODE`, `MATROXFB_GET_OUTPUT_MODE`, `MATROXFB_SET_OUTPUT_CONNECTION`, `MATROXFB_GET_OUTPUT_CONNECTION`, `MATROXFB_GET_AVAILABLE_OUTPUTS`, and `MATROXFB_GET_ALL_OUTPUTS`. Connection bitmasks map each output to a bit. `enum matroxfb_ctrl_id` reserves V4L2 private controls for test output and deflicker.

Control flow: userspace queries available/all outputs, reads or sets output connections, and configures TV/monitor output modes for Matrox framebuffer devices.

State and persistence: state is per framebuffer/device: output routing and mode settings. Persistence depends on driver/hardware/userspace reconfiguration, not this header.

Dependencies and integration points: depends on `asm/ioctl.h`, `linux/types.h`, `linux/videodev2.h`, and `linux/fb.h`; integrates fbdev, V4L2 controls, and Matrox-specific output hardware.

Risks and test signals: risks include ioctl argument type using `size_t`, 32/64-bit compatibility, obsolete fbdev/V4L2 private-control assumptions, and invalid output bitmasks. Test ioctl compat, mode set/get round trip, unavailable outputs, DFP/TV routing, and legacy userspace tools.
