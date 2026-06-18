# sources/cloud-native/moby/integration/networking/drivers_windows_test.go

## Purpose
Windows-specific integration coverage for Docker network drivers and endpoint behavior. It validates NAT, transparent, and l2bridge network creation; NAT port mapping; DNS resolution; lifecycle connect/disconnect/delete operations; network isolation; and endpoint management for multiple containers on one network.

## Important APIs, Types, And Functions
Uses `testEnv.APIClient`, `client.NetworkCreateOptions`, `NetworkInspect`, `NetworkConnect`, `NetworkDisconnect`, `container.Run`, `RunAttach`, `Inspect`, `WithNetworkMode`, `WithExposedPorts`, `WithPortMap`, and Windows ping/PowerShell commands. `network.WithDriver` and `network.WithOption("com.docker.network.windowsshim.dnsservers", ...)` supply Windows driver options. `poll.WaitOn` wraps host-to-container HTTP readiness.

## Control Flow
`TestWindowsNetworkDrivers` iterates `nat`, `transparent`, and `l2bridge`, creates a network, tolerates known l2bridge host-config failure, then inspects driver/name. `TestWindowsNATDriverPortMapping` runs a PowerShell `HttpListener` in a NAT container, maps port 80 to host 8080, checks inspect metadata, and polls `http://localhost:8080`. `TestWindowsNetworkDNSResolution` creates NAT networks with optional DNS options and validates name resolution by pinging one container from another. Lifecycle and isolation tests attach/detach containers and assert inspect state or failed cross-network pings. Endpoint management creates three containers and checks network inspect container count plus same-network pings.

## State And Persistence Behavior
State is limited to temporary Windows networks and containers. The lifecycle test explicitly proves endpoint detachment removes inspect state, reconnection restores it, and network deletion makes inspect fail. No daemon restart or persistent on-disk state is tested.

## Dependencies And Integration Points
Depends on Windows container networking, HNS/network drivers, Windows ping output, PowerShell, HTTP listener behavior, and container runtime support. `TestWindowsNetworkLifecycle` skips Windows containerd because `NetworkConnect` is known unsupported in that mode.

## Risks
Tests can be environment-sensitive: transparent and l2bridge require host network configuration, custom DNS option behavior may vary by Windows networking stack, ping output localization could affect string assertions, and fixed host port 8080 can collide with local services.

## Test Signals
Signals include driver/name equality in network inspect, port binding metadata, successful host HTTP response containing `OK`, ping success text (`Sent = 1, Received = 1, Lost = 0`), failed ping indicators for isolation, and network inspect container count.
