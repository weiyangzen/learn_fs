# sources/distributed-fs/ceph-client/fs/notify/inotify/Makefile

## Purpose

The inotify Makefile wires the userspace inotify implementation into the kernel build when `CONFIG_INOTIFY_USER` is enabled.

## Important APIs, Types, and Functions

The only build rule is `obj-$(CONFIG_INOTIFY_USER) += inotify_fsnotify.o inotify_user.o`.

## Control Flow

There is no runtime control flow. Kbuild includes the backend event handling object and the syscall/file operation object based on the config symbol.

## State and Persistence Behavior

The file owns no runtime state and only affects compiled objects.

## Dependencies and Integration Points

It integrates with `Kconfig`'s `INOTIFY_USER` symbol and with the parent fs/notify build. Both objects are required: `inotify_fsnotify.o` supplies fsnotify ops and event allocation/freeing, while `inotify_user.o` supplies syscalls and fd operations.

## Risks and Edge Cases

Dropping either object would produce missing symbols or a half-built inotify implementation. The simple rule relies on the config symbol selecting generic fsnotify.

## Test Signals

Build `CONFIG_INOTIFY_USER=y` and confirm both objects are compiled/linked; build with it disabled and confirm neither object is included.
