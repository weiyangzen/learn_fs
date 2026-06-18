# Research: sources/cloud-native/moby/daemon/cluster/listen_addr.go

## sources/cloud-native/moby/daemon/cluster/listen_addr.go

Purpose: resolves and validates swarm listen, advertise, data-path, default address pool, and data-path port settings. It also implements generic system address discovery used by platform-specific wrappers.

Important APIs: `resolveListenAddr`, `(*Cluster).resolveAdvertiseAddr`, `validateDefaultAddrPool`, `getDataPathPort`, `resolveDataPathAddr`, `resolveInterfaceAddr`, `resolveInputIPAddr`, `(*Cluster).resolveSystemAddrViaSubnetCheck`, `listSystemIPs`, and `errMultipleIPs`. Control flow favors interface-name resolution before literal IP parsing, allows unspecified listen addresses but rejects unspecified advertise/data-path addresses, fills missing advertise ports from listen ports, validates overlay default subnet sizes, and restricts VXLAN data-path ports to 1024-49151 with default 4789.

State is the host network interface table and Docker-managed subnets from `NetworkSubnetsProvider`. Integration points are `swarm.go` init/join request handling and daemon config `SwarmDefaultAdvertiseAddr`. Risks include ambiguous multi-address hosts, platform-specific interface behavior, Docker-managed subnet exclusion causing unexpected no-address results, and user-facing config errors from address parsing. Tests are not in this subset, so regressions are mostly caught by swarm integration tests.
