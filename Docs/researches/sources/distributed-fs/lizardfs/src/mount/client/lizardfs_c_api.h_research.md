# sources/distributed-fs/lizardfs/src/mount/client/lizardfs_c_api.h

## Purpose
`lizardfs_c_api.h` declares the public C interface for applications using LizardFS client functionality without the FUSE mount process. It defines configuration, opaque handles, data structs, constants, and lifecycle/metadata/IO/ACL/chunk/lock functions.

## Important APIs, Types, And Functions
- `liz_init_params_t` exposes connection, authentication, read/write cache, timeout, directory/attribute/ACL cache, and IO limit settings.
- Opaque handles: `liz_t`, `liz_fileinfo_t`, `liz_context_t`, and `liz_acl_t`.
- Public structs include entries, attributes, direntries, named inode entries, xattr replies, statfs, chunk part/chunk info, chunkserver info, ACL ACEs, and lock interrupt data.
- Constants define special inodes, set-attribute masks, xattr modes, rich ACL flags/masks/special IDs, max goal/readlink sizes, and sugid clear modes.
- Functions cover context lifecycle, init/destroy, group updates, lookup/create/link/symlink/open/read/readv/write/release/flush/fsync/getattr/setattr, directory listing, trash/reserved lists, mkdir/rmdir/unlink/undel/rename, snapshots, goals, statfs, xattrs, ACLs, chunks/chunkservers, and locks.

## Control Flow
The API follows C/POSIX conventions: pointers are returned for created objects or open handles; most operations return `0` on success and `-1` on failure; byte operations return byte counts or `-1`; `liz_last_err` exposes the last LizardFS error for the calling thread. Several functions document required paired cleanup calls for allocated result buffers.

## State And Persistence
The header defines no implementation state. It documents opaque objects whose implementation owns connections, contexts, file handles, and ACL memory. Operations persist metadata/data changes through the LizardFS cluster.

## Dependencies And Integration Points
It includes POSIX headers for file modes, stat, and iovec. It is installed as the public header for `lizardfs-client` along with `lizardfs_error_codes.h`.

## Risks
- Some ACL helper macros appear inconsistent: `LIZ_ACL_POSIX_MODE_EXECUTE` uses `EXECUTE`, and `LIZ_ACL_POSIX_MODE_ALL` references `LIZ_POSIX_MODE_EXEC`, which are not defined in this header.
- The C API requires strict ownership discipline for buffers allocated by read directory, named inode, chunk, chunkserver, and ACL calls.
- Struct field sizes and enum values are ABI-sensitive.
- Comments mention parameters such as ACL `type` or setgoal `job_id` that are not present in the actual signatures, indicating documentation drift.

## Test Signals
Public ABI tests should compile C and C++ consumers, verify default init setup, exercise each cleanup contract under ASan/Valgrind, check macro availability, and validate struct layout compatibility across supported platforms.
