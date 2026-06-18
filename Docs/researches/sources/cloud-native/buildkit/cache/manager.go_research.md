# sources/cloud-native/buildkit/cache/manager.go

## Purpose

`manager.go` defines the top-level BuildKit cache manager. It owns the in-memory cache record map, wires snapshotter/content/lease/metadata dependencies, creates mutable and immutable refs, rehydrates persisted refs on startup, resolves refs by content blob or chain IDs, exposes disk usage, and prunes unused cache records. This file is the central coordinator between `refs.go` lifecycle mechanics and `metadata.go` persistence.

## Important APIs, Types, and Functions

- `ManagerOpt` injects the snapshotter, content store, lease manager, GC callback, applier/differ, metadata store, cache root, mount pool root, and optional external prune checker.
- `Accessor`, `Controller`, and `Manager` define the public cache surface used by workers and solver code: `GetByBlob`, `Get`, `New`, `GetMutable`, `Merge`, `Diff`, `DiskUsage`, `Prune`, and `Close`.
- `cacheManager` stores `records`, `mu`, `muPrune`, containerd/BuildKit backends, mount pool, and a `flightcontrol.Group` used to deduplicate unlazy operations.
- `NewManager` wraps the configured snapshotter in a merge snapshotter, loads metadata via `init`, initializes the sharable mount pool, and returns a `Manager`.
- `GetByBlob` resolves or creates lazy/blob-backed immutable refs from an OCI descriptor and optional parent.
- `Get`, `get`, and `getRecord` load immutable refs by ID, validate lazy provider availability, handle equal mutable/immutable pairs, and recover or clean invalid metadata.
- `New` creates a new mutable snapshot ref, optionally based on a finalized/extracted immutable parent.
- `GetMutable` reopens an unlocked mutable ref, deleting stale equal immutable records if needed.
- `Merge`/`createMergeRef` and `Diff`/`createDiffRef` create synthetic immutable refs for merged filesystem views or differences.
- `Prune`, `prune`, `pruneOnce`, `DiskUsage`, `calculateKeepBytes`, and `sortDeleteRecords` implement usage reporting and garbage collection policy.

## Control Flow

Startup calls `MetadataStore.All()` and attempts `getRecord` for every persisted item. Records whose metadata cannot be reconciled with snapshotter state are cleared and their leases removed. Normal access flows through `cm.mu`, then per-record `cr.mu`, so callers either get an active ref, a lock error, a not-found error, or a lazy-provider error.

`GetByBlob` first computes `diffID`, `chainID`, and a separate `blobChainID` that distinguishes differently compressed blobs with the same uncompressed diff ID. It validates content availability unless descriptor handlers are provided. With a parent, it finalizes the parent and composes parent chain IDs. It prefers an exact `blobChainID` match, then a chain-ID match that may share an existing snapshot, otherwise it creates a new lease, records metadata, and returns a blob-only immutable ref.

`New` finalizes and extracts the parent before preparing a mutable snapshot. It creates a lease first, adds the snapshot resource, prepares the snapshotter key, initializes metadata, and stores a mutable `cacheRecord`. Special snapshotter handling adds stargz temporary labels and overlaybd read/write labels.

`Merge` flattens nested merge refs, clones parents, finalizes inputs, persists merge-parent metadata, and creates a committed immutable record whose actual snapshot is materialized later by `refs.go` mount/extract paths. `Diff` has an optimization where a lower ref that is an ancestor of upper becomes a merge of intervening single-layer diffs, maximizing layer reuse; otherwise it persists a diff ref directly.

`Prune` serializes all prune calls with `muPrune`, computes keep-byte thresholds, repeatedly calls `pruneOnce`, then optionally runs containerd GC. `pruneOnce` scans unlocked, unreferenced records, applies type/shared/filter/age rules, marks selected metadata as deleted while locked, releases locks before slow size computation and removal, emits `UsageInfo`, and deletes leases/metadata/snapshots through `cacheRecord.remove`.

`DiskUsage` snapshots record state, propagates in-use counts through parents, marks externally shared records, filters by age and filter expressions, and computes unknown sizes concurrently by temporarily acquiring refs.

## State and Persistence Behavior

Persistent state is held in the cache metadata store plus containerd leases and snapshotter/content state. Each cache record stores parent relationships, committed/deleted flags, snapshot ID, blob/diff/chain/blobchain data, image refs, usage count, last used timestamp, record type, cache policy, and size. Leases protect snapshots and content from containerd GC. Deletion is two-phase: records are marked deleted in metadata before removing backing state so restart can finish cleanup. Equal mutable/immutable metadata supports lazy commit recovery and is repaired if the mutable side is missing but the immutable snapshot exists.

## Dependencies and Integration Points

The manager integrates with containerd content, diff, leases, snapshots, filter, and GC APIs; BuildKit metadata, session, snapshot, disk, progress, flightcontrol, and logging utilities; OCI digest/image spec identities; and snapshotter-specific stargz/overlaybd behavior. `client.PruneInfo`, `client.DiskUsageInfo`, and `client.UsageInfo` form the user-facing API surface for cache usage and pruning.

## Risks and Edge Cases

- Lock ordering is critical: manager lock plus record locks protect the records map and ref counts, while pruning deliberately releases locks before expensive operations.
- Lazy refs require descriptor handlers. Missing handlers produce `NeedsRemoteProviderError`; incorrect blobchain metadata can cause reuse misses or logged errors.
- Chain ID and blobchain ID semantics are subtle. Chain ID allows snapshot reuse for same uncompressed content, while blobchain ID prevents conflating different compressed blob histories.
- Crash windows around mutable commit/finalize are mitigated but complex, especially equal mutable metadata and lease creation.
- Prune must avoid deleting internal/frontend/shared records unless `All` or filters allow it, and it batches deletes to avoid holding the manager lock too long.
- Disk usage for mutable in-use refs is reported as `0` because size is changing.

## Test Signals

`manager_test.go` heavily exercises this file: basic create/get/commit/release/prune, lazy `GetByBlob`, blobchain merge reuse, lazy extraction, reopen-after-commit behavior, restart recovery, pruning thresholds, merge/diff ops, broken-parent cleanup, readonly mounts, compression variants, and non-distributable descriptor persistence. `TestCalculateKeepBytes` directly validates keep-byte policy.
