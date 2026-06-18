# Research: subset-b-000005

This grouped report covers the BuildKit remote cache, cache import, cache utility, and client gateway files assigned to `subset-b-000005`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/gha/gha.go -->
# sources/cloud-native/buildkit/cache/remotecache/gha/gha.go

## Purpose

This file implements the GitHub Actions remote cache backend for BuildKit. It provides resolver functions for the `gha` cache exporter and importer, translates BuildKit v1 cache-chain metadata into GitHub Actions cache entries, restores cache metadata back into solver cache managers, and optionally signs or verifies the cache index using a configured Sigstore policy helper.

## Important APIs, Types, and Functions

- `Config` is the backend configuration. It carries the BuildKit cache scope, GitHub runtime cache URL/token, optional GitHub REST token/repository for key listing, selected cache service version, timeout, shared `ghatypes.CacheConfig`, and a verifier provider.
- `getConfig` parses exporter/importer attributes: `scope`, `token`, `url`, `url_v2`, `version`, `timeout`, `repository`, and `ghtoken`. It defaults scope to `buildkit`, infers cache API version from `url_v2` or legacy URL shape, and rejects missing token or URL.
- `ResolveCacheExporterFunc` and `ResolveCacheImporterFunc` adapt this backend into the generic `remotecache` registration contract.
- `NewExporter` creates an `actionscache.Cache`, a `v1.CacheChains`, and returns an exporter implementing `solver.CacheExporterTarget`.
- `exporter.Finalize` marshals collected cache chains, uploads missing layer blobs under `buildkit-blob-1-<digest>`, writes the index under `index-<scope>-1-<hashed-github-scope>`, and optionally signs the index.
- `verifySignature`, `certToStringMap`, and `simplePatternMatch` enforce the configured verification policy for signed indexes.
- `NewImporter`, `importer.loadScope`, and `importer.Resolve` load cache indexes for all readable GitHub cache scopes, rebuild `v1.CacheChains`, and expose them as a combined solver cache manager.
- `ciProvider` is a content provider over GitHub cache entries. It caches loaded `actionscache.Entry` objects, provides content info, and returns reader-at handles for layer downloads.

## Control Flow and State

Exporter construction initializes an empty v1 cache-chain target. During solve, the solver calls the embedded `CacheExporterTarget` to add cache records. At finalization, the exporter marshals those records, resolves layer descriptors, verifies uncompressed digest annotations, and uploads each missing blob. Existence checks use a GitHub REST-driven active key map when `repository` and `ghtoken` are available; otherwise the exporter probes entries one by one with the runtime cache API. After layer upload, it serializes the cache config and writes it as a mutable cache entry with a short lock duration. If signing is configured, it runs the configured command with the serialized index on stdin, verifies the produced bundle locally, and uploads the signature as a blob keyed by the index digest plus `-sig`.

Importer construction mirrors exporter setup. `Resolve` starts one goroutine per GitHub cache scope, calls `loadScope`, and combines the resulting cache managers. `loadScope` reads the index entry, optionally verifies its signature, unmarshals `cacheimporttypes.CacheConfig`, converts cache-layer annotations back into OCI descriptors, and asks `v1.ParseConfig` to rebuild the cache graph. Layer bytes remain remote and are fetched later through `ciProvider.ReaderAt` when the worker materializes a remote result.

Persistence is external to the BuildKit process: blobs and index JSON are stored in GitHub Actions cache entries. Keys are deterministic and include BuildKit's local cache format version. The index key includes a hash of the GitHub cache scope chosen from writable cache scopes and adds `-sig` when signing or required verification changes the trust namespace.

## Dependencies and Integration Points

The backend depends on `github.com/tonistiigi/go-actions-cache` for GitHub cache runtime and REST APIs, `cache/remotecache/v1` for cache graph serialization, `solver` and `worker` for imported cache manager construction, `containerd/content` for reader-at content contracts, `progress` for status messages, `tracing.DefaultClient` for HTTP instrumentation, and `moby/policy-helpers` plus Sigstore certificate summaries for signature policy checks.

It integrates with generic cache selection through `remotecache.ResolveCacheExporterFunc` and `ResolveCacheImporterFunc`. The `ghatypes.CacheConfig` policy is supplied by daemon configuration and is shared with this backend instead of being parsed from cache attributes.

## Risks and Edge Cases

Missing `token` or URL attributes fail early. Cache API version inference is best effort for older clients and can select v1 unless `url_v2` or a known v2 URL is present. `exporter.Finalize` uploads blobs sequentially, so large cache exports may be slow. The active key map path depends on optional REST credentials; without it, each layer performs a load probe. `ciProvider.ReaderAt` uses `context.TODO()` for downloads, so cancellation of the caller context is not passed to the actual download handle. Signature verification is intentionally strict when `Verify.Required` is set: missing bundles, missing signer data, insufficient timestamp/tlog thresholds, or mismatched certificate fields all fail imports. The simple wildcard matcher only supports whole-string, prefix, suffix, and contains matching.

## Test Signals

Coverage comes from `gha_test.go`, which performs an end-to-end GitHub Actions cache export/import when the GitHub runtime token and cache URL are present. The test verifies cache reuse across prune by comparing local export files before and after import. Direct unit coverage for config parsing, key naming, REST key map behavior, and signature verification is absent in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/gha/gha.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/gha/gha_test.go -->
# sources/cloud-native/buildkit/cache/remotecache/gha/gha_test.go

## Purpose

This file defines the integration test for the GitHub Actions cache backend. It validates that a BuildKit solve can export cache records to the GitHub Actions cache service, prune all local cache state, and then import the remote cache to reproduce the same build outputs.

## Important APIs, Types, and Functions

- `TestGhaCacheIntegration` registers the single integration scenario and mirrors `busybox:latest`.
- `testBasicGhaCacheImportExportExtraTimeout` builds a two-step LLB state, exports local output and `gha` cache, prunes local cache, then rebuilds with `gha` cache import.
- `ensurePruneAll` retries `client.Prune(..., client.PruneAll)` until `DiskUsage` reports no entries.
- `requiresLinux` skips the scenario outside Linux.

## Control Flow and State

The test initializes OCI/containerd or dockerd workers in `init`, then creates a BuildKit client for the sandbox. It constructs a state rooted in scratch with two files: a constant file and a generated random checksum. It gathers GitHub Actions cache attributes from `ACTIONS_RUNTIME_TOKEN`, `ACTIONS_CACHE_URL`, `ACTIONS_RESULTS_URL`, and `ACTIONS_CACHE_SERVICE_V2`; if the environment is incomplete, the test skips. The scope includes the test name and branch/tag/pull-request suffix from `GITHUB_REF` to avoid broad key collisions.

The first solve exports the filesystem locally and writes `mode=max` remote cache to `gha`. After confirming the files exist, the test prunes all local cache. The second solve uses the same definition with `CacheImports` from the same scope. It then verifies the constant file and generated checksum match the original output, proving the remote cache restored the previously generated layer content.

