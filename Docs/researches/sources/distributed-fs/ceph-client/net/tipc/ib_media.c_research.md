# sources/distributed-fs/ceph-client/net/tipc/ib_media.c

## Purpose

`ib_media.c` registers the InfiniBand media adapter for TIPC bearers. It mirrors the Ethernet adapter pattern but uses InfiniBand hardware address size, broadcast comparison, formatting, and a smaller maximum link window.

## Important APIs, Types, and Functions

Internal converters are `tipc_ib_addr2str()`, `tipc_ib_addr2msg()`, `tipc_ib_raw2addr()`, and `tipc_ib_msg2addr()`. The exported `struct tipc_media ib_media_info` binds those converters to common L2 media send/enable/disable helpers and sets type `TIPC_MEDIA_TYPE_IB`, hardware address length `INFINIBAND_ALEN`, name `"ib"`, default priority/tolerance/window, and `TIPC_MAX_IB_LINK_WIN` as max window.

## Control Flow

Discovery and bearer code call `addr2msg()` to copy an InfiniBand address into the media info payload and `msg2addr()`/`raw2addr()` to build a `struct tipc_media_addr` from inbound data. `raw2addr()` marks broadcast by comparing the raw address with the bearer broadcast address. Diagnostics use `%20phC` formatting when the caller supplies at least 60 bytes.

## State and Persistence Behavior

The file has no mutable persistent state. Registration data is static, and runtime addresses are stored in bearer/media address objects.

## Dependencies and Integration Points

It depends on `<linux/if_infiniband.h>`, TIPC core, bearer abstractions, and common L2 media helpers. It integrates with discovery serialization and bearer media registration like the Ethernet media module.

## Risks and Edge Cases

Buffer sizing for printable addresses is larger than Ethernet. Discovery format differs from Ethernet because it copies from offset zero rather than setting the Ethernet media preamble fields; any shared discovery assumptions must account for media-specific conversion. Broadcast detection depends on a valid bearer broadcast address.

## Test Signals

Enable an InfiniBand TIPC bearer, verify address formatting, confirm discovery address round trips, test broadcast address detection, and ensure max window defaults differ from Ethernet as expected.
