# sources/distributed-fs/ceph/src/mon/Monitor.h

## Purpose

`Monitor.h` declares Ceph's top-level monitor class, the monitor daemon object that coordinates cluster membership, elections, Paxos, per-subsystem monitor services, authentication, sessions, command handling, synchronization, scrubbing, health reporting, time checks, and stretch-mode state. The header is the architectural map for `Monitor.cc`: it exposes the lifecycle APIs used by mainline monitor startup, the callbacks used by `Elector`, `Paxos`, messenger dispatch, auth code, and the service monitors, and the state fields that tie these subsystems together.

The class inherits from `Dispatcher`, `AuthClient`, `AuthServer`, and `md_config_obs_t`, which makes a `Monitor` simultaneously a messenger dispatcher, an outbound auth client for monitor-to-monitor and monitor-to-manager connections, an auth server for clients and daemons, and a config observer for runtime option changes.

## Important APIs and types

The public lifecycle surface includes the constructor/destructor, `preinit()`, `init()`, `init_paxos()`, `refresh_from_paxos()`, `shutdown()`, `tick()`, `handle_signal()`, `mkfs()`, FSID helpers, `sanitize_options()`, `do_admin_command()`, and config observer methods. These are the entry points for daemon setup, store initialization, active operation, and shutdown.

Monitor state is modeled by a private enum with `STATE_INIT`, `STATE_PROBING`, `STATE_SYNCHRONIZING`, `STATE_ELECTING`, `STATE_LEADER`, `STATE_PEON`, and `STATE_SHUTDOWN`. The header provides predicates such as `is_probing()`, `is_synchronizing()`, `is_leader()`, and `is_shutdown()`, plus `get_state_name()` helpers. Callers use these state checks to gate dispatch, election callbacks, leader-only operations, and asynchronous continuations.

Election and quorum fields include `paxos`, `elector`, `required_features`, `leader`, `quorum`, `quorum_since`, `leader_since`, `exited_quorum`, `quorum_feature_map`, `quorum_con_features`, `quorum_mon_features`, `quorum_min_mon_release`, and `outside_quorum`. Public election APIs include `bootstrap()`, `join_election()`, `start_election()`, `win_standalone_election()`, `win_election()`, `lose_election()`, `finish_election()`, feature-application helpers, quorum getters, and `get_combined_feature_map()`.

The `paxos_service` array is indexed by `PAXOS_*` service ids and stores all subsystem services as `unique_ptr<PaxosService>`. Typed accessors expose MDS, monmap, OSD, auth, log, mgr, mgrstat, health, config, KV, and NVMe-oF gateway monitors. `Paxos`, `OSDMonitor`, `MDSMonitor`, `MonmapMonitor`, `LogMonitor`, and `KVMonitor` are friends, reflecting the tight coupling between top-level quorum state and service behavior.

Session and command APIs include `MonSessionMap session_map`, `with_session_map()`, `send_latest_monmap()`, `handle_get_version()`, `handle_subscribe()`, `handle_mon_get_map()`, command map helpers, `_allowed_command()`, `get_mon_status()`, `_quorum_status()`, bootstrap peer hint handling, `handle_tell_command()`, `handle_command()`, `handle_route()`, `reply_command()`, `reply_tell_command()`, and status/metadata helpers. `RoutedRequest` captures forwarded client requests by tid, encoded message, original session/connection/features, and the associated op.

Sync declarations are split into provider and requester state. `SyncProvider` stores provider-side peer addrs, cookie, timeout, last committed version, last key, whether the scan is full, and a `MonitorDBStore::Synchronizer`. Requester fields store source addrs, cookie, full/recent mode, start version, timeout event, and `sync_last_committed_floor`. APIs include `get_sync_targets_names()`, requester/provider reset, timeout, monmap backup, `sync_start()`, `sync_force()`, critical-state stashing, chunk requests, finish, and handlers for each `MMonSync` operation.

Scrub declarations include `ScrubState`, `ScrubContext`, atomic `scrub_ctx`, event pointers, start/check/finish/reset/update APIs, and `_scrub()` for store prefix traversal. Timecheck declarations include maps for waiting peers, skews, latencies, round tracking, event pointer, and leader/peon handlers. Health declarations include a cached overall status, periodic event pointers, health-to-clog scheduling, health logging, and pending metadata update.

Auth declarations cover outbound `AuthClient` methods, inbound `AuthServer::handle_auth_request()`, fast accept/reset hooks, authorizer construction, default keyring writing, monitor key extraction, keyring requirement checks, and metadata collection. These are guarded by `auth_lock` and backed by `KeyRing`, `KeyServer`, and auth method lists.

Stretch-mode declarations include booleans for engaged/degraded/recovering state, CRUSH location information, dead/up bucket tracking, election work, session filtering, disallowed leader updates, and leader-triggered transition methods for degraded, recovery, healthy, enable, disable, and monitor CRUSH location updates.

The header also defines monitor and cluster perf counter id ranges, `CEPH_MON_PROTOCOL`, compat-set key location, release-based incompat feature macros, the release-independent NVMe-oF beacon diff feature, and `C_MonContext`, a shutdown-aware lambda context wrapper that skips completion if the monitor is already shut down.