## Dependencies and Integration Points

The test uses the public `client.Solve` API, `llb` state construction, integration sandbox helpers, worker feature gates for cache import/export and `FeatureCacheBackendGha`, and GitHub-hosted runner environment variables. It exercises the actual remote cache resolver indirectly through cache option type `gha`.

## Risks and Edge Cases

The test is environment-sensitive and skips unless GitHub runtime cache variables are available. GitHub Cache Service v2 is noted as not immediately consistent, so the test sleeps for three seconds before import. `ensurePruneAll` is retry-based and can fail if a worker holds cache references longer than expected. The test does not cover signed cache indexes, REST key-map optimization, malformed attributes, or multiple readable scopes.

## Test Signals

This is the primary test signal for `gha.go`: successful export, local prune, and import with identical output content. It also validates v2 URL selection when `ACTIONS_CACHE_SERVICE_V2` is true.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/gha/gha_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/gha/ghatypes/config.go -->
# sources/cloud-native/buildkit/cache/remotecache/gha/ghatypes/config.go

## Purpose

This file defines the daemon-side configuration structure for signed and verified GitHub Actions cache indexes.

## Important APIs, Types, and Functions

- `CacheConfig` groups optional signing and verification settings.
- `SignConfig` carries the external signing command argv.
- `VerifyConfig` carries a `Required` flag and `VerifyPolicy`.
- `VerifyPolicy` defines timestamp and transparency-log thresholds and embeds Sigstore Fulcio `certificate.Summary` fields for signer certificate matching.

## Control Flow and State

There is no executable control flow. The structures are populated from TOML configuration and consumed by `gha.go`. When `Sign` is non-nil and has a command, the exporter signs serialized cache index bytes. When `Verify.Required` is true, the importer requires a matching signature bundle before accepting the index. Policy fields are compared by converting certificate summaries to a string map and applying simple wildcard matching in the GHA backend.

## Dependencies and Integration Points

The sole dependency is Sigstore's `certificate.Summary`, which provides normalized signer identity fields. The type is imported by `cache/remotecache/gha` through `*ghatypes.CacheConfig`.

## Risks and Edge Cases

Policy behavior depends on JSON field names emitted for `certificate.Summary`; adding or renaming fields upstream can affect matching. Empty certificate policy values are ignored, so partially specified policy is permissive for unspecified fields. An empty signing command with non-nil `Sign` results in no signing work.

## Test Signals

No tests in this subset instantiate these structs directly. Their behavior is indirectly constrained by the signature verification path in `gha.go`, but signed cache integration tests are not present here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/gha/ghatypes/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/import.go -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/inline/inline.go -->
# sources/cloud-native/buildkit/cache/remotecache/inline/inline.go

## Purpose

This file implements the inline cache exporter. Instead of uploading a separate remote cache object, it serializes cache records suitable for embedding into an image config's `moby.buildkit.cache.v0` field while aligning cache results to the actual image layer order.

## Important APIs, Types, and Functions

- `ResolveCacheExporterFunc` returns an inline exporter resolver.
- `NewExporter` creates an exporter backed by `v1.CacheChains`.
- `exporter.Finalize` is a no-op because inline cache bytes are produced per image layer set rather than at generic cache finalization.
- `ExportForLayers` filters cache records to the image's layer set, rewrites layer result references to match image order, and returns JSON cache records.
- `layerToBlobs` walks a parent chain from a top layer index and returns blob digests lowest-to-highest.

## Control Flow and State

The exporter collects cache records through its embedded `CacheExporterTarget`. `ExportForLayers` marshals the full cache graph, builds a descriptor subset containing only blobs that match the supplied image layer digests or their uncompressed labels, parses that subset into a fresh cache chain, and marshals it again. This removes cache entries unrelated to the exported image.

It then builds an image-layer blob index and rewrites each result. If a result chain matches the image layer order, it can be represented as a compact `CacheResult` with the top layer index. If the result uses layers in a different order, it is converted into `ChainedResult` with explicit per-layer indexes and the original `CacheResult` is removed. The function finally marshals only `cfg.Records`, resets internal cache chains, and returns the JSON.

State is transient. The exporter resets after producing inline bytes so subsequent image exports do not reuse stale collected records.

## Dependencies and Integration Points

The exporter relies on v1 cache-chain marshal/parse, `cacheimporttypes` result shapes, containerd's uncompressed digest label, BuildKit compression defaults, and `solver.CacheExporterTarget`. It is invoked by image export paths that need inline BuildKit cache metadata in image configs.

## Risks and Edge Cases

If no cache layers match the supplied image layers, it logs a warning and returns nil. Matching considers both compressed blob digest and uncompressed digest annotation, which is necessary but can be confusing when layer digests differ by compression. Chained-result conversion fails if a result blob cannot be mapped to any supplied image layer. The mutation of `r.Results` while iterating through `r.Results` is subtle and should be kept under test when result structures change.

## Test Signals

No inline-specific tests are in this subset. Inline import handling in `remotecache/import.go` and generic v1 roundtrip tests provide indirect coverage, but `ExportForLayers` ordering and chained-result rewrite behavior are not directly exercised here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/inline/inline.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/local/local.go -->
# sources/cloud-native/buildkit/cache/remotecache/local/local.go

## Purpose

This file implements the `local` remote cache backend. It exports and imports cache manifests and blobs through a client session content store rooted at a user-provided local directory.

## Important APIs, Types, and Functions

- Attribute constants define `digest`, `src`, `dest`, `image-manifest`, and `oci-mediatypes`.
- `ResolveCacheExporterFunc` parses `dest`, media-type, and compression attributes, obtains a session content store, and returns a generic remote cache exporter.
- `ResolveCacheImporterFunc` parses `digest` and `src`, obtains a session content store, looks up the root descriptor size, and returns a generic remote cache importer.
- `getContentStore` resolves the active session and wraps `sessioncontent.NewCallerStore`.
- `unlazyProvider.UnlazySession` exposes the session group for later remote materialization.

## Control Flow and State

Exporter resolution requires `dest`, creates a content store ID `local:<dest>`, and delegates all cache graph serialization and content writing to `remotecache.NewExporter`. `oci-mediatypes` defaults to true. `image-manifest` defaults to true unless Docker media types are requested, preserving compatibility with non-OCI output.

Importer resolution requires explicit `digest` and `src`. It locates `local:<src>`, obtains content info for the digest to fill a descriptor, and creates a generic importer over that store. The descriptor media type is intentionally left empty because local `index.json` support is incomplete and the generic importer can infer manifest type from bytes.

State persists in the client-side directory accessed through the session content service. BuildKit itself only retains transient provider wrappers.

## Dependencies and Integration Points

This backend depends on BuildKit session management, session content stores, generic `remotecache.NewExporter`/`NewImporter`, compression attribute parsing, and OCI descriptors. It is used when cache options specify `type=local`.

## Risks and Edge Cases

