# sources/distributed-fs/ceph-client/include/uapi/linux/usb/cdc-wdm.h

Purpose: Defines the cdc-wdm userspace ioctl for querying maximum command size.

Important APIs/types/functions: `IOCTL_WDM_MAX_COMMAND` uses `_IOR('H', 0xA0, __u16)` to return the device/driver maximum command length.

Control flow: Userspace opens a cdc-wdm device and issues the ioctl before sending management commands, sizing buffers according to the returned maximum.

State and persistence behavior: Read-only query of driver/device capability; no persistent state.

Dependencies and integration points: Includes `linux/types.h`; integrates with USB CDC WDM devices such as modems and MBIM/QMI management channels.

Risks: Callers must still handle short reads/writes and device-specific framing. A stale max value after device reset should be re-queried.

Test signals: Query on supported cdc-wdm devices, verify ioctl return size/value, handle disconnect/reset, and test invalid user pointer behavior.
