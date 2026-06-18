# Research Report: subset-b-006914

Work item `subset-b-006914` covers Ceph MDS cache, journal, daemon, auth-capability, context, continuation, cache-object, and map code under `sources/distributed-fs/ceph/src/mds`. Each file section is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDCache.h -->
# sources/distributed-fs/ceph/src/mds/MDCache.h

## Purpose

`MDCache.h` declares `MDCache`, the central in-memory metadata cache controller for a Ceph MDS rank. It owns inode and dirfrag lookup tables, subtree authority state, request tracking, cache trim policy, replay/rejoin/resolve state, strays, open-file tracking, file-size recovery, directory fragmentation, snaprealm coordination, replica/discovery messaging, and admin operations such as cache dumps, scrub enqueue, quiesce, path locking, and forced read-only mode. The header is the contract that ties together `CInode`, `CDentry`, `CDir`, `Locker`, `Migrator`, `MDLog`, `StrayManager`, `OpenFileTable`, `RecoveryQueue`, and the MDS peer protocol.

## Important APIs, Types, And State

The public API is grouped by subsystem. Discovery uses `discover_info_t`, `_create_discover`, `_send_discover`, `discover_base_ino`, `discover_dir_frag`, `discover_path`, and `kick_discovers`. Subtree authority management uses `adjust_subtree_auth`, `adjust_bounded_subtree_auth`, `try_subtree_merge`, `eval_subtree_root`, `get_subtree_bounds`, `project_subtree_rename`, `adjust_subtree_after_rename`, and summary helpers such as `get_auth_subtrees`.

Request handling exposes `request_start`, `request_start_peer`, `request_start_internal`, `request_finish`, `request_forward`, `dispatch_request`, `request_cleanup`, and `request_kill`, backed by `active_requests`. Mutation and journal helpers include `pick_inode_snap`, `cow_inode`, `journal_cow_dentry`, `journal_dirty_inode`, `project_rstat_*`, `broadcast_quota_to_client`, and `predirty_journal_parents`.

Recovery coordination is represented by `uleader`, `upeer`, `uncommitted_leaders`, `uncommitted_peers`, `ambiguous_peer_updates`, ambiguous import maps, `resolve_*` methods, and rejoin state such as `rejoin_gather`, `rejoin_imported_caps`, `cap_exports`, `cap_imports`, `rejoin_undef_inodes`, and `rejoin_done`. Path and object loading use `path_traverse`, `maybe_request_forward_to_auth`, `cache_traverse`, `open_remote_dirfrag`, `open_remote_dentry`, `open_ino`, `find_ino_peers`, and peer handlers for open/find replies.

Cache lifecycle includes `trim`, `trim_non_auth_subtree`, `standby_trim_segment`, `expire_recursive`, `trim_client_leases`, `check_memory_usage`, `shutdown_start`, `shutdown_check`, `shutdown_pass`, `shutdown`, and `shutdown_export_strays`. In-memory state includes `inode_map`, `snap_inode_map`, `root`, `myin`, `strays`, `subtrees`, `base_inodes`, `lru`, `bottom_lru`, memory thresholds, `Filer`, `OpenFileTable`, `StrayManager`, `RecoveryQueue`, `global_snaprealm`, `uncommitted_fragments`, `fragments`, and an upkeep thread.

## Control Flow And Persistence Behavior

`MDCache` is not a persistence format itself; it orchestrates when metadata changes become persistent through `MDLog`, `EMetaBlob`, inode/dirfrag store operations, purge queue work, and journaled segment references. Requests enter through `request_start*`, traverse paths with `path_traverse`, acquire locks/auth pins elsewhere, dirty or COW metadata with journal helpers, then finish through request cleanup and journal callbacks. Replay and rejoin rebuild cache and capability state from journal events and peer messages; ambiguous imports, uncommitted peer updates, and uncommitted fragments are retained until resolve/rejoin can prove the final authority and namespace state.

The cache open path initializes layouts, system inodes, root, `.ceph/mds*` hierarchy, stray dirs, and snaprealms. Shutdown is phased: stop or cap logging, trim, export strays, terminate sessions, journal subtree state, trim all possible segments, drop strays and system inodes, and wait for subtrees to empty. Directory fragmentation keeps rollback and old-frag state in `ufragment` and `fragment_info_t`; persistence depends on journaled fragment events plus follow-up store/purge completions.

## Dependencies And Integration Points

This header depends directly on MDS object types (`CInode`, `CDentry`, `CDir`), message types (`MDiscover`, `MMDSResolve`, `MMDSCacheRejoin`, `MMDSOpenIno`, `MCacheExpire`, `MDirUpdate`, fragment messages), `MDSContext`, `LogSegmentRef`, `Filer`, `RecoveryQueue`, `StrayManager`, and `OpenFileTable`. `MDLog` calls `create_subtree_map`, `advance_stray`, `standby_trim_segment`, and trim helpers. `MDSDaemon` and `MDSRankDispatcher` indirectly drive map handling, shutdown, and admin socket commands. `Locker`, `Migrator`, `MDBalancer`, event classes, and fragment context classes are friends because they need access to internal maps during replay, migration, locking, and journal event processing.

