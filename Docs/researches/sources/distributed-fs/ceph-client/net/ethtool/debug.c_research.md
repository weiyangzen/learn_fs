# sources/distributed-fs/ceph-client/net/ethtool/debug.c

## Purpose
This file implements ethtool netlink GET/SET support for a device driver's debug message mask. It exposes `get_msglevel`/`set_msglevel` through a named bitset of netif message classes.

## Important APIs, Types, And Functions
Important local types are `debug_req_info` and `debug_reply_data`. Public objects are `ethnl_debug_get_policy`, `ethnl_debug_set_policy`, and `ethnl_debug_request_ops`. Core functions are `debug_prepare_data()`, `debug_reply_size()`, `debug_fill_reply()`, `ethnl_set_debug_validate()`, and `ethnl_set_debug()`.

## Control Flow
GET checks for `get_msglevel`, reads the mask inside ethtool ops bracketing, sizes and emits it with `ethnl_bitset32_size()`/`ethnl_put_bitset32()`, using compact format when requested. SET validates that both get and set callbacks exist, reads the current mask, applies the nested bitset update by named debug class, exits if unchanged, and calls `set_msglevel()`.

## State, Persistence, And Dependencies
The persistent state is driver-owned message-level configuration. The file depends on `bitset.c` helpers, `netif_msg_class_names`, ethtool ops callbacks, and generic netlink request infrastructure.

## Integration Points
Registered request ops cover `ETHTOOL_MSG_DEBUG_GET`, SET, and notifications. The debug class names come from `common.c`, giving userspace a stable mapping between bit positions and debug categories.

## Risks
Drivers can implement get without set or vice versa; SET correctly rejects incomplete support. Bitset parsing must reject unknown names or indices beyond `NETIF_MSG_CLASS_COUNT`. Userspace may use compact or verbose formats, so both must stay compatible.

## Test Signals
Tests should cover unsupported callbacks, compact and verbose mask reads, named class updates, no-op updates, invalid names/indices, and successful driver callback invocation with the expected mask.
