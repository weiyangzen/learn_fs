# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hidraw.c

## Purpose
`hidraw.c` is a kselftest binary for the generic hidraw userspace ABI. It creates a UHID-backed HID device and verifies raw reads, writes, revoke behavior, polling, descriptor ioctls, device info ioctls, feature/input/output report ioctls, string ioctls, and invalid ioctl command validation.

## Important APIs, types, and functions
The `FIXTURE(hidraw)` stores a `struct uhid_device` and `hidraw_fd`. `FIXTURE_SETUP` calls `setup_uhid()` with a USB VID/PID distinct from the BPF tests and opens the hidraw node. `close_hidraw()` and teardown handle cleanup. Tests use Linux hidraw ioctls such as `HIDIOCREVOKE`, `HIDIOCGRDESCSIZE`, `HIDIOCGRDESC`, `HIDIOCGRAWINFO`, `HIDIOCGFEATURE`, `HIDIOCSFEATURE`, `HIDIOCGINPUT`, `HIDIOCSINPUT`, `HIDIOCGOUTPUT`, `HIDIOCSOUTPUT`, `HIDIOCGRAWNAME`, `HIDIOCGRAWPHYS`, and `HIDIOCGRAWUNIQ`.

## Control flow
The basic event test injects a UHID input report and confirms the same bytes are readable from hidraw. Revoke tests first prove the fd works, call `HIDIOCREVOKE`, then assert reads/writes/ioctls fail with `ENODEV` and polling reports `POLLHUP`. Descriptor tests compare size and content against `rdesc`, including a deliberately small descriptor buffer. Report ioctl tests use the UHID listener's canned GET_REPORT behavior, expecting success for report id 1 and `EIO` for invalid report ids. Invalid ioctl tests handcraft bad `_IOC_TYPE`, `_IOC_NR`, and `_IOC_DIR` encodings and assert kernel error codes.

## State and persistence
The file does not persist state beyond the test process. It relies on `hid_common.h` globals for output-report synchronization and feature data. Each fixture instance owns its temporary UHID device and hidraw fd, and teardown destroys both.

## Dependencies and integration points
It integrates with `/dev/uhid`, `/dev/hidrawN`, sysfs matching from `hid_common.h`, the kernel hidraw driver, pthread condition variables, and kselftest harness macros. It is an ABI regression suite for userspace tools that depend on hidraw.

## Risks and test signals
Risks include ioctl error-code expectations changing, old kernels lacking `HIDIOCREVOKE`, nonblocking reads returning before injected data, and environment permissions. Strong signals include descriptor byte equality, exact revoke semantics, correct report forwarding through UHID, and string truncation behavior.
