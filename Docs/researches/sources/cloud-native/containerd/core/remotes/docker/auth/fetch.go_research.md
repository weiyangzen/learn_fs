<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/fetch.go -->
# sources/cloud-native/containerd/core/remotes/docker/auth/fetch.go

Purpose: builds token request options from registry auth challenges and fetches bearer/OAuth tokens from Docker distribution-compatible authorization servers.

Important APIs/types/functions: `ErrNoToken`, `GenerateTokenOptions`, `TokenOptions`, `OAuthTokenResponse`, `FetchTokenWithOAuth`, `FetchTokenResponse`, and `FetchToken`.

Control flow: `GenerateTokenOptions` requires and parses `realm`, copies `service`, username/secret, and splits challenge `scope` on spaces. OAuth POST builds form data for password or refresh-token grant, optional `access_type=offline`, default User-Agent, request headers, and decodes `access_token`. GET token fetch adds service/scope query params, optional Basic auth, optional `offline_token=true`, decodes `token`/`access_token`, and canonicalizes `access_token` into `Token`.

State and persistence: no persistent state. HTTP clients are shallow-copied before tracing instrumentation so caller clients are not mutated.

Dependencies and integration points: used by `docker/authorizer.go` to fetch scoped bearer tokens after parsing `WWW-Authenticate`. Uses containerd tracing, versioned User-Agent, log, and remotes unexpected-status errors.

Risks: only HTTP status 200-399 is accepted; response body size is not explicitly capped here; `strings.Split(scope, " ")` can produce empty scope elements when scope is absent but present as an empty parameter. OAuth POST fallback behavior is implemented in the authorizer, not here.

Test signals: `fetch_test.go` covers token option generation, multiple/single/no scopes, missing realm, and invalid realm. Token HTTP fetch functions are not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/fetch.go -->
