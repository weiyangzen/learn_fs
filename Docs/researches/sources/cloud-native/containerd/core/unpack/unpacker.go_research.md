# sources/cloud-native/containerd/core/unpack/unpacker.go

## Purpose
This file implements asynchronous image layer unpacking integrated into image descriptor walking.

## Important APIs, Types, and Functions
`Platform` describes platform matcher, snapshotter, applier, snapshot options, capabilities, config type, and layer types. `Unpacker` wraps an image handler with `Unpack` and is finalized with `Wait`. Options set platforms, fetch limiter, duplication suppressor, and unpack limiter. Internal helpers lock descriptors/chain IDs, fetch layers, apply diffs, and convert bind mounts to overlay mounts for parallel overlayfs.

## Control Flow
`Unpack` intercepts manifests, separates layers from configs, and starts `unpack` when a matching config is handled. `unpack` reads config, validates diff IDs, chooses a platform, precomputes chain IDs, prepares snapshots, starts or coordinates layer fetch, applies layer diffs, verifies diff IDs, commits snapshots, records uncompressed labels, and updates config GC refs. Sequential mode commits layer-by-layer; parallel mode applies layers concurrently but commits/rebases in order.

## State and Persistence
Persistent effects include prepared/committed snapshots with labels for snapshot ref, parent chain ID, diff ID, and inherited labels; content labels for uncompressed diff IDs; and config labels referencing the final snapshot. Temporary snapshots are removed on abort.

## Dependencies and Integration Points
Integrates content store, diff appliers, image handlers, snapshotters, mount types, identity chain IDs, cleanup helpers, keyed mutexes, tracing, and transfer local pull/import.

## Risks
Correctness depends on descriptor graph order, config/layer count matching, snapshot cleanup on every error path, lock release, and ordered commits under parallel unpack. Parallel rebase is enabled only with an unpack limiter and snapshotter `rebase` capability. Overlayfs bind-to-overlay conversion is a temporary workaround.

## Test Signals
`unpacker_test.go` benchmarks chain ID calculation and tests bind-to-overlay conversion. Integration tests cover pull with unpack, discard content after unpack, and concurrent unpack limiter behavior.
