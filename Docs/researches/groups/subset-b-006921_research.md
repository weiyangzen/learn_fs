# Research: subset-b-006921

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/flock.cc -->
## sources/distributed-fs/ceph/src/mds/flock.cc

`flock.cc` implements CephFS MDS byte-range lock state for `ceph_lock_state_t`, covering held locks, blocked waiters, lock coalescing/splitting, and limited POSIX deadlock detection. The active state is split between persisted `held_locks` plus `client_held_lock_counts`, and runtime-only `waiting_locks`, `client_waiting_lock_counts`, and a file-static `global_waiting_locks` wait graph used only for `CEPH_LOCK_FCNTL`.

Important entry points are `add_lock`, `remove_lock`, `look_for_lock`, `remove_waiting`, `remove_all_from`, `encode`, `decode`, and `dump`. `add_lock` finds overlapping held locks, separates same-owner locks with `split_by_owner`, blocks on conflicting exclusive/shared ranges, optionally checks `is_deadlock`, and otherwise calls `adjust_locks` before inserting the normalized new lock. `remove_lock` trims, splits, or erases same-owner held locks in the requested range and updates client counts. The range helpers treat `length == 0` as "to EOF", so overflow and endpoint logic are central to correctness.

Deadlock detection is intentionally bounded by `MAX_DEADLK_DEPTH` and follows `global_waiting_locks` from owners of conflicting locks to locks they are waiting on. This is process-wide static state, so destructor and removal paths must remove entries to avoid stale wait graph edges. Persistence is narrow: waiting queues are not encoded, so replay restores only granted locks and client held counts.

Dependencies include `include/ceph_fs.h` lock constants and layout, `client_t`, Ceph buffer encoders, `Formatter`, and MDS debug logging. Integration is with client file locking and reconnect/journal paths that serialize `ceph_lock_state_t`.

Risks: off-by-one range math, `uint64_t(-1)` EOF handling, stale global wait entries, blocked waiter loss across failover, and count/map skew when erasing iterators. Test signals are lock encode/decode round trips, overlapping shared/exclusive scenarios, same-owner merge/split coverage, client cleanup, deadlock-chain cases, and replay behavior proving waiting locks are intentionally absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/flock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/flock.h -->
## sources/distributed-fs/ceph/src/mds/flock.h

`flock.h` declares the MDS file-lock state container and ordering helpers around `ceph_filelock`. It defines owner equality and ordering semantics that preserve compatibility with old clients: modern owners are identified by `client` plus high-bit-set `owner`, while old clients also require `pid`.

The public API exposes waiter inspection/removal, lock acquisition, conflict lookup, range unlock, client-wide cleanup, Ceph encoding/decoding, formatter dumping, and generated test instances. `held_locks` and `waiting_locks` are both multimaps keyed by starting offset; client count maps are maintained for fast empty/client cleanup checks. Private helpers cover recursive deadlock detection, waiter insertion, range normalization, lower-bound lookup, overlap discovery, self-neighbor coalescing, owner partitioning, and exclusive-lock discovery.

State behavior is explicitly mixed durable/runtime. The header exposes all four maps, but the implementation persists only held locks and held counts. `type` and `cct` are constructor/runtime values, and waiting state is a transient scheduling aid. The API also returns activated locks from `remove_lock`, although this implementation currently only mutates held state and leaves activation policy to higher layers.

Dependencies are lightweight but important: `ceph_filelock` from `include/ceph_fs.h`, `client_t`, Ceph buffer/formatter forward declarations through used signatures, and standard maps/lists. Integration points are MDS locker code, session reconnect (`cap_reconnect_t` carries flock blobs), and journal/recovery code that expects durable state to round-trip.

Risks: external code can mutate public maps without preserving counts, comparator behavior affects multimap lookup and global wait graph keys, and old/new client owner compatibility must remain stable. Test signals should focus on comparator ordering, old-client pid semantics, public encode/decode compatibility, empty-state behavior, and acquisition/removal paths through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/flock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/fscrypt.h -->
## sources/distributed-fs/ceph/src/mds/fscrypt.h

