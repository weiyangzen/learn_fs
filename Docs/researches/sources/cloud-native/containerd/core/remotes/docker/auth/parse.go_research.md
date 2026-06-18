<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/parse.go -->
# sources/cloud-native/containerd/core/remotes/docker/auth/parse.go

Purpose: parses `WWW-Authenticate` headers into typed Docker registry authentication challenges.

Important APIs/types/functions: `AuthenticationScheme` bit constants `BasicAuth`, `DigestAuth`, `BearerAuth`; `Challenge`; `ParseAuthHeader`; parsing helpers `parseValueAndParams`, `skipSpace`, `expectToken`, and `expectTokenOrQuoted`; `byScheme` prioritizes bearer over digest over basic.

Control flow: initialization classifies ASCII bytes as token or space according to RFC token/separator rules. `ParseAuthHeader` iterates all canonical `WWW-Authenticate` headers, parses scheme/params, ignores unknown schemes, and stable-sorts by scheme priority. Parameter keys are lowercased; quoted strings support backslash escapes.

State and persistence: package-level octet classification table only; parsing itself is stateless.

Dependencies and integration points: consumed by `dockerAuthorizer.AddResponses` to decide whether to configure bearer or basic auth handlers.

Risks: parser is intentionally permissive and returns partial/empty results on malformed input instead of detailed errors. It parses one challenge per header string and does not fully model comma-separated multiple challenges with independent schemes.

Test signals: `parse_test.go` covers bearer challenge parsing, empty quoted parameter values, service extraction, and fuzzes arbitrary header strings for panics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/parse.go -->
