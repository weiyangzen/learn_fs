# sources/cloud-native/composefs/libcomposefs/lcfs-fsverity.h

## Purpose
This header exposes the opaque streaming fs-verity digest context used by libcomposefs internals.

## Important APIs, Types, And Functions
It forward declares `FsVerityContext`, defines `LCFS_SHA256_DIGEST_LEN` as 32, and declares constructor, destructor, update, and final digest functions.

## Control Flow
Callers create a context, feed byte ranges in order, request the digest into a 32-byte buffer, and free the context.

## State And Persistence
No persistent state is defined here; persistence is through the returned digest consumed by writer and tooling paths.

## Dependencies And Integration Points
It includes `stdint.h` and `stddef.h`. `lcfs-internal.h` includes it so writer code can embed `FsVerityContext *` in `lcfs_ctx_s`.

## Risks
The API does not expose errors for update/get operations; allocation failure is only reported by `new` returning NULL. Callers must supply a valid 32-byte digest output buffer.

## Test Signals
Covered by writer digest output, measure-file tests, mount digest tests, and image checksum fixtures.
