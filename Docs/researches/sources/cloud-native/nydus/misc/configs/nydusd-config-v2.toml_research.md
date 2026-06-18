<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-config-v2.toml -->
# sources/cloud-native/nydus/misc/configs/nydusd-config-v2.toml

## Purpose

This sample TOML documents the standard Nydus image service config v2 shape, covering backend, cache, RAFS, and prefetch settings.

## Important APIs, Types, and Functions

It defines version/id, localfs/OSS/registry backends with proxy options, filecache/fscache settings, encryption options, cache prefetch, RAFS mode/validation/xattr/stat/access-pattern settings, and RAFS prefetch controls.

## Control Flow

Nydusd's config parser selects active backend and cache by type. RAFS `mode = "direct"` and prefetch options guide mount-time filesystem behavior and data-fetch policy.

## State and Persistence Behavior

The config stores local blob paths, cache directories, network backend credentials, encryption key placeholders, and runtime validation/prefetch behavior. These settings directly influence nydusd cache persistence and remote access.

## Dependencies and Integration Points

It maps to `nydus_api::ConfigV2` used by `rafs::Rafs::new`, blobfs, and nydusd. Proxy fields match Dragonfly and HTTP proxy integration points.

## Risks and Test Signals

The sample has `[backend.registy]` typo while proxy uses `[backend.registry.proxy]`, creating a risk that registry examples are not loadable as written. Placeholder secrets and skip-verify examples require production hardening. Validation is through config parser/runtime tests rather than this file itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-config-v2.toml -->
