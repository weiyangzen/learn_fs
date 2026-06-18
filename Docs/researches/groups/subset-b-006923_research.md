# subset-b-006923 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/FSCommands.cc -->
# sources/distributed-fs/ceph/src/mon/FSCommands.cc

## Purpose
`FSCommands.cc` implements CephFS monitor command handlers used by `MDSMonitor` to mutate `FSMap` and related OSD pool application metadata. It covers filesystem creation/removal/reset/rename/swap, pool attachment/removal, filesystem option updates, compatibility bits, required client features, mirroring flags/peers, and destructive fail paths.

## Important APIs, Types, and Functions
The file defines concrete `FileSystemCommandHandler` subclasses: `FlagSetHandler`, `FailHandler`, `FsNewHandler`, `SetHandler`, `CompatSetHandler`, `RequiredClientFeaturesHandler`, `AddDataPoolHandler`, `SetDefaultHandler`, `RemoveFilesystemHandler`, `ResetFilesystemHandler`, `RenameFilesystemHandler`, `SwapFilesystemHandler`, `RemoveDataPoolHandler`, mirror enable/disable/peer handlers, and `AliasHandler<T>`. Shared helpers are `FileSystemCommandHandler::load`, `_check_pool`, `is_op_allowed`, `set_val`, and the local `modify_filesystem`.

## Control Flow
`MDSMonitor::prepare_command()` iterates handlers from `FileSystemCommandHandler::load()`. `can_handle()` matches command prefix and validates FS write caps except for global `fs new` and `fs flag set`. Handler `handle()` methods validate command arguments, modify pending `FSMap`, and sometimes request OSDMonitor proposals. Pool-affecting commands wait for `osdmon()->is_writeable()` and return `-EAGAIN` after scheduling retry when OSDMap mutation or blocklisting is required.

## State and Persistence
This file does not persist directly. It mutates the pending `FSMap` that `MDSMonitor::encode_pending()` later stores in Paxos. Pool application metadata, metadata-pool recovery priority, PG autoscale settings, and MDS blocklists are delegated to `OSDMonitor` pending state. `set_val()` modifies `MDSMap` fields such as `max_mds`, flags, session timeouts, standby replay, balancing, snapshot compatibility, and required client behavior.

## Dependencies and Integration Points
It integrates tightly with `Monitor`, `MDSMonitor`, `OSDMonitor`, `MgrStatMonitor`, `Paxos`, `FSMap`, `Filesystem`, `MDSMap`, `OSDMap`, pool metadata, command parsing helpers, and CephFS feature-name conversion. Destructive operations consult `MDSMonitor::has_health_warnings()` and use the shared unhealthy-MDS confirmation message.

## Risks
Many operations are operationally disruptive and rely on explicit confirmation flags. Renames and swaps require offline filesystems, refused client sessions, disabled mirroring, correct FSCIDs, and synchronized pool application tags. `_check_pool()` must reject unsafe pool reuse, snapshots, metadata EC pools, invalid cache-tier behavior, and non-CephFS applications. The `set_val()` path is broad and has subtle interactions with old snapshots, standby replay failure, deprecated settings, and stale `fsp` views after mutation.

## Test Signals
Useful tests should cover each command prefix, capability filtering, idempotent delete/rename/swap cases, OSD writeability retry, pool suitability failures, dangerous confirmations, `fs new` with option setting, data-pool app tags, required client feature add/remove by name and id, mirror peer duplicate detection, and health-warning refusal for fail/max_mds changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/FSCommands.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/FSCommands.h -->
# sources/distributed-fs/ceph/src/mon/FSCommands.h

## Purpose
`FSCommands.h` declares the polymorphic command-handler interface used by `MDSMonitor` for CephFS administration commands. It isolates common prefix matching, capability checking, pool validation, and filesystem-setting helpers from the larger monitor implementation.

