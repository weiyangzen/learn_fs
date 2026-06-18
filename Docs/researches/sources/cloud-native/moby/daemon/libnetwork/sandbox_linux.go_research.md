<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_linux.go

Purpose: Linux-specific sandbox OS namespace operations.

Important APIs/functions: `releaseOSSboxResources`, `Statistics`, `updateGateway`, `ExecFunc`, `SetKey`, `NetnsPath`, `IPv6Enabled`, `releaseOSSbox`, `restoreOslSandbox`, `finishEndpointConfig`, `canPopulateNetworkResources`, and `populateNetworkResourcesOS`.

Control flow: `SetKey` attaches a sandbox to an externally created namespace, destroys old OS sandbox resources if needed, restarts resolver in the new namespace, refreshes IPv6 loopback state, rebuilds hosts, and finishes deferred endpoint configuration. `populateNetworkResourcesOS` validates `osSbox`, starts resolver if needed, adds interfaces with addresses/routes/sysctls/advertisement settings, handles IPv6 address removal if sysctls disabled it, configures DSR VIP aliasing, static routes, gateway updates, hosts entries, DNS, load balancers, and store update.

State and persistence: mutates `sb.osSbox`, `populatedEndpoints`, endpoint interface state, kernel routes, aliases, and datastore checkpoints.

Dependencies and integration points: OSL namespace, endpoint join info, netutils, service load balancers, DNS file code, and gateway selection.

Risks and test signals: namespace moves, resolver restart, IPv6 sysctl side effects, and gateway ordering are high-risk. Tests in this subset cover OSL primitives and sandbox endpoint/gateway ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_linux.go -->
