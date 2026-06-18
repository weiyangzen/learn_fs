<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/authorizer.go -->
# sources/cloud-native/containerd/core/remotes/docker/authorizer.go

Purpose: Docker registry `Authorizer` implementation that reacts to 401 challenges, caches per-host auth handlers, injects Basic or Bearer authorization headers, and optionally returns refresh tokens.

Important APIs/types/functions: `dockerAuthorizer`, `authorizerConfig`, option functions `WithAuthClient`, `WithAuthCreds`, `WithAuthHeader`, `WithFetchRefreshToken`, `NewDockerAuthorizer`, `Authorize`, `AddResponses`, `authHandler`, `authResult`, `doBasicAuth`, `doBearerAuth`, `getExpirationTime`, `invalidAuthorization`, and `sameRequest`.

Control flow: `AddResponses` parses the last response challenge. Bearer challenges may clear cached handlers on invalid-token retry, fetch credentials, generate common token options, and install a per-host auth handler. Basic challenges require non-empty credentials. `Authorize` looks up the host handler, gets an auth value, sets `Authorization`, and calls the refresh-token callback when present. Bearer auth merges request scopes from context, caches token fetches by scope string, uses a `WaitGroup` result so concurrent requests share one fetch, prefers OAuth POST when credentials exist, and falls back to GET on known incompatible statuses.

State and persistence: in-memory host handler map guarded by `mu`; each handler has a mutex-protected scoped token cache with optional expiration time. No disk persistence; refresh token persistence is delegated to the callback.

Dependencies and integration points: used by Docker resolver/pusher request retry loops; depends on `auth.ParseAuthHeader`, `auth.FetchToken*`, remotes unexpected-status errors, `ErrInvalidAuthorization`, and request scope context helpers.

Risks: token cache key is a joined scope string and order-sensitive. Expired token replacement overwrites the cache entry but waiters on the old result still receive old state. Basic credentials are not cached separately from handler setup. `getAuthHandler` takes a write lock even for reads. Invalid authorization retry logic allows one retry per distinct request before returning `ErrInvalidAuthorization`.

Test signals: integration coverage appears in resolver tests outside this subset; `hosts_resolver_test.go` indirectly exercises bearer token fetching with per-host headers. Auth fetch/parse tests cover lower-level pieces.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/authorizer.go -->
