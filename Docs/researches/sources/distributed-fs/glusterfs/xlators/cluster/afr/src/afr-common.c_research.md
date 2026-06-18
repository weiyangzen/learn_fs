# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-common.c

## Purpose

`afr-common.c` is the central implementation body included by `afr.c` for the AFR/replicate translator. It supplies shared logic for lookup/discover, inode refresh, read-subvolume selection, lock and lease fan-out, lock healing, child notification handling, local/frame cleanup, pending-xattr interpretation, split-brain status, heal-status queries, thin-arbiter coordination, and common quorum/error handling. The file is built into `afr.la` indirectly because `afr.c` includes it.

## Important APIs, functions, and internal types

Major exported/common functions include:

- Quorum/error helpers: `afr_quorum_errno()`, `afr_fill_success_replies()`, `afr_is_consistent_io_possible()`, `afr_is_symmetric_error()`, `afr_higher_errno()`, `afr_final_errno()`, `afr_handle_replies_quorum()`, and `afr_lookup_has_quorum()`.
- Inode/read-state helpers: `__afr_inode_ctx_get()`, `afr_inode_read_subvol_get()`, `afr_inode_get_readable()`, `afr_read_subvol_get()`, `afr_read_subvol_select_by_policy()`, `afr_inode_need_refresh_set()`, `afr_is_inode_refresh_reqd()`, `afr_set_inode_local()`, and write-subvolume helpers `afr_write_subvol_get/set/reset()`.
- Lookup/discover flow: `afr_lookup()`, `afr_lookup_do()`, `afr_lookup_cbk()`, `afr_lookup_entry_heal()`, `afr_lookup_metadata_heal_check()`, `afr_lookup_done()`, `afr_discover()`, `afr_discover_do()`, `afr_discover_cbk()`, and `afr_discover_done()`.
- Refresh and heal coordination: `afr_inode_refresh()`, `afr_inode_refresh_do()`, lookup/fstat refresh callbacks, `afr_replies_interpret()`, `afr_readables_fill()`, `afr_is_pending_set()`, `afr_get_heal_info()`, `afr_is_split_brain()`, `afr_get_split_brain_status()`, and `afr_heal_splitbrain_file()`.
- Locking APIs: `afr_inodelk()`, `afr_finodelk()`, `afr_entrylk()`, `afr_fentrylk()`, `afr_lk()`, serialized/parallel lock callbacks, `afr_lk_transaction()` for mandatory lock healing, lease functions, and lock-heal queue helpers.
- FOP support: `afr_flush()`, `afr_fsyncdir()`, `afr_statfs()`, `afr_ipc()`, `afr_release()`, `afr_forget()`, `afr_priv_dump()`, `afr_local_init()`, `afr_transaction_local_init()`, `afr_local_cleanup()`, and matrix allocation helpers.
- Notification and thin-arbiter support: `afr_notify()`, `__afr_handle_child_up_event()`, `__afr_handle_child_down_event()`, HALO latency selection, upcall handling, `afr_ta_post_op_lock()`, `afr_ta_post_op_unlock()`, `afr_ta_frame_create()`, `afr_ta_has_quorum()`, and `afr_ta_dict_contains_pending_xattr()`.

Important state types are declared in `afr.h`: `afr_private_t` holds child arrays, quorum/arbiter/thin-arbiter state, pending xattr keys, event generation, heal queues, saved lock queues, latency/HALO state, and translator options; `afr_local_t` holds per-FOP snapshots, reply arrays, transaction state, lock state, and xdata; `afr_inode_ctx_t` caches read/write subvolume bitmaps, split-brain choice, lock queues, open-fd counts, refresh flags, and unstable-write state; `afr_fd_ctx_t` tracks per-child fd open state and lock-heal metadata.

## Control flow

Frame setup begins with `AFR_FRAME_INIT`, which calls `afr_local_init()` to snapshot `priv->child_up`, initialize reply arrays, set `call_count`, capture `event_generation`, and allocate per-FOP readable/open state. Most multi-child FOPs wind to each up child and use `afr_frame_return()` as a locked fan-in counter.

Lookup has two paths. Nameless lookups go through `afr_discover()`. Named lookups reject private root entries, prepare xattr requests for pending/lock/link-count information, wind lookup to all up children, and collect replies in `afr_lookup_cbk()`. Once all replies arrive, AFR may launch name self-heal or metadata self-heal, interprets pending xattrs into readable data/metadata bitmaps, checks GFID/type mismatch, applies quorum rules, avoids arbiter read selection, and unwinds the chosen child reply. Fresh lookup is forced with `ESTALE` when lower layers report `gfid-changed`.

Inode refresh is a lookup/fstat pass over all usable child subvolumes. It requests AFR pending xattrs, dirty xattrs, link count, and inodelk counts. `afr_readables_fill()` marks accused children from pending vectors, excludes arbiter from read candidates, optionally accuses smaller files when no data transaction appears active, and updates inode read bitmaps. If refresh detects healable divergence and self-heal is enabled, it schedules `afr_throttled_selfheal()`.

Read-subvolume selection first uses cached inode bitmaps. It prefers configured `read_child`, then policies based on GFID hash, GFID+PID hash, least pending reads, least latency, or latency multiplied by pending reads, and finally the first readable child. When data and metadata readable sets intersect, AFR prefers the intersection to avoid mixing content from one child with metadata from another.

