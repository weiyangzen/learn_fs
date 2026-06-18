# sources/distributed-fs/ceph-client/net/devlink/netlink.c

## Purpose

`netlink.c` provides the generic netlink family glue for devlink. It implements multicast groups, per-socket notification filters, devlink handle lookup from attributes, pre/post operation locking, common dump iteration, nested handle emission, and the `devlink_nl_family` registration descriptor.

## Important APIs, Types, and Functions

Important functions are `devlink_nl_notify_filter_set_doit()`, `devlink_nl_notify_filter()`, `devlink_nl_put_nested_handle()`, `devlink_nl_msg_reply_and_new()`, `devlink_get_from_attrs_lock()`, pre-doit variants for devlink, port, device-lock, and optional-port operations, post-doit variants, and `devlink_nl_dumpit()`. The per-socket state is `struct devlink_nl_sock_priv`, holding an RCU-protected `struct devlink_obj_desc` filter.

## Control Flow

Users may install a notification filter by bus name, device name, devlink index, and/or port index. Multicast sends call `devlink_nl_notify_filter()`, which reads the socket filter under RCU and suppresses nonmatching messages. Operation pre-doit resolves a devlink by index or bus/device pair, takes a reference, locks the instance and optionally the parent device, validates registration, and optionally resolves a port into `info->user_ptr[1]`. Post-doit unlocks and drops the reference. Dumps either target a single requested instance or iterate all registered instances in the caller's net namespace, resetting subobject dump state between devlinks.

## State and Persistence Behavior

Notification filter state persists per generic-netlink socket until replaced or socket destruction, then is freed by RCU. Dump progress persists in `struct devlink_nl_dump_state` inside the netlink callback context. Devlink references acquired during pre-doit and dump iteration are released after each operation.

## Dependencies and Integration Points

The file depends on generated `devlink_nl_ops`, `devlink_nl_family`, xarray lookup from `core.c`, port lookup helpers, generic netlink socket-private support, namespace ID allocation for nested handles, and multicast filtering hooks.

## Risks

Lookup supports either index or bus/device identity; accepting mixed identifiers would be ambiguous and is rejected. Pre/post flag mismatches can leave device locks held or drop references incorrectly. Filter string storage uses one allocation with embedded string data, so offset calculations must remain correct. Dump handlers must correctly use and reset shared dump-state fields.

## Test Signals

Test lookup by index, synthetic index bus name, and real bus/device; operations against unregistering devlinks; required and optional port pre-doit paths; device-lock paths under lockdep; notification filters for each field; nested handle netns ID emission; and multi-instance dumps with skb-size induced continuation.