`fscrypt.h` is a small CephFS MDS header defining `ceph_fscrypt_last_block_header`, the metadata prefix used to describe encrypted last-block handling. It carries a format version, compatibility byte, serialized data length, inode `change_attr`, file offset, and encryption block size.

The struct is data-only and has no local encode/decode methods in this file, so any persistence behavior depends on callers treating the layout consistently. `data_len` is documented as the size of `change_attr + file_offset + block_size`, with possible extra block-size data when the final block is in a hole. `file_offset` is zero for a hole or the write offset for the last block. `block_size` is expected to equal the fscrypt block size.

Dependencies are only integer types from the wider Ceph build environment (`__u8`, `uint32_t`, `uint64_t`). Integration is with encrypted file I/O and metadata paths that need to store or interpret the last encrypted block, especially sparse-file hole cases where the data payload may not be a direct file extent.

Risks are mostly ABI/schema risks: no packing directive appears here, so callers must not assume an external wire layout unless an enclosing encoder controls it; version/compat fields need validation by consumers; and inconsistent `data_len` or `block_size` can lead to truncated or over-read encrypted tail data. Test signals are encode/decode or denc tests in consumers, sparse-file encrypted writes, last-block rewrite after inode change-attr changes, and cross-version compatibility cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/fscrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/inode_backtrace.cc -->
## sources/distributed-fs/ceph/src/mds/inode_backtrace.cc

`inode_backtrace.cc` implements serialization, dumping, test fixtures, comparison, and stream output for inode backpointers/backtraces. These structures are used as standalone ancestry records, commonly stored with object metadata to reconstruct or verify where an inode lives in the namespace.

`inode_backpointer_t` encodes directory inode, dentry name, and child version using struct version 2, with `decode_old` for legacy unframed vector entries. `inode_backtrace_t` encodes inode number, ordered ancestor vector, current data pool, and old pools using struct version 5. Decode rejects very old struct versions by returning early for `struct_v < 3`, handles pre-v4 ancestor layout manually, and only reads pool fields at v5+.

The key behavior is `inode_backtrace_t::compare`. It compares two backtraces for the same inode by ancestor versions and dentries, reports whether dentries are equivalent, and flags divergent history when version ordering contradicts path differences. The comparator uses the first ancestor as initial freshness signal, then walks the common prefix while tracking incompatible version direction.

Dependencies include Ceph buffer encoding macros, `Formatter`, `inodeno_t`, `version_t`, and STL strings/vectors. Integration points are backtrace storage during journal segment expiry (`store_backtrace` in `journal.cc`), metadata scrub/repair, object locator changes across pools, and diagnostic formatting.

Risks: old version decode returns a default object silently for ancient data, compare assumes same-inode precondition but does not enforce it, and pool/old-pool history must match actual backtrace writes during data-pool migration. Test signals include generated encode/decode instances, legacy ancestor decoding, compare cases for equal paths/newer versions/divergent versions, and journal expiry tests that commit backtraces in current and old pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/inode_backtrace.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/inode_backtrace.h -->
## sources/distributed-fs/ceph/src/mds/inode_backtrace.h

`inode_backtrace.h` declares two ancestry types: `inode_backpointer_t`, a single parent directory/dentry/version pointer, and `inode_backtrace_t`, a complete standalone chain for one inode. The header frames backtraces as metadata backpointers that can outlive cache context, for example as xattrs on objects.

`inode_backpointer_t` exports encode/decode, legacy decode, formatter dump, generated instances, equality, and stream output. Its durable fields are `dirino`, `dname`, and `version`. `inode_backtrace_t` exports encode/decode/dump/test, `compare`, `clear`, equality, and stream output. Its durable fields are `ino`, ordered `ancestors`, current `pool`, and `old_pools`.

State behavior is simple but critical to recovery. The ancestor order and versions are the evidence used to decide which of two namespace histories is newer or divergent. `old_pools` lets backtrace repair/update account for objects that previously lived outside the current pool. The `clear` method intentionally leaves `ino` and `pool` untouched while clearing ancestry and old pools.

