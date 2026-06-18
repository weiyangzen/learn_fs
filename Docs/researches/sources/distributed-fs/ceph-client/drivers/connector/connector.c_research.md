# sources/distributed-fs/ceph-client/drivers/connector/connector.c

## Purpose
This file is the generic NETLINK_CONNECTOR transport and callback dispatch core. It lets kernel subsystems register callbacks by connector ID and exchange `struct cn_msg` messages with userspace via netlink unicast or multicast groups.

## Important APIs, Types, And Functions
The global connector device is `static struct cn_dev cdev`. Exported APIs are `cn_netlink_send_mult()`, `cn_netlink_send()`, `cn_add_callback()`, and `cn_del_callback()`. Internal functions include `cn_call_callback()` for received-message dispatch, `cn_bind()` for multicast permission checks, `cn_release()` for socket cleanup, `cn_rx_skb()` for netlink receive validation, `cn_proc_show()` for `/proc/net/connector`, `cn_init()`, and `cn_fini()`.

## Control Flow
`cn_init()` creates the NETLINK_CONNECTOR kernel socket in `init_net`, allocates a callback queue, marks the subsystem initialized, and creates `/proc/net/connector`. Incoming skbs are checked for netlink and connector message size, then `cn_call_callback()` finds a registered callback by ID, takes an entry refcount, invokes the callback with netlink parameters, frees the skb, and releases the ref. Outgoing `cn_netlink_send_mult()` resolves the multicast group either from explicit arguments or registered callback ID, checks listeners, allocates an skb, copies the message, and sends by broadcast with optional filter or unicast.

`cn_bind()` allows non-root binding only to the process-events multicast group; other groups require `CAP_NET_ADMIN`. `cn_release()` frees `sk_user_data` for sockets bound to the process group. `cn_fini()` removes proc state, frees callback queue, and releases the netlink socket.

## State And Persistence
`cdev` holds the netlink socket and callback queue. `cn_already_initialized` gates callback registration. Callback registration state is delegated to `cn_queue.c`. Per-socket process subscription state is freed here on release.

## Dependencies And Integration Points
The file depends on Linux netlink APIs, connector queue helpers, procfs/seq_file, capabilities, and connector ABI types. Subsystems such as `cn_proc.c` register callbacks with `cn_add_callback()` and send events with `cn_netlink_send_mult()`.

## Risks And Edge Cases
Message length validation is critical because `msg->len` comes from userspace. Broadcast filtering is optional and subsystem-provided. If no callback group is found and caller did not pass a group/portid, send returns `-ENODEV`. `cn_release()` assumes process connector ownership of `sk_user_data` for the CN_IDX_PROC group. Initialization order matters because `cn_add_callback()` returns `-EAGAIN` until the core is initialized.

## Test Signals
Tests should cover invalid netlink lengths, duplicate/missing callback dispatch, unicast and multicast send paths, listener absence returning `-ESRCH`, permission checks in `cn_bind()`, proc listing of registered callbacks, and callback registration before/after initialization.
