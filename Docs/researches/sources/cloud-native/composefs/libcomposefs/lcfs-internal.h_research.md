# sources/cloud-native/composefs/libcomposefs/lcfs-internal.h

## Purpose
`lcfs-internal.h` defines libcomposefs private data structures, endian/align macros, overlay xattr constants, validation limits, and internal function prototypes shared by writer, EROFS, mount, and utility code.

## Important APIs, Types, And Functions
Key types are `errint_t`, `struct lcfs_xattr_s`, `struct lcfs_inode_s`, `struct lcfs_node_s`, and `struct lcfs_ctx_s`. The node holds refcount, parent/children, hardlink target, name, payload, inline content, xattrs, digest, inode metadata, and temporary EROFS layout fields. The context holds write options, root, queue/layout state, output callback, byte count, fs-verity context, and a format finalizer.

## Control Flow
This header does not execute control flow but codifies the phases used elsewhere: tree construction, compute-tree BFS, format-specific EROFS layout, serialization, digest computation, and cleanup. `cleanup_node` wraps `lcfs_node_unref` for local ownership.

## State And Persistence
In-memory node state maps to persisted EROFS inode metadata, xattrs, payload redirects, inline content, and digest xattrs. Temporary fields such as `next`, `in_tree`, `inode_num`, and `erofs_*` are recomputed during writes.

## Dependencies And Integration Points
It includes endian headers selected by Meson, public writer/fsverity/hash headers, and exposes prototypes implemented by `lcfs-writer.c` and `lcfs-writer-erofs.c`.

## Risks
This is the central ownership contract. Refcount, parent, hardlink, and child ownership mistakes can cause leaks, double unrefs, or cycles. Overlay xattr constants must match kernel overlayfs expectations.

## Test Signals
Most tests exercise this header indirectly. `test-lcfs.c` specifically covers ref/child ownership, invalid uninitialized nodes, xattr replacement, and hardlinked whiteout image-load handling.
