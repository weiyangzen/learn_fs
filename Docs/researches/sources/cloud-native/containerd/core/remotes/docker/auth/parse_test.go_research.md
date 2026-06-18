<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/parse_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/auth/parse_test.go

Purpose: tests and fuzzes Docker auth challenge parsing.

Important APIs/types/functions: `TestParseAuthHeaderBearer`, `TestParseAuthHeader`, and `FuzzParseAuthHeader`.

Control flow: bearer tests format header strings with realm/service/scope and compare exact `Challenge` slices. Empty parameter test ensures an empty quoted value is preserved. Fuzzing feeds arbitrary strings through `ParseAuthHeader`.

State and persistence: no external state.

Dependencies and integration points: protects `authorizer.go` from malformed registry `WWW-Authenticate` headers causing panics or lost important parameters.

Risks covered: multiple-space-separated scopes as one parameter value, empty quoted values, and parser robustness. It does not cover basic/digest sorting or escaped quotes explicitly.

Test signals: useful parser regression coverage plus fuzz panic resistance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/parse_test.go -->
