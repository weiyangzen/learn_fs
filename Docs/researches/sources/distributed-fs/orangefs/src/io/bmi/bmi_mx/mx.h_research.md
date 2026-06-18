# sources/distributed-fs/orangefs/src/io/bmi/bmi_mx/mx.h

## Purpose
Defines the private ABI, constants, state structures, enums, allocation helpers, and debug macros for the OrangeFS BMI MX transport implemented in `mx.c`.

## Important APIs, Types, And Functions
Important definitions include `BMX_MAGIC`, `BMX_VERSION`, peer and unexpected receive pool sizes, unexpected message size, match-bit shifts/masks, timeout, memory-pool sizes, `BMX_MALLOC`, `BMX_FREE`, `struct bmx_data`, `struct bmx_method_addr`, `struct bmx_peer`, `struct bmx_ctx`, `struct bmx_connreq`, `enum bmx_peer_state`, `enum bmx_req_type`, `enum bmx_ctx_state`, and `enum bmx_msg_type`. Debug categories such as `BMX_DB_CTX`, `BMX_DB_PEER`, `BMX_DB_CONN`, and `BMX_DB_MX` control gossip logging through `debug`, `BMX_ENTER`, and `BMX_EXIT`.

## Control Flow
The header encodes the assumptions used by `mx.c`: peer ids occupy 20 match bits, BMI tags occupy 32 low bits, message type occupies the top nibble, and connection messages reuse the id field to exchange peer ids and the tag field to carry the protocol version. Context states describe the lifecycle from idle to prepared, queued, pending, completed, or canceled. Peer states describe disconnected/init/wait/ready transitions around the MX iconnect and connection-ack protocol.

## State And Persistence
`struct bmx_data` is the global runtime container for one MX method instance, including endpoint identity, peername, peer list, global and idle TX/RX lists, completion queues per BMI context, unexpected receive queue, next peer id, locks, and optional pooled buffers. `struct bmx_peer` persists remote endpoint identity, connection session, assigned ids, queues, pending receives, and refcount while a method address is live. `struct bmx_ctx` persists the per-operation transport state until BMI test/cancel returns it to an idle list. The header defines no disk persistence.

## Dependencies And Integration Points
It includes MX runtime headers, BMI method support and callback headers, BMI types, quicklist, gen-locks, gossip, id-generator, and PVFS internal helpers. The type layout is private to the BMI MX method but tightly coupled to `mx.c`, BMI `method_op`, and MX request/status/segment types.

## Risks And Test Signals
Changing match-bit constants or enum values can break interoperability between clients and servers. Pool sizes directly affect unexpected-message loss behavior and memory footprint. `BMX_MEM_TWEAK` is enabled by default and changes allocation semantics, so allocation tests should cover pooled and fallback allocations. Debug masking currently logs only warnings/errors by default even though many internal debug calls exist. Compile coverage of `mx.c`, handshake interoperability tests across version/match-bit changes, and stress tests around context get/put accounting are the main signals.
