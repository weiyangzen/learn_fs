# Research: sources/distributed-fs/ceph-client/fs/notify/dnotify/Makefile

## Purpose

This Kbuild file compiles the dnotify backend object when `CONFIG_DNOTIFY` is enabled.

## Important APIs, Types, and Functions

The only rule is `obj-$(CONFIG_DNOTIFY) += dnotify.o`.

## Control Flow

Kbuild includes `dnotify.o` conditionally based on the Kconfig symbol.

## State and Persistence Behavior

The file has build-time effects only.

## Dependencies and Integration Points

It depends on `fs/notify/dnotify/Kconfig` and the top-level notify Makefile's directory descent.

## Risks

The rule is simple; risk is mainly accidental symbol rename or loss of conditional build coverage.

## Test Signals

Build with `CONFIG_DNOTIFY=y` and `n`, verifying object inclusion and absence respectively.
