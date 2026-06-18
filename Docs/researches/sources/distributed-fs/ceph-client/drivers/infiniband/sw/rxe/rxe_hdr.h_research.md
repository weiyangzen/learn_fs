# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hdr.h

## Purpose
`rxe_hdr.h` defines RXE packet metadata and inline accessors for InfiniBand/RoCE transport headers stored in SKBs or send buffers.

## Important APIs, types, and functions
`struct rxe_pkt_info` fits in `skb->cb` and carries device, QP, WQE, BTH pointer, opcode, mask, PSN, pkey index, payload length, and port. The header defines BTH, RDETH, DETH, RETH, FETH, ATMETH, AETH, ATMACK, immediate, and invalidate header structs plus field masks and inline getters/setters. Helpers include `SKB_TO_PKT()`, `PKT_TO_SKB()`, `bth_init()`, `feth_init()`, `header_size()`, `payload_addr()`, and `payload_size()`.

## Control flow
There is no standalone control flow, but every packet path uses these accessors to parse received headers, build outgoing headers, compute payload ranges, and interpret ACK/NAK syndromes and atomic/read/write parameters.

## State and persistence
Packet state is transient in skb control blocks and packet header buffers. `BUILD_BUG_ON(sizeof(struct rxe_pkt_info) > sizeof(skb->cb))` protects the skb control-block ABI.

## Dependencies and integration points
The header depends on `rxe_opcode[]` offset metadata and Linux networking SKB layout. It is used by requester, responder, receiver, network transmit/receive, ICRC, and completer code.

## Risks
Offset calculations rely on `rxe_opcode[pkt->opcode]` matching the actual packet opcode and header layout. `payload_size()` subtracts header offset, BTH padding, and ICRC; malformed `paylen` or opcode metadata can underflow. Inline byte-order and reserved-bit setters must match IB/RoCE specifications exactly.

## Test signals
Packet encode/decode tests should cover all supported opcodes, BTH reserved bits, PSN and QPN masking, immediate/invalidate fields, AETH syndromes, FLUSH headers, payload size with padding and ICRC, and receive rejection of too-short packets.
