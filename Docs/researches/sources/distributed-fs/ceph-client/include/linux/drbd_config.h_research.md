# sources/distributed-fs/ceph-client/include/linux/drbd_config.h

## Purpose
This header declares DRBD compile-time version information and the build tag accessor.

## Important APIs, types, and functions
It declares `const char *drbd_buildtag(void)` and defines `REL_VERSION` as `8.4.11`, `PRO_VERSION_MIN` as `86`, and `PRO_VERSION_MAX` as `101`.

## Control flow, state, and persistence
The header has no runtime state. Version constants shape protocol negotiation and user-visible module identification.

## Dependencies and integration points
It is consumed by DRBD kernel code and tools that need release/protocol compatibility boundaries.

## Risks and test signals
Risks are stale protocol version bounds or release strings that do not match the implementation. Tests should verify version reporting, protocol negotiation against min/max, and build tag availability.
