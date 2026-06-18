# sources/distributed-fs/ceph/src/mon/MgrMonitor.h

## Purpose

`MgrMonitor.h` declares the monitor service responsible for manager-map authority. It combines `PaxosService` persistence with `CommandHandler` command routing and exposes query/update hooks used by the monitor dispatcher.

## Important APIs, Types, and Functions

The class owns live `map`, `pending_map`, `ever_had_active_mgr`, pending metadata put/remove sets, module option cache, digest timer state, previous health checks, learned command descriptions, and beacon timeout tracking. Public service methods include initialization/shutdown, Paxos lifecycle (`create_initial`, `update_from_paxos`, `create_pending`, `encode_pending`, `get_trim_to`), query/update dispatch, beacon preprocessing/preparation, subscription handling, digest sending, active/restart hooks, ticking, summaries, metadata dumping/counting, version grouping, and `get_command_descs()`.

## Control Flow and State

Private helpers form the failover control surface: `promote_standby()`, `drop_active()`, and `drop_standby()`. `check_caps()` centralizes mgr beacon capability and fsid validation. `should_warn_about_mgr_down()` gates health severity based on OSD presence and grace periods. `last_tick` and `last_beacon` prevent false failovers after slow monitor election or delayed local ticks.

## Dependencies and Integration Points

The header ties together `MgrMap`, `PaxosService`, `MonCommand`, `CommandHandler`, `Context`, monitor subscriptions, and Ceph health maps. It is consumed by `Monitor`, `MgrStatMonitor` for active gid checks, config handling for module options, and command help paths that need manager-provided command descriptions.

## Risks and Test Signals

The main risk is that state declared here has mixed lifetimes: Paxos-persisted map fields, pending transaction fields, leader-local beacon timers, and transient digest state. Tests should distinguish restart behavior from persisted map behavior, verify pending metadata sets are cleared only after encoding, and ensure `last_beacon` reset behavior prevents false lag detection after elections.
