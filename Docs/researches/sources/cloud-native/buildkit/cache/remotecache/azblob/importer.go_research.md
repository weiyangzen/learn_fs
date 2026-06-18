# sources/cloud-native/buildkit/cache/remotecache/azblob/importer.go

## Purpose

`azblob/importer.go` implements BuildKit remote cache import from Azure Blob Storage. It loads one or more named cache manifests, converts Azure-stored layer entries back into remotecache v1 descriptor/provider pairs, and returns a combined solver cache manager.

## Important APIs, Types, and Functions

- `ResolveCacheImporterFunc` creates an Azure cache importer from attrs/session context and returns an empty descriptor because this backend resolves by configured names.
- `importer.Resolve` loads configured manifests in parallel and converts each cache chain into a solver cache manager.
- `loadManifest` checks manifest existence, downloads JSON config, builds layer providers, parses v1 cache config, and returns cache chains.
- `makeDescriptorProviderPair` converts `CacheLayer` metadata into an OCI descriptor and Azure-backed provider.
- `fetcher.Fetch` downloads a blob body by descriptor digest.
- `ciProvider` combines `content.Provider` and `content.InfoProvider`, caching an existence check in `Info`.

## Control Flow

The resolver parses config and creates a container client. `Resolve` starts an errgroup over all configured names, calling `loadManifest` for each. Missing manifests produce empty cache chains rather than errors. Existing manifests are downloaded, logged, unmarshaled, and each layer is converted into a descriptor/provider pair. The v1 parser populates `CacheChains`; then `NewCacheKeyStorage` and `solver.NewCacheManager` wrap those chains for solver use. Multiple named manifests are combined with `solver.NewCombinedCacheManager`.

When a solver later needs layer content, `fetcher.Fetch` checks that the digest key exists in Azure and opens a download stream. `ciProvider.Info` verifies digest equality, returns cached info after the first successful check, and maps missing blobs to containerd not-found errors.

## State and Persistence Behavior

Importer state is in-memory: config, container client, parsed cache chains, and per-provider `checked` flags. It reads persistent Azure manifests and blobs but does not write Azure state. Descriptor annotations are reconstructed from cache layer annotations, including uncompressed diff ID and optional created-at timestamp.

## Dependencies and Integration Points

The importer integrates Azure blob downloads, BuildKit remotecache v1 parsing, solver cache manager construction, worker-backed cache key/result storage, contentutil fetcher adapters, progress reporting, containerd content/info provider interfaces, and OCI descriptors.

## Risks and Edge Cases

- Any error loading one configured manifest aborts the whole resolve, except a missing manifest which returns an empty chain.
- `ciProvider.checked` is read before locking, so concurrent `Info` calls have a benign data race risk unless callers serialize access.
- Missing or incomplete layer annotations abort import because descriptors require diff ID, size, and media type.
- `Fetch` performs an existence check before download, adding latency and a race where the blob can disappear between check and download.
- Manifest JSON is read fully into memory.

## Test Signals

No Azure importer tests are in this subset. Expected behavior is inferred from remotecache v1 contracts and generic cache tests that validate descriptors and provider behavior. Azure integration would benefit from mocked container clients or live-storage tests.
