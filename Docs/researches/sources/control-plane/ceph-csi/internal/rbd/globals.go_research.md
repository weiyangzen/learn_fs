# sources/control-plane/ceph-csi/internal/rbd/globals.go

## Purpose
Holds package-level RBD configuration and journal handles that are initialized by the driver and consumed across controller/node/helper code.

## Important APIs, Types, And Functions
Globals include `volJournal`, `snapJournal`, clone-depth limits, snapshot-count flatten thresholds, `skipForceFlatten`, and `krbdFeatures`. `SetGlobalInt` mutates known numeric settings, `SetGlobalBool` mutates known boolean settings, and `InitJournals` creates CSI volume and snapshot journal configs for the driver instance.

## Control Flow
Setters switch on string keys and panic for unknown variables, making startup misconfiguration fail fast. `InitJournals` builds journal configs but does not connect them until operation code calls `Connect`.

## State And Persistence
All state is process-global. The journal configs point to RADOS OMAP-backed persistent journal data, but this file only stores configuration objects and scalar runtime settings.

## Dependencies And Integration Points
Depends on `internal/journal`. `driver.go` sets these globals at startup; `controllerserver.go` and snapshot/volume helper paths use `volJournal` and `snapJournal`; clone/flatten behavior reads depth and snapshot thresholds.

## Risks And Test Signals
Global mutable state limits multi-cluster or per-StorageClass tuning and can make tests order-sensitive. Panic-on-unknown-key catches programmer errors but is not recoverable. There are no direct tests for this file.
