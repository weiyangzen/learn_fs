<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-config.json -->
# sources/cloud-native/nydus/misc/configs/nydusd-config.json

## Purpose

This JSON sample provides a nydusd runtime configuration using a registry backend and blobcache.

## Important APIs, Types, and Functions

The JSON defines `device.backend.type = "registry"` with timeout, connect timeout, retry limit, skip-verify, and CA certificate file fields; `device.cache.type = "blobcache"` with work dir; and filesystem options including direct mode, digest validation, xattrs, iostats, and `fs_prefetch`.

## Control Flow

Nydusd reads this declarative config at startup. Backend host/repo are absent here, suggesting they are supplied externally or via snapshotter annotations.

## State and Persistence Behavior

Cache data is stored under `/var/lib/nydus/cache`. The config enables prefetch and extended attributes but disables digest validation and per-file IO stats.

## Dependencies and Integration Points

It integrates with nydusd JSON config loading and registry backend runtime configuration. The CA path option aligns with TLS trust customization.

## Risks and Test Signals

Missing registry host/repo fields make it a partial config for contexts that inject backend source dynamically. There are no direct tests for this sample.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-config.json -->
