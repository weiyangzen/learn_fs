<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_windows.go

Purpose: Windows-specific sandbox behavior where `Sandbox.osSbox` is not used.

Important APIs/functions: no-op `releaseOSSboxResources`, `updateGateway`, `ExecFunc`, `releaseOSSbox`, `restoreOslSandbox`, `NetnsPath`, `canPopulateNetworkResources`, `populateNetworkResourcesOS`, and `IPv6Enabled`.

Control flow: most OS namespace operations are no-ops. `populateNetworkResourcesOS` calls `addEpToResolver` with network name, endpoint name, sandbox config, endpoint interface, and network resolvers, wrapping errors with `errdefs.System`. `IPv6Enabled` always returns false/true because Windows container network drivers currently do not support IPv6.

State and persistence: no OSL namespace state. Resolver state is populated through Windows network resolver integration.

Dependencies and integration points: Windows HNS/resolver path elsewhere; endpoint interface and network resolver data.

Risks and test signals: platform divergence means shared sandbox code must not require `osSbox` on Windows. Tests are in Windows-specific suites outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_windows.go -->
