<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.sh

## Purpose
This wrapper runs the GPIO cdev UAF helper across chip, line handle, line event, and v2 line request file descriptor operations.

## Important APIs, Types, And Functions
It defines `fail()` and `skip()`, loads `gpio-sim`, ensures configfs is mounted, and invokes `gpio-cdev-uaf` for chip poll/read/ioctl, handle ioctl, event read/poll/ioctl, and request read/poll/ioctl.

## Control Flow
The script mounts configfs if necessary, then executes numbered subtests and fails immediately on any helper nonzero exit.

## State And Persistence
It may mount configfs and loads `gpio-sim`; per-test configfs state is created by the helper.

## Dependencies And Integration Points
It depends on root, `modprobe`, `gpio-sim`, configfs, and the compiled `gpio-cdev-uaf` helper.

## Risks
No global cleanup beyond helper cleanup is provided if a helper crashes mid-device removal. Mounting configfs modifies host mount state.

## Test Signals
Expected final line is `GPIO gpio-cdev-uaf test PASS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-cdev-uaf.sh -->
