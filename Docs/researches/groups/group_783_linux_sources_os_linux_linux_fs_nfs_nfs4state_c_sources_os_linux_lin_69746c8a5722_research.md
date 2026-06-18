# Group Research: group_783_linux_sources_os_linux_linux_fs_nfs_nfs4state_c_sources_os_linux_lin_69746c8a5722

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4state.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4state.c

## Purpose

`nfs4state.c` implements the Linux NFSv4 client-side state model. It owns client ID establishment, state owner caching, open and lock state objects, stateid selection for I/O, sequence-id serialization, asynchronous state recovery, lease renewal, session reset, migration recovery, and reactions to NFSv4.1 sequence status flags.

## Key Areas

- Client ID setup: `nfs4_init_clientid()` for v4.0 and `nfs41_init_clientid()` for v4.1+.
- Credential selection: machine credentials first, active state-owner credentials for renew fallback.
- Session draining/reset: prevents in-flight slot-table operations from racing recovery.
- State owner lifecycle: credential-keyed RB tree plus LRU caching.
- Open state lifecycle: inode/owner linked state objects with read/write mode tracking.
- Lock state lifecycle: VFS `file_lock` integration and lock-stateid handling.
- Stateid selection: lock stateid, delegation stateid, then open stateid.
- Recovery manager: kthread-driven state machine over `nfs_client->cl_state` bits.
- Migration/trunking: server trunk discovery, lease moved handling, transport replacement.
- Sequence flag handling: maps v4.1 server status flags to reclaim/reset/delegation actions.

## State Manager Flow

`nfs4_state_manager()` processes recovery in priority order:

1. purge state
2. expired lease
3. session reset
4. bind connection to session
5. lease check
6. migration
7. lease moved
8. reboot reclaim plus pNFS layout reboot handling
9. expired delegation detection
10. no-grace reclaim
11. delegation returns and recall-any layout returns

It runs under `memalloc_nofs_save()` to avoid reclaim/writeback deadlocks. Failures are traced with `nfs4_state_mgr_failed`, logged rate-limited, and usually retried after a sleep.

## Recovery Model

The file supports two reclaim modes:

- Reboot/grace reclaim with `NFS_STATE_RECLAIM_REBOOT`, `NFS_OWNER_RECLAIM_REBOOT`, and `NFS4CLNT_RECLAIM_REBOOT`.
- No-grace reclaim with `NFS_STATE_RECLAIM_NOGRACE`, `NFS_OWNER_RECLAIM_NOGRACE`, and `NFS4CLNT_RECLAIM_NOGRACE`.

`nfs4_do_reclaim()` drains sessions, purges cached owners, scans all mounted server state, reclaims opens and locks, handles recoverable protocol errors, and reports lost locks.

## Concurrency Notes

The file uses separate locking domains:

- `cl_lock` for client/server state-owner trees.
- `so_lock` for owner open-state lists.
- inode `i_lock` for inode open-state links.
- state `state_lock` for lock-state lists.
- RCU for open-state lookup/freeing.
- seqlocks for stateid snapshots.
- bit waiters and refcounts for manager lifetime.

## Cross-File Relationships

- Calls NFSv4 RPC helpers such as `nfs4_proc_exchange_id()`, `nfs4_proc_create_session()`, `nfs4_proc_destroy_session()`, `nfs4_proc_get_locations()`, and `nfs4_proc_bind_conn_to_session()`.
- Uses minor-version operation tables from `clp->cl_mvops`.
- Coordinates with delegation code for reclaim, expiry tests, and delegation returns.
- Coordinates with pNFS for layout destruction, reboot handling, recall-any layout return, and migration transport replacement.
- Emits tracepoints declared in `nfs4trace.h`.

## Research Notes

This file is best read as the NFSv4 client state machine. The key behavior is not individual RPC encoding, but ordering, retry policy, state marking, and coordination among leases, sessions, stateids, delegations, pNFS layouts, migration, and VFS locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4state.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4super.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4super.c

## Purpose

