<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.go -->
# sources/cloud-native/buildkit/session/auth/auth.go

Purpose: daemon-side helper functions for retrieving registry credentials and tokens from active BuildKit client sessions.

Important APIs, types, and functions: `sessionAuthTimeout` is 60 seconds. `getSalt` lazily creates a daemon-restart-local 32 byte salt. `CredentialsFunc` returns a callback that asks any session in a group for username/secret. `FetchToken` asks sessions for a registry token. `VerifyTokenAuthority` sends a random challenge and validates a NaCl signed response against a public key. `GetTokenAuthority` retrieves a public key for client-side token authority.

Control flow and state: each public helper wraps the caller context with a timeout cause, iterates sessions through `Manager.Any`, creates an `AuthClient`, and treats unimplemented methods as non-fatal where backward compatibility is needed. Salt is process-local and avoids stable token-authority keys across daemon restarts.

Dependencies and integration: integrates with `session.Manager`, generated Auth gRPC clients, BuildKit gRPC error helpers, and `golang.org/x/crypto/nacl/sign`. Registry resolver code uses these callbacks during image pulls and token requests.

Risks and test signals: `rand.Read` errors are ignored for salt and challenge generation, which is low-probability but security-sensitive. `GetTokenAuthority` error text uses `len(pubKey)` instead of response length when invalid. Tests should cover unimplemented-session fallback, timeout behavior, challenge validation, and invalid public key lengths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/auth.go -->
