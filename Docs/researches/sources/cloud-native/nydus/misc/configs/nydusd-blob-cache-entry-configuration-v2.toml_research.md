<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry-configuration-v2.toml -->
# sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry-configuration-v2.toml

## Purpose

This sample TOML documents a version 2 Nydus image service configuration for a blob-cache entry with metadata blob path support.

## Important APIs, Types, and Functions

Top-level fields include `version = 2`, `id`, and `metadata_path`. It defines localfs, OSS, and registry backend examples, proxy settings, filecache/fscache/cache prefetch settings, encryption options, and bandwidth/thread limits.

## Control Flow

The file is declarative. Nydusd config loading selects the active backend by `backend.type` and active cache by `cache.type`; other backend sections are examples unless selected.

## State and Persistence Behavior

Configured paths point to local blob data, alternate cache directories, metadata blobs, and cache work directories. Credentials and encryption keys appear as placeholders but would be sensitive in real configs.

## Dependencies and Integration Points

It targets Nydus `ConfigV2` parsing and blob-cache entry runtime behavior. Proxy fields align with Dragonfly or HTTP proxy integration.

## Risks and Test Signals

The file contains a likely typo section `[backend.registy]` while proxy uses `[backend.registry.proxy]`, which may confuse users or be ignored by parsers. As a sample, correctness is validated only indirectly by config parser tests or manual nydusd startup.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry-configuration-v2.toml -->
