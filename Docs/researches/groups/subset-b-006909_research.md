# subset-b-006909 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Capability.h -->
# sources/distributed-fs/ceph/src/mds/Capability.h

## Purpose

`Capability.h` declares the MDS-side representation of a CephFS client capability on an inode. It models the protocol described in the file comments: MDS issues caps to clients, later updates may grant or revoke bits, clients confirm receipt or flush dirty metadata, and MDS must track enough sequence history to distinguish current releases from stale or racing revocations.

The class is also the migration payload carrier for caps during subtree export/import. `Capability::Export` captures the full transferable cap state, `Capability::Import` captures compact import-side identity and sequence data, and `revoke_info` preserves revocation history while acknowledgments race with new issues.

## Important APIs, Types, And Functions

`Capability` derives from `Counter<Capability>` and uses `MEMPOOL_CLASS_HELPERS`, so object count/increment/decrement signals feed MDS telemetry and allocation comes from the MDS mempool. Its external identity is `(CInode*, Session*, cap_id)`, with client identity resolved from `Session`.

The most important state accessors are `pending()`, `issued()`, `revoking()`, `wanted()`, `get_last_seq()`, `get_last_issue()`, `get_mseq()`, `get_last_issue_stamp()`, and `get_last_revoke_stamp()`. `pending` is what the MDS currently wants the client to retain; `issued` includes caps still believed to be in the client's possession, including revoking bits.

`issue(unsigned c, bool reval=false)` handles grants and revocations. When `c` removes bits from `_pending`, it appends `revoke_info(_pending, last_sent, last_issue)`, replaces `_pending`, keeps `_issued` broad enough to cover in-flight caps, marks the cap notable, increments `last_sent`, and returns the new sequence. Add-only grants OR bits into `_pending` and `_issued` and trim obsolete revocation history. `issue_norevoke()` is the add-only variant that also clears `STATE_NEW`.

`confirm_receipt(ceph_seq_t seq, unsigned caps)` is declared here and implemented in `Capability.cc`; it reconciles client acknowledgments/releases with `_revokes`, clears revoking list membership when `_issued == _pending`, and returns the bit mask that was actually revoked. `clean_revoke_from(ceph_seq_t li)` drops revocation history older than a known last-issue value, recalculates `_issued`, and removes revoking-list items when revocation has ended.

`make_export()`, `merge(const Export&, bool auth_cap)`, and `merge(int otherwanted, int otherissued)` are migration-facing APIs. `make_export()` exports cap ID, wanted/issued/pending bits, `client_follows`, issue sequence, incremented migration sequence, `last_issue_stamp`, and exported state flags. `merge()` combines pending and issued bits, wanted bits, client follow state, selected state flags, and optionally authoritative `mseq`.

The state flags are meaningful protocol and feature gates: `STATE_NOTABLE`, `STATE_NEW`, `STATE_IMPORTING`, `STATE_NEEDSNAPFLUSH`, `STATE_CLIENTWRITEABLE`, `STATE_NOINLINE`, `STATE_NOPOOLNS`, and `STATE_NOQUOTA`. `MASK_STATE_EXPORTED` limits which flags survive migration. `mark_clientwriteable()`, `clear_clientwriteable()`, `set_wanted()`, `mark_notable()`, and `maybe_clear_notable()` drive session LRU placement and inode notable-cap counters.

## Control Flow And Data Flow

Normal issue flow starts with Locker/Server code deciding a cap mask, then calling `issue()` or `issue_norevoke()`. If revocation is involved, `_revokes` records the prior pending bits and sequence. The message sent to the client carries `last_sent`; later client updates call `confirm_receipt()` with a sequence and retained cap mask. Exact-sequence confirmations clear or rebuild revocation history; older confirmations drop only the historical revokes they cover.

Migration flow exports `Capability::Export` from the source MDS and merges it into the destination cap. Import tracking uses `Capability::Import` for `cap_id`, `issue_seq`, and `mseq`. Peer export/import maps appear in `Migrator`, `MDCache`, `Server`, and `Mutation`, so this header defines the cross-rank cap state contract.

Notability flow keeps caps that matter near the active session list. Writable, revoking, and wanted read/write caps mark the cap notable and call `Session::touch_cap`; when those conditions disappear, `maybe_clear_notable()` moves the cap to the bottom with `touch_cap_bottom`. This is central to cap trimming and session pressure behavior.

## State And Persistence Behavior

Persistent/encoded cap state includes `last_sent`, `last_issue_stamp`, `_wanted`, `_pending`, and `_revokes`; decode restores `_pending`/`_revokes` and recalculates `_issued`. Export encoding additionally persists transfer-specific fields including cap ID, issued/pending/wanted, `client_follows`, sequence values, migration sequence, stamp, and exported state flags. Import encoding is intentionally smaller.

In-memory-only fields include raw pointers to `CInode` and `Session`, intrusive list items for session/snaprealm/revoking queues, `lock_caches`, suppress count, last revoke stamp, warning counters, and `lock_cache_allowed`. `cap_gen` couples a cap to the owning session generation; stale sessions make caps invalid until `revalidate()`.

Sequence correctness is the core persistence risk. `_issued` is derived from `_pending` plus `_revokes`, so any lost or misordered revoke history can make the MDS think a client still has or no longer has authority. `mseq` tracks migration ordering, while `last_issue` records the last issue point that clients must have seen for safe release semantics.

## Dependencies And Integration Points

This file depends on CephFS cap bit definitions from `include/ceph_fs.h`, `mdstypes.h`, `snapid_t`, `version_t`, `utime_t`, Ceph buffer encoding, `Counter`, mempool helpers, and intrusive `xlist`/`elist` containers. It forward-declares `CInode`, `Session`, and `MDLockCache`.

Integration points include `Capability.cc` for encoding and state transitions, `CInode` cap maps and export helpers, `SessionMap` and `Session` cap lists, `Locker` cap issue/revoke decisions, `Migrator` subtree export/import, `MDCache` rejoin/import tracking, `Server` client message handling, and `MDSRank`/`MDCache` performance counters that read `Capability::count()`.

## Risks And Edge Cases

Revocation races are the main risk. A release can race with revocation; `clean_revoke_from()` exists specifically to prevent MDS from waiting forever on revokes the client never processed. Older `confirm_receipt()` sequences must not wipe newer revokes. Add-only grants prune historical revokes only when all revoked bits are no longer outside `_pending`.

State flags mix protocol, migration, and client-feature compatibility. Exporting too many flags would leak local state; exporting too few would lose writeability or feature restrictions. `STATE_NOINLINE`, `STATE_NOPOOLNS`, and `STATE_NOQUOTA` are set from session connection feature bits, so sessionless or stale caps have different assumptions.

