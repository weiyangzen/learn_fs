<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-config.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-config.json

## Purpose

This nydusd config tests Dragonfly SDK integration through a proxy with scheduler endpoint and no fallback.

## Important APIs, Types, and Functions

It targets `ghcr.io/dragonflyoss/image-service/java`, configures proxy URL/ping URL to dfdaemon, includes `dragonfly_scheduler_endpoint: http://127.0.0.1:8002`, disables fallback, enables fs prefetch, and uses blobcache under `/tmp/nydus-sdk-test/cache/`.

## Control Flow

Nydusd registry backend uses Dragonfly proxy/SDK settings to coordinate downloads through the local scheduler. Without fallback, SDK/proxy failures should surface.

## State and Persistence Behavior

Cached blobs live under the SDK test cache directory. Prefetch can populate cache proactively.

## Dependencies and Integration Points

It integrates with local Dragonfly scheduler, manager, dfdaemon, and the Java GHCR fixture image.

## Risks and Test Signals

The config depends on all local Dragonfly components plus network access. It is useful for validating scheduler-aware proxy behavior and prefetch interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-config.json -->
