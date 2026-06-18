<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/network_linux_test.go -->
# sources/cloud-native/moby/integration/network/network_linux_test.go

Purpose: Linux-focused general network integration tests for disabled default bridge behavior, bridge SNAT host IPv4 option, default network options, duplicate names, host-gateway resolution, gateway priority routing, and bridge/ipvlan mixed routing.

Important APIs/types/functions: top-level tests include `TestRunContainerWithBridgeNone`, `TestHostIPv4BridgeLabel`, `TestDefaultNetworkOpts`, `TestForbidDuplicateNetworkNames`, `TestHostGatewayFromDocker0`, `TestCreateWithPriority`, `TestConnectWithPriority`, `TestMixL3IPVlanAndBridge`, and helper `checkCtrRoutes`.

Control flow: tests start daemons with targeted flags, create networks/containers, execute `ip` commands in containers, inspect network state, and compare firewall or route output. Gateway-priority tests create multiple dual-stack networks with explicit IPAM, attach/disconnect endpoints with different `GwPriority`, and assert route counts/default route selection. Mixed ipvlan/bridge test creates bridge and L3 ipvlan networks, optionally restarts with live-restore, then validates default route transitions as networks are disconnected/reconnected.

State/persistence: creates daemon instances, dummy interfaces, networks, containers, routes, firewall rules, default bridge state, and live-restore state. Some tests delete `docker0` or use isolated `L3Segment` namespaces to avoid host pollution.

Dependencies/integration: Linux `ip`, `iptables`/`nft`, `syscall` address families, daemon helper, network/container helpers, API version gating, and bridge/ipvlan driver labels. Rootless/remote/userns/Windows modes are skipped where incompatible.

Risks: route-count assertions depend on kernel/network-driver route emission. Gateway priority tie-breaking and interface-name prefixes are compatibility-sensitive. Firewall backend checks differ for nftables vs iptables. Deleting or recreating docker0 and dummy links can affect other tests if cleanup fails.

Test signals: passing tests verify disabled bridge mode lacks `eth0`, host networking shares namespace, SNAT rules use configured host IPv4, default MTU options propagate, duplicate names are rejected, host-gateway maps v4/v6, gateway priority controls default routes across connect/disconnect, and L3 ipvlan routes coexist correctly with bridge gateways including live restore.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/network_linux_test.go -->
