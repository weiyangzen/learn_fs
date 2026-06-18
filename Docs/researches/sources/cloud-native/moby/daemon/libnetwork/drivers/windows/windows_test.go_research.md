# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows_test.go

Purpose: defines Windows-only integration-style tests and a fake endpoint interface for the HNS driver. Important pieces are `testNetwork`, `TestNAT`, `TestTransparent`, and `testEndpoint`, which implements `driverapi.InterfaceInfo`, `InterfaceNameInfo`, and join-info gateway methods.

Control flow: `testNetwork` creates a temp-store driver, configures an IPv4 IPAM pool/gateway, creates a Windows network, creates then deletes one endpoint, and finally deletes the network. The fake endpoint returns optional address/MAC data and rejects attempts to overwrite an already-present MAC or set nil IP/MAC values. Gateway, static route, namespace, and created-in-container hooks are no-ops except `DisableGatewayService`, which records the call.

State/dependencies: tests depend on `hcsshim` being usable on a Windows host, the libnetwork driver API, `types.ParseCIDR`, and `storeutils.NewTempStore`. Both NAT and transparent tests are skipped because they do not work in CI and historically did not run. Risk signal: real HNS behavior is under-tested by default; these tests mostly document expected driver lifecycle and fake-interface contracts.