## Risks And Test Signals

The largest risks are state-machine coupling and lifecycle ordering: a wrong `MDSContext` completion can leave waiters pinned, a missed uncommitted-peer entry can trim or delete namespace state before commit, and a fragment or import rollback bug can corrupt subtree authority. Cache trim must avoid referenced dentries/inodes and must send correct expire messages to authoritative peers. Memory thresholds and upkeep thread behavior need tests for both ordinary trim pressure and read-only mode. Test signals should include multi-MDS failover/rejoin, standby replay, import/export interruption, fragmented directory split/merge rollback, strays purge after unlink/rename, cap reconnect, journal replay after crash at each shutdown and fragment killpoint, path traversal with forwarding/discovery, and admin operations such as `cache drop`, `dump cache`, `quiesce path`, and `lock path`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDCache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDLog.cc -->
# sources/distributed-fs/ceph/src/mds/MDLog.cc

## Purpose

`MDLog.cc` implements the MDS journal manager declared in `MDLog.h`. It creates and recovers `Journaler` instances, queues and submits `LogEvent` objects, tracks log segments and major segment boundaries, replays events into `MDSRank`/`MDCache`, trims expired segments, reformats older journals, and maintains perf counters for journal positions and event/segment counts.

## Important Functions And Control Flow

Construction reads runtime config such as `mds_debug_subtrees`, `mds_log_events_per_segment`, `mds_log_max_segments`, `mds_log_max_events`, skip-corrupt flags, and trim decay; it starts `log_trim_upkeep`. `create_logger` registers counters for submitted, replayed, large, expiring, expired, trimmed events/segments and read/write/expire positions. `create` initializes a fresh journal inode, writes the journal head and `JournalPointer`, makes the journal writeable, and starts the submit thread. `open` starts the recovery thread and submit thread; `reopen` repeats recovery and then appends.

`submit_entry` locks `submit_mutex`, calls `_submit_entry`, performs `_segment_upkeep`, and wakes `_submit_thread`. `_submit_entry` increments `event_seq`, starts segments for `SegmentBoundary` events, updates touched inode `last_journaled`, associates the event with the current `LogSegment`, stamps it, snapshots up MDS feature bits, and appends it to `pending_events`. `_submit_thread` encodes each event with a header, appends to `Journaler`, updates segment offsets/end, registers a `MDSLogContextBase` flush callback, optionally flushes, and deletes the event.

Replay begins in `replay`; if the journal is non-empty it starts `_replay_thread`. `_replay_thread` loops over readable journal entries, decodes `LogEvent`s, reconstructs segment boundaries, requires a major segment before applying bounded events unless `mds_log_skip_unbounded_events` allows skipping, updates counters and segment end offsets, and calls `le->replay(mds)` under `mds_lock`. Corrupt entries either skip or damage the MDS depending on `mds_log_skip_corrupt_events`.

## State And Persistence Behavior

Persistent state is the RADOS journal plus `JournalPointer`; in-memory state mirrors it through `journaler`, `segments`, `major_segments`, `event_seq`, `num_events`, `safe_pos`, pending submit queues, and expiring/expired segment sets. `MDSLogContextBase` callbacks update `safe_pos` only after completion code runs. `write_head` persists journal expire position and queues `waiting_for_expire` callbacks until the head commit proves the expire position durable. `_reformat_journal` rewrites old journal streams into a new back journal, rewrites segment references in metablobs where necessary, zeros subtree-map `expire_pos`, atomically flips `JournalPointer`, erases the old journal, and resets the active `Journaler`.

Trim is conservative: `trim` only considers flushed segments (`safe_pos` beyond segment end and no pending events), asks each `LogSegment` to expire referenced objects through `try_expire`, moves them through `expiring_segments` to `expired_segments`, and only erases old segments up to a later major segment in `_trim_expired_segments`. `standby_trim_segments` follows another rank's `expire_pos` and drops expired standby segments while keeping at least one segment.

## Dependencies And Integration Points

The implementation depends on `MDSRank`, `MDCache`, `MDSContext`, `LogEvent`, `Journaler`, `JournalPointer`, and event types such as `ESubtreeMap`, `ESegment`, and `ELid`. It calls into `MDCache` for subtree maps, open-file-table commits, stray advancement, standby segment trimming, and cache trimming after replay. It reports severe write/recover errors by respawning or damaging the rank through `MDSRank`.

## Risks And Test Signals

Key risks are journal-ordering bugs, safe-position races, segment-boundary corruption, old-format rewrite mistakes, and deadlocks during shutdown or callbacks under `mds_lock`. Tests should crash around segment creation, event flush completion, journal head writes, trim expiry callbacks, `JournalPointer` front/back swaps, and standby replay while an active rank trims or rewrites the journal. Perf counters and `dump_replay_status` are operational signals; `is_trim_slow`, large-event counters, and replay percent estimates are useful regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDLog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDLog.h -->
# sources/distributed-fs/ceph/src/mds/MDLog.h

