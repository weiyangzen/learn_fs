# sources/distributed-fs/ipfs-kubo/core/corehttp/commands.go

Purpose: mounts the command tree under the HTTP RPC API, configures CORS/headers, optional RPC auth secrets, and client/daemon API version checks.

Important APIs/types/functions: constants `APIPath`, `errAPIVersionMismatch`, CORS origin lists, helpers `addCORSFromEnv`, `addHeadersFromConfig`, `addCORSDefaults`, `patchCORSVars`, `commandsOption`, `convertAuthorizationsMap`, `withAuthSecrets`, `CommandsOption`, and `CheckVersionOption`.

Control flow: `commandsOption` builds a `cmdsHttp.ServerConfig`, adds allowed headers/methods, reads repo config, applies configured headers/CORS, env-origin override, defaults, and listener port substitution, creates the command HTTP handler, wraps it with auth-secret middleware if configured, wraps with OpenTelemetry/metrics labels, and mounts at `/api/v0/`. Auth middleware allows `/api/v0/version` implicitly and otherwise requires exact Authorization header matching a converted configured secret and path prefix allowlist. Version middleware intercepts API paths and rejects Kubo/go-ipfs User-Agent mismatches except for the version endpoint.

State and persistence behavior: read-only. It copies config headers into server config to avoid races with shared config. Environment variable `API_ORIGIN` can append allowed origins with a deprecation warning.

Dependencies and integration points: integrates command tree `corecommands.Root`, `go-ipfs-cmds/http`, Kubo config `API.HTTPHeaders` and `API.Authorizations`, HTTP server mux, OpenTelemetry HTTP instrumentation, and API version constants.

Risks: auth compares the raw Authorization header string against converted secrets; prefix allowlists must be configured carefully to avoid overbroad access. CORS defaults include localhost and browser-extension origins. Version check depends on User-Agent formatting and skips non-Kubo clients.

Test signals: no local tests in this file; HTTP API behavior is likely covered by daemon/RPC integration tests.
