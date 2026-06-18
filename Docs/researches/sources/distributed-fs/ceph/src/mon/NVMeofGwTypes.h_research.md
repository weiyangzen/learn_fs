# sources/distributed-fs/ceph/src/mon/NVMeofGwTypes.h

## Purpose
`NVMeofGwTypes.h` defines the domain model for monitor-managed NVMe-oF gateways. It provides aliases, enums, and structs shared by the map, monitor service, messages, serialization helpers, and gateway client state conversion.

## Important APIs, Types, and Functions
Aliases define gateway ids, locations, group keys `(pool, group)`, subsystem NQNs, ANA group ids, nonce vectors, nonce maps, client maps, timer maps, monitor gateway maps, and disaster location maps. Enums describe internal ANA state (`gw_states_per_group_t`), exported ANA state (`gw_exported_states_per_group_t`), gateway availability, admin state, and beacon subsystem change descriptors.

Beacon structures include `BeaconNamespace` with ANA group id and nonce, `BeaconListener` with address family/address/service id, and `BeaconSubsystem` with NQN, listener list, namespace list, and change descriptor. Equality operators support comparing beacon content.

`NvmeGwMonState` is the internal per-gateway monitor state: native ANA group id, availability, last map epoch validity, startup flag, subsystems, nonce map, per-ANA state machine map, blocklist data, address vector, beacon sequence/index fields, admin state, location, and timing controls for failovers/failbacks. It provides helpers for unavailable state, beacon sequence reset, standby/active state assignment, and down timestamp updates.

`NqnState` converts internal state-machine data into exported ANA state vectors, marking active or wait-blocklist groups optimized and other groups inaccessible. `NvmeGwClientState` is sent to gateways and includes native group id, map epoch, exported subsystems, availability, last beacon sequence status, and map feature flags. `Tmdata`, `NvmeGwTimerState`, and `LocationState` model timers and disaster cleanup state.

## Control Flow
These types are passive data structures used by `NVMeofGwMap` and `NVMeofGwMon`. Beacons populate `BeaconSubsystems`; monitor logic mutates `NvmeGwMonState`; `to_gmap()` creates `NvmeGwClientState` and `NqnState` for outbound maps. State-machine enums govern failover and failback transitions.

## State and Persistence Behavior
Many fields in `NvmeGwMonState` are encoded by `NVMeofGwSerialize.h`, but comments identify some timing fields as non-persistent. `allow_failovers_ts`, `last_gw_down_ts`, `delay_failbacks_ts`, last map validity, and beacon sequence/index fields require explicit restoration across pending map reconstruction. `REDUNDANT_GW_ANA_GROUP_ID` (`0xFF`) marks a gateway without a normal owned ANA group.

## Dependencies and Integration Points
The header depends on Ceph basic types and `entity_addrvec_t`. It is included by `NVMeofGwMap.h`, serialization helpers, monitor service code, and messages. The beacon listener comment ties listener shape to SPDK JSON-RPC NVMf listener representation.

## Risks
Default constructors leave some fields in `NvmeGwMonState` dependent on in-class initializers and some constructor-specific initialization; code must avoid using uninitialized availability in paths that use the default constructor. `NqnState` fills fake inaccessible entries to preserve vector index equals ANA group id, so off-by-one handling between gateway ANA ids and namespace ANA ids is a recurring risk. Timing fields use `system_clock`, making them sensitive to wall-clock changes.

## Test Signals
Tests should cover enum-to-client mapping through `NqnState`, equality operators for beacon diffs, default and ANA-id gateway-state construction, standby/active helper effects on blocklist data, `set_unavailable_state()` preserving deleting state, exported ANA vector indexing, and client-state defaults.