`nfs4super.c` wires NFSv4 into the Linux VFS superblock and module framework. It defines NFSv4 superblock operations, the NFSv4 subversion descriptor, mount/referral tree construction, inode writeback/eviction behavior, and module initialization/exit.

## Main Responsibilities

- `nfs4_sops` installs NFSv4 superblock operations.
- `nfs_v4` advertises the NFSv4 subversion to generic NFS client code.
- `nfs4_write_inode()` performs normal NFS writeback, then commits pNFS layout metadata.
- `nfs4_evict_inode()` truncates pages, clears the inode, returns delegations/layouts, destroys final layout state, clears generic NFS inode state, and zaps the xattr cache.
- Referral loop protection limits nested referral traversal per task.
- `do_nfs4_mount()` mounts the server pseudo-root internally, then walks to the requested export path with `mount_subtree()`.

## Mount Entry Points

- `nfs4_try_get_tree()` creates a normal NFSv4 server and follows the requested remote export path.
- `nfs4_get_referral_tree()` creates a referral server and uses the same root-walk mechanism.
- IPv6 hostnames are bracketed when synthesizing the root source string.

## Module Lifecycle

`init_nfs_v4()` initializes:

1. DNS resolver
2. NFSv4 idmapper
3. NFSv4.2 xattr cache when enabled
4. NFSv4 sysctls
5. NFSv4.2 server-side-copy ops when enabled
6. NFSv4 version registration

`exit_nfs_v4()` reverses those resources and also unloads conditional pNFS v3 data-server connection support.

## Cross-File Relationships

- Calls `nfs4_register_sysctl()` from `nfs4sysctl.c`.
- Uses delegation cleanup from `delegation.h`.
- Uses pNFS layout commit/return/destruction helpers.
- Registers `nfs_v4` for generic NFS mount dispatch.

## Research Notes

The most important behavior is the two-stage NFSv4 mount: mount the server root, then walk to the requested export. This supports NFSv4 pseudo-root and referrals while limiting recursive referral loops.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4sysctl.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4sysctl.c

## Purpose

`nfs4sysctl.c` registers NFSv4 client sysctl controls under `fs/nfs`.

## Sysctls

- `nfs_callback_tcpport`
  - Backs `nfs_callback_set_tcpport`.
  - Uses `proc_dointvec_minmax`.
  - Allows values from `0` through `65535`.
  - Mode `0644`.

- `idmap_cache_timeout`
  - Backs `nfs_idmap_cache_timeout`.
  - Uses `proc_dointvec`.
  - Mode `0644`.

## Entry Points

- `nfs4_register_sysctl()` registers the table and returns `-ENOMEM` on failure.
- `nfs4_unregister_sysctl()` unregisters the table and clears the stored header pointer.

## Cross-File Relationships

- Called by `nfs4super.c` during NFSv4 module initialization and exit.
- Depends on callback and idmap globals from the NFSv4 callback/idmapper code.

## Research Notes

This file only exposes runtime knobs. It does not implement callback service behavior or idmapper cache behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4trace.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4trace.c

## Purpose

`nfs4trace.c` is the tracepoint instantiation unit for NFSv4 tracing. It defines `CREATE_TRACE_POINTS` before including `nfs4trace.h`, causing the trace declarations to generate storage and registration code once.

## Exported Tracepoints

It exports GPL tracepoint symbols for pNFS/layout users:

- `nfs4_pnfs_read`
- `nfs4_pnfs_write`
- `nfs4_pnfs_commit_ds`
- `pnfs_mds_fallback_pg_init_read`
- `pnfs_mds_fallback_pg_init_write`
- `pnfs_mds_fallback_pg_get_mirror_count`
- `pnfs_mds_fallback_read_done`
- `pnfs_mds_fallback_write_done`
- `pnfs_mds_fallback_read_pagelist`
- `pnfs_mds_fallback_write_pagelist`
- `pnfs_ds_connect`
- `ff_layout_read_error`
- `ff_layout_write_error`
- `ff_layout_commit_error`
- `bl_ext_tree_prepare_commit`
- `bl_pr_key_reg`
- `bl_pr_key_reg_err`
- `bl_pr_key_unreg`
- `bl_pr_key_unreg_err`
- `fl_getdevinfo`

