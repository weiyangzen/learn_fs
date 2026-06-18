# Research: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ioctl.h

Purpose: Internal declarations for cx23885 V4L2 advanced-debug ioctl helpers.

Important APIs/types/functions: always declares `cx23885_g_chip_info()`, and conditionally declares `cx23885_g_register()` and `cx23885_s_register()` when `CONFIG_VIDEO_ADV_DEBUG` is enabled.

Control flow: `cx23885-video.c` includes this header and wires these helpers into `v4l2_ioctl_ops` under the same config guard.

State and persistence: no state.

Dependencies/integration: protected by `_CX23885_IOCTL_H_`; relies on V4L2 debug structs and `struct file` from included kernel/V4L2 headers.

Risks: `cx23885_g_chip_info()` is declared unconditionally while its implementation is inside the C file's `CONFIG_VIDEO_ADV_DEBUG` block; current use is also config guarded, so this is compile-safe as long as callers keep the same guard.

Test signals: builds with and without `CONFIG_VIDEO_ADV_DEBUG`; debug ioctls appear only in the enabled configuration.
