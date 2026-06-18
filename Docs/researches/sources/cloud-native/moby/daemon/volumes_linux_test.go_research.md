# sources/cloud-native/moby/daemon/volumes_linux_test.go

## Purpose
Unit coverage for Linux daemon-root bind propagation validation.

## Important APIs and Types
Contains `TestBindDaemonRoot`, with table cases for nil, empty, private, rprivate, slave, rslave, shared, and an intended rshared case.

## Control Flow, State, and Persistence
The test builds a daemon rooted at `/a/b/c/daemon` and runs each propagation option against sources equal to the root, below it, above it, and `/`. It asserts whether an error is returned and whether the caller must apply propagation automatically.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `filepath` and `api/types/mount`. It directly guards the behavior consumed by `registerMountPoints`. A subtle test risk is that the "rshared propagation" row currently uses `PropagationRSlave`, so it does not independently verify explicit `rshared`. The suite still signals that unsafe propagation modes for daemon-root-related binds are rejected.
