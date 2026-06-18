# sources/cloud-native/nydus/api/src/config.rs

## Purpose
This module defines Nydus daemon, backend, cache, RAFS, prefetch, proxy, overlay, and blob-cache configuration models. It parses current v2 JSON/TOML config, accepts selected legacy JSON formats, validates combinations, converts legacy structures into v2, and provides helpers for secret scrubbing and runtime flags.

## Important APIs, Types, and Functions
- `ConfigV2` is the top-level v2 config with `version`, `id`, optional `backend`, `external_backends`, optional `cache`, optional `rafs`, optional `overlay`, and skipped runtime `internal`.
- `ConfigV2::new`, `new_localfs`, `from_file`, `validate`, accessors, `clone_without_secrets`, `is_chunk_validation_enabled`, `is_fs_cache`, and `update_registry_auth_info` are the main user APIs.
- `BackendConfigV2` supports `localdisk`, `localfs`, `oss`, `s3`, `registry`, and `http-proxy` backend types and exposes typed getters.
- `CacheConfigV2` supports `blobcache`/`filecache`, `fscache`, `dummycache`, prefetch settings, and typed cache getters.
- `FileCacheConfig::get_work_dir` and `FsCacheConfig::get_work_dir` create missing cache dirs and reject non-directories.
- `RafsConfigV2`, `PrefetchConfigV2`, and `ProxyConfig` carry filesystem mode, validation, IO batching, metrics flags, prefetch concurrency/bandwidth, and Dragonfly/proxy health settings.
- `BlobCacheEntryConfigV2`, `BlobCacheEntry`, and `BlobCacheList` model cached bootstrap/datablob objects, domain isolation, legacy config compatibility, and metadata paths.
- Legacy-only structs `BackendConfig`, `CacheConfig`, `FactoryConfig`, `RafsConfig`, `FsPrefetchControl`, `BlobPrefetchConfig`, and `BlobCacheEntryConfig` provide conversion routes.

## Control Flow
Parsing first tries `serde_json::from_str::<ConfigV2>`, then TOML `ConfigV2`, then legacy JSON `RafsConfig` converted to `ConfigV2`. Blob cache entry config parsing separately tries JSON then TOML. Validation checks version, backend type and required fields, cache type and work dirs, RAFS mode and batch/thread limits, and blob type. Legacy conversion maps generic `Value` payloads into typed backend/cache structs based on `type` strings. Runtime callers fetch typed subconfigs using getters that distinguish wrong type from missing subconfig.

## State and Persistence
`from_file` reads config files up to 1 MiB. Cache `get_work_dir` helpers may create directories on disk, which is the module's main side effect. `ConfigV2Internal` stores a shared atomic `blob_accessible` runtime probe flag that is skipped during serialization and compared by loaded value. Secret scrubbing clones configs and removes OSS access keys and registry auth/token fields.

## Dependencies and Integration Points
The module depends on serde, serde_json, toml, `std::fs`, `std::io`, `log`, and atomics. It feeds Nydus daemon startup, backend construction, blob cache management APIs, snapshotter-generated configs, Dragonfly proxy settings, and tests in this crate.

## Risks and Edge Cases
- `clone_without_secrets` clears OSS and registry secrets only on the primary backend; S3 access keys and `external_backends` may still carry sensitive values.
- `FileCacheConfig::get_work_dir` and `FsCacheConfig::get_work_dir` mutate the filesystem while looking like accessors.
- Validation accepts empty/no-op cache type and optional backend/cache/rafs sections; callers must enforce their own required sections.
- HTTP proxy validation requires an absolute existing Unix socket path when using a socket, so configs can fail validation before the socket is created.
- Multiple legacy and v2 representations increase drift risk.
- The 1 MiB file limit protects against oversized configs but can reject large generated configs.

## Test Signals
The module has extensive unit tests covering default values, backend/cache/RAFS TOML parsing, OSS/S3/registry/localfs/localdisk/proxy configs, legacy conversion, v2 blob cache parsing, from-file behavior, validation failures, getter error kinds, secret scrubbing, chunk validation logic, fscache detection, and prefetch defaults. CI runs these through workspace unit tests, nextest, Miri, smoke, and coverage workflows.