## Purpose

`MDLog.h` declares the MDS journal manager. It defines log perf-counter IDs, public journal lifecycle APIs, submit/flush/trim/replay controls, segment accessors, and thread classes for recovery, replay, and asynchronous submission.

## Important APIs And Types

The core class is `MDLog`. Public lifecycle methods are `create`, `open`, `reopen`, `append`, `replay`, `shutdown`, and `cap`. Submission and durability methods are `submit_entry`, `wait_for_safe`, `flush`, `is_flushed`, `set_write_iohint`, `kick_submitter`, and `finish_head_waiters`. Segment methods include `peek_current_segment`, `get_current_segment`, `get_segment`, `get_oldest_segment`, `get_last_major_segment_seq`, `get_last_segment_seq`, `trim_expired_segments`, `trim_all`, and `trim_to`.

`PendingEvent` pairs a `LogEvent*`, completion `Context*`, and flush flag. `ReplayThread`, `RecoveryThread`, and `SubmitThread` wrap the corresponding private methods. The class exposes `pending_exports` for replay state and `is_trim_slow` for beacon/health signaling.

## State And Persistence Behavior

The declaration shows the division between persistent journal positions and in-memory control state. `journaler` owns the RADOS journal stream; `safe_pos` records a position that is both durable and whose callbacks have run; `segments`, `major_segments`, `expired_segments`, and `expiring_segments` describe journal trimming boundaries. `pending_events` is protected by `submit_mutex`; `waiting_for_expire` is protected by `mds_lock`. Replay waiters, recovery completion, and submit queues are explicit because journal work runs outside normal request flow.

Runtime configuration is cached in `debug_subtrees`, `event_large_threshold`, `events_per_segment`, `max_events`, `max_segments`, `minor_segments_per_major_segment`, `pause`, corruption skip flags, `log_warn_factor`, and `log_trim_counter`. The upkeep thread uses `cond` and `upkeep_log_trim_shutdown` to perform periodic trim.

## Dependencies And Integration Points

`MDLog` depends on `Journaler`, `JournalPointer`, `LogEvent`, `MDSLogContextBase`, `MDSRank`, `MDSMap`, `LogSegment`, and `SegmentBoundary`. It grants friendship to replay/submit contexts, `ESubtreeMap`, and `MDCache` because replay, segment creation, and subtree-map events require tight coordination. `MDSLogContextBase` in `MDSContext.h` calls `MDLog::set_safe_pos`.

## Risks And Test Signals

The header highlights shared mutable state across three threads plus the rank lock, so lock-order tests and thread-shutdown tests are important. Public trim APIs should be covered by journal replay/trim integration tests, especially `trim_to` and `trim_expired_segments` waiters. The `pending_events` map by segment sequence is a critical invariant: segment creation, event sequence increments, and safe callbacks must stay aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDLog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSAuthCaps.cc -->
# sources/distributed-fs/ceph/src/mds/MDSAuthCaps.cc

## Purpose

`MDSAuthCaps.cc` implements parsing, matching, merging, serialization text, and authorization checks for CephFS MDS capability strings. It turns user/keyring strings such as `allow rw path=/foo fsname=myfs root_squash network ...` into grant objects and evaluates whether a client may perform a requested filesystem operation.

## Important Functions And Control Flow

`MDSCapParser` is a Boost.Spirit grammar. It parses one or more `allow` grants separated by comma or semicolon. A grant has a cap spec (`*`, `all`, `r`, `rw`, and combinations including `f`, `p`, `s`), optional `fsname`, optional `path`, optional `root_squash`, optional `uid`, optional `gids`, and optional network. Parsed grants are stored in `MDSAuthCaps`.

`MDSCapMatch::normalize_path` strips leading slashes from stored match paths. `match` first checks filesystem name, then UID/GID constraints when a UID is specified, then calls `match_path`. `match_path` strips trailing slashes from the configured path and enforces subtree matching without accepting prefix collisions such as `/foo` matching `/food`.

`MDSCapGrant::parse_network` parses the configured network into `entity_addr_t` and prefix length. `MDSAuthCaps::parse` handles the legacy string `allow` as `RWPS`, runs the grammar, sorts grant GIDs, parses networks, and clears all grants on failure. `is_capable` iterates grants, filters invalid/nonmatching networks, checks match predicates and basic read/write bits, applies root squash to root write attempts, validates special bits (`MAY_SET_VXATTR`, `MAY_SNAPSHOT`, `MAY_FULL`), and if the grant is UID-scoped, applies chown/chgrp and Unix owner/group/other mode checks.

`merge_one_cap_grant` and `merge` support `fs authorize` style idempotent grant merging by fsname/path, updating permissions and only adding `root_squash`, not removing it. `to_string` and stream operators render capabilities for diagnostics and keyring output.

## State And Persistence Behavior

