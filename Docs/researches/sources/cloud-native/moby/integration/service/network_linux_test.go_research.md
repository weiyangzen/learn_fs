# sources/cloud-native/moby/integration/service/network_linux_test.go

## Purpose
Exercises Linux Swarm and overlay networking behavior around API compatibility, reconnect idempotency, IPv4 requirements, config-derived swarm-scoped networks, ingress iptables ordering, and firewalld reload recovery.

## Important APIs, Types, And Functions
- `TestDockerNetworkConnectAliasPreV144` starts a daemon with `DOCKER_MIN_API_VERSION=1.43` and validates alias preservation with an API v1.43 client.
- `TestDockerNetworkReConnect` checks duplicate `NetworkConnect` errors do not mutate container network settings.
- `TestSwarmNoDisableIPv4` expects a clear error when disabling IPv4 on a Swarm-scoped network.
- `TestSwarmScopedNetFromConfig` creates a config-only bridge network and a swarm-scoped network from it.
- `TestDockerIngressChainPosition` uses an isolated L3 segment, published ingress port, daemon restart, `wget`, and golden iptables output.
- `TestRestoreIngressRulesOnFirewalldReload` reloads firewalld and verifies ingress remains reachable.

## Control Flow
Tests start Swarm daemons, create overlay or bridge networks, create containers or services, and poll for runtime/network convergence. The ingress-chain test runs daemon and HTTP checks inside an isolated network namespace, checks `DOCKER-FORWARD` before and after restart, and uses golden output. The firewalld test waits for HTTP response before and after `networking.FirewalldReload`.

## State And Persistence
State spans overlay networks, container endpoint settings, Swarm services, iptables chains, firewalld rules, and daemon restart persistence. Network namespace state from `NewL3Segment` is destroyed with `defer`.

## Dependencies And Integration Points
Depends on Linux networking helpers, libnetwork scope constants, Swarm helpers, daemon options, API version negotiation, `iptables`, `wget` or `curl`, firewalld, and gotest golden files. It integrates daemon networking, libnetwork, Swarm ingress, and firewall backends.

## Risks And Edge Cases
Many tests skip rootless, remote daemon, nftables, or missing firewalld cases. Firewall tests are environment-sensitive and can be flaky if host networking differs. Duplicate endpoint comparison needs `cmpopts.EquateComparable` for `netip` values.

## Test Signals
Signals include expected aliases, stable container network settings after rejected reconnect, error text for IPv4-disabled swarm networks, running service tasks on config-derived networks, reachable ingress HTTP returning 404, preserved golden iptables chain ordering, and ingress recovery after firewalld reload.
