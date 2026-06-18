# sources/cloud-native/nydus/rafs/src/metadata/inode.rs

## Purpose
`inode.rs` provides version-neutral inode wrappers and an in-memory RAFS v6 inode intermediate representation. It is used by builder, converter, and metadata code that needs to inspect or mutate inode fields without committing to cached v5, direct v5, direct v6, or owned v5/v6 structures.

## Important APIs, Types, and Functions
- `InodeWrapper::{V5,V6,Ref}` wraps owned `RafsV5Inode`, owned `RafsV6Inode`, or `Arc<dyn RafsInodeExt>`.
- `new(RafsVersion)` constructs an owned default wrapper for v5 or v6.
- `from_inode_info()` wraps runtime inode trait objects.
- `is_v5()` and `is_v6()` classify owned or referenced implementations by enum variant/downcast.
- Field accessors and setters cover mode, type checks, inode number, parent, size, uid/gid, mtime, blocks, rdev, project id, nlink, digest, name size, symlink size, child index, child/chunk count, xattr/hardlink flags, and chunk creation.
- `ensure_owned()` converts a `Ref` into an owned v5 or v6 IR by using `RafsV5Inode::from(&dyn RafsInodeExt)` or `RafsV6Inode::from(&dyn RafsInodeExt)`.
- `RafsV6Inode` is a compact builder-side structure with RAFS common fields and helpers for file type, hardlink, xattr, hole, uid/gid, and mtime.
- `RafsInodeFlags` defines v5-style flags: `SYMLINK`, `HARDLINK`, `XATTR`, and `HAS_HOLE`.

## Control Flow
Most methods dispatch by wrapper variant. Read methods either read owned fields or proxy to `RafsInodeExt`/`RafsInode` for references. Mutating methods call `ensure_owned()` first; after conversion, they mutate owned fields and panic if a reference unexpectedly remains. Some APIs are intentionally version-specific: v6 parent access is unimplemented, v5-only digest access is unimplemented for v6, and some special-file methods on `Ref` are unimplemented if the common trait surface is insufficient.

## State and Persistence Behavior
`InodeWrapper` is an in-memory adapter and does not directly persist metadata. Owned variants can later be serialized by layout/store code. `Ref` variants share runtime metadata objects until mutation, at which point they snapshot into owned IR. `RafsV6Inode::from(&dyn RafsInodeExt)` copies FUSE-style attributes plus RAFS extension fields, so it is a lossy but practical bridge for builder/converter workflows.

## Dependencies and Integration Points
The wrapper bridges `cached_v5::CachedInodeV5`, `direct_v5::OndiskInodeWrapper`, `direct_v6::OndiskInodeWrapper`, `layout/v5::RafsV5Inode`, `layout/v6::{RafsV6InodeCompact,RafsV6InodeExtended}`, `RafsXAttrs`, `ChunkWrapper`, and `RafsVersion`. It is a central compatibility layer between metadata readers and metadata writers.

## Risks and Edge Cases
- Several methods use `unimplemented!()` or `panic!()` for unsupported variant/version combinations. Callers must branch on `is_v5()`/`is_v6()` before using version-specific methods.
- `ensure_owned()` calls `self.is_v6()` while holding a cloned reference path; unsupported reference types or incomplete downcasts can lead to assertions or incorrect ownership conversion.
- `name_size()` for `Ref` depends on runtime inode name context. Direct v6 non-root non-directory references often cannot provide extended name/parent information.
- `set_symlink_size()` sets the symlink flag but not target data; callers must maintain the associated variable-length symlink payload elsewhere.
- `RafsV6Inode` reuses `RafsInodeFlags`, even though v6 runtime direct wrappers return zero flags; builder-side and runtime-side flag semantics differ.

## Test Signals
Tests exercise wrapper classification, field setters/getters for owned v5/v6, conversion from cached/direct refs, expected panics for unsupported ref mutations or version-specific access, v6 inode helper methods, size calculation with xattrs, and default flag behavior. The tests are broad for adapter panic contracts but do not verify serialization round trips for owned v6 IR.
