# subset-b-000182 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_linux_test.go

## Purpose
Exercises the Linux bridge driver at driver, network, endpoint, and persistence boundaries. The tests verify JSON persistence formats, label/config decoding, veth creation, endpoint lifecycle, link programming, gateway selection, existing bridge reuse, concurrent create behavior, and a regression around IPv6 firewall setup with an IPv4 SNAT address.

## Important APIs, Types, And Functions
Key tests include `TestEndpointMarshalling`, `TestNetworkConfigurationMarshalling`, `TestCreateFullOptions`, `TestCreateFullOptionsLabels`, `TestCreateVeth`, `TestCreateMultipleNetworks`, `TestQueryEndpointInfo`, `TestLinkContainers`, `TestValidateConfig`, `TestValidateFixedCIDRV6`, `TestSetDefaultGw`, `TestCreateWithExistingBridge`, `TestCreateParallel`, and `TestSetupIP6TablesWithHostIPv4`. Local fakes `testInterface` and `testEndpoint` implement driver endpoint callbacks for MAC/IP/gateway/routes/name assignment.

## Control Flow
Most tests create an isolated network namespace, build a driver with a temp store and optional stub firewaller/port mapper, create bridge networks from `networkConfiguration` or labels, create endpoints, join them, program or revoke external connectivity, and assert driver state plus netlink artifacts. Serialization tests marshal and unmarshal bridge endpoints/network configs before comparing fields.

## State And Persistence
The file directly validates on-disk JSON compatibility: endpoint port mappings restore with `HostPortEnd` collapsed to `HostPort`, and network configs preserve legacy key names such as `HostIP`. Tests also check in-memory state in `d.networks`, `bridgeNetwork.endpoints`, stub firewall network maps, and operational endpoint info returned through `EndpointOperInfo`.

## Dependencies And Integration Points
Uses `netnsutils`, `nlwrap`, `netlink`, `netns`, `storeutils`, `defaultipam`, `portallocator`, `drvregistry`, `netlabel`, and the bridge firewaller stub. It integrates the bridge driver with IPAM, netlink, network namespace management, port mapping, endpoint callback interfaces, and firewall network creation.

## Risks And Edge Cases
Coverage emphasizes Linux namespace privileges, duplicate network/endpoint IDs, manually created bridges, default bridge constraints, invalid gateway/subnet inputs, IPv4-mapped addresses, and concurrent `CreateNetwork` races. Tests that shell out to `ip netns` or manipulate netlink can be environment-sensitive.

## Test Signals
Strong signals are successful isolated bridge creation/deletion, stable JSON restore behavior, correct endpoint gateway and MTU assignment, stub firewaller rule lifetime matching bridge network lifetime, expected errors for invalid IDs and duplicate endpoints, and only one successful create in the parallel race test.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_store.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_store.go

## Purpose
Implements datastore persistence and live-restore hydration for bridge networks and endpoints. It restores network configuration, endpoint membership, endpoint firewall rules, and host port reservations after daemon restart.

## Important APIs, Types, And Functions
`driver.initStore` calls `populateNetworks` then `populateEndpoints`. `storeUpdate` and `storeDelete` wrap `datastore` atomic put/delete operations. `networkConfiguration` and `bridgeEndpoint` implement `datastore.KVObject` with `Key`, `KeyPrefix`, `Value`, `SetValue`, index/existence methods, `New`, and `CopyTo`. Custom `MarshalJSON` and `UnmarshalJSON` preserve legacy storage format. `bridgeNetwork.restorePortAllocations` replays saved endpoint port mappings.

## Control Flow
Startup lists saved `networkConfiguration` objects, recreates each network through `createNetwork`, then lists `bridgeEndpoint` objects, attaches each endpoint to its restored network, re-adds per-endpoint firewall rules, and re-reserves port mappings. Stale endpoints whose network no longer exists are deleted from the store.

## State And Persistence
Network state is stored under `bridge/<network-id>` and endpoint state under `bridge-endpoint/<endpoint-id>`. JSON encodes IP networks and IPs as strings, joins trusted interfaces with `:`, uses the historical `HostIP` key for IPv4 host SNAT, and normalizes restored operational `HostPortEnd` to `HostPort` to avoid reallocating a different port during live-restore.

## Dependencies And Integration Points
Depends on `datastore`, `portmapperapi`, `types`, OpenTelemetry span/baggage helpers, containerd logging, and `nftabler` cleaner integration. It coordinates with `createNetwork`, `firewallerNetwork.AddEndpoint`, `addPortMappings`, and endpoint/network maps maintained by the bridge driver.

## Risks And Edge Cases
JSON unmarshalling uses map assertions for required historical fields, so missing or malformed persisted state can panic or fail hard. Optional nested endpoint configs are decoded from `nil` if absent, with a TODO noting that fields may be unintentionally nullified. Port restore warns but leaves containers inaccessible if prior host ports cannot be reserved.

## Test Signals
Covered by bridge marshalling and endpoint operational-info tests. Useful additional signals are live-restore tests with stale endpoints, pre-27 port range state, missing optional JSON fields, and cross-firewaller cleanup after switching between iptables and nftables.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/errors.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/errors.go

## Purpose
Centralizes bridge-driver error types so callers can classify invalid gateway, network ID, and endpoint ID failures through Docker/containerd error interfaces.

## Important APIs, Types, And Functions
`errInvalidGateway` is an `errdefs.InvalidParameter` error used when a configured gateway is outside the network. `invalidNetworkIDError` implements `Error` and `NotFound`. `invalidEndpointIDError` implements `Error` and `InvalidParameter`. `endpointNotFoundError` implements `Error` and `NotFound`.

## Control Flow
There is no complex control flow; bridge driver operations construct these values at validation and lookup failure points. Error interface marker methods determine higher-level API classification.

## State And Persistence
No state is stored. The file affects persisted API behavior indirectly because clients and tests depend on stable error categories and messages.

## Dependencies And Integration Points
Depends on `errdefs` and standard `errors`/`fmt`. Integrated by network and endpoint create/delete/join paths and setup validation logic.

## Risks And Edge Cases
Changing message strings or marker methods can break API expectations and tests such as invalid endpoint deletion/creation checks. The gateway error is a package variable, so callers should wrap it carefully if more context is needed.

## Test Signals
Bridge tests assert `InvalidArgument` or `NotFound` style behavior for empty endpoint IDs, duplicate operations, invalid gateways, and missing endpoints/networks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux.go

## Purpose
Models the Linux bridge interface managed by the driver and handles bridge discovery, address listing, and IPv6 address programming.

## Important APIs, Types, And Functions
`DefaultBridgeName` is `docker0`. `bridgeInterface` stores the netlink link, configured IPv4/IPv6 bridge prefixes, gateway IPs, and `nlwrap.Handle`. `newInterface` resolves an existing bridge by name and defaults an empty name to `docker0`. `exists` reports whether a link was found. `addresses` lists v4/v6 addresses. `programIPv6Addresses` reconciles configured IPv6 address state onto the bridge.

