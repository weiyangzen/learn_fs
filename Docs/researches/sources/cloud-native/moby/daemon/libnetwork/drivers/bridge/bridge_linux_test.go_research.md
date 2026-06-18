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
