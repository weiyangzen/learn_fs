<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/fetch_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/auth/fetch_test.go

Purpose: tests challenge-to-token-option generation.

Important APIs/types/functions: `TestGenerateTokenOptions` builds `Challenge` values and asserts `GenerateTokenOptions` output.

Control flow: table cases cover multiple scopes, one scope, and no scope; subtests verify missing `realm` and unparsable `realm` return errors.

State and persistence: in-memory only.

Dependencies and integration points: validates inputs used by `dockerAuthorizer.AddResponses` before token fetching.

Risks covered: required realm validation and scope splitting. The no-scope expected value uses `strings.Split("", " ")`, which yields one empty string when the map includes an empty `scope` value; this documents current behavior.

Test signals: does not exercise HTTP token endpoints, offline token flags, headers, User-Agent, or error status handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/fetch_test.go -->
