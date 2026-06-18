<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.c

## Purpose
This helper exercises GPIO character-device file descriptors after the backing `gpio-sim` chip is destroyed, checking for safe `ENODEV`/poll behavior rather than use-after-free.

## Important APIs, Types, And Functions
Important helpers are `_create_chip()`, `create_chip()`, `remove_chip()`, `_create_bank()`, `create_bank()`, `remove_bank()`, `_enable_chip()`, `enable_chip()`, `disable_chip()`, `open_chip()`, `close_chip()`, `test_poll()`, `test_read()`, `test_ioctl()`, and `main()`. It uses GPIO v1 handle/event ioctls and v2 line request ioctls.

## Control Flow
`main()` validates target object (`chip`, `handle`, `event`, or `req`) and operation (`poll`, `read`, `ioctl`), creates a one-bank simulated chip, obtains the chosen fd, destroys the chip through configfs, then performs the requested operation on the dangling fd. Success is no unexpected readiness for poll or `ENODEV` for read/ioctl.

## State And Persistence
It creates/removes configfs gpio-sim directories, opens `/dev/gpiochip*`, and holds chip/line/event/request fds across device teardown.

## Dependencies And Integration Points
It depends on `gpio-sim`, configfs, GPIO cdev v1/v2 uAPIs, and kernel cleanup paths for removed GPIO devices.

## Risks
Path buffers are fixed-size and assume short chip/bank names. The ioctl test uses command `0`, expecting generic `ENODEV` after removal; behavior changes in fd validation can affect the result.

## Test Signals
Pass is exit `0` for each matrix entry, with reads/ioctls returning `ENODEV` and poll reporting no events except allowed `POLLHUP|POLLERR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.c -->