`maybe_clear_notable()` asserts the cap is notable before clearing; callers must maintain notable state consistently. `mark_notable()` assumes `session` is present. `dec_suppress()` does not guard underflow. `merge()` calls `issue()`, so imports can generate new sequences and revocation history if pending/issued masks are inconsistent.

## Test Signals

Useful tests exercise dencoder round trips for `Capability`, `Export`, `Import`, and `revoke_info`; cap issue/revoke sequences where `confirm_receipt()` is exact, stale, and racing; migration export/import merge preserving wanted, pending, `client_follows`, and exported flags; session staleness/revalidation; and cap trim behavior that moves caps between notable and bottom lists. Runtime signals include MDS cap counters, revoking-cap queues draining, absence of stuck revocation warnings, and correct client behavior after subtree migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Capability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/DamageTable.cc -->
# sources/distributed-fs/ceph/src/mds/DamageTable.cc

## Purpose

`DamageTable.cc` implements the MDS rank's in-memory registry of known damaged metadata objects. It records damage found during dirfrag/dentry fetch, forward scrub, remote inode/backtrace lookup, and data-uninline operations, then exposes lookup and dump paths so the MDS can avoid repeatedly touching known-bad metadata and can surface damage to operators.

## Important APIs, Types, And Functions

Anonymous concrete `DamageEntry` subclasses implement the four damage types declared in the header: `DirFragDamage`, `DentryDamage`, `BacktraceDamage`, and `UninlineDamage`. Each stores type-specific identifiers and implements `get_type()` plus `dump(Formatter*)`. `DamageEntry` construction assigns a random 32-bit-ish ID through `ceph::util::generate_random_number<damage_entry_id_t>(0, 0xffffffff)` and timestamps `reported_at`.

`notify_dentry()` reports an unreadable dentry within a `(ino, frag, snap_id, dname)` tuple. It treats damage to this rank's MDS directory or stray directory as fatal, checks `oversized()`, creates a `DentryDamage` only on first insertion into the per-dirfrag dentry map, and indexes the same entry in `by_id`.

`notify_dirfrag()` reports an unreadable dirfrag. Damage to this rank's stray dirfrag or to root is fatal. Otherwise it deduplicates by `(ino, frag)`, stores `DirFragDamage`, and indexes by ID.

`notify_remote_damaged()` records a remote inode/backtrace lookup failure keyed by inode number. `notify_uninline_failed()` records failed data uninlining keyed by inode and includes rank, errno text, scrub tag, and path in dumps.

Removal APIs map higher-level objects back to IDs: `remove_dentry_damage_entry(CDir*)`, `remove_dirfrag_damage_entry(CDir*)`, and `remove_backtrace_damage_entry(inodeno_t)`. `erase(damage_entry_id_t)` removes the primary `by_id` row and the corresponding secondary index based on `get_type()`. Lookup APIs are `is_dentry_damaged()`, `is_dirfrag_damaged()`, and `is_remote_damaged()`. `dump()` emits a formatter array named `damage_table`.

## Control Flow And Data Flow

Damage notification flow starts in fetch/scrub code, which calls a `notify_*` method with metadata coordinates and an advisory path. Fatal cases return `true`; callers are expected to mark the rank damaged. Nonfatal cases allocate one shared entry and insert it into both a semantic lookup map and the `by_id` administration map. Duplicate notifications for the same key are intentionally ignored except for the existing entry remaining available.

Lookup flow is performance-oriented: MDCache and scrub code check `is_dirfrag_damaged()` before fetching a known-bad dirfrag, `is_dentry_damaged()` before dentry lookup, and `is_remote_damaged()` before following remote links. Admin flow dumps all `by_id` entries, and MDSRank exposes `erase(id)` to remove operator-cleared damage.

Erase flow first finds the entry in `by_id`, casts according to type, removes the secondary index, then removes the ID row. For dentry damage, `erase()` currently erases the entire per-dirfrag dentry map for that entry's dirfrag rather than only the individual dentry key, so one dentry erase can clear sibling dentry records in the same fragment.

## State And Persistence Behavior

The table is in-memory and protected by `MDS::mds_lock` per the header. It does not encode itself to disk. Persistence of the underlying damage is external in RADOS metadata objects; this table caches observed damage and exposes it until cleared or the rank restarts.

State is stored in four secondary maps: `dirfrags`, `dentries`, `remotes`, and `uninline_failures`, plus `by_id` for operator addressing. Entries preserve `reported_at` and advisory `path`, but dumps do not include `reported_at`. `oversized()` compares `by_id.size()` with `g_conf()->mds_damage_table_max_entries`.

## Dependencies And Integration Points

The implementation depends on `CDir` and `CInode` for dirfrag identity, `BatchOp.h`, Ceph debug/errno helpers, `include/random.h`, `g_conf()`, and MDS inode macros such as `MDS_INO_IS_MDSDIR`, `MDS_INO_MDSDIR_OWNER`, `MDS_INO_IS_STRAY`, `MDS_INO_STRAY_OWNER`, and `CEPH_INO_ROOT`.

Integration points include `MDSRank::damage_table`, `Beacon.cc` detecting non-empty damage, `CDir` reporting fetch failures and removing dentry damage after successful load, `MDCache` avoiding damaged paths and reporting remote damage, `ScrubStack` moving scrub failures into the table, `CInode` clearing backtrace damage, and MDS admin dump/erase commands.

## Risks And Edge Cases

The configured limit check uses `by_id.size() > max_entries`, so the table can grow to `max_entries + 1` before becoming fatal. Random damage IDs are not checked for collision before `by_id[entry->id] = ...`; a collision could overwrite an existing ID row while secondary indexes still hold both entries. `notify_uninline_failed()` passes global `errno` instead of its `failure_errno` parameter to `UninlineDamage`, which can report the wrong failure text.

`remove_dentry_damage_entry()` copies the per-frag dentry map before erasing by ID, which avoids iterator invalidation but may be expensive for a large damaged fragment. `erase()` for a `DENTRY` removes the entire `dentries[DirFragIdent]` map, not just the named dentry, so clearing one ID can unintentionally clear all dentry damage for that dirfrag. The table is advisory and volatile; a restart loses the cache even if damage remains.

## Test Signals

