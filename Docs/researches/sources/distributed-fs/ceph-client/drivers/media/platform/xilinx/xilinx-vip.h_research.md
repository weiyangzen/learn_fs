# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.h

Purpose: common Xilinx Video IP interface header. It defines width/height limits, standard sink/source pad IDs, common control/timing register offsets and bit masks, `struct xvip_device`, `struct xvip_video_format`, exported helper prototypes, and inline MMIO/core-control helpers.

Important APIs: `xvip_read/write/clr/set`, `xvip_reset/start/stop/suspend/resume`, `xvip_set_frame_size/get_frame_size`, `xvip_enable_reg_update/disable_reg_update`, and `xvip_print_version`. It also declares format lookup, OF parsing, format-size, enum, and resource-management helpers implemented in `xilinx-vip.c`.

Control flow/state: inline helpers directly manipulate memory-mapped registers. `xvip_suspend()` saves the control register and disables SW enable; `xvip_resume()` restores it with enable set. Frame-size helpers encode/decode width and height into `XVIP_ACTIVE_SIZE`.

Dependencies and integration: used by all Xilinx media drivers in this subset. Depends on Linux I/O accessors, clocks, V4L2 subdev types, and Xilinx DT binding format codes.

Risks: register masks encode 11-bit active size in this header while some blocks use wider VTC limits; callers must use block-specific limits where needed. Direct read-modify-write helpers are not internally locked. Test signals include static compile coverage, register-level hardware tests for reset/start/stop, and PM tests that validate saved control restoration.