Both import and export require a live client session; `getContentStore` fails without one. Session selection uses the next session from the session group, with a TODO noting that store support detection should be improved. Content-store acquisition has a five-second timeout and can fail in slow or disconnected clients. The importer requires the digest explicitly; if a user points at a directory without passing the root digest, import cannot proceed.

## Test Signals

This subset contains no direct tests for the local cache backend. Generic cache import/export behavior and integration suites elsewhere are expected to exercise it.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/local/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/registry/registry.go -->
# sources/cloud-native/buildkit/cache/remotecache/registry/registry.go

## Purpose

This file implements the `registry` remote cache backend. It exports cache manifests to container registries, imports cache manifests from registries, supports insecure registry configuration, and annotates imported layer descriptors with distribution-source metadata for efficient later pulls and snapshot labels.

## Important APIs, Types, and Functions

- `canonicalizeRef` validates and normalizes registry references, applying a default tag.
- `ResolveCacheExporterFunc` parses compression and media-type attributes, resolves a pusher, and returns a generic cache exporter over the registry pusher.
- `ResolveCacheImporterFunc` resolves a registry reference, creates a fetcher, wraps it in `withDistributionSourceLabel`, and returns a generic cache importer.
- `withDistributionSourceLabel` implements `remotecache.DistributionSourceLabelSetter` and snapshot label helpers.
- `registryConfig` swaps in plain HTTP/insecure registry hosts when `registry.insecure=true`.

## Control Flow and State

Export resolution canonicalizes `ref`, parses `oci-mediatypes`, `image-manifest`, `registry.insecure`, and compression attributes, then constructs a resolver scoped for push. It creates a pusher and delegates cache manifest construction and upload to `remotecache.NewExporter`.

Import resolution canonicalizes the same reference, creates a resolver scoped for pull, resolves the reference to a descriptor, and builds a limited fetcher provider. The provider wrapper records distribution source labels in the local content store and injects `containerd.io/distribution.source.ref` annotations into descriptors during generic cache import. It can also produce inherited snapshot labels, including estargz labels and target-ref labels.

Persistent state lives in the target registry. Local content state may be updated with distribution-source labels so later snapshot/content operations know where blobs came from.

## Dependencies and Integration Points

The backend uses containerd resolver, fetcher, pusher, content, snapshot label, and Docker distribution label APIs. It integrates with BuildKit resolver pools, session-authenticated registry access, generic remote cache import/export, compression parsing, and estargz snapshot labeling.

## Risks and Edge Cases

Invalid or missing refs fail early. `registry.insecure=true` replaces host configuration for the reference domain and sets both insecure and plain HTTP, which is useful for tests but sensitive in production. The importer ignores errors when setting source labels because layers may not exist locally; failures there do not stop import. `SnapshotLabels` checks `len(descs) < index`, which does not guard `index == len(descs)` and could panic if called with an out-of-range equal index.

## Test Signals

No direct tests for this file are present in the subset. It is indirectly exercised by client integration tests that push/pull images and by broader cache import/export tests outside this assignment.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/registry/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/s3/readerat.go -->
# sources/cloud-native/buildkit/cache/remotecache/s3/readerat.go

## Purpose

This file adapts offset-based object reads, such as S3 ranged `GetObject` requests, into a `ReaderAtCloser` implementation for BuildKit content providers.

## Important APIs, Types, and Functions

- `ReaderAtCloser` combines `io.ReaderAt` and `io.Closer`.
- `readerAtCloser` stores the current sequential read stream, current offset, optional native reader-at delegate, opener function, mutex, and closed flag.
- `toReaderAtCloser` constructs the adapter from an `open(offset)` callback.
- `ReadAt` opens or reuses an object stream at the requested offset.
- `Close` marks the adapter closed and closes any active stream.

## Control Flow and State

All operations are serialized by a mutex. `ReadAt` returns `io.EOF` after close. If the currently open stream is absent or its offset does not match the requested `off`, the adapter closes it and calls `open(off)`. If the stream itself implements `io.ReaderAt`, future reads delegate directly to it. Otherwise, the adapter reads sequentially into the caller's buffer and advances its tracked offset by bytes read.

The object state is in-memory and per reader. The underlying S3 object is not mutated.

## Dependencies and Integration Points

`s3.go` uses this adapter in `s3Client.ReaderAt`, passing an opener that performs ranged `GetObject` requests. It satisfies the `content.ReaderAt` expectations when combined with the size wrapper in `s3.go`.

## Risks and Edge Cases

The sequential read loop compares `nn == len(p)` after slicing `p = p[nn:]`, so full-buffer detection is fragile; normally it exits because subsequent reads return zero/EOF. The implementation serializes all reads, so concurrent random `ReadAt` calls will reopen streams often and may be inefficient. Returning `io.EOF` after close is simple but loses distinction between closed and natural EOF.

## Test Signals

No direct tests are included for this adapter. Its behavior is indirectly exercised by any S3 cache import path that materializes remote blobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/s3/readerat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/s3/s3.go -->
# sources/cloud-native/buildkit/cache/remotecache/s3/s3.go

## Purpose

This file implements the Amazon S3 remote cache backend. It exports v1 cache layers and manifests to S3-compatible object storage, imports cache manifests from S3, and provides random-access object reads for worker remote materialization.

## Important APIs, Types, and Functions

- `Config` captures bucket, region, key prefixes, manifest names, touch-refresh interval, endpoint and credential overrides, path-style mode, upload parallelism, accept-encoding behavior, and retry settings.
- `getConfig` parses backend attributes with environment fallbacks for `AWS_BUCKET` and `AWS_REGION`.
- `ResolveCacheExporterFunc` and `ResolveCacheImporterFunc` expose the S3 backend to generic cache option resolution.
- `exporter.Finalize` uploads missing or stale blobs in parallel and writes manifest JSON under configured names.
- `importer.load` reads the first configured manifest, reconstructs descriptors from annotations, parses v1 cache chains, and creates cache manager storage.
- `newS3Client` builds the AWS SDK client and transfer manager.
- `s3Client` methods implement manifest read/write, object existence checks, ranged reads, blob key generation, and touch-by-copy for retention refresh.

## Control Flow and State

Configuration starts from attributes. Bucket and region are required through attributes or environment. Prefix defaults split manifests under `manifests/` and blobs under `blobs/`; manifest `name` defaults to `buildkit` and can contain semicolon-separated names. `touch_refresh` defaults to 24 hours. Upload parallelism defaults to 4 and must be positive.

During export finalization, the exporter marshals cache chains, starts a bounded worker pool, and processes each cache layer. For every layer it validates the descriptor annotations, extracts diff ID, checks S3 object presence, touches old objects when their last modified time exceeds the refresh interval, or uploads missing blobs through the transfer manager. It then stores layer annotations needed for future import. After all layers complete, it marshals the cache config and writes it to every configured manifest name.

During import, the importer reads only the first manifest name. Missing manifests produce an empty cache chain. Existing manifests are decoded strictly so trailing JSON data fails. Each layer annotation becomes an OCI descriptor backed by `s3Client` as content provider. `Resolve` converts the parsed chains into a solver cache manager using the worker.

