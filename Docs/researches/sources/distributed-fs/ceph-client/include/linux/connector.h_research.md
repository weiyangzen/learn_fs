## sources/distributed-fs/ceph-client/include/linux/connector.h

Purpose: This header declares the connector core interface, a netlink-based mechanism for in-kernel producers/consumers to exchange structured messages with userspace or registered callbacks.

Important APIs, types, and functions: `struct cn_queue_dev` represents a callback queue device with refcount, queue list/lock, name, and netlink socket. `struct cn_callback_id` combines a symbolic name with `struct cb_id`. `struct cn_callback_entry` stores callback list membership, refcount, device, ID, callback function, sequence, and group. `struct cn_dev` captures connector device ID, sequence, groups, socket, and queue device. Public APIs include `cn_add_callback`, `cn_del_callback`, `cn_netlink_send_mult`, `cn_netlink_send`, queue add/delete/release, queue allocation/free, and `cn_cb_equal`.

Control flow: Kernel users register callbacks by unique connector IDs. Incoming netlink messages are matched to callback entries, invoking the callback with `struct cn_msg` and netlink sender credentials. Outgoing messages use `cn_netlink_send()` or `_mult()` to deliver by port ID or multicast group; if both destination fields are zero, the core finds the group associated with the message ID.

State and persistence: Connector runtime state includes registered callback entries, queue lists, sequence counters, multicast group assignments, netlink sockets, and refcounts. State lasts until callbacks and queues are explicitly removed.

Dependencies and integration points: It depends on `linux/refcount.h`, lists, workqueues, netlink sockets, `netlink_filter_fn`, and UAPI connector message definitions. Integration points are kernel subsystems that need low-volume event/control messages over netlink.

Risks and test signals: Risks include callback ID collisions, silent send failure under memory pressure, use-after-free if callback refs are mishandled, group routing mistakes, and softirq-context allocation constraints. Test signals include registering duplicate IDs, netlink listener absence returning `-ESRCH`, filtered multicast delivery, module unload while callbacks are active, and memory pressure send tests.
