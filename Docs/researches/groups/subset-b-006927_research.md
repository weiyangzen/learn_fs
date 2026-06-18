# subset-b-006927 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonitorDBStore.h -->
# sources/distributed-fs/ceph/src/mon/MonitorDBStore.h

## Purpose
`MonitorDBStore.h` defines the monitor's local persistent key/value store wrapper. It hides the configured `KeyValueDB` backend, gives Paxos services a common transaction format, supports synchronous and serialized asynchronous commits, exposes iterators used by monitor-store synchronization, and stores small out-of-band metadata files such as backend type, creation version, creation time, and minimum monitor release. The class is implemented almost entirely in the header, so callers use it as both the monitor database facade and the transaction builder API.

## Important APIs, Types, and Functions
The core type is `MonitorDBStore`, with members for the filesystem path, `KeyValueDB` instance, optional transaction dump streams, a `Finisher` named `io_work`, and an `is_open` guard. `get_devname()`, `get_path()`, and `get_priority_cache()` expose backend identity and cache integration.

`Op` is the encoded transaction operation. It supports `OP_PUT`, `OP_ERASE`, `OP_COMPACT`, and `OP_ERASE_RANGE` through `Transaction`, carries `prefix`, `key`, `endkey`, and value `bufferlist`, and has versioned encode/decode plus formatter dumping. `Transaction` owns a list of `Op`s and tracks approximate `bytes` and `keys`. It offers typed `put()`/`erase()` helpers for string and `version_t` keys, range erase, prefix/range compaction, append, append-from-encoded, size accounting, and formatter dumping.

`apply_transaction()` converts a `MonitorDBStore::Transaction` to a `KeyValueDB::Transaction`, optionally writes a binary or JSON transaction dump, applies data mutations synchronously, and triggers asynchronous compaction only after the write succeeds. `C_DoTransaction` and `queue_transaction()` serialize asynchronous commits through the `Finisher`; `flush()` blocks until queued IO drains. `StoreIteratorImpl` and `WholeStoreIteratorImpl` implement synchronization chunks as transactions, with optional CRC accumulation under `mon_sync_debug`.

Read/lifecycle APIs include `get_synchronizer()`, prefixed and whole-space `get_iterator()`, value and `version_t` `get()`, `exists()`, `clear_key()`, `clear()`, `_open()`, `open()`, `create_and_open()`, `close()`, compaction helpers, estimated size, `write_meta()`, and `read_meta()`.

## Control Flow
Creation/opening starts with metadata. `open()` reads `kv_backend`, backfills it to `rocksdb` for old stores, calls `_open()`, opens the backend, raises perf-counter priority, starts `io_work`, and marks the store open. `create_and_open()` first writes `ceph_version_when_created` and `created_at`, chooses `g_conf()->mon_keyvaluedb` when no backend metadata exists, creates the backend, starts `io_work`, and marks the store open. `_open()` trims trailing slashes, opens `<path>/store.db`, configures transaction dumping, and initializes RocksDB with monitor-specific options when appropriate.

Callers build a `TransactionRef` using helper methods. Synchronous paths call `apply_transaction()` directly. Asynchronous paths call `queue_transaction()`, which queues `C_DoTransaction`; that callback can inject configured transaction delay, calls `apply_transaction()`, and completes the caller's `oncommit` context without monitor locks held. `close()` asserts no pending work, stops the finisher, clears `is_open`, and drops the DB pointer.

Store synchronization uses `get_synchronizer()` with a start key and sync-prefix set. `WholeStoreIteratorImpl::get_chunk_tx()` walks the whole-space iterator, skips prefixes outside the sync set, appends one PUT operation per selected KV pair until byte/key limits would be exceeded, records the next key in `last_key`, and marks `done` at iterator exhaustion. `get_next_key()` advances to the next synchronizable raw key.

## State and Persistence
Persistent monitor service data lives in the `KeyValueDB` backend under service prefixes and string keys. Transaction encoding is separate from backend encoding and is used for dumping and sync reconstruction. Metadata keys written with `write_meta()` are plaintext files under the monitor store path and are available before the DB is open. `do_dump`, dump file descriptors, and `dump_fmt` are debug state, not cluster state.

The store serializes queued writes through one `Finisher`, so transaction order is preserved for `queue_transaction()`. Compactions are explicitly deferred until after a successful write. `Transaction::bytes` is approximate and used for sync chunk sizing, not durable metadata. `read_meta()` strips trailing whitespace; `get(prefix,key)` returning a `version_t` treats `ENOENT` as zero but aborts on other read errors.

## Dependencies and Integration Points
The class depends on `KeyValueDB`, Ceph `bufferlist` encoding, `Context`, `Finisher`, `PriorityCache`, `safe_io`, block-device lookup, monitor config, debug/logging, and perf counters. It is used by monitor Paxos services for `put_version()`, `put_last_committed()`, health encoding, one-off local metadata, and direct cleanup operations such as removing mkfs bootstrap keys.

## Risks
Error handling is intentionally fatal for unexpected DB write/read failures: failed transaction submission aborts the process, and invalid operation types abort. `close()` requires the caller to flush/drain first. The async transaction callback sleeps inside the finisher when delay injection is enabled, which preserves ordering but can stall all later monitor DB writes. `Transaction::append()` adds the other transaction's full initial byte overhead as well as operations, so byte accounting is approximate.

Iterator chunking writes every synchronized key as a separate PUT operation; that is simple but can be inefficient for large stores. `get_next_key()` advances the iterator before returning the key, so consumers must rely on the documented behavior. Transaction dumping must be configured with valid output paths; binary dump close is unconditional if dumping was enabled.

