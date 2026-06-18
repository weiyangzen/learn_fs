# sources/cloud-native/moby/integration/daemon/daemon_linux_test.go

Purpose: Linux daemon integration tests covering default bridge IPAM inference, fixed CIDR behavior, user-supplied bridges, swarm startup without nftables, and daemon shutdown with an open events connection.

Important APIs and helpers: `TestDaemonDefaultBridgeWithFixedCidrButNoBip`, `TestDaemonDefaultBridgeIPAM_Docker0`, `TestDaemonDefaultBridgeIPAM_UserBr`, `defaultBridgeIPAMTestCase`, `testDefaultBridgeIPAM`, `newHostInL3Seg`, `createBridge`, `TestSwarmNoNftables`, and `TestDaemonShutsDownQuicklyDespiteEventsConnection`.

Control flow: the IPAM tests create isolated network namespaces and optional bridge addresses, start sub-daemons with combinations of `--fixed-cidr`, `--fixed-cidr-v6`, `--bip`, `--bip6`, `--bridge`, and default address pools, then inspect the default bridge network and compare IPAM config. Link-local gateway placeholders are replaced with the kernel-assigned address before comparison. Startup-error cases assert daemon startup failure. Swarm and shutdown tests start daemons with selected firewall behavior and verify swarm init or stop timing while API connections remain open.

State and persistence: most state is kernel network namespace state: bridge devices, assigned addresses, route/sysctl side effects, and daemon-created libnetwork bridge configuration. The tests isolate that state to avoid leaking iptables or bridge rules into other integration tests.

Dependencies and integration: depends on rootful Linux network namespaces, `vishvananda/netlink`, Moby libnetwork wrappers, internal networking test utilities, daemon harness helpers, and network inspect API. It integrates daemon command-line parsing with libnetwork bridge IPAM and kernel networking.

Risks: highly environment-dependent: rootless mode skips, network namespace setup can fail, firewall backend differences matter, and exact IPAM expectations encode historical compatibility behavior. These tests are sensitive to bridge address selection rules.

Test signals: strong regression coverage for fixed-CIDR/bip compatibility, bridge address inference, IPv6 link-local handling, historical IPv4 permissiveness vs IPv6 rejection, swarm startup under firewall constraints, and graceful daemon shutdown with live event streams.
