# Research: sources/distributed-fs/ceph-client/fs/notify/fanotify/Makefile

## Purpose

This Kbuild file compiles the fanotify backend and userspace interface objects when FANOTIFY is enabled.

## Important APIs, Types, and Functions

The rule is `obj-$(CONFIG_FANOTIFY) += fanotify.o fanotify_user.o`.

## Control Flow

Kbuild includes both the core backend event code and user-facing syscall/file-descriptor code under the FANOTIFY config.

## State and Persistence Behavior

The file has build-time effects only.

## Dependencies and Integration Points

It depends on the top-level notify directory descent and `CONFIG_FANOTIFY` from Kconfig.

## Risks

Core and user-interface objects must be built together because they share types, caches, and group setup. Splitting the rule incorrectly would cause link or runtime failures.

## Test Signals

Build with FANOTIFY enabled and disabled, confirming both objects are present or absent together.