This file does not persist data directly, but parsed caps are security-critical state attached to authenticated sessions and keyrings. Failure to parse clears `grants`, preventing partial malformed capabilities from being retained. Network parse state is cached in each grant as `network_parsed`, `network_prefix`, and `network_valid`. Merge behavior is intentionally monotonic for `root_squash` to avoid authorizing commands that silently reduce an existing restriction.

## Dependencies And Integration Points

The implementation uses Boost.Spirit/Qi, Boost.Phoenix, Ceph address parsing helpers (`parse_network`, `network_contains`), `mdstypes.h` operation masks, and Ceph debug logging. `MDSDaemon` calls `MDSAuthCaps::parse` during messenger authentication and session accept, and command handling uses `Session::auth_caps.allow_all()` for privileged tell commands.

## Risks And Test Signals

Primary risks are authorization bypass via path-prefix mistakes, UID/GID list ordering assumptions, malformed network handling, and inconsistent legacy grammar behavior. Tests should cover quoted/unquoted paths, leading/trailing slash normalization, `/foo` versus `/food`, wildcard and empty fs names, root-squash write denial for UID/GID 0, set-vxattr/snapshot/full bits, chown/chgrp constraints, network inclusion/exclusion, parse failure clearing grants, and merge idempotency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSAuthCaps.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSAuthCaps.h -->
# sources/distributed-fs/ceph/src/mds/MDSAuthCaps.h

## Purpose

`MDSAuthCaps.h` declares the data model and public authorization API for CephFS MDS capabilities. It defines operation masks, grant specs, match criteria, grant records, and the `MDSAuthCaps` container used by authenticated clients and daemon command paths.

## Important APIs And Types

The Unix-style operation mask includes `MAY_READ`, `MAY_WRITE`, `MAY_EXECUTE`, `MAY_CHOWN`, `MAY_CHGRP`, `MAY_SET_VXATTR`, `MAY_SNAPSHOT`, and `MAY_FULL`. `MDSCapSpec` stores cap bits (`ALL`, `READ`, `WRITE`, `SET_VXATTR`, `SNAPSHOT`, `FULL`) plus convenience combinations such as `RWPS` and `RWFPS`. Its `allows` method only covers read/write gating; special bits are checked separately by `is_capable`.

`MDSCapMatch` stores optional `uid`, `gids`, subtree `path`, `fs_name`, and `root_squash`. It provides `normalize_path`, `match`, `match_path`, `match_fs`, and versioned encode/decode helpers. `MDSCapAuth` is a compact encoded readable/writeable match used for passing cap-auth summaries. `MDSCapGrant` combines `MDSCapSpec`, `MDSCapMatch`, and optional network parse state.

`MDSAuthCaps` owns a vector of grants. Public methods include `clear`, `set_allow_all`, `parse`, `merge_one_cap_grant`, `merge`, `allow_all`, `is_capable`, `path_capable`, `fs_name_capable`, `get_cap_auths`, `root_squash_in_caps`, and `to_string`.

## State And Persistence Behavior

`MDSCapMatch` and `MDSCapAuth` are encoded with Ceph `ENCODE_START` version 1, so their wire/storage shape is explicit. `MDSCapGrant` network parse fields are runtime cache state and are not encoded in this header. `MDSAuthCaps` stores grants privately; callers must go through parsing/merging APIs to mutate them. `set_allow_all` normalizes universal access into a single all-match grant.

## Dependencies And Integration Points

The header depends on Ceph encoding, `entity_addr_t`, and standard string/vector types. It is consumed by `MDSDaemon`, sessions, auth/keyring handling, and any path permission checks that need to ask whether an authenticated identity can access a filesystem/path/mode combination.

## Risks And Test Signals

The separation between read/write `allows` and special-operation bits is easy to misuse; callers should use `is_capable` rather than testing `MDSCapSpec` directly. Encoding compatibility for `MDSCapMatch` and `MDSCapAuth` should be tested with round-trip cases. Security tests should validate that private `grants` cannot be left partially parsed after failed `parse`, and that `allow_all`, `fs_name_capable`, and `root_squash_in_caps` agree with full `is_capable` semantics where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSAuthCaps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSCacheObject.cc -->
# sources/distributed-fs/ceph/src/mds/MDSCacheObject.cc

## Purpose

`MDSCacheObject.cc` implements common behavior for `MDSCacheObject`, the base class for cacheable MDS metadata objects such as inodes, dentries, and dirfrags. The implementation covers debug pin naming, waiter completion, formatted state dumping, and waiter lookup/removal.

## Important Functions And Control Flow

`generic_pin_name` maps shared pin constants to readable strings and aborts on unknown pins. `finish_waiting` gathers waiters matching a `waitmask_t` via `take_waiting` and completes them with a result code using `finish_contexts`. `dump` emits common auth/replica state: auth flag, replica map, authority pair, replica nonce, auth pin count, freeze/freezing booleans, debug pin map when enabled, and total ref count. `dump_states` emits named state bits for auth, dirty, notifyref, rejoining, and rejoinundef.

