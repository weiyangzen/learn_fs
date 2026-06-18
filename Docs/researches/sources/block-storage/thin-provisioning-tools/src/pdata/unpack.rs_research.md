# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/unpack.rs

Defines `Unpack` and `Pack` traits for fixed-size on-disk values. Provides helper `unpack<U>` converting nom parse failures to `io::ErrorKind::InvalidData`.

Implements little-endian packing/unpacking for `u64` and `u32`, which are the primitive value types used throughout btree, bitmap, and array structures.
