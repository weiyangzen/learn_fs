# sources/distributed-fs/ceph-client/include/uapi/linux/tipc_config.h

## Purpose
Defines the legacy TIPC configuration management ABI: command numbers, TLV encoding helpers, generic netlink message header, and TIPC socket configuration message header.

## Important APIs, Types, and Constants
Commands are grouped as public (`TIPC_CMD_GET_NODES`, media/bearer/link/name-table/stats queries), protected (`TIPC_CMD_ENABLE_BEARER`, `DISABLE_BEARER`, link parameter updates), private (`TIPC_CMD_SET_NODE_ADDR`, remote management, netid), and reserved. TLV types include unsigned, strings of several sizes, error string, network address, media/bearer/link names, node/link info, bearer/link config, name table query, and port reference. Config structs include `tipc_node_info`, `tipc_link_info`, `tipc_bearer_config`, `tipc_link_config`, `tipc_name_table_query`, `tlv_desc`, `tlv_list_desc`, `tipc_genlmsghdr`, and `tipc_cfg_msg_hdr`. Inline helpers validate, get/set, append, iterate, and align TLVs and TCM messages.

## Control Flow, State, and Persistence
Userspace builds requests with `TCM_SET` and `TLV_SET`, sends them over generic netlink or TIPC config service, and parses TLV replies. Kernel applies configuration to node, bearer, link, and management state; query replies may contain variable TLV lists.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/string.h>`, `<linux/tipc.h>`, and `<asm/byteorder.h>`. Integrates with TIPC generic netlink family `TIPC`, legacy socket config service, byte-order helpers, and management tools.

## Risks and Test Signals
Risks include TLV length/alignment bugs, network-byte-order mistakes, command privilege rules, deprecated commands, and inline helper use with undersized buffers. Test TLV boundary validation, multi-TLV iteration, public/protected/private privilege behavior, generic netlink header sizing, socket config message encoding, and malformed reply handling.
