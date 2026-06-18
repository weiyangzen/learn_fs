# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_redbox.sh

## Purpose

This selftest validates HSR RedBox behavior, where an HSR node with an interlink connects a redundant HSR network to singly attached nodes through a bridge. It focuses on IPv4 connectivity between HSR nodes and SAN-side hosts.

## Important APIs, Types, and Functions

It sources `hsr_common.sh` with `ipv6=false` and defines `do_complete_ping_test` and `setup_hsr_interfaces`. It uses `ip link help hsr` to check for `INTERLINK`, veth pairs, a bridge in `ns3`, `ip link add type hsr ... interlink`, and common ping helpers.

## Control Flow

The script checks prerequisites, creates five namespaces, sets up HSRv1 with `ns2` as the RedBox containing `hsr2` and interlink `ns2eth3`, builds a bridge in `ns3` to SAN hosts `ns4` and `ns5`, then runs short connectivity pings, waits for HSR management frames, and runs long pings between SAN and HSR endpoints.

## State and Persistence Behavior

Temporary state includes five namespaces, five veth pairs, bridge `ns3br1`, HSR devices `hsr1` and `hsr2`, an HSR interlink, fixed MAC addresses, and IPv4 addresses. Cleanup removes all namespaces.

## Dependencies and Integration Points

It depends on HSR interlink support in iproute2 and the kernel, bridge support, veth, and HSR duplicate filtering. It integrates with the RedBox path between HSR and standard Ethernet segments.

## Risks and Edge Cases

If `ip link help hsr` lacks `INTERLINK`, the script exits 0 rather than using the kselftest skip code. The five-second wait is a fixed delay rather than an explicit node table condition. Shared MAC assignment on `ns3` bridge ports models bridge behavior but can obscure debugging if the topology changes.

## Test Signals

Success is short pings among HSR and SAN endpoints, followed by long pings with no loss or duplicates between SAN hosts and `hsr1` through the RedBox.
