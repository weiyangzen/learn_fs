# sources/cloud-native/containerd/plugins/snapshots/devmapper/plugin/plugin.go

## Purpose
This file registers the devmapper snapshotter plugin.

## Important APIs, Types, And Functions
The snapshot plugin ID is `devmapper` and config type is `*devmapper.Config`. Initialization sets default platform metadata, validates config type, skips when `PoolName` is empty, defaults `RootPath`, exports `plugins.SnapshotterRootDir`, and calls `devmapper.NewSnapshotter`.

## Control Flow
The plugin does minimal config normalization before delegating validation and pool setup to the snapshotter.

## State And Persistence
Persistent state is created under `RootPath` and in the configured thin pool by the snapshotter.

## Dependencies And Integration Points
It integrates containerd plugin registration, platform metadata, and the devmapper snapshotter package.

## Risks
An empty pool name causes a skip, so devmapper must be explicitly configured. Config type mismatch fails initialization. Root path defaults to plugin property if absent.

## Test Signals
No direct plugin tests are included. Devmapper snapshotter tests validate the underlying implementation.
