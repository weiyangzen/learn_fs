# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_unaware.sh

## Purpose
`bridge_vlan_unaware.sh` verifies baseline bridge forwarding with VLAN filtering disabled. It specifically ensures that manipulating bridge VLAN/PVID metadata on a port does not affect VLAN-unaware forwarding.

## Important APIs, Functions, and Control Flow
Setup creates `br0` without `vlan_filtering`, with low ageing time and multicast snooping disabled, then enslaves two ports and configures two hosts. `ping_ipv4`, `ping_ipv6`, `learning`, and `flooding` delegate to common helpers. `pvid_change` adds VID 3 as PVID/untagged on `$swp1`, confirms IPv4 and IPv6 still work, deletes VID 3, and confirms connectivity still works.

## State, Dependencies, Integration Points, and Risks
State is mostly bridge membership, FDB learning, and optional VLAN metadata that should be ignored by VLAN-unaware forwarding. Dependencies include `lib.sh`, ping helpers, learning/flooding helpers, and normal bridge VLAN commands even though VLAN filtering is off. Risk is low; failures generally indicate a regression where bridge VLAN state leaks into VLAN-unaware forwarding.

## Test Signals
Signals are ping success, learning helper success, flooding helper success, and repeated connectivity after PVID add/delete operations.
