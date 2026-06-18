# sources/cloud-native/nydus/rafs/src/metadata/layout/mod.rs

## Purpose
`layout/mod.rs` is the shared metadata layout utility module for RAFS. It defines RAFS version constants, root inode identity, xattr type aliases and validation helpers, unsafe byte-structure conversion macros, common xattr parsing/storage utilities, and `MetaRange` range validation used by direct-mapped metadata loaders.

## Important APIs, Types, and Functions
- Version constants: `RAFS_SUPER_VERSION_V4`, `RAFS_SUPER_VERSION_V5`, `RAFS_SUPER_VERSION_V6`, `RAFS_SUPER_MIN_VERSION`, and `RAFS_V5_ROOT_INODE`.
- `XattrName` and `XattrValue` are byte-vector aliases used by inode APIs.
- `pub mod v5` and `pub mod v6` expose version-specific on-disk layout structures.
- `RafsBlobTable` is a simple enum over v5 and v6 blob table implementations.
- `impl_bootstrap_converter!` generates checked `TryFrom<&[u8]>`, `TryFrom<&mut [u8]>`, `AsRef<[u8]>`, and `AsMut<[u8]>` for fixed-size layout structs, enforcing exact size and alignment before unsafe casting.
- `impl_pub_getter_setter!` generates little-endian public getters/setters for on-disk fields.
- `parse_string()` parses UTF-8 data into a leading string and trailing remainder split at the first NUL.
- `bytes_to_os_str()` converts raw bytes to Unix `OsStr` without UTF-8 validation.
- `parse_xattr()`, `parse_xattr_names()`, and `parse_xattr_value()` parse v5-style xattr records encoded as little-endian pair length plus `name\0value`.
- `RafsXAttrs` owns xattr pairs and validates allowed prefixes and key/value sizes.
- `MetaRange` validates aligned metadata regions, overflow, containment, and intersection.

## Control Flow
Fixed layout conversion starts with macro-generated size/alignment checks before any unsafe cast. Xattr parsing walks a bounded byte slice, repeatedly reading a pair length, validating that enough bytes remain, splitting the pair at the first NUL, and invoking a callback. `parse_xattr_names()` and `parse_xattr_value()` are thin callback specializations. `RafsXAttrs::add()` validates key length, value length, and namespace prefix before inserting. `MetaRange::new()` rejects unaligned or overflowing ranges; direct metadata loaders compose `is_subrange_of()` and `intersect_with()` to reject malformed bootstrap sections.

## State and Persistence Behavior
This module mostly defines stateless helpers. `RafsXAttrs` is the owned stateful piece; it stores pairs in a `HashMap<OsString, Vec<u8>>` and computes serialized v5 size from key/value lengths. It does not itself write xattrs in this file, but version-specific layout modules use it for storage sizing and serialization. `MetaRange` is an immutable validation value.

## Dependencies and Integration Points
The module is imported by cached and direct metadata backends for root inode constants, xattr parsing, byte-to-name conversion, and metadata range validation. Version-specific modules `layout/v5` and `layout/v6` depend on the macros and shared xattr concepts. `MetaRange` is a security boundary for direct mmap backends, while `parse_xattr*` is the shared parser for cached and direct v5 xattr access.

## Risks and Edge Cases
- `impl_bootstrap_converter!` uses unsafe casts after checks; all callers rely on exact length and alignment validation being correct.
- `parse_xattr()` silently ignores a pair with no NUL separator rather than returning an error, which may hide malformed xattr records.
- `parse_string()` requires UTF-8, while many filesystem names are handled as raw `OsStr`; callers must choose the correct helper.
- `RafsXAttrs::add()` allows only predefined prefixes and caps key/value sizes. That is good for consistency but can reject future namespaces unless the prefix list is updated with v6 namespace constants.
- `MetaRange` alignment uses `RAFSV5_ALIGNMENT` even though it is also used by v6 direct validation; this is currently compatible with the code's assumptions but should be revisited if v6 alignment constraints diverge.

## Test Signals
Tests cover unsafe converter rejection for misalignment and wrong length, mutable conversion and byte views, UTF-8/NUL parsing, invalid and valid xattr records, and `MetaRange` overflow, alignment, containment, and intersection behavior. There is no test for xattr pairs without NUL separators or for all allowed `RafsXAttrs::add()` prefixes.
