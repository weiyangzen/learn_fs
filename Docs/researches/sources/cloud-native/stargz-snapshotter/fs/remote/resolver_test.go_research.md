# sources/cloud-native/stargz-snapshotter/fs/remote/resolver_test.go

## Purpose
Tests HTTP fetcher resolution against registry mirrors, redirects, headers, check behavior, and retryable transport configuration.

## Important APIs, Types, And Functions
`TestMirror` is the main resolver matrix. `checkFetcherURL` validates selected hosts. `sampleRoundTripper` simulates success, error status codes, redirects, and expected headers. `TestCheck` exercises `httpFetcher.check`; `TestRetry` verifies retryablehttp integration. `hostSimple`, `hostWithHeaders`, and `hostsConfig` build `source.RegistryHosts` fixtures.

## Control Flow
Tests construct a dummy reference and digest, then invoke `newHTTPFetcher` with configured mirrors. The fake transport validates custom headers, returns redirect locations or status codes per URL pattern, and provides content lengths for size detection. After resolution, tests call `check` and `refreshURL` to ensure the selected host remains consistent.

## State And Persistence
No persistence. State consists of fake transport maps and retry counters.

## Dependencies And Integration
Depends on containerd `reference`, Docker registry host structs, retryablehttp, OCI descriptors, and the production resolver internals. It specifically validates integration with `source.RegistryHosts` ordering and per-host headers.

## Risks And Test Signals
Signals include fallback from bad mirrors to good mirrors or origin, rejection of invalid mirror hostnames, redirect host selection, preservation of headers to registry but not redirected backend, check behavior, and retry count across transient failures. It does not exercise real TLS, authentication token exchange, or actual registry behavior.