Object state persists in S3. Blob keys are content-addressed by digest under the configured prefix; manifest keys are mutable names.

## Dependencies and Integration Points

The backend depends on AWS SDK v2 S3 and transfer manager packages, BuildKit `v1` cache serialization, BuildKit compression defaults, solver/worker cache manager APIs, containerd content interfaces, and OCI descriptors. It supports S3-compatible services through `endpoint_url`, `use_path_style`, retry knobs, and `disable_accept_encoding` for GCS compatibility.

## Risks and Edge Cases

Attribute parsing silently ignores invalid `touch_refresh`, boolean `use_path_style`, and boolean `disable_accept_encoding` values, while upload parallelism and retry settings are strict. Import reads only `Names[0]`, even though export can write many names. Touching large objects uses multipart copy in 5 GiB chunks and must abort on failure. `touch` dereferences `size` from `HeadObject`; a nil content length would panic. `defer ra.Close()` inside upload worker loops can hold multiple readers open until the worker goroutine exits. The backend does not sign or verify manifests.

## Test Signals

No S3 backend tests are present in this subset. Behavior is likely covered by broader integration suites, but config parsing, touch logic, multipart copy, strict manifest decode, and reader-at behavior are not directly tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/s3/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/cachestorage.go -->
# sources/cloud-native/buildkit/cache/remotecache/v1/cachestorage.go

## Purpose

This file converts in-memory `CacheChains` into immutable solver cache key and result storage for imported remote caches. It lets the solver query remote cache keys, links, result IDs, and lazily load remote worker refs.

## Important APIs, Types, and Functions

- `NewCacheKeyStorage` computes item IDs, walks cache-chain leaves, and returns `solver.CacheKeyStorage` plus `solver.CacheResultStorage`.
- `addItemToStorage` recursively registers items, outgoing links, and result-to-key reverse indexes.
- `cacheKeyStorage` implements existence, walking, result lookup, link walking, backlinks, and result-to-key lookup.
- `cacheResultStorage` implements immutable result loading from remote descriptors.
- `LoadWithParents` materializes a selected result and any parent/sub-remote results needed by solver callers.
- `LoadRemotes` returns raw remote descriptors, optionally filtered by compression.
- `remoteID` creates a non-stable ID by hashing the sequence of remote descriptor digests.

## Control Flow and State

`NewCacheKeyStorage` computes deterministic item IDs in the cache graph and registers every leaf recursively. `addItemToStorage` uses `byItem` as both a deduplication table and recursion-loop sentinel. For each parent link, it records an outgoing link from the source item to the target item using normalized link data. For each result, it derives a remote result ID and records which cache key IDs provide that result.

The key storage is read-only: mutation methods such as `AddResult`, `Release`, and `AddLink` are no-ops because imported caches are immutable. Link walking maps solver link requests through the internal `nlink` key, including the output-key digest form. Result storage loads remotes by asking the worker to convert `solver.Remote` descriptors into worker refs. On partial failure in `LoadWithParents`, already loaded refs are released.

All state is in-memory. Persisted cache state remains in the remote backend that supplied descriptors and providers.

## Dependencies and Integration Points

The storage implements BuildKit solver cache interfaces and depends on worker `FromRemote`, BuildKit session groups, compression filtering, and the `CacheChains` item graph from `chains.go`. Remote cache importers call it after parsing a backend-specific manifest.

## Risks and Edge Cases

`remoteID` is explicitly not stable, so it must not be used as a persisted identifier. `Load` assumes `byResultID` returns a non-nil item and would panic if called with an unknown result ID; callers typically check existence first, but this is a sharp edge. `Walk` map iteration order is nondeterministic. `LoadRemotes` compression filtering is best effort and can return nil rather than an error when no matching remote exists. Add/release mutation methods silently do nothing, which is correct for imports but easy to misunderstand in generic cache code.

## Test Signals

There are no direct tests for `cachestorage.go` in this subset. It is indirectly exercised by v1 parse/marshal tests and all cache importer integrations that produce solver cache managers.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/cachestorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/chains.go -->
# sources/cloud-native/buildkit/cache/remotecache/v1/chains.go

## Purpose

This file defines the core in-memory cache graph used by remote cache export and import. It implements `solver.CacheExporterTarget`, deduplicates cache records, links records through dependencies, tracks remote results, and marshals the graph into the v1 cache config schema.

## Important APIs, Types, and Functions

- `NewCacheChains` constructs a graph with root records indexed by digest.
- `CacheChains.Add` accepts solver cache records, dependencies, and export results, merging compatible graph nodes and recording parent/child links.
- `computeIDs` and `item.computeID` assign deterministic IDs for solver key storage.
- `leaves` returns graph nodes without children, which become marshal/storage roots.
- `IntersectAll` intersects dependency candidate sets.
- `Marshal` serializes the graph into `cacheimporttypes.CacheConfig` and a descriptor/provider map.
- `DescriptorProviderPair` wraps OCI descriptors and content/info providers, while forwarding optional unlazy-session and snapshot-label capabilities.
- `item` tracks digest, children, parents, results, and owning graph.
- `addChild`, `addResult`, `bestResult`, `walkChildren`, and `walkAllResults` maintain and traverse graph relationships.

## Control Flow and State

`Add` ignores digests with the `random:` prefix, since those cache keys should not become portable cache records. Root records with no dependencies are deduplicated by digest. Records with dependencies validate that every source is an `*item` from the same `CacheChains`, build candidate sets from existing child links that match selector/input/digest, and merge multiple candidate items into one main item when necessary. It then adds results, protects against cycles by removing dependency sources that are already children of the target item, and records child/parent links.

Marshalling starts from leaves and recursively marshals parents before children. Each item emits at most its best result, chosen by newest `CreatedAt`. Remote descriptor chains are serialized through `marshalRemote` in `utils.go`; the final config is sorted deterministically.

Graph state is in memory during a solve or import parse. Persisted state is the marshaled cache config plus remote blobs managed by the backend.

## Dependencies and Integration Points

This graph is shared by all remote cache exporters in the subset: GHA, S3, inline, local, and registry via the generic exporter. It integrates with solver cache export records, containerd content providers, OCI descriptors, BuildKit sessions, and snapshot label extension interfaces.

## Risks and Edge Cases

The merge path for multiple dependency candidates rewrites child parent links and carries results forward; regressions here can create incorrect cache graph aliases. `computeID` iterates over maps, so deterministic ID stability depends on the surrounding graph structure and may be vulnerable to map iteration nondeterminism despite deterministic hashing intent. Only the best result per item is marshaled, so older results are dropped from exported configs. Cycle avoidance mutates dependency sources to nil when needed, which can remove links silently.

## Test Signals

