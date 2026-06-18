# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-helpers.c

## Purpose

`posix-helpers.c` is the shared utility layer for GlusterFS's POSIX storage translator. It sits below the translator FOP implementations and above raw backend filesystem syscalls, centralizing behaviors that many POSIX operations need: extended attribute policy, GFID assignment and handle maintenance, `iatt` construction, ACL translation, background janitor and health threads, disk-space reserve tracking, fd/inode context creation, batched fsync processing, bitrot signature lookup, cloudsync xattr state repair, and small validation helpers.

The file is not a standalone service. Its functions are exported through `posix.h` and are called heavily by `posix-entry-ops.c`, `posix-inode-fd-ops.c`, `posix-handle.c`, `posix-common.c`, POSIX AIO, and io_uring paths. Its correctness matters because it defines how the brick's local filesystem state is represented to the rest of GlusterFS.

## Important APIs, Types, and Functions

- `posix_xattr_fill(...)` builds a response dictionary for requested xattrs. It supports explicit keys, `list-xattr`, file content reads via `GF_CONTENT_KEY`, fd counters, ancestry path lookup, quota marker contribution xattrs, ACL fetches, link count and size metadata, and backend xattr wildcard matching.
- `posix_handle_pair(...)` and `posix_fhandle_pair(...)` apply path- or fd-based xattr updates. They reject pathinfo mutation, reject gfid2path xattrs, bridge virtual POSIX ACL requests through ACL library calls, handle metadata xattr updates through `posix_set_mdata_xattr_legacy_files`, and otherwise call `sys_lsetxattr` or `sys_fsetxattr`.
- `posix_fdstat(...)`, `posix_istat(...)`, and `posix_pstat(...)` convert backend `stat`/`lstat` results into Gluster `struct iatt`, adjust non-directory link counts, fetch ctime metadata when enabled, fill GFID, and derive synthetic inode numbers from GFID.
- `posix_gfid_set(...)`, `posix_gfid_unset(...)`, and `posix_gfid_heal(...)` manage the on-disk `trusted.gfid` xattr and the `.glusterfs` handle tree. `posix_gfid_heal` specifically tries to avoid a lookup/create race by treating very fresh files without GFID as not yet stable.
- `posix_pacl_get(...)` and `posix_pacl_set(...)` translate Gluster POSIX ACL xattr requests into platform ACL APIs when available, with ENOTSUP stubs otherwise.
- `posix_janitor_timer_start(...)`, `posix_janitor_task(...)`, and `janitor_walker(...)` periodically purge the trash/landfill path and clean stale GFID handles for removed directories.
- `posix_spawn_ctx_janitor_thread(...)` and `posix_ctx_janitor_thread_proc(...)` run a context-wide fd cleanup worker that closes deferred file and directory descriptors from all POSIX xlators in the process.
- `posix_spawn_health_check_thread(...)`, `posix_health_check_thread_proc(...)`, and `posix_fs_health_check(...)` periodically write/read a hidden health-check file using POSIX AIO and bring down or detach the brick when the backend is unhealthy.
- `posix_spawn_disk_space_check_thread(...)` and `posix_disk_space_check(...)` maintain `priv->disk_space_full` based on configured reserve thresholds, using one context-wide checker across registered POSIX xlators.
- `posix_fsyncer(...)` batches fsync requests from `priv->fsyncs`; modes include direct reverse fsync, `syncfs`, `syncfs` plus one fsync, and reverse fsync after `syncfs`.
- `posix_get_objectsignature(...)` and `posix_fdget_objectsignature(...)` fetch bitrot version/signature xattrs and annotate signature size.
- `posix_resolve_dirgfid_to_path(...)` reconstructs a path by walking `.glusterfs` directory handle symlinks from a directory GFID back to root.
- `__posix_inode_ctx_get(...)`, `posix_inode_ctx_get_all(...)`, and unlink flag setters allocate and access per-inode POSIX context containing `xattrop`, atomic-write, pgfid, and unlink state locks.
- `posix_fd_ctx_get(...)` lazily opens anonymous fd contexts from a GFID handle or background-unlink path when a Gluster fd has no POSIX context.
- `posix_cs_check_status(...)`, `posix_cs_heal_state(...)`, `posix_cs_set_state(...)`, and `posix_cs_maintenance(...)` implement cloudsync object state detection and repair from `GF_CS_OBJECT_REMOTE` and `GF_CS_OBJECT_DOWNLOADING` xattrs.
- `posix_set_iatt_in_dict(...)`, `posix_set_mode_in_dict(...)`, `posix_override_umask(...)`, `posix_check_internal_writes(...)`, `posix_check_dev_file(...)`, `posix_update_iatt_buf(...)`, `posix_is_layout_stale(...)`, and `posix_delete_user_xattr(...)` are smaller helpers used by FOP paths for metadata propagation, overwrite protection, cloudsync stat override, stale-layout detection, and xattr cleanup.