Dependencies are Ceph buffer types, formatter forward declaration, `inodeno_t`, `version_t`, strings, and vectors. Integration points include `CInode` backtrace commit operations, journal segment expiry, metadata scrub, data-pool migration, and damage repair.

Risks: callers must compare only backtraces for the same inode; missing or stale ancestors can make repair choose the wrong namespace location; and old-pool information must be kept in sync with inode pool state. Test signals are equality and encode/decode round trips, old-format decode, compare divergence/equivalence matrices, and object backtrace updates during journal trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/inode_backtrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/journal.cc -->
## sources/distributed-fs/ceph/src/mds/journal.cc

`journal.cc` implements CephFS MDS journal event serialization, replay, and log-segment expiry coordination. It connects event classes such as `EMetaBlob`, `EUpdate`, `EOpen`, `ESession`, `ETableServer`, `EPeerUpdate`, `ESubtreeMap`, `EFragment`, `EExport`, and import/reset/no-op events to live `MDSRank`, `MDCache`, `MDLog`, `Locker`, session map, inode table, and table server/client state.

`LogSegment::try_to_expire` is the central durability gate for trimming old journal segments. It gathers dirty dirfrags, dentries, inodes, uncommitted peer/leader ops, fragments, scatterlocks, open files, backtraces, inode/session/table versions, truncates, and purge work. It schedules commits or waiters and only allows expiry when all relevant durable state has caught up. Backtraces are batched through `BatchCommitBacktrace` and `BatchStoredBacktrace`, including old-pool updates when inode pool history is dirty.

`EMetaBlob` is the main metadata delta container. It records directory context, full/remote/null dentries, roots, table tids, inode allocation/session effects, truncates, destroyed inodes, client request/flush completion, and rename information. Replay rebuilds or updates roots, dirfrags, dentries, inodes, subtree auth, unlinked inode handling, inotable/sessionmap versions, open-file table notes, truncation recovery, and completed requests. It includes damage paths for missing dirs, invalid file layouts, malformed event ops, and optional debug corruption injection.

Other event classes layer on top of metablob replay: `EUpdate` handles client/session maps and uncommitted leaders; `EPeerUpdate` handles prepare/commit/rollback with preserved rollback blobs; `ETableServer` and `ETableClient` replay distributed table transactions; `ESubtreeMap` verifies or reconstructs subtree auth maps; `EFragment` replays dirfrag split/merge prepare/commit/rollback; export/import events adjust bounded subtree authority and ambiguous imports; `EResetJournal` wipes session/inode allocation state and re-establishes root/mydir auth.

Persistence is versioned with Ceph encoding macros throughout, with many legacy decode branches. Risks are high because replay mutates live cache state: event ordering assumptions, version mismatch repair, stale ambiguous imports, lost uncommitted peers, invalid layouts, and heartbeat starvation in large replays. Test signals include journal encode/decode corpus tests, MDS failover/replay suites, subtree migration/import-export tests, fragment rollback tests, session/inotable mismatch injection, log trimming, scrub/backtrace persistence, and damage-path assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/journal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/locks.c -->
## sources/distributed-fs/ceph/src/mds/locks.c

`locks.c` defines the static lock state-machine tables used by CephFS MDS cache locks. It is C rather than C++ and duplicates capability bit constants from `ceph_fs.h` so it can initialize plain C structures declared in `locks.h`.

The exported tables are `sm_simplelock`, `sm_scatterlock`, `sm_filelock`, and `sm_locallock`. Each points at a `sm_state_t[LOCK_MAX]` array describing, per lock state, the stable target state, loner mode, replica-visible state, read/projected-read/read-lock/write-lock/force-write/lease/xlock permissions, and cap masks for normal/loner/xlocker/replica cases. The `sm_t` wrapper also declares capabilities that may ever be issued to auth or replica holders, which cap bits require careful handling, and whether remote xlock is allowed.