## Test Signals
Useful tests include encode/decode round trips for `Op` and `Transaction` versions, all operation types through `apply_transaction()`, dump JSON/binary paths, async queue ordering and completion return codes, metadata read/write before open, missing-version `get()` returning zero, synchronization chunks respecting prefix filters and byte/key limits, and lifecycle assertions around `flush()`/`close()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonitorDBStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonmapMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/MonmapMonitor.cc

## Purpose
`MonmapMonitor.cc` implements the Paxos-backed monitor-map service. It creates and commits monmap versions, loads committed maps, services monmap read commands, prepares mutating monitor commands, processes monitor join messages, applies persistent monitor feature bits, manages subscriptions, and coordinates stretch-mode monitor-map changes with `OSDMonitor`.

## Important APIs, Functions, and Types
The main lifecycle methods are `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, and `on_active()`. `apply_mon_features()` updates persistent feature bits and `min_mon_release` after a full quorum agrees on support; `C_ApplyFeatures` retries that work once the service is writeable.

Query and update dispatch is split into `preprocess_query()`, `preprocess_command()`, `preprocess_join()`, `prepare_update()`, `prepare_command()`, and `prepare_join()`. Supported read commands include `mon stat`, `mon getmap`, `mon dump`, and `mon feature ls`. Mutating commands include `mon add`, `mon remove`/`mon rm`, `mon feature set`, `mon set-rank`, `mon set-addrs`, `mon set-weight`, `mon enable-msgr2`, election strategy changes, disallowed-leader add/remove, `mon set_location`, stretch tiebreaker changes, and stretch-mode enable/disable.

Stretch-mode logic is centralized in `try_enable_stretch_mode()` and static `validate_and_enable_stretch_mode()`, with emergency state helpers `trigger_degraded_stretch_mode()` and `trigger_healthy_stretch_mode()`. `get_monmap()`, `check_subs()`, `check_sub()`, `tick()`, `dump_info()`, and `should_propose()` fill out the service surface.

## Control Flow
Initial cluster creation copies the boot monmap, sets epoch 1, and records default persistent monitor features unless the debug override disables that. Normal loading asks Paxos for `get_last_committed()`, skips if the running `mon.monmap` is already current, optionally signals bootstrap, decodes the version into `mon.monmap`, erases the old `mkfs/monmap` key if present, updates subscribers, records `min_mon_release` metadata, and notifies the monitor about the new map.

For a pending proposal, `create_pending()` clones the committed monmap, increments epoch, updates `last_changed`, and clears `removed_ranks`. `encode_pending()` asserts epoch monotonicity, encodes with quorum connection features, stores the new version and last-committed marker, creates the first cluster fingerprint at epoch 1, and persists health checks generated from `pending_map`.

Read commands are answered during preprocessing when they can be satisfied from committed state. `mon getmap` and `mon dump` optionally decode historical versions from Paxos. Mutating commands run in `prepare_command()` against the committed `monmap` for validation and mutate only `pending_map`. The function explicitly documents that user replies must not claim a change is committed until the proposal finishes. Successful mutating commands call `wait_for_commit()` and return `true` so PaxosService proposes immediately; non-mutating/idempotent failures reply without proposing.

Monitor joins first pass `preprocess_join()`, which filters already-known joins, duplicate address/name cases, insufficient caps, and missing stretch locations. `prepare_join()` removes conflicting name/address entries from `pending_map`, adds the joining monitor, preserves existing location when appropriate, and updates `last_changed`.

Stretch-mode enablement plugs Paxos while it validates OSD pool/rule changes and monmap changes together. The monmap side validates that the CRUSH dividing bucket has exactly two data subtrees, every monitor has a location at that bucket type, monitors exist in both data zones, and the tiebreaker is exactly one monitor in a third location or an explicit valid monitor outside the data zones. Commit mode sets connectivity election, disallows the tiebreaker, records it, and enables stretch mode. OSDMonitor is then asked to propose its companion changes.

## State and Persistence
Persistent state is the encoded `MonMap` at each Paxos version plus service health checks. `monmap_bl` caches the currently loaded buffer, and `pending_map` holds uncommitted state during a proposal. `on_active()` also writes the local `Monitor::MONITOR_NAME/joined` marker once the daemon has been part of an active quorum. `update_from_paxos()` keeps `min_mon_release` as a side metadata file in the monitor store.

`should_propose()` always returns true with zero delay, so this service intentionally avoids batching and assumes only one pending mutation is handled at a time. Subscriptions track the next epoch a client wants; `check_sub()` sends the latest monmap and advances or removes the subscription.

## Dependencies and Integration Points
This implementation is tightly coupled to `Monitor`, `PaxosService`, `Paxos`, `MonMap`, monitor sessions/subscriptions, `MMonCommand`, `MMonJoin`, Ceph feature definitions, `OSDMonitor`, `CrushWrapper`, command parsing, and monitor logging. Stretch mode crosses service boundaries: monmap election/tiebreaker state and OSD pool/CRUSH state must be validated and proposed together.

## Risks
The command path depends on disciplined committed-vs-pending semantics. Returning success based on uncommitted pending state could mislead users if quorum is lost after a monitor add/remove. Several commands mutate `pending_map` without rechecking all races because immediate proposal delay is assumed; changes to `should_propose()` would require revisiting those assumptions. Stretch-mode validation dereferences `crush.get_validated_type_id(dividing_bucket)` and relies on the caller having already validated CRUSH type existence. The `set_new_tiebreaker` path parses `yes_i_really_mean_it` but does not appear to use it in the final guard.

Monitor add/remove can affect quorum availability, so reply wording and wait-for-commit behavior are important. Historical map reads allocate a temporary `MonMap` and must delete it on all success paths. Subscription removal uses session-map mutation and must not race with iteration assumptions.

