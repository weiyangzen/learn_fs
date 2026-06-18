
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/no_forwarding.sh

Purpose: Verifies traffic is not forwarded between disconnected switch ports under standalone, separate-bridge, and different-PVID bridge configurations.

Important APIs/functions: send helpers for non-IP, IPv4 unicast/multicast, IPv6 unicast/multicast; `check_rcv`, `run_test`, scenario functions `standalone`, `two_bridges`, `one_bridge_two_pvids`, and host setup helpers.

Control flow: builds H1/H2 VRF endpoints and switch ports, starts tcpdump on H2, sends untagged and many VLAN-tagged packet types from H1, stops tcpdump, and asserts none of the expected patterns were received. Scenarios change switch-side isolation but all should prevent forwarding.

State/persistence: creates VRFs, optional bridges `br0`/`br1`, VLAN devices over H1 for test packets, tcpdump temp files, and bridge VLAN entries.

Dependencies/integration: depends on tcpdump pattern output, mausezahn, ping/ping6, `ipv6_lladdr_get`, and `lib.sh`.

Risks: the `vids` array includes duplicate 1000, which repeats coverage but is harmless. Tcpdump output matching is fragile across versions. All tests expect non-forwarding, so any received pattern is a failure.

Test signals: every untagged and tagged unicast/multicast/broadcast/non-IP pattern lookup fails in tcpdump output, logged per packet type.