`is_waiter_for` scans the ordered waiter multimap and returns true if any waiter mask intersects the requested mask. `take_waiting` removes matching waiters, appends their contexts to the caller-provided vector, and drops the `PIN_WAITER` pin once no waiters remain. `last_wait_seq` is the global monotonically increasing sequence for ordered waiters.

## State And Persistence Behavior

The file manages transient in-memory state only. Pins, waiter masks, replica maps, and state bits influence whether cache objects can be trimmed, expired, replicated, or completed, but they are not persisted here. Waiter completion can indirectly trigger persistent operations through the completed `MDSContext` bodies.

## Dependencies And Integration Points

The implementation depends on `MDSCacheObject.h`, `MDSContext.h`, and `Formatter`. Subclasses provide object-specific authority, freeze, lock, and print behavior. `MDCache`, locks, migrator/export code, and scrub paths use these base pins and waiters to coordinate object lifecycle.

## Risks And Test Signals

Risks include ref/pin leaks, completing waiters in the wrong order, and dropping `PIN_WAITER` while callbacks still reference the object. Tests should cover ordered and unordered waiters, mask intersection with 128-bit lock masks, replica add/remove pin transitions, formatted dump output for auth/replica objects, and debug assertions for invalid pin names or bad ref transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSCacheObject.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSCacheObject.h -->
# sources/distributed-fs/ceph/src/mds/MDSCacheObject.h

## Purpose

`MDSCacheObject.h` declares the common base class for metadata objects held in the MDS cache. It provides shared state bits, reference pins, auth-pin interfaces, replica tracking, waiter tracking, formatter dumping, and abstract hooks for subclass-specific authority, locking, freezing, and ordering.

## Important APIs And Types

Shared pin constants include `PIN_REPLICATED`, `PIN_DIRTY`, `PIN_LOCK`, `PIN_REQUEST`, `PIN_WAITER`, `PIN_DIRTYSCATTERED`, `PIN_AUTHPIN`, `PIN_PTRWAITER`, `PIN_TEMPEXPORTING`, `PIN_CLIENTLEASE`, `PIN_DISCOVERBASE`, and `PIN_SCRUBQUEUE`. State bits include `STATE_AUTH`, `STATE_DIRTY`, `STATE_NOTIFYREF`, `STATE_REJOINING`, and `STATE_REJOINUNDEF`. Wait bits include `WAIT_ORDERED`, `WAIT_SINGLEAUTH`, and `WAIT_UNFREEZE`; `waitmask_t` is 128 bits to combine object and lock wait masks.

Core ref methods are `get`, `put`, `get_num_ref`, `first_get`, `last_put`, `bad_get`, `bad_put`, `_put`, and `print_pin_set`. Authority and auth-pin behavior is abstract through `authority`, `can_auth_pin`, `auth_pin`, `auth_unpin`, `is_frozen`, and `is_freezing`. Replica APIs include `add_replica`, `remove_replica`, `clear_replica_map`, `get_replicas`, `list_replicas`, `get_replica_nonce`, and `set_replica_nonce`.

Waiter APIs are `add_waiter`, `take_waiting`, `finish_waiting`, `is_waiter_for`, and `count_waiters`. Lock-related methods default to abort and must be implemented by subclasses that expose `SimpleLock` state.

## State And Persistence Behavior

This class is in-memory lifecycle infrastructure. Ref counts and pins gate cache trimming and deletion; replica maps describe which peers have copies; waiters hold contexts until object state changes. The class itself does not encode persistent metadata, but its state determines when persistent metadata can safely be mutated, journaled, expired, or dropped.

## Dependencies And Integration Points

The header depends on Ceph mempool containers, `mdstypes`, `elist`, `MDSContext`, rank types, and `Formatter`. It is inherited by object types that `MDCache` stores in `inode_map`, dirfrag structures, dentry structures, lock code, scrub queues, export/import code, and rejoin handling.

## Risks And Test Signals

This is a high-blast-radius base class. Incorrect pin accounting can create leaks or premature frees; invalid replica map transitions can break cache coherence; waiter masks must remain compatible with lock waiters above 64 bits. Tests should exercise ref debug maps, `STATE_NOTIFYREF` callbacks, replica first/last pin behavior, auth-pin refusal reasons, waiter ordering, and subclass lock-waiter integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSCacheObject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSContext.cc -->
# sources/distributed-fs/ceph/src/mds/MDSContext.cc

## Purpose

`MDSContext.cc` implements MDS-specific `Context` completion wrappers. These wrappers ensure asynchronous callbacks run under the MDS rank lock when required, reset heartbeats, track outstanding I/O callbacks for slow-op diagnostics, respawn on severe I/O errors, and update the MDLog safe position after log completions.

## Important Functions And Control Flow

`MDSContext::complete` assumes `mds_lock` is already held, resets the rank heartbeat, and delegates to `Context::complete`. `MDSInternalContextWrapper::finish` forwards completion to a wrapped `Context`.

