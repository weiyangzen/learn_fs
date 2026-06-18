# sources/distributed-fs/ceph-client/net/qrtr/qrtr.h

## Purpose
`qrtr.h` is the private QRTR core/transport interface. It defines the endpoint abstraction used by transport drivers and declares core endpoint and nameservice lifecycle functions.

## Important APIs, Types, And Functions
The central type is `struct qrtr_endpoint`, with an `xmit()` callback and private `struct qrtr_node *node`. Public functions are `qrtr_endpoint_register()`, `qrtr_endpoint_unregister()`, `qrtr_endpoint_post()`, `qrtr_ns_init()`, and `qrtr_ns_remove()`. `QRTR_EP_NID_AUTO` requests node id auto-assignment from incoming traffic.

## Control Flow
Transports fill `ep.xmit`, call register, pass inbound bytes to `qrtr_endpoint_post()`, and unregister on device/file removal. The core calls `xmit()` with skbs it no longer owns; transport drivers must consume or free them.

## State And Persistence
The header exposes only the endpoint handle. The private `node` pointer is owned by QRTR core and persists from register to unregister.

## Dependencies And Integration Points
This file is shared by `af_qrtr.c`, `ns.c`, and transport drivers `mhi.c`, `smd.c`, and `tun.c`. It intentionally hides `struct qrtr_node` internals from transports.

## Risks
The ownership contract for `xmit()` is critical: transport code must free or consume skbs exactly once. Endpoint users must not access the private node pointer except through core APIs.

## Test Signals
Test signals are mostly integration-level: endpoint register rejection for missing `xmit`, unregister cleanup, inbound post after registration, and transport skb ownership behavior.
