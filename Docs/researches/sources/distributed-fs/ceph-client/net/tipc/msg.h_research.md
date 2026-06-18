# sources/distributed-fs/ceph-client/net/tipc/msg.h

## Purpose
`msg.h` is the internal TIPC wire-format contract. It defines message users, message types, header sizes, the skb control block layout, packed TIPC header structures, gap-ACK records, inline header bitfield accessors, protocol constants for internal users, and prototypes for the skb/message helpers implemented in `msg.c`.

## Important APIs, Types, And Functions
Important constants include `TIPC_VERSION`, payload types such as `TIPC_CONN_MSG`, `TIPC_NAMED_MSG`, and group message types, internal users such as `BCAST_PROTOCOL`, `LINK_PROTOCOL`, `NAME_DISTRIBUTOR`, `MSG_FRAGMENTER`, `TUNNEL_PROTOCOL`, and `MSG_CRYPTO`, plus header sizes from `SHORT_H_SIZE` through `MAX_H_SIZE`. Important types are `struct tipc_skb_cb`, `struct tipc_msg`, `struct tipc_gap_ack`, and `struct tipc_gap_ack_blks`. Inline APIs read and write every significant header field: size, user/type, errors, sequence/ack, broadcast ACKs/gaps, ports, nodes, service ranges, fragmentation metadata, link state, tunnel sync, group broadcast state, crypto/discovery node IDs, and skb queue operations.

## Control Flow
The header has no standalone runtime loop, but its inlines are on the hot path for nearly all TIPC send and receive logic. `buf_msg()` casts skb data to the wire header; `msg_word()`, `msg_set_word()`, `msg_bits()`, and `msg_set_bits()` centralize endian-aware bitfield access. Higher-level helpers then interpret the same header words differently depending on user/type, for example word 1 bits serve payload type/error/legacy flags, name-distribution bulk markers, or link activation session state. Queue helpers wrap locked or lockless skb list access used by links, sockets, and receive queues.

## State And Persistence
Persistent protocol state is encoded in skb headers and the skb control block. `struct tipc_skb_cb` stores reassembly tail pointers, retransmission metadata, bytes read, chain importance, ackers, retransmit count, validation and optional crypto flags/context. `struct tipc_msg` is a fixed 15-word big-endian header that supports the largest internal layouts. Gap ACK structures persist selective acknowledgement records in message payloads for unicast and broadcast loss reporting.

## Dependencies And Integration Points
The header includes `<linux/tipc.h>` and `core.h`, and is included throughout the TIPC subsystem. It underpins `msg.c`, `link.c`, `bcast.c`, `node.c`, `name_distr.c`, socket receive/transmit code, crypto handling, discovery, group communication, and netlink-facing diagnostics that inspect link/node state. Public prototypes expose the message helper surface used by those modules.

## Risks And Edge Cases
Field overlap is intentional and context-sensitive, so changing one accessor can corrupt unrelated protocol users. Size accessors assume headers have already been validated or pulled into linear data. Several fields are only valid for internal message users, and some helpers transparently descend into an inner header for fragments. `TIPC_SKB_CB` must fit within `skb->cb`, remain packed as expected, and keep crypto fields conditional. Queue helpers mix lock-protected and caller-lock-required forms, so misuse can race list mutation.

## Test Signals
Compile coverage across `CONFIG_TIPC_CRYPTO` variants is important. Runtime signals include protocol header encode/decode tests, endian correctness, max/min header size validation, fragment inner-header access, gap ACK serialization, queue helper behavior under lockdep, payload/internal user importance mapping, legacy/non-legacy name distributor bits, and fuzzing that exercises all accessors through `tipc_msg_validate()` and receive paths.
