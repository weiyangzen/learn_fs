# Chunk Research: sources/os/linux/linux-stable/fs/nfs/nfs4proc.c lines 9527-10750

## Scope

This chunk covers the tail of the Linux NFSv4 client procedure implementation. It includes NFSv4.1 reclaim-complete, pNFS `LAYOUTGET`/`LAYOUTRETURN`/`GETDEVICEINFO`/`LAYOUTCOMMIT`, `SECINFO_NO_NAME` root security probing, `TEST_STATEID`/`FREE_STATEID`, NFSv4.1/v4.2 minor-version tables, VFS inode/xattr wiring, server cloning, swap hooks, and `nfs_v4_clientops`.

## APIs and Entry Points

- `nfs41_proc_reclaim_complete()` issues `NFSPROC4_CLNT_RECLAIM_COMPLETE`.
- `nfs4_proc_layoutget()` sends `LAYOUTGET`, handles pNFS-specific errors, and returns a layout segment or `ERR_PTR`.
- `nfs4_proc_layoutreturn()` sends `LAYOUTRETURN`, optionally async, with pNFS cleanup state protection.
- `nfs4_proc_getdeviceinfo()` wraps `GETDEVICEINFO` in exception retry logic and is GPL-exported.
- `nfs4_proc_layoutcommit()` sends `LAYOUTCOMMIT` sync or async and updates inode WCC attributes on release.
- `nfs41_find_root_sec()` resolves root auth flavor via `SECINFO_NO_NAME`, falling back to older probing.
- `nfs41_test_stateid()` and `nfs41_free_stateid()` implement NFSv4.1 stateid validation/freeing.
- `nfs_v4_minor_ops[]`, `nfs_v4_clientops`, inode ops, and xattr handlers publish the client’s operation tables.

## Control Flow

`LAYOUTGET` binds a sequence slot, runs an async RPC task, waits for completion, then converts server responses into local retry/fallback behavior. `LAYOUTUNAVAILABLE` becomes `-ENODATA`, `BADLAYOUT` becomes `-EOVERFLOW`, layout conflicts become retryable, and revoked/expired/bad stateids trigger either open-state recovery or local layout invalidation.

`LAYOUTRETURN` tolerates many cleanup failures. It may exit early for invalid layouts, retries transient network/session/delay errors, refreshes old stateids where possible, and otherwise often clears protocol failure status so local cleanup can proceed.

`SECINFO_NO_NAME` first tries integrity-protected machine credentials when possible, then falls back to the current filesystem RPC client on `WRONGSEC` or unavailable integrity. Root security probing filters returned flavors against mount auth policy.

The end of the chunk is table-driven: minor-version ops wire recovery/session/renewal/migration helpers, VFS inode ops expose NFSv4 directory/file behavior, and xattr handlers expose ACL/DACL/SACL/security-label/user attributes depending on config.

## State, Dependencies, Risks

Session state flows through `seq_args`/`seq_res`; pNFS state flows through layout headers, stateids, ranges, layout segments, and commit/return data. Retry state is carried by `struct nfs4_exception`.

Key dependencies include SUNRPC task APIs, `nfs4_procedures[]`, NFSv4 sequence/session helpers, pNFS layout helpers, state recovery helpers, RPC auth flavor mapping, VFS inode operations, LSM xattr listing, and NFSv4 ACL/user xattr helpers.

Notable risks:
- `nfs41_free_stateid()` increments `cl_count` before allocation/task failure paths that do not visibly drop the reference.
- Async `FREE_STATEID` marks the local stateid freed immediately after task submission.
- `LAYOUTRETURN` intentionally suppresses many failures, which can hide server-side return failure.
- `nfs4_proc_layoutcommit()` replaces flags with `RPC_TASK_ASYNC`, dropping the initial `RPC_TASK_MOVEABLE`.
- `nfs4_listxattr()` checks aggregate size only after calling all producers.

## Cross-Chunk References

Earlier chunks define most functions installed into `nfs_v4_clientops`, the NFSv4.0 minor ops table, reclaim-complete callbacks immediately preceding this range, state recovery helpers wired here, and ACL/security-label/user-xattr implementations exposed by this chunk. The final per-file report should merge this with prior `nfs4proc.c` chunk research.