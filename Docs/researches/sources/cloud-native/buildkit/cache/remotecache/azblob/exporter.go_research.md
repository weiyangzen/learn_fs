# sources/cloud-native/buildkit/cache/remotecache/azblob/exporter.go

## Purpose

`azblob/exporter.go` implements BuildKit remote cache export to Azure Blob Storage. It serializes BuildKit cache chains, uploads missing layer blobs to Azure by content digest, writes cache manifests for configured names, and exposes the `remotecache.Exporter` interface.

## Important APIs, Types, and Functions

- `ResolveCacheExporterFunc` returns the resolver used by BuildKit to create an Azure Blob cache exporter from attrs/session context.
- `exporter` embeds `solver.CacheExporterTarget`, stores `v1.CacheChains`, Azure container client, and parsed config.
- `Name` returns a progress/display string.
- `Finalize` marshals cache chains, uploads blobs, enriches layer annotations, uploads manifests, and returns no extra metadata.
- `Config` returns default compression config for this backend.
- `uploadManifest` writes manifest bytes with Azure `Upload`, using last-writer-wins semantics.
- `uploadBlobIfNotExists` writes layer blobs with `UploadStream` and `IfNoneMatch: *` so content-addressed blobs are uploaded only if absent.
- `bytesToReadSeekCloser` adapts manifest bytes for Azure upload APIs.

## Control Flow

The resolver parses config with `getConfig`, creates or verifies the Azure container, creates a new v1 cache chain target, and returns an exporter. On `Finalize`, the exporter marshals chains into a cache config and descriptor/provider pairs. For each cache layer, it validates descriptor annotations, extracts the uncompressed diff ID, checks if the target blob key already exists, uploads missing content from the descriptor provider, then stores cache import annotations containing diff ID, size, media type, and created-at timestamp. After the config is updated, it is marshaled and uploaded once per configured cache name under the manifest prefix.

## State and Persistence Behavior

Layer blobs are persisted in Azure under `blobKey(config, digest)`. Manifests are persisted under `manifestKey(config, name)` and overwrite prior manifests for the same name. The exporter does not store local state beyond the cache chains accumulated through the embedded solver export target. Blob uploads are idempotent by digest; manifest writes are intentionally last-writer-wins.

## Dependencies and Integration Points

The file uses Azure SDK block blob/container clients, blob access conditions, BuildKit remotecache v1 chain serialization, cache import type annotations, session and solver interfaces, progress, compression defaults, containerd content readers, and OCI digests. It relies on `utils.go` for config, clients, paths, and existence checks.

## Risks and Edge Cases

- `Finalize` requires uncompressed annotations on every descriptor; missing annotations abort export.
- Layer upload and manifest upload use fixed five-minute timeouts, which may be too short for very large layers or slow networks.
- Blob existence check before upload is an optimization, but concurrent exporters are still handled by `IfNoneMatch` and BlobAlreadyExists.
- Manifests are uploaded sequentially for all names.
- Created-at parsing errors abort the export.

## Test Signals

No Azure-specific tests are in this subset. Generic remote-cache and manager tests cover descriptor annotations and cache chain construction indirectly; live Azure behavior would need integration tests or mocked Azure clients.
