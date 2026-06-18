<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_unsupported.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_unsupported.go

## Purpose
Provides non-Linux `Plugin.InitSpec` behavior for unsupported platforms.

## Important APIs, Types, And Functions
`InitSpec(execRoot string) (*specs.Spec, error)` returns an error.

## Control Flow
The function immediately returns `nil` and `errors.New("not supported")`.

## State, Dependencies, And Integration Points
No state. Build tags select this for `!linux`, keeping package APIs compilable while disabling Linux-specific OCI spec construction.

## Risks And Test Signals
Callers must not assume managed plugin runtime support on non-Linux. Compile tests and backend unsupported behavior are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_unsupported.go -->
