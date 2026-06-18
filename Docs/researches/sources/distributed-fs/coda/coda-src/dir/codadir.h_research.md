# sources/distributed-fs/coda/coda-src/dir/codadir.h

## Purpose
Primary public interface for Coda directory handles, directory entries, directory inodes, directory-handle cache entries, and file identifier helpers.

## APIs, Types, and Functions
Defines `DIR_PAGESIZE`, `DIR_MAXPAGES`, data-location constants, `DirHandle`, `DirNFid`, `DirEntry`, and `DirInode`. Declares `DIR_Init()`, all `DH_*` operations, FID helpers (`FID_EQ()`, `FID_Cmp()`, local/disconnected/fake-root makers), `DIR_*` body helpers, `DI_*` inode copy/refcount/page routines, and `DC_*` cache functions.

## Control Flow, State, and Persistence
No implementation, but it describes the split: `DirHandle` owns locked contiguous `DirHeader` data, `DirInode` persists page pointers and refcount, and the `DCEntry` cache bridges the two. Directory data can live in RVM or VM depending on initialization.

## Dependencies and Integration
Depends on LWP locks, Coda kernel/Vice common FID types, doubly linked lists, and transaction annotations. It is included by directory library code, repair tooling, and Coda vnode/server components.

## Risks and Test Signals
Risks include a wide mutable API, duplicate declarations, exposed opaque pointer typedefs without full cache structure, fixed maximum of 128 pages, and macro comparisons assuming same volume. Test signals are clean cross-module compilation and runtime directory operations through handle, inode, and cache layers.
