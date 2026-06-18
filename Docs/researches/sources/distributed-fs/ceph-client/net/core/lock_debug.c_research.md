# sources/distributed-fs/ceph-client/net/core/lock_debug.c

Purpose: Registers debug netdevice notifiers that assert expected RTNL, per-net RTNL, and device ops locking for netdevice events. It is a runtime diagnostic guard for networking lock discipline.

Important APIs, types, and functions: `netdev_debug_event()` is the notifier callback and is exported in the `NETDEV_INTERNAL` namespace. Initialization uses pernet operations `rtnl_net_debug_net_ops`, a global notifier block `rtnl_net_debug_block`, and `rtnl_net_debug_init()` at `subsys_initcall`.

Control flow: On each notifier event, `netdev_debug_event()` converts notifier info to `net_device`, switches over the event enum, and asserts the required lock context. `NETDEV_XDP_FEAT_CHANGE` requires `netdev_assert_locked()` then falls through to events requiring `netdev_ops_assert_locked()`, which then fall through to many events requiring `ASSERT_RTNL()`. `NETDEV_CHANGENAME` asserts per-net RTNL with `ASSERT_RTNL_NET(net)`. Per-net init allocates/registers a notifier per namespace; global init registers pernet ops and then the global notifier, unwinding on failure.

State and persistence: State is notifier registration state plus one per-net notifier block stored in generic net namespace storage. No durable persistence exists.

Dependencies and integration points: Depends on netdevice notifier chains, RTNL/per-net RTNL locking APIs, net namespace generic storage, and netdev ops locks. It observes broad netdevice lifecycle and configuration events.

Risks: Missing switch cases intentionally trigger compiler warnings because there is no default. Incorrect assertions can generate false positives or hide real lock violations. Registration failure handling must avoid dangling pernet subsystems.

Test signals: Build with warning-as-error after adding new netdev events to ensure switch coverage. Trigger representative notifier events under correct and incorrect locks in debug kernels, including XDP feature change, register/up/down/change, changename with per-net RTNL, and namespace teardown.
