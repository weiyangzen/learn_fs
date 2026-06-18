# sources/cloud-native/containerd/plugins/snapshots/devmapper/metadata.go

## Purpose
`metadata.go` manages the devmapper pool metadata database, including thin device records and device ID allocation.

## Important APIs, Types, And Functions
`PoolMetadata` wraps a Bolt DB. Public methods include `NewPoolMetadata`, `AddDevice`, `ChangeDeviceState`, `MarkFaulty`, `UpdateDevice`, `GetDevice`, `RemoveDevice`, `WalkDevices`, `GetDeviceNames`, and `Close`. Helpers include `getNextDeviceID`, `markDeviceID`, `putObject`, and `getObject`.

## Control Flow
Initialization creates `devices` and `device_ids` buckets. `AddDevice` rejects non-faulty duplicate names, allocates the next free or new device ID, and stores JSON `DeviceInfo`. `UpdateDevice` loads a record, runs a callback, ensures name and device ID did not change, then stores it. `RemoveDevice` deletes the record and marks the ID free. `MarkFaulty` marks both the device record and ID as faulty.

## State And Persistence
State persists in Bolt buckets: `devices` maps device names to JSON `DeviceInfo`, while `device_ids` maps numeric ID keys to free/taken/faulty state bytes. Faulty IDs are intentionally not reused automatically.

## Dependencies And Integration Points
It integrates Bolt transactions, `errdefs` not-found/already-exists errors, and `DeviceInfo` state transitions used by `PoolDevice`.

## Risks
Device ID keys are string-sorted, which is acceptable for scanning free entries but not numeric ordering after multi-digit IDs. Faulty records allow same-name recreation only by overwriting a faulty device, preserving faulty ID tracking. Context parameters are currently unused by Bolt operations.

## Test Signals
`metadata_test.go` covers add, rollback, duplicate rejection, ID reuse, removal, update, faulty marking, walking, and name listing.
