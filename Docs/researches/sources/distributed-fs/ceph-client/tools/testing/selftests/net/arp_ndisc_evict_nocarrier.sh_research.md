# sources/distributed-fs/ceph-client/tools/testing/selftests/net/arp_ndisc_evict_nocarrier.sh

Purpose: Tests IPv4 `arp_evict_nocarrier` and IPv6 `ndisc_evict_nocarrier` sysctls when a peer veth is brought down and the local link enters `NOCARRIER`.

Important APIs/types/functions: Uses `setup_ns/cleanup_ns` from `lib.sh`, veth pairs, `ip neigh get`, `ping`, per-interface and `all` sysctls for ARP/ND eviction, and root privilege checks.

Control flow: For IPv4 and IPv6 separately, setup creates veth connectivity, assigns addresses, applies the requested sysctl, establishes a neighbor entry by pinging, then brings the peer link down. Enabled tests expect the neighbor entry to be gone; disabled per-interface and disabled `all` tests expect it to remain. Cleanup resets sysctls to defaults and removes links/namespaces.

State and persistence behavior: Temporarily mutates host/network namespace sysctls, neighbor cache entries, veth devices, routes, and namespaces. Cleanup resets tested sysctls to `1`.

Dependencies and integration points: Requires root, `ip`, ping, veth, IPv6, and kselftest lib helpers.

Risks: IPv4 setup touches root namespace veth and default route, so failures before cleanup can disturb the environment. Neighbor creation can fail on systems with unusual MAC address policy, which the script notes. Sysctl inheritance from `all` can be subtle.

Test signals: `ok`/`failed` lines for six cases identify whether neighbor entries are evicted or preserved according to sysctl settings.
