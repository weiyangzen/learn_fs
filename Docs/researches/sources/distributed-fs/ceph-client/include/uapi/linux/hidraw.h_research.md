<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hidraw.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hidraw.h

## Purpose
`hidraw.h` defines the raw HID character-device ABI. It lets userspace read and write reports with minimal kernel parsing and query device metadata and report descriptors.

## Important APIs, types, and functions
`struct hidraw_report_descriptor` contains descriptor size and up to `HID_MAX_DESCRIPTOR_SIZE` bytes. `struct hidraw_devinfo` contains bus type, vendor, and product IDs. Ioctls include `HIDIOCGRDESCSIZE`, `HIDIOCGRDESC`, `HIDIOCGRAWINFO`, `HIDIOCGRAWNAME`, `HIDIOCGRAWPHYS`, `HIDIOCSFEATURE`, `HIDIOCGFEATURE`, `HIDIOCGRAWUNIQ`, `HIDIOCSINPUT`, `HIDIOCGINPUT`, `HIDIOCSOUTPUT`, `HIDIOCGOUTPUT`, and `HIDIOCREVOKE`. Limits include `HIDRAW_FIRST_MINOR`, `HIDRAW_MAX_DEVICES`, and `HIDRAW_BUFFER_SIZE`.

## Control flow
Users open `/dev/hidrawN`, query descriptor size and descriptor bytes, then read input reports and write output or feature reports. For feature/input/output ioctls, the first byte of the buffer is the report number.

## State and persistence behavior
The char device has per-open buffering and access state. `HIDIOCREVOKE` can revoke further access. Report effects persist according to device firmware.

## Dependencies and integration points
It depends on `linux/hid.h` and `<linux/types.h>`. It integrates with HID core, udev permissions, USB/Bluetooth/I2C-HID devices, and userspace HID libraries.

## Risks and test signals
Risks include descriptor truncation, missing report-number byte, buffer length mismatches, concurrent access surprises, revoked fds, and device-specific report side effects. Test signals include descriptor round trips, raw report echo tests, feature get/set, disconnect/revoke behavior, minor allocation limits, and fuzzing malformed descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hidraw.h -->
