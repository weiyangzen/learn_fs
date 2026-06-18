# sources/cloud-native/moby/integration/networking/nat_windows_test.go

## Purpose
Windows NAT networking coverage for same-network container communication and cross-network hairpin access to a mapped host port.

## Important APIs, Types, And Functions
Uses `testEnv.APIClient`, `network.CreateNoError` with `network.WithDriver("nat")`, container run/attach helpers, `container.WithPortMap`, `networktypes.PortMap`, `net.Dial` to discover host address, and Windows ping/wget commands.

## Control Flow
`TestNatNetworkICC` covers the default `nat` network and a user-created `nat` network. It starts `ctr1`, runs `ctr2` on the same network, and pings by hostname to validate DNS and communication. `TestFlakyPortMappedHairpinWindows` creates separate NAT networks, runs an HTTP server with an ephemeral host port, then uses a client container on another network to access the server via the host address and mapped port.

## State And Persistence Behavior
State is transient networks and containers. The tests validate endpoint registration, DNS records, and host port mappings, but no restart persistence.

## Dependencies And Integration Points
Depends on Windows NAT driver, Windows ping output, host outbound connectivity to determine a source address, and BusyBox/Windows container command availability depending on the test image.

## Risks
The hairpin test is explicitly marked flaky and linked to issue 48881. Host address discovery depends on network access to `hub.docker.com:80`, and port mapping behavior can vary by Windows networking stack.

## Test Signals
Signals are successful ping output, empty stderr, and `wget` stderr containing `404 Not Found` from the mapped HTTP server.
