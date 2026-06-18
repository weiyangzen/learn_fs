# sources/cloud-native/fuse-overlayfs/src/sys/statx.rs

## Purpose
`sys/statx.rs` converts Linux `statx` results into traditional `libc::stat` and re-exports statx mask constants used by datasource and overlay metadata paths.

## Important APIs, Types, And Functions
`statx_to_stat` maps device, inode, mode, nlink, uid/gid, rdev, size, block size/count, and atime/mtime/ctime fields. Constants include `STATX_TYPE`, `STATX_MODE`, `STATX_INO`, and `STATX_BASIC_STATS`.

## Control Flow
Callers perform `statx`, then call `statx_to_stat` when they need the legacy `stat` shape expected by overlay attribute logic.

## State And Persistence
The module is pure conversion logic with no state and no writes.

## Dependencies And Integration Points
`overlay.rs` requests these masks when statting layer entries and converts stats to `fuser::FileAttr`. Datasource implementations likely bridge `statx` to `stat` with this helper.

## Risks
Field conversions are architecture-sensitive, especially device ids, nanosecond timestamps, and signedness/width of libc stat fields. Birth time and extended statx fields are intentionally not propagated.

## Test Signals
No direct tests in this file. Integration tests validate metadata presentation for mode, uid/gid, nlink, device rdev, timestamps, and file sizes through `stat`.
