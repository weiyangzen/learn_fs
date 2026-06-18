# sources/cloud-native/buildkit/cache/manager_test.go

## Purpose

`manager_test.go` is an integration-heavy test suite for BuildKit cache manager behavior. It creates real containerd metadata DBs, native snapshotters, content stores, lease managers, appliers, differs, and BuildKit metadata stores, then exercises cache refs across creation, mutation, lazy blob import, compression conversion, remote export preparation, merge/diff, prune, restart, and mount behavior.

## Important APIs, Types, and Functions

- `newCacheManager` builds an isolated test manager with containerd metadata DB, local content store, namespaced lease manager, native snapshotter by default, BuildKit metadata store, applier/differ, and mount pool.
- `cmOpt` and `cmOut` define test setup inputs and returned manager dependencies.
- Helper functions include `checkDiskUsage`, `checkNumBlobs`, `ensurePrune`, `pruneResultBuffer`, `mapToBlob`, `mapToBlobWithCompression`, `fileToBlob`, `mapToSystemTarBlob`, `checkInfo`, `checkDescriptor`, `checkVariantsCoverage`, `getCompressor`, `esgzBlobDigest`, `zstdBlobDigest`, and `isReadOnly`.
- Test cases cover the full lifecycle: `TestManager`, `TestLazyGetByBlob`, `TestMergeBlobchainID`, `TestSnapshotExtract`, `TestExtractOnMutable`, `TestSetBlob`, `TestPrune`, `TestLazyCommit`, `TestLoopLeaseContent`, `TestSharingCompressionVariant`, `TestConversion`, `TestGetRemotes`, `TestNondistributableBlobs`, `TestMergeOp`, `TestDiffOp`, `TestLoadHalfFinalizedRef`, `TestMountReadOnly`, `TestLoadBrokenParents`, and `TestCalculateKeepBytes`.

## Control Flow

Most tests create a namespaced context, temporary directories, native snapshotter, and a fresh manager. They then drive cache refs through public methods and inspect disk usage, snapshot directories, content-store blobs, metadata-derived IDs, or mount options. Lazy blob tests construct tar layer descriptors with `containerd.io/uncompressed` annotations and use `DescHandlers` backed by in-memory content buffers.

The compression tests generate all combinations of gzip, zstd, eStargz, and uncompressed blobs, then call `GetRemotes` with forced compression to ensure conversion and variant linking. The merge and diff tests build multiple refs, release parents, prune aggressively, and verify synthetic refs retain their parents until released. Restart tests close and reopen the manager over the same metadata/snapshotter state to validate recovery paths.

## State and Persistence Behavior

The tests validate that refs are tracked as in-use while handles are held and unused after release, that `CachePolicyRetain` prevents immediate mutable deletion, and that prune removes snapshots/content only when no active parent or derived ref depends on them. `TestLazyCommit` and `TestLoadHalfFinalizedRef` verify equal mutable/immutable state survives restarts and that half-finalized metadata can be recovered. `TestLoadBrokenParents` verifies a deleted parent does not leak references when a merge parent fails to load.

## Dependencies and Integration Points

The suite depends on containerd content, diff, metadata, lease, native snapshotter, archive/compression, local content store, BuildKit snapshot wrappers, winlayers, compression/converter utilities, solver remote descriptors, OCI descriptors, and filesystem mount helpers. Several tests are OS-gated because mount, overlay, merge, or lazy extraction behavior is unavailable or different on Windows/FreeBSD.

## Risks and Edge Cases

- Tests use real snapshotter and content-store state, so failures can indicate integration regressions rather than simple unit bugs.
- Parallel compression tests intentionally stress variant sharing and concurrency.
- Some helper-generated tar blobs use Go tar writer and system `tar` to catch format-specific conversion bugs.
- `TestLoopLeaseContent` creates a compression-variant graph loop and verifies variant walking/prune does not hang or leak.
- `TestNondistributableBlobs` checks URL/media-type preservation only when requested, protecting distribution semantics.

## Test Signals

This file itself is the primary test signal for `manager.go`, `refs.go`, `remote.go`, `metadata.go`, and compression helpers. It covers normal and crash-recovery flows, lazy and materialized refs, remote descriptor generation, content lease cleanup, pruning, mount read-only behavior, and disk usage accounting.
