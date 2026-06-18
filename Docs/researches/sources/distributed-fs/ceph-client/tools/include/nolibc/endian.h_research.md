# sources/distributed-fs/ceph-client/tools/include/nolibc/endian.h

## Purpose
Provides host-to/from big- and little-endian conversion macro names for nolibc.

## APIs, Types, and Functions
Defines `htobe16`, `htole16`, `be16toh`, `le16toh`, and the corresponding 32- and 64-bit variants, each mapped to Linux byteorder helpers.

## Control Flow, State, and Persistence
Macros expand into endian conversion expressions and keep no state. Control flow is limited to whatever the underlying byteorder helper emits for the target endian.

## Dependencies and Integration
Depends on `stdint.h` and `<asm/byteorder.h>`. It integrates with binary format, network, and filesystem tools that use common endian conversion names.

## Risks and Test Signals
Risks include side-effect arguments, mismatch with libc feature-test expectations, and missing less-common macros such as PDP endian helpers. Test signals are constant-expression conversions, big/little-endian build coverage, and parser round trips.
