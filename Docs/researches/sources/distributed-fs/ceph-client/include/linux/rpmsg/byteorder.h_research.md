# sources/distributed-fs/ceph-client/include/linux/rpmsg/byteorder.h

## Purpose
`rpmsg/byteorder.h` provides typed endian conversion helpers for rpmsg protocol fields.

## Important APIs, types, and functions
The header defines rpmsg-specific bitwise types `__rpmsg16`, `__rpmsg32`, and `__rpmsg64`, plus `rpmsg_is_little_endian()`, `__rpmsg16_to_cpu()`, `__cpu_to_rpmsg16()`, `__rpmsg32_to_cpu()`, `__cpu_to_rpmsg32()`, `__rpmsg64_to_cpu()`, and `__cpu_to_rpmsg64()`.

## Control flow, state, and persistence
There is no persistent state. Conversion helpers select little-endian or big-endian conversion based on the transport's endian flag; `rpmsg_is_little_endian()` reflects the default kernel-side rpmsg byte order.

## Dependencies and integration points
It depends on Linux endian annotations and byteorder helpers. `rpmsg.h` wraps these primitives with device-aware helpers using `rpdev->little_endian`, and vendor name-service/message headers use the typed fields for wire formats.

## Risks and test signals
Risks include bypassing the typed helpers, mixing CPU-endian integers with `__rpmsg*` fields, and assuming all transports are little-endian. Test signals are sparse/endian annotation coverage, loopback tests on little- and big-endian transports, and decoding name-service or vendor messages with known byte sequences.
