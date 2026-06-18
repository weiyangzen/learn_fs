# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-helpers.c

## Purpose
Provides shared helpers for utime-generated fop wrappers: current-time capture and mapping fops to metadata-update flags.

## Important APIs, Types, and Functions
- `gl_timespec_get()` uses C11 `timespec_get(TIME_UTC)` when available, otherwise Gluster's `timespec_now_realtime()`.
- `utime_update_attribute_flags()` sets `frame->root->flags` bits such as `MDATA_CTIME`, `MDATA_MTIME`, `MDATA_ATIME`, `MDATA_PAR_CTIME`, and `MDATA_PAR_MTIME` based on `glusterfs_fop_t`.

## Control Flow
Generated wrappers call `gl_timespec_get(&frame->root->ctime)`, then call `utime_update_attribute_flags()`. The switch maps each fop family: xattr changes to ctime, allocation/zero-fill to mtime/atime, open/read/opendir to optional atime, creates to all inode and parent timestamps, deletes to ctime and parent timestamps, writes/truncates to ctime/mtime, and copy-file-range to destination ctime/mtime plus optional source atime.

## State and Persistence
Updates only per-call `frame->root` timestamp and flags. It reads `utime_priv_t.noatime` from `this->private`.

## Dependencies and Integration Points
Depends on `utime.h`, GlusterFS stack/time APIs, and metadata flag definitions. Called by generated utime fops.

## Risks
Default case clears `frame->root->flags`; unexpected fops passed here can erase preexisting flags. Missing null check for `this->private` after `this` validation assumes initialized translator private state.

## Test Signals
Unit or integration tests should assert flags for each generated fop class, especially noatime behavior and copy-file-range dual timestamp semantics.
