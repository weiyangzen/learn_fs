# sources/distributed-fs/ceph-client/include/net/fib_notifier.h

Read `sources/distributed-fs/ceph-client/include/net/fib_notifier.h` completely for this pass (51 lines, 1390 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/fib_notifier.h_research.md`.

Purpose: declares the FIB notifier API used to publish route, rule, nexthop, and multicast VIF changes to listeners per network namespace and address family.

Important APIs/types/functions: `struct fib_notifier_info` carries address family and extack pointer. `enum fib_event_type` includes entry replace/append/add/delete, rule add/delete, nexthop add/delete, and VIF add/delete. `struct fib_notifier_ops` registers family-specific sequence read and full dump callbacks plus module owner and RCU node. APIs include `call_fib_notifier()`, `call_fib_notifiers()`, `register_fib_notifier()`, `unregister_fib_notifier()`, `fib_notifier_ops_register()`, and `fib_notifier_ops_unregister()`.

Control flow: route/rule/nexthop code emits events through `call_fib_notifiers()`. Listeners register notifier blocks and may request an initial dump through family-specific `fib_dump()` when registering. Sequence reads let consumers detect missed updates and resync.

State and persistence: notifier blocks and `fib_notifier_ops` registrations are runtime per-netns/family state protected by notifier and RCU mechanisms. No route state is stored here; it references FIB state owned elsewhere.

Dependencies and integration points: depends on notifier chains, net namespaces, modules, RCU, netlink extack, IPv4/IPv6 FIB/rules/nexthop/multicast code, and offload consumers such as switchdev/driver route offload.

Risks: listeners must handle missed events and dump/resync correctly. Module owner lifetime matters for `fib_notifier_ops`. Event payloads extend `fib_notifier_info` by embedding, so consumers must cast based on event/family. Registration error extacks must be propagated.

Test signals: route/rule/nexthop add/delete event delivery, initial dump during registration, sequence mismatch resync, unregister during concurrent events, module unload safety, extack on dump/register errors, and per-netns isolation.
