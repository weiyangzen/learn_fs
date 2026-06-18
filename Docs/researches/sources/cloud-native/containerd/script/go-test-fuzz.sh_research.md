<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/go-test-fuzz.sh -->
# sources/cloud-native/containerd/script/go-test-fuzz.sh

- Purpose: Thin wrapper for running Go fuzz tests with repository defaults.
- Important behavior: Uses strict shell options and `set -x`, sets `fuzztime=30s`, discovers fuzz functions with `git grep 'func Fuzz.*testing\.F'`, and runs each fuzz target separately because `go test -fuzz` accepts one fuzz function at a time.
- Control flow: Build a newline-delimited list of matching source locations excluding vendor, derive package path and `Fuzz...` function name with grep, then run `go test -fuzz=$fuzz_name ./$pkg_path -fuzztime=$fuzztime`.
- State and persistence: Persists Go fuzz cache/corpus data through the Go toolchain, typically under package `testdata/fuzz` or Go build cache depending on invocation.
- Dependencies and integration: Requires a Go version with native fuzzing support and package-level `Fuzz...` functions.
- Risks: Fuzzing is resource-intensive and can be nondeterministic by design; unbounded or long durations can stress CI.
- Test signals: Go test exit status, minimized failing corpus entries, and standard `go test` output.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/go-test-fuzz.sh -->