Tests should cover deduplication for repeated dirfrag/dentry/remote/uninline notifications, fatal return behavior for root, rank-owned stray, and rank-owned MDS directory cases, configured max-entry handling, dump formatting for every damage type, and erase consistency between `by_id` and secondary maps. Regression tests should specifically check `notify_uninline_failed()` records the supplied `failure_errno`, dentry ID erasure does not clear unrelated dentries unless intended, and random ID collisions do not corrupt operator addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/DamageTable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/DamageTable.h -->
# sources/distributed-fs/ceph/src/mds/DamageTable.h

## Purpose

`DamageTable.h` declares the MDS rank damage registry used to remember in-RADOS metadata damage detected during normal fetches and scrub. It provides operator-visible damage entries, fast lookup of known-bad metadata paths, and a fatal/nonfatal signal to callers when damage affects critical rank-local system directories or when the table exceeds its configured capacity.

## Important APIs, Types, And Functions

`damage_entry_id_t` is a `uint64_t` external handle for damage entries. `damage_entry_type_t` enumerates `DAMAGE_ENTRY_DIRFRAG`, `DAMAGE_ENTRY_DENTRY`, `DAMAGE_ENTRY_BACKTRACE`, and `DAMAGE_ENTRY_UNINLINE_FILE`.

`DamageEntry` is the abstract base for all damage records. It requires `get_type()` and `dump(Formatter*)`, and stores common `id`, `reported_at`, and advisory `path`. `DamageEntryRef` is a `std::shared_ptr<DamageEntry>` shared between primary and secondary indexes.

`DirFragIdent` orders dirfrag keys by inode then `frag_t`. `DentryIdent` orders dentry keys by name then `snapid_t`. Both are map keys used for deduplication and lookup.

`DamageTable` is constructed with a concrete `mds_rank_t` and asserts it is not `MDS_RANK_NONE`. Public notify APIs are `notify_dirfrag()`, `notify_dentry()`, `notify_remote_damaged()`, and `notify_uninline_failed()`, each returning `true` for fatal damage. Public cleanup APIs are `remove_dentry_damage_entry()`, `remove_dirfrag_damage_entry()`, `remove_backtrace_damage_entry()`, and `erase(damage_entry_id_t)`. Query APIs are `empty()`, `is_dentry_damaged()`, `is_dirfrag_damaged()`, and `is_remote_damaged()`.

## Control Flow And Data Flow

Callers report damage with metadata coordinates and an advisory path. The table deduplicates by secondary keys and assigns one ID-addressable `DamageEntry` per unique damaged object. Later path traversal or scrub can query the relevant secondary map before attempting an operation. Operators or successful repair paths remove entries by ID or by object identity.

The table has one primary administration index, `by_id`, and several semantic indexes. Dirfrag damage is keyed by `DirFragIdent`. Dentry damage is grouped by `DirFragIdent` and keyed by `DentryIdent` inside each fragment. Remote/backtrace damage and uninline failures are keyed by inode number.

## State And Persistence Behavior

This header defines in-memory state only. The table itself is not encoded and does not persist across MDS restarts. Its entries reflect observed damage, not authoritative repair state. The header documents that callers must hold `MDS::mds_lock` around access.

The rank field is immutable and used to identify rank-owned system directories where damage must be fatal. `oversized()` is protected and implemented in the `.cc` file using `mds_damage_table_max_entries`.

## Dependencies And Integration Points

Dependencies include `mdstypes.h`, CephFS rank/inode types, `frag_t`, `snapid_t`, `utime_t`, `Formatter`, and forward-declared `CDir`/`CInode`. The table is a member of `MDSRank` and is consulted by `MDCache`, `CDir`, `ScrubStack`, `Beacon`, and admin dump/erase paths.

The design intentionally separates generic `DamageEntry` presentation from MDS cache object types. Notify callers can pass only coordinates and a path, while cleanup/lookups can use `CDir*` when a cache object exists.

## Risks And Edge Cases

The advisory path should not be treated as authoritative; path names can change while damage remains tied to inode/frag/snap identifiers. Because the table is volatile, external repair tooling must not infer that missing entries mean absence of damage after restart. The ID map is secondary by design, so erase implementations must keep all indexes consistent.

The header documents fatal behavior for table overflow and critical damage, so callers must check the boolean return. Ignoring the return could let an MDS continue after damage to rank-owned metadata. Since access is protected by `MDS::mds_lock` rather than internal locking, adding call sites outside that lock would introduce races.

## Test Signals

Header-level contract tests should validate map ordering for `DirFragIdent` and `DentryIdent`, notify return handling by callers, and index consistency after remove/erase. Integration signals include beacon warning when `empty()` is false, MDCache skipping damaged paths, scrub moving failures into the table, and admin dumps listing each damage type with stable IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/DamageTable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/FSMap.cc -->
# sources/distributed-fs/ceph/src/mds/FSMap.cc

## Purpose

`FSMap.cc` implements serialization, printing, health checks, lookup helpers, and mutators for the CephFS filesystem map. The map is the monitor-owned cluster view of CephFS filesystems, their embedded `MDSMap`s, standby daemons, daemon-to-filesystem roles, compatibility, mirror peer metadata, and filesystem IDs.

## Important APIs, Types, And Functions

`ClusterInfo`, `Peer`, and `MirrorInfo` implement encode/decode, dump, print, and test-instance support for filesystem mirroring peer metadata. `MirrorInfo` stores a `mirrored` flag and a set of peers; disabling mirroring clears peers.

`Filesystem` wraps an `MDSMap`, `fs_cluster_id_t`, and `MirrorInfo`. Its encode format stores `fscid`, an encoded nested `MDSMap` bufferlist, and mirror info as version 2. `dump()` and `print()` delegate heavily to `MDSMap`.

`FSMap::dump()`, `print()`, `print_summary()`, `print_daemon_summary()`, and `print_fs_summary()` produce operator and status output. They aggregate daemon states, degraded/failed/damaged filesystems, standby counts, btime, compatibility, and feature flags.

Creation and filesystem mutators include `create_filesystem()`, `commit_filesystem()`, `reset_filesystem()`, `erase_filesystem()`, and `swap_fscids()`. `create_filesystem()` initializes a `Filesystem` with pools, compat, timestamps, and optional recovery state. `commit_filesystem()` assigns or accepts an FSCID, updates `next_filesystem_id`, and sets the legacy client filesystem for the first filesystem.

Daemon state mutators include `insert()` for new standby beacons, `promote()` for assigning a standby or standby-replay to an active rank, `assign_standby_replay()`, `erase()` for daemon removal/failure, `damaged()`, `undamaged()`, and `stop()`.

Lookup and parsing helpers include `get_mds_info()`, `get_available_standby()`, `find_mds_gid_by_name()`, `find_by_name()`, `find_replacement_for()`, `parse_filesystem()`, `parse_role()`, `pool_in_use()`, `is_any_degraded()`, and `sanitize()`.

