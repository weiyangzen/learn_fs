# Chunk Research: sources/os/linux/linux/fs/nfs/nfs4proc.c lines 9521-10754

## Scope

This chunk covers the tail of NFSv4.1 reclaim-complete RPC handling, pNFS `LAYOUTGET` / `LAYOUTRETURN` / `GETDEVICEINFO` / `LAYOUTCOMMIT`, NFSv4.1 `SECINFO_NO_NAME`, stateid test/free helpers, minor-version operation tables for NFSv4.1/v4.2, VFS inode operation tables, NFSv4 client RPC operation registration, and NFSv4 xattr handler registration.

Primary lines covered: `sources/os/linux/linux/fs/nfs/nfs4proc.c:9521-10754`.

The range begins inside `nfs4_reclaim_complete_done()` at the restart/return path; adjacent preceding lines define the callback's sequence completion and reclaim-complete error handler.

## APIs and Entry Points

- `nfs41_proc_reclaim_complete()` issues a global NFSv4.1 `RECLAIM_COMPLETE` using `clp->cl_rpcclient`, a privileged sequence, and `nfs4_reclaim_complete_call_ops`.
- `nfs4_proc_layoutget()` sends asynchronous `LAYOUTGET`, waits for completion, converts pNFS layout errors into Linux errno/retry signals, and returns either a `struct pnfs_layout_segment *` or `ERR_PTR(status)`.
- `max_response_pages()` computes the page-array length required for the session's maximum response size.
- `nfs4_proc_layoutreturn()` sends `LAYOUTRETURN`, optionally asynchronously, protects cleanup with machine credentials when required, and lets release handling free or retry local layout segments.
- `nfs4_proc_getdeviceinfo()` wraps `_nfs4_proc_getdeviceinfo()` with `nfs4_handle_exception()` retry handling and is exported with `EXPORT_SYMBOL_GPL`.
- `nfs4_proc_layoutcommit()` sends `LAYOUTCOMMIT`, either synchronously or asynchronously, and cleans pNFS layoutcommit state on task release.
- `_nfs41_proc_secinfo_no_name()`, `nfs41_proc_secinfo_no_name()`, and `nfs41_find_root_sec()` implement root security-flavor discovery through `SECINFO_NO_NAME`, with fallback to older root security probing.
- `_nfs41_test_stateid()` and `nfs41_test_stateid()` perform `TEST_STATEID` and handle delay/session retry classes.
- `nfs41_free_stateid()` sends asynchronous `FREE_STATEID`; `nfs41_free_lock_state()` uses it before freeing local lock state.
- `nfs41_match_stateid()` implements NFSv4.1 stateid matching, treating a zero sequence id as a wildcard; exported `nfs4_match_stateid()` delegates to generic `nfs4_stateid_match()`.
- `nfs_v4_minor_ops[]` registers minor-version operation tables for NFSv4.1 and, when compiled, NFSv4.2.
- `nfs4_listxattr()` merges generic, LSM/security, and NFSv4.2 user xattr names.
- `nfs4_enable_swap()` and `nfs4_disable_swap()` control NFSv4 state-manager liveness for swap usage.
- `nfs4_clone_server()` clones a server, applies session size limits, and allocates the NFSv4 delegation hash.
- `nfs_v4_clientops` publishes NFSv4 operations to the generic NFS client/VFS layer.
- `nfs4_xattr_handlers[]` publishes NFSv4 ACL, DACL, SACL, security-label, and NFSv4.2 user-xattr handlers.

## Control Flow

`nfs41_proc_reclaim_complete()` allocates callback data, sets `one_fs = 0` for global completion, initializes an NFSv4 sequence, and executes a synchronous custom RPC task. The visible part of `nfs4_reclaim_complete_done()` restarts the RPC call after retryable reclaim-complete errors.

`nfs4_proc_layoutget()` initializes a sequence, runs an async moveable RPC task with `RPC_TASK_CRED_NOREF`, waits for completion, and sends non-empty successful replies to `pnfs_layout_process()`. Important pNFS errors are translated to local fallback/retry statuses: `LAYOUTUNAVAILABLE` to `-ENODATA`, `BADLAYOUT` to `-EOVERFLOW`, conflicts to retry-style errors, and bad/revoked stateids to either open-state recovery or layout-stateid invalidation.

`nfs4_proc_layoutreturn()` applies state protection for pNFS cleanup, manages inode references for async operation, initializes the sequence, and starts the RPC. Release handling either frees returned layout segments or queues them for later retry, then drops sequence slots, layout private data, layout headers, inode refs, credentials, and the allocation.

`_nfs4_proc_getdeviceinfo()` requests change/delete notifications and marks a device `nocache` if notification support is incomplete. `nfs4_proc_getdeviceinfo()` wraps this in normal NFSv4 exception retry handling.

`nfs4_proc_layoutcommit()` can run sync or async. Its done callback ignores layout recall/no-layout/grace classes by clearing status; other errors can restart through `nfs4_async_handle_error()`. Release cleans layoutcommit state and forces WCC inode update.

