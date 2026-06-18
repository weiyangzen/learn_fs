<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x.h -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x.h

Purpose: common private header for Silicon Labs Si470x FM radio receiver drivers. It centralizes register numbers and bit masks, the shared `struct si470x_device`, firmware/frequency constants, and common function declarations used by the USB and I2C Si470x implementations.

Important APIs and types: `struct si470x_device` embeds `v4l2_device`, `video_device`, a V4L2 control handler, cached 16-bit register image, RDS circular buffer state, completion and lock primitives, and transport-specific fields under `CONFIG_USB_SI470X` or `CONFIG_I2C_SI470X`. Export-facing declarations are `si470x_viddev_template`, `si470x_ctrl_ops`, `si470x_disconnect_check`, `si470x_set_freq`, `si470x_start`, and `si470x_stop`. Register macros cover `DEVICEID`, `POWERCFG`, `CHANNEL`, `SYSCONFIG*`, `STATUSRSSI`, `READCHAN`, and RDS blocks.

Control flow: this file has no executable code, but it defines the shared state and register contract that source-specific drivers use when starting/stopping the chip, tuning, reading RDS data, and exposing V4L2 radio ioctls. Transport callbacks in `struct si470x_device` abstract register get/set and file-operation overrides.

State and persistence: state is volatile kernel driver state. The `registers[]` array caches hardware register values; the RDS buffer uses read/write indices plus a wait queue and mutex; completion/status flags coordinate asynchronous hardware or USB/I2C activity. Hardware configuration persists only in the Si470x chip while powered.

Dependencies and integration points: depends on Linux kernel, input, mutex, unaligned helpers, and V4L2 device/control/event/ioctl headers. Integrates with USB and I2C Si470x transport drivers through conditional members and common function prototypes. The frequency scale `FREQ_MUL` matches V4L2 low-frequency units.

Risks: the header uses `#define FREQ_MUL (1000000 / 62.5)`, which relies on floating constant conversion in preprocessor-facing C and can be surprising in integer contexts. Because transport-specific members are conditional, code using `struct si470x_device` must be built with matching Kconfig symbols. Register cache consistency depends on all writers using the common helpers.

Test signals: compile coverage for both USB and I2C Si470x builds, V4L2 capability/frequency/RDS behavior, RDS buffer wrap tests under interrupt load, and hardware tune/seek tests confirming register masks and frequency scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x.h -->
