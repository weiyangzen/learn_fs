# sources/distributed-fs/ceph-client/net/ethtool/netlink.c

## Purpose
This file is the generic netlink core for ethtool. It registers the `ethtool` family, defines common header policies, parses device/PHY selectors, provides generic GET/SET/dump/notify machinery, owns netlink socket private teardown, and dispatches every `ETHTOOL_MSG_*` command to the appropriate request ops or action handler.

## Important APIs, Types, And Functions
Public helpers include `ethnl_sock_priv_set()`, `ethnl_bcast_seq_next()`, `ethnl_ops_begin()`, `ethnl_ops_complete()`, `ethnl_parse_header_dev_get()`, `ethnl_req_get_phydev()`, `ethnl_fill_reply_header()`, `ethnl_reply_init()`, `ethnl_dump_put()`, `ethnl_bcastmsg_put()`, `ethnl_unicast_put()`, `ethnl_multicast()`, `ethnl_notify()`, and exported `ethtool_notify()`. Internal core types are `struct ethnl_dump_ctx` and `struct ethnl_perphy_dump_ctx`. Dispatch tables include `ethnl_default_requests`, `ethnl_default_notify_ops`, `ethnl_notify_handlers`, and `ethtool_genl_ops`.

## Control Flow
Single GET uses `ethnl_default_doit()`: allocate request/reply blocks, parse header and type-specific request data, lock RTNL and netdev ops, call `prepare_data()`, size and allocate reply skb, fill header and payload, cleanup, and reply. Dump GET uses start/dump/done callbacks and iterates netdevices; per-PHY dump variants iterate `dev->link_topo->phys` and set `req_info->phy_index` for each PHY.

SET uses `ethnl_default_set_doit()`: parse a required device, run optional `set_validate()`, lock RTNL and netdev ops, clone `dev->cfg` into `cfg_pending`, enter ethtool ops, call type-specific `set()`, swap pending config on success, and call `ethnl_notify()` if the type reports a change. Notifications rebuild a compact GET reply and multicast it to the monitor group.

## State And Persistence
Global state includes the registered genl family, `ethnl_ok`, broadcast sequence, and per-socket private data used by module firmware flashing. Persistent device configuration is not stored here except transient `dev->cfg_pending` handling during SET. Dump cursors persist in `netlink_callback` context across dump iterations.

## Dependencies And Integration Points
The file depends on generic netlink, netdevice lookup/refcounting, RTNL, netdev ops locking, runtime PM, PHY link topology, module firmware flashing teardown, and all per-command `ethnl_request_ops` declared in `netlink.h`. It also listens for netdevice feature-change and pre-up events, emitting feature notifications and blocking port-up during module flash.

## Risks And Edge Cases
Header parsing permits ifindex/name matching and optional `phy_index`; bad combinations return extack-rich errors. Dumps ignore a device selector for normal per-device operations but preserve it for per-PHY dumps. SET swaps `dev->cfg` and `cfg_pending` only after callback success, so callback implementations must update the pending config consistently. A failed notifier registration after family registration is only warned; the family remains usable. The source snippet contains an apparent duplicated `struct ethnl_dump_ctx {` line in this checkout, which would be a compile-time issue if literal.

## Test Signals
Test signals include genetlink policy validation, GET/SET no-op/change/error paths, dump continuation across small skbs, per-PHY dump filtering by device, notification monitor payloads, socket-private destroy during module flashing, runtime PM pairing, and `NETDEV_PRE_UP` rejection while flashing.