`chains_test.go` verifies a simple graph with two roots and one dependent result, deterministic layer parent encoding, record inputs/selectors, idempotent repeated adds, marshal/parse roundtrip, and adding an extra root. It does not cover merging multiple candidates, cycles, random digests, multi-result best selection, or optional provider capabilities.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/chains.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/chains_test.go -->
# sources/cloud-native/buildkit/cache/remotecache/v1/chains_test.go

## Purpose

This file tests the basic v1 cache-chain marshal and parse behavior.

## Important APIs, Types, and Functions

- `TestSimpleMarshal` is the sole test. It builds a cache graph, marshals it, verifies structural fields, repeats adds for idempotency, roundtrips through JSON and `Parse`, and verifies adding an extra root record changes record count.
- `dgst` is a helper that creates canonical digests from test strings.

## Control Flow and State

The test creates two root records using `outputKey`, then creates a dependent `baz` record with two inputs: one unselected link to `foo` and one selected link to `bar`. It attaches a two-descriptor remote result and a timestamp. After marshal, it checks that the two layer descriptors are serialized as a parent chain, the dependent record contains two input groups and one result, and link indexes/selectors point at the expected records. It then calls the same add sequence again and verifies the config remains identical. Finally, it marshals the config to JSON, parses it into new chains, and checks the original config remains stable.

## Dependencies and Integration Points

The test uses the public `CacheChains.Add`, `Marshal`, `Parse`, `outputKey`, `solver.Remote`, and OCI descriptors. It is the nearest direct test signal for the v1 graph implementation used by all remote cache backends.

## Risks and Edge Cases

The test assumes a deterministic record order for the simple fixture. It does not assert the newly parsed chain's marshaled config; it calls `cc.Marshal` after parsing into `newChains`, so it mainly checks that parsing did not error rather than full roundtrip equality on the new graph. Broader graph cases are untested.

## Test Signals

This test confirms the simple cache config shape and idempotency of repeated adds. Missing coverage includes candidate merging, chained results, missing providers, invalid loops, compression filtering, and storage loading.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/chains_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/parse.go -->
# sources/cloud-native/buildkit/cache/remotecache/v1/parse.go

## Purpose

This file parses serialized v1 cache config JSON back into a `solver.CacheExporterTarget`, reconstructing cache records, input links, and remote result chains.

## Important APIs, Types, and Functions

- `Parse` unmarshals JSON into `cacheimporttypes.CacheConfig` and delegates to `ParseConfig`.
- `ParseConfig` iterates cache records and recursively parses each one.
- `parseRecord` validates record indexes, detects loops, reconstructs input links, resolves compact and chained remote results, and calls target `Add`.
- `getRemoteChain` resolves a parent-linked layer chain into a `solver.Remote` with a multi-provider.

## Control Flow and State

Parsing uses a map from record index to already parsed record; a nil value is a recursion sentinel for loop detection. For each record, inputs are parsed first so dependency links point at concrete exporter records. Compact `Results` use `getRemoteChain`, which recursively follows `ParentIndex` through the `Layers` array and builds a remote descriptor list from parent to child. `ChainedResults` directly append listed layer descriptors in the declared order and use a multi-provider over all descriptors. Results whose provider descriptors are missing are skipped instead of failing. The reconstructed record is added to the target.

All state is in-memory and scoped to a single parse call.

## Dependencies and Integration Points

The parser depends on `cache/remotecache/v1/types`, solver cache exporter target APIs, content multi-provider helpers, and OCI descriptors. Backend importers call this parser after reading cache config from registry, local, S3, GHA, or inline image config.

## Risks and Edge Cases

Invalid record or layer indexes fail. Looping records and looping layer parent chains fail. Empty input groups are invalid. Missing providers silently remove affected results, allowing partial cache import. `getRemoteChain` mutates the returned remote while unwinding recursion and wraps prior providers in a new multi-provider for each child. Chained results do not use parent relationships and rely entirely on explicit layer order.

## Test Signals

`chains_test.go` exercises successful parsing of a simple compact result but does not assert a newly parsed graph's output. There are no tests here for invalid loops, chained results, missing providers, or malformed indexes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/types/doc.go -->
# sources/cloud-native/buildkit/cache/remotecache/v1/types/doc.go

## Purpose

This package documentation describes the v1 BuildKit distributable cache format: an OCI image index or manifest containing cache layer descriptors and one BuildKit cache config object.

## Important APIs, Types, and Functions

This file does not declare runtime APIs. It documents the JSON layout later expressed by `spec.go`: `layers` reference blobs and parent layer indexes; `records` reference cache key digests, result layer pointers, chained layer pointers, and dependency inputs.

## Control Flow and State

There is no control flow. The documented state model is persisted in remote cache backends. Cache layer descriptors require uncompressed digest annotations and may include `buildkit/createdat` to preserve timestamps. Cache records describe solver cache-key graph edges and associated remote layer chains.

## Dependencies and Integration Points

The documentation references OCI image index layout and the BuildKit cache config media type used by registry/local importers and exporters.

## Risks and Edge Cases

The comment still describes older field names such as `chains` and conceptual `layers` pointers; it should stay aligned with `spec.go` JSON tags and parser behavior. Drift here can confuse backend implementers.

## Test Signals

No tests target package documentation directly. Consistency is indirectly validated by compile-time struct tags and v1 marshal/parse tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/types/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/types/spec.go -->
# sources/cloud-native/buildkit/cache/remotecache/v1/types/spec.go

## Purpose

This file defines the serialized v1 BuildKit remote cache config schema.

## Important APIs, Types, and Functions

- `CacheConfigMediaTypeV0` is the OCI media type for BuildKit cache config blobs.
- `CacheConfig` contains `Layers` and `Records`.
- `CacheLayer` records blob digest, parent index, and optional annotations.
- `LayerAnnotations` stores media type, uncompressed diff ID, size, and creation time.
- `CacheRecord` stores result layer references, explicit chained results, cache key digest, and input links.
- `CacheResult`, `ChainedResult`, and `CacheInput` encode result and dependency references by index.

## Control Flow and State

There is no executable logic. These types are marshaled by v1 exporters, embedded inline by image exporters, stored in external cache backends, read by importers, and parsed back into solver cache records. Parent indexes in `CacheLayer` use `-1` for roots. `CacheResult.LayerIndex` refers to a top layer whose parents are loaded transitively, while `ChainedResult.LayerIndexes` lists exact layer indexes without following parents.

## Dependencies and Integration Points

The schema depends on OCI digest types and Go `time.Time`. It is consumed by all cache backends in this subset and by `remotecache/import.go` for inline cache handling.

## Risks and Edge Cases

`LayerAnnotations.CreatedAt` lacks `omitempty`, so zero times serialize as the zero timestamp when annotations are present. Index-based references require stable sorting and careful rewrites during marshal. Schema compatibility is important because remote caches may outlive the BuildKit process that produced them.

## Test Signals

`chains_test.go` checks basic `CacheConfig` field shape after marshal. There are no schema-compatibility or golden JSON tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/types/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/utils.go -->
# sources/cloud-native/buildkit/cache/remotecache/v1/utils.go

## Purpose

