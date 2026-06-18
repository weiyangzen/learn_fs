<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_unix.go -->
# sources/cloud-native/buildkit/util/system/path_unix.go

Purpose: non-Windows helpers for host absolute path handling.

Important APIs and types: `IsAbsolutePath` and `GetAbsolutePath`.

Control flow: `IsAbsolutePath` delegates to `filepath.IsAbs`; `GetAbsolutePath` returns the input unchanged.

State and persistence: pure path helpers.

Dependencies and integration: keeps API symmetry with Windows implementation for host path code.

Risks: unlike Windows, `GetAbsolutePath` does not enforce absolutization; callers must know this helper’s platform-specific contract.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_unix.go -->
