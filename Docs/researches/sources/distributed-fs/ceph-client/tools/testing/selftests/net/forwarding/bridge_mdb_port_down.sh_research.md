# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_port_down.sh

## Purpose
`bridge_mdb_port_down.sh` verifies permanent MDB entries can be added to a bridge port while that port is administratively down, remain present across link up/down transitions, forward traffic after the port comes up, and stop forwarding after deletion.

## Important APIs, Functions, and Control Flow
`add_del_to_port_down` is the only test. It disables `$swp2`, adds `bridge mdb add dev br0 port "$swp2" grp 239.10.10.10 permanent`, brings the port up, and uses `mcast_packet_test` from `lib.sh` to ensure multicast traffic from `$h1` reaches `$h2`. It then brings `$swp2` down again, confirms `bridge mdb show` still reports a permanent entry, deletes the entry while down, brings the port up, and expects multicast forwarding to fail.

Setup creates two hosts, a bridge with `mcast_snooping 1` and `mcast_querier 1`, enslaves two switch ports, disables multicast flooding on `$swp2`, and sleeps for bridge multicast grace-time behavior before testing.

## State, Dependencies, Integration Points, and Risks
The tested state is a permanent MDB entry on a down bridge slave and the bridge’s forwarding behavior once that slave becomes live. Dependencies include `ip`, `bridge`, `lib.sh`, `mcast_packet_test`, and mausezahn/packet capture support behind that helper. The hard-coded `sleep 10` mitigates bridge startup flooding grace period; reducing it could make the negative forwarding checks flaky.

## Test Signals
Success requires add/delete return codes to pass, `bridge mdb show` to retain the permanent group while the port is down, and `mcast_packet_test` to invert from forwarded after add to not forwarded after delete.
