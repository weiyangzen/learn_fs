# sources/distributed-fs/ceph/src/mon/NVMeofGwSerialize.h

## Purpose
`NVMeofGwSerialize.h` provides inline stream operators and encode/decode functions for NVMe-oF gateway monitor types. It defines the wire/persistent layout used by `NVMeofGwMap`, gateway client maps, beacon subsystem data, timer state, per-group epochs, disaster additions, and human-readable debug output.

## Important APIs, Types, and Functions
The header defines `MAX_SUPPORTED_ANA_GROUPS` as 16 for legacy fixed-width layouts. Stream operators cover gateway export state, internal state-machine state, availability, admin state, `SmState`, beacon namespace/listener/subsystem, `NqnState`, `NvmeGwClientState`, group keys, gateway maps, nonce maps, internal gateway state, location states, and whole `NVMeofGwMap`.

Serialization functions cover `ana_state_t`, `GwSubsystems`, `NvmeGwClientState`, `NvmeGwTimerState`, `NvmeAnaNonceMap`, `NvmeGwMonStates`, `gw_epoch`, `LocationState`, `created_gws`, beacon-diff additions, client gateway maps, timer maps, `BeaconNamespace`, `BeaconListener`, `BeaconSubsystem`, and beacon change descriptors.

## Control Flow
Encoding is feature-aware. `GwSubsystems` encodes version 1 with exactly 16 ANA entries unless `NVMEOFHA` is present, where version 2 uses variable-sized ANA state. `NvmeGwTimerState` similarly uses a fixed 16-entry legacy layout or keyed variable entries with end-time milliseconds. `NvmeGwMonStates` uses version 1 fixed state/blocklist arrays, version 2 keyed HA state, and version 3 adds `addr_vect` and `beacon_index` under `NVMEOFHAMAP`.

`NVMeofGwMap::encode()` calls these helpers in a fixed order, then `decode()` mirrors that order by struct version. Beacon-diff additions are encoded after base `created_gws`; they iterate the already decoded gateway order to append admin state, location, and subsystem change descriptors. Legacy version-1 decode collects created ANA groups and erases unused fixed-array entries after all gateways are known.

## State and Persistence Behavior
This header defines what is durable. State encoded here survives Paxos replication and monitor restart; fields omitted here must be restored or treated as runtime-only. Timer end-times are serialized as milliseconds since the system-clock epoch. Gateway address vectors are encoded only in `NvmeGwMonStates` version 3. Beacon sequence values for client state are encoded in `NvmeGwClientState` version 2, while internal gateway map sequence persistence is partly managed outside these helpers.

Change descriptors are not encoded inside `BeaconSubsystem` itself; they are stored by the separate beacon-diff additions pass for gateway map persistence. That means the decode order must match the exact nested order of decoded `created_gws`.

## Dependencies and Integration Points
The header depends on `NVMeofGwTypes.h`, Ceph encoding macros, feature bits `NVMEOFHA` and `NVMEOFHAMAP`, `entity_addrvec_t` encoding, monitor logging, and `MAX_SUPPORTED_ANA_GROUPS` consumers in `NVMeofGwMap.cc`. It is included at the end of `NVMeofGwMap.h`, making the overloads available to map and message encoding.

## Risks
Most stream operators and some encode helpers take values by copy, which is fine for debug but expensive for large gateway maps. Feature-gated layouts must remain backward-compatible; adding fields without version increments or matching decode guards would corrupt Paxos state or gateway messages. `decode_gws_beacon_diff_additions()` assumes the base created-gateway structure has already been decoded and iterates in identical map order. Legacy fixed-array handling depends on `MAX_SUPPORTED_ANA_GROUPS` staying consistent with older clients.

Timer persistence uses wall-clock `system_clock`; clock jumps can affect timeout behavior after decode. Debug output may include sensitive listener/nonce-like values in logs.

## Test Signals
Serialization tests should round-trip each type under no HA, `NVMEOFHA`, and `NVMEOFHAMAP` feature sets; verify legacy fixed 16-entry maps shrink to created ANA ids on decode; verify beacon-diff additions preserve admin state, location, and descriptors; test timer end-time persistence; and check client map encode/decode for version-1 and version-2 fields.
