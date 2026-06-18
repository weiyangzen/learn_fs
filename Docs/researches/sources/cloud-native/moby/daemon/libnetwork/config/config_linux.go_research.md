<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/config/config_linux.go

## Purpose
Adds Linux-specific libnetwork configuration, especially bridge driver configuration and OSL base-path setup.

## Important APIs, Types, And Functions
`PlatformConfig` contains `BridgeConfig bridge.Configuration`. `OptionBridgeConfig` sets bridge driver settings. `optionExecRoot` sets both `Config.ExecRoot` and `osl.SetBasePath`.

## Control Flow
The common `OptionExecRoot` delegates here on Linux, so controller config and namespace path setup stay in sync.

## State And Persistence
No direct persistence. Exec root determines runtime paths for OSL namespace metadata and external key listeners.

## Dependencies And Integration Points
Connects common config to bridge driver and `osl` Linux namespace handling.

## Risks And Edge Cases
Exec-root changes after namespaces are created would not retroactively move existing state. Bridge configuration is Linux-only, so common callers must account for platform builds.

## Test Signals
Linux controller startup, bridge driver registration, and namespace creation depend on these options.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config_linux.go -->
