# sources/distributed-fs/ceph/src/mds/Server.cc lines 7834-12486

## Scope and Purpose

This chunk is the tail of CephFS MDS `Server.cc`. It implements metadata mutations and snapshot-diff style read operations after the earlier path-resolution and create/open logic: hard link completion, unlink/rmdir, rename, peer prepare/commit/rollback protocols, snapshot listing and mutation, block diff, readdir snapdiff, and reconnect status helpers.

The code is centered on making client-visible POSIX namespace changes durable through MDS journal entries (`EUpdate`, `EPeerUpdate`) while preserving consistency across multiple authoritative MDS ranks. Most client operations follow the same pattern: validate and lock dentries/inodes, prepare projected dentry/inode/snaprealm state, journal the prepared state, apply projections in a log callback, notify peers/clients/cache subsystems, and respond to the client. Distributed mutations add a peer prepare/ack/commit or rollback protocol with explicit rollback blobs.

## Important APIs, Types, and Functions

- Link paths:
  - `_link_local()` and `_link_local_finish()` create a new remote dentry for a hard link to an auth inode, increment `nlink`, update `ctime`, `rstat.rctime`, `change_attr`, handle global snaprealm splitting, journal parent/inode dirties, then apply and notify dentry link watchers.
  - `_link_remote()` and `_link_remote_finish()` handle hard-link increment and remote unlink decrement when the target inode is authoritative on another MDS. They send `MMDSPeerRequest::OP_LINKPREP` or `OP_UNLINKPREP`, record `witnessed` peers, journal local dentry changes with `had_peers`, and commit after peer acks.
  - `handle_peer_link_prep()`, `_logged_peer_link()`, `_commit_peer_link()`, `_committed_peer()`, `do_link_rollback()`, and `_link_rollback_finish()` implement the peer side and rollback for remote link/unlink nlink changes.

- Unlink and rmdir:
  - `handle_client_unlink()` branches between unlink and rmdir, validates directory/non-directory semantics, checks permissions, prepares stray dentries for primary-link removal, locks link/snap/file/stray state, prepares snaprealm handoff blobs, gathers rmdir witnesses for subtree-root directories, and dispatches to `_link_remote(..., false, ...)` or `_unlink_local()`.
  - `_unlink_local()` projects the dentry to null, decrements inode `nlink`, records `stray_prior_path`, marks zero-link inodes orphaned, moves primary links to stray dentries when needed, journals cow/null dentries, and projects subtree renames for directories.
  - `_unlink_local_finish()` pops projected linkages, applies inode/fnode changes, sends unlink notifications, adjusts subtree and snaprealm state, responds, removes unlinked dentries, and notifies stray purge logic.
  - `_rmdir_prepare_witness()`, `handle_peer_rmdir_prep()`, `_logged_peer_rmdir()`, `handle_peer_rmdir_prep_ack()`, `_commit_peer_rmdir()`, `do_rmdir_rollback()`, and `_rmdir_rollback_finish()` provide distributed rmdir witness, journal, commit, and rollback behavior for auth subtree dirfrags.
  - `_dir_is_nonempty_unlocked()`, `_dir_has_snaps()`, and `_dir_is_nonempty()` are validation helpers for rmdir and rename-over-directory checks.

