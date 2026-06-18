# sources/distributed-fs/ceph-client/fs/coda/upcall.c

Purpose: implements the Coda kernel-to-Venus RPC layer and Venus-to-kernel downcall invalidation handling. All high-level Coda operations are marshaled into protocol packets and sent over the pseudo-device queues.

Important APIs/functions: `alloc_upcall()` fills common input headers with opcode, initial-namespace pid/pgid, and fsuid. `venus_rootfid()`, `venus_getattr()`, `venus_setattr()`, `venus_lookup()`, `venus_open()`, `venus_close()`, `venus_create()`, `venus_mkdir()`, `venus_remove()`, `venus_rmdir()`, `venus_rename()`, `venus_link()`, `venus_symlink()`, `venus_readlink()`, `venus_fsync()`, `venus_access()`, `venus_pioctl()`, `venus_statfs()`, and `venus_access_intent()` build operation-specific buffers. `coda_upcall()` queues synchronous or async `upc_req`s and waits for Venus. `coda_downcall()` handles cache invalidation and fid replacement.

Control flow: wrappers allocate a max(input, output) buffer, populate fixed fields plus inline NUL-terminated names, call `coda_upcall(coda_vcp(sb), ...)`, copy results back, and free buffers. `coda_upcall()` assigns a unique id, appends to `vc_pending`, wakes Venus, optionally waits on `uc_sleep`, maps positive Venus results to negative errno, and sends `CODA_SIGNAL` if interrupted after Venus read the request. Downcalls validate message size, find target inodes, then mark attributes/children stale, prune aliases, or replace fids.

State and persistence: uses `venus_comm` queues and sequence state; per-inode cache flags are updated for invalidation. No disk state is modified directly.

Dependencies/integration: tightly coupled to `psdev.c`, Coda protocol unions, VFS inode/dentry cache helpers, signal handling, and cache helpers in `coda_cache.h`.

Risks: packet sizing and inline string offsets must match the Coda ABI. Signal handling is subtle: close/store/access-intent are made hard to interrupt to preserve reference and data-loss invariants. Async finalizer access-intent requests transfer buffer ownership to the queue on success. Downcall size validation is essential before reading union fields.

Test signals: all Venus operation wrappers with boundary name lengths, interrupted synchronous upcalls before and after Venus read, Venus death while waiting, async access-intent finalizers, pioctl in/out bounds, and each downcall opcode invalidating expected dentries/inodes.
