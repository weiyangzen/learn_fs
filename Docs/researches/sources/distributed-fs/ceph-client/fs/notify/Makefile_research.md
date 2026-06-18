# Research: sources/distributed-fs/ceph-client/fs/notify/Makefile

## Purpose

This Makefile wires the common fsnotify core and notification backend subdirectories into the kernel build.

## Important APIs, Types, and Functions

`obj-$(CONFIG_FSNOTIFY)` builds `fsnotify.o`, `notification.o`, `group.o`, `mark.o`, and `fdinfo.o`. `obj-y` always descends into `dnotify/`, `inotify/`, and `fanotify/`, leaving their own Makefiles to decide whether backend objects are built.

## Control Flow

Kbuild conditionally adds common fsnotify objects when `CONFIG_FSNOTIFY=y`. Directory descent happens unconditionally for backend directories.

## State and Persistence Behavior

The file affects build artifacts only. It has no runtime state.

## Dependencies and Integration Points

It depends on Kbuild conventions and the Kconfig symbols defined in the notify tree. Backend object files depend on the common objects when their configs select `FSNOTIFY`.

## Risks

Adding a backend without selecting `FSNOTIFY` can compile backend code without the common support it expects. Removing a common object here breaks all backends.

## Test Signals

Build kernels with no notification backend, DNOTIFY only, FANOTIFY only, and combined backends; inspect built objects and link success.
