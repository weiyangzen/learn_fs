# sources/cloud-native/moby/integration/container/nat_test.go

Purpose: Network address translation tests for published ports via external address, localhost, and container-shared network namespace.

Important APIs and flow: `startServerContainer` runs a netcat listener with exposed port and explicit `PortBindings`. `TestNetworkNat` dials the host `eth0` address and reads the expected message. `TestNetworkLocalhostTCPNat` dials `localhost`. `TestNetworkLoopbackNat` runs a second container sharing the server container network namespace and connects to the host external address. `getExternalAddress` selects the first IPv4 on `eth0` when available.

State and dependencies: Uses host networking stack, published ports, netcat in busybox, and the make-test integration environment exposing `eth0`. Skips remote and some Windows/GitHub Actions cases.

Risks and signals: It catches port publishing/NAT regressions for localhost, external host IP, and loopback through shared namespaces. Failures usually indicate libnetwork, iptables, rootlesskit, or host environment issues.
