# sources/cloud-native/buildkit/cache/remotecache/import.go

## Purpose

This file implements the generic remote cache importer used by registry, local, and OCI-style cache sources. It reads a cache manifest or image manifest, detects whether BuildKit cache config is stored as a dedicated config blob or inline in image config, rebuilds v1 cache chains, and returns solver cache managers that can load remote results.

## Important APIs, Types, and Functions

- `ResolveCacheImporterFunc` is the resolver signature for cache backends.
- `Importer` is the interface implemented by all remote cache importers.
- `DistributionSourceLabelSetter` allows providers to add registry distribution source labels and annotations to layer descriptors.
- `NewImporter` returns a content-provider-backed importer.
- `contentCacheImporter.Resolve` is the main import entry point for OCI or Docker manifests.
- `readBlob` reads small manifest/config blobs and tolerates valid bytes returned with `io.EOF`.
- `importInlineCache` extracts inline BuildKit cache metadata from image configs.
- `allDistributionManifests` recursively walks image indexes or manifest lists to collect leaf manifests.
- `parseCreatedLayerInfo` maps non-empty image history entries to layer creation metadata.

## Control Flow and State

`Resolve` reads the descriptor blob and detects its manifest media type. For an image index or Docker manifest list, it scans child descriptors: the cache config descriptor is identified by `application/vnd.buildkit.cacheconfig.v0`, while other descriptors become candidate layer providers. For an image manifest, it treats the config as cache config when its media type matches and treats layers as candidate remote layer descriptors. If a provider supports distribution source labels, it annotates descriptors and best-effort writes labels to the local content store.

When a dedicated cache config descriptor is present, `Resolve` reads it, parses it into a `v1.CacheChains`, creates key/result storage, and returns a solver cache manager. Without dedicated config, it falls back to inline import. Inline import recursively collects all distribution manifests, loads each image config, reads `moby.buildkit.cache.v0` records, reconstructs layer descriptors with uncompressed diff IDs and optional history metadata, parses each into cache chains, and combines all resulting cache managers.

State is not persisted locally except through optional distribution labels. The importer constructs an in-memory graph and leaves layer content remote through the content provider.

## Dependencies and Integration Points

The importer depends on containerd content and image media type helpers, BuildKit's `v1` cache parser/storage, solver cache manager APIs, worker remote loading, `imageutil.DetectManifestBlobMediaType`, and optional registry-specific distribution labeling. Registry and local importers feed this importer with a provider and root descriptor.

## Risks and Edge Cases

`readBlob` caps manifest/config reads at 1 MiB; oversized config blobs fail. Unsupported or uninferrable manifest media types return an error built from a possibly nil prior error, so error wording depends on wrapping behavior. Inline cache import requires image config rootfs diff IDs to match manifest layer count; mismatches are logged and skipped. Inline `parseCreatedLayerInfo` returns only non-empty-layer history entries, and later code indexes by manifest layer count, so malformed history shorter than layer count can panic if not aligned by upstream image config validity. Missing layer provider entries cause cache results to be skipped rather than failing the whole parse.

## Test Signals

This subset does not include direct tests for `import.go`. Behavior is indirectly covered by cache backend integration tests and the v1 marshal/parse roundtrip test. Specific inline-cache edge cases, distribution labeling failures, and oversized config handling are not tested here.