## Control Flow
`newInterface` looks up `config.BridgeName`, accepts missing links, and rejects existing non-bridge links. IPv6 programming stores desired state, converts the network to `netip.Prefix`, lists existing IPv6 addresses, removes unexpected non-multicast and non-standard link-local addresses, and finally calls `AddrReplace` with `IFA_F_NODAD`.

## State And Persistence
State is kernel netlink state plus cached fields on `bridgeInterface`. The code intentionally preserves standard link-local and multicast addresses and avoids removing/readding the same IPv6 address on live-restore to reduce traffic disruption.

## Dependencies And Integration Points
Uses `nlwrap`, `netlink`, `netiputil`, `errdefs`, and containerd logging. Called by bridge setup and network creation paths before IPv4/IPv6 gateway and firewall setup.

## Risks And Edge Cases
Existing non-bridge interfaces with the requested name are fatal. Prefix-length changes on an existing address are not actually reflected by `AddrReplace`, a documented cosmetic limitation. The code must avoid deleting kernel link-local addresses that keep IPv6 neighbor discovery functional.

## Test Signals
`interface_linux_test.go` covers default naming, absent interface address listing, v4/v6 address listing, link-local preservation, nonstandard link-local replacement, multicast preservation, and prefix shrink behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux_test.go

## Purpose
Validates bridge interface helper behavior in isolated Linux network namespaces.

## Important APIs, Types, And Functions
Helpers `cidrToIPNet`, `addAddr`, and `prepTestBridge` create test networks, assign addresses, and create bridge devices. Tests cover `newInterface`, `bridgeInterface.addresses`, and `programIPv6Addresses`.

## Control Flow
Each test uses `netnsutils.SetupTestOSContext` where kernel state is touched. The IPv6 programming test repeatedly mutates `networkConfiguration.AddressIPv6`, calls `programIPv6Addresses`, lists bridge addresses, sorts actual/expected strings, and checks cached bridge/gateway fields.

## State And Persistence
All state is temporary kernel netlink state in the test namespace. The tests specifically observe persistence of the kernel link-local address and multicast autoconf address across daemon-driven address reconciliation.

## Dependencies And Integration Points
Uses `nlwrap`, `netlink`, `unix.IFA_F_MCAUTOJOIN`, and `gotest.tools` assertions. It is the focused test companion for `interface_linux.go` and `setup_device_linux.go`.

## Risks And Edge Cases
Requires netlink and namespace privileges. The prefix-shrink case documents that Linux may keep the old displayed prefix even though the bridge driver updates its cached config. Link-local handling is subtle because nonstandard link-local prefixes may come from IPAM and should be removed.

## Test Signals
Passing tests signal default bridge naming, safe behavior with missing links, accurate family-specific address listing, configured IPv6 insertion, standard link-local preservation, nonstandard link-local cleanup, and multicast preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/firewaller.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/firewaller.go

## Purpose
Defines the bridge driver's firewall abstraction used by both iptables and nftables implementations.

## Important APIs, Types, And Functions
`IPVersion` identifies IPv4 or IPv6. `Config` contains top-level daemon settings such as enabled families, hairpin mode, direct routing, and WSL2 mirrored networking. `NetworkConfig` carries bridge-scoped policy: interface name, internal flag, ICC, masquerade, trusted host interfaces, fwmark allowance, and family configs. `NetworkConfigFam` carries host SNAT address, prefix, routed mode, and unprotected mode. Interfaces `Firewaller`, `Network`, and `FirewallCleaner` define lifecycle, endpoint, port, link, and cleanup operations.

## Control Flow
The bridge driver selects a concrete `Firewaller`, creates one `Network` per bridge, then calls network methods as endpoints, port mappings, legacy links, and reload/cleanup events occur.

## State And Persistence
The interface itself stores no state. It makes explicit which firewall state is network-level, endpoint-level, port-level, and link-level, and it documents cleaner behavior for deleting rules left by a previous backend during live-restore.

## Dependencies And Integration Points
Depends on `types.PortBinding`, `types.TransportPort`, `context`, and `netip`. Implemented by `iptabler`, `nftabler`, and the test `StubFirewaller`; consumed by the bridge driver, port mapping, IP forwarding, and store restore logic.

## Risks And Edge Cases
Semantics must remain consistent across backends. `DelNetworkLevelRules` intentionally excludes per-port/per-link cleanup, so driver call ordering is important. `AllowDirectRouting`, `Unprotected`, and `Routed` have security-sensitive meanings and must map cleanly to backend rules.

## Test Signals
Stub-backed bridge tests verify call ordering and object lifetimes; iptabler/nftabler golden tests verify equivalent rule output across policy combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/firewaller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/stub.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/stub.go

## Purpose
Provides an in-memory firewaller implementation for unit tests, recording requested networks, endpoints, ports, and links without touching host firewall state.

## Important APIs, Types, And Functions
`NewStubFirewaller` constructs `StubFirewaller` with a `Networks` map. `NewNetwork` creates a `StubFirewallerNetwork`. Network methods implement `ReapplyNetworkLevelRules`, `DelNetworkLevelRules`, `AddEndpoint`, `DelEndpoint`, `AddPorts`, `DelPorts`, `AddLink`, and `DelLink`. Helpers `PortExists`, `LinkExists`, and `matchLink` support assertions.

## Control Flow
Tests install the stub through `useStubFirewaller`; bridge operations then mutate in-memory maps/slices. Deleting network-level rules removes the network only when endpoints, ports, and links have already been cleared.

## State And Persistence
State is in memory only. It records endpoint address pairs, copied port bindings, and cloned legacy link port lists. It deliberately tracks networks even though production firewallers rely on the bridge driver to own network objects.

## Dependencies And Integration Points
Depends on `types`, `netip`, and `slices`. Integrated by bridge lifecycle, link, and port mapping tests to validate driver behavior independently of iptables/nftables availability.

## Risks And Edge Cases
The stub is stricter than some production backends about deletion ordering; that is useful for driver tests but may not model reload-tolerant behavior. `AddPorts` ignores duplicate ports, matching idempotent firewall intent.

## Test Signals
Bridge tests use `PortExists` and `LinkExists` to assert port/link programming and verify network entries are created and removed as driver networks come and go.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/stub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/cleaner.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/cleaner.go

## Purpose
Detects and cleans iptables rules left by a previous daemon/backend, then exposes targeted cleanup hooks for restored networks, endpoints, and ports.

## Important APIs, Types, And Functions
`iptablesCleaner` stores top-level `firewaller.Config`. `NewCleaner` checks built-in FORWARD jumps for Docker chains, removes top-level jumps and user-defined chains, warns about `FORWARD` policy DROP, and returns a cleaner when work was done. `DelNetwork`, `DelEndpoint`, and `DelPorts` reconstruct lightweight `network` objects and call backend removal methods.

## Control Flow
On startup, if switching away from iptables, the new backend can obtain a cleaner. Immediate cleanup removes chains and jumps that can be identified globally. Later, when persisted networks/endpoints/ports are replayed, the cleaner removes rules that require bridge interface names or endpoint addresses.