## Important APIs, Types, and Functions
`FileSystemCommandHandler` derives protectedly from `CommandHandler`. It stores a command `prefix`, defines `fs_or_fscid` as `std::variant<Filesystem*, fs_cluster_id_t>`, and exposes `can_handle()`, `is_op_allowed()`, static `load(Paxos*)`, and pure virtual `handle()`. Protected helpers are `_check_pool()` and `set_val()`. The enum values `POOL_METADATA`, `POOL_DATA_DEFAULT`, and `POOL_DATA_EXTRA` categorize pool validation strictness. `errmsg_for_unhealthy_mds` is shared by fail-like commands that need explicit operator confirmation.

## Control Flow
`can_handle()` first checks exact prefix. `fs new` and `fs flag set` bypass per-filesystem authorization because they are global operations. Other commands call `is_op_allowed()` before dispatching to the concrete handler. `load()` constructs the handler list consumed by `MDSMonitor`.

## State and Persistence
The header owns no persistent state beyond the handler prefix. The interface passes mutable `FSMap`, `Monitor`, `MonOpRequestRef`, command maps, and response streams into handlers, leaving actual persistence to `MDSMonitor` Paxos commits and OSDMap side effects.

## Dependencies and Integration Points
Forward declarations keep the header light while exposing direct contracts with `Filesystem`, `FSMap`, `Monitor`, `OSDMap`, and `Paxos`. It depends on `MonOpRequest`, `CommandHandler`, and CephFS cluster id types.

## Risks
The protected inheritance from `CommandHandler` means only selected parsing helpers are intended for subclasses. `fs_or_fscid` lets `set_val()` operate on either a newly-created uncommitted filesystem object or a filesystem already inside `FSMap`; misuse could update a stale object. Prefix-based dispatch requires command JSON prefixes to remain stable.

## Test Signals
Header contract tests should verify `can_handle()` prefix behavior, authorization bypass for global commands, capability rejection on named filesystems, load order coverage for expected prefixes, and `_check_pool()`/`set_val()` behavior through concrete handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/FSCommands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/HealthMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/HealthMonitor.cc

## Purpose
`HealthMonitor.cc` aggregates cluster health checks from all monitor Paxos services, persists monitor-local and leader-derived health state, handles health mute commands, and produces formatted health status output.

## Important APIs, Types, and Functions
Core methods include `update_from_paxos`, `create_pending`, `encode_pending`, `preprocess_query`, `prepare_update`, `prepare_command`, `prepare_health_checks`, `tick`, `check_member_health`, `check_leader_health`, `check_mutes`, `gather_all_health_checks`, and `get_health_status`. Leader checks are factored into `check_for_colocated_monitors`, `check_for_older_version`, `check_for_mon_down`, `check_for_clock_skew`, `check_if_msgr2_enabled`, `check_mon_crush_loc_stretch_mode`, `check_netsplit`, and `check_erasure_code_profiles`.

## Control Flow
Every active monitor runs `check_member_health()` on tick. A leader writes its local `quorum_checks` directly; peons send `MMonHealthChecks` for the leader to prepare. Leaders also compute monmap/elector/OSDMap-derived checks and expire or adjust mutes. Any change triggers `propose_pending()`. Commands only mutate `pending_mutes`: `health mute` validates code, sticky flag, TTL, current alert presence, count, and summary; `health unmute` clears one or all mutes.

## State and Persistence
Paxos state stores `quorum_checks`, `leader_checks`, and `mutes` under service keys, plus the combined health map via `encode_health()`. `pending_mutes` is copied from committed `mutes` in `create_pending()`. Netsplit maps are runtime state split into pending and current location/monitor pairs with first-seen timestamps; they are not directly persisted.

## Dependencies and Integration Points
The monitor reads `Monitor`, `MonMap`, `OSDMonitor`, `OSDMap`, CRUSH topology, election netsplit tracking, session map global-id status, monitor store size, filesystem stats, config options, and all `mon.paxos_service` health maps. It formats through `Formatter`/plain strings and logs mute lifecycle events to the cluster log.

## Risks
Health accuracy depends on leader synthesis and timely peon reports. Netsplit detection is topology-sensitive and relies on valid CRUSH location type names; invalid types are logged and sorted after valid entries. Mute stability is subtle: non-sticky mutes clear when alert count increases, summary changes, or the alert disappears. Some warnings depend on local monitor config values, so a heterogeneous monitor configuration can produce rotating warnings.

