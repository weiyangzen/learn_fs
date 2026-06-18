<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry.toml -->
# sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry.toml

## Purpose

This sample TOML describes a bootstrap blob-cache entry wrapping a nested version 2 Nydus configuration under `config_v2`.

## Important APIs, Types, and Functions

Top-level `type = "bootstrap"`, `id`, and `domain_id` identify the cache entry. Nested `[config_v2]` mirrors Nydus config v2 with metadata path, backend localfs/OSS/registry/proxy settings, cache settings, and cache prefetch controls.

## Control Flow

The file is loaded declaratively by consumers that understand bootstrap entry documents. The runtime selects backend/cache sections based on nested type fields.

## State and Persistence Behavior

It points to metadata blob paths, local blob files, cache work directories, and optional proxy endpoints. In real deployments, it persists domain-specific cache entry identity.

## Dependencies and Integration Points

It integrates with blob cache entry parsing and Nydus image service config v2. The top-level wrapper differs from plain `ConfigV2` files and is intended for cache entry/bootstrap management.

## Risks and Test Signals

Like the v2 sample, it includes a `[config_v2.backend.registry]` section here, avoiding the typo seen in the other sample. Placeholder credentials and broad encryption examples should not be copied into production without replacement. Validation is mostly by parser/runtime loading.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry.toml -->
