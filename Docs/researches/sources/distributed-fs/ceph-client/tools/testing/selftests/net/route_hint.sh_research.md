<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/route_hint.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/route_hint.sh

## Purpose

`route_hint.sh` verifies that directed broadcast routes use the destination hint mechanism efficiently. It sends a burst of crafted TCP packets to a subnet broadcast address and checks that the server's broadcast counter does not grow excessively.

## Important APIs, Types, and Functions

The script sources `lib.sh`, defines `setup`, `cleanup`, and `directed_bcast_hint_test`, and uses `setup_ns`, `ip link`, `ip addr`, `ethtool`, sysfs GRO/NAPI knobs, `mausezahn`, `lnstat -j`, `jq`, and `bc`. Addresses are `192.168.0.1`, `192.168.0.2`, and directed broadcast `192.168.0.255`.

## Control Flow

It verifies the presence of `mausezahn`, `jq`, and `bc`, installs cleanup trap, creates client/server namespaces with a veth pair, configures addresses, disables TSO on the client, enables/defer-tunes GRO on the server, then records `lnstat` `in_brd` before and after a single mausezahn command that emits a range of TCP source ports to the broadcast destination. If the counter delta is below 100, the test passes.

## State and Persistence Behavior

State is two temporary namespaces, a veth pair, interface offload settings, sysfs GRO/NAPI values in the server namespace, and namespace-local counters. Cleanup deletes the server-side veth and both namespaces.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include root/CAP_NET_ADMIN, `mausezahn`, `jq`, `bc`, `lnstat`, `ethtool`, veth, GRO sysfs knobs, and namespace support. Integration points are route hints for directed broadcast, GRO/NAPI behavior, and `/proc/net/stat` style counters surfaced through `lnstat`. Risks include missing tooling, counter name/output changes, timing around `sleep 1`, and offload behavior differences. Signals are `[ OK ]` when `new_in_brd - orig_in_brd < 100`, otherwise `[FAIL]` with the observed delta.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/route_hint.sh -->
