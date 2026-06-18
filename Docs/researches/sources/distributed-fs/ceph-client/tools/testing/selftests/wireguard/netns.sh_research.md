# sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/netns.sh

## Purpose

`netns.sh` is WireGuard's large network-namespace integration stress test. It builds multiple namespace topologies, configures WireGuard peers with generated keys, and validates IPv4/IPv6 transport, throughput, MTU behavior, roaming, crypto routing, nested WireGuard, NAT traversal, policy routing, source-address stickiness, netlink split responses, key handling, low-order point rejection behavior, and namespace lifetime cleanup.

## Important APIs, Types, and Functions

The script uses `ip netns`, `ip -n`, `wg`, `ping`, `ping6`, `iperf3`, `ncat`, `iptables`, `ss`, `conntrack`-related sysctls, `/proc/sys/net/core/message_cost`, and `/dev/kmsg`. Helper functions include `pretty()`, `pp()`, namespace command wrappers `n0/n1/n2` and `ip0/ip1/ip2`, `waitiperf()`, `waitncatudp()`, `waitiface()`, `cleanup()`, `configure_peers()`, and `tests()`. It exports `WG_HIDE_KEYS=never` so key assertions can compare exact values.

## Control Flow

Startup creates three namespaces, creates WireGuard devices in a central namespace and moves peers into endpoint namespaces, generates four private/public key pairs plus a preshared key, and configures base peer addresses. `tests()` runs ping and iperf3 coverage for IPv4, IPv6, UDP, TCP, and parallel TCP. The script then runs many scenario blocks: IPv4 and IPv6 outer endpoints at normal and large MTU, route-MTU padding, endpoint roaming, crypto-RP filtering with more-specific allowed IPs, private-key rotation, WireGuard-over-WireGuard and routing loop checks, NAT and persistent keepalive behavior, bound-device and fwmark routing, onion routing, wg-quick-style default route policy routing, ICMP error routing through NAT, source-address stickiness, persistent keepalives on interface/private-key activation, large netlink/IPC allowed-ips responses, key clearing and public-key derivation behavior, low-order public-key behavior, dst-cache cleanup across namespace deletion, and circular namespace reference cleanup.

## State and Persistence Behavior

All state is intended to be transient: namespaces named with the shell pid, WireGuard/veth/dummy devices, iptables rules, sysctls, generated keys, background iperf/ncat processes, and kernel log observations. `cleanup()` restores `message_cost`, deletes devices and namespaces, kills namespace pids, and exits.

## Dependencies and Integration Points

The script requires root privileges, WireGuard kernel support, `wireguard-tools`, iproute2, iptables legacy behavior for some commands, iperf3, nmap `ncat`, ping utilities, netns support, and optional modules such as `vsock_loopback` are not relevant here. It integrates with WireGuard netlink APIs, routing tables/rules, netfilter NAT/filter/mangle tables, DSA-free ordinary network namespaces, and kernel object lifetime logs.

## Risks and Edge Cases

The test intentionally changes global `/proc/sys/net/core/message_cost`, manipulates iptables, creates many routes/rules, and can be disruptive on a non-isolated host. Some assertions depend on exact transfer byte counters and endpoint string formatting. The routing-loop section prints a prominent warning but continues for a known unsolved architecture behavior. Cleanup depends on namespace names being unique and deletion succeeding.

## Test Signals

Pass signals are command success under `set -e`, successful pings/iperf runs, expected WireGuard transfer counters and latest-handshake timestamps, expected endpoint strings after roaming/source routing, dropped packets in negative crypto routing cases, successful large allowed-ips enumeration counts, no packets sent to low-order peers, and `/dev/kmsg` evidence that created WireGuard objects are destroyed.
