# sources/cloud-native/containerd/plugins/services/opt/path_unix.go

## Purpose
`path_unix.go` defines the default opt directory for non-Windows builds.

## Important APIs, Types, And Functions
The only exported behavior is the package-level `defaultPath` constant set to `/opt/containerd`.

## Control Flow
There is no executable control flow. The value is selected by the `!windows` build tag.

## State And Persistence
The path is used by the opt service as the base directory for `bin` and `lib` subdirectories. It affects process environment setup but does not persist anything itself.

## Dependencies And Integration Points
It feeds `service.go` in the same package and is mutually exclusive with `path_windows.go`.

## Risks
The hard-coded Unix default may require elevated permissions to create, depending on how containerd is launched. Operators can override it through opt plugin config.

## Test Signals
No direct tests are included. Build-tag selection is the main signal.