## Test Signals
Tests should cover member disk/auth warnings, peon-to-leader health updates, stale quorum pruning, mute TTL/count/summary/sticky behavior, formatted muted status, older-version delay, mon-down grace intervals, clock skew details, msgr2 checks, stretch-mode CRUSH location validation, netsplit grace/current transitions, and EC profile warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/HealthMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/HealthMonitor.h -->
# sources/distributed-fs/ceph/src/mon/HealthMonitor.h

## Purpose
`HealthMonitor.h` declares the monitor service responsible for durable cluster-health aggregation and health command handling. It presents a `PaxosService` interface plus helpers used by monitor status paths.

## Important APIs, Types, and Members
`HealthMonitor` stores `version`, per-quorum-member `health_check_map_t`, leader-only health checks, committed and pending `health_mute_t` maps, and runtime netsplit tracking maps. Public overrides cover initialization, Paxos update lifecycle, query/update preprocessing, ticking, trimming, and health rendering through `gather_all_health_checks()` and `get_health_status()`.

## Control Flow Contract
Monitor dispatch calls `preprocess_query()` for commands and health-check messages, then `prepare_update()` for mutes and peon health reports. Periodic `tick()` refreshes local and leader checks and proposes when state changes. Consumers call `get_health_status()` to gather all service health maps and render plain or structured output.

## State and Persistence
The header distinguishes committed `mutes` from `pending_mutes`, while `quorum_checks` and `leader_checks` are persisted by the implementation. Netsplit maps are runtime grace-period state and are intentionally not part of the durable Paxos contract.

## Dependencies and Integration Points
It depends on `PaxosService`, Ceph health types, monitor operation references, formatter support, and coarse monotonic clocks. Private methods expose integration with monmap, OSDMap, CRUSH, config, session map, and leader election state through the implementation.

## Risks
The class mixes durable health state with runtime-only netsplit grace data; restarts can reset pending netsplit timing. Callers must treat `get_health_status()` as a snapshot assembled from all Paxos services, not just state owned by `HealthMonitor`.

## Test Signals
Header-level checks should validate lifecycle override wiring, public health rendering availability, and that private check categories remain represented when command or health-message behavior changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/HealthMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/KVMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/KVMonitor.cc

## Purpose
`KVMonitor.cc` implements the monitor-backed config-key key/value service. It serves read commands directly from the monitor store, commits set/delete deltas through Paxos, supports dm-crypt/daemon-private OSD key helpers, and pushes `kv:` subscription updates.

## Important APIs, Types, and Functions
Key functions are `preprocess_command`, `prepare_command`, `encode_pending`, `update_from_paxos`, `_have_prefix`, `validate_osd_destroy`, `do_osd_destroy`, `validate_osd_new`, `do_osd_new`, `check_sub`, `check_all_subs`, and `maybe_send_update`. `KV_PREFIX` is `"mon_config_key"`. Pending changes are `map<string, optional<bufferlist>>`, where `nullopt` means remove.

## Control Flow
Read-only commands (`config-key get/exists/list/ls/dump`) are handled in preprocess. Mutating commands (`set/put/del/rm`) parse key/value or input data, enforce `mon_config_key_max_entry_size`, populate `pending`, force immediate propose, and reply after commit. Paxos update stores the delta under the service version and applies actual puts/erases under `KV_PREFIX`.

## State and Persistence
`version` mirrors `get_last_committed()`. Each commit stores the encoded pending delta as a versioned Paxos record and writes actual key contents under `mon_config_key`. `get_trim_to()` retains only the last 50 delta records for incremental subscribers. OSD helper methods store dm-crypt keys under `dm-crypt/osd/<uuid>/luks` and remove both dm-crypt and `daemon-private/osd.<id>/` prefixes during destroy.

## Dependencies and Integration Points
It integrates with `MonitorDBStore`, `KeyValueDB::Iterator`, `MMonCommand`, `MKVData`, session subscriptions, config limits, `uuid_d`, and OSD lifecycle code that calls validate/do helpers. Binary-looking values are masked in dumps to keep JSON output safe.