## State And Persistence
No repo state is persisted. Host iptables state is mutated. The returned cleaner carries only enough config to delete per-family rules matching restored bridge configuration.

## Dependencies And Integration Points
Uses `iptables`, `firewaller`, containerd logging, and iptabler network/port/endpoint helpers. Paired with `nftabler.SetFirewallCleaner` and bridge store live-restore.

## Risks And Edge Cases
Built-in chain rules cannot be flushed indiscriminately because that would affect non-Docker firewall policy. Cleanup is best-effort and ignores many deletion errors. A remaining DROP policy on `FORWARD` may still break traffic accepted by nftables.

## Test Signals
`TestCleanupIptableRules` verifies Docker chains are flushed/removed as expected across IPv4 and IPv6 in an isolated namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/cleaner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/endpoint.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/endpoint.go

## Purpose
Programs per-endpoint direct-access filtering for the iptables backend.

## Important APIs, Types, And Functions
`AddEndpoint` and `DelEndpoint` call `modEndpoint`. `filterDirectAccess` adds or deletes raw table `PREROUTING` rules that allow trusted interfaces and drop packets addressed directly to container IPs from untrusted interfaces.

## Control Flow
For each valid IPv4/IPv6 endpoint address and enabled family, `modEndpoint` delegates to `filterDirectAccess`. The filter is skipped for internal, unprotected, routed, daemon-wide direct-routing, or raw-disabled configurations. Otherwise it creates ACCEPT rules for trusted interfaces and a DROP rule for traffic not arriving from the bridge.

## State And Persistence
State is host iptables raw table state keyed by endpoint IP and bridge/trusted interface names. It is intentionally endpoint-scoped so direct-routed traffic is blocked even before an endpoint becomes a gateway for published ports.

## Dependencies And Integration Points
Uses `iptables`, `firewaller.NetworkConfigFam`, `rawRulesDisabled`, and `appendOrDelChainRule`. Called during endpoint create/delete and live-restore endpoint replay.

## Risks And Edge Cases
`DOCKER_INSECURE_NO_IPTABLES_RAW=1` disables these rules and weakens direct-access protection. Trusted interface names become part of security policy. Config changes across live-restore deliberately force deletion when direct routing becomes allowed or raw rules are disabled.

## Test Signals
Iptabler golden tests include endpoint add/delete and raw rule output across routed, unprotected, internal, and WSL2-related combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler.go

## Purpose
Initializes and manages top-level iptables chains used by Docker bridge networking.

## Important APIs, Types, And Functions
Constants define Docker chains: `DOCKER`, `DOCKER-FORWARD`, `DOCKER-BRIDGE`, `DOCKER-CT`, `DOCKER-INTERNAL`, and legacy isolation chains. `Iptabler` holds `firewaller.Config`. `NewIptabler` initializes IPv4/IPv6 chains and reload hooks. `FilterForwardDrop` sets the built-in `FORWARD` policy to DROP. `setupIPChains`, `deleteLegacyTopLevelRules`, `programChainRule`, and `appendOrDelChainRule` perform core rule management.

## Control Flow
Initialization removes old chains, creates NAT/filter chains, adds NAT PREROUTING/OUTPUT jumps to `DOCKER`, installs filter FORWARD jumps into Docker chains, adds WSL2 loopback handling when needed, and deletes legacy top-level rules. IPv6 setup logs and continues on kernel/module failure so IPv4 daemon startup can proceed.

## State And Persistence
State is global host iptables chain/rule state. Reload callbacks replay chain creation and default DROP policy after firewall reloads. Failure cleanup removes newly created chains and jump rules where possible.

## Dependencies And Integration Points
Uses `iptables`, `modprobe`, `firewaller`, and containerd logging. It is selected by bridge driver configuration and provides network objects implemented in `network.go`.

## Risks And Edge Cases
Global chain mutation is security-sensitive and can interact with firewalld and user policies. IPv6 setup may silently degrade to logged warnings. Legacy rule deletion is necessary for upgrades but must avoid deleting unrelated user rules.

## Test Signals
`iptabler_test.go` checks cleanup and broad golden snapshots; `network_test.go` checks rule programming, setup, and outgoing NAT variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler_test.go

## Purpose
Validates iptables backend cleanup and rule output over a large policy matrix.

## Important APIs, Types, And Functions
`TestCleanupIptableRules` verifies `removeIPChains`. `TestIptabler` enumerates booleans for IPv4, IPv6, hairpin, internal, ICC, masquerade, SNAT, localhost binding, and WSL2 mirrored mode across gateway modes. `testIptabler` initializes the backend, adds a network, endpoint, and port bindings, compares `iptables-save`/`ip6tables-save` output to golden files, then deletes everything and checks cleaned state.

## Control Flow
Tests run in isolated namespaces, skip when host firewalld interferes, generate expected-result names that collapse irrelevant dimensions, and dump raw/filter/nat tables explicitly to reduce backend ordering differences.

## State And Persistence
Temporary iptables state is created and destroyed in the test namespace. Golden files under backend testdata persist expected rule output for many combinations.

## Dependencies And Integration Points
Uses `iptables`, `netnsutils`, `gotest.tools/golden`, `icmd`, and `types.PortBinding`. It covers `Iptabler`, network, endpoint, port, and WSL2 helpers together.

## Risks And Edge Cases
Rule dump order can differ between iptables backends, so comments are stripped and tables are dumped separately. The matrix is broad but expensive; firewalld on the host can invalidate namespace assumptions.

## Test Signals
Passing golden checks signal stable cleanup, NAT/filter/raw rule generation, WSL2 exception behavior, localhost binding filtering, and equivalence of add/delete lifecycle to a known cleaned baseline.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/link.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/link.go

## Purpose
Implements legacy container link firewall rules for the iptables backend.

## Important APIs, Types, And Functions
`AddLink` validates parent/child IP addresses and appends rules through `iptables.ChainInfo.Link`. `DelLink` deletes matching rules and logs failures.

## Control Flow
For each exposed transport port, add or delete a rule in the `DOCKER` chain allowing traffic between a parent container IP and child container IP on the bridge interface.

## State And Persistence
State is per-link iptables filter state in the `DOCKER` chain. The bridge driver tracks which links exist and calls deletion on disconnect; this file does not store refcounts.

## Dependencies And Integration Points
Uses `iptables.ChainInfo`, `types.TransportPort`, `netip`, and containerd logging. Called by bridge external-connectivity/link logic and covered indirectly by link tests.

## Risks And Edge Cases
Invalid or unspecified IPs are rejected on add. Delete is best-effort and only logs failures, so stale link rules could remain after partial cleanup. It is IPv4-oriented through legacy `ChainInfo.Link` behavior.

## Test Signals
`TestLinkContainers` with the stub firewaller validates the driver-level link lifecycle; iptabler golden tests include link rule groups through backend operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/link.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network.go

