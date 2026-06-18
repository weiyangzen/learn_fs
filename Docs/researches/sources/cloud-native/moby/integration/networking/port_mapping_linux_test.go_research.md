# sources/cloud-native/moby/integration/networking/port_mapping_linux_test.go

## Purpose
Comprehensive Linux integration coverage for published port behavior, NAT disablement, direct routing, userland proxy, loopback scoping, firewall marks, raw table skipping, rootless loopback address distinction, and host/container/remote access paths.

## Important APIs, Types, And Functions
Uses `networktypes.PortMap`, `PortBinding`, `bridge` driver options (`IPv4GatewayMode`, `IPv6GatewayMode`, `TrustedHostInterfaces`), daemon flags (`--userland-proxy`, `--allow-direct-routing`, `--bridge-accept-fwmark`), synthetic L3 segments from `testutils/networking`, and BusyBox/httpd/nc/curl/wget/ping commands. Helpers include `getIfaceAddrs`, `enableIPv6OnAll`, `retryFlaky`, `sendPayloadFromHost`, and `getContainerStdout`.

## Control Flow
The file starts isolated daemons for most cases, creates bridge networks with IPv4/IPv6/gateway-mode combinations, runs server containers with mapped or exposed ports, then probes from the host, peer containers, or synthetic remote hosts. `TestDisableNAT` checks inspect port metadata for routed gateway modes. Hairpin tests cover TCP and UDP mapped access from other networks. Host access tests exercise loopback, physical interface, IPv4/IPv6, userland proxy on/off, and bridge-nf-call-iptables. Direct-routing tests build L3 segments, add routes, and compare NAT, nat-unprotected, and routed modes for ping and HTTP to mapped/unmapped ports. Attack-oriented tests confirm exposed ports and loopback-published ports are not directly reachable unless trusted interfaces or `--allow-direct-routing` apply.

## State And Persistence Behavior
Tests mutate daemon port allocator state, host sysctls, host interface IPv6 addresses, L3 namespace routes, iptables/nftables state, and container log streams. `TestRestartUserlandProxyUnder2MSL` verifies a port can be reused after a proxy connection enters TIME_WAIT. `TestMixAnyWithSpecificHostAddrs` validates allocator consistency across any-address and specific-address bindings.

## Dependencies And Integration Points
Deeply integrates with Linux networking, iptables/nftables raw and filter chains, firewalld presence, docker-proxy, RootlessKit behavior, L3 namespace utilities, BusyBox tools, golden files for raw rules, and stdcopy log decoding.

## Risks
High flake surface: host sysctl writes, fixed host ports, remote route simulation, TIME_WAIT timing, firewalld rpfilter behavior, network access for host address discovery, and UDP retries. Several tests skip rootless because firewall rules or namespace visibility would not reflect host behavior. Exact golden raw rules are backend- and environment-sensitive.

## Test Signals
Signals include inspect `Ports` equality, HTTP status/body checks, ping/curl exit codes, daemon process behavior, container stdout payload detection, golden iptables raw table snapshots, and assertions about port allocator uniqueness and loopback address routing.
