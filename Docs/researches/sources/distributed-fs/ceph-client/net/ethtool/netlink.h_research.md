# sources/distributed-fs/ceph-client/net/ethtool/netlink.h

## Purpose
This header declares the internal ethtool netlink framework shared by all per-command files. It defines common request/reply base structs, update helpers, socket-private state, request operation contracts, policies, request ops externs, and action handler prototypes.

## Important APIs, Types, And Functions
Important inline helpers are `ethnl_strz_size()`, `ethnl_put_strz()`, `ethnl_update_u32()`, `ethnl_update_u8()`, `ethnl_update_bool32()`, `ethnl_update_bool()`, `ethnl_update_binary()`, `ethnl_update_bitfield32()`, `ethnl_reply_header_size()`, and `ethnl_parse_header_dev_put()`. Core types are `struct ethnl_req_info`, `struct ethnl_reply_data`, `enum ethnl_sock_type`, `struct ethnl_sock_priv`, and `struct ethnl_request_ops`.

## Control Flow
Per-command files instantiate `struct ethnl_request_ops` with request/reply command ids, header attr id, struct sizes, optional parse/prepare/size/fill/cleanup callbacks, and optional SET validation and mutation callbacks. `netlink.c` consumes these definitions to implement generic GET, dump, SET, and notifications.

## State And Persistence
The base request tracks referenced netdevice, ref tracker, common flags, and optional PHY index. Reply base stores the current device. Socket-private state stores device, portid, and type for long-running operations such as module firmware flashing.

## Dependencies And Integration Points
The header depends on UAPI ethtool netlink definitions, netdevice, generic netlink, sock internals, and all ethtool command modules. Its extern lists are the integration surface: adding a command generally requires a new request ops object, policy declaration, and `genl_ops` entry in `netlink.c`.

## Risks And Edge Cases
The inline update helpers rely on policy validation to match attribute types. `ethnl_update_binary()` compares and copies only `min(nla_len, len)`, so callers must ensure partial writes are acceptable. `ethnl_parse_header_dev_put()` unconditionally calls `netdev_put()` on the stored pointer; callers must only use it after successful parse or a known-held ref.

## Test Signals
Compile-time coverage is significant because every command includes this header. Runtime tests should verify no-op detection through update helpers, compact reply sizing, request ops cleanup callbacks, socket-private destruction, and invalid `phy_index` header behavior.
