# sources/distributed-fs/ceph-client/drivers/hv/channel.c

## Purpose
Implements core VMBus channel operations for Hyper-V guests: event notification, ring allocation/freeing, GPADL establishment/teardown, channel open/close/reconnect, packet send/receive, channel retargeting, and request ID tracking.

## Important APIs, Types, and Functions
- Ring APIs: `vmbus_alloc_ring()`, `vmbus_free_ring()`, `vmbus_open()`, `vmbus_connect_ring()`, `vmbus_close()`, `vmbus_disconnect_ring()`.
- GPADL APIs: `vmbus_establish_gpadl()`, internal `__vmbus_establish_gpadl()`, `create_gpadl_header()`, and `vmbus_teardown_gpadl()`.
- Packet APIs: `vmbus_sendpacket_getid()`, `vmbus_sendpacket()`, `vmbus_sendpacket_mpb_desc()`, `vmbus_recvpacket()`, and `vmbus_recvpacket_raw()`.
- Requestor APIs: `vmbus_next_request_id()`, `vmbus_request_addr_match()`, `__vmbus_request_addr_match()`, and `vmbus_request_addr()`.
- Retargeting and notification: `vmbus_setevent()`, `vmbus_send_modifychannel()`.

## Control Flow
Opening a channel allocates or reuses ring pages, optionally initializes the requestor array, establishes a ring GPADL with the host, initializes outbound and inbound ring buffers, posts `CHANNELMSG_OPENCHANNEL`, waits for completion, and transitions state to opened. GPADL establishment builds header/body channel messages for Hyper-V page PFNs, may decrypt memory for host visibility, posts messages, waits for creation status, and records the handle. Close resets callbacks/tasklet access, posts `CHANNELMSG_CLOSECHANNEL`, tears down the ring GPADL, frees requestor state, and then frees ring pages. Packet send builds aligned VMBus descriptors and writes kvecs into the ring; receive delegates to ring-buffer read. Modify-channel uses ACK waiting only for VMBus protocol 5.3 and newer.

## State and Persistence
Per-channel state includes open state, ring page pointer/count/send offset, GPADL handle/buffer/size/decrypted flag, callbacks, requestor freelist/bitmap, target CPU, rescind flag, and close message storage. State is volatile; no disk persistence. Confidential-computing memory visibility is tracked so failed re-encryption intentionally leaks memory rather than freeing pages in an unknown encryption state.

## Dependencies and Integration Points
Depends on VMBus connection globals, Hyper-V message protocols, ring-buffer implementation, architecture Hyper-V page/PFN helpers, tasklets, completions, spinlocks, mutexes, memory encryption helpers, tracing, and exported symbols used by Hyper-V service drivers such as netvsc/storvsc/utilities.

## Risks and Test Signals
Risks include GPADL PFN math for PAGE_SIZE versus HV_HYP_PAGE_SIZE, memory encryption/decryption failure handling, rescind races while waiting for host completions, callback/tasklet races during close, requestor ID exhaustion or leaks, and version-specific modify-channel ACK behavior. Test signals include open/close under rescind, channel retargeting on old/new protocol versions, packet send/receive alignment, GPADL teardown re-encryption, ring reconnect, requestor allocation/match/free cycles, and service driver unload while callbacks are active.
