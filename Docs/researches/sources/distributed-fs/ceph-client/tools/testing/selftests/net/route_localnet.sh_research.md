<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/route_localnet.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/route_localnet.sh

## Purpose

`route_localnet.sh` tests IPv4 loopback-address routing over a veth link when `route_localnet=1`. It specifically checks that ARP source-selection settings `arp_announce=2` and `arp_ignore=3` do not prevent pinging a peer loopback-range address over veth.

## Important APIs, Types, and Functions

The script defines `setup`, `cleanup`, `run_arp_announce_test`, `run_arp_ignore_test`, and `run_all_tests`. It uses `ip netns`, veth creation, `sysctl net.ipv4.conf.<dev>.route_localnet`, deletion/restoration of the local route for `127.0.0.0/8`, assignment of `127.25.3.4/24` and `127.25.3.14/24`, `ip route flush cache`, and `ping -I veth0`.

## Control Flow

Each subtest calls `setup`, writes one ARP sysctl on both ends, pings from the init namespace veth to the peer namespace's loopback-range address, prints `ok` or `failed`, and calls `cleanup`. `run_all_tests` executes both subtests sequentially.

## State and Persistence Behavior

The script mutates init namespace networking: it creates `veth0`, deletes the local route for `127.0.0.0/8`, assigns a 127/8 address to veth0, writes sysctls, flushes route cache, and then restores the local route in cleanup. It also creates and deletes a peer namespace. Cleanup is called per subtest but there is no global trap, so interruption can leave altered local route state.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include root, veth, namespaces, IPv4 sysctls, and ping. Integration points are `route_localnet`, local table route handling, ARP announce/ignore policy, and route-cache behavior. Risks include host route mutation if not isolated, no exit-status aggregation despite printed failure, cleanup failing if setup partially fails, and missing trap on interrupt. Signals are printed `ok` for both ARP sysctl cases; the script itself does not force a nonzero exit on ping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/route_localnet.sh -->
