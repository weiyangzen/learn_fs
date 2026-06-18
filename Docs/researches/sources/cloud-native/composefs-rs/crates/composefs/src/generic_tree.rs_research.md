# sources/cloud-native/composefs-rs/crates/composefs/src/generic_tree.rs

## Purpose
This module defines a generic metadata-rich filesystem tree where regular file content is caller-defined. It is the reusable tree model underneath composefs image construction, scanning, dump parsing, OCI transforms, and hardlink representation.

## Important APIs, Types, and Functions
Core types are `Stat`, `LeafId`, `LeafContent<T>`, `Leaf<T>`, `Directory<T>`, `Inode<T>`, `ImageError`, `FileSystem<T>`, and `DirectoryRef<'a, T>`. `Stat::uninitialized()` provides placeholder root metadata for incremental builds. `Directory` offers lookup, traversal, split, insert, merge, remove, pop, clear, hardlink remapping, top-level filtering, and newest-mtime discovery. `FileSystem` offers construction, root stat replacement, leaf allocation, OCI transforms, stat iteration, xattr filtering, regular-content mapping, compaction, nlink counts, fsck validation, and leaf access. `DirectoryRef` pairs a directory reference with the filesystem leaves table for ergonomic read-only operations.

## Control Flow
Directory traversal uses `Path::components()` and rejects prefixes, `.`, and `..` for image safety. `split()` and `split_mut()` locate the parent directory and basename for path-based operations. `merge()` preserves existing directory entries when a directory overlays a directory but replaces non-directory content. Hardlinks are represented by multiple `Inode::Leaf` entries pointing at one `LeafId`. `try_map_regular()` maps each leaf table entry exactly once and retypes the directory tree without changing indices. `compact()` counts references, builds an old-to-new `LeafId` map, drains live leaves into a new vector, remaps tree references, and debug-checks consistency.

OCI-related flow is explicit: `transform_for_oci()` copies root metadata from `/usr` and canonicalizes `/run`. `add_overlay_whiteouts()` creates root entries `00` through `ff` as character devices unless already present, inheriting root uid/gid/mtime and only `security.selinux` xattr for C format compatibility.

## State and Persistence Behavior
All state is in memory. Directory entries are `BTreeMap`s, giving deterministic ordering. The leaves vector is the authoritative storage for non-directory metadata and content; tree nodes reference it by index. Methods like `remove()` and `clear()` can orphan leaves until `compact()` is called, while `fsck()` detects such orphans. Xattrs are stored per `Stat` as `BTreeMap<Box<OsStr>, Box<[u8]>>`.

## Dependencies and Integration Points
This module depends only on standard collections/path types and `thiserror`. Other modules alias or wrap it as `tree`, serialize it to EROFS/dump formats, scan into it from `fs.rs`, and transform it for OCI consistency. It deliberately does not know about fs-verity object IDs except through generic `T`.

## Risks and Edge Cases
`Inode::stat()` and `FileSystem::leaf()` index directly and can panic if the tree is invalid; callers should use `fsck()` when consuming untrusted trees. `Directory::remap_leaf()` panics on invalid entries and is intended for internal hardlink surgery. Removing entries without compacting can leave orphan leaves that affect iteration and validation. `copy_root_metadata_from_usr()` and `canonicalize_run()` require `/usr` for standard OCI flows, so minimal filesystems without `/usr` will error. The whiteout helper mutates the root namespace heavily and must remain aligned with C compatibility rules.

## Test Signals
Tests cover directory insertion, lookup, error variants, file access, removal, merge semantics, clear, newest mtime, sorted entries, root metadata copying, missing `/usr`, xattr filtering, `/run` canonicalization, regular-content mapping, hardlink sharing, error propagation, OCI transform, Send/Sync, compaction, nlink counts, mutable stat iteration, and overlay whiteout behavior.
