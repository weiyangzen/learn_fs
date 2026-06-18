# sources/control-plane/ceph-csi/internal/rbd/errors/errors.go

## Purpose
Centralizes sentinel errors and an optional error-code interface for RBD package operations. These errors let controller, group, migration, mirror, and utility paths classify expected failure modes with `errors.Is`.

## Important APIs, Types, And Functions
Sentinels include image/snapshot not found, volume-name conflict, invalid volume ID, missing stash, flatten in progress, migration volume-ID field errors, last-sync info missing, failed precondition, unavailable, aborted, invalid argument, image in use, group not connected/found, and unknown mounter. `ErrGroupNotConnected` and `ErrGroupNotFound` wrap go-ceph/rados or librbd errors to preserve lower-level classification. `ErrorCode` defines `ErrorCode() int` for error types that can expose numeric codes.

## Control Flow
The file is declarative. Runtime behavior comes from callers matching these sentinels and translating them into gRPC codes or retry decisions.

## State And Persistence
No state is persisted. The sentinel values are process-global constants by convention.

## Dependencies And Integration Points
Imports standard errors/fmt plus go-ceph `rados` and `rbd` error values. `controllerserver.go`, `group/util.go`, `manager.go`, `migration.go`, `mirror.go`, and disk usage paths use these sentinels for idempotency, cleanup, and status mapping.

## Risks And Test Signals
Risk comes from changing or wrapping errors in a way that breaks `errors.Is` checks in controller cleanup and retry paths. This file has no direct tests, but many table tests and integration paths depend on stable sentinel identity.
