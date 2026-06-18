# sources/cloud-native/composefs-rs/crates/composefs/src/tree.rs

Purpose: specializes the generic filesystem tree model for composefs regular-file storage, where small files are inline and larger files are external fs-verity-addressed objects.

Important APIs/types/functions: `RegularFile<ObjectID>` with `Inline(Box<[u8]>)` and `External(ObjectID, u64)`, plus type aliases `LeafContent`, `Leaf`, `Directory`, `Inode`, `FileSystem`, and `DirectoryRef`. It re-exports `generic_tree`, `ImageError`, and `Stat`.

Control flow: this file mostly defines types; behavior is inherited from `generic_tree`. Tests create directories/leaves, insert entries into `BTreeMap`-backed directories, and validate lookup helpers for leaf IDs, regular file retrieval, and subdirectory retrieval.

State/persistence: persistent semantics are the tree metadata and leaf content strategy. External regular files persist only as an object hash plus declared size; inline regular files persist raw bytes in the image metadata.

Dependencies/integration: integrates fs-verity hash values into the generic tree and is used by dumpfile parsing, EROFS image writers, repository code, mkfs tests, and proptest tree generation.

Risks/test signals: correctness depends on external object size/hash consistency and on `generic_tree` preserving hardlink/shared-leaf semantics. Local tests cover basic insertion and typed lookup; broader coverage comes from mkfs and property tests that serialize this tree to EROFS.
