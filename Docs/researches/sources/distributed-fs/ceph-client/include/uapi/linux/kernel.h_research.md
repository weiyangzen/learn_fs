# sources/distributed-fs/ceph-client/include/uapi/linux/kernel.h

## Purpose
`kernel.h` is a small umbrella UAPI header that exposes generic kernel userspace definitions by including `sysinfo` and constant-expression helpers.

## Important APIs, Types, and Functions
This header defines no direct symbols in this snapshot. It includes `<linux/sysinfo.h>` and `<linux/const.h>`.

## Control Flow
There is no control flow. Its role is include compatibility for userspace code that expects `<linux/kernel.h>` to pull in common kernel UAPI definitions.

## State and Persistence
No state is represented.

## Dependencies and Integration Points
It integrates indirectly with `sysinfo(2)` structure definitions and constant macros used by Linux UAPI headers.

## Risks and Test Signals
Tests should verify userspace inclusion, absence of kernel-only leakage, and compatibility with libc headers. Risk is low, but adding broad definitions here can create namespace conflicts.
