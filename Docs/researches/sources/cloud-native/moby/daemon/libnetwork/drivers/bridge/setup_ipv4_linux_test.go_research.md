# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux_test.go

Purpose: Linux bridge IPv4 setup tests exercise the bridge device creation helper, IPv4 address programming, and default gateway storage behavior used by the bridge driver setup pipeline.

Important APIs and functions: `setupTestInterface` creates a `networkConfiguration` with `DefaultBridgeName`, builds a `bridgeInterface` around an `nlwrap.Handle`, and calls `setupDevice`. `TestSetupBridgeIPv4Fixed` validates `setupBridgeIPv4` by adding `192.168.1.1/24` and checking `AddrList` for `FAMILY_V4`. `TestSetupGatewayIPv4` validates `setupGatewayIPv4` accepts a gateway inside the bridge network and records it in `br.gatewayIPv4`.

Control flow: each test enters an isolated OS network namespace via `netnsutils.SetupTestOSContext`, opens a netlink handle, creates or prepares the bridge interface, calls the setup function under test, then inspects netlink state or in-memory gateway fields.

State and persistence: no datastore state is touched. The tests mutate only the temporary network namespace and `bridgeInterface` fields.

Dependencies and integration points: depends on `nlwrap`, `netlink`, and the bridge setup helpers defined in sibling files. It verifies integration between bridge setup code and Linux netlink address state.

Risks: tests require netlink namespace support and sufficient privileges. They cover the positive path but not invalid IPv4 gateway rejection or address replacement behavior.

Test signals: strong signal for bridge IPv4 address programming and gateway field assignment in an isolated namespace.
