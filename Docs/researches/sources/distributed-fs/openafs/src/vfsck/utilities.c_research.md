<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/utilities.c -->
# sources/distributed-fs/openafs/src/vfsck/utilities.c

## Purpose
Provides shared fsck utility behavior: file-type validation, user prompting, buffer-cache management, raw disk read/write, block allocation/free, pathname reconstruction, signal handling, fix policy, diagnostics, clean-state updates, mount/writable checks, and HP-UX block-seek support.

## Important APIs, Types, And Functions
Important functions include `ftypeok`, `reply`, `bufinit`, `getdatablk`, `getblk`, `flush`, `rwerror`, `ckfini`, `bread`, `bwrite`, `allocblk`, `freeblk`, `getpathname`, `catch`, `catchquit`, `voidquit`, `dofix`, `errexit`, `pfatal`, `pwarn`, `pinfo`, `panic`, Sun helpers `debugclean`, `updateclean`, `printclean`, `hasvfsopt`, `writable`, `mounted`, and HP-UX helpers `setup_block_seek`, `setup_block_seek_2`, and `setup_all_block_seek`.

## Control Flow
The buffer cache is an LRU list of `bufarea` objects. `getdatablk` finds or loads a block, moves it to the front, and marks it in use. `getblk` flushes a reusable buffer before reading another disk block. `flush` writes dirty buffers and, for the superblock, also writes summary information. `ckfini` flushes all cached buffers, optionally updates the standard superblock when an alternate was used, frees buffers, and closes descriptors.

`reply` centralizes interactive policy for `-n`, `-y`, preen, no-write, and HP-UX fixed-state tracking. `dofix` decides whether a detected corruption should be salvaged now and caches that decision in `inodesc.id_fix`. `bread` and `bwrite` implement raw block I/O with fallback sector-by-sector diagnostics. Sun clean-state helpers update `fs_clean`/`fs_state` consistently. HP-UX 10.1 code can enable `O_BLKSEEK` and switch seek units for block devices.

## State And Persistence
This file mutates the dirty buffer cache, `fsmodified`, clean-state fields, block maps, counters, signal-driven exit state, and HP-UX `seek_options`. Persistent writes happen through `bwrite`, `flush`, `ckfini`, and `updateclean`.

## Dependencies And Integration Points
All pass files depend on these helpers for prompting, diagnostics, block I/O, and buffer lifecycle. `setup.c` calls `bufinit` and may use `writable`/`mounted`; `main.c` relies on `ckfini` and signal handlers. The HP-UX path depends on `libfs.h` and `O_BLKSEEK`.

## Risks And Test Signals
Risks include old unbounded varargs declarations, fixed-size buffers, no-write mode silently suppressing writes after prompts, sector fallback behavior on partial I/O, possible resource leaks in early `updateclean` returns, and platform-specific seek semantics. Tests should cover `-n/-y` prompt policy, dirty buffer flush, alternate superblock update, read/write error fallback, block allocation/free, pathname reconstruction, SIGINT/SIGQUIT handling, Sun clean-state transitions, mounted/writable detection, and HP-UX block-seek mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/utilities.c -->