This file provides helper logic for deterministic cache config ordering, link key creation, remote chain marshaling, item marshaling, and sub-remote comparison.

## Important APIs, Types, and Functions

- `sortConfig` sorts layers and records and rewrites all index references to their new positions.
- `outputKey` derives per-output cache key digests from a digest and output index.
- `nlink` is the normalized internal link lookup key used by cache storage.
- `marshalState` tracks layers, descriptor providers, chain IDs, records, and item-to-record indexes while marshaling.
- `marshalRemote` converts a `solver.Remote` descriptor chain into `CacheLayer` entries and descriptor providers.
- `marshalItem` recursively emits parent records and the current item's best result.
- `isSubRemote` checks whether one remote's descriptor sequence is a prefix of another.

## Control Flow and State

`sortConfig` first sorts layers by blob digest and parent index, assigns new layer indexes, and rewrites parent indexes. It then sorts records by digest, input count, input group lengths, selectors, and input record digest, assigns new record indexes, rewrites result layer indexes and input link indexes, and sorts inputs within each input group by link index.

`marshalRemote` validates provider availability via `Info` when a provider exists, recursively marshals parent descriptors, registers the last descriptor in the descriptor map, and appends a `CacheLayer` if the descriptor chain ID is new. `marshalItem` uses `recordsByItem` as a recursion sentinel, recursively marshals parents, records input links, marshals the best result if present, and appends the cache record.

State is transient during marshal but determines persisted remote cache config bytes, so determinism matters for digest-addressed exports.

## Dependencies and Integration Points

The helpers depend on solver remotes, OCI digests, containerd error definitions, and the v1 schema types. They are called by `CacheChains.Marshal` and later consumed by cache storage and parser code.

## Risks and Edge Cases

`sortConfig` does not rewrite `ChainedResults.LayerIndexes`, so configs containing chained results could keep stale layer indexes after layer sorting. Record sorting compares input link target digests, not full recursively sorted identity, which may be insufficient for complex ties. `marshalRemote` returns an empty ID if provider info fails with anything other than not-implemented, causing a result to be skipped silently. `marshalItem` drops parents still marked `-1`, which is used to break cycles or incomplete recursion.

## Test Signals

`chains_test.go` exercises simple layer sorting, record sorting, result layer index rewrite, and parse/marshal shape. It does not cover chained result index rewrites, provider `Info` failures, complex record sort ties, or `isSubRemote` directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/remotecache/v1/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/util/fsutil.go -->
# sources/cloud-native/buildkit/cache/util/fsutil.go

## Purpose

This file provides filesystem helper functions for reading, listing, and statting files under a cache/reference root while preserving user-facing request paths in errors.

## Important APIs, Types, and Functions

- `ReadRequest` and `FileRange` describe a file read and optional byte range.
- `ReadFile` resolves a path under a root, opens it, optionally applies an `io.SectionReader`, and returns all bytes.
- `ReadDirRequest` describes a directory listing request and optional include pattern.
- `ReadDir` walks one level of a resolved directory and returns fsutil stat entries.
- `StatFile` resolves and stats one path.
- `replaceErrorPath` rewrites an `os.PathError` path inside an error chain for clearer client errors.

## Control Flow and State

All public helpers first use `fs.RootPath` to resolve the requested path safely under the root. `ReadFile` rewrites open errors so internal root paths are replaced with the request filename, then reads either the full file or the requested section. `ReadDir` builds a `fsutil.FilterOpt`, walks the resolved path, appends `*fstypes.Stat` from each entry, and skips descending into directories beyond the current level. `StatFile` wraps `fsutil.Stat` and rewrites path errors using `replaceErrorPath`.

No persistent state is created. The functions read filesystem state only.

## Dependencies and Integration Points

The helpers depend on containerd continuity `fs.RootPath`, `tonistiigi/fsutil` stat/walk types, and BuildKit callers that expose gateway or cache reference filesystem operations. They are related to gateway `ReadFile`, `ReadDir`, and `StatFile` flows exercised in client tests.

## Risks and Edge Cases

`FileRange` uses `int`, then converts to `int64`; negative offsets or lengths are not explicitly validated here and rely on `io.NewSectionReader` behavior. `ReadDir` expects every walked `FileInfo.Sys()` to be `*fstypes.Stat`, returning an error otherwise. `replaceErrorPath` mutates an error object in place, and comments acknowledge that wrapped error strings may not always update if library behavior changes.

## Test Signals

`fsutil_test.go` verifies that rewriting an `os.PathError` returned by `fsutil.Stat` changes the rendered error string. There are no direct tests here for `ReadFile`, ranged reads, `ReadDir`, or root path escape behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/util/fsutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cache/util/fsutil_test.go -->
# sources/cloud-native/buildkit/cache/util/fsutil_test.go

## Purpose

This file tests the error-path rewriting helper used by cache filesystem utilities.

## Important APIs, Types, and Functions

- `TestSetErrorPath` calls `fsutil.Stat` on a missing path, invokes `replaceErrorPath`, and asserts the error string reflects the new path.

## Control Flow and State

The test creates a temporary directory, constructs a guaranteed-missing nested path, and confirms the original error mentions that path. It then mutates the path error to `/my/new/path` and checks the original path disappears from `err.Error()` while the replacement appears.

## Dependencies and Integration Points

The test depends on `tonistiigi/fsutil` returning an error chain containing a mutable `*os.PathError`. It protects `StatFile` and `ReadFile` user-facing error reporting.

## Risks and Edge Cases

The test documents a dependency on a specific fsutil error implementation detail. If fsutil changes wrapping behavior or formats error strings eagerly, this method may stop working.

## Test Signals

The test gives focused coverage for `replaceErrorPath` only. It does not cover successful stat/read/list behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cache/util/fsutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/build.go -->
# sources/cloud-native/buildkit/client/build.go

## Purpose

This file implements the high-level client `Build` API and the build-scoped gateway client wrapper. It lets callers run a custom frontend/gateway build function inside a BuildKit solve while ensuring gateway RPCs carry the active build ID and respect negotiated capabilities.

## Important APIs, Types, and Functions

- `Client.Build` prepares frontend options, worker metadata, a gateway callback, and delegates to `c.solve`.
- `gatewayClientForBuild` wraps `gatewayapi.LLBBridgeClient` with a build ID and optional capability set.
- `GatewayClientForBuild` exposes a build-scoped gateway client for advanced callers.
- Gateway wrapper methods include `ResolveImageConfig`, `ResolveSourceMeta`, `Solve`, `ReadFile`, `ReadDir`, `StatFile`, `Evaluate`, `Ping`, `Return`, `Inputs`, container lifecycle, container filesystem, `ExecProcess`, and `Warn`.

## Control Flow and State

`Build` always closes `statusChan` when it returns. It captures frontend attrs, clears `opt.Frontend` so the custom build function drives the frontend, defaults the product string, and lists workers to pass worker metadata into the gateway client. The callback passed to `solve` merges frontend options from the daemon into the caller's frontend attrs, constructs a gateway client scoped to the build reference, creates a grpc gateway frontend client, stores negotiated capabilities on the wrapper, and runs the caller's `buildFunc`.

