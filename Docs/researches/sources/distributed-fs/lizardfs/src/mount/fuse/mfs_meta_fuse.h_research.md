# sources/distributed-fs/lizardfs/src/mount/fuse/mfs_meta_fuse.h

## Purpose
This header declares the meta filesystem's low-level FUSE callback surface. It is the compile-time contract used by `main.cc` to populate the meta `fuse_lowlevel_ops` table.

## Important APIs, Types, And Functions
Declarations cover meta statfs, lookup, getattr/setattr, unlink, rename, opendir/readdir/releasedir, open/release/read/write, and `mfs_meta_init()`. FUSE version gates handle `statfs` and FUSE 3 `rename` flags.

## Control Flow
No runtime flow exists in the header. The declared callbacks are invoked by libfuse only when `mfsmeta` selects the meta operation table.

## State And Persistence
No state is defined here. Runtime state lives in `mfs_meta_fuse.cc` through static cache settings and per-handle buffers.

## Dependencies And Integration Points
It depends on `common/platform.h` and `fuse_lowlevel.h`, and it integrates directly with the FUSE bootstrap in `main.cc` and implementation in `mfs_meta_fuse.cc`.

## Risks And Test Signals
The primary risk is signature mismatch across libfuse versions. Build coverage for FUSE 2 and FUSE 3, plus meta mount callback registration, are the relevant signals.
