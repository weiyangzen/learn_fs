<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-fallback-config.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-fallback-config.json

## Purpose

This nydusd config tests Dragonfly SDK/proxy integration with fallback enabled.

## Important APIs, Types, and Functions

It targets the Java fixture image, sets local proxy and scheduler endpoint, enables `fallback: true`, disables fs prefetch, and stores cache under `/tmp/nydus-sdk-fallback-test/cache/`.

## Control Flow

Nydusd may use the Dragonfly scheduler/proxy path but can return to direct registry access if the proxy path is unavailable.

## State and Persistence Behavior

Cache state is isolated under the SDK fallback directory. Digest and cache validation are enabled.

## Dependencies and Integration Points

It integrates with local Dragonfly scheduler/dfdaemon and registry backend fallback paths.

## Risks and Test Signals

Fallback can hide SDK/proxy failures unless tests assert which path served data. This fixture is intended to contrast with the no-fallback SDK config.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-fallback-config.json -->