## Purpose
Implements per-bridge network-level iptables rules for internal, NAT, routed, unprotected, ICC, masquerade, SNAT, conntrack, and default-forward policy behavior.

## Important APIs, Types, And Functions
`network` holds `firewaller.NetworkConfig`, parent `Iptabler`, and cleanup functions. `NewNetwork`, `ReapplyNetworkLevelRules`, `DelNetworkLevelRules`, `configure`, and `setupIPTables` manage lifecycle. Helpers include `setICMP`, `addNATJumpRules`, `deleteLegacyFilterRules`, `setDefaultForwardRule`, `setupNonInternalNetworkRules`, `setIcc`, `removeIPChains`, `setupInternalNetworkRules`, and `iptablesFwMark`.

## Control Flow
Creating a network configures each enabled valid family. Internal networks get ingress/egress DROP rules plus ICC handling. External networks get SNAT/MASQUERADE rules when configured, hairpin host masquerade, ICC rules, optional ICMP for routed mode, outgoing ACCEPT rules, default incoming DROP/ACCEPT in `DOCKER`, conntrack established ACCEPT, and jumps from Docker bridge/CT chains. Each successful step registers a reverse cleanup function.

## State And Persistence
State is host iptables state plus in-memory cleanup closures. Cleanups are lost on daemon restart, so store restore and cleaner paths reconstruct removal based on persisted network config.

## Dependencies And Integration Points
Uses `firewaller`, `iptables`, containerd logging, and numeric parsing for firewall marks. Called by `Iptabler.NewNetwork`, cleaner, and reload paths.

## Risks And Edge Cases
Ordering matters: per-port ACCEPT rules must precede default DROP. Upgrade cleanup deletes legacy FORWARD rules from old releases. Firewall mark parsing accepts Go-style numeric syntax and converts to decimal for iptables. Internal network IPv4/IPv6 rule forms differ.

## Test Signals
`network_test.go` verifies setup/deletion and NAT/SNAT combinations; `iptabler_test.go` golden files validate full network rule output across policy combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network_test.go

## Purpose
Provides focused tests for iptables network-level rule helpers and outgoing NAT/SNAT behavior.

## Important APIs, Types, And Functions
`TestProgramIPTable` checks `programChainRule` add/delete. `TestSetupIPChains` creates networks with varying masquerade and ICC. `TestSetupIP6TablesWithHostIPv4` covers an IPv6 setup regression with IPv4 host SNAT. `TestOutgoingNATRules` enumerates daemon/family/host-IP combinations and asserts expected MASQUERADE or SNAT rules.

## Control Flow
Tests create isolated namespaces, initialize `NewIptabler`, create `firewaller.NetworkConfig` values, call `NewNetwork`, then assert rule existence or delete network-level rules. NAT tests dump tables to logs for troubleshooting and compare explicit expected iptables rules.

## State And Persistence
Only namespace-local iptables state is modified. No repository state is changed except optional test logs.

## Dependencies And Integration Points
Uses `iptables`, `netnsutils`, `firewaller`, `netip`, and `gotest.tools`. It bridges low-level rule helpers with the `firewaller.Firewaller` interface.

## Risks And Edge Cases
Environment must support iptables in isolated namespaces. The NAT matrix guards against accidental SNAT/MASQUERADE when iptables/ip6tables or masquerading is disabled, and against IPv4 host SNAT leaking into IPv6 setup.

## Test Signals
Passing tests signal reliable rule insertion/removal and correct outgoing NAT selection for IPv4, IPv6, host-specific SNAT, disabled tables, and mixed-family configurations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/port.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/port.go

## Purpose
Programs per-port iptables rules for published ports, DNAT, hairpin masquerade, direct forwarding, loopback protection, and legacy cleanup.

## Important APIs, Types, And Functions
`AddPorts`, `DelPorts`, and `modPorts` iterate port bindings. `setPerPortIptables` dispatches family and security decisions. `setPerPortNAT` creates DNAT and hairpin MASQUERADE. `setPerPortForwarding` opens published container ports. `filterPortMappedOnLoopback` protects loopback-bound host ports. `dropLegacyFilterDirectAccess` removes older direct-access rules. `rawRulesDisabled` honors `DOCKER_INSECURE_NO_IPTABLES_RAW`.

## Control Flow
Each binding is skipped if its family/backend is disabled or the network is internal. Loopback filtering and legacy direct-access cleanup run first. Cross-family IPv6-host to IPv4-container mappings are left to docker-proxy. NAT rules are added only for nonzero host ports, and forwarding ACCEPT rules are added unless the family config is unprotected.

## State And Persistence
State is iptables nat/filter/raw rules keyed by host IP/port, container IP/port, protocol, and bridge name. The bridge endpoint stores operational mappings; on restore the driver replays `AddPorts`.

## Dependencies And Integration Points
Uses `types.PortBinding`, `iptables`, `os.Getenv`, and containerd logging. Called from bridge port mapping and cleaner paths.

## Risks And Edge Cases
Raw-rule opt-out weakens loopback and direct-routing protections. IPv6 link-local sources are excluded from DNAT. Duplicate host mappings and hairpin mode must avoid duplicate or missing rules. Legacy direct-access cleanup is upgrade-sensitive.

## Test Signals
Golden iptabler tests cover per-port rule output; bridge port mapping tests validate firewall calls through the stub firewaller.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/port.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/wsl2.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/wsl2.go

## Purpose
Adds/removes an iptables NAT exception for WSL2 mirrored networking loopback traffic.

## Important APIs, Types, And Functions
`mirroredWSL2Workaround` accepts an `iptables.IPVersion` and enable flag. It only acts for IPv4 and programs a `DOCKER` nat chain RETURN rule for `loopback0` traffic to `127.0.0.0/8`.

## Control Flow
Top-level chain setup calls this helper when hairpin mode is disabled and WSL2 mirrored networking is detected. The helper no-ops for IPv6 because WSL2 mirrored mode does not support Windows-to-Linux `::1` in this path.

## State And Persistence
State is a single IPv4 nat rule in the `DOCKER` chain. It is replayed during chain setup and removed during cleanup.

## Dependencies And Integration Points
Uses the iptables backend helpers and is paired with similar nftables logic. It integrates with docker-proxy behavior for loopback-bound published ports.

## Risks And Edge Cases
Without the rule, Windows-originated `127.0.0.1` traffic in WSL2 mirrored mode can be DNATed directly to a container with an unusable source address. The rule assumes the WSL2 interface name `loopback0`.

## Test Signals
Iptabler golden tests include WSL2-specific expected output only when IPv4, mirrored mode, and relevant loopback/proxy conditions apply.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/wsl2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/cleaner.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/cleaner.go

## Purpose
Deletes nftables rules created by a previous nftables bridge firewaller and stores a cross-backend cleaner on the current `Nftabler`.

## Important APIs, Types, And Functions
`Cleanup` calls `tryCleanup` for enabled IPv4/IPv6 families. `tryCleanup` runs `nft delete table <family> docker-bridges`. `SetFirewallCleaner` stores a `firewaller.FirewallCleaner` for targeted cleanup of old backend rules as networks/endpoints/ports are restored.