Health APIs are `get_health()`, `check_health()`, and `get_health_checks()`. `sanity(bool pending=false)` asserts consistency among `filesystems`, embedded `MDSMap` structures, standby maps, `mds_roles`, and quiesce-db membership.

## Control Flow And Data Flow

Monitor update flow typically increments the map epoch outside these methods, mutates filesystem or daemon state, and persists the encoded `FSMap` through the monitor Paxos path. Most mutators stamp the affected embedded `MDSMap` with the current `FSMap::epoch` and `ceph_clock_now()`.

Standby assignment flow begins with `insert()` placing a beaconed daemon in `standby_daemons`, `standby_epochs`, and `mds_roles[gid] = FS_CLUSTER_ID_NONE`. `get_available_standby()` filters standby daemons by lag/frozen state, compatibility, upgradeability, and `join_fscid` preference. `promote()` moves the daemon into a filesystem's `mds_info`, upgrades compatibility only if the filesystem is upgradeable, selects `CREATING`, `STARTING`, or `REPLAY` based on rank history, updates `in`/`up`, and removes standby bookkeeping.

Failure flow uses `erase()` to remove a daemon. Standbys are simply removed. Active non-standby-replay daemons have their rank removed from `up`; depending on state, the rank is removed from `in`, moved to `stopped`, or moved to `failed`. `damaged()` wraps `erase()`, then moves the rank from `failed` to `damaged`. `undamaged()` moves a rank back from `damaged` to `failed`.

Health flow delegates per-filesystem checks to `MDSMap`, computes insufficient standby warnings using the maximum per-filesystem standby need, and emits `FS_WITH_FAILED_MDS` only for failed ranks that have no replacement from standby-replay or available standby.

Encoding flow writes struct version 8 with minimum compatible version 6, but decode requires oldest 7. It stores epoch, next filesystem ID, legacy FSCID, compat, multiple-FS flags, filesystems, role map, standby maps, ever-enabled-multiple flag, and birth time. Older struct versions omit later fields and leave defaults.

## State And Persistence Behavior

`FSMap` state persisted by encode/decode includes global `epoch`, `btime`, `next_filesystem_id`, `legacy_client_fscid`, `default_compat`, `enable_multiple`, `ever_enabled_multiple`, all `Filesystem` objects, `mds_roles`, `standby_daemons`, and `standby_epochs`. `struct_version` is decode-only state that lets monitor code detect old maps through `is_struct_old()`.

Embedded `Filesystem` state persists its `fscid`, nested `MDSMap`, and mirror metadata. `reset_filesystem()` intentionally preserves data pools, metadata pool, CAS pool, inline-data setting, name, standby count wanted, and stopped-rank history while rebuilding active/failure state around failed rank 0.

`mds_roles` is the cross-index that states whether a daemon GID is a standby (`FS_CLUSTER_ID_NONE`) or belongs to a filesystem. `standby_epochs` tracks the FSMap epoch associated with each standby. `legacy_client_fscid` identifies the filesystem used by clients that do not specify one.

## Dependencies And Integration Points

The file depends on `MDSMap`, `CompatSet`, Ceph buffer encoding, `ceph_clock_now`, `global_context`, monitor health-check types, strict integer parsing, debug logging, and C++20 ranges for sanity checks. It is integrated with `MDSMonitor`/`PaxosFSMap`, MDS beacon handling, `MFSMap` and `MFSMapUser` message production, `ceph status` formatting, filesystem admin commands, and pool deletion checks.

Mirror metadata integrates with CephFS mirroring control-plane APIs. Compatibility checks integrate with `MDSMap::compat`, daemon beacons, and upgrade policy. `sanitize()` integrates with OSDMap/pool existence checks by delegating to each `MDSMap`.

## Risks And Edge Cases

Consistency depends on keeping `filesystems`, embedded `mds_info`, `up`/`in`/`failed`/`damaged` sets, `standby_daemons`, `standby_epochs`, and `mds_roles` synchronized. `sanity()` documents many invariants and should be run on pending maps when changing transitions.

`operator=` copies `enable_multiple` but omits `ever_enabled_multiple` and `struct_version`, unlike the copy constructor. That can lose historical multiple-FS state if assignment is used on live maps. `erase_filesystem()` removes the filesystem but does not update `legacy_client_fscid` if the erased filesystem was the legacy target. Its loop over `fs.mds_map.get_mds_info()` appears to iterate a returned map copy, so `modify_daemon()` is relied on for actual updates.

`get_filesystem(void)` assumes at least one filesystem. `gid_has_rank()` uses `mds_roles.at(gid)` after `gid_exists()`, which is safe only if `mds_roles` remains complete. `parse_role()` rank-only input depends on `legacy_client_fscid`; multiple-filesystem clusters need explicit filesystem prefixes. Compatibility merging in `promote()` is allowed only for upgradeable filesystems and asserts otherwise.

## Test Signals

High-value tests include encode/decode round trips across struct versions 7 and 8, `generate_test_instances()` dencoder coverage, creation/commit with explicit and automatic FSCIDs, standby insert/promote/erase/stop/damaged/undamaged transitions followed by `sanity()`, standby selection with laggy/frozen/join_fscid/compat combinations, health-check output for failed ranks with and without replacements, and filesystem erase/swap effects on roles, names, legacy target, and pool-in-use checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/FSMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/FSMap.h -->
# sources/distributed-fs/ceph/src/mds/FSMap.h

## Purpose

`FSMap.h` declares the CephFS filesystem map data model used by monitors, MDS daemons, clients, and admin/status code. It represents multiple CephFS filesystems, the MDS ranks and daemons assigned to them, unassigned standby daemons, filesystem mirroring peers, compatibility sets, default legacy filesystem selection, and epoch/version metadata.

## Important APIs, Types, And Functions

`ClusterInfo` identifies a remote mirrored filesystem by client name, cluster name, and filesystem name. `Peer` adds a UUID and orders peers by UUID. `MirrorInfo` owns the `mirrored` flag and peer set with helpers to enable/disable mirroring, test peer existence by UUID or remote cluster info, add/remove peers, dump/print, and encode/decode.

`Filesystem` wraps one `MDSMap`, its `fs_cluster_id_t`, and `MirrorInfo`. Public APIs expose encode/decode, dump/print, `is_upgradeable()`, standby-replay lookup, `get_mds_map()`, `get_mirror_info()`, and `get_fscid()`. `FSMap` is a friend so only the aggregate can set `fscid` directly.

