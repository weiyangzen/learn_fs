# sources/cloud-native/buildkit/cache/remote.go

## Purpose

`remote.go` turns immutable cache refs into solver remotes: ordered OCI layer descriptors plus content providers that can read local content or lazily materialize remote blobs. It also enumerates compression variants and exposes an `Unlazier` path for prefetch/materialization.

## Important APIs, Types, and Functions

- `Unlazier` defines `Unlazy(ctx) error`.
- `immutableRef.GetRemotes` returns one or more `*solver.Remote` values for a ref, respecting compression config and an `all` variants flag.
- `appendRemote` appends a descriptor/provider to each parent remote.
- `getAvailableBlobs` recursively builds all available compression-variant remote chains.
- `immutableRef.getRemote` computes blob chains, reconstructs descriptors, forces compression if configured, adds distribution source annotations for lazy refs, and builds a lazy multiprovider.
- `getBlobWithCompressionWithRetry` tries existing variants, then calls `ensureCompression`.
- `lazyMultiProvider` implements `content.Provider` plus `Unlazy`.
- `lazyRefProvider` implements provider/info/unlazy behavior for a single descriptor/ref pair.

## Control Flow

`GetRemotes` creates a temporary lease, gets the main remote, and usually returns it immediately. When `all=true`, compression is not forced, and descriptors exist, it searches for all available chains whose topmost blob matches the requested compression type. It uses `getBlobWithCompression` for the topmost descriptor and recursively enumerates parent variants.

`getRemote` first calls `computeBlobChain` to ensure each layer has descriptor/blob metadata. It walks the layer chain, creates descriptors through `ociDesc`, detects missing media types from content, adds distribution source annotations for lazy image refs, optionally forces compression conversion, and registers each descriptor in a `lazyMultiProvider`.

`lazyRefProvider.ReaderAt` checks digest equality, calls `Unlazy`, then reads from the local content store. `Info` returns local content info when available; for lazy refs it returns digest/size without pulling content. `Unlazy` deduplicates pulls by digest with `unlazyG`, validates laziness, uses descriptor handler progress, copies remote content into the content store, links the blob to the ref, and optionally sets a human-readable description from image refs.

## State and Persistence Behavior

Remote generation may mutate cache/content state. `computeBlobChain`, compression conversion, `linkBlob`, and lazy copy can write blob metadata, content blobs, variant leases/labels, size invalidations, and cache descriptions. Temporary leases protect content during remote construction. Lazy provider maps are in-memory capabilities tied to returned remotes.

## Dependencies and Integration Points

The file integrates BuildKit cache config, solver remotes, session groups, content utilities, compression/converter helpers, lease utilities, pull progress, logs, containerd reference parsing, content stores, and OCI descriptors. It is the bridge between local cache refs and exporters/importers that consume `solver.Remote`.

## Risks and Edge Cases

- `all=true` can produce combinatorial chains across available parent compression variants, though each layer usually has few variants.
- Forced compression on lazy refs may trigger full unlazy when conversion is needed.
- Distribution source annotations are built by parsing image refs with a dummy scheme; malformed refs fail remote generation.
- `lazyMultiProvider.Info` can report existence for lazy content without local bytes, so callers must use `ReaderAt` to force materialization.
- `Unlazy` assumes non-nil descriptor handlers for lazy refs; missing handlers are guarded earlier but still checked.

## Test Signals

`TestGetRemotes`, `TestSharingCompressionVariant`, `TestLoopLeaseContent`, `TestConversion`, and `TestNondistributableBlobs` validate descriptor media types, annotations, compression variants, lazy/local content behavior, variant graph traversal, and non-distributable media/URL handling.