## Risks
Incremental subscription correctness depends on retained delta history; subscribers at or before the first committed version receive full dumps. `do_osd_destroy()` iterates by prefix and must not miss multiple keys. `validate_osd_new()` returns positive `EEXIST` for idempotent matching keys but `-EEXIST` on mismatch, so callers must preserve that convention.

## Test Signals
Tests should cover read output formats, binary dump masking, size-limit rejection, value from command vs input data, set/delete commit deltas, full vs incremental `MKVData`, subscription removal for onetime subs, OSD dm-crypt idempotency, mismatched key rejection, and prefix deletion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/KVMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/KVMonitor.h -->
# sources/distributed-fs/ceph/src/mon/KVMonitor.h

## Purpose
`KVMonitor.h` declares the Paxos-backed monitor config-key service and its OSD lifecycle helper API.

## Important APIs, Types, and Members
The class derives from `PaxosService`, stores a committed `version`, and a pending map of key to optional bufferlist. Public methods include Paxos lifecycle overrides, command preprocess/prepare, subscription checks, OSD new/destroy validation and execution, and `enqueue_set()`/`enqueue_rm()` for other services that batch KV mutations into an existing proposal.

## Control Flow Contract
Monitor command dispatch routes read commands to `preprocess_command()` and writes to `prepare_command()`. External services may enqueue pending KV updates but must call `propose_pending()` and force commit themselves, as documented in the header comment.

## State and Persistence
The class exposes `get_store_prefixes()` for both service metadata and `KV_PREFIX`. Its persistent state is maintained by the implementation as versioned deltas plus current key values.

## Dependencies and Integration Points
It depends on `PaxosService`, `MonSession`, subscriptions, `uuid_d`, `bufferlist`, and OSD code paths that need dm-crypt keys in monitor KV storage.

## Risks
`enqueue_set()` takes a non-const bufferlist reference but copies into pending; callers still need to manage proposal atomicity. `_have_prefix()` is a private store scan helper and can be costly if used on large keyspaces.

## Test Signals
Tests should verify lifecycle overrides, external enqueue semantics, OSD helper contracts, prefix registration, and subscriber update behavior after commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/KVMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/LogMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/LogMonitor.cc

## Purpose
`LogMonitor.cc` implements cluster log collection, durable log history, external log fanout, `log` commands, `log last` reads, and log subscriptions.

## Important APIs, Types, and Functions
Important methods include `create_initial`, `update_from_paxos`, `create_pending`, `encode_pending`, `encode_full`, `should_stash_full`, `get_trim_to`, `preprocess_log`, `prepare_log`, `_updated_log`, `preprocess_command`, `prepare_command`, `check_sub`, `_create_sub_incremental`, `log_external`, `log_external_backlog`, `update_log_channels`, and config observer callbacks. `log_channel_info` parses per-channel syslog/file/graylog/journald configuration and expands `$channel`.

## Control Flow
Incoming `MLog` messages are deduplicated against `LogSummary` and current `pending_keys`; new entries are inserted into timestamp-ordered `pending_log` and acknowledged after commit. CLI `log` creates a local `LogEntry`. `log last` reads from legacy in-summary tails or post-Quincy per-entry keys. Subscribers named `log-<level>` receive incremental `MLog` messages from requested Paxos versions.

## State and Persistence
Pre-Quincy commits encoded entries directly and stashed a full `LogSummary` every commit. Quincy+ commits write each entry under `service_name/channel/<seq>`, store incrementals with entry payloads plus per-channel prune bounds, keep `summary.channel_info` start/end sequence ranges, and periodically stash full summaries. `external_log_to` is a monitor-store meta key that records how far external logging has caught up.

## Dependencies and Integration Points
The monitor uses `LogEntry`, `LogSummary`, `MLog`, `MLogAck`, subscriptions, monitor store, config observers, syslog, Graylog, journald, safe file writes, and `mon_cluster_log_*` settings. It registers config keys in `get_tracked_keys()` and refreshes channel destinations on change.

