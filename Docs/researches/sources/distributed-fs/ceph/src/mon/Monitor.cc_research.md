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

`handle_command()` is the main client command dispatcher. It parses JSON command maps, validates command descriptions against leader/local/mgr command sets, enforces obsolete/deprecated/noforward/compatibility rules, checks monitor capabilities, audits dispatches, forwards unsupported commands to the leader when allowed, proxies manager commands with `mgr_proxy_bytes` accounting, and dispatches command families to the appropriate Paxos service or local handler.

`_ms_dispatch()` and `dispatch_op()` form the message ingress path. `_ms_dispatch()` creates a tracked op, creates or refreshes `MonSession` objects, updates session auth/caps metadata, applies stretch-mode connection filtering, and either waitlists clients during sync/out-of-quorum or dispatches immediately. `dispatch_op()` handles auth/ping/tell before authentication, enforces insecure global-id reclaim policy, passes known service messages to Paxos services, handles monitor-readable messages, and accepts monitor-only messages such as route/probe/sync/scrub/join/paxos/election/forward/timecheck/health-check messages.

`forward_request_leader()`, `handle_forward()`, `send_reply()`, `handle_route()`, and `resend_routed_requests()` implement leader forwarding. A peon stores the original request in `routed_requests`, sends an `MForward` to the leader with client caps and connection features, and later routes `MRoute` replies back to the original client. The leader unwraps the original request onto an `AnonConnection` and dispatches it as if it came from the client, while preserving proxy metadata.

Health, time, and scrub APIs are implemented by `health_tick_start()`, `health_interval_start()`, `do_health_to_clog()`, `log_health()`, `timecheck_*()`, `scrub_start()`, `scrub()`, `handle_scrub()`, `_scrub()`, `scrub_check_results()`, and timeout/event helpers. Persistence and identity helpers include supported-feature APIs, feature read/write, compat application, cluster fingerprint, FSID, mkfs, metadata loading, and forced sync. Auth helpers implement monitor outbound authorizers and inbound auth sessions. Stretch-mode helpers handle enable/disable, degraded/recovery/healthy transitions, disallowed leaders, and OSD session filtering.

## Control flow

Startup enters `preinit()` before active messenger dispatch. That stage validates configuration, store identity, compat features, auth bootstrap state, and admin/config hooks. `init()` starts asynchronous infrastructure and calls `bootstrap()`. Bootstrap resets transient state, decides rank membership, handles address changes by respawning, sends probes, and waits for replies.

Probe replies drive one of four branches: adopt a newer committed monmap and rebootstrap; sync if local Paxos state is too far behind; join an already existing quorum; or start a new election once enough out-of-quorum monitors are visible. Election callbacks come from `Elector`; winning makes this monitor leader and initializes Paxos/services in leader mode, losing makes it peon and initializes them in peon mode. `finish_election()` applies compat feature persistence, enables auth with mon rank/size, releases waiters, resends routed requests, and performs stretch-mode election work.

Runtime message flow starts in `_ms_dispatch()` under `Monitor::lock`. It builds a `MonOpRequest`, ensures a session exists when legal, updates auth/session metadata, then defers, drops, or calls `dispatch_op()`. The dispatch layer is type-based and intentionally staged: unauthenticated auth/ping/tell can pass; authenticated client/service messages are routed by message type; monitor-only control messages require monitor origin and often `MON_CAP_X`; Paxos messages are additionally epoch-checked and ignored during sync.

Command flow is parallel to message flow but command-aware. `handle_command()` maps a command prefix to a leader-advertised command, validates local compatibility, optionally forwards to leader, checks caps, and then dispatches by module. It uses `C_Command` continuations for asynchronous command completion, so a successful command path audits completion and sends `MMonCommandAck`; `-EAGAIN` redispatches; `-ECANCELED` drops silently.

Periodic control flow runs through `tick()`, which logs delayed health updates, ticks and trims Paxos services, trims client sessions, expires sync provider cookies, releases maybe-wait-for-quorum messages, proposes a cluster fingerprint when needed, updates mgr daemon health metrics, and reschedules itself. Separate timer events handle probe timeouts, sync timeouts, timecheck rounds, scrub rounds, and health-to-clog intervals.

## State and persistence behavior

In-memory monitor state is represented by `state`, `leader`, `quorum`, quorum timestamps, feature intersections, metadata maps, sync request/provider state, scrub context, timecheck maps, session maps, routed request maps, and stretch-mode flags. `Monitor::lock` protects most monitor state; `session_map_lock` protects session collections; `auth_lock` protects auth server/client state.