Lock operations use two strategies. Inode/entry locks first try parallel nonblocking acquisition; on contention they release partial locks and retry serialized to avoid two clients each holding partial locks. `afr_lk()` for POSIX byte-range locks walks children serially, tracks `locked_nodes`, honors quorum, and unlocks on failure. Mandatory lock mode uses `afr_lk_transaction()` with a domain lock (`AFR_LK_HEAL_DOM`) and saved lock records so locks can be healed when a child returns.

Notification flow aggregates child up/down/connecting/ping/upcall events. `afr_notify()` updates `child_up`, `last_event`, `event_generation`, quorum transitions, and HALO latency decisions under `priv->lock`; it only propagates selected events upward to avoid exposing every child transition. Child-up schedules pending lock heal and self-heal; child-down marks saved locks for healing or invalidates fds if quorum was lost.

Thin-arbiter flow uses a special child index and lock domains `AFR_TA_DOM_NOTIFY` and `AFR_TA_DOM_MODIFY`. Clients hold notify-domain locks as a notification mechanism; self-heal daemon contention can trigger clients to release after in-memory/on-wire transactions finish. Thin-arbiter quorum allows two data bricks, or one data brick plus the thin arbiter.

## State and persistence behavior

Persistent correctness state is primarily stored in per-child AFR pending xattrs (`priv->pending_key[]`) and dirty xattrs (`AFR_DIRTY`). `afr_mark_pending_changelog()` constructs data/metadata/entry changelog matrices for on-disk pending state. `afr_replies_interpret()` reads those xattrs back and caches readable sets in `afr_inode_ctx_t`.

In-memory persistence includes inode ctxs attached to Gluster inode objects, fd ctxs attached to fds, `priv->event_generation`, child health arrays, saved lock queues, lock-heal queues, split-brain choice timers, and thin-arbiter lock offsets. `afr_forget()` destroys inode ctx state, including split-brain choice timers. `afr_release()` destroys fd ctx state and removes saved lock records. `afr_priv_destroy()` frees translator private arrays and lock resources.

Split-brain choice is temporarily persisted in inode ctx as `spb_choice` with a timer controlled by `priv->spb_choice_timeout`; expiry invalidates the inode and clears the choice. HALO latency state persists in `priv->child_latency` and `priv->halo_child_up` while the translator is alive.

## Dependencies and integration points

The file depends on `afr.h`, AFR operation headers, self-heal headers, transaction helpers, lock helpers, libglusterfs dictionaries/lists/statedump/events/upcall APIs, syncop/synctask APIs, Gluster call-frame/stack macros, inode/fd ctx APIs, and child translator FOP tables. It calls functions defined in sibling files such as `afr_has_quorum()` and thin-arbiter loc helpers from `afr-transaction.c`, `afr_locked_nodes_count()` from `afr-lk-common.c`, self-heal routines from `afr-self-heal-*`, read helpers from `afr-inode-read.c`, and quota handling from inode-read code.

Build integration is unusual: `xlators/cluster/afr/src/Makefile.am` lists `afr-common.c` as `noinst_HEADERS`, and `afr.c` includes it directly. This gives the file access to static/private AFR symbols in one translation unit but means duplicate compilation would create symbol conflicts.

Runtime integration points include child storage/protocol translators via `STACK_WIND`, parent translators via `AFR_STACK_UNWIND` and `default_notify`, self-heal daemon synctasks, md-cache invalidation via upcalls, statedump via `afr_priv_dump()`, and NFS/client behavior through read-child and consistency options.

## Risks and edge cases

- Many code paths depend on correctly paired dict refs/unrefs, inode/fd refs, and `AFR_STACK_DESTROY`; leaks or use-after-free bugs are plausible around async self-heal, timers, and error exits.
- `event_generation` is central to consistency checks. Missing an increment or comparing stale local snapshots can either reject valid I/O with `ENOTCONN` or allow stale reads.
- Readable bitmaps are packed into 16-bit fields for child counts <= 16; larger replica counts are explicitly unsupported in those helpers.
- Lock healing supports only replica-3 non-arbiter volumes in `afr_lk_transaction()`. Other layouts return `ENOTSUP`.
- Partial lock recovery is complex: parallel lock contention, serialized retry, quorum failure, and unlock failure logging must preserve POSIX expectations and avoid leaving locks behind.
- Lookup GFID mismatch handling intentionally tolerates some in-flight transactions but fails with `EIO` when mismatch cannot be explained. This path is sensitive to pending xattr accuracy.
- Arbiter and thin-arbiter children must not be selected for normal reads; several paths explicitly filter them, and regressions can return invalid size/content.
- HALO can mark high-latency children down or swap children to satisfy min/max replica constraints; bad latency inputs can change availability decisions.
- Some helpers use `alloca0(priv->child_count)` heavily; unexpected large child counts could create stack pressure.
- Error priority (`ENODATA > ENOENT > ESTALE > ENOSPC > other`) affects user-visible behavior and repair decisions.

## Test signals

High-value tests include AFR lookup under GFID mismatch, pending entry heal, in-flight create/unlink/rename, data and metadata split-brain, root private-directory filtering, arbiter read exclusion, read policy selection, refresh after child up/down, md-cache invalidation when pending xattrs appear, quorum loss/recovery, HALO latency threshold behavior, mandatory lock healing across child down/up, partial lock cleanup after `EAGAIN`/`EINTR`, POSIX `lk` quorum failure, lease unlock cleanup, thin-arbiter notify/modify lock contention, split-brain choice timeout, fd-bad behavior after lost lock quorum, and cleanup paths under allocation failures. Build tests must also confirm `afr-common.c` remains included only through `afr.c`.