## Control flow implied by the header

Startup flow is declared as `preinit()` for store/config/auth/admin preparation, `init()` for starting timers, messengers, thread pools, and bootstrap, then `bootstrap()` for probing and election. Election completion enters either `win_election()` or `lose_election()`, both of which ultimately call `finish_election()` after Paxos and service setup.

Runtime message flow enters `ms_dispatch()` with the monitor lock and delegates to `_ms_dispatch()`, then `dispatch_op()`. The declared handlers show the major dispatch categories: auth, subscriptions, get-map/get-version, commands, forwarding/routing, probes, sync, scrub, ping, timecheck, and service messages.

Sync control flow is request/response oriented. A synchronizing monitor calls `sync_start()`, receives a cookie, repeatedly requests chunks, applies encoded transactions, and calls `sync_finish()`. A provider keeps one `SyncProvider` per cookie and expires stale providers in periodic work.

Leader-only periodic control flow is visible through scrub, health, timecheck, and stretch-mode declarations. Timer `Context*` fields make cancellation important during state changes, shutdown, and election resets. Waiter lists (`waitfor_quorum` and `maybe_wait_for_quorum`) indicate that operations can be deferred until quorum or retried on tick/election completion.

## State and persistence behavior

The header separates durable store access (`MonitorDBStore *store`, `MONITOR_NAME`, `MONITOR_STORE_PREFIX`) from in-memory runtime state. It declares APIs that persist feature compatibility, FSID, mkfs seed data, monitor metadata, sync markers, and cluster fingerprint. The `CompatSet features` field and `required_features` are key gates for upgrades and peer compatibility.

Quorum state is deliberately volatile: leader, quorum set, feature intersections, outside-quorum set, and time stamps are reset on bootstrap or election changes. Persistent Paxos state is owned by `Paxos` and `PaxosService` instances, but the monitor owns the sync machinery that copies the relevant store prefixes and protects the latest monmap and last-committed floor during full sync.

Session state is mostly volatile and connection-bound. `MonSessionMap`, routed requests, feature maps, subscriptions, and session timeouts are not durable. The header's separate `session_map_lock` signals that session collections can be manipulated outside the primary monitor lock in messenger callbacks.

## Dependencies and integration points

`Monitor.h` depends on Ceph common types, health types, timer/finisher/thread-pool primitives, config observer APIs, log client, auth client/server/keyring/CephX APIs, monitor DB store, monmap types, manager client, op tracking, and work queue support. It forward-declares messenger and map types where possible but includes many monitor-specific headers because the class owns concrete subsystems.

Integration points are broad: `Elector` calls election callbacks and is a friend; `Paxos` and services access monitor state; messenger calls dispatch and connection/auth hooks; admin socket routes local commands through `AdminSocketHook`; config changes arrive through `md_config_obs_t`; manager integration uses `MgrClient`; service monitors use typed accessors and command dispatch.

## Risks and edge cases

The header exposes a large mutable class with many raw pointers (`Messenger*`, `MonMap*`, `MonitorDBStore*`, `PerfCounters*`, event `Context*`, `AdminSocketHook*`) mixed with owned `unique_ptr` and reference-counted Ceph types. Shutdown ordering and timer cancellation are therefore critical. `C_MonContext` mitigates callbacks after shutdown, but only for callbacks wrapped with it.

Because many subsystems are friends or accessed through typed casts from `paxos_service`, refactors can easily break hidden invariants. The service order in the constructor and election finish order matter, especially `MonmapMonitor` being finished before other services on leader election.

Feature macros at the bottom are upgrade-sensitive. Adding a new monitor feature requires updating supported-feature construction and requirement calculation in the implementation. Missing one side can make monitors write unsupported feature sets, fail to require necessary peer bits, or admit incompatible peers.

Sync and scrub state use raw event pointers and shared/atomic scrub context. Races around state reset, election changes, and timeouts must preserve the rule that only a leader drives scrub and only a synchronizing requester accepts sync chunks.

Stretch mode assumes monitor CRUSH locations and OSDMap CRUSH topology are populated consistently. Several implementation paths assert on missing entries, so callers must set locations before enabling stretch-mode behavior.

## Test signals

Header-driven coverage should verify state predicate transitions, lifecycle method ordering, config observer registration/removal, election callback effects, service accessor indices, and command description compatibility for old/new mon features.

Persistence tests should exercise feature macro additions, `read_features_off_disk()` and `write_features()` behavior, FSID checking/writing, mkfs seed keys, and sync marker declarations through the implementation. Static or compile-time checks are useful when adding `PAXOS_*` services to ensure the `paxos_service` array, typed accessor, constructor initialization, dispatch, and sync prefix logic remain aligned.

Concurrency tests should stress shutdown while timers, finisher callbacks, auth handshakes, sync timeouts, scrub timeouts, and forwarded requests are active. Stretch-mode tests should cover location parsing, election disallowed leaders, degraded/recovery/healthy transitions, and OSD session filtering.
