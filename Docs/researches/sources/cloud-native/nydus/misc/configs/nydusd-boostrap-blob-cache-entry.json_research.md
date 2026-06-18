<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-boostrap-blob-cache-entry.json -->
# sources/cloud-native/nydus/misc/configs/nydusd-boostrap-blob-cache-entry.json

## Purpose

This JSON sample defines a bootstrap blob-cache entry for localfs-backed metadata and fscache caching.

## Important APIs, Types, and Functions

Fields include top-level `type`, `id`, `domain_id`, and nested `config` with `id`, `backend_type`, `backend_config.dir`, `cache_type`, `cache_config.work_dir`, and `metadata_file`.

## Control Flow

There is no procedural logic. Consumers parse the entry and use the nested config to locate local blobs, cache data, and metadata.

## State and Persistence Behavior

The sample references `/tmp/nydus` for backend/cache data and `/tmp/nydus/bootstrap1` for metadata. It models persisted cache entry identity and paths.

## Dependencies and Integration Points

It integrates with older or JSON-based blob-cache entry configuration paths in nydusd tooling.

## Risks and Test Signals

The filename contains `boostrap`, likely preserving an existing typo. The sample uses tmp paths and should not be treated as production persistence. There are no direct tests for this specific file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-boostrap-blob-cache-entry.json -->
