# sources/control-plane/ceph-csi/internal/journal/volumegroupjournal.go

## Purpose
`volumegroupjournal.go` extends the journal pattern to CSI volume groups and volume group snapshots. It maps request names to generated group UUIDs/names and stores member volume mappings plus creation time in RADOS OMAPs.

## Important APIs, Types, And Functions
`VolumeGroupJournal` is the public interface for group journal operations. `VolumeGroupJournalConfig` embeds `Config` and adds a creation-time key. `volumeGroupJournalConnection` binds config to a `Connection`. Constructors include `NewCSIVolumeGroupJournal` and namespace-aware variants. Key methods are `Connect`, `Destroy`, `CheckReservation`, `UndoReservation`, `ReserveName`, `GetVolumeGroupAttributes`, `AddVolumesMapping`, `RemoveVolumesMapping`, `MakeVolumeGroupID`, and `generateVolumeGroupName`.

## Control Flow And State
`ReserveName()` reserves a UUID OMAP, creates the request-name mapping, writes request name, generated group name, and creation time into the UUID object, and defers cleanup on failure. `CheckReservation()` looks up a request-name mapping, fetches UUID attributes, validates the back-pointer request name, and returns `VolumeGroupData`. `UndoReservation()` removes the per-UUID object and then removes the request-name key. Mapping methods add or remove volume IDs from the group UUID OMAP.

## State And Persistence Behavior
Group state is persisted in RADOS OMAPs named with `csi.groups.<suffix>` and per-group UUID OMAPs. Per-group attributes include request name, group name, creation time, and remaining key/value pairs treated as volume-to-value mappings. `CreationTime` is marshaled as text and optional on read.

## Dependencies And Integration Points
This file reuses `Config`, `Connection`, `reserveOMapName`, OMAP helpers, UUID parsing, `util.CSIIdentifier`, and Ceph-CSI logging. It integrates with group snapshot/volume group workflows that need idempotent request-name reservation.

## Risks And Edge Cases
As with volume reservations, callers must externally serialize by request name. If a crash occurs after UUID reservation but before directory mapping, a UUID object can be leaked. `GetVolumeGroupAttributes()` tolerates missing pool/object by logging and then reading from an empty values map, which can return empty attributes instead of a hard failure. Member mappings share the same OMAP namespace as metadata keys, so key naming collisions need discipline.

## Test Signals
No tests for this file are in the subset. Useful tests would cover group ID composition, stale reservation cleanup, creation time parse failures, member add/remove behavior, missing object behavior, namespace propagation, and concurrent reservation protection through caller locks.
