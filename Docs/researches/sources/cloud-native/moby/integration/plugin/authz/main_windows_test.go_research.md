# sources/cloud-native/moby/integration/plugin/authz/main_windows_test.go

## Purpose
Windows package stub for `integration/plugin/authz`. It declares `package authz` so the package has a Windows file even though the actual authz plugin tests are non-Windows build-tagged.

## Important APIs, Types, And Functions
No imports, functions, types, or runtime behavior are defined.

## Control Flow
There is no executable control flow.

## State And Persistence Behavior
No state or persistence behavior.

## Dependencies And Integration Points
Its integration point is Go package/build compatibility on Windows when `main_test.go`, `authz_plugin_test.go`, and `authz_plugin_v2_test.go` are excluded by `//go:build !windows`.

## Risks
Low risk. Any Windows-specific authz setup would need to be added here or in another Windows file.

## Test Signals
No direct test signals; successful package loading on Windows is the only signal.
