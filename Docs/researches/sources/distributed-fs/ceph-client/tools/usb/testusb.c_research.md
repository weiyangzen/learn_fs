# sources/distributed-fs/ceph-client/tools/usb/testusb.c

Purpose: `testusb.c` is the userspace frontend for the kernel `usbtest` driver. It discovers recognized USB test devices under usbfs, then issues `USBDEVFS_IOCTL` requests wrapping `USBTEST_REQUEST` to run kernel-side transfer test cases.

Important APIs, types, and functions: `struct usbtest_param` mirrors the ioctl payload with test number, iterations, length, variation, scatter/gather count, and duration. `struct testdev` tracks discovered devices, speed, interface number, thread, and parameters. `testdev_ifnum()` recognizes known test VID/PID pairs and FunctionFS descriptors, using `testdev_ffs_ifnum()` to scan interface descriptors. `find_testdev()` is the `ftw()` callback. `usbdev_ioctl()` wraps interface ioctls. `handle_testdev()` opens the device, queries `USBDEVFS_GET_SPEED`, runs selected test cases, and prints duration or errors.

Control flow: `main()` parses `-D`, `-a`, `-A`, `-c`, `-g`, `-l`, `-n`, `-s`, `-t`, and `-v`, discovers `/dev/bus/usb` unless an alternate tree is supplied, builds a linked list of recognized devices, then either runs a single device inline or starts one pthread per device. `-l` restarts test enumeration forever.

State and dependencies: state is in process memory plus opened usbfs device files. It depends on usbfs, kernel `usbtest` support, usbdevfs ioctls, pthreads, and known device descriptors. Risks include intentionally permissive fallback when a specific `DEVICE` is not recognized, test result errors being ignored for threaded all-device mode, descriptor parsing trusting length bytes, and requiring privileges for device ioctls. Test signals are recognized device listings, per-test timing lines, ioctl errno lines, and stress behavior when run through `hcd-tests.sh`.
