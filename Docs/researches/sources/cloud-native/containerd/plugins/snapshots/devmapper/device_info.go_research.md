# sources/cloud-native/containerd/plugins/snapshots/devmapper/device_info.go

## Purpose
This file defines devmapper thin-device state and metadata records.

## Important APIs, Types, And Functions
`maxDeviceID` defines the 24-bit device ID limit. `DeviceState` enumerates lifecycle states from `Unknown` through create/activate/suspend/resume/deactivate/remove states plus `Faulty`. `DeviceState.String` renders names. `DeviceInfo` stores device ID, size, name, parent name, state, and error text.

## Control Flow
Only `String` has control flow, mapping known states to labels and unknown values to `unknown <n>`.

## State And Persistence
`DeviceInfo` is JSON-marshaled into the devmapper pool metadata Bolt database. State transitions mirror dmsetup operations and recovery status.

## Dependencies And Integration Points
It is used by `metadata.go`, `pool_device.go`, and devmapper tests.

## Risks
State names are part of diagnostics and persisted JSON values. Adding states requires recovery logic in `ensureDeviceStates`.

## Test Signals
Metadata and pool-device tests exercise several states, especially `Faulty`, `Activated`, `Removed`, and ID reuse.
