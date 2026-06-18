## sources/cloud-native/moby/integration-cli/utils_unix_test.go

Purpose: Unix implementation of `getLongPathName`. It is a no-op because Unix paths do not have Windows short-name expansion.

Control flow simply returns the input path and nil error. State and persistence are none. Dependencies are package `main` and Unix build selection.

Risks are minimal; shared callers must still handle the `(string, error)` signature. Test signals are indirect through path-normalization tests that compile/run on Unix without Windows syscall dependencies.
