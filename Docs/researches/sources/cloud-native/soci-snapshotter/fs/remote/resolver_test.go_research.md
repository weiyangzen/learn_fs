# sources/cloud-native/soci-snapshotter/fs/remote/resolver_test.go

Purpose: validates remote HTTP resolver behavior around mirror selection, connectivity checks, retry handling, user-agent propagation, layer-size parsing, and header fallback.

Important APIs and flow: `TestMirror` builds registry host lists with optional mirrors and a sample round tripper to ensure `newHTTPFetcher` selects the first usable mirror or falls back to the original host, handles invalid mirror hostnames, observes redirects, and errors when all hosts fail. `TestCheck` verifies `httpFetcher.check` status handling. `TestRetry` wraps a fake transport in retryablehttp and expects retries through transient errors/statuses. `TestCustomUserAgent` verifies `socihttp.AuthClient` attaches global User-Agent headers during fetch. `TestParseSize` covers 200 `Content-Length`, 206 `Content-Range`, and unsupported status. `TestGetHeader` confirms HEAD success and HEAD failure followed by GET success.

State and persistence: fake round trippers and in-memory HTTP responses only. No real registry traffic.

Dependencies and integration: exercises `newHTTPFetcher`, `fetch`, `check`, `ParseSize`, `GetHeader`, `socihttp.AuthClient`, retryablehttp, Docker registry host configuration, and reference parsing.

Risks and test signals: strong coverage for resolver decision logic and HTTP shape handling. It does not test URL refresh after 401/403 in `fetch`, bad `Content-Type` multipart parsing, custom handler resolution, or auth-client retry option cloning.
