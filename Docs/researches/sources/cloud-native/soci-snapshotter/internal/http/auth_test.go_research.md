# sources/cloud-native/soci-snapshotter/internal/http/auth_test.go

Purpose: unit tests for the authenticated HTTP client wrapper.

Important APIs/types/functions: test doubles include `authRoundTripper`, `basicAuthHandler`, `policyAuthHandler`, `statusRoundTripper`, `headerRoundTripper`, `emptyAuthHandler`, `SimpleMockAuthClient`, and `redirectRoundTripper`. Tests are `TestAuthHandler`, `TestCustomAuthPolicy`, `TestCustomAuthHeaders`, and `TestRedirectCacheSetsRefererHeader`.

Control flow: tests wire a retryable client with a fake transport, create an `AuthClient`, issue requests, and assert second-round authorization, policy invocation count, headers, or redirect target/referer. The basic auth flow simulates first 401 then a second request with credentials obtained during challenge handling.

State and persistence: fake handlers store credentials or auth counts in memory. Redirect tests enable `CacheRedirects(true)` and use two requests to prove cache population then reuse.

Dependencies/integration points: uses base64-encoded basic auth, retryablehttp, and Go request/response primitives. It exercises `AuthClient.Do` but not real network or Docker auth.

Risks: `statusRoundTripper` has a value receiver, so its `reqCount` does not persist between calls; the custom-policy test only asserts challenge handling count and does not verify second-response status behavior. Redirect tests simulate a followed redirect by setting `resp.Request.URL` and do not cover non-GET or non-200/206 exclusions.

Test signals: strong signals for core challenge replay and header injection; limited coverage for error wrapping, missing handlers, clone behavior, and cache invalidation.