## Control Flow
Startup cleanup is table-level: delete the whole Docker bridge table for each enabled family and log success or the expected absence. During normal setup, `Nftabler` uses its `cleaner` field in network/endpoint/port methods before adding new nftables rules.

## State And Persistence
Host nftables table state is mutated. No repository state is stored. Cleaner state is an in-memory bridge between old and new firewall implementations.

## Dependencies And Integration Points
Uses internal `nftables.RunCmd`, `firewaller.Config`, and containerd logging. Integrated with bridge driver backend switching and store live-restore.

## Risks And Edge Cases
Table deletion is coarse but safe because the table is backend-owned. Errors for missing tables are logged at info level, so unexpected nft command failures need log inspection.

## Test Signals
Covered indirectly by nftabler golden tests and backend-switch cleanup flows; direct tests would assert table absence after `Cleanup`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/cleaner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/endpoint.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/endpoint.go

## Purpose
Programs per-endpoint direct-access filtering for the nftables backend.

## Important APIs, Types, And Functions
`AddEndpoint` optionally invokes the stored cleaner, then calls `modEndpoint`. `DelEndpoint` removes rules. `filterDirectAccess` builds raw prerouting drop rules using family-specific `daddr`, the bridge interface, and trusted host interfaces.

## Control Flow
For each enabled family and valid endpoint address, create/delete a modifier against the family table. Filtering is skipped for internal, unprotected, routed, or daemon-wide direct-routing configurations. Otherwise packets addressed to the container from interfaces outside the bridge/trusted set are dropped.

## State And Persistence
State is nftables raw-prerouting rules in the backend-owned table. Cleaner calls remove old backend rules during live-restore before nftables rules are added.

## Dependencies And Integration Points
Uses internal `nftables`, `firewaller.NetworkConfigFam`, `netip`, and string formatting for interface sets. Called by bridge endpoint creation/removal and store restore.

## Risks And Edge Cases
Trusted interface formatting can produce an empty set element if no trusted interfaces exist, so rule generation depends on nftables helper behavior. Direct-routing flags are security-sensitive. Unlike iptabler, there is no raw-rule environment opt-out in this backend.

## Test Signals
Nftabler golden tests cover endpoint rule output across routed, unprotected, internal, direct filtering, and WSL2-related combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/link.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/link.go

## Purpose
Implements legacy container link firewall rules for the nftables backend.

## Important APIs, Types, And Functions
`AddLink` validates parent and child IP addresses, creates per-port rules with `updateLegacyLinkRules`, and applies them to the IPv4 table. `DelLink` deletes the same rules and logs apply failures.

## Control Flow
For each exposed port, two rules are generated in the network's filter-forward ingress chain: parent-to-child destination-port accept and child-to-parent source-port accept for unsolicited reverse traffic.

## State And Persistence
State is per-network nftables filter rules grouped under `fwdInLegacyLinksRuleGroup`. The code currently uses `table4`, reflecting legacy link behavior for IPv4 container addresses.

## Dependencies And Integration Points
Uses `nftables.Modifier`, `types.TransportPort`, `netip`, and logging. Called by bridge link programming and mirrored conceptually by iptabler link handling.

## Risks And Edge Cases
Delete is best-effort. The implementation does not combine rules into sets yet, so many linked ports produce many rules. IPv6 legacy link behavior is not represented here.

## Test Signals
Nftabler golden tests include legacy link rule groups as part of the backend lifecycle; bridge link tests validate driver behavior with the stub firewaller.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/link.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/network.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/network.go

## Purpose
Creates per-network nftables chains, verdict-map entries, NAT rules, ICC rules, direct ingress policy, and cleanup modifiers for bridge networks.

## Important APIs, Types, And Functions
`network` stores config, parent `Nftabler`, and reverse modifiers. `Nftabler.NewNetwork` invokes optional old-backend cleanup and configures IPv4/IPv6 tables. `configure` builds chains/maps/rules. `DelNetworkLevelRules` applies reverse modifiers. Helpers derive chain names and parse firewall marks with `nftFwMark`.

## Control Flow
For each valid family, `configure` creates ingress/egress filter chains and postrouting chains, inserts verdict-map elements keyed by bridge interface, adds conntrack rules, then branches for internal or external networks. Internal networks drop non-bridge ingress/egress and enforce ICC. External networks add optional fwmark accept, ICC, outgoing accept, final ingress accept/drop for unprotected/default, ICMP in routed mode, SNAT/MASQUERADE for outgoing NAT, and hairpin host masquerade.

## State And Persistence
State is nftables table state plus reverse modifiers retained in memory for cleanup. Firewalld reload does not delete nftables rules, so `ReapplyNetworkLevelRules` logs that it is not implemented.

## Dependencies And Integration Points
Uses internal `nftables`, OpenTelemetry spans, logging, and `firewaller`. Called by bridge network creation and backend live-restore.

## Risks And Edge Cases
In-memory reverse modifiers are unavailable after daemon restart, so persistent cleanup relies on table deletion or reconstructive cleaners. Rule grouping controls order; mistakes can expose unpublished ports or block established traffic. Firewall mark mask syntax differs from iptables and is converted to nft expressions.

## Test Signals
`nftabler_test.go` golden matrix validates generated table content and cleanup for IPv4/IPv6, internal, ICC, masquerade, SNAT, routed/unprotected, hairpin, localhost binding, and WSL2 options.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler.go

## Purpose
Initializes the nftables backend's per-family Docker bridge tables and base chains.

## Important APIs, Types, And Functions
Constants name the `docker-bridges` table, base chains, NAT chain, raw chain, verdict maps, and rule groups. `Nftabler` stores config, optional cleaner, and IPv4/IPv6 tables. `NewNftabler`, `Close`, and `init` manage table creation and resources.

## Control Flow
For each enabled family, `init` creates a table, filter FORWARD base chain with ingress/egress verdict maps, NAT POSTROUTING base chain with ingress/egress maps, shared NAT chain, NAT PREROUTING and OUTPUT chains that jump for local destinations, raw PREROUTING chain, and optional WSL2 loopback rule. IPv6 table apply failures are logged and tolerated.

## State And Persistence
State is host nftables table state. The object holds table handles that must be closed, but `Close` does not delete firewall rules. The table is intended to be backend-owned and cleaned by table deletion when needed.

## Dependencies And Integration Points
Uses internal `nftables`, `firewaller`, and logging. It is selected by bridge driver firewall configuration and returns per-network objects implemented in `network.go`.

## Risks And Edge Cases
Base chain priorities and verdict-map dispatch are central to packet path correctness. Hairpin mode changes OUTPUT loopback exceptions. IPv6 failure tolerance can leave IPv6 bridge networking unavailable while daemon startup succeeds.

## Test Signals
Nftabler golden tests validate table initialization and cleaned state for enabled/disabled families and hairpin/WSL2 combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler_test.go

