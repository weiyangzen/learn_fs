<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_linux.go -->
# sources/cloud-native/moby/daemon/config/config_linux.go

## Purpose
Defines Linux daemon platform configuration, defaults, binary lookup, rootless paths, swarm compatibility checks, and Linux-specific validation.

## Important APIs, Types, And Functions
Constants for IPC/cgroup namespace modes and runtime names; `BridgeConfig`, `DefaultBridgeConfig`, `Config`; methods `GetExecRoot`, `GetInitPath`, `LookupInitPath`, `GetResolvConf`, `IsSwarmCompatible`, `IsRootless`; functions `setPlatformDefaults`, `lookupBinPath`, `validatePlatformConfig`, `validatePlatformExecOpt`, `verifyUserlandProxyConfig`, `verifyDefaultIpcMode`, `validateFirewallBackend`, `validateFwMarkMask`, `verifyDefaultCgroupNsMode`.

## Control Flow
Defaults initialize ulimits, shm size, seccomp, IPC mode, runtime map, cgroup namespace based on cgroup v1/v2, userland proxy path lookup, and rootless or rootful root/exec/pid paths. Validation checks proxy path, IPC mode, fixed IPv6 CIDR, firewall backend, fwmark mask, and cgroup namespace mode.

## State And Persistence Behavior
No writes, but default paths determine where daemon state will persist. Binary lookup reads filesystem/PATH and rootless mode reads homedir helpers.

## Dependencies And Integration Points
Integrates containerd cgroups, rootless detection, bridge validation, daemon opts, homedir, and OS executable lookup.

## Risks And Test Signals
Risks include missing `docker-proxy` only surfacing when proxy remains enabled, rootless environment lookup failures, and swarm incompatibility with nftables unless feature-gated. Linux config tests cover feature merge, init path, host gateway migration, and fwmark parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_linux.go -->
