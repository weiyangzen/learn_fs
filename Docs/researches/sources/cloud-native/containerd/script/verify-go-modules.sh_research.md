<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/verify-go-modules.sh -->
# sources/cloud-native/containerd/script/verify-go-modules.sh

- Purpose: Verifies Go module files and generated vendor/module state remain clean.
- Important behavior: Accepts exactly one argument naming a second module directory, requires `jq`, and compares `require` plus `replace` directives from root `go.mod` against the second `go.mod`.
- Control flow: Load root requires/replaces into bash associative arrays using `go mod edit -json | jq`, load the second module's arrays, compare shared require versions, compare shared replace values, and ensure root replace directives also exist in the second module except for `github.com/containerd/containerd*`.
- State and persistence: Read-only against repository files; it may populate Go module cache while evaluating module metadata.
- Dependencies and integration: Requires Bash associative arrays, Go, and jq. Used when submodules must stay aligned with root module dependency overrides.
- Risks: String splitting around `#` and `:` assumes module paths/versions do not contain those separators; only overlapping requires are checked, while missing root requires are not considered errors.
- Test signals: Zero exit when no mismatch messages are emitted; nonzero exit with a count of module sync errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/verify-go-modules.sh -->