## Purpose
Golden-tests the nftables backend across the same major policy dimensions as the iptables backend.

## Important APIs, Types, And Functions
`TestNftabler` enables the internal nftables mode and iterates boolean flags for IPv4, IPv6, hairpin, internal, ICC, masquerade, SNAT, localhost binding, and WSL2 mirrored mode across gateway modes. `testNftabler` initializes the backend, adds a network, endpoint, and port bindings, checks `nft list table` output, then deletes all objects and checks cleaned state.

## Control Flow
Each subtest creates an isolated namespace, chooses a shared golden result name for irrelevant combinations, creates `NewNftabler`, adds/removes network objects, and compares `ip`/`ip6` family table output.

## State And Persistence
Only test namespace nftables state is mutated. Expected outputs are persisted as golden files under backend testdata.

## Dependencies And Integration Points
Uses internal `nftables.Enable/Disable`, `netnsutils`, `icmd`, `golden`, `firewaller`, and `types.PortBinding`. Exercises all nftabler implementation files together.

## Risks And Edge Cases
The test currently avoids parallelism because cgo/libnftables behavior and shared golden files can be problematic. Output normalization handles nft priority wording differences.

## Test Signals
Passing golden checks signal stable nft table construction, network chain setup, endpoint filtering, port DNAT/forwarding, hairpin masquerade, WSL2 loopback exceptions, and cleanup back to the expected baseline.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/port.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/port.go

## Purpose
Programs nftables rules for published ports: forwarding accepts, DNAT, hairpin masquerade, and loopback-bound host-port protection.

## Important APIs, Types, And Functions
`AddPorts`, `DelPorts`, and `modPorts` manage lifecycle. `splitByContainerFam` separates IPv4/IPv6 bindings. `setPerPortRules` coordinates modifiers. `setPerPortForwarding`, `setPerPortDNAT`, `setPerPortHairpinMasq`, and `filterPortMappedOnLoopback` emit rule objects.

## Control Flow
Internal networks skip all port rules. On add, any old-backend cleaner first deletes equivalent old rules. Bindings are grouped by container address family and applied to valid family tables. Unprotected networks skip forwarding accept rules because final ingress accepts all. DNAT skips zero host ports and cross-family mappings handled by docker-proxy. Hairpin masquerade only applies when hairpin is enabled.

## State And Persistence
State is nftables table rules in network-specific chains and shared NAT/raw chains. Duplicate per-container forwarding and hairpin rules are marked with `IgnoreExist` semantics where needed.

## Dependencies And Integration Points
Uses internal `nftables`, `types.PortBinding`, `net.JoinHostPort`, logging, and the parent network config. Called from bridge port mapping and live-restore replay.

## Risks And Edge Cases
Multiple host ports for one container port can create duplicate rules; current behavior relies on idempotent add/delete rather than refcounting. IPv6 link-local sources are skipped for DNAT. WSL2 loopback accept is IPv4-only.

## Test Signals
Nftabler golden tests validate rule output; bridge port mapping tests validate that expected firewall port bindings are passed to the firewaller abstraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/port.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/wsl2.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/wsl2.go

## Purpose
Adds nftables NAT exception logic for WSL2 mirrored networking loopback traffic.

## Important APIs, Types, And Functions
`mirroredWSL2Workaround` appends a rule to the shared `natChain` returning early for `iifname "loopback0"` and IPv4 destination `127.0.0.0/8`.

## Control Flow
`Nftabler.init` calls this helper only when hairpin is disabled, WSL2 mirrored mode is detected, and the table family is IPv4.

## State And Persistence
State is one nftables rule in the backend-owned table. It persists until the table is deleted or recreated.

## Dependencies And Integration Points
Uses internal `nftables.Modifier`. It mirrors the iptables WSL2 workaround and integrates with docker-proxy loopback behavior.

## Risks And Edge Cases
Assumes WSL2 uses `loopback0` and that IPv6 loopback from Windows is not supported in this path. Missing the rule can make Windows-originated localhost traffic reach containers with an unroutable source.

## Test Signals
Nftabler golden tests include WSL2-specific output only for combinations where IPv4 loopback/proxy behavior is affected.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/wsl2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/labels.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/labels.go

## Purpose
Defines public bridge-driver option labels used in network creation/configuration.

## Important APIs, Types, And Functions
Constants include `BridgeName`, `EnableIPMasquerade`, `IPv4GatewayMode`, `IPv6GatewayMode`, `EnableICC`, `InhibitIPv4`, `DefaultBindingIP`, `DefaultBridge`, and `TrustedHostInterfaces`.

## Control Flow
There is no executable flow. Other bridge configuration code reads these keys from network labels/options and maps them into `networkConfiguration`.

## State And Persistence
Labels become persisted network configuration through `bridge_store.go` and are visible as user-facing Docker network options.

## Dependencies And Integration Points
No imports. Integrated with Docker CLI/API network creation, `netlabel.GenericData`, config validation, and bridge tests that pass labels.

## Risks And Edge Cases
These string constants are part of a user-facing compatibility surface. Renaming or changing semantics would break existing network creation workflows and persisted configs.

## Test Signals
`TestCreateFullOptionsLabels` validates label decoding for bridge name, default bridge, ICC, masquerade, default binding IP, host IPv4, and IPv6 gateway config.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/network_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/network_linux_test.go

## Purpose
Tests bridge endpoint creation, joining, duplicate detection, IPv6 enablement behavior, and endpoint deletion in isolated Linux namespaces.

## Important APIs, Types, And Functions
Tests include `TestLinkCreate`, `TestLinkCreateTwo`, `TestLinkCreateNoEnableIPv6`, and `TestLinkDelete`. They use helper endpoint fixtures from `bridge_linux_test.go`, `newDriver`, `CreateNetwork`, `CreateEndpoint`, `Join`, and `DeleteEndpoint`.

## Control Flow
Each test creates a driver and bridge network, then exercises endpoint creation/join/delete. Assertions inspect veth source link existence, MTU inheritance, assigned endpoint IPs, configured gateways, duplicate endpoint errors, and nil IPv6 fields when IPv6 is not enabled.

## State And Persistence
State is temporary bridge/netlink/driver state plus temp datastore. No long-lived repository state is changed.

## Dependencies And Integration Points
Uses `drvregistry`, `netlabel`, `nlwrap`, `netnsutils`, and `storeutils`. Integrates driver API callbacks with netlink-created veth pairs and bridge network config.

## Risks And Edge Cases
Tests require namespace/netlink privileges. Duplicate endpoint handling checks error type and message. IPv6 IPAM data may be present even when bridge config disables IPv6, and the test ensures it is ignored.

## Test Signals
Passing tests signal correct endpoint lifecycle, duplicate endpoint rejection, gateway assignment, veth MTU propagation, IPv4/IPv6 address containment, and deletion error handling for empty IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/network_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux.go

## Purpose
Coordinates bridge published-port allocation, port mapper calls, firewall programming, docker-proxy startup, operational state storage, and cleanup.