## Test Signals
Tests should cover monmap encode/load across epochs, epoch-1 fingerprint behavior, mkfs monmap cleanup, feature application only under full quorum, all read command formats, add/remove duplicate name/address cases, msgr2 address expansion, election strategy and disallowed-leader invariants, join idempotency, stretch-mode validation for missing locations/wrong tiebreakers/wrong subtree counts, degraded/healthy stretch triggers, and subscription next-epoch updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonmapMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonmapMonitor.h -->
# sources/distributed-fs/ceph/src/mon/MonmapMonitor.h

## Purpose
`MonmapMonitor.h` declares the monitor-map Paxos service. It defines the public service contract used by the monitor daemon to create, load, propose, query, mutate, and subscribe to the cluster monitor map, including stretch-mode helpers.

## Important APIs, Types, and Functions
`MonmapMonitor` derives from `PaxosService`. Its constructor passes `Monitor`, `Paxos`, and service name through to the base. Public state includes `MonMap pending_map`, the uncommitted map awaiting Paxos passage. Lifecycle overrides are `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, empty `encode_full()`, and `on_active()`.

The command/message surface is `preprocess_query()`, `prepare_update()`, `preprocess_join()`, `prepare_join()`, `preprocess_command()`, `prepare_command()`, `get_monmap()`, `should_propose()`, `check_sub()`, and `tick()`. `dump_info()` exposes service state to formatters. `apply_mon_features()` updates persistent feature state after quorum negotiation.

Stretch-mode declarations include private `try_enable_stretch_mode()`, public static `validate_and_enable_stretch_mode()` for unit-testable validation, and public `trigger_degraded_stretch_mode()`/`trigger_healthy_stretch_mode()` for marking failed monitors or clearing degraded stretch state.

## Control Flow Contract
The base `PaxosService` calls create/update/encode methods as the service becomes active and proposes new versions. Read and join messages enter through `preprocess_query()`, while mutating messages enter `prepare_update()`. `should_propose()` declares that this service proposes immediately, which shapes the implementation's pending-state race assumptions.

`check_sub()` is called when a monmap subscriber may need an update. `tick()` performs periodic leader-only maintenance, currently including repair of an empty created timestamp in old maps. Stretch helpers are called from the command path and from monitor health/stretch orchestration.

## State and Persistence
The header declares `pending_map` and private `monmap_bl`. The committed state lives in `mon.monmap` and in Paxos versions written through `MonitorDBStore`. `pending_map` is process-local until encoded by `encode_pending()`. Stretch-mode state such as tiebreaker, disallowed leaders, and marked-down monitors is persisted as part of the `MonMap`.

## Dependencies and Integration Points
The class includes `PaxosService`, `MonMap`, and `MonitorDBStore`, and forward-declares `Subscription`. Stretch validation takes a `CrushWrapper`, reflecting its dependency on OSD/CRUSH topology. It is a friend-adjacent service to `Monitor`, which exposes `monmon()` and relies on this service for monitor membership.

## Risks
Because `pending_map` is public, callers can theoretically mutate it outside the service's command sequencing; current usage relies on monitor single-threaded service discipline. Static stretch validation is testable but still modifies a passed `pending_map` when `commit=true`, so tests must keep committed and pending maps distinct. Empty `encode_full()` is intentional because full versions are not used; consumers expecting full-version snapshots would be wrong.

## Test Signals
Header-level contract tests should instantiate the service with mocked monitor/Paxos state, verify method overrides are called by the base service, exercise static stretch validation directly, and confirm immediate proposal delay. Integration tests should confirm per-command behavior through the declared preprocess/prepare split and subscription updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonmapMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwBeaconConstants.h -->
# sources/distributed-fs/ceph/src/mon/NVMeofGwBeaconConstants.h

## Purpose
`NVMeofGwBeaconConstants.h` centralizes the monitor-side beacon protocol version constants for NVMe-oF gateway beacons. It avoids duplicating magic numbers in map and monitor code that must distinguish full legacy beacons from enhanced beacon-diff beacons.

## Important APIs, Types, and Functions
The header defines `BEACON_VERSION_LEGACY` as `1` for the original full beacon format with no diff support, and `BEACON_VERSION_ENHANCED` as `2` for the enhanced diff-capable format. It has only include guards and no functions or types.

## Control Flow
The constants are consumed by beacon handling code such as `NVMeofGwMon::apply_beacon()` and sequence tracking in `NVMeofGwMap`. Legacy beacons replace the gateway's full subsystem list and rebuild nonce maps. Enhanced beacons are interpreted as add/change/delete deltas and use beacon sequence numbers to detect out-of-order delivery.

## State and Persistence
The header has no state. The chosen version value affects how gateway subsystem state, nonce maps, and beacon sequence fields are interpreted and persisted by the surrounding NVMe gateway monitor map.

## Dependencies and Integration Points
The constants align `MNVMeofGwBeacon` message versions, `NVMeofGwMon` beacon application, `NVMeofGwMap` sequence helpers, and feature negotiation around beacon diff support.

## Risks
Because these are preprocessor macros rather than typed constants, accidental redefinition or broad macro visibility is possible. Any future beacon version must update all switch/compare sites that currently test greater than legacy rather than equality with enhanced.

## Test Signals
Compatibility tests should send version-1 full beacons and version-2 diff beacons through the monitor and verify subsystem replacement versus delta application, nonce-map clearing, and sequence ACK behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwBeaconConstants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwMap.cc -->
# sources/distributed-fs/ceph/src/mon/NVMeofGwMap.cc

## Purpose
`NVMeofGwMap.cc` implements the persistent and runtime policy engine for monitor-managed NVMe-oF gateway high availability. It owns gateway creation/deletion, ANA group ownership, gateway availability transitions, failover/failback, disaster-location recovery, beacon-diff features, per-gateway map epochs, state-machine timers, OSD blocklisting, and monitor health checks.

## Important APIs, Functions, and Types
Client-map conversion is handled by `to_gmap()`, which filters unavailable/deleting gateways and builds `NvmeGwClientState` values with `NqnState` ANA exports. Configuration entry points include `cfg_add_gw()`, `cfg_delete_gw()`, `cfg_admin_state_change()`, `cfg_set_location()`, `cfg_location_disaster_set()`, `cfg_location_disaster_clear()`, and `cfg_enable_disable_beacon_diff()`.

Gateway state updates enter through `gw_performed_startup()`, `set_addr_vect()`, `process_gw_map_ka()`, `process_gw_map_gw_down()`, `process_gw_map_gw_no_subsys_no_listeners()`, `track_deleting_gws()`, `skip_failovers_for_group()`, `put_gw_beacon_sequence_number()`, and `set_gw_beacon_sequence_number()`. HA logic is split across `handle_abandoned_ana_groups()`, `find_failover_candidate()`, `find_failover_gw_logic()`, `set_failover_gw_for_ANA_group()`, `find_failback_gw()`, `check_relocate_ana_groups()`, and `relocate_ana_grp()`.

State-machine helper functions include `add_grp_id()`, `remove_grp_id()`, `fsm_handle_gw_alive()`, `fsm_handle_gw_no_subsystems()`, `fsm_handle_gw_down()`, `fsm_handle_gw_delete()`, and `fsm_handle_to_expired()`. Persistence and maintenance helpers include `increment_gw_epoch()`, `validate_gw_map()`, timer start/get/cancel/update functions, `blocklist_gw()`, `get_health_checks()`, and disaster-location helpers.

## Control Flow
Gateway creation allocates an ANA group id. With `NVMEOFHAMAP`, it ensures a group epoch exists. It rejects existing non-deleting gateways, resurrects a deleting gateway if the same ID is recreated, inherits a deleting gateway's ANA group for a different replacement gateway, or allocates the first gap in existing ANA ids. The new ANA id is added to all existing gateways' state maps and all existing ids are added to the new gateway. The maximum legacy ANA group count is `MAX_SUPPORTED_ANA_GROUPS` (16).

Deletion is feature-dependent. Without `NVMEOFHA`, `do_delete_gw()` removes the gateway immediately after state cleanup. With HA, `cfg_delete_gw()` marks it `GW_DELETING`, optionally suppresses failover briefly for an available gateway, and records deletion time for health. `track_deleting_gws()` later deletes one `GW_DELETING` gateway once live subsystem data shows no namespaces for that gateway's ANA group. If every gateway in a group is deleting, `check_all_gws_in_deleting_state()` force-removes the group to avoid being stuck without beacons.

Availability transitions are driven by beacons and ticks. `process_gw_map_ka()` moves `CREATED` or `UNAVAILABLE` gateways to `AVAILABLE`, either setting all states standby for redundant ids or starting failback for a native ANA group. Existing available gateways run `fsm_handle_gw_alive()`, which completes `WAIT_BLOCKLIST_CMPL` once the gateway reports an OSD epoch at least as new as the blocklist epoch. `process_gw_map_gw_down()` marks a gateway unavailable, records down time, resets beacon sequence, invokes down-state handlers for each ANA group, validates no duplicate active owners, and increments the per-group epoch.

Failover starts when an active gateway goes down or `handle_abandoned_ana_groups()` discovers an ANA group with no active owner. `find_failover_candidate()` avoids groups under skip-failover windows, ignores already-started failovers, prefers the least-loaded available gateway in the same location, falls back to any non-disaster available gateway, and then calls `set_failover_gw_for_ANA_group()`. That function blocklists the failed gateway's nonce addresses through OSDMonitor when possible; otherwise it directly marks the candidate active. While waiting for blocklist completion, the candidate is `GW_WAIT_BLOCKLIST_CMPL` and a timer is started.

Failback starts when a gateway returns and its native ANA group is active elsewhere. `find_failback_gw()` can immediately restore ownership if no other gateway is active for that group; otherwise it sets the current owner to `GW_WAIT_FAILBACK_PREPARED`, starts a short timer, and sets the returning owner to `GW_OWNER_WAIT_FAILBACK_PREPARED`. When `fsm_handle_to_expired()` fires and both gateways have observed current maps, the old owner becomes standby and the returning owner becomes active. Disaster cleanup uses similar relocation logic to bring ANA groups back to a recovered location.

Location disaster commands require beacon-diff monitor feature support. Setting a disaster location requires all gateways in that location to be unavailable and the location to exist. Clearing disaster either marks failbacks in process if an available standby gateway in that location can recover ownership, or removes the location immediately. `check_relocate_ana_groups()` periodically moves ANA groups back to the recovering location and removes the disaster entry once every gateway in the location has an active ANA group there.

## State and Persistence
The persistent map includes global `epoch`, `published_features`, `ever_enabled_features`, `created_gws`, `fsm_timers`, `gw_epoch`, and `disaster_locations`, encoded by `NVMeofGwMap::encode()`. Each gateway stores native ANA id, availability, subsystem/listener/namespace data, state machine state per ANA group, blocklist epochs, address vector, beacon sequence fields, admin state, location, and some non-persistent timing fields. `NVMeofGwMon::restore_pending_map_info()` restores selected non-serialized fields across pending-map reconstruction.

`gw_epoch` lets the monitor send per-group unicast map slices when `NVMEOFHAMAP` is supported. `increment_gw_epoch()` is called after changes that affect gateways in a group. State-machine timers are persisted with start/value/end-time data; active timers are checked on monitor tick and can cause further map changes.

## Dependencies and Integration Points
The map depends on `Monitor` for quorum features, `NVMeofGwMon` for deletion-time health state and proposal requests, `OSDMonitor` for blocklisting and OSD Paxos proposals, `MNVMeofGwBeacon` types, Ceph health checks, monitor config values, and serialization helpers in `NVMeofGwSerialize.h`. Gateway clients consume maps generated from `to_gmap()` and subscription/ACK paths in `NVMeofGwMon`.

## Risks
The state machine is distributed and timing-sensitive. Skip-failover windows, failback delays, beacon grace, blocklist timers, and persisted timer end times all affect correctness. Several paths mutate `std::map` entries through `operator[]`, which can create empty group entries during read-like operations if callers pass unknown groups. `check_beacon_timeout()` in the monitor erases from `last_beacon` during range iteration, which should be reviewed carefully for iterator safety.

Failover correctness depends on nonce extraction from subsystem namespaces and successful parsing into `entity_addrvec_t`. If no nonce context exists, failover proceeds by directly marking a candidate active in some paths, reducing fencing strength. `validate_gw_map()` only logs duplicate active states instead of enforcing an invariant. Disaster-location validation is partly stubbed (`validate_number_locations()` returns true), so topology mistakes may pass today.

## Test Signals
Tests should cover ANA id allocation gaps, delete/recreate inheritance, all-deleting force cleanup, admin disable/enable transitions, location and disaster command validation, beacon keepalive transitions, no-subsystem/no-listener transitions, out-of-order beacon sequence handling, same-location and cross-location failover selection, blocklist success/failure paths, failback timer completion, disaster cleanup relocation, per-group epoch increments, persisted timer encode/decode, and health warnings for single gateway, down gateway, and long deleting state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwMap.h -->
# sources/distributed-fs/ceph/src/mon/NVMeofGwMap.h

## Purpose
`NVMeofGwMap.h` declares the monitor-side NVMe-oF gateway map. It is the durable data model and API surface used by `NVMeofGwMon` to mutate gateway state, encode Paxos versions, derive client maps, and produce health checks.

## Important APIs, Types, and Members
The class stores a raw `Monitor *mon`, global Paxos `epoch`, `delay_propose`, `published_features`, `ever_enabled_features`, `created_gws`, `fsm_timers`, per-group `gw_epoch`, and `disaster_locations`. `FLAG_BEACONDIFF` is the map-level feature flag exposed to clients. Public mutation APIs cover gateway lifecycle, admin state, locations, disaster state, beacon-diff enablement, keepalive/down/no-subsystem transitions, timer maintenance, startup, address-vector updates, failover suppression, and beacon sequence persistence.

Private helpers implement deletion, ANA group add/remove, the failover/failback state machine, candidate selection, timer access, map validation, per-group epoch increments, and disaster cleanup. `blocklist_gw()` and `get_health_checks()` are public because they integrate with OSDMonitor and monitor health.

The inline `encode()` writes version 3 map state: global epoch, gateway states, timers, per-group epochs, beacon-diff additions, disaster locations, ever-enabled features, and currently published features. `decode()` handles versions up to 3 and leaves older maps without newer fields at defaults.

## Control Flow Contract
`NVMeofGwMon` owns proposal sequencing. It copies committed `map` to `pending_map`, calls mutators on `pending_map`, and encodes the pending map into Paxos. Mutators set `propose_pending` when the caller should commit a new version. Functions that affect gateway-visible state usually call or rely on `increment_gw_epoch()` under `NVMEOFHAMAP`.

Client-visible maps are not just the persisted structure: `to_gmap()` filters states and converts internal gateway states into `NvmeGwClientState`. Subscription logic may send a full map or a single-gateway slice depending on feature support.

## State and Persistence
The header distinguishes durable encoded fields from runtime-only fields indirectly. Durable fields are written by `encode()` and helpers in `NVMeofGwSerialize.h`; runtime fields such as selected timestamps and beacon counters are restored by the monitor around pending-map cloning. `fsm_timers` are part of the persisted map, but monitor ticks are responsible for expiring them and proposing resulting state changes.

## Dependencies and Integration Points
The map depends on `NVMeofGwTypes.h` for all gateway/domain types, `NVMeofGwSerialize.h` for inline serialization, `Monitor` for feature and service integration, Ceph message/address/time/formatter types, and monitor health infrastructure. It is referenced by `NVMeofGwMon.h`, `MNVMeofGwMap`, and command/beacon handling.

## Risks
The API uses many mutable references and out-parameters; callers must initialize and combine `propose_pending` values correctly. `mon` is a nullable raw pointer but most implementation paths assume it is set. Inline encoding makes feature-dependent wire layout part of the header contract, so changing fields requires strict compatibility handling. Some public methods have side effects beyond their names, such as updating epochs or starting timers.

## Test Signals
Header-level tests should verify encode/decode compatibility for map versions and features, `FLAG_BEACONDIFF` behavior, `to_gmap()` filtering, and per-group epoch semantics. Integration tests should exercise public mutators through `NVMeofGwMon` to ensure proposal flags and persisted state match caller expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwMon.cc -->
# sources/distributed-fs/ceph/src/mon/NVMeofGwMon.cc

## Purpose
`NVMeofGwMon.cc` implements the monitor Paxos service for NVMe-oF gateway HA maps. It loads and commits `NVMeofGwMap` versions, handles admin commands, receives gateway beacons, sends map ACKs/slices to gateways, tracks beacon timeouts, periodically advances map state, and exposes gateway status/listener queries.

## Important APIs, Functions, and Types
Lifecycle functions include `init()`, `on_restart()`, `on_shutdown()`, `create_pending()`, `encode_pending()`, `update_from_paxos()`, `get_trim_to()`, `cleanup_pending_map()`, `restore_pending_map_info()`, `recreate_gw_epoch()`, and `synchronize_last_beacon()`.

Periodic/subscription functions are `tick()`, `check_beacon_timeout()`, `check_subs()`, `check_sub_unconditional()`, `check_sub()`, and `get_gw_by_addr()`. Command handlers are `preprocess_query()`, `prepare_update()`, `preprocess_command()`, `prepare_command()`, and `get_gw_listeners()`. Beacon flow is implemented in `preprocess_beacon()`, `prepare_beacon()`, `apply_beacon()`, `process_gw_down()`, `get_ack_map_epoch()`, and `do_send_map_ack()`.

## Control Flow
On restart, the service clears `last_beacon`, resets the pending map, and calls `synchronize_last_beacon()` to seed timeout tracking for gateways that were available in the committed map. That function also forces gateways to receive ACK/full map information after leader election by setting beacon indexes and sequence/out-of-order flags.

`tick()` is leader-only and active-only. It compensates for missed monitor ticks by resetting beacon timestamps, then asks `pending_map` to expire active FSM timers, checks beacon timeouts, tracks deleting gateways using any live subsystem snapshot in each group, auto-enables beacon diff once the monitor quorum supports `FEATURE_NVMEOF_BEACON_DIFF`, handles abandoned ANA groups, and proposes if any of those actions changed pending state.

Paxos proposal flow mirrors other monitor services. `create_pending()` saves the previous pending map, copies committed `map`, restores selected non-persistent gateway fields, and increments epoch. `encode_pending()` asserts the expected next epoch, recreates missing `gw_epoch` entries under `NVMEOFHAMAP`, encodes with quorum features, stores the version and last-committed marker, and persists health checks. `update_from_paxos()` decodes the latest committed version, loads health, and notifies subscriptions.

Read commands are handled in `preprocess_command()`. `nvme-gw show` prints group epoch, beacon-diff status, feature/load-balancing hints, ANA group list, namespace counts, per-gateway location/admin/availability/startup/listener/state data, and disaster state. `nvme-gw listeners` aggregates live listeners by subsystem NQN and gateway id.

Mutating commands are handled in `prepare_command()`. `nvme-gw create/delete`, `enable/disable`, `set-location`, `disaster-set`, `disaster-clear`, and `set beacon-diff` call matching `NVMeofGwMap` mutators. If a real map change is needed, the command waits for the next commit; otherwise it replies immediately with errors or idempotent success.

Beacon handling is the most important runtime flow. `preprocess_beacon()` always returns false so the leader prepare path runs. `prepare_beacon()` parses gateway id, pool/group, beacon version, header version, sequence, reported availability, last OSD epoch, last gateway-map epoch, and subsystem list. A `GW_CREATED` beacon from a known gateway clears subsystems, sets beacon sequence, handles fast reboot by marking the old available gateway down and suppressing failovers briefly, records startup/address state, and refreshes `last_beacon`. Non-created beacons from unknown or deleting gateways are ignored/no-replied.

For existing gateways, enhanced beacon sequence numbers are checked. Out-of-order available beacons suppress failover briefly and force the gateway back through created/full-map handling. `apply_beacon()` either replaces full subsystem state for legacy beacons or applies add/change/delete subsystem deltas for enhanced beacons. It also clears old nonce maps when diff mode takes over and derives effective availability from admin state, subsystem presence, and listener presence. Available beacons refresh timeout state and call `process_gw_map_ka()`; unavailable or created states call `process_gw_down()`.

ACK logic deliberately separates proposal from response. The monitor periodically ACKs available correct-sequence beacons according to `mon_nvmeofgw_beacons_till_ack`, always ACKs cases that need recovery/full-map behavior, and sends an ACK immediately when no conflicting proposal is pending or when the gateway is in created state. ACK maps may contain a single gateway slice and use per-group `gw_epoch` when available.

## State and Persistence
Committed durable state is `map`; uncommitted state is `pending_map`. `last_beacon` and `last_beacon_check` are runtime timeout state, not encoded in Paxos. `gws_deleting_time` tracks how long gateways have been in deleting state for health warnings and is also runtime state. Selected non-persistent gateway fields (`allow_failovers_ts`, down/failback timestamps, map-epoch validity, beacon index, beacon sequence and out-of-order flag) are restored across pending map recreation.

Old NVMe-oF map versions are trimmed according to `mon_max_nvmeof_epochs`; the service keeps only a bounded history.

## Dependencies and Integration Points
The service integrates `PaxosService`, `md_config_obs_t`, `Monitor`, monitor sessions/subscriptions, `MMonCommand`, `MNVMeofGwBeacon`, `MNVMeofGwMap`, `NVMeofGwMap`, monitor feature negotiation, OSDMonitor through map blocklisting requests, and monitor health encoding. Gateway clients depend on ACK/map semantics for liveness and ANA ownership transitions.

## Risks
Beacon and timer handling is sensitive to monitor leadership gaps and local slowness; the tick compensation resets beacon clocks after missed ticks to avoid false failovers. `check_beacon_timeout()` erases entries while iterating over `last_beacon`, which should be scrutinized for C++ iterator correctness. Command preprocessing for read paths uses `map.created_gws[group_key]`, which can create empty groups in a non-const map if not carefully guarded.

ACK decisions combine feature bits, proposal state, gateway availability, sequence correctness, and beacon index; regressions could either spam ACKs or starve gateways of map updates. Runtime-only fields restored in `restore_pending_map_info()` are easy to miss when new fields are added. Unknown/deleting gateways get `no_reply`, so client retry behavior is part of the contract.

## Test Signals
Tests should cover restart synchronization, beacon-timeout suppression after missed ticks, Paxos encode/load/trim, subscription full-map versus unicast-map behavior, command idempotency and error replies, beacon created/available/unavailable paths, fast reboot suppression, out-of-order sequence ACKs, legacy full subsystem replacement, enhanced subsystem diff application, no-subsystem/no-listener downgrade, ACK epoch selection, and health updates after map changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwMon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwMon.h -->
# sources/distributed-fs/ceph/src/mon/NVMeofGwMon.h

## Purpose
`NVMeofGwMon.h` declares the NVMe-oF gateway monitor Paxos service. It defines the service state, lifecycle hooks, command/beacon dispatch, subscription handling, timeout tracking, and helper APIs that connect monitor Paxos to `NVMeofGwMap`.

## Important APIs, Types, and Members
`LastBeacon` identifies a gateway/group pair for timeout tracking and defines ordering/equality for `std::map`. `NVMeofGwMon` derives from `PaxosService` and `md_config_obs_t`. It owns committed `map`, `pending_map`, `last_beacon`, and `last_beacon_check`. It also exposes `gws_deleting_time` for health timing.

Overrides include config observer stubs, `create_initial()`, `create_pending()`, `encode_pending()`, `init()`, `on_shutdown()`, `on_restart()`, `update_from_paxos()`, `get_trim_to()`, `preprocess_query()`, `prepare_update()`, empty `encode_full()`, `tick()`, and `print_summary()`. Public service helpers include command/beacon preprocess/prepare methods, subscription checks, and `get_map()`.

Private helpers cover last-beacon synchronization, gateway-down processing, gateway lookup by connection address, ACK epoch selection, gateway epoch recreation, pending-map restoration/cleanup, listener formatting, beacon application, ACK sending, and timeout checks.

## Control Flow Contract
The service is leader-driven for periodic work and Paxos-driven for mutations. Gateway beacons always flow to the prepare path because they may mutate pending state. Commands can be answered in preprocessing if read-only or prepared as Paxos updates if mutating. Subscriptions are checked after map loads and ticks to deliver full or filtered maps.

## State and Persistence
`map` is the committed Paxos state, while `pending_map` is rebuilt from `map` for each proposal. `last_beacon`, `last_beacon_check`, and `gws_deleting_time` are monitor-local runtime state. The constructor sets `map.mon = &mn`; `pending_map.mon` is not set in the header, so implementation paths rely on copy/assignment or external initialization to preserve monitor access.

## Dependencies and Integration Points
The class includes `PaxosService` and `NVMeofGwMap`. It is instantiated by `Monitor` as the `PAXOS_NVMEGW` service and interacts with monitor sessions, gateway beacon/map messages, OSDMonitor, and monitor health. `md_config_obs_t` is present but currently observes no keys.

## Risks
The class stores maps by value, so copies must preserve embedded `Monitor *` where implementation methods need it. Config observer stubs mean changes to relevant NVMe-oF config are read dynamically through `g_conf()` rather than cached here. `LastBeacon` ordering must remain stable with `NvmeGroupKey` ordering for timeout erasure and lookup correctness.

## Test Signals
Tests should instantiate the service with monitor fixtures, verify lifecycle and map pointer initialization, exercise LastBeacon ordering, check runtime state reset on restart, and cover public preprocess/prepare dispatch with beacon and command messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwMon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwSerialize.h -->
# sources/distributed-fs/ceph/src/mon/NVMeofGwSerialize.h

## Purpose
`NVMeofGwSerialize.h` provides inline stream operators and encode/decode functions for NVMe-oF gateway monitor types. It defines the wire/persistent layout used by `NVMeofGwMap`, gateway client maps, beacon subsystem data, timer state, per-group epochs, disaster additions, and human-readable debug output.

## Important APIs, Types, and Functions
The header defines `MAX_SUPPORTED_ANA_GROUPS` as 16 for legacy fixed-width layouts. Stream operators cover gateway export state, internal state-machine state, availability, admin state, `SmState`, beacon namespace/listener/subsystem, `NqnState`, `NvmeGwClientState`, group keys, gateway maps, nonce maps, internal gateway state, location states, and whole `NVMeofGwMap`.

Serialization functions cover `ana_state_t`, `GwSubsystems`, `NvmeGwClientState`, `NvmeGwTimerState`, `NvmeAnaNonceMap`, `NvmeGwMonStates`, `gw_epoch`, `LocationState`, `created_gws`, beacon-diff additions, client gateway maps, timer maps, `BeaconNamespace`, `BeaconListener`, `BeaconSubsystem`, and beacon change descriptors.

## Control Flow
Encoding is feature-aware. `GwSubsystems` encodes version 1 with exactly 16 ANA entries unless `NVMEOFHA` is present, where version 2 uses variable-sized ANA state. `NvmeGwTimerState` similarly uses a fixed 16-entry legacy layout or keyed variable entries with end-time milliseconds. `NvmeGwMonStates` uses version 1 fixed state/blocklist arrays, version 2 keyed HA state, and version 3 adds `addr_vect` and `beacon_index` under `NVMEOFHAMAP`.

`NVMeofGwMap::encode()` calls these helpers in a fixed order, then `decode()` mirrors that order by struct version. Beacon-diff additions are encoded after base `created_gws`; they iterate the already decoded gateway order to append admin state, location, and subsystem change descriptors. Legacy version-1 decode collects created ANA groups and erases unused fixed-array entries after all gateways are known.

## State and Persistence Behavior
This header defines what is durable. State encoded here survives Paxos replication and monitor restart; fields omitted here must be restored or treated as runtime-only. Timer end-times are serialized as milliseconds since the system-clock epoch. Gateway address vectors are encoded only in `NvmeGwMonStates` version 3. Beacon sequence values for client state are encoded in `NvmeGwClientState` version 2, while internal gateway map sequence persistence is partly managed outside these helpers.

Change descriptors are not encoded inside `BeaconSubsystem` itself; they are stored by the separate beacon-diff additions pass for gateway map persistence. That means the decode order must match the exact nested order of decoded `created_gws`.

## Dependencies and Integration Points
The header depends on `NVMeofGwTypes.h`, Ceph encoding macros, feature bits `NVMEOFHA` and `NVMEOFHAMAP`, `entity_addrvec_t` encoding, monitor logging, and `MAX_SUPPORTED_ANA_GROUPS` consumers in `NVMeofGwMap.cc`. It is included at the end of `NVMeofGwMap.h`, making the overloads available to map and message encoding.

## Risks
Most stream operators and some encode helpers take values by copy, which is fine for debug but expensive for large gateway maps. Feature-gated layouts must remain backward-compatible; adding fields without version increments or matching decode guards would corrupt Paxos state or gateway messages. `decode_gws_beacon_diff_additions()` assumes the base created-gateway structure has already been decoded and iterates in identical map order. Legacy fixed-array handling depends on `MAX_SUPPORTED_ANA_GROUPS` staying consistent with older clients.

Timer persistence uses wall-clock `system_clock`; clock jumps can affect timeout behavior after decode. Debug output may include sensitive listener/nonce-like values in logs.

## Test Signals
Serialization tests should round-trip each type under no HA, `NVMEOFHA`, and `NVMEOFHAMAP` feature sets; verify legacy fixed 16-entry maps shrink to created ANA ids on decode; verify beacon-diff additions preserve admin state, location, and descriptors; test timer end-time persistence; and check client map encode/decode for version-1 and version-2 fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwSerialize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwTypes.h -->
# sources/distributed-fs/ceph/src/mon/NVMeofGwTypes.h

## Purpose
`NVMeofGwTypes.h` defines the domain model for monitor-managed NVMe-oF gateways. It provides aliases, enums, and structs shared by the map, monitor service, messages, serialization helpers, and gateway client state conversion.

## Important APIs, Types, and Functions
Aliases define gateway ids, locations, group keys `(pool, group)`, subsystem NQNs, ANA group ids, nonce vectors, nonce maps, client maps, timer maps, monitor gateway maps, and disaster location maps. Enums describe internal ANA state (`gw_states_per_group_t`), exported ANA state (`gw_exported_states_per_group_t`), gateway availability, admin state, and beacon subsystem change descriptors.

Beacon structures include `BeaconNamespace` with ANA group id and nonce, `BeaconListener` with address family/address/service id, and `BeaconSubsystem` with NQN, listener list, namespace list, and change descriptor. Equality operators support comparing beacon content.

`NvmeGwMonState` is the internal per-gateway monitor state: native ANA group id, availability, last map epoch validity, startup flag, subsystems, nonce map, per-ANA state machine map, blocklist data, address vector, beacon sequence/index fields, admin state, location, and timing controls for failovers/failbacks. It provides helpers for unavailable state, beacon sequence reset, standby/active state assignment, and down timestamp updates.

`NqnState` converts internal state-machine data into exported ANA state vectors, marking active or wait-blocklist groups optimized and other groups inaccessible. `NvmeGwClientState` is sent to gateways and includes native group id, map epoch, exported subsystems, availability, last beacon sequence status, and map feature flags. `Tmdata`, `NvmeGwTimerState`, and `LocationState` model timers and disaster cleanup state.

## Control Flow
These types are passive data structures used by `NVMeofGwMap` and `NVMeofGwMon`. Beacons populate `BeaconSubsystems`; monitor logic mutates `NvmeGwMonState`; `to_gmap()` creates `NvmeGwClientState` and `NqnState` for outbound maps. State-machine enums govern failover and failback transitions.

## State and Persistence Behavior
Many fields in `NvmeGwMonState` are encoded by `NVMeofGwSerialize.h`, but comments identify some timing fields as non-persistent. `allow_failovers_ts`, `last_gw_down_ts`, `delay_failbacks_ts`, last map validity, and beacon sequence/index fields require explicit restoration across pending map reconstruction. `REDUNDANT_GW_ANA_GROUP_ID` (`0xFF`) marks a gateway without a normal owned ANA group.

## Dependencies and Integration Points
The header depends on Ceph basic types and `entity_addrvec_t`. It is included by `NVMeofGwMap.h`, serialization helpers, monitor service code, and messages. The beacon listener comment ties listener shape to SPDK JSON-RPC NVMf listener representation.

## Risks
Default constructors leave some fields in `NvmeGwMonState` dependent on in-class initializers and some constructor-specific initialization; code must avoid using uninitialized availability in paths that use the default constructor. `NqnState` fills fake inaccessible entries to preserve vector index equals ANA group id, so off-by-one handling between gateway ANA ids and namespace ANA ids is a recurring risk. Timing fields use `system_clock`, making them sensitive to wall-clock changes.

## Test Signals
Tests should cover enum-to-client mapping through `NqnState`, equality operators for beacon diffs, default and ANA-id gateway-state construction, standby/active helper effects on blocklist data, `set_unavailable_state()` preserving deleting state, exported ANA vector indexing, and client-state defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/NVMeofGwTypes.h -->
