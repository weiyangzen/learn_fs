## sources/cloud-native/moby/daemon/libnetwork/osl/interface_linux.go

Purpose: Linux implementation of libnetwork sandbox interface management. It creates/moves/renames/configures links in network namespaces, assigns addresses/routes/sysctls, brings links up, waits for readiness, advertises addresses with unsolicited ARP/NA, and removes interfaces.

Important APIs/types/functions: `Interface` stores source/destination names, master, MAC, IPv4/IPv6/link-local addresses, routes, sysctls, advertisement settings, and namespace pointer. Key methods/functions include `newInterface`, accessors, `Statistics`, `Namespace.AddInterface`, `createInterface`, `generateIfaceName`, `waitForIfUpped`, `waitForBridgePort`, `waitForMcastRoute`, `advertiseAddrs`, `prepAdvertiseAddrs`, `RemoveInterface`, `configureInterface`, `setInterfaceMAC/IP/IPv6/Master/LinkLocalIPs/Routes/Name`, `setSysctls`, and `checkRouteConflict`.

Control flow: `AddInterface` opens the target netns if needed, builds an `Interface`, moves or creates the link, configures it, retries `LinkSetUp`, adds non-default connected routes, waits for link-up events, waits for bridge forwarding/multicast route where relevant, then sends ARP/NA advertisements. On configuration failure it tries to rename and move the link back to host namespace.

State and persistence behavior: mutates kernel network namespace state and tracks configured interfaces in `Namespace.iFaces` under lock. `Interface.stopCh` cancels background advertisement sends on removal. Sysctls write `/proc/sys/net/...` inside the namespace. IPv6 address state may be cleared from `Interface` if sysctl settings remove it.

Dependencies and integration points: heavy integration with `nlwrap`, global `ns` handles, vishvananda/netlink/netns, OpenTelemetry spans, `l2disco` unsolicited ARP/NA helpers, libnetwork `types`, and Linux `/sys/class/net` bridge files.

Risks: high-risk kernel-facing code. Races around interface readiness, namespace movement, bridge forwarding, multicast routes, and sysctl effects can affect container connectivity. Error recovery after partial configuration is best effort. `checkRouteConflict` is conservative and may reject overlapping routes. Background ARP/NA sends must stop when interfaces are removed.

Test signals: `interface_linux_test.go` covers generated name gaps and parallel `AddInterface` name allocation. Broader integration tests are needed for real link movement, address assignment, route conflicts, sysctls, neighbor advertisements, and removal behavior.
