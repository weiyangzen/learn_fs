<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/ipvlan_test.go -->
# sources/cloud-native/moby/integration/network/ipvlan/ipvlan_test.go

Purpose: Linux ipvlan driver integration suite covering persistence, parent/subinterface handling, L2/L3/L3S routing, internal networks, multi-subnet dual-stack behavior, IPAM status, overlapping IPAM pools, DNS forwarding, point-to-point allocation, and custom interface names.

Important APIs/types/functions: top-level tests include `TestDockerNetworkIpvlanPersistence`, `TestDockerNetworkIpvlan`, `TestIpvlanIPAM`, `TestIpvlanIPAMOverlap`, `TestIPVlanDNS`, `TestPointToPoint`, and `TestEndpointWithCustomIfname`. Helper tests create dummy parents with `integration/network` helpers and networks with `net.WithIPvlan`, IPAM, IPv4/IPv6 flags, internal mode, and endpoint `netlabel.Ifname`.

Control flow: persistence creates a VLAN parent, creates an ipvlan network, restarts the daemon, and checks network availability. The table-driven driver test starts a fresh daemon per subcase and runs subinterface, overlap, nil-parent, internal, L2/L3 multi-subnet, and addressing checks. IPAM tests create networks under multiple API versions/IPv4/IPv6 combinations, run containers, inspect loopback/eth0 address state, sysctls, and API 1.52 subnet status while ensuring API 1.51 hides status. DNS tests use a loopback test resolver and compare parent/internal combinations for expected forwarding or `SERVFAIL`.

State/persistence: mutates dummy/VLAN links, creates ipvlan networks/containers, relies on daemon restart persistence, and observes per-network IPAM counters. No repository state.

Dependencies/integration: requires Linux privileged networking, non-rootless local daemon, BusyBox image, `ip` commands inside containers, Docker network/client APIs, `cmpopts.EquateEmpty`, and helper package aliases `net` and `n`.

Risks: hard-coded link names and subnets can collide if cleanup fails. Parentless ipvlan behaves like internal networking, and tests rely on that subtle semantic. Overlapping IPAM status counts are global across same-driver subnets, so allocator changes can require updates. Legacy API behavior intentionally ignores `enableIPv4=false` for API 1.46.

Test signals: pings, route/default-gateway assertions, DNS lookup outcomes, network availability checks, inspect IPAM status, sysctl values, and custom interface-name checks provide broad coverage of ipvlan functional and compatibility behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/ipvlan_test.go -->
