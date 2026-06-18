<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/macvlan_test.go -->
# sources/cloud-native/moby/integration/network/macvlan/macvlan_test.go

Purpose: Linux macvlan driver integration suite covering persistence, parent/subinterface lifecycle, passthru overlap rejection, nil-parent/internal behavior, multi-subnet dual-stack addressing, IPAM status/overlap accounting, DNS forwarding, point-to-point allocation, custom interface names, and attachment when the parent is down.

Important APIs/types/functions: top-level tests include `TestDockerNetworkMacvlanPersistence`, `TestDockerNetworkMacvlan`, `TestMacvlanIPAM`, `TestMacvlanIPAMOverlap`, `TestMACVlanDNS`, `TestPointToPoint`, `TestEndpointWithCustomIfname`, and `TestParentDown`. Helper functions exercise overlap variants, dynamic parent creation, parent preservation/deletion, multi-subnet addressing, and route assertions.

Control flow: the table-driven driver test starts a new daemon for each subcase and manipulates dummy/VLAN parents. Overlap tests check when shared parents are allowed, when passthru blocks sharing, and when generated subinterfaces are deleted only after the final owning network is removed. IPAM tests vary IPv4/IPv6 flags and API version, run a container, inspect addresses/sysctls, and compare API 1.52 status counters with API 1.51 hiding status. DNS tests use a loopback daft DNS resolver to distinguish parent/internal behavior.

State/persistence: creates host dummy/VLAN/tap interfaces, macvlan networks, containers, daemon state across restart, and IPAM allocations. `TestParentDown` creates a tap interface without bringing it up to verify attachment still succeeds.

Dependencies/integration: requires Linux privileged networking, `ip`/`tuntap`, Docker daemon/client helpers, network helper package, BusyBox image, and gotest assertions. Rootless/remote daemon modes are skipped for most host-link tests.

Risks: parent-link ownership semantics are delicate; cleanup failure can leak interfaces or delete an interface expected by another test. IPAM counters encode allocator details including gateway, broadcast, aux, anycast, and container reservations. Nil-parent macvlan connectivity expectations differ from ipvlan and can be easy to regress.

Test signals: network availability, link existence/nonexistence, ping success or expected failure, route output, DNS success/SERVFAIL, inspect IPAM status, sysctl values, and custom-ifname output collectively validate macvlan driver behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/macvlan_test.go -->
