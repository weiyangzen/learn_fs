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