Persistent state lives in `MonitorDBStore`. `MONITOR_NAME` keys include `cluster_uuid`, `feature_set`, `joined`, and `cluster_fingerprint`. `MONITOR_STORE_PREFIX` stores `last_metadata`. The `mkfs` prefix stores seed monmap/osdmap/keyring. The `mon_sync` prefix stores `in_sync`, `force_sync`, `last_committed_floor`, `latest_monmap`, and `temp_newer_monmap` to survive restart or interrupted sync. Paxos and each Paxos service own additional prefixes returned by `get_sync_targets_names()`.

Feature persistence is conservative. `read_features_off_disk()` creates a legacy feature set when missing. Election finish can add required compat features derived from quorum connection features and monmap persistent features, then writes `feature_set` and recalculates `required_features`. Startup refuses unsupported on-disk features via `check_features()`.

Sync persistence is failure-conscious. Full sync first stashes the latest known monmap and a last-committed floor, marks `in_sync`, applies the transaction, then clears synchronizable prefixes. Completion reconstructs Paxos transactions for full sync, erases sync markers, reinitializes Paxos/services, and bootstraps. This ordering avoids silently booting from partially cleared state, but it also means interrupted sync paths must preserve the stash markers correctly.

## Dependencies and integration points

The file depends heavily on Ceph monitor internals: `Paxos`, `PaxosService`, `Elector`, `MonitorDBStore`, `MonMap`, `MonSession`, command parsing, message classes, `LogClient`, `MgrClient`, auth client/server APIs, CephX key server, `SafeTimer`, `Finisher`, `ThreadPool`, perf counters, admin socket, and config observers. It integrates with every monitor service through the `paxos_service` array and typed accessors.

External daemon integration happens through messenger sessions for clients, OSDs, MDSs, MGRs, NVMe-oF gateways, and peer monitors. Manager integration includes `MgrClient` command proxying, daemon metadata updates, daemon health metrics, and service/progress status reporting. Admin integration is via admin socket command registration and `do_admin_command()`. Storage integration uses `MonitorDBStore` transactions, synchronizers, compaction, flush, and raw device metadata for SMART and metadata reporting.

## Risks and edge cases

This file is a high-risk coordination point because election, Paxos, sync, auth, and command dispatch share the same monitor lock. Any blocking store, auth, messenger, or admin-socket call in the wrong lock order can create deadlock or latency spikes. The implementation explicitly unlocks around admin socket registration and store flush in some places, which are important patterns to preserve.

Sync has several crash windows and uses debug kill injection points. The ordering around `mon_sync/in_sync`, store clearing, `last_committed_floor`, and `sync_finish()` is critical. Regressions can lead to a monitor rejoining with stale committed state, clearing too much, or failing to preserve the newest monmap.

Command dispatch is broad and security-sensitive. It checks command existence, compatibility, obsolete/deprecated flags, forwarding policy, session capabilities, mgr proxy byte limits, and module-specific dispatch. A new command in `MonCommands.h` or a service command map can become unsafe if its module, permissions, or noforward/mgr flags do not match this dispatcher.

Forwarding and routed requests depend on session lifetimes and feature-specific reencoding. Losing a session must remove routed requests; elections must resend or self-retry them. `AnonConnection` intentionally aborts if code tries to reply directly rather than route through `send_reply()`, so forwarded command paths must use monitor reply helpers.

Stretch-mode session filtering can mark down OSD sessions whose CRUSH zone differs from the monitor's zone. It assumes monmap CRUSH locations and OSDMap CRUSH data are readable and consistent; missing locations are asserted. Changes here can disrupt client/OSD routing in stretched clusters. Timecheck and health logging have timing-dependent behavior and must be tested with delayed or repeated events.

## Test signals

Useful direct test signals include monitor integration tests for bootstrap/probe/election, singleton election, joining an existing quorum, monmap address changes, full and recent monitor store sync, `sync_force`, interrupted sync marker recovery, and `sync_last_committed_floor` protection.

Command tests should cover unknown commands, missing/empty prefixes, obsolete/deprecated handling, command-description output, leader/peon forwarding, noforward rejection, mgr proxy byte limiting, service dispatch routing, `mon scrub`, `quorum_status`, metadata/version commands, and permission denial audit paths.

Message dispatch tests should cover unauthenticated stray messages, auth handshakes, insecure global-id reclaim behavior, session trimming, waitlist-or-zap behavior while out of quorum or synchronizing, routed reply cleanup on session reset, and monitor-only message cap checks.

Persistence tests should inspect `feature_set`, `cluster_uuid`, `cluster_fingerprint`, `last_metadata`, `mkfs` seed keys, and `mon_sync` keys before and after mkfs, preinit, election finish, sync, and forced sync. Scrub tests can use missing-key and CRC mismatch injection; sync tests can use provider/requester kill injection and payload/key limits. Stretch-mode tests should cover monmap/OSDMap enable/disable, degraded/recovery/healthy transitions, tiebreaker exclusion, disallowed leaders, and OSD session rejection.