- Rename:
  - `handle_client_rename()` is the leader-side rename state machine. It validates dot/dotdot, alternate names, source/destination type compatibility, no self-descendant moves, stray migration constraints, common-ancestor traces, link-merge cases, cross-subvolume snaprealm rules, permissions, fragmentation limits, and directory emptiness. It prepares stray dentries, locks involved inodes and dentries, opens remote directory frags when necessary, builds snaprealm updates, computes witnesses, flushes projected dentries before peer prepares, sends `OP_RENAMEPREP` to peers, then journals `_rename_prepare()` and completes through `_rename_finish()`.
  - `_rename_prepare_witness()` encodes source/destination traces, alternate name, stray info, snaprealm blobs, source auth rank, witness set, and op stamp into peer prepare messages.
  - `_rename_prepare_import()` decodes imported inode/capability state from peer acks and stages force-open sessions and migrated cap state.
  - `_need_force_journal()` detects when rename must force-journal a destination or stray dentry because local auth subtree dirfrags need replayable subtree metadata.
  - `_rename_prepare()` is the shared projection and journal builder for leader and peer rename. It handles primary/remote link variants, link merge, silent stray reintegration, destination overwrite to stray, inode import/export projections, snaprealm projections, nlink/ctime/change_attr updates, parent fnode accounting, `EMetaBlob` dentry records, forced subtree journaling, corruption injection for dentry `first`, and `project_subtree_rename()`.
  - `_rename_apply()` applies the projected namespace changes after journaling: unlink old destination/source entries, pop projected linkages, link remote or primary destination, finish inode import/cap transfer, mark dirty versions, apply mutation projections, update subtree maps, issue snaprealm invalidation, and remove unlinked source dentries.
  - `handle_peer_rename_prep()`, `_logged_peer_rename()`, `_commit_peer_rename()`, `do_rename_rollback()`, `_rename_rollback_finish()`, `handle_peer_rename_prep_ack()`, `handle_peer_rename_notify_ack()`, and `_peer_rename_sessions_flushed()` implement peer-side prepare, ambiguity/freeze handling, session flushing, inode export/import, prepare ack expansion for insufficient witnesses, commit, abort rollback, and cleanup.
  - `_rollback_repair_dir()` repairs projected fnode accounting for rollback.

- Snapshot operations:
  - `handle_client_lssnap()` reads a directory's `SnapRealm`, encodes snapshot dentries with leases and inode stats, honors max entry/byte limits, and sets readdir completion flags.
  - `handle_client_mksnap()` validates snapshot feature enablement, UID bounds, directory/system-dir rules, subvolume restrictions, name and count limits, obtains a snap table transaction from `snapclient`, projects inode and snaprealm creation state, journals `TABLE_SNAP`, and finishes in `_mksnap_finish()`.
  - `handle_client_rmsnap()` validates name/existence/access, obtains snap destroy transaction state, projects snaprealm deletion and inode stat updates, journals `TABLE_SNAP`, and finishes in `_rmsnap_finish()` with stale snap-data purge.
  - `handle_client_renamesnap()` validates same parent directory, source/destination names, access, prepares snap update transaction state, changes `SnapInfo::name`, journals, and finishes in `_renamesnap_finish()`.

- Diff/read helpers:
  - `handle_client_file_blockdiff()` resolves two file paths, validates regular files, handles identical inodes as no-diff, and delegates object diff scanning to `mdcache->file_blockdiff()`. `handle_file_blockdiff_finish()` encodes `BlockDiff` into reply extra data.
  - `handle_client_readdir_snapdiff()` resolves and locks an auth directory, throttles on high cap acquisition, adjusts requested dirfrag/hash cursor, opens/fetches complete dirfrag data, validates snapshot ids, encodes directory stat, budgets reply bytes, and delegates to `_readdir_diff()`.
  - `_readdir_diff()` builds a bounded directory diff response between two snap ids, preserving hash-order flags and rollback points for same-name entries that do not fit in the response.
  - `build_snap_diff()` walks dentries, skips purging/out-of-range entries, opens remote dentries when needed, distinguishes deleted/new/unchanged/modified files and directories across snap ranges, and calls a result callback with existence state.
  - `get_snap_trace()` selects old or new snaprealm trace encoding based on client feature bits.
  - `waiting_for_reconnect()` and `dump_reconnect_status()` expose reconnect gather state.

## Control Flow and Distributed Protocols

Local mutations generally do:

1. Traverse/auth-pin dentries and inodes through earlier helpers.
2. Validate operation-specific semantic constraints and access.
3. Acquire `MutationImpl::LockOpVec` locks, often `linklock`, `snaplock`, `filelock`, `nestlock`, and dentry xlocks.
4. Project inode, dentry, fnode, and snaprealm changes in memory.
5. Build an `EUpdate` metablob with client request identity and dirty dentry/inode/parent records.
6. Submit to `mdlog` through `journal_and_reply()` or `submit_mdlog_entry()`.
7. In the log callback, pop/apply projections, mark dirties, update subtree/snaprealm/cache state, send dentry/snap notifications, then respond.

Peer-assisted mutations add a two-phase protocol:

- The leader sends an `MMDSPeerRequest` prepare message and inserts the peer in `waiting_on_peer`.
- The peer journals an `EPeerUpdate::OP_PREPARE` when local replay state is required, stores rollback data, applies projected state, and replies with `OP_*PREPACK`. Some peer paths may mark replies as not journaled when no metablob is needed.
- The leader resumes the client request after all peers are witnessed, records `had_peers` in its own journal entry, and later commits or aborts peers through the stored `peer_commit` context.
- Peers commit with `EPeerUpdate::OP_COMMIT` and notify the leader with `OP_COMMITTED`; on failure they call the operation-specific rollback routine and finish rollback before resolve can proceed.

Rename has the most complex control flow. The destination dentry auth MDS acts as leader so cached inodes stay connected. It may need all replicas of source/destination/stray dentries as witnesses; source dentry auth is prepared last to handle ambiguous auth and inode export. When source primary auth moves to destination auth, the peer exports inode/cap state in `inode_export`; the leader imports that state in `_rename_prepare_import()` and `_rename_apply()`. The peer may return an expanded witness list instead of a normal witnessed ack, causing the leader to retry with additional witnesses.

## State and Persistence Behavior

- Dentry linkage state is staged with `push_projected_linkage()` and made real with `pop_projected_linkage()`, `link_remote()`, `unlink_inode()`, `mark_dirty()`, and `touch_dentry_bottom()`.
- Inode state is staged through `project_inode()`, `pre_dirty()`, and projected `mempool_inode` fields. Mutations update `nlink`, `ctime`, recursive stat timestamps, `change_attr`, versions, `stray_prior_path`, orphan state, and backtraces.
- Directory fnode and recursive accounting are adjusted through `predirty_journal_parents()`, `project_fnode()`, `_rollback_repair_dir()`, and `mut->add_updated_lock()` for file/nest locks.
- Snaprealm state is projected through `project_snaprealm()`, `prepare_new_srnode()`, `record_snaprealm_parent_dentry()`, `record_snaprealm_past_parent()`, `mark_snaprealm_global()`, `clear_snaprealm_global()`, encoded into peer request snap blobs, and invalidated/notified with `send_snap_update()`, `do_realm_invalidate_and_update_notify()`, `send_snaps()`, or `prepare_realm_merge()`.
- Persistent journal records are `EUpdate` for leader/local client operations and `EPeerUpdate` for peer prepare/commit/rollback. They include client request ids, oldest client tids, table transaction ids, rollback blobs, renamed directory inode/frags, and metablobs describing dentry/inode/dir state needed for replay.
- Rollback blobs preserve enough old state to undo peer-side changes: link rollback stores old inode ctime, dir mtimes/rctimes, nlink direction, and optional snap blob; rmdir rollback stores source/destination dentry locations and optional snap blob; rename rollback stores source/destination/stray dentry records, old directory times, old ctimes, snap blobs, and dentry linkage identifiers.
- Snapshot create/remove/rename are coupled to the snap table through `snapclient->prepare_*()` and `snapclient->commit()`, with `TABLE_SNAP` transactions recorded in the metadata journal.

## Dependencies and Integration Points

- `MDRequestRef` carries client or peer request state, request ids, op stamps, paths, locks, projected value maps, rollback blobs, witness/peer sets, import/export buffers, snap ids, and reply buffers.
- `MDSRank` services are used for session lookup, mdsmap feature/epoch checks, sending peer messages, waiting for active peers/maps, timers, queueing waiters, and snapclient table operations.
- `MDCache` supplies inode/dentry/dirfrag lookup, path traversal, journal metablob helpers, subtree rename projection/application, peer uncommitted tracking, rollback tracking, stray handling, snap update notifications, remote dentry opening, lru touches, and blockdiff/snapdiff helpers.
- `Locker` is responsible for metadata locks, snap layout locks, cap/lease encoding, client lease issuance, lock cache creation, imported/exported xlock repair, and eval after cap imports.
- `Migrator` integrates with rename auth transfer by encoding/decoding inode export, finishing imported/exported caps, gathering export clients, and forcing sessions open.
- `MMDSPeerRequest` encodes cross-MDS prepare/ack/commit traffic for link/unlink, rmdir, and rename, including paths, snap blobs, alternate names, witness sets, stray blobs, inode export blobs, and status flags.
- `EMetaBlob`, `EUpdate`, and `EPeerUpdate` are the journal substrate that make namespace changes replayable.
- `SnapRealm`, `SnapInfo`, `SnapPayload`, `sr_t`, and `TABLE_SNAP` connect namespace mutations to snapshot isolation and client-visible snapshot directories.
- `Session` and client feature flags influence snap trace format, cap throttling, lease/stat encoding, and forced session flushing.

