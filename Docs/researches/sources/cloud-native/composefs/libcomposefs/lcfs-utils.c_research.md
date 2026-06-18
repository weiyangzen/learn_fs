# sources/cloud-native/composefs/libcomposefs/lcfs-utils.c

## Purpose
`lcfs-utils.c` implements digest string/raw conversion helpers shared by tools and mount code.

## Important APIs, Types, And Functions
`digest_to_string` converts a 32-byte composefs digest to lowercase hex plus NUL. `digest_to_raw` parses a hex string into bytes up to a caller-supplied maximum, returning byte count or `-1` on invalid hex, odd input, or overflow.

## Control Flow
String conversion iterates digest bytes and emits two hex digits each. Raw parsing consumes two chars at a time through `hexdigit`; a missing second nibble is rejected because `hexdigit('\0')` returns negative.

## State And Persistence
No persistent state. Outputs are caller-provided buffers used for display, file paths, and mount digest comparison.

## Dependencies And Integration Points
It includes `lcfs-utils.h` and `lcfs-writer.h` for `LCFS_DIGEST_SIZE`. `lcfs-mount.c` uses `digest_to_raw`; tools use these helpers for user-facing digest output.

## Risks
`digest_to_raw` accepts any even-length hex string up to `max_size`; callers that require exact SHA-256 length must validate the returned size. No errno is set on parse failures.

## Test Signals
Digest output and digest mount tests in `test-units.sh`, checksum tests, and integration scripts exercise these conversions indirectly.
