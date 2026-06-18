# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/composefs.rs

Purpose: Defines composefs-specific EROFS overlay metadata for fs-verity metacopy digests.

Important APIs and types: `OverlayMetacopy<H: FsVerityHashValue>` is a `repr(C)` zerocopy struct with private version, length, flags, digest algorithm fields and public `digest`. `new`, `valid`, and private field accessors provide construction and validation.

Control flow: `new` fills version 0, struct length, flags 0, digest algorithm from the hash type's kernel id, and clones the digest. `valid` checks that all metadata fields match the expected current encoding for hash type `H`.

State and persistence: This is an on-disk/xattr binary layout type. It has no runtime state beyond struct contents and is intended to be serialized/deserialized by zerocopy.

Dependencies and integration: Depends on `zerocopy` derives and `FsVerityHashValue`. It is used by EROFS writer/reader code that encodes overlayfs metacopy xattrs containing fs-verity digests.

Risks: The `len` field is `u8`, so layout growth beyond 255 bytes would require a format change. Validation is type-specific; digest algorithm mismatch is rejected. Because fields are private, external callers cannot forge metadata except through raw bytes.

Test signals: No tests in this file; coverage should come from EROFS xattr/metacopy writer-reader tests.