## Risks
External log replay must not double-log or skip committed entries across quorum changes; `external_log_to` rewind/skip paths are critical. File descriptors are cached per channel and must close on rotation or config change. Mixed-version compatibility requires legacy and v2 decoding/encoding paths to remain correct. `log last` over all channels merges bounded per-channel tails, which can miss older cross-channel entries when a single channel dominates.

## Test Signals
Tests should cover dedupe, ack seq, proposal threshold by pending count, legacy/v2 decode, per-channel key generation and pruning, full-summary stashing, `log last` filtering by level/channel, subscriber skip messages after trims, external backlog catchup, log rotation, and config parsing for syslog/file/graylog/journald.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/LogMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/LogMonitor.h -->
# sources/distributed-fs/ceph/src/mon/LogMonitor.h

## Purpose
`LogMonitor.h` declares the monitor service for cluster log persistence, replay, subscriptions, and external logging destinations.

## Important APIs, Types, and Members
`LogMonitor` derives from `PaxosService` and `md_config_obs_t`. Members include `pending_log`, `pending_keys`, `LogSummary summary`, `external_log_to`, per-channel file descriptors, formatting buffer, rotation flag, and nested `log_channel_info`. Public APIs cover `tick`, `dump_info`, subscription checks, `reopen_logs`, external logging, `sub_name_to_id`, shutdown observer removal, tracked config keys, and config-change handling.

## Control Flow Contract
The Paxos lifecycle persists log entries and summaries. Message dispatch handles `MLog` and monitor commands. Config observer callbacks call `update_log_channels()` to rebuild channel destinations and close stale descriptors. `reopen_logs()` marks fds for lazy reopening during the next external log write.

## State and Persistence
The header distinguishes pending in-memory entries from durable `summary` and `external_log_to`. `log_channel_info` holds runtime parsed configuration and destination clients, not Paxos state.

## Dependencies and Integration Points
It exposes integration with `MLog`, `Subscription`, `Formatter`, config observers, `LogEntry`, `Graylog`, `JournaldClusterLogger`, and Ceph string-map config parsing.

## Risks
The class owns OS file descriptors and external clients; lifecycle cleanup depends on `on_shutdown()` and `log_external_close_fds()`. Config maps are stringly typed, so invalid booleans or endpoints are handled at runtime.

## Test Signals
Tests should verify observer registration/removal, rotation flag behavior, channel metadata expansion, subscription type parsing, and that tracked config keys match options consumed by channel refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/LogMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MDSMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/MDSMonitor.cc

## Purpose
`MDSMonitor.cc` is the Ceph monitor service for CephFS `FSMap` and MDS daemon membership. It persists FSMap epochs, processes MDS beacons and load-target updates, dispatches CephFS commands, maintains MDS metadata/health, manages laggy or failed daemons, promotes standbys, resizes ranks, and serves FSMap/MDSMap subscriptions.

## Important APIs, Types, and Functions
Major methods are `update_from_paxos`, `create_pending`, `encode_pending`, `preprocess_query`, `prepare_update`, `preprocess_beacon`, `prepare_beacon`, `prepare_command`, `filesystem_command`, `fail_mds_gid`, `fail_mds`, `check_health`, `maybe_resize_cluster`, `maybe_promote_standby`, `drop_mds`, `check_sub`, metadata helpers, and `tick`. It specializes `cmd_getval()` for `mds_gid_t`, `mds_rank_t`, and `MDSMap::DaemonState`.

## Control Flow
Paxos updates load metadata, health, and the target FSMap epoch, decode through `PaxosFSMap`, sanity-check, and notify subscribers. Beacon preprocessing validates session caps, fsid, address port, leader routing, map epoch freshness, state seq, join target changes, laggy state, and health changes. Beacon preparation updates health, handles boot insertion, validates compatibility and legal state transitions, processes stopped/damaged/DNE cases, blocklists via OSDMonitor when needed, and replies after finished proposals.

Commands first go through loaded `FileSystemCommandHandler`s from `FSCommands.cc`; remaining legacy MDS commands handle set_state, fail, rm, rmfailed, compat defaults, repaired, and freeze. The leader `tick()` prunes history, flushes old FSMap structs if needed, computes health, detects beacon timeouts, performs rank resize, replaces failed ranks, promotes standbys, and batches OSDMap proposals with FSMap proposals using `paxos.plug()`.

