# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec_ctrls.c

This file initializes and services V4L2 controls for Venus decoder instances. It maps standard MPEG/decoder controls to `inst->controls.dec` and exposes volatile firmware-derived profile, level, and minimum capture-buffer data.

Important functions are `vdec_ctrl_init()`, `vdec_op_s_ctrl()`, and `vdec_op_g_volatile_ctrl()`. Controls include MPEG4/H264/VP8/VP9 profile and level menus, MPEG4 deblock filter, `V4L2_CID_MIN_BUFFERS_FOR_CAPTURE`, display delay and enable controls, and conceal color.

Control flow starts in `vdec_ctrl_init()`, which creates a control handler with menu/std controls and marks profile/level/min-buffer controls volatile where firmware or current stream data can update them. `vdec_op_s_ctrl()` copies user values into decoder control state. `vdec_op_g_volatile_ctrl()` refreshes profile/level through `venus_helper_get_profile_level()` and minimum capture buffers through `venus_helper_get_bufreq(HFI_BUFFER_OUTPUT)`.

State persists in `inst->ctrl_handler` and `inst->controls.dec`: profile, level, post-loop deblock mode, display delay, display-delay enable, and conceal color. Dependencies include V4L2 controls, core/helper utilities, HFI buffer requirements, and HFI version-specific count accessors.

Risks include exposing unsupported profile/level combinations through static masks, stale volatile values before firmware has parsed stream headers, and buffer-minimum queries failing during session transitions. Test signals include V4L2 control enumeration, set/get for each control, volatile profile/level after sequence parsing, minimum capture buffers matching firmware/platform requirements, and proper handler cleanup on init error.
