## sources/distributed-fs/ceph-client/fs/orangefs/dir.c

### Purpose
This file implements OrangeFS directory file operations, including stateful readdir over daemon-returned directory trailers.

### Important APIs, types, and functions
- `struct orangefs_dir_part` and `struct orangefs_dir` store linked readdir result parts, server token, logical end position, and sticky error.
- `do_readdir()` sends `ORANGEFS_VFS_OP_READDIR`, allocates a readdir slot, handles purged retry, validates trailer size, and updates the token.
- `parse_readdir()` attaches the trailer buffer as a directory part after the response header.
- `fill_from_part()` decodes length/string/khandle records and emits dirents.
- `orangefs_dir_iterate()`, `orangefs_dir_llseek()`, `orangefs_dir_open()`, and `orangefs_dir_release()` implement VFS directory behavior.
- `orangefs_dir_operations` exports `.iterate_shared`, `.llseek`, `.open`, `.release`, and lease support.

### Control flow
Open allocates per-file directory state with token `ORANGEFS_ITERATE_START`. Iterate emits `.` and `..`, then uses high bits of `ctx->pos` as a part index and low bits as an offset within the part. If the caller seeks beyond cached parts, the code reads more from the server until it reaches the requested position or end token. Each trailer is parsed lazily as emitted. A seek to an earlier offset frees cached parts and restarts token iteration so userspace sees fresh directory contents.

### State and persistence behavior
Per-open state caches server directory result parts in vmalloc-backed trailer buffers returned by the daemon. Directory contents are not persisted locally and are discarded on release or when llseek resets the stream.

### Dependencies and integration points
Depends on `service_operation()`, readdir slot allocation from `orangefs-bufmap.c`, trailer layout from `downcall.h`, handle hashing from `orangefs-kernel.h`, and VFS `dir_context` emission. It is installed for directory inodes by `orangefs_init_iops()`.

### Risks
Directory offset encoding is custom and must remain compatible with userspace `telldir/seekdir` behavior. Corrupt trailer data or invalid offsets are mapped to `-EIO`. Trailer ownership transfers to the directory part list, so every path must either free or retain exactly once. The code uses `BUG_ON()` for impossible offset overflow, which is harsh if malformed trailers bypass validation.

### Test signals
Test large directories over multiple parts, seekdir/telldir, short userspace buffers, daemon restart during readdir, corrupt trailer handling, readdir after rename/create/delete, and release freeing all cached parts.
