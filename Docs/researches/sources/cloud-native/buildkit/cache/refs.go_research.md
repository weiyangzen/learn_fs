# sources/cloud-native/buildkit/cache/refs.go

## Purpose

`refs.go` implements the concrete mutable and immutable cache refs returned by the manager. It owns reference counting, parent ownership, mount behavior, lazy materialization, blob metadata and compression variant linking, layer-chain traversal, mutable commit/finalize semantics, size accounting, read-only mount wrapping, and sharable overlay mount pooling.

## Important APIs, Types, and Functions

- Public interfaces: `Ref`, `ImmutableRef`, `MutableRef`, `Mountable`, and `RefList`.
- Core state: `cacheRecord`, `immutableRef`, `mutableRef`, `parentRefs`, and `diffParents`.
- Ref creation helpers: `cacheRecord.ref`, `cacheRecord.mref`, `immutableRef.clone`, `LayerChain`, `layerChain`, `layerWalk`, `layerDigestChain`, and ancestor walkers.
- Lazy/materialization helpers: `isLazy`, `Extract`, `ensureLocalContentBlob`, `unlazy`, `unlazyDiffMerge`, `unlazyLayer`, `prepareRemoteSnapshotsStargzMode`, `prepareRemoteSnapshotsOverlaybdMode`, and `withRemoteSnapshotLabelsStargzMode`.
- Blob/descriptor helpers: `ociDesc`, `linkBlob`, `getBlobWithCompression`, `walkBlob`, `walkBlobVariantsOnly`, `getBlobDesc`, `addBlobDescToInfo`, `filterAnnotationsForSave`, `layerToDistributable`, and `layerToNonDistributable`.
- Lifecycle methods: `Mount`, `Release`, `Finalize`, mutable `Commit`, mutable `release`, `remove`, and `size`.
- Mount helpers: `setReadonly`, `readonlyOverlay`, `newSharableMountPool`, `sharableMountPool`, and `sharableMountable`.

## Control Flow

Records hold a shared mutex, a ref set, parent union, metadata, mount cache, optional equal mutable/immutable partner, and cached digest chain. `ref` and `mref` add handle objects to `refs`; `Release` removes handles, updates last-used metadata when the last last-used-triggering handle is released, and cleans view leases/mount cache. Mutable release removes non-retained records, or removes equal immutable records when appropriate.

Mutable `Commit` does not immediately commit the snapshotter snapshot. It creates a new immutable `cacheRecord` sharing the mutable record mutex and parent refs, records `equalMutable`, persists committed metadata on the immutable side, and returns an immutable ref. `Finalize` commits the mutable snapshot into the immutable snapshot ID, creates a lease, marks the mutable dead, asynchronously removes mutable state, clears equal-mutable metadata, and persists the immutable record.

Mounting an immutable ref extracts lazy content first, then creates or reuses a readonly view snapshot for immutable refs, or uses the equal mutable snapshot until finalization is required. Mutable mounts are wrapped in a sharable mount pool so multiple callers can bind-mount a shared overlayfs mount safely.

Lazy extraction distinguishes blob-only layers from merge/diff refs. For layers, `unlazyLayer` ensures the blob is present via `lazyRefProvider`, prepares a temporary snapshot, applies the layer with the applier, commits it to the target snapshot ID, and flips `blobOnly` false. For merge/diff, `unlazyDiffMerge` recursively unlazies layer inputs and calls the merge snapshotter with constructed diffs. Stargz and overlaybd paths try to prepare remote snapshots before falling back to full unlazy.

Compression variant support stores blob descriptor metadata in content labels and links variant blobs with GC labels in both directions. `walkBlobVariantsOnly` traverses this graph with a visited set. `ociDesc` reconstructs OCI descriptors from metadata/content labels, adds uncompressed and created-at annotations, and converts non-distributable media types depending on URL/preference.

## State and Persistence Behavior

Ref state spans memory (`refs`, mount cache, equal refs, lazy handler maps), metadata (`blobOnly`, diff/blob/chain IDs, snapshot ID, size, image refs, deleted flags), leases (record, view, compression variant), snapshotter snapshots/views, and content-store labels. Size is cached in metadata and recomputed through snapshotter usage plus linked blob variants. View snapshots use temporary leases and are deleted when refs are released. Sharable mount pool directories are cleaned on manager startup and unmounted/removed when reference counts drop.

## Dependencies and Integration Points

This file integrates containerd content, images, leases, mounts, snapshots, labels, errdefs, BuildKit config/session/snapshot/solver/compression/lease/progress/tracing/rootless/winlayers utilities, OCI descriptors/digests, OpenTelemetry tracing, and OS mount/user namespace helpers. It is called by `manager.go`, `remote.go`, and external worker code via the public ref interfaces.

## Risks and Edge Cases

- Ref counting and equal mutable/immutable sharing are subtle; mutable and immutable records may share a mutex and backing snapshot until finalization.
- `layerWalk` intentionally treats some diff refs as reused upper blobs, but other diffs become their own synthetic blob.
- Lazy extraction requires valid descriptor handlers and an applier; nil handlers or missing content produce runtime failures.
- Compression variant graphs can contain cycles; traversal must keep `visited`.
- Read-only overlay conversion rewrites `lowerdir` to include the former `upperdir`; incorrect option parsing could expose writable state.
- `sharableMountable` keeps a count and can panic on double release only under `BUILDKIT_DEBUG_PANIC_ON_ERROR=1`; otherwise under-release is tolerated but may hide misuse.
- Snapshotter-specific label injection for stargz uses temporary unique labels and best-effort cleanup.

## Test Signals

`manager_test.go` exercises ref commit/finalize/release, lazy extraction, mount readonly behavior, sharable mount pool cleanup, blob metadata, compression variant linking and loops, remote descriptor generation, merge/diff refs, broken parent recovery, and prune behavior. OS-gated tests cover Linux mount semantics.
