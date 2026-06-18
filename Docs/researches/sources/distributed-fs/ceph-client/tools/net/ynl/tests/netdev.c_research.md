# sources/distributed-fs/ceph-client/tools/net/ynl/tests/netdev.c

Purpose: C selftest for generated netdev YNL bindings, including dump, single get, and multicast notification handling.

Important APIs/functions: `netdev_print_device()` validates `ifindex`, resolves names with `if_indextoname()`, and prints XDP/XSK feature bit strings using generated enum-to-string helpers. `veth_create()` and `veth_delete()` use generated `rt-link` bindings to create/delete veth devices and optionally consume echo notifications. Fixture opens `ynl_netdev_family`; notification test also opens `ynl_rt_link_family`.

Control flow: `dump` iterates `netdev_dev_get_dump()`. `get` selects an ifindex from a dump, builds `netdev_dev_get_req`, and queries it. `ntf_check` subscribes to `mgmt`, creates a veth through rtnetlink, calls `ynl_ntf_check()`, dequeues notifications, drains leftovers, deletes the veth, and asserts one netdev notification arrived.

State/dependencies: socket notification queues, generated heap requests/responses, and kernel netdev state are central. Requires netdev family support, rtnetlink generated bindings, and permission to create links.

Risks/test signals: validates generated notification wrappers, enum string maps, dump lists, and cross-family integration. Risk areas include missed cleanup if veth creation succeeds but notification handling fails, and environment-dependent notification timing.
