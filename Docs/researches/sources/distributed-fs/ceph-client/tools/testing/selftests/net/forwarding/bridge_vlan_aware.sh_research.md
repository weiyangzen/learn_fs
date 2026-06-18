# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_aware.sh

## Purpose
`bridge_vlan_aware.sh` exercises baseline bridge behavior with `vlan_filtering 1`: IPv4/IPv6 forwarding, FDB learning, unknown unicast flooding, VLAN deletion effects, externally learned FDB behavior, handling of non-802.1Q TPIDs, 802.1p VID 0 traffic, and dropping untagged/priority-tagged traffic when no PVID exists.

## Important APIs, Functions, and Control Flow
Setup creates a VLAN-aware bridge with ageing time from `LOW_AGEING_TIME` and multicast snooping disabled, then enslaves two ports. `ping_ipv4`, `ping_ipv6`, `learning`, and `flooding` delegate to common `lib.sh` helpers. `vlan_deletion` adds and deletes VID 10 on `$swp1` and confirms default PVID forwarding is unaffected. `extern_learn` adds an `extern_learn` FDB entry, waits longer than bridge ageing time to prove it does not age out, sends a frame from the other host with that MAC, and verifies the external entry roams.

`other_tpid` installs a tc ingress filter on `$h2`, sends an 802.1ad outer tag followed by 802.1Q inner tag through `$h1`, and verifies the bridge treats it as untagged under a bridge configured for 802.1Q protocol. It then removes the PVID and confirms the same traffic no longer forwards. `8021p` and `8021p_do` verify VID 0 priority-tagged traffic is accepted with default PVID 1 and after changing the bridge default PVID to 10. `drop_untagged` removes PVID behavior through several paths and checks both untagged ping and 802.1p reception fail, including after port down/up and re-enslave.

## State, Dependencies, Integration Points, and Risks
State includes bridge VLAN membership, default PVID, FDB attributes, ageing timer, tc filters, promiscuous mode, and NIC VLAN filtering offloads disabled through `ethtool -K`. Dependencies include `CHECK_TC=yes`, `jq`, `tc`, mausezahn, ethtool, and bridge/FDB JSON support. Timing risk exists in `extern_learn`, which sleeps for ageing time plus ten seconds. Offload behavior can affect `other_tpid`, which compensates by matching self addresses and disabling rx VLAN filters.

## Test Signals
Signals come from ping helpers, learning/flood helpers, grep/JQ FDB checks, tc packet counters, and inverted checks for dropped untagged/802.1p traffic when no PVID is present.