`MDSIOContextBase` constructs with a creation timestamp and optionally inserts itself into a global intrusive list protected by a spinlock. Its destructor removes the list item. `check_ios_in_flight` scans this list for contexts older than a cutoff, returning a bounded slow count and oldest timestamp. `MDSIOContextBase::complete` acquires `mds_lock`, drops callbacks while the daemon is stopping, respawns on `-EBLOCKLISTED` or `-ETIMEDOUT`, and otherwise calls `MDSContext::complete`.

`MDSLogContextBase::complete` captures the write position, calls `pre_finish`, runs normal I/O completion, and then calls `MDLog::set_safe_pos`. `MDSIOContextWrapper::finish` and `C_IO_Wrapper::finish` forward to wrapped contexts. `C_IO_Wrapper::complete` first queues itself on the finisher for async completion, then runs as a normal `MDSIOContext` when invoked synchronously by the finisher.

## State And Persistence Behavior

The only persistent-facing state is `MDSLogContextBase::write_pos`: it advances `MDLog::safe_pos` after the completion body has run, establishing the journal position that is both durable and callback-safe. The global I/O context list is transient diagnostic state.

## Dependencies And Integration Points

This file depends on `MDSRank`, `MDLog`, Ceph debug logging, and the `Context`/finisher model. `MDLog`, `MDCache`, objecter/filer callbacks, and gather builders use these contexts to cross from asynchronous storage/network completion back into MDS locked state.

## Risks And Test Signals

Risks include lock-order deadlocks, deleting wrapped contexts twice, failing to remove tracked I/O contexts, and advancing journal safe position before completion side effects are visible. Tests should cover slow I/O detection, stopping-daemon callback drops, blocklist/timeout respawn behavior, async `C_IO_Wrapper` queueing, and log safe-position monotonicity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSContext.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSContext.h -->
# sources/distributed-fs/ceph/src/mds/MDSContext.h

## Purpose

`MDSContext.h` declares the MDS-specific context hierarchy. It adapts generic Ceph `Context` completions to the MDS rank locking model and provides wrappers for internal callbacks, I/O callbacks, journal callbacks, gather builders, and continuation stages.

## Important APIs And Types

`MDSContext` is the abstract base with `complete` and `get_mds`. `MDSHolder<T>` is a template that stores an `MDSRank*` and implements `get_mds`. `MDSInternalContext` is for callbacks already running inside MDS lock context. `MDSInternalContextWrapper` wraps an arbitrary `Context`.

`MDSIOContextBase` is for callbacks from I/O paths and declares `complete`, `print`, and static `check_ios_in_flight`. `MDSLogContextBase` extends it for journal operations with `write_pos`, `set_write_pos`, and `pre_finish`. `MDSIOContext` and `MDSIOContextWrapper` provide concrete MDS-held I/O contexts. `C_MDSInternalNoop` is a no-op gather leaf. `C_IO_Wrapper` turns an internal context into an I/O context and can queue itself through the MDS finisher.

Aliases `MDSGather`, `MDSGatherBuilder`, and `MDSContextFactory` bind generic gather/context helper templates to `MDSContext`.

## State And Persistence Behavior

The header does not persist state. The important durability contract is in `MDSLogContextBase`: journal completions carry write positions and are responsible for advancing MDLog safe position after completion. `MDSIOContextBase` instances may be tracked for diagnostics with creation timestamps and intrusive list items.

## Dependencies And Integration Points

It depends on `Context`, `elist`, `ceph_time`, and forward-declared `MDSRank`. It is widely used by `MDCache`, `MDLog`, `MDSContinuation`, journal events, storage completions, and gather patterns where callbacks need MDS lock semantics.

## Risks And Test Signals

Every subclass must respect whether `complete` expects the lock to be held or will acquire it itself. Mixing `MDSInternalContext` and `MDSIOContextBase` incorrectly can deadlock or run unlocked. Test signals include context tracking counts, callback behavior during daemon stop, wrapper ownership/destruction, gather cancellation, and journal callback safe-position updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSContext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSContinuation.h -->
# sources/distributed-fs/ceph/src/mds/MDSContinuation.h

## Purpose

`MDSContinuation.h` declares `MDSContinuation`, a small adapter between Ceph's generic `Continuation` framework and MDS callback types. It lets staged server operations request callbacks already wrapped as `MDSInternalContext` or `MDSIOContextBase`.

## Important APIs And Control Flow

`MDSContinuation` stores a `Server*` and passes `NULL` to the base `Continuation` constructor. `get_internal_callback(stage)` calls the base `get_callback(stage)` and wraps the returned generic context in `MDSInternalContextWrapper(server->mds, ...)`. `get_io_callback(stage)` similarly wraps the stage callback in `MDSIOContextWrapper`.

## State And Persistence Behavior

This file has no persistence behavior. It holds only the server pointer needed to access `server->mds` for context wrapping. Persistent side effects occur in the staged callbacks created by users of the continuation.

## Dependencies And Integration Points

