# sources/distributed-fs/ceph/src/mon/MDSMonitor.h

## Purpose
`MDSMonitor.h` declares the CephFS monitor service that owns `FSMap` state and MDS daemon lifecycle coordination.

## Important APIs, Types, and Members
`MDSMonitor` derives from `PaxosService`, `PaxosFSMap`, and protected `CommandHandler`. Public methods expose Paxos lifecycle, dispatch, proposal policy, health-warning predicates, active/restart hooks, subscriptions, info dumping, `fail_mds_gid()`, and version summaries. Protected helpers cover beacons, commands, health, resizing, standby promotion, metadata, and quiesce leader assignment.

## Control Flow
Monitor dispatch calls `preprocess_query()` and `prepare_update()` for beacons, commands, and offload targets. `tick()` drives leader automation. FS command handlers are loaded in the constructor.

## State and Persistence
The header exposes staged health and metadata maps that implementation writes into monitor transactions, plus runtime beacon/tick tracking and struct flush controls.

## Dependencies and Integration Points
It depends on monitor core types, `PaxosFSMap`, `MDSMap`, `MMDSBeacon`, command parsing, Ceph clocks, and `FileSystemCommandHandler`. `has_health_warnings()` is consumed by FS commands.

## Risks
The interface combines service, FSMap, and command responsibilities, so caller context must respect leader, writeability, and capability assumptions.

## Test Signals
Verify override wiring, handler loading, health-warning predicates, subscription entry points, restart state clearing, and `fail_mds_gid()` interactions with blocklisting.