`FSMap` defines `STRUCT_VERSION = 8` and `STRUCT_VERSION_TRIM_TO = 7`. It exposes iterators over `filesystems`, default compatibility access, feature flag `set_enable_multiple()`, legacy FSCID access, filesystem lookup by ID/name/GID, role parsing, pool-use checks, health functions, print/dump functions, encode/decode, and `sanity()`.

The mutator surface is intentionally broad: `insert()`, `assign_standby_replay()`, `promote()`, `stop()`, `erase()`, `damaged()`, `undamaged()`, `create_filesystem()`, `commit_filesystem()`, `erase_filesystem()`, `reset_filesystem()`, `modify_filesystem()`, `swap_fscids()`, `modify_daemon()`, and `update_export_targets()`.

The protected state is the core schema: `epoch`, `btime`, `next_filesystem_id`, `legacy_client_fscid`, `default_compat`, `enable_multiple`, `ever_enabled_multiple`, `filesystems`, `mds_roles`, `standby_daemons`, and `standby_epochs`. Private `struct_version` records the decoded wire version.

## Control Flow And Data Flow

Read-only callers use lookup helpers to resolve names, GIDs, roles, and standby replacement choices. Admin and monitor code use mutators after validating commands and OSD pool state. The template helpers `modify_filesystem()` and `modify_daemon()` centralize timestamp/epoch updates after local changes and accept lambdas that can optionally return `false` to skip stamping.

Daemon role data flows through `mds_roles`. For standbys, the role maps to `FS_CLUSTER_ID_NONE` and details live in `standby_daemons`. For assigned daemons, the role maps to a filesystem and details live in that filesystem's `MDSMap::mds_info`. Accessors such as `get_info_gid()`, `fs_name_from_gid()`, `fscid_from_gid()`, `is_standby_replay()`, and `get_standby_replay()` rely on this invariant.

Filtering flow for restricted views uses `filter(const std::vector<std::string>& allowed)`, which removes filesystems not named in `allowed` and removes daemon-role entries whose filesystem name is not allowed.

## State And Persistence Behavior

The class is an encoded monitor map. Fields in the protected schema persist through `FSMap::encode()`. Each `Filesystem` persists a nested encoded `MDSMap`, giving this map both global monitor state and per-filesystem MDS state. `struct_version` is not part of normal construction but is populated by decode and used to identify old maps that may need monitor-side upgrading.

`ever_enabled_multiple` is sticky: `set_enable_multiple(true)` sets it permanently, while `enable_multiple` can be toggled. `legacy_client_fscid` may be `FS_CLUSTER_ID_NONE`, but if set should reference an existing filesystem. `next_filesystem_id` advances past explicit IDs to prevent reuse.

## Dependencies And Integration Points

Dependencies include `MDSMap`, `CompatSet`, Ceph feature and type headers, `Formatter`, `health_check_map_t`, `mds_role_t`, `fs_cluster_id_t`, `mds_gid_t`, `mds_rank_t`, and Ceph encoding macros. The file also polyfills `erase_if` for C++17 builds.

Integration points include monitor FSMap Paxos storage, MDS beacon and assignment logic, Ceph status output, admin command parsing, mirroring configuration, OSD pool safety checks, MDSMap health, and client-facing compact maps generated through `FSMapUser`.

## Risks And Edge Cases

Many accessors use `.at()` and assert-like invariants, so corrupt or partially updated maps fail hard. Any new mutator must update both the primary object and cross-indexes. `filter()` calls `fs_name_from_gid()` inside `erase_if` over `mds_roles`; this relies on roles still pointing to filesystems not yet erased or returning an empty view for standbys.

`get_filesystem()` with no arguments assumes at least one filesystem and returns the first map entry, not necessarily the legacy filesystem. Rank parsing can be ambiguous without a filesystem prefix. Template return-type detection in `modify_filesystem()` treats lambdas returning bool specially; accidental bool returns can suppress or trigger timestamping unexpectedly.

## Test Signals

Tests should compile both C++17 polyfill and newer builds, dencode `ClusterInfo`, `Peer`, `MirrorInfo`, `Filesystem`, and `FSMap`, and validate `sanity()` after every daemon/filesystem transition. Additional test signals include filtered maps containing only allowed filesystems, sticky `ever_enabled_multiple`, legacy FSCID assertions, correct standby-replay lookup, correct role parsing by name/ID/rank, and health checks that merge embedded `MDSMap` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/FSMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/FSMapUser.cc -->
# sources/distributed-fs/ceph/src/mds/FSMapUser.cc

## Purpose

`FSMapUser.cc` implements the compact client-facing filesystem map. It strips the full monitor `FSMap` down to epoch, legacy client filesystem ID, and filesystem `(cid, name)` pairs so clients can resolve filesystem names and IDs without receiving full MDS daemon topology.

## Important APIs, Types, And Functions

`FSMapUser::encode()` writes version 1 with `epoch`, `legacy_client_fscid`, and a vector of `fs_info_t` values built from the `filesystems` map. `decode()` reads the same vector, clears the map, and rebuilds it by `cid`.

`fs_info_t::encode()` and `decode()` persist only `cid` and `name`. `generate_test_instances()` creates a sample map with epoch 2, legacy FSCID 1, and two named filesystems.

`print()` emits a multiline human-readable representation. `print_summary()` emits either formatter fields or a compact stream form like `e<epoch>: name(cid) ...`.

## Control Flow And Data Flow

Monitor code builds an `FSMapUser` from the authoritative `FSMap` when sending `MFSMapUser` messages to client subscribers. The encode path converts the map to a vector because only `fs_info_t` values are transmitted; decode reconstructs the keyed map using each row's embedded `cid`.

Formatting flow is simple: formatter mode dumps `epoch` and repeated `id`/`name` pairs; stream mode emits all filesystem names and IDs on one line. The header helper `get_fs_cid(name)` performs linear lookup by filesystem name.

## State And Persistence Behavior

The encoded state is stable and intentionally small: `epoch`, `legacy_client_fscid`, and each filesystem's `cid`/`name`. No MDS ranks, pools, health, standby state, mirror info, or compat sets persist in this compact map. Because `filesystems` is keyed by `cid` after decode, duplicate CIDs in the encoded vector would collapse to the last decoded value.

Map iteration order is by `fs_cluster_id_t`, so the encoded vector and printed stream are deterministic for a given map. `legacy_client_fscid` may be `FS_CLUSTER_ID_NONE` when no default exists.

## Dependencies And Integration Points

