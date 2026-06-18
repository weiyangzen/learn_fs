<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/portable_endian.h -->
# sources/distributed-fs/lizardfs/src/common/portable_endian.h

## Purpose
Provides portable host/big/little-endian conversion macro definitions across Linux, Cygwin, Apple, BSD, OpenBSD, NetBSD, Windows, and Solaris-like systems. The source was read completely for this report.

## Important APIs, Types, And Functions
Exports `htobe16/32/64`, `htole16/32/64`, `be16toh`, `le16toh`, byte-order constants, and platform-specific aliases where missing.

## Control Flow
Preprocessor branches include native endian headers or define conversion macros from platform byte-swap APIs.

## State And Persistence Behavior
No runtime state or persistence.

## Dependencies And Integration Points
Used by serialization/protocol code needing explicit endian conversions.

## Risks And Edge Cases
Unsupported platforms hit preprocessor errors. Macro names can collide with system headers if include order differs.

## Test Signals
Build tests on each supported OS/compiler are required; runtime byte-swap vector tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/portable_endian.h -->
