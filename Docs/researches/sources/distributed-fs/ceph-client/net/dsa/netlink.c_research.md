# sources/distributed-fs/ceph-client/net/dsa/netlink.c

## Purpose
This file defines the rtnetlink link operations for DSA user interfaces. It exposes and changes the conduit netdev associated with a DSA user port through `IFLA_DSA_CONDUIT`.

## Important APIs, Types, And Functions
`dsa_policy` validates `IFLA_DSA_CONDUIT` as a `u32` ifindex. `dsa_changelink()` handles requested conduit changes by resolving the ifindex and calling `dsa_user_change_conduit()`. `dsa_get_size()` and `dsa_fill_info()` report the current conduit ifindex. `struct rtnl_link_ops dsa_link_ops` registers kind `"dsa"` with these callbacks and `netns_refund = true`.

## Control Flow
`dsa.c` registers `dsa_link_ops` at module init. Netlink change requests pass through validation, lookup the target conduit in the same net namespace, and delegate the complex migration to user/port code. Dump/getlink paths serialize the current conduit.

## State And Persistence
This file stores no per-interface state. It reads and mutates DSA user state through `dsa_user_to_conduit()` and `dsa_user_change_conduit()`.

## Dependencies And Integration Points
It integrates with rtnetlink, UAPI `IFLA_DSA_*` attributes, DSA user netdevs, and conduit migration code in `user.c`/`port.c`.

## Risks And Edge Cases
An invalid ifindex returns `-EINVAL`; deeper validation of whether the netdev can be a conduit is delegated. Changing conduits live is high-risk because host FDB/MDB/VLAN and bridge offload state must migrate.

## Test Signals
Netlink tests should read `IFLA_DSA_CONDUIT`, attempt valid and invalid conduit changes, verify extack failures, and check that traffic and bridge/VLAN state survive a successful migration.
