# sources/distributed-fs/ceph-client/tools/include/tools/le_byteshift.h

## Purpose
Provides unaligned little-endian load/store helpers for 16-, 32-, and 64-bit integers in tools code.

## Important APIs, Types, and Functions
Defines `__get_unaligned_le16/32/64()`, `__put_unaligned_le16/32/64()`, and public wrappers `get_unaligned_le16/32/64()` and `put_unaligned_le16/32/64()`.

## Control Flow, State, and Persistence
Reads combine lower-address bytes as low-order bits; writes emit low-order bytes first. The 64-bit helpers compose two 32-bit operations. There is no state or persistence.

## Dependencies and Integration
Depends only on `<stdint.h>`. It integrates with perf data, ELF-related tooling, and other Linux tools that parse packed little-endian structures on hosts where direct unaligned access may trap or violate aliasing.

## Risks and Test Signals
Risks include buffer length errors, side-effect assumptions around inline wrappers, and accidental use for host-endian data. Test signals include round-trip arrays, unaligned addresses, 64-bit split-boundary cases, and comparison with `htole*`/`le*toh`.
