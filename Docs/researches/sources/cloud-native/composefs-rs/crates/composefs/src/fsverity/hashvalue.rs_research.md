# sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/hashvalue.rs

## Purpose
This module defines the fs-verity hash value contract, concrete SHA-256 and SHA-512 value types, and algorithm identifiers. It centralizes digest parsing, formatting, object-store pathname conversion, serde support, and kernel algorithm IDs.

## Important APIs, Types, and Functions
`FsVerityHashValue` requires cloneable, hashable, zerocopy-compatible, sendable digest value types with an associated `Digest`, `ALGORITHM`, and `EMPTY`. Provided helpers include `from_hex()`, `from_object_dir_and_basename()`, `from_object_pathname()`, `to_object_pathname()`, `to_object_dir()`, `to_hex()`, and `to_id()`. `Sha256HashValue` and `Sha512HashValue` are repr(C) byte wrappers with `From<Output<_>>` conversions. `Algorithm` covers SHA-256 and SHA-512 with a log2 block size, plus `for_hash()`, `hash_name()`, `kernel_id()`, `lg_blocksize()`, `is_compatible()`, `FromStr`, `Display`, and serde implementations. `AlgorithmParseError` documents all parse failures.

## Control Flow
Hex parsing decodes into a zero-initialized value buffer. Object path parsing accepts trailing `xx/rest` pathnames so higher-level prefixes can be ignored. Algorithm parsing requires the `fsverity-` prefix, splits at the last dash, validates the block size against `DEFAULT_LG_BLOCKSIZE`, and maps the hash name to a variant. Serialization stores the same string that `Display` emits.

## State and Persistence Behavior
These types carry value state only. They do not access the filesystem. The object pathname format is a persistence contract because repositories and flat digest stores use the first byte as a directory and remaining bytes as the basename.

## Dependencies and Integration Points
The module depends on `hex`, `sha2`, `serde`, and `zerocopy`. It is imported by fs-verity ioctl wrappers, userspace digest computation, repository object layout, dump/image parsing, and mount verification options. `kernel_id()` couples these values to Linux `FS_VERITY_HASH_ALGORITHM_*` IDs.

## Risks and Edge Cases
`from_object_pathname()` intentionally ignores leading path components, which is useful for repository paths but unsuitable where callers need strict path validation. `is_compatible()` compares enum discriminants only, so it distinguishes hash family but not block size; this is currently acceptable because only block size 12 is supported. New algorithms or block sizes would need updates across descriptor construction, ioctl wrappers, tests, and parsing.

## Test Signals
Generic tests validate empty hash formatting, debug output, `to_id()`, invalid hex cases, object basename and pathname parsing, SHA-256/SHA-512 instantiations, algorithm round-trips, error variants, equality, and compatibility checks.
