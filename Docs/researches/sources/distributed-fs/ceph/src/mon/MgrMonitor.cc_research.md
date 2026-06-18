# sources/distributed-fs/ceph/src/mon/MgrMonitor.cc

## Purpose

`MgrMonitor.cc` implements the monitor Paxos service that owns `MgrMap`. It elects and fails over active manager daemons from beacons, persists manager metadata and command descriptions, serves mgr-map subscriptions and CLI queries, updates health when no active mgr exists, manages always-on module policy, and blocklists old active mgr instances and their RADOS clients during failover.

## Important APIs, Types, and Functions

Important functions include `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, `preprocess_query()`, `prepare_update()`, `preprocess_beacon()`, `prepare_beacon()`, `tick()`, `promote_standby()`, `drop_active()`, `drop_standby()`, `preprocess_command()`, `prepare_command()`, metadata helpers, subscription helpers, and digest helpers. The static `always_on_modules()` table defines release-keyed built-in mgr modules. `find_module_option()` normalizes `mgr/$module/$instance/$option` names to global module options for `ConfigMonitor`.

## Control Flow and State

Beacons are accepted only from sessions with `mgr` execute caps and matching fsid. `prepare_beacon()` handles daemon restarts, standby registration, active selection, active service/address/availability/module/client updates, command description capture on first available active beacon, and stale active self-reset through a null mgr map. `tick()` runs only on the leader and drops laggy standbys, drops laggy active daemons when OSDMonitor is writable, promotes standbys unless `FLAG_DOWN` is set, triggers delayed health warnings, and removes obsolete `orchestrator_cli`.

Paxos state is `pending_map` encoded as the next mgr map epoch plus metadata updates under `mgr_metadata`, health checks, and active mgr command descriptions under `mgr_command_descs`. Dropping the active plugs Paxos, blocklists active addresses and mgr-owned RADOS clients through `OSDMonitor`, records `last_failure_osd_epoch`, clears active state, forces an immediate proposal, and cancels digest timers.

CLI preprocessing serves read-only commands: `mgr stat`, `mgr dump`, `mgr module ls`, `mgr services`, `mgr metadata`, `mgr versions`, and `mgr count-metadata`. Update preparation implements `mgr set down`, `mgr fail`, `mgr module enable`, `mgr module disable`, and `mgr module force disable`, with wait-for-commit replies on successful proposals.

## Dependencies and Integration Points

This service integrates with `PaxosService`, `CommandHandler`, `OSDMonitor`, `ConfigMonitor`, `HealthMonitor`, monitor sessions and subscriptions, `MMgrBeacon`, `MMgrMap`, `MMgrDigest`, `MMonCommand`, mgr static commands, and the monitor store. Manager module option data is converted into `Option` objects and forces config reload. Digest subscribers receive health JSON and monitor status JSON periodically.

## Risks and Test Signals

Risks include failover races around daemon restart and old active blocklisting, incorrect Paxos plug/unplug ordering, stale command descriptions after active change, map updates while OSDMonitor is not writable, and module enablement decisions during rolling upgrades. `mgr module force disable` intentionally permits disabling always-on modules only after explicit confirmation. Tests should cover beacon promotion, active restart, standby restart, laggy active failover, `mgr set down`, blocklist epoch recording, metadata persistence/removal, command description persistence, module command errors, subscription delivery, digest timer cancellation, and health warning grace periods.
