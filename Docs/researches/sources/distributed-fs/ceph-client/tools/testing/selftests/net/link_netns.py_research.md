# sources/distributed-fs/ceph-client/tools/testing/selftests/net/link_netns.py

## Purpose
This Python selftest validates `link-netnsid` behavior for link creation, peer-link creation, and rtnetlink notification suppression across network namespaces.

## Important APIs and Functions
`test_event` subscribes to rtnetlink link notifications in one namespace and verifies no unexpected notification is queued after creating/deleting links that reference another namespace. `validate_link_netns` reads `ip -d -j link show` and compares `link_netnsid`. `test_link_net` covers single-device link types including ipvlan, macsec, macvlan, macvtap, vlan, GRE/VTI/IPIP/IP6 tunnel types, sit, and xfrm. `test_peer_net` covers peer devices `vxcan`, `netkit`, and `veth`. `main` runs the three cases through `ksft_run`.

## Control Flow and State
Each test builds temporary namespaces with `NetNS`, assigns namespace IDs with `ip netns set`, creates links with combinations of `netns`, `link-netns`, and peer `netns`, validates the resulting JSON field, then deletes created links. State is transient kernel namespace/link state scoped to context managers.

## Dependencies and Integration
It depends on `lib.py` helpers, YNL rtnetlink support, `iproute2`, and kernel support for the listed link types. It uses `RtnlFamily.ntf_subscribe` and `check_ntf` to inspect async netlink messages.

## Risks and Test Signals
Some link types may be unavailable as modules or kernel config. Tunnel types marked as fallback expect dev-net behavior rather than link-netns behavior. Pass signals are KTAP `ok` lines; failures come from missing/incorrect `link_netnsid` values or unexpected rtnetlink notifications.
