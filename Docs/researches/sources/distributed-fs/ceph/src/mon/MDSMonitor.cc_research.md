# sources/distributed-fs/ceph/src/mon/MDSMonitor.cc

## Purpose
`MDSMonitor.cc` owns CephFS `FSMap` and MDS daemon lifecycle coordination. It persists FSMap epochs, processes beacons and offload targets, dispatches commands, stores daemon metadata/health, handles laggy/failure cases, promotes standbys, resizes ranks, and serves map subscriptions.

## Important APIs, Types, and Functions
Major methods include `update_from_paxos`, `create_pending`, `encode_pending`, beacon preprocess/prepare, command dispatch, `filesystem_command`, `fail_mds_gid`, `check_health`, `maybe_resize_cluster`, `maybe_promote_standby`, `drop_mds`, `check_sub`, metadata helpers, and `tick`.

## Control Flow
Paxos updates decode the committed FSMap and notify subscribers. Beacon preprocessing validates caps, fsid, address, leadership, epoch freshness, seq, join target, laggy state, and health deltas. Preparation mutates pending FSMap, validates transitions, handles boot/stopped/damaged/DNE states, coordinates OSD blocklisting, and replies after finished proposals. Leader ticks prune history, compute health, detect timeouts, resize, replace, and promote.

## State and Persistence
Durable state is encoded FSMap versions plus MDS health under `mds_health` and metadata under `mds_metadata/last_metadata`. Runtime leader state includes `last_beacon`, `last_tick`, struct-flush timing, and loaded handlers.

## Dependencies and Integration Points
It integrates with `PaxosService`, `PaxosFSMap`, `Monitor`, `OSDMonitor`, `FSCommands`, `MDSMap`, `FSMap`, MDS/FSMap messages, session caps, subscriptions, config, and cluster log.

## Risks
Failure handling and blocklisting require careful OSDMap coordination. Beacon correctness depends on effective epochs and legal transitions. Capability filtering protects per-FS visibility and mutation. Tick automation changes rank assignments without direct commands.

## Test Signals
Cover beacon boot/update/failure paths, stale seq/epoch, damaged and stopped handling, unique-name enforcement, command caps, FS command delegation, metadata/health persistence, subscriptions, timeout grace, resize, standby promotion, and OSD proposal batching.
