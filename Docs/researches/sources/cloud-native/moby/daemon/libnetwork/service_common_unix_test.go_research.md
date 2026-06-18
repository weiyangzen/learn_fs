<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_common_unix_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_common_unix_test.go

Purpose: Unix tests for service discovery cleanup and service alias reference counting.

Important APIs/functions: `TestCleanupServiceDiscovery` and `TestServiceAliasRefCounting`.

Control flow: cleanup test creates two bridge networks, adds service records to both, verifies `cleanupServiceDiscovery(nID)` removes only one network and `cleanupServiceDiscovery("")` removes all. Alias tests add/remove service bindings with VIPs across rolling-update, per-network, and same-endpoint rebind scenarios, using `Network.ResolveName` to verify DNS visibility.

State and persistence: temporary controller/network state, `svcRecords`, `serviceBindings`, load-balancer alias refs, and resolver records. Networks are deleted after tests.

Dependencies and integration points: controller setup, bridge networks, IPAM defaults, service binding functions, DNS resolver records, and netns context.

Risks and test signals: strong regression signal for the alias ref-counting behavior documented in service structs. Ensures aliases do not disappear too early or leak across networks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_common_unix_test.go -->
