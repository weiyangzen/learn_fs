# sources/cloud-native/nydus/smoke/tests/tool/snapshotter.go

## Purpose
This helper provides a small HTTP-over-Unix-socket client for the nydus-snapshotter system controller API used by takeover tests.

## Important APIs, Types, And Functions
`SnapshotterClient` wraps `http.Client`. `DaemonInfoFromSnapshotter` models daemon details including ID, PID, API socket, supervisor path, references, mountpoints, resource metrics, and RAFS instances. `UpgradeRequest` models upgrade API input. `NewSnapshotterClient` creates a Unix-socket transport. `request` marshals an optional JSON body, sends a request, reads the response, and enforces 2xx status. `GetNydusDaemonInfos` calls `GET /api/v1/daemons`. `Upgrade` calls `PUT /api/v1/daemons/upgrade`.

## Control Flow
Tests instantiate the client with the system socket path, call typed methods, and receive decoded daemon state or errors.

## State And Persistence
The client itself is stateless aside from connection pooling. It reads live snapshotter state and sends upgrade commands that mutate daemon fleet state.

## Dependencies And Integration Points
It integrates with nydus-snapshotter's controller API over a Unix socket and is used by `takeover_test.go`.

## Risks
The request helper typo in error text is harmless. The client has a fixed 30-second timeout. API schema changes will break JSON decoding or tests relying on fields such as PID.

## Test Signals
Successful daemon info fetch and upgrade request completion are prerequisite signals for snapshotter takeover/hot-upgrade tests.
