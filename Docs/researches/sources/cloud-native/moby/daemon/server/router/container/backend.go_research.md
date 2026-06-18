# sources/cloud-native/moby/daemon/server/router/container/backend.go

## Purpose
Defines the composite backend interface required by the container API router.

## Important APIs, Types, And Functions
Subinterfaces include `execBackend`, `copyBackend`, `stateBackend`, `monitorBackend`, `attachBackend`, `systemBackend`, `commitBackend`, and `sysInfoProvider`. `Backend` embeds all of them.

## Control Flow
Interface definitions only.

## State And Persistence
No state is changed. Methods represented here perform container lifecycle, exec, archive, logs, stats, prune, attach, commit, and sysinfo operations in implementations.

## Dependencies And Integration Points
Connects container router handlers to daemon implementations. Depends on Docker API container/network types, daemon container state types, backend option structs, filters, archive changes, and sysinfo.

## Risks And Edge Cases
The interface is broad; adding a route often expands this contract. Correct error classification and stream ownership are delegated to backend implementations.

## Test Signals
Compile-time implementation by daemon plus container router tests validate this contract.
