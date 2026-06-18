# sources/distributed-fs/ceph-client/fs/notify/inotify/Kconfig

## Purpose

This Kconfig entry exposes userspace inotify support as `CONFIG_INOTIFY_USER`. Enabling it selects the generic fsnotify infrastructure and compiles the inotify syscall/file-descriptor implementation.

## Important APIs, Types, and Functions

The relevant symbol is `INOTIFY_USER`, a boolean option defaulting to `y` and selecting `FSNOTIFY`. The help text documents inotify as a single-fd, pollable event interface for files and directories and points to `Documentation/filesystems/inotify.rst`.

## Control Flow

There is no runtime control flow. Kconfig resolution ensures `FSNOTIFY` is enabled whenever inotify userspace support is selected.

## State and Persistence Behavior

The file owns no runtime state. It controls whether inotify syscalls, caches, sysctls, and file operations are built into the kernel.

## Dependencies and Integration Points

It integrates with the fsnotify core by selecting `FSNOTIFY`, and with the inotify Makefile by controlling `obj-$(CONFIG_INOTIFY_USER)`.

## Risks and Edge Cases

Disabling this symbol removes userspace inotify support even if fsnotify remains available to other backends. Default `y` preserves long-standing userspace expectations.

## Test Signals

Configuration tests should verify that enabling the option builds `inotify_fsnotify.o` and `inotify_user.o`, and disabling it removes inotify syscalls/fdinfo hooks while fanotify or other fsnotify users can still build.
