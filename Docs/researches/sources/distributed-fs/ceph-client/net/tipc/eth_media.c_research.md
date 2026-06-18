# sources/distributed-fs/ceph-client/net/tipc/eth_media.c

## Purpose

`eth_media.c` registers the Ethernet media adapter for TIPC bearers. It converts Ethernet MAC addresses between TIPC media-address structures, discovery message payloads, raw L2 addresses, and printable strings, and supplies default link properties for Ethernet bearers.

## Important APIs, Types, and Functions

Internal functions are `tipc_eth_addr2str()`, `tipc_eth_addr2msg()`, `tipc_eth_raw2addr()`, and `tipc_eth_msg2addr()`. The exported object is `struct tipc_media eth_media_info`, which binds these converters to common L2 send/enable/disable helpers and sets priority, tolerance, window bounds, media type, hardware address length, and name `"eth"`.

## Control Flow

Bearer/media registration consumes `eth_media_info`. When discovery is sent, `addr2msg()` writes media type plus MAC address into the TIPC media info area. When discovery is received, `msg2addr()` skips the discovery preamble and calls `raw2addr()`. Raw address conversion stores the MAC, sets `TIPC_MEDIA_TYPE_ETH`, and marks broadcast via `is_broadcast_ether_addr()`. Printable diagnostics use `%pM`.

## State and Persistence Behavior

The file has no mutable persistent state. `eth_media_info` is static global registration data. Runtime address state is carried in `struct tipc_media_addr` and bearers.

## Dependencies and Integration Points

It depends on TIPC bearer abstractions and Ethernet address helpers. It integrates with generic L2 bearer operations `tipc_l2_send_msg()`, `tipc_enable_l2_media()`, and `tipc_disable_l2_media()`, plus discovery code that serializes/deserializes media addresses.

## Risks and Edge Cases

The string buffer must be at least 18 bytes. Discovery format correctness depends on writing `TIPC_MEDIA_TYPE_ETH` at the media type offset and copying exactly `ETH_ALEN` bytes at the address offset. Broadcast detection controls rejection/handling of discovery messages and bearer destination behavior.

## Test Signals

Enable an Ethernet bearer, inspect discovery packets for media type and MAC placement, verify broadcast media address detection, check `tipc media`/link diagnostics for printable MACs, and compile with Ethernet/L2 bearer support.
