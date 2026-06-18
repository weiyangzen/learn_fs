# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/rndis.h

## Purpose
This header defines RNDIS message layouts, per-instance state, response queue records, and exported function prototypes for the USB gadget RNDIS implementation. It is the contract between `rndis.c` and USB Ethernet function code.

## Important APIs, types, and functions
Wire-format typedefs cover INIT, HALT, QUERY, SET, RESET, INDICATE_STATUS, KEEPALIVE, packet, and configuration-parameter messages. `struct rndis_packet_msg_type` is packed and used as the data-plane header. `enum rndis_state` models uninitialized, initialized, and data-initialized states. `rndis_resp_t` stores queued control responses. `rndis_params` stores netdev, filter, state, medium/speed, media state, host MAC, vendor metadata, response callback, callback context, and a spinlock-protected response list. Prototypes expose registration, parser, parameter setters, response draining, header conversion, state signals, and host MAC update.

## Control flow
Consumers allocate a `rndis_params` with `rndis_register()`, provide the netdev/filter and metadata, feed EP0 control payloads into `rndis_msg_parser()`, transmit queued responses obtained from `rndis_get_next_response()`, and release them with `rndis_free_response()`. Data packets are converted through `rndis_add_hdr()` and `rndis_rm_hdr()`.

## State and persistence
All state is per registered `rndis_params`. The response queue is protected by `resp_lock`; the packet filter pointer is supplied by the CDC/RNDIS Ethernet function and is updated by SET OID handling. There is no persistent storage.

## Dependencies and integration points
The header includes `<linux/rndis.h>` for constants, `u_ether.h` for `struct gether`, and `ndis.h` for NDIS PM structures. It exports the API shape that `f_rndis`/Ethernet gadget code relies on.

## Risks and edge cases
Wire structures use little-endian fields and fixed offsets; changes must preserve RNDIS host ABI. `rndis_params` contains raw pointers to netdev, filter, host MAC, and vendor description, so lifetime must be managed by the caller. The packed packet header must remain layout-compatible with host RNDIS framing.

## Test signals
Build all RNDIS gadget functions, verify structure sizes and offsets used by protocol tests, run RNDIS enumeration with a host, exercise response queue APIs, and validate SKB header conversion against known packet captures.