Every gateway RPC appends the build ID to outgoing gRPC metadata through `buildid.AppendToOutgoingContext`. Some methods check capabilities before making the RPC. `Evaluate` has a compatibility fallback: when `CapGatewayEvaluate` is missing but `CapStatFile` exists, it uses `StatFile` on `.` to force evaluation and returns an empty evaluate response.

State is mostly per-call. The wrapper holds the build ID and a pointer to negotiated capabilities.

## Dependencies and Integration Points

This API integrates the public client package, gateway frontend client, gRPC bridge protobuf API, build ID metadata helpers, session handling, API capability sets, worker listing, and the lower-level `solve` method defined elsewhere. It is heavily exercised by gateway integration tests in `build_test.go`.

## Risks and Edge Cases

`feOpts` points to `opt.FrontendAttrs` and is mutated by `maps.Copy`, so caller-provided maps can be modified. `Build` calls `ListWorkers` before running the build function; worker-list failure prevents custom frontend execution. Capability checks are wrapper-side and must be updated as new gateway methods are added. The `Warn` method ignores variadic call options when forwarding, unlike most other methods.

## Test Signals

`build_test.go` validates successful gateway solve, build option propagation, missing/unknown build ID behavior, warnings, gateway filesystem and container APIs, capability-gated paths, and many failure/release scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/build_test.go -->
# sources/cloud-native/buildkit/client/build_test.go

## Purpose

This file is a broad integration test suite for the client gateway build API and gateway container/debug APIs. It validates custom frontend execution, build ID scoping, warnings, result handling, container lifecycle, exec and TTY behavior, mounts, secrets, error debugging, entitlements, networking, credential cancellation, and empty-result/image edge cases.

## Important APIs, Types, and Functions

- `TestClientGatewayIntegration` registers the main Linux gateway integration matrix.
- Gateway solve tests: `testClientGatewaySolve`, `testWarnings`, `testClientGatewayFailedSolve`, `testClientGatewayEmptySolve`, `testNoBuildID`, and `testUnknownBuildID`.
- Container lifecycle and exec tests: `testClientGatewayContainerCancelOnRelease`, pipe tests, PID1 failure/exit tests, TTY tests, signal tests, and `testPrompt`.
- Mount/secret/platform tests: `testClientGatewayContainerMounts`, `testClientGatewayContainerSecretEnv`, and `testClientGatewayContainerPlatformPATH`.
- Debug/error tests: `testClientSlowCacheRootfsRef`, `testClientGatewayExecError`, `testClientGatewaySlowCacheExecError`, and `testClientGatewayExecFileActionError`.
- Entitlement/network tests: security mode and host networking variants.
- Registry/auth edge test: `testClientGatewayCanceledCredentialsCallbackReturns` with `blockingAuthProvider`.
- Result edge tests: `testClientGatewayNilResult` and `testClientGatewayEmptyImageExec`.

## Control Flow and State

The suite creates BuildKit clients against integration sandboxes, then invokes `Client.Build` with custom gateway build functions. The basic solve test checks product and frontend attrs, solves an LLB graph, reads the result through the gateway ref, exports locally, and checks final content. Warning tests capture status messages and verify warning fields including source info, ranges, detail, URL, and level.

Container tests solve `busybox`, create gateway containers with bind/cache/tmpfs/secret/SSH/local mounts, start PID1 and exec processes, pipe stdio, resize TTYs, send signals, release containers, and verify cancellation/resource cleanup through `checkAllReleasable`. Debug tests intentionally fail solve operations and use returned `SolveError` mount/input IDs to recreate containers over failed exec or file-operation refs and inspect intermediate filesystem state.

Entitlement tests run the same container API with security and network modes while toggling allowed entitlements, expecting success or explicit validation errors. The credential cancellation test sets up a registry proxy and a blocking auth session provider to ensure canceled image config resolution does not remain stuck behind credentials callbacks. Edge tests cover nil results from merge-diff and executing from an intentionally empty pushed image.

State includes temporary directories, local session mounts, SSH agent sockets, secret providers, registry fixtures, HTTP proxy fixtures, and interactive pipe buffers. All state should be released by each test through client close, container release, process wait, and integration cleanup.

## Dependencies and Integration Points

The suite depends on the public `client` package, gateway client interfaces, LLB builders, solver error definitions, protobuf mount/security/network types, session auth/secrets/SSH providers, fsutil local mounts, integration worker feature gates, mirrored images, registry fixtures, echoserver fixtures, gRPC status helpers, and Linux process semantics.

## Risks and Edge Cases

The tests are integration-heavy and Linux-centric; many skip outside Linux or without feature gates. TTY tests use prompt polling and fixed timeouts, which can be sensitive to slow workers. Host networking tests are disabled unless `BUILDKIT_RUN_NETWORK_INTEGRATION_TESTS` is set. Several tests intentionally return errors from build functions and assert the outer build error, so cleanup paths are as important as success paths. The auth cancellation test has a deliberately blocking provider and time-based fallback, making it useful for deadlock detection but sensitive to timing.

## Test Signals

This file is the primary behavioral signal for `client/build.go` and a broad regression suite for gateway APIs. It validates build ID metadata routing, capability gating, warning propagation, filesystem reads/stats, container process semantics, entitlement enforcement, debug ref reconstruction, and release hygiene.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/build_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/buildid/metadata.go -->
# sources/cloud-native/buildkit/client/buildid/metadata.go

## Purpose

This file defines the gRPC metadata key and helpers used to route gateway API calls to the active BuildKit build job.

## Important APIs, Types, and Functions

- `metadataKey` is `buildkit-controlapi-buildid`.
- `AppendToOutgoingContext` appends the build ID to outgoing gRPC metadata when non-empty.
- `FromIncomingContext` extracts exactly one build ID value from incoming gRPC metadata.

## Control Flow and State

The client-side gateway wrapper calls `AppendToOutgoingContext` before every gateway RPC. Server-side handlers can call `FromIncomingContext` to recover the target job. If no metadata exists, no IDs are present, or multiple IDs are present, extraction returns an empty string.

No persistent state is stored; build ID travels with each gRPC request.

## Dependencies and Integration Points

The helpers depend on `google.golang.org/grpc/metadata`. They are integrated by `client/build.go` and tested indirectly by gateway tests that call the bridge with missing or unknown build IDs.

## Risks and Edge Cases

`AppendToOutgoingContext` appends rather than replaces. If a context already contains the same metadata key, `FromIncomingContext` will see multiple values and return empty. This is a deliberate strictness but can surprise callers that reuse contexts. Empty build IDs are silently omitted.

## Test Signals

`build_test.go` verifies that direct gateway calls without build ID fail with "no buildid found in context" and that random unknown IDs return a not-found error. There are no direct unit tests for duplicate metadata values.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/buildid/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/client.go -->
# sources/cloud-native/buildkit/client/client.go

