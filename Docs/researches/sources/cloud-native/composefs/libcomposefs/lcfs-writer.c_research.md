# sources/cloud-native/composefs/libcomposefs/lcfs-writer.c

## Purpose
`lcfs-writer.c` implements the public node/tree API, filesystem tree ingestion, fs-verity helper wrappers, generic write context handling, and format dispatch for composefs images.

## Important APIs, Types, And Functions
Major public APIs include node lifecycle, cloning, loading from files/fds/images, building directory trees, child/xattr/payload/content accessors, fs-verity digest helpers, `lcfs_write_to`, and `lcfs_fd_enable_fsverity`. Important internals are `lcfs_compute_tree`, `follow_links`, `lcfs_write`, `lcfs_write_pad`, `lcfs_write_align`, `read_xattrs`, `lcfs_node_set_from_content`, `lcfs_node_validate`, and xattr set/unset/rename logic.

## Control Flow
Tree build starts with `lcfs_load_node_from_file`, records stat metadata, optional content digest/payload/inline content, symlink target, mtime, and xattrs, then recursively descends directories. Writing validates flags/version, may upgrade version for whiteouts, creates a format context, dispatches to the EROFS writer, captures digest output, and closes context. `lcfs_compute_tree` sorts xattrs, fixes directory nlink counts, forbids directory hardlinks, assigns BFS inode numbers, and verifies hardlink targets are in-tree.

## State And Persistence
Nodes own children, xattrs, payloads, inline content, digest, and inode metadata. Write contexts stream bytes to callbacks and optionally compute a fs-verity digest of the generated image. Persistent output is delegated to `lcfs-writer-erofs.c`.

## Dependencies And Integration Points
It depends on Linux stat/xattr/fsverity/ioctl APIs, EROFS chunking, internal hash/util helpers, and the public writer/mount headers. Tools use this as the main library surface.

## Risks
Ownership is subtle: `lcfs_node_add_child` takes ownership on success, children cannot be re-added, and hardlink refs can create invalid cycles caught lazily. Xattr size accounting limits external input. `lcfs_fd_get_fsverity` checks errno values after a helper that returns negative errno, which deserves care because the helper may canonicalize return codes and errno differently.

## Test Signals
`test-lcfs.c` covers basic writes, invalid uninitialized children, xattr add/remove/overwrite, fsverity absence, and a loader regression. Shell tests cover inline/object behavior, checksums, dump round trips, malformed input rejection, and random trees.
