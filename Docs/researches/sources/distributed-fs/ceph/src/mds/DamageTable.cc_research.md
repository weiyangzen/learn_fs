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
