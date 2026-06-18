# sources/distributed-fs/ceph-client/fs/jffs2/compr.c

## Purpose
`compr.c` owns the JFFS2 compressor registry and the policy layer used by inode writes and garbage collection to choose how data nodes are stored. It provides compressor registration, global/default compression-mode selection, runtime compression dispatch, decompression dispatch, statistics accounting, and init/exit ordering for the optional zlib, rtime, Rubin, and LZO backends.

## Important APIs, Types, And Functions
The public entry points are `jffs2_compress()`, `jffs2_decompress()`, `jffs2_register_compressor()`, `jffs2_unregister_compressor()`, `jffs2_free_comprbuf()`, `jffs2_compressors_init()`, and `jffs2_compressors_exit()`. The static `jffs2_selected_compress()` implements priority/forced single-backend selection, while `jffs2_is_best_compression()` ranks backends for size and LZO-favoring modes. All backend implementations plug in through `struct jffs2_compressor` from `compr.h`.

## Control Flow
`jffs2_compress()` derives the active mode from mount options or the global default. Priority mode calls the first registered enabled compressor that succeeds; size and favour-LZO modes try every enabled backend using each compressor's temporary buffer and keep the best result; force modes call a requested backend. If no backend wins, the original input buffer is returned with `JFFS2_COMPR_NONE`. `jffs2_decompress()` special-cases uncompressed and zero-filled nodes, then looks up the backend by compression id and calls its decompressor.

## State And Persistence Behavior
Persistent on-flash state is the compression byte stored in raw inode nodes by write/GC code. In-core state includes `jffs2_compressor_list`, `jffs2_compression_mode`, per-backend `usecount`, temporary compression buffers, and compression/decompression counters. The registry is protected by `jffs2_compressor_list_lock`; the lock is dropped while backend code runs, with `usecount` preventing safe unregister during active use.

## Dependencies And Integration Points
This file depends on Linux list/spinlock allocation APIs, `linux/jffs2.h` compression constants, and the backend init/exit functions declared in `compr.h`. It is called by `write.c` and `gc.c` before `jffs2_write_dnode()` persists raw inode nodes, and by read paths when reconstructing file data.

## Risks And Test Signals
Risk concentrates around lock dropping while manipulating per-compressor buffers, failure to restore `datalen`/`cdatalen` between backend trials, backend id availability for old media, and fallback behavior that returns the original buffer. Useful tests mount with each compression mode, force LZO/zlib, disable individual compressors, verify decompression of legacy images, and stress concurrent writes, GC, and module teardown.