## Purpose

This file implements construction and core plumbing for the BuildKit client: gRPC connection setup, credentials, tracing, dialer resolution, service accessors, readiness waiting, session dialing, and client options.

## Important APIs, Types, and Functions

- `Client` holds the gRPC connection and optional custom session dialer.
- `New` builds a client connection from an address and `ClientOpt` values.
- Service accessors: `ControlClient`, `ContentClient`, and `Dialer`.
- Lifecycle methods: `Wait` and `Close`.
- Client options include `WithContextDialer`, `WithCredentials`, `WithServerConfig`, `WithServerConfigSystem`, `WithTracerProvider`, `WithTracerDelegate`, `WithSessionDialer`, and `WithGRPCDialOption`.
- `loadCredentials` builds TLS transport credentials.
- `resolveDialer` maps connection-helper schemes to custom dialers.

## Control Flow and State

`New` starts with large default gRPC message sizes, scans options, merges TLS credential options, installs a custom context dialer or resolves one from the address, and configures tracing from explicit options or an existing span in the input context. It appends BuildKit gRPC error interceptors, optional custom dial options, and authority metadata. Empty addresses default to `appdefaults.Address`; `tcp://` addresses are converted to host form for grpc-go name resolution. It then dials and optionally sets up delegated tracing.

`loadCredentials` constructs a TLS config from system roots and/or a CA file, applies server name, and loads a client key pair when either cert or key is provided. `Wait` polls the control API `Info` endpoint until success, `Unimplemented`, context cancellation, or a non-retryable error. `Dialer` returns a hijacked session dialer over the control service.

Persistent state is the open gRPC connection and configured session dialer on the client object.

## Dependencies and Integration Points

The file depends on containerd defaults and content API, BuildKit control API, connection helpers, session hijacking, app defaults, tracing/OTLP plumbing, OpenTelemetry gRPC stats handlers, TLS/x509, and gRPC credentials/interceptors. Higher-level methods such as `Build`, `Solve`, `DiskUsage`, and cache operations all depend on clients created here.

## Risks and Edge Cases

`grpc.DialContext` is used despite deprecation warnings because behavior differs from newer APIs. Authority handling must align with TLS server name and address parsing. Supplying only cert or only key attempts to load both and returns a credential error. `Wait` treats `Unimplemented` as success for older BuildKit daemons. Tracer setup failure is ignored by design. Option merging allows later credential options to override earlier fields selectively.

## Test Signals

No direct tests for `client.go` are included in this subset. It is exercised indirectly by every integration test that calls `New`, `Wait`, service accessors, or `Close`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/client_cdi_test.go -->
# sources/cloud-native/buildkit/client/client_cdi_test.go

## Purpose

This file tests BuildKit client/LLB integration with CDI devices. It verifies device injection, allow/deny behavior, entitlement-based access, shorthand device selection, wildcard selection, class selection, and CDI spec discovery refresh.

## Important APIs, Types, and Functions

- `cdiTests` lists CDI integration test functions for registration elsewhere.
- `testCDI`, `testCDINotAllowed`, `testCDIEntitlement`, `testCDIFirst`, `testCDIWildcard`, and `testCDIClass` cover CDI behavior variants.
- `cdiSpecFile` describes a temporary CDI spec fixture.
- `writeCDISpecFile` atomically writes CDI spec YAML files and waits for workers to report matching devices.

## Control Flow and State

Each test skips rootless and Windows, requires `FeatureCDI`, creates a client, writes one or more CDI spec files into the sandbox's CDI spec directory, and builds an LLB graph that requests CDI devices via `llb.AddCDIDevice`. Tests export local output files containing environment variables injected by CDI container edits, then assert expected variables are present or absent.

`testCDI` uses autoallowed devices from two vendors plus an optional missing device. `testCDINotAllowed` omits autoallow and expects a denial. `testCDIEntitlement` grants `device=vendor1.com/device` and expects success. `testCDIFirst` requests a kind without a name and expects the first selected device behavior expressed by current CDI ordering. `testCDIWildcard` requests all devices of a kind. `testCDIClass` requests devices by class annotation.

`writeCDISpecFile` writes files using `continuity.AtomicWriteFile`, records expected kinds, and polls `ListWorkers` until reported CDI devices include all kinds or a timeout expires.

## Dependencies and Integration Points

The tests depend on CDI spec YAML semantics, BuildKit LLB CDI device options, worker CDI discovery and caching, integration sandbox CDI directories, local export, `ListWorkers`, and feature-gated worker capabilities.

## Risks and Edge Cases

Spec discovery is asynchronous, so the helper uses polling with a five-second deadline. Rootless and Windows skips mean behavior there is not covered. Autoallow depends on BuildKit-specific `org.mobyproject.buildkit.device.autoallow` annotations. The "first" selection test encodes current ordering expectations and could be sensitive to CDI library ordering changes.

## Test Signals

These tests provide the CDI-specific signal for client solves and worker device reporting. They do not directly test gateway container APIs, but they verify LLB solve behavior through the public client.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/client_cdi_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/client_nydus_test.go -->
# sources/cloud-native/buildkit/client/client_nydus_test.go

## Purpose

This build-tagged test file validates image export behavior when Nydus compression is enabled. It ensures Nydus layers are produced with expected annotations and are not mixed incorrectly with gzip or zstd compressed layers across repeated exports.

## Important APIs, Types, and Functions

- Build tag `nydus` gates compilation.
- `init` appends `testBuildExportNydusWithHybrid` to the shared integration test list.
- `testBuildExportNydusWithHybrid` builds and pushes images with Nydus, gzip, and zstd compression and inspects stored manifests.

## Control Flow and State

The test requires direct push support, Linux, and a containerd worker address. It creates a containerd client, a registry fixture, and a BuildKit client. Helper `buildNydus` builds an Alpine-derived image that touches a file, exports it as an image with `compression=nydus`, OCI media types, push, and forced compression, then reads the pushed image manifest from containerd. It asserts there are three layers and checks Nydus blob/bootstrap annotations. Helper `buildOther` repeats the flow for gzip or zstd and asserts two layers with the expected OCI media type.

The sequence builds Nydus, gzip, zstd for one file and gzip, zstd, Nydus for another, guarding against cross-build compression cache contamination.

## Dependencies and Integration Points

The test depends on containerd image/content services, nydus snapshotter converter annotations, BuildKit image exporter compression options, registry fixtures, LLB image/run construction, and integration worker feature gates.

## Risks and Edge Cases

The test is only compiled with the `nydus` build tag and requires containerd, a registry fixture, and direct push. It inspects manifests from the containerd namespace `buildkit`, so namespace or image-service changes can affect it. It validates manifest shape and annotations, not runtime mountability of the resulting Nydus image.

## Test Signals

This is the subset's signal for Nydus export compression isolation. It indirectly exercises the client solve/export path and cache/compression behavior across sequential builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/client_nydus_test.go -->
