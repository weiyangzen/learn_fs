<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-nofallback.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-nofallback.json

## Purpose

This nydusd config models a proxy error scenario where fallback is disabled.

## Important APIs, Types, and Functions

It is similar to the fallback variant but sets `fallback: false`, uses `use_http: true`, disables fs prefetch, and stores cache under `/tmp/nydus-proxy-error-nofallback-test/cache/`.

## Control Flow

Registry blob reads are routed through the local proxy. Proxy errors should propagate instead of falling back to the source registry.

## State and Persistence Behavior

Cache state is isolated to the no-fallback error directory. Digest validation and cache validation are enabled.

## Dependencies and Integration Points

It is an E2E fixture for Dragonfly proxy error handling and nydusd registry backend fallback policy.

## Risks and Test Signals

This config should fail when proxy access fails, so test harnesses must ensure the intended proxy error is produced. Skip-verify and fixed GHCR image paths are test-only choices.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-nofallback.json -->
