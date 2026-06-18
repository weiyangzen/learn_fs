<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-http-proxy-nofallback-config.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-http-proxy-nofallback-config.json

## Purpose

This nydusd config tests local Dragonfly HTTP proxy access without fallback to the source registry.

## Important APIs, Types, and Functions

It uses a registry backend for `ghcr.io/dragonflyoss/image-service/nginx`, proxy URL/ping URL `http://127.0.0.1:4001`, `fallback: false`, blobcache under `/tmp/nydus-http-proxy-nofallback-test/cache/`, digest validation, xattrs, and disabled filesystem prefetch.

## Control Flow

Nydusd routes registry blob access through the proxy. If the proxy is unhealthy or fails, no fallback path is allowed, so reads should fail.

## State and Persistence Behavior

Cache data is isolated under the no-fallback test cache directory. No persistent registry credentials are configured.

## Dependencies and Integration Points

It integrates with Dragonfly dfdaemon as an HTTP proxy and is useful for E2E assertions that proxy failures surface as runtime errors.

## Risks and Test Signals

The config intentionally makes availability depend on the proxy. Skip-verify remains enabled for test convenience.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-http-proxy-nofallback-config.json -->
