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