## State and Persistence
The durable state is the encoded `FSMap` version and last committed epoch, plus MDS health entries under `mds_health` and metadata under `mds_metadata/last_metadata`. Pending maps include `pending_daemon_health`, `pending_daemon_health_rm`, and `pending_metadata`. Runtime leader state includes `last_beacon`, `last_tick`, `last_fsmap_struct_flush`, and `check_fsmap_struct_version`.

## Dependencies and Integration Points
It integrates with `PaxosService`, `PaxosFSMap`, `Monitor`, `Paxos`, `OSDMonitor`, `FSCommands`, `MDSMap`, `FSMap`, `MMDSBeacon`, `MMDSMap`, `MFSMap`, `MFSMapUser`, `MMDSLoadTargets`, session capabilities, monitor subscriptions, cluster log, config, metadata dump utilities, and CephFS feature definitions.

## Risks
The highest-risk behavior is failure handling: laggy detection, blocklisting, standby replacement, damaged ranks, and command-driven fail paths must coordinate with OSDMap writeability. Beacon acceptance depends on effective epoch matching, legal state transitions, and consistent daemon compatibility. History pruning and old-struct flushing affect recovery and client last-seen queries. Capability filtering must be applied before exposing or mutating per-filesystem state. Tick automation can change rank assignment without direct operator commands.

## Test Signals
Tests should cover boot and non-boot beacons, stale seq/epoch behavior, laggy clearing, invalid transitions and compat changes, damaged rank blocklisting, stopped daemon removal, unique-name enforcement, command capability checks, FS command delegation, legacy MDS commands, metadata persistence/dumps, health encoding from daemon metrics, FSMap/MDSMap/fsmap.user subscriptions, beacon timeout grace during monitor changes, standby promotion, resize down/up, and OSD proposal batching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MDSMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MDSMonitor.h -->
# sources/distributed-fs/ceph/src/mon/MDSMonitor.h

## Purpose
`MDSMonitor.h` declares the CephFS monitor service that owns `FSMap` state and MDS daemon lifecycle coordination.

## Important APIs, Types, and Members
`MDSMonitor` derives from `PaxosService`, `PaxosFSMap`, and protected `CommandHandler`. Public methods expose Paxos lifecycle, query/update dispatch, proposal policy, health-warning predicates, active/restart hooks, subscriptions, info dumping, `fail_mds_gid()`, and version summaries. Protected methods cover beacon/offload/command processing, filesystem commands, health checks, standby promotion, resizing, metadata persistence, and quiesce DB leader assignment. State includes `last_beacon`, loaded FS command `handlers`, pending daemon health removal, pending metadata, `last_tick`, and old-struct flush timers.

## Control Flow Contract
Monitor dispatch calls `preprocess_query()` and `prepare_update()` for beacons, commands, and MDS load-target messages. `tick()` is the leader automation entry point. `check_subs()` and `check_sub()` serve map subscribers. FS command handlers are loaded in the constructor.

## State and Persistence
The header exposes both durable inputs (`PaxosFSMap`, metadata and health prefixes in implementation) and runtime-only leader tracking. `pending_daemon_health` and `pending_metadata` are staged into monitor transactions during encode.

## Dependencies and Integration Points
It depends on monitor core types, `PaxosFSMap`, `MDSMap`, `MMDSBeacon`, monitor metadata, command parsing, Ceph clocks, and `FileSystemCommandHandler`. Public `has_health_warnings()` is used by FS command handlers to gate risky fail/resize operations.

## Risks
The interface combines monitor-service, FSMap, and command-handler responsibilities, so callers must respect leader/writeability and capability assumptions. Raw pointers in handler lists and metadata helpers rely on monitor-owned lifetimes.

## Test Signals
Tests should verify override wiring, handler load availability, health-warning predicates by gid/vector, subscription entry points, restart clearing of leader runtime state, and interactions between `fail_mds_gid()` and OSD writeability/blocklisting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MDSMonitor.h -->
