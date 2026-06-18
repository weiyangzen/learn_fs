# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/prp_ping.sh

## Purpose

This selftest verifies basic PRP connectivity between two nodes connected by two parallel LANs, including optional VLAN-over-PRP connectivity. It checks IPv4 and IPv6 unless `-4` is supplied.

## Important APIs, Types, and Functions

It sources `hsr_common.sh` and defines `usage`, `setup_prp_interfaces`, `setup_vlan_interfaces`, `do_ping_tests`, `run_ping_tests`, and `run_vlan_ping_tests`. It creates PRP devices through `ip link add type hsr ... proto 1`.

## Control Flow

The script parses options, checks prerequisites, creates two namespaces, adds parallel veth pairs `vethA` and `vethB`, creates `prp1` and `prp2`, assigns IPv4/IPv6 addresses, brings links up, runs base ping tests, then conditionally creates VLAN subinterfaces and repeats the ping tests for network id 2.

## State and Persistence Behavior

Temporary state includes namespaces `node1` and `node2`, two veth pairs, PRP devices, IPv4/IPv6 addresses, optional VLAN devices `prp1.2` and `prp2.2`, and ping-observed connectivity state. Cleanup removes namespaces.

## Dependencies and Integration Points

It depends on HSR driver PRP mode, veth, IPv6, VLAN support, `ethtool`, and the shared HSR common helpers. It validates the kernel PRP duplicate handling and LAN A/B redundancy in a minimal topology.

## Risks and Edge Cases

VLAN tests run only if either PRP device reports non-`vlan-challenged`; that condition may be broad if one side supports VLAN and the other does not. MAC addresses are explicitly set only on LAN A and copied by PRP semantics. Long ping parsing inherits the common helper's output-format assumptions.

## Test Signals

Success is short and long IPv4/IPv6 pings in both directions with no duplicate/loss indication, plus optional VLAN ping success when supported.
