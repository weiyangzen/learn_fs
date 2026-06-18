# sources/distributed-fs/ceph-client/include/net/netns/nexthop.h

Purpose: Defines per-network-namespace nexthop object table state.

Important APIs/types/functions: `struct netns_nexthop` stores an RB tree of nexthops by id, a device hash for nexthops by device, RTNL-protected sequence number `seq`, `last_id_allocated`, and a blocking notifier chain.

Control flow: Nexthop create/lookup/replace/delete operations update the RB tree and device hash under routing locks. Route code observes sequence changes and notifier events when nexthop objects change.

State and persistence: Runtime per-net nexthop index, device hash, last allocated id, sequence counter, and notifier subscribers.

Dependencies/integration: Depends on fib/nexthop core, notifier chains, route lookup, and namespace lifecycle.

Risks/test signals: Test id allocation wrap/duplicates, RB tree and devhash consistency, object replacement under route references, notifier ordering, sequence increments under RTNL, and namespace cleanup.
