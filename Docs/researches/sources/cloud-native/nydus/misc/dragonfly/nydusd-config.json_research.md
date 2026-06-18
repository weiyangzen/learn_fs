<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-config.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-config.json

## Purpose

This nydusd JSON config exercises registry access through a Dragonfly proxy with fallback enabled and filesystem prefetch enabled.

## Important APIs, Types, and Functions

It targets `ghcr.io/dragonflyoss/image-service/nginx`, uses HTTPS with skip-verify, sets proxy URL and ping URL to local dfdaemon port 4001, enables fallback, configures blobcache under `/tmp/nydus-test/cache/`, enables digest validation/xattrs, and configures `fs_prefetch`.

## Control Flow

At runtime, nydusd attempts blob reads through the proxy and may fall back to the registry when proxy health fails. Prefetch uses 10 threads, 128 KiB merging size, and a 1 MiB/s bandwidth rate.

## State and Persistence Behavior

Blob cache persists under `/tmp/nydus-test/cache/`. The config validates cache data and filesystem digests.

## Dependencies and Integration Points

It integrates with Dragonfly dfdaemon local proxy and GHCR registry image fixtures.

## Risks and Test Signals

Skip-verify is enabled for testing. The config depends on network availability, GHCR content, and local proxy health. It signals fallback behavior in E2E tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-config.json -->
