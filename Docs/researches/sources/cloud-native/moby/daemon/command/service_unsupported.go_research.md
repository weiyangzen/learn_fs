<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/service_unsupported.go -->
# sources/cloud-native/moby/daemon/command/service_unsupported.go

## Purpose
Provides the non-Windows stub for service flag registration.

## Important APIs, Types, And Functions
`installServiceFlags` accepts a `*pflag.FlagSet` and intentionally does nothing under `!windows`.

## Control Flow
No branching or side effects.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Keeps `docker.go` platform-neutral by providing a build-tagged function that only has behavior on Windows.

## Risks And Test Signals
Risk is minimal; accidental service flags on Unix would be an API change. Command flag tests on Unix implicitly rely on no service flags being installed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/service_unsupported.go -->
