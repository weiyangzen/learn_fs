# sources/cloud-native/containerd/plugins/snapshots/devmapper/pool_device.go

## Purpose
`pool_device.go` coordinates devmapper thin-pool operations with persistent pool metadata and recovery state transitions.

## Important APIs, Types, And Functions
`PoolDevice` stores pool name, `PoolMetadata`, and discard policy. Major APIs are `NewPoolDevice`, `CreateThinDevice`, `CreateSnapshotDevice`, `SuspendDevice`, `ResumeDevice`, `DeactivateDevice`, `IsActivated`, `IsLoaded`, `GetUsage`, `RemoveDevice`, `RemovePool`, `MarkDeviceState`, `WalkDevices`, and `Close`. Internal helpers include `ensureDeviceStates`, `transition`, `rollbackActivate`, `createDevice`, `activateDevice`, `createSnapshot`, `deleteDevice`, and retry helpers.

## Control Flow
Initialization checks dmsetup, optional blkdiscard, opens metadata, verifies pool presence, and reconciles persisted device states. Creation saves metadata, sends dmsetup create/snapshot messages, activates devices, and rolls back or marks faulty on failures. Snapshot creation suspends active parent devices before taking internal snapshots and resumes afterward. Deactivation can discard blocks and remove devices with retry/deferred/force options.

## State And Persistence
Device lifecycle state persists in the pool metadata DB. Kernel device-mapper state is mutated through dmsetup. Faulty states preserve device IDs for manual repair. Removed devices may remain until cleanup when deferred or async behavior is used.

## Dependencies And Integration Points
It depends on `dmsetup`, `blkdiscard`, Bolt-backed pool metadata, logging, `unix` errno, and snapshotter cleanup policy.

## Risks
Recovery is complex: incomplete states after crashes are marked faulty except selected safe states. Suspend/resume retries use string matching on error text. Device removal with discard must avoid busy devices. Rollback failures can leave faulty devices requiring manual intervention.

## Test Signals
`pool_device_test.go` covers real thin device creation, filesystem formatting, snapshot isolation, deactivation/removal, rollback activation, and faulty-state marking.