Control flow is table-driven outside this file: locker code indexes these arrays by `LOCK_*` enum values and interprets permission fields such as `ANY`, `AUTH`, `XCL`, and `REQ`. `simplelock` covers generic metadata locks, `scatterlock` adds sync/lock/mix/temp-sync behavior for distributed counters, `filelock` adds file cap states including cache/read/write/buffer/lazyio and xsync/excl/mix transitions, and `locallock` is a minimal auth-local lock state.

Persistence is indirect: these tables are not persisted themselves, but their state numbers and capability masks govern journaled/cache lock transitions and client cap issuance. Changing table entries can alter replay behavior for locks restored from encoded inode/dir state.

Risks: enum/table index drift, incorrect cap mask combinations causing client over-issuance or unnecessary recalls, C/C++ constant duplication, and subtle transition regressions. Test signals are locker state-machine unit tests, client cap recall/issue integration tests, scatterlock flush tests, failover replay with dirty locks, and mixed auth/replica lock transition coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/locks.h -->
## sources/distributed-fs/ceph/src/mds/locks.h

`locks.h` declares the table-driven MDS cache-lock state-machine schema and the complete `LOCK_*` state/action enum set. It is consumed by both C and C++ code and exposes four external state machines: simple, file, scatter, and local locks.

`sm_state_t` is the core row format. `next` identifies the stable state for transitional states, `loner` indicates exclusive client mode, `replica_state` is what replicas should see, permission chars encode read/projected-read/rdlock/wrlock/force-wrlock/lease/xlock availability, and cap masks describe caps for normal, loner, xlocker, and replica holders. `sm_t` binds a state array to global allowed/careful caps and remote-xlock policy.

The enum assigns numeric values for stable states (`LOCK_SYNC`, `LOCK_LOCK`, `LOCK_EXCL`, `LOCK_MIX`, `LOCK_TSYN`, `LOCK_XSYN`, `LOCK_SCAN`) and many transition states (`LOCK_SYNC_LOCK`, `LOCK_LOCK_SYNC`, `LOCK_PREXLOCK`, etc.). Action constants distinguish replica-directed negative actions from auth-directed positive actions.

State/persistence behavior is by convention: encoded locks elsewhere store enum values, while this header fixes their meaning. Any change in ordering is a compatibility change. Integration points include `SimpleLock`, `ScatterLock`, `Locker`, client capability calculation, journal replay, and MDS replica/auth coordination.

Risks: enum reorder breaks persisted or networked states; permission token semantics are compact and easy to misread; table consumers must handle zero/uninitialized rows; and negative/positive action direction must remain consistent. Test signals are compile coverage from C/C++ users, cap string/locker tests, replay of existing journal states, and assertions around `LOCK_MAX` table bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mds_table_types.h -->
## sources/distributed-fs/ceph/src/mds/mds_table_types.h

`mds_table_types.h` centralizes small enum definitions and printable names for MDS distributed metadata tables and table operations. It currently identifies `TABLE_ANCHOR` and `TABLE_SNAP`, table-server protocol operation codes, and generic table mutation operations.

The inline helpers `get_mdstable_name`, `get_mdstableserver_opname`, and `get_mdstable_opname` map enum integers to stable strings for logs, dumps, and journal replay diagnostics. Invalid values call `ceph_abort()`, intentionally treating unknown table or op codes as fatal programmer/journal corruption errors.

State behavior is indirect but compatibility-sensitive. `journal.cc` stores table ids and operation ids in `ETableServer`, `ETableClient`, and `EMetaBlob::table_tids`; replay switches on these constants and uses the name helpers for logging. Because these values cross journal/network boundaries, changing numeric assignments would break older logs or messages.

Dependencies are minimal: `std::string_view` and `ceph_assert.h` for `ceph_abort`. Integration points include `MDSTableServer`, `MDSTableClient`, `MMDSTableRequest`, journal replay, and any table-specific implementation such as anchor/snap tables.

Risks: adding new tables or ops requires updating all switch helpers and replay logic; abort-on-unknown is useful for corruption detection but harsh for forward compatibility; negative server op values encode reply/client-directed meanings that must match message handling. Test signals include table op encode/decode, journal replay of prepare/commit/rollback/server-update/ack, and logging/dump tests for all enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mds_table_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mdstypes.cc -->
## sources/distributed-fs/ceph/src/mds/mdstypes.cc

