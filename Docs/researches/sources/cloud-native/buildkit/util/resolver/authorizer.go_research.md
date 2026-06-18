<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/authorizer.go -->
# sources/cloud-native/buildkit/util/resolver/authorizer.go

Purpose: implements Docker registry request authorization for BuildKit resolvers, including Basic auth, Bearer token flow, BuildKit session credential lookup, delegated token authority, token caching, and scope normalization.

Important APIs and types: `authHandlerNS`, `dockerAuthorizer`, `authFetcher`, `authResult`, `parseScopes`, `scopes.normalize`, `scopes.contains`, `invalidAuthorization`, and `sameRequest`.

Control flow: `Authorize` finds a cached `authFetcher` for the request host/session and sets an Authorization header. `AddResponses` parses registry auth challenges from a 401 response, invalidates handlers on repeated invalid auth, obtains token authority or credentials from BuildKit sessions, creates a fetcher for Bearer or Basic auth, and merges old scopes. Bearer authorization normalizes token scopes from context, flightcontrols token fetches by scope string, reuses unexpired scoped tokens, and fetches via session token authority, OAuth, token GET, or anonymous token flow.

State and persistence: `authHandlerNS` maintains host/session keyed fetchers and host configs. `authFetcher` caches scoped bearer tokens with expiry at 90 percent of server lifetime and records `lastUsed` for pool GC. State is process-local and guarded by mutexes/flightcontrol.

Dependencies and integration: integrates with containerd docker auth/challenge handling, BuildKit session auth provider, resolver pool, BuildKit logging/version user-agent, and containerd remotes error types.

Risks: credential and token cache keys are security-sensitive; push scopes are isolated by session in `pool.go`, while pull-only scopes are shared. Insufficient-scope handling only treats repeated same-request errors as fatal. Anonymous token fallback is intentional when no active session exists. Scope parsing returns nil for empty scope input, so callers must tolerate nil maps.

Test signals: `authorizer_test.go` covers scope parsing and anonymous bearer token fallback without a session.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/authorizer.go -->