The implementation depends on `FSMapUser.h`, Ceph encoding macros, `common/Formatter.h`, `mds/mdstypes.h` for role/string support, and monitor message code. `MDSMonitor` fills this object and sends it through `MFSMapUser`; clients use it to choose or resolve a CephFS filesystem.

## Risks And Edge Cases

Formatter mode dumps repeated `id` and `name` fields without opening an array or object per filesystem, so consumers expecting strict JSON arrays may need to handle repeated keys according to the formatter backend. `get_fs_cid()` is linear and returns the first matching name; duplicate names should be prevented by monitor validation, not by this class.

The compact encoding intentionally omits topology and health. Callers that need ranks, pools, or MDS states must use full `FSMap`/`MDSMap` paths. Any future fields require versioning without breaking old clients.

## Test Signals

Tests should dencode `FSMapUser` and `fs_info_t`, verify encode/decode round trips preserve epoch, legacy FSCID, names, and IDs, validate `get_fs_cid()` for existing and missing names, and check stream/formatter output for single and multiple filesystems. Integration tests should confirm monitor-generated `MFSMapUser` updates client filesystem name resolution after create, rename if supported, and remove events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/FSMapUser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/FSMapUser.h -->
# sources/distributed-fs/ceph/src/mds/FSMapUser.h

## Purpose

`FSMapUser.h` declares the compact, user/client-visible view of the filesystem map. It is smaller than `FSMap` and carries only the data needed to identify available CephFS filesystems by name and cluster ID plus the current map epoch and legacy default.

## Important APIs, Types, And Functions

`FSMapUser::fs_info_t` stores a filesystem `name` and `cid`, with feature-aware encode/decode. `FSMapUser` stores `filesystems`, `legacy_client_fscid`, and `epoch`.

Core methods are `get_epoch()`, `get_fs_cid(std::string_view name)`, `encode()`, `decode()`, `print()`, `print_summary()`, and `generate_test_instances()`. `WRITE_CLASS_ENCODER_FEATURES` registrations make both `fs_info_t` and `FSMapUser` available to Ceph's encoding/dencoder machinery. `operator<<` delegates to `print_summary()`.

## Control Flow And Data Flow

The class is a passive value object. Producers populate `filesystems` from the monitor's authoritative `FSMap`; encode transmits values to clients; decode reconstructs them; users call `get_fs_cid()` to resolve a name to ID. There is no daemon assignment or health logic here.

## State And Persistence Behavior

Encoded state is just epoch, legacy FSCID, and filesystem rows. The map key and each row's `cid` should match after decode, but the row's `cid` is the transmitted source of truth. No persistent state is kept outside the buffer encoding.

Because this type is feature-encoded but currently version 1, additions must preserve old client compatibility. The default values are `FS_CLUSTER_ID_NONE` for IDs and epoch 0.

## Dependencies And Integration Points

Dependencies include Ceph encoding, `fs_cluster_id_t`, `epoch_t`, `mdstypes.h`, `Formatter`, and C++ maps/strings. It integrates with `MFSMapUser` messages, `MDSMonitor` client session subscriptions, and client code that resolves named filesystems.

## Risks And Edge Cases

`get_fs_cid()` scans values and returns `FS_CLUSTER_ID_NONE` for both "not found" and the sentinel value, so callers cannot distinguish a missing name from an invalid/default ID without external validation. Duplicate filesystem names would make lookup order-dependent by numeric ID. The compact model can become stale; clients should compare epochs.

## Test Signals

Tests should cover default construction, name lookup, encode/decode round trips, operator stream output, and compatibility with monitor-generated messages. Negative tests should verify missing names return `FS_CLUSTER_ID_NONE` and empty maps print/encode without crashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/FSMapUser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/InoTable.cc -->
# sources/distributed-fs/ceph/src/mds/InoTable.cc

## Purpose

`InoTable.cc` implements the MDS rank inode-number allocation table. It tracks free inode numbers for one rank, supports projected allocations/releases for journaled operations in flight, applies committed changes, replays journal events after restart, and offers repair/tooling helpers for consuming inode numbers that were incorrectly marked free.

## Important APIs, Types, And Functions

`reset_state()` initializes this rank's inode range to `[(rank + 1) << 40, (rank + 2) << 40)`, stores it in `free`, and mirrors it into `projected_free`.

Single-ID allocation uses `project_alloc_id(id=0)` and `apply_alloc_id(id)`. A zero projected ID means allocate `projected_free.range_start()`. Batch allocation uses `project_alloc_ids(interval_set<inodeno_t>& ids, int want)` and `apply_alloc_ids(interval_set<inodeno_t>& ids)`. Release uses `project_release_ids()` and `apply_release_ids()`.

Replay APIs are `replay_alloc_id()`, `replay_alloc_ids()`, `replay_release_ids()`, and `replay_reset()`. They mutate both `free` and `projected_free` and set `projected_version = ++version` so replay catches up without outstanding projections.

Tooling/repair APIs are `skip_inos(inodeno_t count)`, `is_marked_free()`, `intersects_free()`, `repair(inodeno_t id)`, and `force_consume_to(inodeno_t ino)`. `dump()` emits both projected and committed free ranges, and `generate_test_instances()` supports dencoder coverage.

## Control Flow And Data Flow

Normal allocation flow is two-phase. Request handling calls a `project_*` method while the table is active; this removes IDs from `projected_free` and bumps `projected_version`. Once the journaled mutation commits, `apply_*` removes the same IDs from committed `free` and bumps `version`. Release mirrors this in reverse by inserting intervals into projected then committed state.

Replay flow consumes journal records after restart. Allocation replay checks the committed `free` set, logs cluster errors if journaled IDs are not free, subtracts only the intersection for batch replay, and advances both committed and projected versions. Release replay inserts IDs into both sets.

Repair flow refuses to repair while `projected_version != version`, because in-flight projections could conflict. If safe, it asserts the inode is marked free, erases it from both sets, and advances versions. `force_consume_to()` skips all free IDs from the current first free ID through a specified inode if that inode lies at or beyond the first free value.

## State And Persistence Behavior

The persistent state is the committed `free` interval set encoded by `InoTable::encode_state()` in the header. `decode_state()` restores `free` and sets `projected_free = free`. The projected set is runtime state for outstanding journal operations, not separately persisted.

`version` and `projected_version` come from `MDSTable` and track committed versus projected mutations. Replay deliberately synchronizes them after each journal event. `reset_state()` depends on the MDS rank value inherited from `MDSTable`.

## Dependencies And Integration Points

