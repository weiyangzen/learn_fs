# sources/distributed-fs/moosefs/mfsmaster/sessions.c

## Purpose
`sessions.c` owns MooseFS master client session records. It creates and changes sessions, tracks connection/disconnection and close state, stores export/root/UID/GID/trash/storage-class limits, exposes session info/statistics packets, expires sustained disconnected sessions, and persists session metadata.

## Important APIs, Types, And Functions
The private `session` struct contains session id, export checksum, client info string, peer IP, close/disconnect/socket counters, mount flags, umask, allowed storage-class groups, trash-retention limits, root and map-all identities, disabled operation mask, root inode, info peer/version, and four operation-stat arrays.

The exported lifecycle APIs are `sessions_new_session()`, `sessions_chg_session()`, `sessions_attach_session()`, `sessions_close_session()`, `sessions_disconnection()`, `sessions_force_remove()`, and `sessions_find_session()`. Metadata replay APIs are `sessions_mr_sesadd()`, `sessions_mr_seschanged()`, `sessions_mr_sesdel()`, `sessions_mr_connected()`, `sessions_mr_disconnected()`, and deprecated `sessions_mr_session()`.

Query/enforcement APIs include session id/export/root/flag/umask/disables getters, `sessions_check_sclass()`, `sessions_check_trashretention()`, `sessions_is_root_remapped()`, and `sessions_ugid_remap()`. Reporting APIs include `sessions_datasize()`, `sessions_datafill()`, `sessions_inc_stats()`, `sessions_add_stats()`, and `sessions_info()`.

## Control Flow
New sessions are allocated by `sessions_create_session()`, assigned `nextsessionid` below `0x80000000`, trimmed of trailing NUL bytes in the info field, inserted into a 256-bucket hash, and changelogged as `SESADD` unless created during metadata restore.

Session changes compare all meaningful fields with `sessions_not_changed()`. Real changes update the record, replace the info string, and changelog `SESCHANGED` unless running as metarestore.

Connection attach increments `nsocks`, updates info peer/version, clears disconnection timestamp, and changelogs `SESCONNECTED` when reconnecting. Disconnection decrements `nsocks`; when it reaches zero, it records `main_time()` and changelogs `SESDISCONNECTED`. Close marks a one-socket session as closed so expiration can remove it.

Periodic `sessions_check()` waits until master uptime exceeds two minutes, then removes sessions with no sockets that are closed or disconnected longer than `SESSION_SUSTAIN_TIME`. Removal notifies open-file code through `of_session_removed()` and changelogs `SESDEL`.

## State, Persistence, And Dependencies
Runtime state is `sessionshashtab[256]`, `nextsessionid`, and `SessionSustainTime`. Session statistics are explicitly not stored in current metadata.

`sessions_store()` writes `nextsessionid`, zero stats count, then one 61-byte record plus info bytes for each non-closed session, terminated by a zero session id record. `sessions_load()` reads multiple metadata versions, converting older min/max goal fields to `sclassgroups`, absent export checksums/disables/umasks to defaults, and old disconnected semantics to current timestamps.

`sessions_import_data()` imports legacy `sessions.mfs` files with several signatures and older record layouts. `sessions_reload()` clamps `SESSION_SUSTAIN_TIME` to one minute through one week.

Dependencies include `filesystem.h` for path reporting, `openfiles.h` for cleanup and opened-file counts, `storageclass.h` for export-group checks, `changelog.h`, `metadata.h`, `datapack.h`, `cfg.h`, `main.h`, socket IP formatting, and logging/assertions.

## Integration Points
Client mount/login paths create, attach, change, and disconnect sessions. Filesystem permission code calls UID/GID remapping, root/session flags, storage-class permission, trash-retention permission, and disables checks. Open-file cleanup is notified when sessions are removed. `restore.c` maps `SES*` changelog entries into the metadata replay functions. Master info and admin packet code use `sessions_datasize()`/`sessions_datafill()`.

## Risks
The header declares several open-file-related functions that are not implemented in this file, suggesting stale API drift.

`sessions_not_changed()` calls `memcmp(sesdata->info, info, ileng)` after checking nullness. With `ileng == 0` and both pointers NULL this is usually harmless in C libraries, but it is still a sensitive pattern for sanitizers.

`sessions_mr_sesadd()` creates a session before checking that the generated id equals the changelog id. A mismatch returns an error after mutation, relying on restore abort semantics.

Session id wrap skips the high bit range. Tests should include wrap and collision assumptions, although the code does not search for existing ids on wrap.

## Test Signals
Tests should cover session create/change/no-change, attach/disconnect reconnect changelog behavior, close and timed expiration, forced removal active versus inactive, store/load across supported metadata versions, import of legacy `sessions.mfs`, operation-stat shifts, UID/GID remapping, storage-class group permission, trash-retention bounds, and admin packet size/data agreement for all `vmode` variants.
