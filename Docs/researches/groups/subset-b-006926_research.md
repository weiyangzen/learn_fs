# subset-b-006926 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Monitor.cc -->
# sources/distributed-fs/ceph/src/mon/Monitor.cc

## Purpose

`Monitor.cc` implements the top-level Ceph monitor daemon behavior declared in `Monitor.h`. It is the glue between the monitor messenger, auth, election, Paxos, monitor-local commands, Paxos-backed services, monitor store synchronization, cluster health logging, clock skew checking, monitor DB scrubbing, session management, and stretch-mode policy. The file is intentionally central: it decides whether incoming messages are accepted locally, forwarded to the elected leader, dispatched to a Paxos service, delayed until quorum, or dropped.

The implementation covers the whole monitor lifecycle: constructor service wiring, `preinit()`, `init()`, bootstrap/probe, election transitions, quorum activation, periodic `tick()`, admin and client command handling, store sync, and shutdown. It also persists and checks critical monitor-local data such as feature compatibility, cluster UUID, cluster fingerprint, mkfs seed state, mon metadata, and sync recovery markers.

## Important APIs, types, and functions

The constructor builds the monitor's long-lived dependencies: `Paxos`, all `PaxosService` implementations (`MDSMonitor`, `MonmapMonitor`, `OSDMonitor`, `AuthMonitor`, `LogMonitor`, `MgrMonitor`, `MgrStatMonitor`, `HealthMonitor`, `ConfigMonitor`, `KVMonitor`, `NVMeofGwMon`), log channels, auth requirement lists, manager client, perf tracking, command descriptions, and monitor caps. The destructor asserts that sessions have already been removed and shuts down the op tracker.

`preinit()` validates options, creates monitor and cluster perf counters, checks or writes the FSID, reads on-disk compat features, applies initial monmap member filtering, handles previously-joined monitor removal semantics, clears partial sync state when needed, initializes Paxos and services, bootstraps keyring/auth material, registers admin socket commands, and installs config/auth hooks. `init()` starts the finisher, timer, CPU thread pool, messengers, mgr client, moves to `STATE_PROBING`, calls `bootstrap()`, and records this monitor in the session feature map.

`bootstrap()`, `_reset()`, `handle_probe_probe()`, and `handle_probe_reply()` implement discovery and join logic. `bootstrap()` recalculates rank from the monmap, respawns if the address changed, resets quorum/election/Paxos service state, optionally compacts the store, handles singleton-mon election, sends `MMonProbe` to peers and hints, and waits for enough peers to form or join a quorum. Probe replies can update the monmap, rename seed peers, start full or recent sync when Paxos versions diverge, join an existing quorum via `MMonJoin`, or call an election when enough out-of-quorum mons are visible.

`join_election()`, `start_election()`, `win_standalone_election()`, `win_election()`, `lose_election()`, and `finish_election()` transition between probing/electing/leader/peon. The leader path initializes Paxos leader state, finishes `MonmapMonitor` first, schedules health/timecheck/scrub work, persists pending metadata into the next Paxos transaction, and registers cluster counters. The peon path initializes Paxos peon state and finishes all services.

`sync_start()`, `handle_sync()`, `handle_sync_get_cookie()`, `handle_sync_get_chunk()`, `handle_sync_cookie()`, `handle_sync_chunk()`, and `sync_finish()` implement monitor DB synchronization. Requesters can perform a full sync, which stashes critical state and clears Paxos service prefixes, or a recent catch-up sync. Providers issue cookies, stream Paxos commits and key/value chunks bounded by configured payload/key limits, and expire stale provider state. `sync_last_committed_floor` prevents a monitor that used to have newer commits from syncing backward from an outdated peer.

`handle_command()` is the main client command dispatcher. It parses JSON command maps, validates command descriptions against leader/local/mgr command sets, enforces obsolete/deprecated/noforward/compatibility rules, checks monitor capabilities, audits dispatches, forwards unsupported commands to the leader when allowed, proxies manager commands with `mgr_proxy_bytes` accounting, and dispatches command families to the appropriate Paxos service or local handler. Local command handling covers `fsid`, `mon scrub`, `time-sync-status`, `status`, `health`, `df`, `report`, `node ls`, `features`, metadata/version commands, quorum status, ok-to-stop/add/rm checks, and version reporting.

`_ms_dispatch()` and `dispatch_op()` form the message ingress path. `_ms_dispatch()` creates a tracked op, creates or refreshes `MonSession` objects, updates session auth/caps metadata, applies stretch-mode connection filtering, and either waitlists clients during sync/out-of-quorum or dispatches immediately. `dispatch_op()` handles auth/ping/tell before authentication, enforces insecure global-id reclaim policy, passes known service messages to Paxos services, handles monitor-readable messages, and accepts monitor-only messages such as route/probe/sync/scrub/join/paxos/election/forward/timecheck/health-check messages.

