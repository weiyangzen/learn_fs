<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_windows.go -->
# sources/cloud-native/moby/daemon/config/config_windows.go

## Purpose
Defines Windows daemon platform configuration defaults and validation.

## Important APIs, Types, And Functions
Constants `StockRuntimeName` and `WindowsV1RuntimeName`; `BridgeConfig`, `DefaultBridgeConfig`, `Config`; methods `GetExecRoot`, `GetInitPath`, `IsSwarmCompatible`, `IsRootless`; functions `setPlatformDefaults`, `validatePlatformConfig`, `validatePlatformExecOpt`.

## Control Flow
Defaults derive root, exec-root, and pidfile from `%programdata%`. Validation warns that non-default MTU is ignored and rejects Linux-only firewall backend. Exec options allow `isolation` and reject Linux cgroup driver.

## State And Persistence Behavior
No writes, but default paths define Windows daemon state locations.

## Dependencies And Integration Points
Uses containerd logging, Windows environment, and common config validation hooks.

## Risks And Test Signals
Risks include empty `%programdata%` producing relative paths and warnings rather than errors for ignored MTU. Windows config tests cover merge behavior; common validation tests cover exec-opt platform split.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_windows.go -->
