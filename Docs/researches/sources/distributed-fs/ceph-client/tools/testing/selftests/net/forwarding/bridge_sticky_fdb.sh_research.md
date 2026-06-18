# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_sticky_fdb.sh

## Purpose
`bridge_sticky_fdb.sh` tests bridge FDB `sticky` behavior. It verifies that a sticky static FDB entry can survive deletion of the static master record in a way that still prevents learning/movement from an incoming frame on another port.

## Important APIs, Functions, and Control Flow
The topology is a simple two-port bridge with hosts directly connected. `sticky` adds `TEST_MAC` on `$swp1` with `bridge fdb add ... master static sticky`, deletes the corresponding static sticky entry for VLAN 1, sends an ARP frame from `$h2` using source MAC `TEST_MAC`, and then queries JSON FDB output for a record on `$swp1`. The expected behavior is that the sticky FDB record remains anchored on `$swp1` despite the frame arriving from `$h2`.

## State, Dependencies, Integration Points, and Risks
State is bridge FDB state, the sticky flag, and one mausezahn-generated ARP packet. Dependencies include `bridge -j fdb`, `jq`, `$MZ`, and `lib.sh`. The test assumes the default VLAN context reported as VLAN 1 for bridge FDB operations. If bridge FDB JSON schema or default VLAN handling changes, the jq predicate can fail despite equivalent behavior.

## Test Signals
The test passes when the FDB add succeeds and `bridge -j fdb show br br0 brport $swp1` contains `TEST_MAC` after a packet with that source was injected from the other host.