It includes `common/Continuation.h`, `mds/Mutation.h`, `mds/Server.h`, and `MDSContext.h`. It is intended for multi-stage MDS server operations where some stages complete internally and others complete from I/O.

## Risks And Test Signals

The main risks are callback ownership and incorrect wrapper selection. A stage that completes from I/O must use `get_io_callback` so it acquires `mds_lock`; a stage already under MDS control should use `get_internal_callback`. Tests should cover staged operation cancellation, callback deletion, and lock expectations for both wrapper types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSContinuation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSDaemon.cc -->
# sources/distributed-fs/ceph/src/mds/MDSDaemon.cc

## Purpose

`MDSDaemon.cc` implements the top-level Ceph MDS daemon process object. It initializes messenger/monitor/auth/logging/admin-socket integration, receives MDS maps, creates and delegates to an `MDSRankDispatcher` when assigned a rank, handles daemon-level commands and signals, manages shutdown/respawn, and wires authenticated client connections to `Session` objects.

## Important Functions And Control Flow

The constructor initializes timers, GSS keytab environment, beacon, messenger/monitor references, manager/log clients, start time, and an empty `MDSMap`. `init` rejects unsupported Windows daemon mode, logs structure sizes, registers beacon and daemon dispatchers, initializes and authenticates `MonClient`, waits for rotating keys, subscribes to `mdsmap`, sets up the admin socket, initializes timer/beacon state, sets messenger identity to rankless MDS, and schedules periodic `tick`.

`set_up_admin_socket` registers daemon and rank-facing commands. `asok_command` handles daemon-local commands (`status`, `lockup`, `exit`, `respawn`, `heap`, `cpu_profiler`) and delegates all other commands to `mds_rank->handle_asok_command` when active. `dump_status` emits cluster FSID, rank identity, wanted/current state, MDS/OSD map epochs, uptime, sysinfo, and endian.

`handle_mds_map` discards old maps, decodes the new map, validates compatibility, determines this daemon's global id, rank, old/new state, and incarnation, marks removed peer addrs down, initializes `MgrClient` when first added to the FS map, handles rankless standby state, creates `MDSRankDispatcher` when assigned a rank, delegates map processing to the rank dispatcher, and notifies the beacon.

`ms_dispatch2` takes `mds_lock`, drops messages during stop/DNE state, handles core messages, then delegates rank messages. `handle_core_message` filters by peer type and handles monitor maps, MDS maps, snap removals, command messages, OSD map notifications, and legacy monitor commands. `handle_command` authorizes tell commands using session `auth_caps.allow_all` and queues accepted commands through the admin socket.

Shutdown paths are `handle_signal`, `suicide`, and `respawn`. `suicide` marks `stopping`, cancels tick, unregisters admin socket, sets beacon wanted state to DNE, unlocks while waiting for beacon ACK, shuts down beacon/manager, then either shuts down rank or timer/monitor/messenger. `respawn` logs recent messages and `execv`s the current executable path.

## State And Persistence Behavior

`MDSDaemon` persists no metadata directly. It owns runtime identity, map, timer, beacon, clients, and rank dispatcher. Its handling of `MDSMap` controls when rank-level persistent subsystems start or stop. `parse_caps` decodes authenticated cap strings and populates `MDSAuthCaps` for connections and sessions.

## Dependencies And Integration Points

The file integrates `Messenger`, `MonClient`, `MgrClient`, `LogClient`, `Beacon`, `MDSMap`, `MDSRankDispatcher`, `Session`, `Server`, `Locker`, snap components, admin socket, auth keyrings, profiler hooks, and Ceph message types. It is the root dispatcher for the daemon and the owner of `mds_lock`.

## Risks And Test Signals

Risks include lock ordering during shutdown/admin commands, invalid rank transitions, accepting malformed caps, dispatching rank messages while rankless, and failing to respawn on removal or blocklist-related paths. Tests should cover startup auth failures, rotating key timeout, admin socket command delegation, MDS map old/new transitions, removal from map, rank assignment, signal shutdown, session replacement on reconnect, tell-command authorization, and message peer-type filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSDaemon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSDaemon.h -->
# sources/distributed-fs/ceph/src/mds/MDSDaemon.h

## Purpose

`MDSDaemon.h` declares the top-level MDS daemon dispatcher and process-lifecycle object. It exposes daemon initialization, signal handling, clean-shutdown inspection, the global MDS lock, and protected/private hooks for admin socket, tick, message dispatch, authentication, shutdown, and respawn.

## Important APIs And State

Public methods are `MDSDaemon`, destructor, `get_starttime`, `get_uptime`, `handle_signal`, `init`, and `is_clean_shutdown`. The public `mds_lock` and `stopping` flag are central: comments require every lock holder to check `stopping` and either do no work or never drop the lock again.

Protected methods include `reset_tick`, `wait_for_omap_osds`, `set_up_admin_socket`, `clean_up_admin_socket`, `check_ops_in_flight`, `asok_command`, `dump_status`, `suicide`, `respawn`, `tick`, `handle_core_message`, `handle_command`, and `handle_mds_map`. Private messenger overrides are `ms_dispatch2`, auth/connect/reset handlers, and `parse_caps`.