`mdstypes.cc` implements serialization, JSON decode, dump, stream output, and generated test instances for many core MDS value types declared in `mdstypes.h`. These types describe dirfrag statistics, recursive directory stats, quotas, writeable ranges, inline data, fnode state, feature bitsets, client metadata/session info, dentries, table pending records, request ids, cache object ids, load vectors, reconnect records, replay-time diagnostics, block diffs, and subvolume metrics.

Most functions are versioned Ceph encoders/decoders. Compatibility branches preserve old fields such as removed `ranchors`, old `completed_requests` sets, older client metadata maps, reconnect formats before flock/snap-follow fields, and fnode versions before damage/scrub fields. Several `decode_json` methods support admin/JSON ingestion for stat-like structs.

Important logic includes `feature_bitset_t` parsing from comma-separated bit numbers, packed byte-length encode/decode for arbitrary feature vectors, `dentry_key_t` string encoding as `name_head` or `name_hexsnap`, `session_info_t` merging old used/preallocated inode sets, `cap_reconnect_t` embedding a raw flock buffer using `capinfo.flock_len`, and load vector meta-load weighting for dirfrag balancing. `MDSCacheObjectInfo` compares either inode/snap identity or dirfrag+dentry identity depending on whether `ino` is present.

Dependencies include Ceph buffer macros, JSON decoder, `Formatter`, `DecayCounter`, entity names, interval sets, caps, and generated/raw encoders from the Ceph type system. Integration spans session map persistence, client reconnect, MDS balancer load reporting, journal/table replay, cache-object messaging, scrub and damage flags, and subvolume metric aggregation.

Risks: versioned decode defaults can silently drop newer/older fields, `dentry_key_t::decode_helper` assumes an underscore separator, feature bitset string parsing can throw, cap reconnect relies on raw buffer lengths, and session replay must preserve idempotency. Test signals are generated encode/decode corpus tests, legacy decode fixtures, JSON decode tests, reconnect with file locks and snap realms, balancer load dumps, and subvolume metric v1/v2 compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mdstypes.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mdstypes.h -->
## sources/distributed-fs/ceph/src/mds/mdstypes.h

`mdstypes.h` is the central CephFS MDS type header for identifiers, inode namespace constants, capability string helpers, old inode/xattr containers, directory stats, client/session metadata, dentry keys, table transactions, reconnect structures, dirfrag identities, load vectors, authority pairs, cache object identifiers, replay timing, block diffs, and subvolume metrics.

The header defines private/system inode ranges (`MDS_INO_*`), `mds_role_t`, cap string helpers, `old_inode_t`, `fnode_t`, `old_rstat_t`, `feature_bitset_t`, `metric_spec_t`, `client_metadata_t`, `session_info_t`, `dentry_key_t`, `string_snap_t`, `mds_table_pending_t`, `metareqid_t`, `cap_reconnect_t`, `snaprealm_reconnect_t`, old reconnect compatibility structs, `dirfrag_t`, `inode_load_vec_t`, `dirfrag_load_vec_t`, `mds_load_t`, authority constants, `MDSCacheObjectInfo`, `EstimatedReplayTime`, `BlockDiff`, and `SubvolumeMetric`.

State and persistence behavior is pervasive: nearly every struct has Ceph encode/decode contracts or `DENC`, many with explicit struct versions. `session_info_t` is documented as the durable part of a session; `fnode_t` holds persistent dirfrag accounting, damage, and scrub stamps; reconnect types capture client cap and snaprealm state for MDS recovery; and load vectors are decay-counter snapshots used for balancing rather than strict namespace correctness.

Dependencies include low-level Ceph integer/fs/cap types, `frag_t`, `interval_set`, `utime_t`, `DecayCounter`, entity names, formatter/dump helpers, and STL containers. Integration points include almost every MDS subsystem: MDCache, Locker, SessionMap, Journal, Migrator, Balancer, table services, client reconnect, scrub, and admin dumps.

