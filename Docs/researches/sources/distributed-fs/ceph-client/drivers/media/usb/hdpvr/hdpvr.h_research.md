<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr.h

Purpose: private HD-PVR driver header. It centralizes product IDs, firmware versions, statuses, control request constants, runtime structures, option enums, and cross-file prototypes.

Important APIs/types/functions: `struct hdpvr_device` carries all device state shared by core/control/video/I2C code. `struct hdpvr_options` caches firmware options. `struct hdpvr_buffer` wraps one coherent bulk URB and stream-list state. `struct hdpvr_video_info` carries queried input geometry. Enums define device statuses, buffer statuses, video/audio inputs, video standard, bitrate mode, and GOP mode. Function prototypes expose deletion, hardware control, V4L2 registration, I2C registration, queue cancellation, and buffer allocation/free.

Control flow: all HD-PVR C files include this header and manipulate the same state layout. Probe fills `hdpvr_device`, control helpers program options, video code owns streaming and V4L2 registration, and I2C code uses the embedded adapter fields.

State and persistence: this header declares persistent in-memory state: locks, waitqueues, work item, buffer lists, current owner, cached options, firmware version, endpoint address/size, I2C state, and shared USB control buffer. It also documents firmware control values that persist in device hardware.

Dependencies and integration: includes USB, I2C, mutex/workqueue, V4L2 device/control, and `ir-kbd-i2c` declarations. It is the private ABI binding the four HD-PVR objects.

Risks: many fields are shared across files with locking comments rather than type-enforced access. Status values and buffer states are simple bytes, so invalid transitions can go undetected. The product ID naming order is nonmonotonic (`PRODUCT_ID4` before `PRODUCT_ID3`). Several long comment blocks document reverse-engineered USB controls; implementation must stay aligned with them.

Test signals: compile all HD-PVR objects; static checking for lock coverage on `io_mutex`, `i2c_mutex`, and `usbc_mutex`; runtime exercise of every status transition and all enums through V4L2 ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr.h -->
