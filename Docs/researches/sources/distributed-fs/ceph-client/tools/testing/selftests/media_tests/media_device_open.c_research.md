# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_device_open.c

Purpose: opens a specified media controller device once and queries device information.

Important APIs/types/functions: parses `-d /dev/mediaX`, uses `open(O_RDWR)`, `ioctl(MEDIA_IOC_DEVICE_INFO)`, and `struct media_device_info`.

Control flow: validates an argument is present, requires root via `getuid()`, opens the media device, prints ioctl error or model/driver, and exits. The device FD is intentionally left to process teardown.

State and persistence: read-only media device query; no persistent state.

Dependencies and integration points: `/dev/mediaX`, media controller API, root, kselftest skip helper.

Risks: `media_device` is uninitialized if `-d` is omitted but argc is still high enough through unrelated args; normal usage avoids this. Exit status on ioctl failure remains success-like because it only prints.

Test signals: skip if not root; open failure exits negative; device info print is the main signal.
