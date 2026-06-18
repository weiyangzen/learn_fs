# Research: sources/cloud-native/moby/daemon/cluster/executor/container/validate_unix_test.go

## sources/cloud-native/moby/daemon/cluster/executor/container/validate_unix_test.go

Purpose: supplies Unix path constants for the shared mount validation tests. The build tag is `!windows`.

APIs are package constants `testAbsPath` and `testAbsNonExistent`, set to Unix absolute paths. There is no control flow or state. The integration point is `validate_test.go`, where the constants make `filepath.IsAbs` checks target Unix semantics.

Risk is low but important for portability: without platform constants, shared validation tests could pass with paths that are not absolute on the active GOOS. Test signal is the shared test file itself.
