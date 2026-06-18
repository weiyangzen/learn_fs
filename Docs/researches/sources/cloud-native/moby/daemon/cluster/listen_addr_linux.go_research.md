# Research: sources/cloud-native/moby/daemon/cluster/listen_addr_linux.go

## sources/cloud-native/moby/daemon/cluster/listen_addr_linux.go

Purpose: Linux-specific implementation of `(*Cluster).resolveSystemAddr`. It uses netlink via daemon `nlwrap` to prefer real device interfaces and falls back to subnet-check discovery when running in environments where interfaces are not type `device`.

Control flow lists links, skips non-device or down interfaces, lists addresses, skips non-global-unicast addresses, favors IPv4 over IPv6 per interface, rejects multiple usable addresses on one or multiple interfaces, and returns `errNoIP` if active devices exist but none have usable addresses. If no suitable device is found, it calls `resolveSystemAddrViaSubnetCheck`, which helps containerized dockerd cases where NICs appear as veths.

State is host network interface state. Dependencies are `nlwrap`, `vishvananda/netlink`, and shared address error helpers. Risks include netlink failures, interface type assumptions, ambiguity on multi-homed hosts, and different behavior from non-Linux fallback. No direct tests are in this subset.
