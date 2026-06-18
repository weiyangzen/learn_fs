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
