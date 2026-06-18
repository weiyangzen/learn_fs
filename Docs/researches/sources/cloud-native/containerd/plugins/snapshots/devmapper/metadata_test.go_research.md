# sources/cloud-native/containerd/plugins/snapshots/devmapper/metadata_test.go

## Purpose
This file unit-tests the devmapper pool metadata store.

## Important APIs, Types, And Functions
Tests cover `AddDevice`, rollback on invalid metadata, duplicates, device ID reuse, removal, update callbacks, `MarkFaulty`, `WalkDevices`, and `GetDeviceNames`. Helpers create and close a temp Bolt store.

## Control Flow
Each test creates an isolated metadata DB, performs metadata operations, and checks persisted `DeviceInfo` values or expected errors.

## State And Persistence
Temporary Bolt databases are created under test temp dirs and closed after use.

## Dependencies And Integration Points
Tests use Bolt directly for checking faulty ID state and `testify/assert`.

## Risks
Walk order follows Bolt key order and tests assert specific order for simple names. The tests do not simulate max device ID exhaustion or JSON corruption.

## Test Signals
They provide solid coverage for local persistence invariants and state/ID bookkeeping.
