# sources/distributed-fs/glusterfs/xlators/features/quota/src/quota.c

## Purpose
`quota.c` implements the main GlusterFS quota feature translator. It enforces size and object-count limits before mutating operations, caches quota metadata in inode contexts, refreshes cluster-wide usage through quotad, adjusts `statfs` output when requested, protects internal quota xattrs from normal clients, and registers the quota xlator API.

## Important APIs, Types, and Functions
- Lifecycle/API: `init()`, `reconfigure()`, `notify()`, `fini()`, `mem_acct_init()`, `quota_priv_dump()`, `xlator_api`, `fops`, `cbks`.
- Inode/local state helpers: `quota_inode_ctx_get()`, `__quota_init_inode_ctx()`, `quota_local_new()`, `quota_local_cleanup()`, `quota_fill_inodectx()`, `quota_forget()`.
- Path and ancestry helpers: `quota_loc_fill()`, `quota_inode_loc_fill()`, `quota_inode_parent()`, `quota_find_common_ancestor()`, `quota_build_ancestry()`, `check_ancestory()`, `check_ancestory_2()`.
- Enforcement core: `quota_validate()`, `quota_validate_cbk()`, `quota_check_limit()`, `quota_check_size_limit()`, `quota_check_object_limit()`, `do_quota_check_limit()`, `quota_link_count_decrement()`.
- Mutating FOPs with precheck stubs: `quota_writev()`, `quota_fallocate()`, `quota_create()`, `quota_mkdir()`, `quota_mknod()`, `quota_symlink()`, `quota_link()`, `quota_rename()`.
- Metadata updating/pass-through FOPs: `quota_lookup()`, `quota_readdirp()`, `quota_unlink()`, `quota_truncate()`, `quota_ftruncate()`, `quota_stat()`, `quota_fstat()`, `quota_readv()`, `quota_readlink()`, `quota_fsync()`, `quota_setattr()`, `quota_fsetattr()`.
- Xattr/statfs interfaces: `quota_setxattr()`, `quota_fsetxattr()`, `quota_removexattr()`, `quota_fremovexattr()`, `quota_getxattr()`, `quota_fgetxattr()`, `quota_statfs()`.

## Control Flow
Initialization requires exactly one child, reads options (`server-quota`, `deem-statfs`, soft/hard timeout, alert time, default soft limit, volume UUID), creates a `quota_local_t` mem pool, and starts the quota enforcer RPC client when quota is active. Reconfigure toggles RPC setup/teardown as `server-quota` changes.

Lookup and `readdirp` request quota limit xattrs from lower layers and call `quota_fill_inodectx()` to populate `quota_inode_ctx_t`. This stores limits, object limits, stat data, and for regular files/symlinks a parent dentry list. If parent ancestry is missing, `quota_build_ancestry()` issues an internal `readdirp` with `GET_ANCESTRY_DENTRY_KEY` and quota keys to reconstruct paths to root and fill contexts.

Mutating operations allocate `quota_local_t`, create a call stub for the real child FOP, set `delta` and `object_delta`, and start `quota_check_limit()` from the relevant parent or file parents. `quota_check_limit()` walks upward to root or to a rename/link common ancestor. At each inode it checks object and size limits. If cached usage is stale based on soft/hard timeout, it calls `quota_validate()`, which requests cluster-wide metadata from quotad and resumes checking in `quota_validate_cbk()`. When all async path checks decrement `link_count` to zero, the stored stub is resumed.

If a hard size limit is exceeded but some bytes remain, `quota_writev_helper()` trims the iovec to `space_available` and performs a partial write. `fallocate` uses `len` as an assumed allocation delta. `mkdir/create/mknod/symlink` use `object_delta = 1`. Link and rename first build ancestry for source and destination, compute a common ancestor, and avoid double-counting above that ancestor.

`statfs` optionally finds the nearest limited ancestor, validates its usage, then rewrites `f_blocks`, `f_bfree`, and `f_bavail` to represent the quota hard limit and current usage. `getxattr/fgetxattr` synthesize `trusted.limit.list` from cached context. `setxattr/fsetxattr` update cached limits after a successful lower-layer operation, while normal clients are blocked from setting/removing trusted quota and pgfid xattrs.

## State and Persistence
Persistent quota facts live in lower-layer extended attributes such as `QUOTA_LIMIT_KEY`, `QUOTA_LIMIT_OBJECTS_KEY`, `QUOTA_SIZE_KEY`, contribution keys, dirty keys, and pgfid data. This translator keeps derived runtime cache in `quota_inode_ctx_t`: size, hard/soft size limits, file/dir counts, hard/soft object limits, latest `iatt`, parent dentries, validation/log timestamps, and ancestry status. `quota_priv_t` stores translator options, RPC client/service references, volume UUID, validation counter, and connection synchronization. `quota_local_t` stores per-FOP locs, deltas, pending stub, async link count, common ancestor, validation loc/xdata, and result status.

## Dependencies and Integration Points
The file depends heavily on GlusterFS xlator stack macros, inode context APIs, dictionaries, loc/inode/fd reference management, call stubs, iobuf/RPC through `quota_enforcer_lookup()`, event logging, and quota-common utilities. It integrates with marker/posix quota xattrs from lower layers, quotad for cluster-wide validation, DHT internal fop markers, statedump, and the volume option framework.

## Risks
- Enforcement correctness depends on valid ancestry. Missing parents trigger expensive reconstruction and can fail FOPs with `EIO`, but some active-FD write/fallocate cases intentionally allow operation on `ENOENT`/`ESTALE`.
- Cached size/object counts can be stale until validation timeouts expire; low timeouts increase quotad traffic while high timeouts increase overrun windows.
- Rename/link accounting is complex and includes FIXME comments around common-ancestor accounting and stripe assumptions.
- `fallocate` assumes the requested range was not already allocated, so it can reject valid preallocated-range operations.
- If contexts are absent after enabling quota before crawler completion, some operations log and proceed with weaker enforcement.
- Internal xattr filtering must stay aligned with trusted-client semantics; PID-based trust (`pid < 0`) is central to bypass behavior.

## Test Signals
Key tests should cover hard/soft size limits, object limits, soft-limit alerts, partial writes at remaining quota, writes with multiple hardlinks, stale parent dentry cleanup, rename/link across directories, directory rename validation, quotad restart during validation, crawler/nameless lookup ancestry recovery, `statfs` with `deem-statfs` on/off and ignore xdata, trusted xattr access from normal versus internal clients, reconfigure quota on/off, and memory cleanup through `forget`/`fini`.
