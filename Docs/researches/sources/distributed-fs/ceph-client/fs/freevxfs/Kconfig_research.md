# sources/distributed-fs/ceph-client/fs/freevxfs/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/Kconfig` defines the build-time configuration option for the FreeVxFS filesystem driver. The complete 27-line file was read for this report.

## Important APIs, Types, and Functions

The sole config symbol is `VXFS_FS`, a tristate option named "FreeVxFS file system support (VERITAS VxFS(TM) compatible)". It depends on `BLOCK` and selects `BUFFER_HEAD`.

## Control Flow

There is no runtime control flow. Kconfig selection enables the driver as built-in or module and ensures the buffer-head dependency is available.

## State and Persistence Behavior

The file affects kernel build configuration only. It does not own runtime state or on-disk persistence.

## Dependencies and Integration Points

It integrates with the kernel build system, block-device filesystem support, and `fs/freevxfs/Makefile`. The help text documents read-only support for VxFS versions 2, 3, and 4, with known SCO UnixWare and HP-UX image coverage.

## Risks and Edge Cases

Risks are mostly build/configuration drift: the driver uses buffer-head APIs, requires block devices, and supports only read-only mounting despite VxFS being a full filesystem format. The help text typo "VxFX" is cosmetic.

## Test Signals

Useful signals are `allyesconfig`, modular build, built-in build, dependency checks with `BLOCK=n`, module autoload via `mount -t vxfs`, and documentation/help consistency checks.
