# sources/cloud-native/containerd/plugins/snapshots/devmapper/snapshotter.go

## Purpose
`snapshotter.go` implements the containerd snapshotter interface using Linux device-mapper thin devices.

## Important APIs, Types, And Functions
`Snapshotter` stores a `storage.MetaStore`, `PoolDevice`, config, cleanup functions, and `sync.Once`. It implements `NewSnapshotter`, `Stat`, `Update`, `Usage`, `Mounts`, `Prepare`, `View`, `Commit`, `Remove`, `Walk`, `ResetPool`, `Close`, `Cleanup`, and helpers `createSnapshot`, `removeDevice`, `mkfs`, `getDeviceName`, `getDevicePath`, and `buildMounts`.

## Control Flow
Creation parses and validates config, creates root and metadata store, and opens the pool device. Prepare/View create snapshot metadata, determine filesystem type from config or parent label, create a thin device or snapshot device, format base devices, remove `lost+found`, and return mount specs. Commit calculates device usage, commits metadata, suspends/resumes to flush IO, and deactivates the committed device. Remove deletes snapshot metadata and either removes the device immediately or marks it removed for async cleanup. Cleanup removes devices marked `Removed` when async remove is enabled.

## State And Persistence
Containerd snapshot metadata persists in `metadata.db`. Pool device metadata persists in `<pool>.db`. Thin devices persist in kernel thin-pool state until removed. Filesystem type is stored in snapshot labels under `containerd.io/snapshot/devmapper/fstype`.

## Dependencies And Integration Points
It integrates snapshot storage metadata, `PoolDevice`, dmsetup paths, filesystem mkfs tools, containerd mount helpers, errdefs, logging, and snapshot GC cleanup via `snapshots.Cleaner`.

## Risks
Metadata and kernel state must stay synchronized across failures. `mkfs` failures trigger rollback but depend on `RemoveDevice`. Async remove can leave devices until `Cleanup`. XFS requires `nouuid` mounts. Parent snapshots without fs type labels default to ext4 for compatibility.

## Test Signals
`snapshotter_test.go` runs the generic snapshotter suite, usage tests, mkfs command error tests, and an XFS multiple-mount scenario.
