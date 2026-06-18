# sources/distributed-fs/ceph-client/include/net/genetlink.h

Purpose: declares the in-kernel Generic Netlink family and message construction API. It lets kernel subsystems define named families, operations, multicast groups, per-socket private storage, validation policy, namespace behavior, and request/reply/notification helpers.

Important APIs/types: `struct genl_family` is the central registration object with name, version, max attributes, policy, ops arrays, split ops, multicast groups, hooks, module owner, and socket-private callbacks. `struct genl_info` carries request metadata, parsed attributes, namespace, context, and extack. Operation forms include `genl_small_ops`, `genl_ops`, and `genl_split_ops`. Message helpers include `genlmsg_put()`, `genlmsg_iput()`, `genlmsg_put_reply()`, `genlmsg_end()`, `genlmsg_cancel()`, `genlmsg_parse()`, `genlmsg_new()`, `genlmsg_reply()`, multicast/unicast helpers, listener/error helpers, and dump accessors.

Control flow and state: families register globally through `genl_register_family()` and unregister later. Requests are parsed and dispatched under either a global genl lock or parallel ops. Replies allocate an skb, put a genl header, fill attributes, end, and unicast/multicast. Dump callbacks access `genl_dumpit_info`.

Dependencies and integration: depends on netlink, network namespaces, UAPI genetlink, xarrays for per-socket private storage, and extack. It is used by modern kernel control planes including IOAM, TLS handshake, wireless, tunnels, and filesystems needing netlink control.

Risks: validation policy changes are userspace ABI. Multicast group indexes are offsets, not absolute ids. `parallel_ops` shifts locking to the family. Tests should cover strict/deprecated parsing, missing required attrs, multicast group bounds, namespace targeting, per-socket private init/destroy, dump consistency, and unregister while sockets/listeners exist.
