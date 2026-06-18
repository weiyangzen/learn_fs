# sources/cloud-native/soci-snapshotter/internal/http/auth.go

Purpose: reusable authenticated HTTP client wrapper for challenge-response registry/blob access. It wraps `retryablehttp.Client`, delegates auth logic to an `AuthHandler`, supports custom auth policies/context creation, attaches global headers, and caches successful GET redirects.

Important APIs/types/functions: `AuthHandler` defines `HandleChallenge` and `AuthorizeRequest`. `AuthPolicy`, `DefaultAuthPolicy`, `AuthReqContextFunc`, and `DefaultAuthReqContext` configure challenge detection and replay context. `AuthClient` provides `Do`, `StandardClient`, `RoundTrip`, `CloneWithNewClient`, `Client`, `CacheRedirects`, `redirected`, and `shouldCache`. Options include `WithHeader`, `WithAuthPolicy`, `WithRetryableClient`, and `WithAuthRequestCtxFunc`.

Control flow: `Do` initializes defaults, applies cached redirect rewriting for GETs, authorizes the request, converts it to retryablehttp, and sends it. If the policy matches the response, it calls `HandleChallenge`, drains the response body for connection reuse, clones the request with a fresh auth context, reauthorizes, and resends. Redirect caching records original URL to final response URL after successful 200/206 GETs.

State and persistence: persistent in-memory state includes header, handler, retry client, policy, redirect map, redirect mutex, and redirect-cache flag. Redirects are cached per original URL string and are not affected when `CacheRedirects(false)` is called except for future writes.

Dependencies/integration points: integrates with HashiCorp retryablehttp, Go `http.RoundTripper`, and internal `Drain`. Resolver code builds this client around containerd's Docker authorizer. `StandardClient` allows APIs requiring `*http.Client` to use the auth client as transport.

Risks: `roundTrip` mutates request headers and passes the same request to the handler. `CloneWithNewClient` does not copy `getAuthCtx` or redirect cache settings, so clones rely on defaults. Redirect cache rewrites only GETs and sets `Referer`; stale signed URLs could be cached if upstream returns 200/206 but short TTL. `DefaultAuthReqContext` drops original cancellation unless a custom context func is provided.

Test signals: tests cover basic-auth challenge retry, custom auth policy, global headers, and redirect cache rewriting with `Referer`. Missing-handler errors are defined but not deeply tested here.