## Important APIs, Types, And Functions
`addPortMappings` normalizes requested bindings and groups same-port allocations. `mapPorts` calls registered port mappers, applies firewall rules, and starts proxies. `sortAndNormPBs`, `needSamePort`, `configurePortBindingIPv4`, and `configurePortBindingIPv6` derive per-family requests. `releasePorts`, `unmapPBs`, `reapplyPerPortIptables`, `collectFirewallPorts`, `toNATBinding`, and `toFwdBinding` handle cleanup/replay/conversion.

## Control Flow
Requests are normalized by endpoint addresses, default host IP, gateway mode, and existing port-binding state. Bindings that differ only by host IP are grouped so they receive the same host port. Mapping reserves/binds ports through the selected mapper, adds firewall rules from mapped NAT/forwarding data, starts docker-proxy when enabled and supported, and registers defers to undo every step on failure.

## State And Persistence
Endpoint `portMapping` stores operational mappings, stop-proxy callbacks, sockets, mapper names, NAT/forwarding metadata, and selected host ports. Persistent restore uses saved mappings with collapsed ranges to re-reserve previous ports.

## Dependencies And Integration Points
Uses `drvregistry.PortMappers`, `portmapperapi`, `portallocator`, `portmapper.StartProxy`, `netutils.IsV6Listenable`, firewaller network methods, and bridge endpoint/network state. Integrates NAT and routed port mappers plus rootlesskit clients.

## Risks And Edge Cases
Cross-family host IPv6 to container IPv4 requires docker-proxy. Routed mode disables NAT and ignores specific host ports. Default host IP selection, IPv4-mapped addresses, host port ranges, busy ports, loopback bindings, and proxy socket filter detachment all affect behavior. Cleanup must stop proxies, unmap ports, and remove firewall rules without leaking state.

## Test Signals
`port_mapping_linux_test.go` covers default mappings, explicit/ranged/busy ports, IPv4-mapped addresses, IPv6-to-IPv4 proxy behavior, routed mode, rootless clients, same-port grouping, release errors, and stub firewaller calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux_test.go

## Purpose
Validates bridge port mapping behavior across IPv4/IPv6, NAT/routed gateway modes, docker-proxy, rootless port drivers, host-port ranges, defaults, loopback, and cleanup failures.

## Important APIs, Types, And Functions
`TestPortMappingConfig` and `TestPortMappingV6Config` exercise full driver flow. `TestAddPortMappings` contains the large table for `addPortMappings`. Helpers include `loopbackUp`, `newIPNet`, `proxyCall`, `mockPortDriverClient`, and `stubPortMapper`.

## Control Flow
Tests create isolated namespaces, install stub or real NAT/routed port mappers, optionally mock `startProxy`, construct bridge networks/endpoints, call `addPortMappings` or full `Join`/`ProgramExternalConnectivity`, then verify returned mappings, firewall stub ports, proxy calls, port driver state, logs, and release behavior.

## State And Persistence
State includes allocated ports from `portallocator`, temporary listening sockets for busy-port simulation, fake proxy maps, mock rootless open-port maps, and endpoint operational port mapping. All are reset per test namespace.

## Dependencies And Integration Points
Uses `nat` and `routed` port mapper packages, rootless port driver client interface, `netlink`, `netnsutils`, `storeutils`, `logrus`, and the stub firewaller.

## Risks And Edge Cases
The table covers high-risk cases: host port exhaustion, first port busy, same host port across multiple host IPs, NAT disabled with specific host addresses, no proxy for IPv6-to-IPv4, rootless IPv6 unsupported, release errors from proxies, and IPv4-mapped addresses.

## Test Signals
Passing tests signal correct binding expansion, stable selected host ports, expected log warnings for ignored mappings, correct proxy lifecycle, correct rootless child host IPs, and complete cleanup through `releasePorts`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup.go

## Purpose
Provides a small ordered setup pipeline for applying bridge network setup steps with OpenTelemetry spans.

## Important APIs, Types, And Functions
`setupStep` stores a name and `stepFn`. `stepFn` accepts `networkConfiguration` and `bridgeInterface`. `bridgeSetup` stores config, bridge, and queued steps. `newBridgeSetup`, `apply`, and `queueStep` manage the pipeline.

## Control Flow
Callers queue named setup functions, then `apply` iterates in order. Each step runs inside a span named from the bridge span prefix and step name, records success/error, ends the span, and stops on first error.

## State And Persistence
Only in-memory step slices are held. Effects are produced by the queued functions: netlink devices, addresses, sysctls, and firewall state.

## Dependencies And Integration Points
Uses `context`, OpenTelemetry, and `otelutil.RecordStatus`. It is the orchestration layer for setup files such as device, IPv4/IPv6, forwarding, and bridge netfiltering.

## Risks And Edge Cases
Step order is semantically important and errors stop later setup, so queued order must match bridge lifecycle requirements. The current `stepFn` does not accept context; `apply` creates a child context for future compatibility.

## Test Signals
No direct tests in this subset; behavior is exercised indirectly through network creation tests that depend on successful setup sequencing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_bridgenetfiltering.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_bridgenetfiltering.go

## Purpose
Enables bridge netfilter sysctls when packet forwarding is active so bridged packets traverse iptables/ip6tables filtering.

## Important APIs, Types, And Functions
`setupIPv4BridgeNetFiltering` checks global IPv4 forwarding and enables `/proc/sys/net/bridge/bridge-nf-call-iptables`. `setupIPv6BridgeNetFiltering` checks per-bridge IPv6 forwarding and enables `/proc/sys/net/bridge/bridge-nf-call-ip6tables`. Helpers include `loadBridgeNetFilterModule`, `enableBridgeNetFiltering`, `getKernelBoolParam`, and `isRunningInContainer`.

## Control Flow
If forwarding is disabled, setup is a no-op. If enabled, the code loads `br_netfilter`, reads the target sysctl, and writes `1` when needed. Missing bridge sysctls inside a Docker container are logged and ignored; other failures can be ignored via `DOCKER_IGNORE_BR_NETFILTER_ERROR=1`.

## State And Persistence
State is kernel module/sysctl state under `/proc/sys`. Changes persist until the host sysctl is changed or rebooted according to system policy.

## Dependencies And Integration Points
Uses `modprobe.LoadModules`, `os`, `syscall`, and logging. Called during bridge setup when filtering behavior is required for ICC restriction or running without userland proxy.

## Risks And Edge Cases
Host kernel support, containerized daemon environments, and permissions affect behavior. Ignoring errors can leave host traffic less restricted than expected. IPv6 requires a bridge name to check the per-interface forwarding sysctl.

## Test Signals
Indirectly covered by bridge setup tests; targeted tests would mock procfs/module availability and environment variables.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_bridgenetfiltering.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux.go

## Purpose
Creates and configures the Linux bridge device: bridge creation, MTU, IPv6 router advertisement sysctl, and link-up state.

