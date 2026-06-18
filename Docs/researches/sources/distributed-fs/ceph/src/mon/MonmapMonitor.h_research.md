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
