# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/format.rs

Purpose: Defines the zerocopy EROFS and composefs on-disk ABI: headers, constants, mode/file type encoding, format versions, feature flags, inode layouts, xattr structures, and directory entry headers.

Important APIs and types: Key exports include `BLOCK_BITS`, `BLOCK_SIZE`, `FormatError`, `FormatField`, `InodeLayout`, `DataLayout`, mode constants, `FileType`, `FileTypeField`, `ModeField`, `FormatVersion`, `FormatEpoch`, `FormatConfig`, `ComposefsHeader`, `Superblock`, `CompactInodeHeader`, `ExtendedInodeHeader`, `InodeXAttrHeader`, `XAttrHeader`, xattr constants/prefixes, and `DirectoryEntryHeader`.

Control flow: This file is mostly declarative, but conversions are important. `FormatField` maps raw bits to inode layout and fallible data layout. `InodeLayout | DataLayout` builds a `FormatField`. `FileTypeField` maps raw directory entry values to `FileType`, defaulting unknown values to `Unknown`. `FileType | permissions` constructs raw mode fields. `FormatVersion::epoch` collapses V0/V1 to compact-inode epoch 1 and V2 to extended-inode epoch 2. `FormatConfig::versions` yields default first and sorted extras excluding duplicates.

State and persistence: These structs are persisted directly in image bytes via `repr(C)` and little-endian `zerocopy` integer wrappers. `FormatConfig` is persisted in metadata JSON and controls which image format variants are generated.

Dependencies and integration: Depends on `zerocopy`, `serde`, and `serde_repr`. Reader, writer, debug, corpus generation, and repository metadata all consume these definitions.

Risks: This file is ABI-sensitive; field order, widths, and endianness cannot change casually. Unknown feature flags and unsupported xattr prefix differences matter for compatibility with C `mkcomposefs`, especially V0/V1. V1 deliberately skips `lustre.` prefix matching for C compatibility. `FileType::Unknown` must be handled by readers rather than passed into mode construction.

Test signals: Unit tests cover `FormatConfig` single/multi/dedup behavior, ordering, epoch mapping, and composefs version field values. Broader layout correctness is indirectly tested by reader/writer round trips and fuzz seeds.
