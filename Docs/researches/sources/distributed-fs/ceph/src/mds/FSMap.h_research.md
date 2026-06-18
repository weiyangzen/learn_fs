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
