# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv6_linux.go

Purpose: Implements Linux bridge IPv6 setup, including toggling `/proc/sys/net/ipv6/conf/<bridge>/disable_ipv6`, programming bridge IPv6 addresses, and validating the configured IPv6 default gateway.

Important APIs and functions: `linkLocalPrefix` records `fe80::/64`. `setupBridgeIPv6` reads the bridge `disable_ipv6` procfs file, disables IPv6 for isolated gateway mode, enables it otherwise, then delegates address reconciliation to `bridgeInterface.programIPv6Addresses`. `setupGatewayIPv6` validates that `DefaultGatewayIPv6` is contained in `AddressIPv6` and stores it in `bridgeInterface.gatewayIPv6`.

Control flow: isolated IPv6 mode returns early after disabling IPv6 and copying `AddressIPv6` into `i.bridgeIPv6`. Non-isolated mode ensures procfs contains `0\n`, then calls into the interface address programming routine.

State and persistence: mutates kernel procfs and netlink address state, plus in-memory `bridgeInterface` fields. There is no datastore persistence.

Dependencies and integration points: used as a bridge setup step by the Linux bridge driver. It depends on `networkConfiguration` gateway mode helpers and `bridgeInterface.programIPv6Addresses` from the bridge interface implementation.

Risks: `ipv6BridgeData[0]` assumes procfs returned at least one byte. Procfs writes require privilege and can fail on kernels or namespaces without IPv6 sysctls. Isolated mode deliberately suppresses kernel-assigned link-local addresses, so incorrect gateway mode selection can affect connectivity.

Test signals: covered by `setup_ipv6_linux_test.go` for enabling IPv6, address assignment, and gateway storage; isolated mode is not directly covered here.