The implementation depends on `MDSTable`, `MDSRank`, `interval_set<inodeno_t>`, debug logging, and `mds->clog` for replay consistency errors. `MDSRank` constructs `InoTable`; journal event code calls project/apply/replay; `Server` and inode creation paths allocate IDs; `CInode` repair code uses `repair()` when a discovered inode number was marked free.

## Risks And Edge Cases

Allocation assumes `projected_free` is non-empty; `range_start()` on an empty set would fail. `project_alloc_id(id)` does not check that an explicit ID is in `projected_free` before erasing. `project_alloc_ids()` loops until `want` is satisfied and likewise assumes enough space exists. `force_consume_to()` computes `ino + 1 - first`, so extremely large `ino` values near the type limit need care.

Replay of inconsistent journal state logs errors but still advances versions, subtracting only the intersection for batch allocation. That avoids crashing recovery but can leave evidence only in cluster logs. The rank-based 40-bit range is static; any change to rank allocation semantics must preserve old table compatibility.

## Test Signals

Tests should verify reset range boundaries per rank, project/apply version movement, batch allocation across interval boundaries, release reinsertion and coalescing, encode/decode round trips, replay behavior for valid and invalid allocations, `repair()` refusal with outstanding projections, `force_consume()` and `force_consume_to()` behavior, and dump output for committed versus projected ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/InoTable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/InoTable.h -->
# sources/distributed-fs/ceph/src/mds/InoTable.h

## Purpose

`InoTable.h` declares the MDS inode-number allocation table. It is an `MDSTable` subclass named `inotable` whose encoded state is the set of unused inode IDs for an MDS rank, with a projected copy used to reserve IDs for journaled operations before they commit.

## Important APIs, Types, And Functions

Constructors initialize the base `MDSTable` with table name `"inotable"` and persistence enabled. Allocation methods are `project_alloc_id()`, `apply_alloc_id()`, `project_alloc_ids()`, and `apply_alloc_ids()`. Release methods are `project_release_ids()` and `apply_release_ids()`.

Replay methods are `replay_alloc_id()`, `replay_alloc_ids()`, `replay_release_ids()`, and `replay_reset()`. Repair/tooling methods are `repair()`, `is_marked_free()`, `intersects_free()`, `skip_inos()`, `force_consume()`, and `force_consume_to()`.

`encode_state()` writes version 2 and encodes only `free`. `decode_state()` reads `free` and initializes `projected_free` to match. Standalone `encode()`/`decode()` wrappers support dencoder. `dump()` and `generate_test_instances()` support diagnostics and serialization tests.

## Control Flow And Data Flow

The header exposes a two-phase allocation contract: callers first project changes against `projected_free`, journal the mutation, then apply the same changes to `free` after commit. Replay methods rebuild both sets from journal events. Tooling methods can consume IDs directly when repairing or adjusting a table offline or in controlled online repair paths.

`intersects_free()` is a safety query for detecting whether an external interval overlaps available IDs. `force_consume()` and `force_consume_to()` are explicitly documented for tools, not normal allocation.

## State And Persistence Behavior

`free` is committed persistent state. `projected_free` is runtime state rebuilt from `free` after decode/reset and changed by outstanding projected operations. Only `free` is encoded, so all in-flight projected operations must be represented by journal state or otherwise resolved during recovery.

Versioning is inherited from `MDSTable`; the implementation advances `version` for applied mutations and `projected_version` for projections/replay.

## Dependencies And Integration Points

Dependencies include `MDSTable`, `MDSRank`, `inodeno_t`, `interval_set`, Ceph buffer encoding, and `Formatter`. Integration points include inode creation, journal replay, table reset/recovery, MDSRank table lifecycle, dencoder tests, and repair code that reconciles discovered inode usage with free ranges.

## Risks And Edge Cases

The class relies on callers respecting active-state and projection/apply ordering. Explicit allocation of an ID outside `projected_free`, insufficient free ranges for a requested batch, or applying a different interval than projected can desynchronize committed and projected state. Since only `free` persists, crashes between projection and apply must be recoverable through journal replay.

The repair helpers bypass normal journaling assumptions if used incorrectly. They should be limited to tooling or guarded online repair paths. `is_marked_free()` returns true if either committed or projected state contains the ID, which is conservative for detecting conflicts but can surprise callers expecting only committed state.

## Test Signals

Tests should cover encode/decode compatibility, projected versus committed state after every project/apply pair, replay reset and replay mutation paths, repair guard on version mismatch, interval intersection results, and tool helpers consuming only intended ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/InoTable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/JournalPointer.cc -->
# sources/distributed-fs/ceph/src/mds/JournalPointer.cc

## Purpose

`JournalPointer.cc` implements durable RADOS load/save operations for the MDS journal pointer object. The pointer tells an MDS rank which journal inode is currently active (`front`) and which backup/reformat journal inode may exist (`back`).

## Important APIs, Types, And Functions

`get_object_id()` computes the fixed RADOS object name for the rank by adding `node_id` to `MDS_INO_LOG_POINTER_OFFSET` and formatting it as `<hex ino>.00000000`.

`load(Objecter*)` performs a blocking `read_full()` on the pointer object in `pool_id`, waits with `C_SaferCond`, decodes the object into `front` and `back`, and returns the objecter result or `-EINVAL` for decode errors.

`save(Objecter*) const` is the blocking write path. It asserts the objecter is non-null and the pointer is not null, encodes the pointer, writes the full object with `write_full()`, waits for completion, logs write errors, and returns the status.

`save(Objecter*, Context*) const` is the asynchronous variant. It encodes the pointer and submits `write_full()` with the supplied completion context. The comment says it assumes the caller already holds the objecter lock.

## Control Flow And Data Flow

MDLog creates a `JournalPointer` for the rank and metadata pool. On startup/recovery it calls `load()` to find existing journal locations. On journal creation or reformat, it updates `front`/`back` and calls a save variant to persist the new pointer. Data flows through Ceph buffer encoding into one RADOS object per MDS rank.

Error flow is deliberately simple. Missing/read-failed objects return the objecter error and leave the pointer as-is/null. Decode corruption maps to `-EINVAL`. Blocking writes return the objecter write status and log negative results; asynchronous writes leave error handling to the completion path.

## State And Persistence Behavior

The durable state is the encoded `front` and `back` inode numbers stored in the metadata pool object named by rank. `node_id` and `pool_id` are not encoded; they are local addressing parameters. `is_null()` means both inode numbers are zero, and the blocking save path refuses to persist such a null pointer.

Writes use `write_full()`, replacing the whole pointer object. Reads use `read_full()`, so partial state is not interpreted. The timestamp passed to writes is `ceph::real_clock::now()`.

## Dependencies And Integration Points

