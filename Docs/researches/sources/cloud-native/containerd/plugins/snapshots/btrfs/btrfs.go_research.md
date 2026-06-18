# sources/cloud-native/containerd/plugins/snapshots/btrfs/btrfs.go

## Purpose
`btrfs.go` implements a Linux/cgo btrfs snapshotter using btrfs subvolumes and readonly snapshots.

## Important APIs, Types, And Functions
`NewSnapshotter` validates that root is on btrfs, creates `active`, `view`, and `snapshots` directories, and opens a `storage.MetaStore`. `snapshotter` implements `Stat`, `Update`, `Usage`, `Walk`, `Prepare`, `View`, `Commit`, `Mounts`, `Remove`, and `Close`. Helpers include `usage`, `makeSnapshot`, and `mounts`.

## Control Flow
Prepare/View create metadata and then create a btrfs subvolume or subvolume snapshot. Mounts use the root device plus a `subvolid=<id>` option from `btrfs.SubvolID`. Commit computes usage, commits metadata, creates a readonly snapshot under `snapshots`, and deletes the active subvolume. Remove creates a temporary `rm-<id>` snapshot, deletes the source, and restores from it if metadata transaction commit fails.

## State And Persistence
Metadata persists in `metadata.db`. Filesystem state persists as btrfs subvolumes under `active`, `view`, and `snapshots`. Usage for active snapshots is computed from filesystem disk usage or diff usage against the parent.

## Dependencies And Integration Points
It depends on `github.com/containerd/btrfs/v2`, containerd mount lookup, snapshot storage metadata, continuity filesystem usage helpers, and plugin skip errors.

## Risks
The root must be a mounted btrfs filesystem. Removal and commit use multiple filesystem operations around metadata transactions, so rollback paths are important but not perfect. Usage can be expensive for active snapshots. Build tags limit availability to Linux with cgo and without `no_btrfs`.

## Test Signals
`btrfs_test.go` runs the generic snapshotter suite on a loopback btrfs filesystem and includes a mount-specific content inheritance test.