`nfs41_find_root_sec()` uses `SECINFO_NO_NAME` when available, falls back to older probing on `WRONGSEC`/`ENOTSUPP`, then tests returned auth flavors against mount auth policy with `nfs4_lookup_root_sec()`.

Stateid helpers wrap `TEST_STATEID` and async `FREE_STATEID`, using protected machine credentials where required. Minor-version, VFS, RPC, and xattr tables at the end of the chunk publish earlier functions as externally reachable operations.

## State and Synchronization

- NFSv4 sessions use `nfs4_init_sequence()`, `nfs4_setup_sequence()`, sequence process/done callbacks, and explicit slot frees on retry/release paths.
- pNFS layout state is coordinated through layout headers, layout stateids, segment lists, driver-private cleanup hooks, and `NFS_LAYOUT_INVALID_STID`.
- `nfs4_layoutget_handle_exception()` holds `inode->i_lock` while comparing/invalidating layout stateids, then commits/frees affected segments after unlocking.
- Async pNFS operations preserve inode/client/credential/layout lifetime until RPC release callbacks.
- `nfs4_state_protect()` may switch RPC clients/credentials for pNFS cleanup and stateid operations.
- `nfs41_free_stateid()` uses `clp->cl_count` to keep `struct nfs_client` alive until async release.
- Swap hooks manipulate the NFSv4 state-manager state bits and wake waiters.
- `nfs4_clone_server()` owns and frees cloned server state on delegation-hash allocation failure.

## Dependencies

This chunk depends on SunRPC task APIs, NFSv4 procedure table entries, sequence/session helpers, exception recovery helpers, pNFS layout helpers, stateid/credential helpers, VFS xattr/security APIs, and NFS auth/root-security helpers.

Key dependencies include `rpc_run_task()`, `rpc_wait_for_completion_task()`, `rpc_restart_call_prepare()`, `nfs4_call_sync_custom()`, `nfs4_handle_exception()`, `nfs4_async_handle_error()`, `pnfs_layout_process()`, `pnfs_layoutreturn_free_lsegs()`, `pnfs_layoutreturn_retry_later()`, `pnfs_cleanup_layoutcommit()`, `nfs4_state_protect()`, `nfs_igrab_and_active()`, `generic_listxattr()`, `security_inode_listsecurity()`, `rpcauth_get_pseudoflavor()`, and `nfs_auth_info_match()`.

## Risks and Edge Cases

- The range starts mid-callback; reclaim-complete behavior depends on preceding error handling.
- Allocation failure in `nfs41_proc_reclaim_complete()` prevents protocol completion and can prolong recovery.
- `LAYOUTGET` retry paths must free sequence slots correctly to avoid session-slot leaks.
- Bad stateid classification depends on comparing the request stateid to the layout stateid under `inode->i_lock`; wrong classification can trigger the wrong recovery path.
- Empty successful `LAYOUTGET` replies are retryable and rely on backoff to avoid tight retry loops.
- `LAYOUTRETURN` intentionally treats several local RPC failures as local cleanup success, which can leave server-side awareness to lease/recovery behavior.
- `nfs41_free_stateid()` appears to increment `clp->cl_count` before allocations/task creation without visible cleanup on later failure paths in this chunk.
- `nfs41_free_lock_state()` ignores async `FREE_STATEID` status and frees local lock state regardless.
- `nfs41_match_stateid()` wildcard-matches zero sequence ids, a subtle NFSv4.1 semantic difference from strict equality.
- `nfs4_listxattr()` can report `-ERANGE` after component list functions have already generated partial output.
- `nfs4_clone_server()` depends on correct pairing of session-size limiting, delegation-hash allocation, and cloned-server cleanup.

## Cross-Chunk References

- The immediately preceding chunk defines the beginning of reclaim-complete handling, including prepare, error handling, and the first half of `nfs4_reclaim_complete_done()`.
- Earlier `nfs4proc.c` sections define most callbacks registered in `nfs_v4_clientops`.
- Earlier minor-version code defines `nfs_v4_0_minor_ops`, referenced conditionally here.
- Earlier NFSv4.1 session code defines `nfs41_call_sync_ops` and sequence slot operations installed here.
- Earlier state recovery functions are assembled into reboot/no-grace recovery tables in this chunk.
- pNFS code outside this file consumes the layoutget/layoutreturn/getdeviceinfo/layoutcommit entry points as metadata-server RPC backends.
- NFSv4 ACL, security-label, and user-xattr helpers referenced here are defined in adjacent NFS client xattr/ACL code.

## Research Notes

This chunk is the final integration layer for NFSv4.1/v4.2 client behavior in `nfs4proc.c`: it wires pNFS protocol operations into SunRPC tasks, converts NFS protocol statuses into retry/recovery/local fallback decisions, and publishes minor-version, VFS, RPC, and xattr operation tables. The highest-risk areas are asynchronous lifetime ownership, sequence-slot cleanup on retry paths, and pNFS error classification.