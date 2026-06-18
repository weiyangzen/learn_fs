# sources/cloud-native/containerd/pkg/kernelversion/kernel_linux_test.go

Purpose: tests Linux kernel parsing and minimum-version comparison.

Important APIs/types/functions: `TestGetKernelVersion` validates nonnil host version with nonzero kernel component. `TestParseRelease` table-tests valid release formats such as `3.8.0-19-generic`, distro suffixes, short `3.8`, and invalid strings. `TestGreaterEqualThan` overwrites the package `kernelVersion` cache with synthetic versions and checks boundary comparisons.

Control flow: table tests parse input and compare either exact `KernelVersion` or expected error string. Comparator tests set cached state directly to avoid host dependency.

State/persistence: mutates package-global `kernelVersion` during tests; no external persistence.

Dependencies/integration: Linux-only package tests with Go `testing` and `fmt`.

Risks: direct global mutation can leak between tests if future tests assume actual host state. Error string comparisons are brittle if parser wording changes.

Test signals: ensures parser tolerates common uname suffixes and that `GreaterEqualThan` handles equal, lower, and higher second components.