`forward_request_leader()`, `handle_forward()`, `send_reply()`, `handle_route()`, and `resend_routed_requests()` implement leader forwarding. A peon stores the original request in `routed_requests`, sends an `MForward` to the leader with client caps and connection features, and later routes `MRoute` replies back to the original client. The leader unwraps the original request onto an `AnonConnection` and dispatches it as if it came from the client, while preserving proxy metadata.

Health, time, and scrub APIs are implemented by `health_tick_start()`, `health_interval_start()`, `do_health_to_clog()`, `log_health()`, `timecheck_*()`, `scrub_start()`, `scrub()`, `handle_scrub()`, `_scrub()`, `scrub_check_results()`, and timeout/event helpers. Health logging deduplicates repeated messages, emits clear messages, and schedules interval output. Timecheck is leader-driven ping/pong/report for quorum clock skew and latency. Scrub compares CRC/key-count summaries of monitor-store prefixes across quorum members.

Persistence and identity helpers include `get_supported_features()`, `read_features_off_disk()`, `write_features()`, `apply_*_compatset_features()`, `calc_quorum_requirements()`, `prepare_new_fingerprint()`, `check_fsid()`, `write_fsid()`, `mkfs()`, `load_metadata()`, and `sync_force()`. Auth helpers include `write_default_keyring()`, `extract_save_mon_key()`, `get_auth_request()`, `handle_auth_request()`, `get_authorizer()`, `ms_handle_accept()`, and `ms_handle_fast_authentication()`.

Stretch-mode functions include `set_mon_crush_location()`, `notify_new_monmap()`, `set_elector_disallowed_leaders()`, `try_engage_stretch_mode()`, `try_disable_stretch_mode()`, `do_stretch_mode_election_work()`, degraded/recovery/healthy transition triggers, and `session_stretch_allowed()`.

## Control flow

Startup enters `preinit()` before active messenger dispatch. That stage validates configuration, store identity, compat features, auth bootstrap state, and admin/config hooks. `init()` starts asynchronous infrastructure and calls `bootstrap()`. Bootstrap resets transient state, decides rank membership, handles address changes by respawning, sends probes, and waits for replies.

Probe replies drive one of four branches: adopt a newer committed monmap and rebootstrap; sync if local Paxos state is too far behind; join an already existing quorum; or start a new election once enough out-of-quorum monitors are visible. Election callbacks come from `Elector`; winning makes this monitor leader and initializes Paxos/services in leader mode, losing makes it peon and initializes them in peon mode. `finish_election()` applies compat feature persistence, enables auth with mon rank/size, releases waiters, resends routed requests, and performs stretch-mode election work.

Runtime message flow starts in `_ms_dispatch()` under `Monitor::lock`. It builds a `MonOpRequest`, ensures a session exists when legal, updates auth/session metadata, then defers, drops, or calls `dispatch_op()`. The dispatch layer is type-based and intentionally staged: unauthenticated auth/ping/tell can pass; authenticated client/service messages are routed by message type; monitor-only control messages require monitor origin and often `MON_CAP_X`; Paxos messages are additionally epoch-checked and ignored during sync.

Command flow is parallel to message flow but command-aware. `handle_command()` maps a command prefix to a leader-advertised command, validates local compatibility, optionally forwards to leader, checks caps, and then dispatches by module. It uses `C_Command` continuations for asynchronous command completion, so a successful command path audits completion and sends `MMonCommandAck`; `-EAGAIN` redispatches; `-ECANCELED` drops silently.

Periodic control flow runs through `tick()`, which logs delayed health updates, ticks and trims Paxos services, trims client sessions, expires sync provider cookies, releases maybe-wait-for-quorum messages, proposes a cluster fingerprint when needed, updates mgr daemon health metrics, and reschedules itself. Separate timer events handle probe timeouts, sync timeouts, timecheck rounds, scrub rounds, and health-to-clog intervals.

## State and persistence behavior

In-memory monitor state is represented by `state`, `leader`, `quorum`, `quorum_since`, `leader_since`, `outside_quorum`, feature intersections, metadata maps, sync request/provider state, scrub context, timecheck maps, session maps, routed request maps, and stretch-mode flags. `Monitor::lock` protects most monitor state; `session_map_lock` protects session collections; `auth_lock` protects auth server/client state.

Persistent state lives in `MonitorDBStore`. `MONITOR_NAME` keys include `cluster_uuid`, `feature_set`, `joined`, and `cluster_fingerprint`. `MONITOR_STORE_PREFIX` stores `last_metadata`. The `mkfs` prefix stores seed monmap/osdmap/keyring. The `mon_sync` prefix stores `in_sync`, `force_sync`, `last_committed_floor`, `latest_monmap`, and `temp_newer_monmap` to survive restart or interrupted sync. Paxos and each Paxos service own additional prefixes returned by `get_sync_targets_names()`.