Dependencies include `JournalPointer.h`, `mdstypes.h`, `Objecter`, `Messenger` for debug prefix identity, `C_SaferCond`, `cpp_strerror`, object locators, and snap context. Integration is primarily with `MDLog.cc`, including asynchronous pointer writes and journal reformat logic.

## Risks And Edge Cases

The asynchronous `save()` does not assert `!is_null()`, unlike the blocking variant, so callers can accidentally persist a null pointer through that path. `get_object_id()` depends on valid `node_id`; the default constructor leaves `node_id = -1` and `pool_id = -1`, so load/save on a default object would address invalid storage. Decode errors return `-EINVAL` without logging details beyond the caller's handling.

Because this object is the root of journal discovery, stale or corrupted pointer contents can prevent MDS recovery or send it to the wrong journal inode. Objecter write/read error handling must distinguish missing pointer during first initialization from real I/O failures.

## Test Signals

Tests should cover object ID formatting for rank values, encode/decode round trips, blocking save refusing null pointers, load returning `-EINVAL` on malformed data, load behavior for missing objects, asynchronous save behavior and completion error propagation, and MDLog recovery/reformat paths that update `front` and `back` correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/JournalPointer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/JournalPointer.h -->
# sources/distributed-fs/ceph/src/mds/JournalPointer.h

## Purpose

`JournalPointer.h` declares the small encoded object that records where an MDS rank's journal lives. It always lives at a rank-derived RADOS object location and stores the active journal inode plus an optional backup journal inode.

## Important APIs, Types, And Functions

The public data fields are `front` for the active journal and `back` for the backup journal. Constructors either accept `(node_id, pool_id)` addressing parameters or leave a default object with invalid addressing values.

`encode()`/`decode()` version 1 persist `front` and `back`. `load(Objecter*)`, blocking `save(Objecter*)`, and asynchronous `save(Objecter*, Context*)` are implemented in the `.cc` file. `is_null()` checks both journal inode fields. `dump()` emits a `journal_pointer` object with `front` and `back`. `generate_test_instances()` provides a null and non-null sample for dencoder. `get_object_id()` is private and computes the RADOS object key.

## Control Flow And Data Flow

Callers construct the object with the MDS rank and metadata pool, then load or save it through an `Objecter`. The value is passive apart from persistence helpers: MDLog owns the higher-level journal state machine and updates `front`/`back`.

## State And Persistence Behavior

Only `front` and `back` are encoded. `node_id` and `pool_id` determine where the encoded object is stored and must be supplied by the caller. A null pointer is represented as both fields zero and is valid in memory, but blocking save treats it as invalid to persist.

The class uses `WRITE_CLASS_ENCODER(JournalPointer)`, so dencoder and Ceph buffer machinery can serialize it independently of RADOS object I/O.

## Dependencies And Integration Points

Dependencies include `Formatter`, `inodeno_t`, Ceph encoding, `mdstypes.h`, `Context`, and `Objecter`. Integration points are `MDLog` startup/recovery, journal reformat, journal pointer object I/O, and diagnostics.

## Risks And Edge Cases

The default constructor is useful for decode/test instances but not for RADOS I/O because `node_id` and `pool_id` remain `-1`. The header exposes `front` and `back` as mutable public fields, so correctness depends on MDLog updating them in valid sequences. A future encoding change must preserve recovery compatibility because old pointer objects are required for MDS startup.

## Test Signals

Tests should validate dencoder coverage, `is_null()`, dump output, RADOS object load/save integration through mocked or real Objecter, and MDLog behavior when no pointer, only `front`, or both `front` and `back` are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/JournalPointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LocalLockC.h -->
# sources/distributed-fs/ceph/src/mds/LocalLockC.h

## Purpose

`LocalLockC.h` declares a local-only metadata cache lock built on `SimpleLock`. It is used for lock types that do not participate in distributed lock state the same way normal inode/dentry locks do, while still supporting local xlock/wrlock coordination inside the MDS.

## Important APIs, Types, And Functions

`LocalLockC(MDSCacheObject*, const LockType*)` forwards to `SimpleLock` and immediately sets state to `LOCK_LOCK`, meaning the lock is always considered locally locked. `is_locallock()` overrides the base to return true.

`can_xlock_local()` permits a local exclusive lock when there are no write locks and no existing xlock owner. `can_wrlock()` permits a write lock when the lock is not xlocked and there is no waiter for `SimpleLock::WAIT_XLOCK`.

`get_wrlock(client_t client)` asserts `can_wrlock()`, takes the base write lock, and records `last_wrlock_client`. `put_wrlock()` releases a base write lock and clears `last_wrlock_client` once the write-lock count drops to zero. `get_last_wrlock_client()` exposes that recorded client. `print()` extends base lock printing with `last_client` when nonnegative.

## Control Flow And Data Flow

Locker code treats `LocalLockC` specially through `local_wrlock_grab()`, `local_wrlock_start()`, and `local_xlock_start()`. Cache objects such as `CInode` and `CDentry` embed local locks for version/quiesce-style coordination. Lock acquisition flows through the base `SimpleLock` counters/waiters, with this wrapper adding client attribution for the latest write lock.

## State And Persistence Behavior

The lock state is purely in-memory and is not encoded. Persistent metadata is protected by operations using the lock, but the lock itself resets with the cache object. The only local field is `last_wrlock_client`, which is cleared when no write locks remain.

## Dependencies And Integration Points

The class depends on `SimpleLock`, `MDSCacheObject`, `LockType`, `client_t`, base lock waiters, and output printing. Integration points include `CInode`'s `quiescelock` and `versionlock`, `CDentry`'s `versionlock`, and `Locker.cc` local lock acquisition paths.

## Risks And Edge Cases

`last_wrlock_client` is not explicitly initialized in the constructor. It is printed only if `>= 0`, but without initialization the first print or read before `get_wrlock()` can be undefined. `get_wrlock()` records only one client even if multiple write locks are held; it represents the last acquisition, not a complete owner set. `can_wrlock()` blocks new write locks when an xlock waiter exists, which gives xlock waiters priority but can affect write-heavy paths.

Because the lock is always in `LOCK_LOCK`, code expecting normal distributed lock state transitions should not use this class. Misclassifying a distributed lock as local would bypass inter-MDS coordination.

## Test Signals

Tests should validate constructor state, `is_locallock()`, wrlock/xlock exclusion rules, xlock waiter priority, `last_wrlock_client` set/clear behavior across nested write locks, and print output. A regression test should initialize or check `last_wrlock_client` before first use to prevent undefined diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LocalLockC.h -->