State includes `Beacon`, daemon `name`, `Messenger*`, `MonClient*`, `io_context`, `MgrClient`, current `MDSMap`, `LogClient`, cluster log channel, optional `MDSRankDispatcher`, timer tick event, admin socket hook, original argv for respawn, and start time.

## State And Persistence Behavior

This header models runtime process state, not filesystem persistence. Persistent effects are indirect: map transitions create/drive rank dispatchers; shutdown state updates beacons and monitor-visible wanted state; authentication parsing determines session capabilities. `orig_argc`/`orig_argv` preserve command-line state for process replacement.

## Dependencies And Integration Points

It inherits from `Dispatcher`, depends on `Beacon`, `LogClient`, `Timer`, `MgrClient`, `Messenger`, `MonClient`, `MDSMap`, `MCommand`, `MMDSMap`, and `MDSAuthCaps`. `MDSRankDispatcher` owns rank-specific metadata subsystems after rank assignment.

## Risks And Test Signals

The API makes `mds_lock` public because many subsystems coordinate through it, so lock discipline is the main risk. Tests should verify dispatcher behavior while rankless, while stopping, and after DNE desired state. Clean shutdown should distinguish rankless standby from active rank stop. `parse_caps` should reject undecodable buffers and malformed strings consistently with fast authentication and accept handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSDaemon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSMap.cc -->
# sources/distributed-fs/ceph/src/mds/MDSMap.cc

## Purpose

`MDSMap.cc` implements the CephFS MDS map data model: daemon/rank state reporting, compatibility feature sets, health summaries, versioned encoding/decoding, cluster availability, state-transition validation, pool/rank helpers, required client feature derivation, and balancer rank-mask parsing.

## Important Functions And Control Flow

Compatibility helpers build all/default/base/pre-v16.2.5 `CompatSet` values. `mds_info_t::dump`, `dump(std::ostream&)`, and `human_name` render per-daemon state. `MDSMap::dump`, `print`, `print_summary`, `dump_flags_state`, and `print_flags` expose map contents: epoch, flags, features, timestamps, pools, ranks, failed/damaged/stopped sets, daemon info, balancer settings, standby counts, and quiesce DB membership.

Health APIs include legacy `get_health` and structured `get_health_checks`. They report damaged ranks, degraded filesystems, online MDS count below `max_mds`, all-down filesystems, multi-MDS with old snapshots, laggy daemons, and deprecated inline data.

Encoding is heavily versioned. `mds_info_t::encode_versioned` selects struct version based on peer features and encodes addrs, laggy state, export targets, MDS features, join fscid, flags, and compat. `MDSMap::encode` has legacy branches for peers without `CEPH_FEATURE_PGID64` or `CEPH_FEATURE_MDSENC`, then the modern `ENCODE_START(5,4)` form with extended version `ev=19`. `decode` mirrors these versions, provides defaults for older fields, converts old snap booleans to feature flags, derives required client features for older encodings, and bootstraps missing daemon compat from map compat.

Query helpers include `is_cluster_available`, `get_state_gid`, `get_state`, `get_gid`, `get_info`, `state_transition_valid`, `check_health`, `is_data_pool`, `find_mds_gid_by_name`, `get_num_mds`, `get_up_mds_set`, `add_data_pool`, `remove_data_pool`, `get_up_features`, `get_recovery_mds_set`, `get_mds_set_lower_bound`, `get_mds_set`, `get_standby_replay`, `is_followable`, `is_laggy_gid`, `is_degraded`, address/rank/incarnation helpers, `set_min_compat_client`, and rank-mask methods.

## State And Persistence Behavior

The encoded MDS map is persistent monitor-distributed cluster state. It records feature compatibility, filesystem enablement/name, pools, rank membership, daemon info by global id, failed/damaged/stopped ranks, required client features, balancer configuration, and qdb cluster fields. Decode sanitizes old layouts and inserts `MDS_FEATURE_INCOMPAT_INLINE` for compatibility during transition. `sanitize` removes data pools that no longer exist according to an external pool predicate.

## Dependencies And Integration Points

The file depends on `MDSMap.h`, CephFS feature helpers, `Formatter`, monitor health-check types, and Ceph encoding. `MDSDaemon` decodes maps from `MMDSMap` and validates compat before processing. Clients use availability and address/rank queries; monitors use health/check and state-transition logic.

## Risks And Test Signals

Risks include wire-compatibility regression, incorrect defaults for old maps, health false positives/negatives, invalid state transitions, and rank-mask parsing mistakes. Tests should round-trip every supported encoding branch, decode old map fixtures, validate transition tables, exercise availability with empty/damaged/laggy/active states, check health checks for each degraded condition, sanitize missing pools, compute up-feature intersections, and parse `bal_rank_mask` values including `all`, `-1`, `0`, `0x0`, valid hex, invalid hex, oversize masks, and all-zero masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDSMap.cc -->