Feature persistence is conservative. `read_features_off_disk()` creates a legacy feature set when missing. Election finish can add required compat features derived from quorum connection features and monmap persistent features, then writes `feature_set` and recalculates `required_features`. Startup refuses unsupported on-disk features via `check_features()`.

Sync persistence is failure-conscious. Full sync first stashes the latest known monmap and a last-committed floor, marks `in_sync`, applies the transaction, then clears synchronizable prefixes. Completion reconstructs Paxos transactions for full sync, erases sync markers, reinitializes Paxos/services, and bootstraps. This ordering avoids silently booting from partially cleared state, but it also means interrupted sync paths must preserve the stash markers correctly.

## Dependencies and integration points

The file depends heavily on Ceph monitor internals: `Paxos`, `PaxosService`, `Elector`, `MonitorDBStore`, `MonMap`, `MonSession`, command parsing, message classes, `LogClient`, `MgrClient`, auth client/server APIs, CephX key server, `SafeTimer`, `Finisher`, `ThreadPool`, perf counters, admin socket, and config observers. It integrates with every monitor service through the `paxos_service` array and typed accessors.

External daemon integration happens through messenger sessions for clients, OSDs, MDSs, MGRs, NVMe-oF gateways, and peer monitors. Manager integration includes `MgrClient` command proxying, daemon metadata updates, daemon health metrics, and service/progress status reporting. Admin integration is via admin socket command registration and `do_admin_command()`. Storage integration uses `MonitorDBStore` transactions, synchronizers, compaction, flush, and raw device metadata for SMART and metadata reporting.

## Risks and edge cases

The file is a high-risk coordination point because election, Paxos, sync, auth, and command dispatch share the same monitor lock. Any blocking store, auth, messenger, or admin-socket call in the wrong lock order can create deadlock or latency spikes. The implementation explicitly unlocks around admin socket registration and store flush in some places, which are important patterns to preserve.

Sync has several crash windows and uses debug kill injection points. The ordering around `mon_sync/in_sync`, store clearing, `last_committed_floor`, and `sync_finish()` is critical. Regressions can lead to a monitor rejoining with stale committed state, clearing too much, or failing to preserve the newest monmap.

Command dispatch is broad and security-sensitive. It checks command existence, compatibility, obsolete/deprecated flags, forwarding policy, session capabilities, mgr proxy byte limits, and module-specific dispatch. A new command in `MonCommands.h` or a service command map can become unsafe if its module, permissions, or noforward/mgr flags do not match this dispatcher.

Forwarding and routed requests depend on session lifetimes and feature-specific reencoding. Losing a session must remove routed requests; elections must resend or self-retry them. `AnonConnection` intentionally aborts if code tries to reply directly rather than route through `send_reply()`, so forwarded command paths must use monitor reply helpers.

Stretch-mode session filtering can mark down OSD sessions whose CRUSH zone differs from the monitor's zone. It assumes monmap CRUSH locations and OSDMap CRUSH data are readable and consistent; missing locations are asserted. Changes here can disrupt client/OSD routing in stretched clusters.

Timecheck uses wall-clock `utime_t` and explicitly handles clock readjustment. Clock skew reporting can be masked by latency because skew is bounded by subtracting observed latency. Health logging intentionally suppresses repeated updates for a configured period, so tests must account for delayed output.

## Test signals

Useful direct test signals include monitor unit or integration tests that exercise bootstrap/probe/election with varied monmaps, singleton monitor election, joining an existing quorum, monmap address changes and respawn stashing, full and recent monitor store sync, `sync_force`, interrupted sync marker recovery, and `sync_last_committed_floor` protection.

Command tests should cover unknown commands, missing/empty prefixes, obsolete/deprecated handling, command-description output, leader/peon forwarding, noforward rejection, mgr proxy byte limiting, service dispatch routing, monitor-local commands such as `mon scrub`, `quorum_status`, metadata/version commands, and permission denial audit paths.

Message dispatch tests should cover unauthenticated stray messages, auth handshakes for msgr1/msgr2, insecure global-id reclaim behavior, session trimming, waitlist-or-zap behavior while out of quorum or synchronizing, routed reply cleanup on session reset, and monitor-only message cap checks.

Persistence tests should inspect `feature_set`, `cluster_uuid`, `cluster_fingerprint`, `last_metadata`, `mkfs` seed keys, and `mon_sync` keys before and after mkfs, preinit, election finish, sync, and forced sync. Scrub tests can use `mon_scrub_inject_missing_keys` and `mon_scrub_inject_crc_mismatch`; sync tests can use `mon_sync_provider_kill_at`, `mon_sync_requester_kill_at`, and payload/key limits. Stretch-mode tests should cover monmap/OSDMap enable/disable, degraded/recovery/healthy transitions, tiebreaker exclusion, disallowed leaders, and OSD session rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Monitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Monitor.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Monitor.h -->