## Risks and Edge Cases

- Distributed operations rely on exact ordering of peer prepare, local journal, peer commit, and rollback. Missing a `waiting_on_peer` transition or incorrect `witnessed` bookkeeping can leave uncommitted peer updates or double-apply rollback.
- Rename is highly sensitive to auth ownership and witness completeness. Insufficient witness sets are dynamically expanded; failures in that path can leave ambiguous auth/frozen inode state that must be cleaned by `_commit_peer_rename()` or `_rename_rollback_finish()`.
- Snaprealm transitions are interleaved with link/unlink/rename. Incorrect projection or rollback of `sr_t` blobs can break snapshot visibility, global snaprealm parentage, or cap snap notifications.
- Rmdir and rename-over-directory use fast unlocked emptiness checks followed by locked checks. The fast path can only reject obvious non-empty directories; correctness depends on later `filelock` validation.
- Stray dentries are used for primary-link deletion and overwritten rename targets. Races are explicitly noted after `respond_to_request()` drops locks, so `notify_stray()` is conditional on the stray still being linked.
- Peer paths sometimes skip journaling when the local metablob is empty. Callers must honor `is_not_journaled()` so commit/rollback cleanup does not assume a journaled peer update exists.
- `do_rename_rollback()` intentionally avoids `is_auth()` during resolve and uses authority ranks directly. Resolve-mode behavior is fragile if required dirfrags/dentries were trimmed or not discoverable.
- Reply byte budgeting in `lssnap`, blockdiff, and snapdiff must avoid partial/inconsistent entries. `_readdir_diff()` has explicit rollback logic for same-name snapshot entries that would otherwise split across fragments.
- Remote dentry resolution during snapdiff may issue leases/caps before discovering missing remote inode state; the code either opens remote dentry asynchronously and returns a partial reply or drops locks and retries when no entries were emitted.
- Fault-injection assertions (`mds_kill_link_at`, `mds_kill_rename_at`, `inject_rename_corrupt_dentry_first`) indicate intentionally tested crash windows. Production changes around those points need replay/rollback coverage.

## Test Signals

- Hard link tests should cover local auth targets, remote auth targets, cross-subvolume rejection (`-EXDEV`), no-link target rejection, alternate name length, snaprealm global split, and replay through `link_local`/`link_remote` journal events.
- Unlink/rmdir tests should cover file unlink, directory unlink rejection (`-EISDIR`), rmdir non-dir rejection (`-ENOTDIR`), empty/non-empty directory checks, primary-link move to stray, remote unlink prepare, subtree-root rmdir witnesses, and rollback after peer failure.
- Rename tests should cover no-op same dentry, self-descendant rejection, type mismatch over existing destination, alternate-name mismatch, link merge from stray, overwrite to stray, remote source auth import/export, expanded witness retry, forced journal for nested auth subtrees, cross-subvolume rejection, and crash/replay at `mds_kill_rename_at` points.
- Snapshot tests should cover disabled snapshots, UID min/max enforcement, invalid names, duplicate names, per-directory snapshot limit, subvolume descendant rejection, create/remove/rename journal table commits, snap update notification, stale snap-data purge, and lssnap pagination/byte limits.
- Snapdiff and blockdiff tests should cover invalid snap ids, cap acquisition throttling, dirfrag cursor adjustment, incomplete/frozen dirfrag retry, remote dentry opening during diff, same-file no-op blockdiff, byte-limited responses, same-name rollback behavior, and feature-dependent snap trace encoding.
- Recovery tests should verify `EPeerUpdate` prepare/commit/rollback replay, `mdcache->add_uncommitted_*` cleanup, `finish_rollback()`, resolve-mode subtree trimming, snaprealm rollback, and ambiguous-auth cleanup after aborted peer rename.
