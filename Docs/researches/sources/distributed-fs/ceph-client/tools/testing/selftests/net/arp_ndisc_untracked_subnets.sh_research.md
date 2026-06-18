# sources/distributed-fs/ceph-client/tools/testing/selftests/net/arp_ndisc_untracked_subnets.sh

Purpose: Tests acceptance of untracked ARP gratuitous updates and IPv6 unsolicited neighbor advertisements for same-subnet and off-subnet hosts.

Important APIs/types/functions: Uses `arp_accept`, `accept_untracked_na`, `drop_unsolicited_na`, `ndisc_notify`, veth namespaces, `arping`, `tc flower` counters for IPv6 NA observation, `ip neigh`, and `lib.sh` helpers.

Control flow: Command-line `-t` selects `arp`, `ndisc`, or both. ARP setup creates router/host namespaces, configures IPv4 addresses and router sysctl, sends gratuitous ARP from host, and verifies neighbor entry presence according to `arp_accept` values 0, 1, or 2 with same-subnet distinction. IPv6 setup creates veth namespaces, adds a `tc` ingress filter for NA packets, enables host notification, configures router forwarding and `accept_untracked_na`, waits for one NA packet, and verifies stale neighbor presence according to sysctl and subnet relation.

State and persistence behavior: Creates temporary namespaces, veths, sysctls, `tc` qdisc/filter state, and neighbor entries. Cleanup removes namespaces.

Dependencies and integration points: Requires root, `ip`, `tcpdump` presence check, `arping`, `tc`, IPv6, and `lib.sh`.

Risks: The IPv6 path relies on asynchronous unsolicited NA generation and `tc` packet counters. The script mutates global shell variables (`HOST_ADDR`, `HOST_ADDR_V6`) between cases, so cleanup/setup sequencing matters. It checks for `tcpdump` although it does not directly capture packets in this script.

Test signals: OK/FAIL lines for each ARP and ND combination show whether untracked neighbor advertisements are accepted only under configured modes.
