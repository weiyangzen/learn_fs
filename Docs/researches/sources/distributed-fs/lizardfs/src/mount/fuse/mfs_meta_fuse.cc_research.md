# sources/distributed-fs/lizardfs/src/mount/fuse/mfs_meta_fuse.cc

## Purpose
This file implements the low-level FUSE adapter for the LizardFS meta mount. The meta filesystem exposes synthetic directories and files for trash, undelete, reserved files, and master location data, allowing administrative actions such as purge and undel through filesystem operations.

## Important APIs, Types, And Functions
`mfs_meta_name_to_inode()` parses detached inode names encoded as eight hex digits followed by `|`. `mfs_meta_stat()` and `mfs_attr_to_stat()` build `stat` values for synthetic and detached entries. `mfs_meta_lookup()`, `getattr()`, `statfs()`, `unlink()`, and `rename()` implement discovery, attributes, purge, and undelete. `dirbuf` stores packed directory listings with a mutex; `pathbuf` stores editable trash paths. `dir_metaentries_*` emits synthetic `.`/`..`/trash/undel/reserved entries, while `dir_dataentries_*` converts master trash/reserved listings into FUSE entry names. `mfs_meta_open/read/write/release()` handle either the read-only `masterinfo` file or editable detached-object path files.

## Control Flow
Root lookup recognizes trash, reserved, and masterinfo. Trash lookup additionally recognizes `undel` and detached inode names; reserved lookup recognizes detached inode names. `unlink()` is accepted only under trash and calls `fs_purge()`. `rename()` is effectively an undelete trigger from trash to undel and calls `fs_undel()`. `opendir()` allocates a `dirbuf`; `readdir()` refreshes packed contents on first read or rewind, walks packed records from `off`, and replies with `fuse_add_direntry()` output. Opening a detached inode fetches its trash path, writes modify the path buffer up to 1024 bytes, and release calls `fs_settrashpath()` if changed.

## State And Persistence
Static state holds debug and cache timeout settings set by `mfs_meta_init()`. Per-open directory and path buffers are heap-allocated and protected with pthread mutexes. Persistent effects occur through master RPCs: purge, undelete, fetching trash/reserved lists, fetching detached attrs/paths, setting trash paths, and retrieving master location.

## Dependencies And Integration Points
The implementation depends on special inode definitions, `mastercomm` RPC functions, `masterproxy_getlocation()`, `exports` policy for non-root meta permissions, datapack helpers, protocol attribute formats, libfuse, and pthread mutexes. It is selected by `main.cc` when `mfsmeta` is enabled.

## Risks And Test Signals
Risks include manual packed-buffer parsing, missing replies on some allocation or mutex-init failures, old C-style pointer ownership, FUSE 3 rename flags ignored, and path writes that can create NUL-filled sparse buffers. Test signals should cover root/trash/reserved lookup, purge/undel behavior, directory rewind refresh, malformed directory data logging, masterinfo read sizes with and without version support, and path edit release behavior.
