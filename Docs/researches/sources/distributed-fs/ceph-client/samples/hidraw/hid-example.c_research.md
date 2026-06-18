# sources/distributed-fs/ceph-client/samples/hidraw/hid-example.c

Purpose: user-space hidraw API example that queries descriptors/device info and performs feature/input/output report operations.

Important APIs/functions: `open` on `/dev/hidraw0` or argv path, ioctls `HIDIOCGRDESCSIZE`, `HIDIOCGRDESC`, `HIDIOCGRAWNAME`, `HIDIOCGRAWPHYS`, `HIDIOCGRAWINFO`, `HIDIOCSFEATURE`, `HIDIOCGFEATURE`, plus `read` and `write`.

Control flow: opens device nonblocking, prints report descriptor, name, physical path, bus/vendor/product info, sends and reads feature report 9, writes report 1, attempts a nonblocking read, and closes.

State and persistence: local buffers only; feature/output reports may affect the device.

Dependencies and integration: integrates with `/dev/hidraw*` and Linux input bus constants.

Risks: hard-coded report IDs and payloads are not safe for arbitrary HID devices. Nonblocking read may fail with `EAGAIN`. Fallback ioctl macros support older headers.

Test signals: run against a known hidraw device and compare descriptor/info output with `udevadm` or sysfs; verify expected feature report behavior for that device.
