<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-fallback.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-fallback.json

## Purpose

This nydusd config models a proxy error scenario where fallback to the source registry is allowed.

## Important APIs, Types, and Functions

It targets the nginx fixture image, sets proxy URL to local port 4001, enables `fallback: true`, uses `use_http: true`, lengthens proxy health check interval to 300 seconds, disables fs prefetch, and stores cache under `/tmp/nydus-proxy-error-fallback-test/cache/`.

## Control Flow

Nydusd first attempts proxy-based reads and may fall back to direct registry access when proxy operations fail.

## State and Persistence Behavior

Blob cache is isolated to the fallback error test directory. Registry requests are unauthenticated and skip TLS verification.

## Dependencies and Integration Points

It integrates with Dragonfly proxy error E2E tests and registry backend fallback code paths.

## Risks and Test Signals

The config intentionally tolerates proxy failure, so tests must distinguish successful fallback from healthy-proxy success. Long check intervals can preserve stale proxy state during tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-fallback.json -->
