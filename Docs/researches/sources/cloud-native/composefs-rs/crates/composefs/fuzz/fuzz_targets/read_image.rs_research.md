# sources/cloud-native/composefs-rs/crates/composefs/fuzz/fuzz_targets/read_image.rs

Purpose: Fuzz target for EROFS image reading and high-level conversion APIs.

Important APIs and types: Uses `Image`, `InodeHeader`, `InodeOps`, `collect_objects`, `erofs_to_filesystem`, and `dumpfile::write_dumpfile`. The helper `exercise_image` walks as many reachable reader APIs as possible.

Control flow: The target tries `Image::open`; invalid images are ignored. For valid openings, it reads superblock fields, root inode metadata, xattrs, inline data, inode blocks, data blocks, directory entries, child inodes, object collection, and optional filesystem conversion followed by dumpfile serialization.

State and persistence: Stateless and in-memory. No corpus mutation is performed by the target itself; libFuzzer owns input generation.

Dependencies and integration: Integrates reader, fs-verity SHA-256 object collection, tree conversion, and dumpfile serialization, creating broader coverage than a parser-only target.

Risks: Traversal loops over entries and blocks from untrusted images; the reader must enforce bounds to avoid panics or excessive work. The target intentionally ignores errors, so it detects crashes but not missed validation or incorrect conversion.

Test signals: Excellent panic-safety signal for reader methods, xattr iteration, inline data handling, directory block parsing, block addressing, high-level conversion, and dumpfile writer interaction.