Risks: macros encode persistent inode ranges and must remain stable; many inline comparators/hashers define map identity; public structs invite inconsistent mutation; old/new allocator templates must match mempool expectations; and version fields must be advanced carefully. Test signals are broad encode/decode generated tests, static assertions around inode ranges, cap formatting tests, reconnect/failover tests, dentry-key parsing, load-vector dumps, and subvolume metric v1/v2 denc compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mdstypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/snap.cc -->
## sources/distributed-fs/ceph/src/mds/snap.cc

`snap.cc` implements CephFS MDS snapshot descriptors and snap realm records. It provides versioned encoding/decoding, formatter dumps, generated test instances, and stream output for `SnapInfo`, `snaplink_t`, and `sr_t`.

`SnapInfo` stores one snapshot id, source inode, timestamp, name, alternate name, metadata map, and a mutable cached long name. Encoding is version 4 with metadata at v3+ and alternate name at v4+. `get_long_name` lazily formats `_<name>_<ino>` and invalidates by checking the cached string against current `name` shape. `snaplink_t` records a past parent inode and the first snap id for that parent relationship.

`sr_t` is the durable snap realm version: sequence, creation/destruction watermarks, current-parent-since, snap map, past parent map, past parent snap set, last-modified timestamp, change attr, and flags for parent-global, subvolume, and snapdir visibility. Decode handles an odd v2 extra byte, v5+ past parent snaps, v6+ flags, and v7+ timestamp/change attr. It upgrades old records so snapdir visibility is enabled in memory for pre-v8 data.

Dependencies are Ceph snap/object/utime/buffer types and `Formatter`. Integration points include `SnapRealm`, snapshot table/event replay, inode snap blobs in `journal.cc`, subvolume handling, and admin dumps.

Risks: cached `long_name` invalidation is string-shape based; old decode paths need precise compatibility; flags defaulting affects user-visible `.snap` behavior after upgrade; and snap maps are central to correct clone/past-parent lookup. Test signals include encode/decode across struct versions, visibility flag upgrade cases, snap realm dump output, long-name cache changes after rename/name mutation, and journal replay of snap blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/snap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/snap.h -->
## sources/distributed-fs/ceph/src/mds/snap.h

`snap.h` declares persistent MDS snapshot metadata structures. `SnapInfo` is a generic snapshot descriptor; `snaplink_t` records historical parent realm links; `sr_t` carries a complete durable version of a `SnapRealm`.

`SnapInfo` exposes encode/decode/dump/test generation, equality, stream output, and `get_long_name`. Fields are snapshot id, inode, timestamp, name, alternate name, cached long name, and metadata. Equality intentionally ignores alternate name, long-name cache, and metadata. `snaplink_t` has inode and first-snap fields plus standard encode/dump/test/stream APIs.

`sr_t` provides flag mutators for parent-global, subvolume, and snapdir visibility, plus encode/decode/dump/test/print. Durable fields include realm sequence, creation/destruction ids, parent-history maps, snap set, last modification time, change attribute, and flags. The default flags enable snapdir visibility.

State/persistence behavior is tightly tied to namespace snapshots. `seq` versions realm changes, `last_created`/`last_destroyed` bound visible snapshot sets, and past-parent state supports resolving historical paths after realm movement. `change_attr` tracks attribute mutations. The flag helpers define in-memory semantics that the implementation preserves through versioned decode upgrades.

Dependencies are Ceph `snapid_t`, `inodeno_t`, `utime_t`, buffer encoders, object types, and STL maps/sets. Integration points include `SnapRealm`, MDCache snapshot propagation, journal metablob snap blobs, subvolume metadata, and admin formatting.

Risks: equality omits metadata/alternate name, so callers must not use it for full record equivalence; default snapdir visibility is compatibility-sensitive; and parent history maps must be kept consistent with realm moves. Test signals are generated encode/decode, flag mutation tests, equality semantics checks, snap realm migration/history tests, and upgrade decode fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/snap.h -->
