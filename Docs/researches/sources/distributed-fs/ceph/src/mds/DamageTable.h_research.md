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