Key shared types come from `posix.h`:

- `struct posix_private` stores translator configuration and runtime state: `base_path`, hidden handle directory identity, ctime mode, gfid2path mode, batch fsync settings, janitor/health/disk thread state, disk reserve flags, fd cleanup counters, locks, and condition variables.
- `struct posix_fd` wraps backend fd or `DIR *`, open flags, deferred cleanup list node, owning xlator, and O_DIRECT state.
- `posix_xattr_filler_t` carries the active xattr fill context: translator, path or fd, response dict, stat buffer, loc/fd/inode, listed xattr buffer, and op errno.
- `posix_inode_ctx_t` stores per-inode POSIX locks and unlink state.

## Control Flow

Xattr response flow starts in FOP code with `posix_xattr_fill`. The function creates a response dict, optionally removes the synthetic `list-xattr` request, records path/fd context in a stack `posix_xattr_filler_t`, preloads the backend xattr name list, and runs `_posix_xattr_get_set` for each requested key. Special keys are resolved from memory or by side computations; normal keys are matched against the backend list and fetched with `_posix_xattr_get_set_from_backend`. If `list-xattr` was requested, `_handle_list_xattr` adds visible backend xattrs while suppressing GFID, volume-id, SELinux, marker/quota, geo-replication, and gfid2path internals.

Xattr write flow passes each dict pair through `posix_handle_pair` or `posix_fhandle_pair`. The helpers first enforce Gluster's policy around protected/internal xattrs, handle ACL and metadata xattrs specially, and only then call backend setxattr syscalls. Return values are generally negative errno values for caller-friendly propagation.

Stat flow wraps backend stat syscalls. Path and inode-handle stat paths reject the hidden `.glusterfs` handle directory itself by comparing device/inode with `priv->handledir_st_*`. File link counts are decremented for non-directories because the hidden GFID hardlink should not be visible to clients. When ctime metadata is enabled, the stat helpers overlay metadata xattr values before returning `iatt`.

GFID creation flow in `posix_gfid_set` first checks for an existing `trusted.gfid`. If absent, it extracts `gfid-req`, validates non-null UUID, writes `GFID_XATTR_KEY` with `XATTR_CREATE`, and creates either a hard handle for non-directories or a soft/symlink handle for directories. `posix_gfid_heal` is used during lookup to avoid racing newly created files that have not yet received their intended GFID.

Background maintenance uses two patterns. The trash janitor uses a timer-wheel callback to spawn a synctask, then reschedules itself after completion. The fd janitor and disk-space checker are context-wide pthreads with shared Gluster context lists and counters. Health checks are per translator and use cancellation around sleep/check windows, then notify parent/down or detach the brick on failure.

Cloudsync maintenance locks the inode, reads remote/downloading state xattrs by path or fd, optionally repairs inconsistent combinations by removing `DOWNLOADING` and truncating local content to zero, then records object state and remote value in the xattr response dict.

## State and Persistence Behavior

Persistent state lives mostly in backend files and xattrs:

- `GFID_XATTR_KEY` stores the object GFID on backend entries.
- The `.glusterfs` handle tree stores hardlinks/symlinks that map GFID to backend objects and lets anonymous fd reopen and path reconstruction work.
- Metadata xattrs, including `GF_XATTR_MDATA_KEY`, preserve Gluster ctime/mtime behavior beyond plain POSIX stat fields.
- Quota/marker, geo-replication, bitrot, cloudsync, lock-count, and layout xattrs are selectively hidden, exposed, or transformed depending on caller and request type.
- Health checks persist a hidden `health_check` file under the brick's hidden directory and validate write/read consistency.
- Background unlink may move deleted file data under a hidden unlink path; anonymous fd recovery tries both handle path and unlink path.

Transient state includes `struct posix_private` flags/counters, context-wide janitor/disk lists, fd contexts attached to Gluster `fd_t`, inode contexts attached to `inode_t`, queued fsync `call_stub_t` objects, and thread/timer lifecycle fields. Locking is split across translator locks, inode locks, fd/inode context mutexes, and Gluster context locks.

## Dependencies and Integration Points

This file depends on Gluster core primitives (`dict_t`, `data_t`, `xlator_t`, `inode_t`, `fd_t`, `loc_t`, `call_stub_t`, `synctask`, timer wheel, logging/events, memory accounting, `iatt`, UUID helpers, lock macros) and on POSIX/backend filesystem APIs (`stat`, `statvfs`, xattr syscalls, ACL APIs, `nftw`, pthreads, AIO, `syncfs`/`sync`, truncate, open/read/close).

Major local integration points:

- `posix-entry-ops.c` calls GFID set/heal, xattr fill, stat helpers, stale-layout checks, and inode context helpers around lookup/create/link/rename/unlink paths.
- `posix-inode-fd-ops.c` calls fd context/stat helpers, xattr fill/write helpers, cloudsync maintenance, object signature fetch, fd janitor cleanup, and user xattr deletion.
- `posix-handle.c` provides handle creation/path resolution primitives used by GFID, anonymous fd, janitor, and path reconstruction logic.
- `posix-metadata.c` provides metadata xattr get/set functions used by stat and mdata write paths.
- `posix-common.c` initializes `struct posix_private`, configures batch fsync/health/disk options, spawns helper threads, and cleans their state.
- `posix-aio.c` and `posix-io-uring.c` use `posix_fd_ctx_get` and `posix_fdstat` around asynchronous I/O completion.

The file also defines policy boundaries for other translators: DHT requests mode/link/iatt xdata and stale-layout checks, quota/marker xattrs are filtered and expanded, geo-replication receives selected internal xattrs only for the gsyncd pid, bitrot consumes object signature xattrs, and cloudsync consumes object status/repair responses.

## Risks and Edge Cases

- Xattr filtering is security- and correctness-sensitive. Mistakes can expose internal keys, hide keys needed by higher layers, or incorrectly deny legitimate geo-replication, quota, ACL, bitrot, or cloudsync requests.
- `_posix_xattr_get_set_from_backend` intentionally optimizes for small xattrs, then falls back on ERANGE. Races between listxattr/getxattr or xattr size changes can produce missing values or warnings.
- `posix_gfid_heal` is explicitly described as hacky and timing dependent. Clock skew, ctime metadata behavior, or delayed GFID assignment can cause false ENOENT or wrong GFID healing under lookup/create races.
- Link count adjustment assumes the hidden GFID hardlink should be subtracted for non-directories. Changes to handle layout or backend link behavior can make client-visible link counts wrong.
- Several functions return negative errno values while others return `-1` and set `errno`/`op_errno`; callers must preserve the expected convention.
- Background threads share context-global lists and mutable translator state. Detach/cleanup races are mitigated with locks and condition variables, but thread cancellation, brick multiplexing, and `THIS` manipulation are high-risk areas.
- Health checking uses POSIX AIO and sleeps up to configured timeouts. A slow but recovering backend can trigger child-down/detach/termination behavior; EAGAIN is specially ignored.
- `posix_cs_set_state` assumes the remote xattr exists when asked to include cloudsync state; missing or unreadable remote xattr makes status reporting fail.
- Cloudsync repair truncates files to size zero when remote state says the object is remote. That is intended for stub files but dangerous if xattr state is corrupt.
- `posix_resolve_dirgfid_to_path` parses backend symlink layout strings directly and depends on exact `.glusterfs/xx/yy/gfid` relative-link format.
- `posix_is_layout_stale` mutates the request dict by deleting the checked xattr and parent key, so callers must not reuse those entries afterward.
- ACL handling differs by platform and by whether file descriptor or path APIs can support default ACLs. Non-Linux builds may return ENOTSUP.

## Test Signals

Useful validation signals for this file include:

- Lookup/create race tests where lookup tries to heal a GFID while mkdir/create is concurrently assigning one; expected result is no mismatched GFID across replica/distribute subvolumes.
- Xattr get/list/set/removexattr tests covering internal key filtering, `list-xattr`, geo-replication pid behavior, marker/quota contribution expansion, ACL virtual keys, gfid2path rejection, and `GF_CONTENT_KEY` file-content reads.
- Stat and readdirp tests that verify `iatt` GFID, synthetic inode number, link count adjustment, ctime metadata overlay, and cloudsync stat-size override.
- Trash/landfill janitor tests that remove files/directories, purge the trash path, and verify stale directory handles are removed only when the target is absent or GFID-mismatched.
- Health-check tests that simulate write/read/open/AIO failure and verify events, child-down notification, brick detach under multiplexing, and process termination path without multiplexing.
- Disk reserve tests for both percent and absolute-byte modes, including `DISK_SPACE_CHECK_AND_GOTO` callers returning ENOSPC for client writes but allowing internal FOPs.
- Batched fsync tests for every `batch_fsync_mode`, validating `syncfs` and per-fd fsync ordering and correct stub unwind.
- Bitrot signature tests where signature xattrs are absent, oversized, present, or unreadable; absence should be tolerated while non-absence errors propagate.
- Cloudsync state tests for local, remote, downloading, remote+downloading, remote+nonzero-size repair, response dict contents, and `ignore_failure` behavior.
- Detach/finalization stress tests around deferred fd cleanup, disk-space checker registration, health-check cancellation, and condition variable signaling.
