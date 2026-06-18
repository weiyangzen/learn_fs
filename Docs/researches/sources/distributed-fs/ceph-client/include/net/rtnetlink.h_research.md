# sources/distributed-fs/ceph-client/include/net/rtnetlink.h

## Purpose
This header defines the in-kernel rtnetlink registration and link/address-family operation contracts. It lets protocol families and virtual/link drivers register message handlers, link kinds, validation callbacks, namespace handling, and netlink dump/fill routines used by `rtnetlink.c`.

## Important APIs, Types, And Functions
Key types are `rtnl_doit_func`, `rtnl_dumpit_func`, `struct rtnl_msg_handler`, `struct rtnl_newlink_params`, `struct rtnl_link_ops`, and `struct rtnl_af_ops`. The handler flags control lock behavior and dump semantics: `RTNL_FLAG_DOIT_UNLOCKED`, `RTNL_FLAG_BULK_DEL_SUPPORTED`, `RTNL_FLAG_DUMP_UNLOCKED`, and `RTNL_FLAG_DUMP_SPLIT_NLM_DONE`. `rtnl_msgtype_kind()` masks message types into new/delete/get/set classes. `rtnl_msg_family()` safely extracts `rtgen_family` only when the nlmsg is long enough. Registration APIs include `rtnl_register_many()`, `rtnl_unregister_many()`, `rtnl_link_register()`, `rtnl_link_unregister()`, `rtnl_af_register()`, and `rtnl_af_unregister()`.

## Control Flow
Netlink receive paths dispatch through registered `rtnl_msg_handler` entries. Link creation flows parse attributes, resolve link and peer namespaces with `rtnl_newlink_link_net()` and `rtnl_newlink_peer_net()`, allocate/configure devices through `rtnl_link_ops::alloc`, `setup`, `validate`, and `newlink`, then use dump callbacks for rtnetlink responses.

## State And Persistence
The header declares registration objects with list and SRCU fields; actual persistence is in global rtnetlink registries. `rtnl_link_ops` and `rtnl_af_ops` lifetime is module-sensitive through `owner` or registration ordering.

## Dependencies And Integration Points
It depends on Linux rtnetlink UAPI, SRCU, netlink attributes, network namespaces, and `net_device`. It integrates virtual devices, address-family specific link data, module aliases via `MODULE_ALIAS_RTNL_LINK`, and namespace-capable lookups through `rtnl_get_net_ns_capable()`.

## Risks And Test Signals
Risks center on attribute validation gaps, namespace mis-selection, unlocked handler races, and module lifetime while SRCU readers walk operations. Test signals include rtnetlink create/change/delete coverage, extack validation failures, namespace peer/link cases, and dump size/fill consistency checks.
