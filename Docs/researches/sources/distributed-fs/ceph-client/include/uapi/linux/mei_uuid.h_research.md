# sources/distributed-fs/ceph-client/include/uapi/linux/mei_uuid.h

## Purpose
Provides the little-endian UUID representation and construction macros used by MEI userspace ABI.

## Important APIs, Types, And Functions
Exports `uuid_le`, `UUID_LE(...)`, and `NULL_UUID_LE`. `UUID_LE` expands UUID fields into a 16-byte little-endian layout for the first three fields followed by raw trailing bytes.

## Control Flow
There is no runtime control flow. Callers use macros to initialize `uuid_le` constants passed into MEI connect ioctls.

## State, Persistence, And Dependencies
No persistent state. Depends on `linux/types.h` for `__u8`.

## Integration Points
Included by `linux/mei.h` and any userspace client that identifies ME firmware services.

## Risks
The macro is layout-specific; confusing canonical string order with in-memory little-endian order can connect to the wrong firmware client. It is a legacy MEI-specific UUID type, not a generic libuuid replacement.

## Test Signals
Validate byte layout for known MEI UUIDs, `NULL_UUID_LE` all-zero initialization, and compiler acceptance in constant initializers.
