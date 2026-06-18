<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/node.rs -->
# sources/cloud-native/fuse-overlayfs/src/node.rs

Purpose: node arena, directory state, inode table, path computation, and statistics for the overlay filesystem.

Important APIs and flow: `DirState` separates non-directories from directories with child and whiteout maps plus loaded state. `NodeArena` owns `OvlNode` values behind opaque `NodeId`s and updates global node counters. `OvlNode` stores parent, layer indexes, underlying inode/device, name, hidden deletion state, link count, mode, and child/whiteout helpers. `Drop` cleans hidden files/dirs from workdir. `compute_fuse_ino` uses raw inode when layers share a device or hashes inode/device otherwise. `InodeTable` maps `(ino,dev)` to `OvlIno`, tracks hardlinks and lookup counts, resolves collisions with fallback inode numbers, leaves tombstones for recycled inodes, and handles FUSE forget.

State and persistence: all primary state is in-memory; hidden node cleanup can unlink workdir paths on drop. Integration points are overlay lookup/readdir/forget/copy-up paths and SIGUSR1 stats in `main.rs`. Risks include stale tombstones until forget, path computation cost via parent walks, concurrent consistency depending on outer locks, hidden cleanup best-effort behavior, and inode collision/recycling edge cases. Unit tests cover node creation, child maps, arena insert/remove, inode registration, forget, path computation, hashing, collision behavior, and related primitives.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/node.rs -->
