# sources/cloud-native/containerd/plugins/services/opt/path_windows.go

## Purpose
`path_windows.go` defines the Windows-specific default opt directory.

## Important APIs, Types, And Functions
The package-level `defaultPath` variable is `filepath.Join(defaults.DefaultRootDir, "opt")`.

## Control Flow
There is no runtime control flow beyond variable initialization. The file is selected on Windows by the absence of a restrictive build tag and the competing Unix file's `!windows` tag.

## State And Persistence
The value controls where the opt service creates `bin` and `lib` directories on Windows. It does not directly create files.

## Dependencies And Integration Points
It depends on `path/filepath` and `containerd/v2/defaults`, and is consumed by `opt/service.go`.

## Risks
The path follows the configured/default containerd root, so unexpected root changes affect PATH and library search path injection.

## Test Signals
No direct tests are present. Cross-platform builds validate that the package has exactly one `defaultPath`.
