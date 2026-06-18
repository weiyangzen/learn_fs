# sources/cloud-native/moby/integration/networking/bridge_linux_test.go

## Purpose
Linux bridge-network integration coverage for Docker Engine. The file exercises bridge driver behavior across inter-container communication, inter-network isolation, NAT/routed/nat-unprotected gateway modes, published-port reachability, default bridge IPv6 addressing, internal networks, per-endpoint sysctls, IPv4/IPv6 disablement, docker-proxy gateway selection, gratuitous ARP/neighbour advertisement, firewall ordering, legacy links, Swarm DNS interaction, explicit IP assignment, network disconnect recovery, and publish-all regressions.

## Important APIs, Types, And Functions
The tests use `daemon.New`, `StartWithBusybox`, `Restart`, `StartAndSwarmInit`, and `NewClientT` to run isolated daemon instances. Network setup flows through `integration/internal/network` helpers such as `CreateNoError`, `RemoveNoError`, `WithDriver`, `WithIPv6`, `WithIPv4(false)`, `WithInternal`, `WithIPAM`, `WithOption`, `WithIPvlan`, and endpoint `DriverOpts`. Container lifecycle uses `container.Run`, `RunAttach`, `ExecT`, `Inspect`, `WithNetworkMode`, `WithEndpointSettings`, `WithPortMap`, `WithExposedPorts`, `WithIPv4`, `WithIPv6`, `WithMacAddress`, `WithSysctls`, `WithLinks`, and `WithPublishAllPorts`.

The local `expProxyCfg` type describes expected docker-proxy processes, and `checkProxies` inspects child processes of the daemon, parses `docker-proxy` flags, resolves expected container IPs from inspect output, and compares exact proxy bindings.

## Control Flow
Most tests create a daemon, create one or more bridge networks with explicit options, start containers, then assert connectivity or isolation using `ping`, `ping6`, `wget`, `httpd`, `ip`, `sysctl`, `nslookup`, or inspect output. Matrix tests iterate gateway modes, IP families, userland proxy settings, internal/external networks, and firewall backends. Several tests run subtests in parallel only after shared network setup is complete.

`TestBridgeICC` verifies same-network DNS, ARP/NDP, and IPv4/IPv6 connectivity, including link-local and SLAAC cases. `TestBridgeINC`, `TestBridgeINCRouted`, `TestAccessToPublishedPort`, and `TestInterNetworkDirectRouting` validate cross-network isolation and gateway-mode semantics. `TestDefaultBridgeIPv6` and `TestDefaultBridgeAddresses` check default bridge IPv6 assignment and daemon restart behavior when `fixed-cidr-v6` changes. `TestGatewaySelection` mutates network attachments and expects docker-proxy bindings to move between IPv4-only, IPv6-only, dual-stack, and ipvlan endpoints. `TestAdvertiseAddresses` and `TestAdvertiseAddressesLiveRestore` listen for unsolicited ARP/NA packets and verify neighbor cache updates.

## State And Persistence Behavior
The tests deliberately mutate daemon state, bridge interfaces, firewall rules, network endpoint membership, proxy processes, ARP/ND neighbor caches, and container inspect metadata. Persistence is tested across container stop/start and daemon restart in default bridge addressing, live-restore advertisement, configured gateway recovery, and publish-all behavior. Cleanup is handled through deferred network removal, container removal, daemon stop, and helper cleanup for synthetic interfaces.

## Dependencies And Integration Points
This file integrates with Linux kernel networking, iptables/nftables, firewalld reloads, docker-proxy process management, libnetwork bridge labels (`bridge.*`, `netlabel.*`), Swarm initialization, OpenTelemetry test spans, Moby integration helpers, and BusyBox tools. Some paths depend on host namespace visibility and are skipped for rootless or incompatible firewall backends.

## Risks
Primary risks are host-network flakiness, timing-sensitive ARP/NA packet capture, dependence on `ps` output format for proxy inspection, firewall backend differences, rootless namespace differences, and assumptions about BusyBox command behavior. Tests that mutate firewall policies or host bridge state must clean up reliably or can affect later integration tests. Link-local IPv6 and firewalld interactions are especially sensitive to environment configuration.

## Test Signals
Strong signals include explicit exit-code checks, stdout/stderr substring assertions, `NetworkInspect` and container inspect validation, exact docker-proxy process comparisons, golden-style packet count/interval checks, and daemon restart assertions. Several comments tie cases to regressions such as issues 46829, 47329, 47619, 47751, 49509, 49518, 51491, 51569, 51578, 51620, and feature request 51796.
