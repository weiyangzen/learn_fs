<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/authorizer_test.go -->
# sources/cloud-native/buildkit/util/resolver/authorizer_test.go

Purpose: verifies resolver auth helper behavior for scope parsing and no-session anonymous bearer token acquisition.

Important APIs and types: `TestParseScopes` and `TestBearerAuthFallsBackToAnonymousTokenWithoutSession`.

Control flow: scope tests compare parsed map structures for invalid empty scopes, separate scope strings, and combined space-delimited scope strings. The bearer test starts an HTTP token server, synthesizes a registry 401 Bearer challenge, calls `AddResponses`, then verifies `Authorize` fetches and applies an anonymous bearer token with no Authorization header on the token request.

State and persistence: in-memory test HTTP server and session manager only.

Dependencies and integration: uses `httptest`, BuildKit `session.Manager`, `testify/require`, and the unexported authorizer constructors.

Risks: tests do not cover Basic auth, token caching expiry, delegated token authority, invalid authorization retries, OAuth fallback, or session-specific cache linking.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/authorizer_test.go -->
