<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/config/config_windows.go

## Purpose
Provides non-Unix/Windows platform config stubs for libnetwork.

## Important APIs, Types, And Functions
`PlatformConfig` is empty. `optionExecRoot` returns a no-op option.

## Control Flow
Common `OptionExecRoot` compiles but has no effect on this platform file.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Keeps the common config API portable across platform builds where Linux OSL/bridge config is absent.

## Risks And Edge Cases
Callers expecting `ExecRoot` to be recorded on Windows will not get that behavior from this file.

## Test Signals
Cross-platform build success is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config_windows.go -->
