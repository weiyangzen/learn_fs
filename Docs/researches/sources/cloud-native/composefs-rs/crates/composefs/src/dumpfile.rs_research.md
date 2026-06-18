# sources/cloud-native/composefs-rs/crates/composefs/src/dumpfile.rs

Purpose: Serializes `FileSystem` trees to composefs dumpfile text and rebuilds trees from parsed dumpfile entries. It bridges the internal tree model, dumpfile syntax, hardlink semantics, and EROFS validation.

Important APIs and types: Public writer APIs are `write_directory`, `write_leaf`, `write_hardlink`, `write_dumpfile`, `dump_single_dir`, and `dump_single_file`. Reader/conversion APIs are `add_entry_to_filesystem`, `dumpfile_to_filesystem`, and `dumpfile_to_validated_filesystem`. `DumpfileWriter` tracks hardlinks and nlink counts during traversal.

Control flow: Serialization writes root and sorted directory entries recursively. `write_entry` emits path, size, mode, nlink, uid/gid, rdev, mtime, payload, content, digest, and xattrs. It uses sentinel-aware escaping for normal fields and raw escaping for xattr key/value pairs. Leaf serialization distinguishes inline regular files, external fs-verity objects, devices, fifos, sockets, and symlinks. For repeated `LeafId`s, the first occurrence is serialized normally and later occurrences become hardlink lines. Parsing requires the first non-empty line to be root, then inserts entries into parent directories, resolving hardlinks through a path-to-`LeafId` map.

State and persistence: The module writes dumpfile bytes to supplied writers and builds in-memory `FileSystem` values from strings. It does not manage files directly. Temporary state includes hardlink maps, nlink maps, and buffered output.

Dependencies and integration: Depends on `dumpfile_parse::{Entry, Item}`, `generic_tree`, `tree`, `fsverity`, `rustix::fs::FileType`, and EROFS writer validation. It is exercised by the EROFS fuzz target when reader conversion succeeds.

Risks: Dumpfile parsing currently accepts `&str`, so non-UTF-8 dumpfile bytes cannot round-trip through `dumpfile_to_filesystem`. Parent directories must appear before children. External regular entries require a digest. Hardlinked whiteout character devices are rejected because composefs cannot represent them correctly.

Test signals: Unit tests cover simple conversion, hardlinks, dash symlink target round trips, xattr empty/dash round trips, hardlink writer round trips, hardlinked whiteout rejection, escape behavior, and proptest round trips for SHA-256/SHA-512 filesystem specs.
