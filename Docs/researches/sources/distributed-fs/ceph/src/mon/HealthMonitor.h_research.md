# sources/distributed-fs/ceph/src/mon/HealthMonitor.h

## Purpose
`HealthMonitor.h` declares the monitor service responsible for durable cluster-health aggregation and health command handling.

## Important APIs, Types, and Members
The class derives from `PaxosService` and stores `version`, per-quorum health maps, leader checks, committed/pending mutes, and pending/current netsplit maps. Public APIs cover Paxos lifecycle, command/message dispatch, ticking, trimming, `gather_all_health_checks()`, and `get_health_status()`.

## Control Flow
Monitor dispatch routes commands and `MMonHealthChecks` through preprocess/prepare methods. Periodic `tick()` refreshes local and leader checks, then proposes when state changes.

## State and Persistence
The interface separates committed `mutes` from `pending_mutes`; implementation persists checks and mutes but keeps netsplit grace tracking in memory.

## Dependencies and Integration Points
It depends on `PaxosService`, health types, formatter support, monitor ops, and coarse monotonic clocks. Private check declarations connect to monmap, OSDMap, CRUSH, config, session, and election state.

## Risks
Runtime-only netsplit state means restart can reset grace timers. `get_health_status()` is an aggregate across all Paxos services, not only this service's own checks.

## Test Signals
Validate lifecycle overrides, public health rendering, mute state transitions, and that declared check categories remain covered by implementation tests.
