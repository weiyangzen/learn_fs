# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_ping.sh

## Purpose

This selftest verifies basic HSRv0 and HSRv1 connectivity in a three-node redundant ring, including optional VLAN-over-HSR connectivity. It checks both IPv4 and IPv6 unless `-4` disables IPv6.

## Important APIs, Types, and Functions

It sources `hsr_common.sh` and defines `usage`, `do_ping_tests`, `setup_hsr_interfaces`, `setup_vlan_interfaces`, `run_ping_tests`, and `run_vlan_tests`. It uses `ip link add type hsr`, veth pairs, explicit slave MAC addresses, VLAN subinterfaces, `ethtool -k` for `vlan-challenged`, and the common ping helpers.

## Control Flow

The script parses options, checks prerequisites, traps namespace cleanup, then creates three namespaces. It sets up HSRv0, runs base and VLAN tests, recreates namespaces, sets up HSRv1, and repeats the same tests. `do_ping_tests` first checks pairwise short pings, waits for debugfs HSR node table merge, then runs longer pings to detect duplicates or loss.

## State and Persistence Behavior

Runtime state includes namespaces `ns1`/`ns2`/`ns3`, three veth links forming a ring, `hsr1`/`hsr2`/`hsr3`, IPv4/IPv6 addresses, optional VLAN devices `hsr*.2`, and debugfs node table observations. Cleanup removes namespaces.

## Dependencies and Integration Points

It depends on HSR kernel support, veth, IPv6, VLAN support, debugfs HSR node tables, `ethtool`, and the selftest namespace library. It integrates with kernel HSR duplicate discard and supervision frame processing.

## Risks and Edge Cases

The wait for merged node table entries uses `/sys/kernel/debug/hsr/hsr*/node_table`; missing debugfs or changed output can cause timing issues. VLAN tests run only when any queried HSR device reports `vlan-challenged` as `off`. The IPv6 ns3-to-ns2 initial ping appears to target `dead:beef:$netid::2`, duplicating one pair, which may reduce matrix coverage.

## Test Signals

Success is all short and long IPv4/IPv6 pings passing for HSRv0 and HSRv1, no duplicate packets in 10-packet long pings, and optional VLAN ping tests passing when supported.
