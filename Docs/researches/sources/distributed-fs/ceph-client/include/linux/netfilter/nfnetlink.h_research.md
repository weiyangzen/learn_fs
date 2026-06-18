# sources/distributed-fs/ceph-client/include/linux/netfilter/nfnetlink.h

Purpose: Declares the kernel-side nfnetlink subsystem registration and message dispatch interface for netfilter families.

Important APIs, types, and functions: Key types are `struct nfnl_info`, `enum nfnl_callback_type`, `struct nfnl_callback`, `enum nfnl_abort_action`, and `struct nfnetlink_subsystem`. APIs include subsystem register/unregister, send/unicast/broadcast/set_err, `nfnl_msg_type()`, `nfnl_fill_hdr()`, `nfnl_msg_put()`, and per-subsystem locking. Detected source surface: 108 lines; includes `linux/capability.h`, `linux/netlink.h`, `net/netlink.h`, `uapi/linux/netfilter/nfnetlink.h`; macros `MODULE_ALIAS_NFNL_SUBSYS`, `_NFNETLINK_H`; structs `module`, `net`, `netlink_ext_ack`, `nfgenmsg`, `nfnetlink_subsystem`, `nfnl_callback`, `nfnl_info`, `nlmsghdr`, `sock`; enums `nfnl_abort_action`, `nfnl_callback_type`; typedefs none; function-like declarations/helpers `lockdep_nfnl_is_held`, `nfnetlink_broadcast`, `nfnetlink_has_listeners`, `nfnetlink_send`, `nfnetlink_set_err`, `nfnetlink_subsys_register`, `nfnetlink_subsys_unregister`, `nfnetlink_unicast`, `nfnl_fill_hdr`, `nfnl_lock`, `nfnl_msg_type`, `nfnl_unlock`.

Control flow: Subsystems register callback arrays keyed by message type. nfnetlink receives netlink messages, checks policy and privileges, dispatches callbacks, supports batch commit/abort, and emits replies or multicast notifications.

State and persistence behavior: Registered subsystem tables, callback arrays, and locks are global kernel state; skb messages are transient. Batch callbacks use abort actions to unwind partial transactions.

Dependencies and integration points: Depends on netlink, capabilities, net namespaces, and UAPI nfnetlink IDs. Used by conntrack, queue, log, accounting, osf, and nftables-style netfilter subsystems.

Risks and test signals: Risks are policy gaps, missing capability checks, lock ordering bugs, and malformed nested attributes. Test strict netlink validation, listener multicast, batch abort, and namespace isolation.
