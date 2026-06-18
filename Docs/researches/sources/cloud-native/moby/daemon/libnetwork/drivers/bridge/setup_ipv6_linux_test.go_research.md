# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv6_linux_test.go

Purpose: Tests Linux bridge IPv6 setup by verifying procfs enablement, netlink address assignment, and gateway configuration.

Important APIs and functions: `TestSetupIPv6` creates a bridge through `setupTestInterface`, sets `AddressIPv6`, calls `setupBridgeIPv6`, reads `/proc/sys/net/ipv6/conf/<bridge>/disable_ipv6`, and checks the bridge has the requested IPv6 address. `TestSetupGatewayIPv6` verifies `setupGatewayIPv6` stores an in-subnet gateway in `br.gatewayIPv6`.

Control flow: tests run in a temporary network namespace, use `nlwrap.NewHandle`, call the implementation, then inspect procfs and netlink `FAMILY_V6` addresses.

State and persistence: only temporary namespace kernel state and in-memory `bridgeInterface` fields are mutated.

Dependencies and integration points: exercises `setup_ipv6_linux.go`, `setupDevice` through `setupTestInterface`, and Linux netlink/procfs integration.

Risks: requires IPv6 sysctls and netlink privilege in the test namespace. Negative cases for invalid gateway and isolated mode are not covered.

Test signals: confirms the expected positive IPv6 setup path and catches regressions where IPv6 remains disabled or the requested bridge address is not programmed.
