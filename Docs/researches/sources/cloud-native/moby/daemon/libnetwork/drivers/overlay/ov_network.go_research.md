# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_network.go

Purpose: Implements Linux overlay network lifecycle, lazy sandbox/subnet initialization, VXLAN/bridge creation, stale sandbox cleanup, and network locking.

Important APIs and types: `network`, `subnet`, and global `vniTbl` model overlay networks and VNI ownership. `CreateNetwork` validates IPv4 IPAM and VNI options, parses secure/MTU options, stores subnets, publishes the network under lock, cleans stale encryption rules for non-secure networks, and registers the peer table. `DeleteNetwork` cleans endpoint links, encryption firewall rules, and removes the network. `joinSandbox`, `leaveSandbox`, `destroySandbox`, `populateVNITbl`, name generators, `setupSubnetSandbox`, `setDefaultVLAN`, `initSubnetSandbox`, `cleanupStaleSandboxes`, `initSandbox`, `lockNetwork`, and `getSubnetforIP` manage the lazy network namespace.

Control flow: overlay resources are created lazily on first join. Global VNI table is populated once from existing namespace paths to reclaim stale VXLANs. Network object locking avoids driver/network lock inversion by double-checking active map entries. Sandbox teardown happens when join count reaches zero.

State and persistence: no datastore. Mutates OSL network namespaces, Linux bridges, VXLAN links, sysfs bridge VLAN settings, encryption firewall state, endpoint links, and in-memory tables.

Dependencies and integration points: integrates with libnetwork IPAM/options, `overlayutils.AppendVNIList`, OSL sandbox, netlink/netns, nftables/iptables encryption helpers, and NetworkDB peer table registration.

Risks: many kernel side effects can partially fail. `setDefaultVLAN` uses mount namespace operations on a locked OS thread. Stale sandbox cleanup uses name-pattern matching and must avoid deleting current resources. `CreateNetwork` type-asserts generic options.

Test signals: no direct lifecycle tests in this subset; ovmanager tests cover VNI allocation separately.