## Important APIs, Types, And Functions
`setupDevice` creates a `netlink.Bridge` with a random MAC and enforces default bridge naming rules. `setupMTU` sets MTU. `setupDefaultSysctl` disables IPv6 router advertisements on the bridge when the sysctl exists. `setupDeviceUp` brings the link up and refreshes cached link flags.

## Control Flow
Bridge creation rejects a non-default bridge name when `DefaultBridge` is true, assigns a generated MAC, and calls `LinkAdd`. MTU and sysctl steps are independent. Link-up calls `LinkSetUp`, then attempts `LinkByName` to refresh `bridgeInterface.Link`.

## State And Persistence
State is kernel netlink device state and `/proc/sys/net/ipv6/conf/<bridge>/accept_ra`. The random MAC becomes the bridge hardware address.

## Dependencies And Integration Points
Uses `nlwrap.Handle`, `netlink`, `netutils.GenerateRandomMAC`, `errdefs`, `os`, and logging. Invoked by the bridge setup pipeline and tested in isolated namespaces.

## Risks And Edge Cases
Creating a default bridge with a custom name is forbidden for compatibility. MTU limits are kernel-dependent. Missing IPv6 sysctl is logged as info and ignored, which is appropriate on IPv4-only hosts.

## Test Signals
`setup_device_linux_test.go` validates bridge creation down, rejection of non-default default bridge, link-up, random MAC uniqueness, MTU 9000 success, and MTU 65536 `EINVAL`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux_test.go

## Purpose
Tests Linux bridge device setup helpers against kernel netlink behavior in isolated namespaces.

## Important APIs, Types, And Functions
Tests include `TestSetupNewBridge`, `TestSetupNewNonDefaultBridge`, `TestSetupDeviceUp`, `TestGenerateRandomMAC`, `TestMTUBiggerThan1500`, and `TestMTUBiggerThan64K`.

## Control Flow
Each netlink test creates an `nlwrap.Handle`, constructs a `networkConfiguration` and `bridgeInterface`, calls setup helpers, then checks link existence, link flags, error types/messages, or MTU syscall errors.

## State And Persistence
State is temporary namespace-local bridge devices and link attributes. Tests clean up by namespace teardown.

## Dependencies And Integration Points
Uses `netnsutils`, `nlwrap`, `netutils`, `syscall`, and `gotest.tools`. It directly validates `setup_device_linux.go`.

## Risks And Edge Cases
Requires netlink privileges. MTU behavior references specific kernel bridge limits, so very old kernels could differ. The random MAC test is probabilistic but the chance of collision is negligible.

## Test Signals
Passing tests signal correct bridge creation semantics, non-default default-bridge rejection as permission denied, link-up refresh, and expected kernel validation for large MTUs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding.go

## Purpose
Checks and configures host IPv4/IPv6 forwarding sysctls and optionally asks the firewaller to set a default FORWARD DROP policy when enabling forwarding.

## Important APIs, Types, And Functions
Constants name forwarding sysctls. `filterForwardDropper` abstracts `FilterForwardDrop`. `checkIPv4Forwarding`, `setupIPv4Forwarding`, `checkIPv6Forwarding`, `setupIPv6Forwarding`, and `configureIPForwarding` implement checks/writes.

## Control Flow
Check functions read sysctls and return user-facing errors if forwarding is disabled. Setup functions write `1` to the required sysctls, register rollback defers if they changed values, and call `FilterForwardDrop` only when forwarding was newly enabled and requested. Rollback resets sysctls to `0` if later setup fails.

## State And Persistence
State is host `/proc/sys/net/ipv4/ip_forward` and IPv6 `default`/`all` forwarding files. These are host-global and security-sensitive.

## Dependencies And Integration Points
Uses firewaller `IPVersion`, `os.ReadFile/WriteFile`, and logging. Called by daemon bridge setup when IP forwarding management is enabled or checked.

## Risks And Edge Cases
The duplicate zero-length read check is harmless but redundant. Partial failure after changing one IPv6 sysctl triggers rollback. Enabling forwarding without filter DROP can expose host routing depending on firewall rules.

## Test Signals
`setup_ip_forwarding_test.go` validates sysctl writes, firewaller callback family selection, and check errors when forwarding is disabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding_test.go

## Purpose
Tests IP forwarding setup/check helpers and their interaction with the firewaller default-DROP callback.

## Important APIs, Types, And Functions
`ffDropper` records whether `FilterForwardDrop` was called for IPv4 or IPv6. Tests include `TestSetupIPForwarding`, `TestSetupIP6Forwarding`, `TestCheckForwarding`, and helper `setForwarding`.

## Control Flow
Tests run in isolated OS context, force forwarding sysctls to `0`, call setup with `wantFFD` true/false, assert callback state and sysctl contents, then verify check functions fail when disabled and pass when enabled.

## State And Persistence
State is temporary namespace/proc sysctl values for IPv4 and IPv6 forwarding. `setForwarding` writes all three sysctls used by the implementation.

## Dependencies And Integration Points
Uses `netnsutils`, `os`, `firewaller`, and `gotest.tools`. It directly validates `setup_ip_forwarding.go`.

## Risks And Edge Cases
Requires writable forwarding sysctls in the test namespace. Tests focus on success and disabled-check paths; they do not inject write failures to validate rollback defers.

## Test Signals
Passing tests signal correct sysctl enablement, correct IPv4/IPv6 callback dispatch, no callback when not requested, and clear error messages for disabled forwarding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ip_forwarding_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux.go

## Purpose
Configures IPv4 bridge addressing, gateway selection, and loopback-address routing for hairpin/localhost behavior.

## Important APIs, Types, And Functions
`selectIPv4Address` chooses an existing address matching a selector or the first available address. `setupBridgeIPv4` assigns/reconciles the bridge IPv4 address and default gateway. `setupGatewayIPv4` validates and stores a configured default gateway. `setupLoopbackAddressesRouting` enables per-bridge `route_localnet`.

## Control Flow
Bridge IPv4 setup caches `AddressIPv4`, optionally lists existing IPv4 addresses, removes a mismatched selected address, adds the configured address, and stores the gateway for non-internal networks. Gateway setup checks containment and rejects internal networks. Loopback routing reads the sysctl and writes `1` if not already enabled.

## State And Persistence
State is kernel netlink IPv4 address state, cached bridge/gateway fields, and `/proc/sys/net/ipv4/conf/<bridge>/route_localnet`. The bridge driver's persisted network config supplies the desired address and gateway.

## Dependencies And Integration Points
Uses `netlink`, `types.CompareIPNet`, `errInvalidGateway`, `os`, `filepath`, and logging. Invoked by the bridge setup pipeline and port/hairpin behavior.

## Risks And Edge Cases
`selectIPv4Address` errors on an empty pool but setup ignores that error because no current address is acceptable. Internal networks cannot have a gateway. `route_localnet` changes can affect host loopback routing security for the bridge interface.

## Test Signals
Covered indirectly by bridge creation, existing bridge reuse, gateway, and port mapping tests; focused tests would check address replacement and route_localnet sysctl behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux.go -->