## Cross-File Relationships

- `nfs4trace.h` contains the actual event definitions.
- NFSv4 and pNFS source files include the header to emit trace events.
- pNFS layout modules rely on the exported tracepoint symbols.

## Research Notes

There is no business logic here beyond tracepoint materialization and symbol export. Its importance is build/linkage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4trace.h -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4trace.h

## Purpose

`nfs4trace.h` declares the NFSv4 client tracepoint surface. It covers client ID negotiation, sessions, callbacks, XDR decode errors, opens, closes, locks, recovery, delegations, namespace operations, attributes, idmapping, read/write/commit, pNFS layouts, device IDs, flexfiles, block-layout reservation keys, and NFSv4.2 operations.

## Structure

- Sets `TRACE_SYSTEM` to `nfs4`.
- Includes SUNRPC, filesystem, and NFS trace helper headers.
- Defines many reusable `DECLARE_EVENT_CLASS` blocks.
- Uses `TRACE_DEFINE_ENUM` to make state bits and protocol constants printable.
- Ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>`.

## Major Trace Families

- Client/session: `nfs4_setclientid`, `nfs4_exchange_id`, `nfs4_create_session`, `nfs4_sequence`, `nfs4_reclaim_complete`, `nfs4_sequence_done`.
- Callback: `nfs4_cb_sequence`, `nfs4_cb_seqid_err`, `nfs4_cb_offload`, `nfs_cb_no_clp`, `nfs_cb_badprinc`.
- State manager: `nfs4_state_mgr`, `nfs4_state_mgr_failed`.
- XDR: `nfs4_xdr_bad_operation`, `nfs4_xdr_status`, `nfs4_xdr_bad_filehandle`.
- Open/close/lock: `nfs4_open_file`, `nfs4_open_reclaim`, `nfs4_open_expired`, `nfs4_cached_open`, `nfs4_close`, `nfs4_get_lock`, `nfs4_set_lock`, `nfs4_unlock`.
- Delegation/stateid: `nfs4_set_delegation`, `nfs4_reclaim_delegation`, `nfs4_detach_delegation`, `nfs_delegation_need_return`, `nfs4_delegreturn_exit`, stateid test/match events.
- Namespace/metadata: lookup, create-like operations, remove, secinfo, rename, access, readlink, readdir, ACL, getattr, fsinfo.
- I/O: `nfs4_read`, `nfs4_pnfs_read`, `nfs4_write`, `nfs4_pnfs_write`, `nfs4_commit`, `nfs4_pnfs_commit_ds`.
- pNFS layout: `nfs4_layoutget`, layoutcommit/return/error/stats, `pnfs_update_layout`, MDS fallback events.
- Device/layout drivers: deviceid events, `fl_getdevinfo`, flexfiles error events, block-layout PR key events.
- NFSv4.2 conditional events: llseek, fallocate/deallocate, copy, clone, copy-notify, offload cancel/status, xattr operations.

## Payload Patterns

Most events normalize negative errors to positive status fields for formatting with `show_nfs4_status()`. File-related events commonly capture:

- device major/minor
- NFS fileid
- filehandle hash
- stateid sequence/hash
- byte ranges, offsets, counts, or open/lock modes where relevant

Trace classes reduce duplication for repeated operation shapes.

## Cross-File Relationships

- `nfs4trace.c` materializes these tracepoints.
- `nfs4state.c` emits state-manager and lock-reclaim events.
- NFSv4 proc/XDR/callback/delegation/pNFS/idmap/NFSv4.2 files include this header to trace protocol behavior.
- Exported pNFS tracepoints are made available by `nfs4trace.c`.

## Research Notes

This header is the primary observability contract for NFSv4 client behavior. A practical reading order is: client/session state, VFS protocol operations, pNFS/layout diagnostics, then conditional NFSv4.2 features.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4trace.h -->