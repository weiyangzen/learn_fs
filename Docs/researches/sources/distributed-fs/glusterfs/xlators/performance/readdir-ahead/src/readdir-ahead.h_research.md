# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead.h

## Purpose
Declares internal flags, helper macros, and state structures for `performance/readdir-ahead`.

## Important APIs, Types, And Functions
State flags define fd lifecycle and bypass behavior. `RDA_COMMON_MODIFICATION_FOP` allocates a local, refs the inode and xdata, captures the inode generation, and winds a child mutation fop. `RDA_STACK_UNWIND` unwinds and cleans `rda_local`. `rda_fd_ctx` stores directory prefetch state and cached entries. `rda_local` carries per-call state for prefetch and mutation callbacks. `rda_priv` stores option values and global cache size. `rda_inode_ctx_t` stores cached `iatt` plus generation.

## Control Flow
The macros shape most mutation callback control flow in `readdir-ahead.c`: every wrapped mutation captures pre-operation generation and updates stat cache only if the callback data is still valid for that generation.

## State And Persistence
All structures are in-memory translator state. Fd context lifetime follows directory fd lifetime; inode context lifetime follows inode forget.

## Dependencies And Integration Points
Requires Gluster locks, atomics, dirent lists, dicts, fds, inodes, and call stubs through included implementation context. It is the contract between the prefetch path and the metadata invalidation path.

## Risks
The macros assume `__rda_inode_ctx_get()` succeeds; if allocation fails, dereferencing `ctx_p` would be unsafe. The state flags are bit masks manipulated under `ctx->lock`; missing locking can corrupt bypass/EOD/run decisions.

## Test Signals
Compile tests should catch macro signature mismatch for all wrapped fops. Runtime mutation tests should show locals cleaned, xdata unrefed, and generation counters preventing stale stat updates.
