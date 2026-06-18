# sources/distributed-fs/ceph-client/fs/hpfs/hpfs_fn.h

Purpose: this is the HPFS private runtime header. It defines in-memory superblock/inode state, helper macros/inlines, cross-file function prototypes, time conversion helpers, and the global locking API.

Important types and helpers: `struct hpfs_inode_info` extends VFS inodes with directory root dnode, parent fnode, file extent cache, EA state bits, active readdir offsets, and dirty state. `struct hpfs_sb_info` stores mount options, bitmap pointers, free counts, code-page table, hotfix mappings, and the filesystem mutex. `struct quad_buffer_head` represents four sector buffers plus a contiguous view. Inlines parse dirents and EAs, compute dirent sizes, copy dirent metadata, scan bitmap bits, convert local/GMT HPFS time, and assert/take/release `hpfs_mutex`.

Control flow role: the prototypes define subsystem boundaries across allocation, anode, buffer, dentry, directory, dnode, EA, file, inode, map, name, namei, and superblock code. The locking comment establishes the design: VFS-entry methods take one whole-filesystem mutex rather than fine-grained locks.

State and persistence: the header itself persists nothing, but its state structs are the in-memory control plane for all persistent operations. Inline helpers directly interpret on-disk data inside mapped buffers.

Dependencies and integration: it includes kernel mutex, pagemap, buffer-head, slab, signal, blkdev, and unaligned helpers, and includes `hpfs.h` for raw layout. Every HPFS `.c` file includes this header.

Risks: helper inlines operate on raw variable-length records; bad lengths can create pointer errors if callers did not map/validate structures first. `tstbits()` encodes bitmap semantics used by allocator and trim. The global mutex is simple but easy to forget in new VFS paths; `hpfs_lock_assert()` catches some internal misuse.

Test signals: build all HPFS objects after prototype changes, run strict-check mounts to exercise dirent/EA inlines, validate time conversion with `timeshift`, test lock assertions, and ensure active readdir offset tracking is initialized/freed on inode lifecycle.
