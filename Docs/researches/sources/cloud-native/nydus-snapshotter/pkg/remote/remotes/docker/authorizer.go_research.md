# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/authorizer.go

## Purpose
Implements Docker Registry authentication for the local remotes resolver. It reacts to `WWW-Authenticate` challenges, builds Basic or Bearer credentials, caches per-host handlers, and fetches scoped tokens for repository pull/push operations.

## Important APIs, Types, And Functions
`NewDockerAuthorizer`, `WithAuthClient`, `WithAuthCreds`, `WithAuthHeader`, and `WithFetchRefreshToken` construct the authorizer. `dockerAuthorizer.Authorize` injects the `Authorization` header, and `AddResponses` learns challenges from 401 responses. `authHandler.doBasicAuth` and `doBearerAuth` implement the two schemes. `invalidAuthorization` detects repeated failed credentials.

## Control Flow
Requests initially run unauthenticated. On 401, `AddResponses` parses challenges, gets credentials for the registry host, builds common token options, and stores an `authHandler`. Later `Authorize` asks that handler for the correct header. Bearer auth derives current scopes from context, caches one `authResult` per joined scope string, and uses a wait group so concurrent callers share one token fetch. OAuth POST is preferred when a secret is available, with GET fallback for registries that reject POST.

## State And Persistence
State is in memory only: a host-to-handler map and each handler's scoped token cache. Mutexes protect handler lookup and token fetch coordination. Refresh tokens are exposed through a callback but not persisted here.

## Dependencies And Integration Points
Depends on the package-local `auth` subpackage for challenge parsing and token requests, `remote/remotes/errors` for status inspection, and `scope.go` context values for repository scopes. It is wired into `RegistryHost.Authorizer` and used by `request.doWithRetries`.

## Risks And Edge Cases
The token cache has no expiry awareness in this file, so expiry handling depends on retrying after registry rejection. Basic auth refuses empty username or secret. `invalidAuthorization` only treats repeated same-request challenge errors as invalid credentials to avoid rejecting first challenges and redirect flows.

## Test Signals
`resolver_test.go` exercises Basic auth, anonymous bearer tokens, password/refresh-token OAuth, GET fallback, bad-token rejection, and refresh-token callback behavior.
