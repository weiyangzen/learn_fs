# sources/distributed-fs/openafs/src/vol/ihandle.c

Purpose: implementation of the inode-handle and file-descriptor-handle cache used by the volume package. It centralizes inode identity, descriptor reuse, buffered stream I/O, configurable fsync behavior, and portable low-level I/O wrappers.

Important APIs/types/functions: initialization/configuration functions are `ih_PkgDefaults`, `ih_SetSyncBehavior`, `ih_Initialize`, and `ih_UseLargeCache`. Handle lifecycle functions are `ih_init`, `ih_copy`, `ih_open`, `ih_attachfd`, `fd_close`, `fd_reallyclose`, `ih_reallyclose`, `ih_release`, and `ih_condsync`. Buffered I/O is implemented by `stream_fdopen`, `stream_open`, `stream_read`, `stream_write`, `stream_aseek`, `stream_flush`, and `stream_close`. OS support includes `ih_icreate`, `ih_icreate_init`, `ih_size`, fallback `ih_pread`/`ih_pwrite`, `ih_isunlinked`, `ih_fdsync`, and `fd_blocksize`.

Control flow: `ih_init` hashes `(dev, vid, ino)` and reuses an existing `IHandle_t` or allocates a chunk from the free list. `ih_open` first tries reusable descriptors on the handle, otherwise opens with `OS_IOPEN`, evicting from the global LRU when too many descriptors are open or `EMFILE` occurs. `fd_close` either returns a descriptor to the LRU cache or delegates to `fd_reallyclose`; `fd_reallyclose` closes and returns the descriptor handle to the free list. `ih_reallyclose` handles deferred syncs and closes all cached descriptors for one inode. Streams use positioned I/O and a fixed 2048-byte buffer, with explicit seek/flush needed to switch direction.

State and persistence: global mutable state includes free lists for inode/fd/stream handles, descriptor LRU, `ihashTable`, initialization flag, cache sizes, open descriptor count, global lock, and `vol_io_params`. Persistent effects are file creation, reads/writes/truncates/syncs through OS/namei/inode operations. `IH_SYNC_ONCLOSE` records `ih_synced` and defers fsync until `ih_reallyclose`.

Dependencies: `ihandle.h`, `viceinode.h`, OpenAFS assertions/logging, platform resource limits, pthread locks where enabled, OS open/read/write/seek/sync/stat calls, and NAMEI or inode syscall macros selected by the header.

Integration points: volume, vnode, salvager, and partition code use `IH_*`, `FDH_*`, and `STREAM_*` macros that map here. `listinodes.c` and volume conversion helpers rely on `FDH_PREAD/PWRITE`, `IH_CREATE`, and link-count operations.

Risks: one global lock simplifies correctness but limits concurrency and is temporarily dropped around close/sync operations. Header comments warn that concurrent `IH_OPEN` and `IH_REALLYCLOSE` on the same handle can race semantically. The cache shrinks after `EMFILE`, and descriptor accounting must remain exact. Stream write paths do not retry partial positioned writes. `IH_SYNC_NEVER` trades durability for speed.

Test signals: handle hash reuse/refcounts, chunk allocation, LRU reuse and eviction, `EMFILE` retry path, concurrent open/close stress, `IH_REALLY_CLOSED` behavior with in-use descriptors, sync behavior modes, stream read/write/seek/flush/close, fallback pread/pwrite seek semantics, blocksize/stat failures, and NAMEI versus inode build variants.
