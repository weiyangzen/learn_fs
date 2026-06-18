# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/rndis.c

## Purpose
This file implements the Remote NDIS message parser and response engine used by USB Ethernet gadget functions. It translates host RNDIS control messages into NDIS OID responses, updates network-device carrier/filter state, queues RNDIS responses for the USB notification/data path, and wraps or unwraps Ethernet SKBs with RNDIS packet headers.

## Important APIs, types, and functions
Public exported APIs include `rndis_register()`, `rndis_deregister()`, `rndis_set_param_dev()`, `rndis_set_param_vendor()`, `rndis_set_param_medium()`, `rndis_msg_parser()`, `rndis_get_next_response()`, `rndis_free_response()`, `rndis_add_hdr()`, `rndis_rm_hdr()`, `rndis_signal_connect()`, `rndis_signal_disconnect()`, `rndis_uninit()`, and `rndis_set_host_mac()`. Internally, `gen_ndis_query_resp()` handles supported OID queries, `gen_ndis_set_resp()` handles packet-filter and multicast-list sets, and message-specific helpers build INIT, QUERY, SET, RESET, KEEPALIVE, and status-indication responses.

## Control flow
An Ethernet function calls `rndis_register()` with a response-available callback, then sets netdev, vendor, medium, speed, filter, and host MAC parameters. Host control messages enter `rndis_msg_parser()`, which reads the unaligned little-endian message type and length, updates `params->state` for INIT/HALT, and dispatches to response builders. Response builders allocate `rndis_resp_t` entries with `rndis_add_response()`, fill little-endian message structures, and invoke `params->resp_avail()`. The USB function later drains unsent responses with `rndis_get_next_response()` and releases them with `rndis_free_response()`. Data TX uses `rndis_add_hdr()`; RX uses `rndis_rm_hdr()` to strip the RNDIS packet message and queue the Ethernet SKB.

## State and persistence
`struct rndis_params` contains the per-instance state: allocated config number, RNDIS state machine value, saved packet filter pointer, media state, medium/speed, host MAC pointer, netdev pointer, vendor metadata, callback context, and a spinlock-protected response queue. IDs are allocated from a process-wide IDA up to 999. Optional debug proc entries expose and mutate link state. No state persists beyond the registered object lifetime.

## Dependencies and integration points
The code depends on Linux netdevice APIs, SKB helpers, procfs debug support, RNDIS protocol constants from `<linux/rndis.h>`, local `rndis.h`, and `u_rndis.h`. It integrates with the USB Ethernet function through exported symbols and the `gether` receive path. Packet-filter SET has side effects on `netif_carrier_*()` and `netif_{wake,stop}_queue()`.

## Risks and edge cases
RNDIS host input is untrusted. Some query debug dumping reads 16-byte chunks from the provided buffer without checking that the final chunk is complete when debugging is enabled. `rndis_msg_parser()` reads message headers before validating `MsgLength` against the actual control request length, so callers must pass a sufficiently sized buffer. Response queue entries are heap-allocated with GFP_ATOMIC and must be freed by the caller after transmission. `rndis_rm_hdr()` validates packet type and pull length but does not use the `port` argument. State transitions are host-driven and Windows-specific behavior is explicitly accommodated.

## Test signals
Protocol tests should cover INIT, QUERY for every supported OID, unsupported OID status, SET packet filter on/off and resulting netdev queue/carrier state, RESET queue drain, KEEPALIVE, HALT, connect/disconnect indications, response queue ordering and freeing, SKB header add/remove round trips, malformed packet headers, and optional procfs debug commands.
