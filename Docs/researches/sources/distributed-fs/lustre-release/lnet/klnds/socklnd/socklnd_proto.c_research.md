# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_proto.c

## Purpose
Implements socklnd wire protocol variants v1, v2, v3, and v4. It owns hello serialization/deserialization, LNet header packing/unpacking, connection-type TX matching, zero-copy request/ACK handling, NOOP ACK piggybacking, and the exported `ksock_proto` operation tables.

## Important APIs and functions
Protocol tables `ksocknal_protocol_v1x`, `v2x`, `v3x`, and `v4x` provide callbacks consumed by the rest of socklnd. Queueing helpers include `ksocknal_queue_tx_msg_v1`, `ksocknal_queue_tx_msg_v2`, `ksocknal_queue_tx_zcack_v2`, `ksocknal_queue_tx_zcack_v3`, and `ksocknal_next_tx_carrier`. Matching functions are `ksocknal_match_tx`, `ksocknal_match_tx_v3`, and `ksocknal_match_tx_v4`. Handshake helpers are versioned send/receive functions. Pack/unpack helpers convert between LNet header forms and socklnd message layout.

## Control flow
V1 sends bare legacy LNet headers and has no NOOP or zero-copy support. V2/V3 use NID4 hello and `ksock_msg_hdr`; V4 uses the large-NID hello and NID16 LNet header. Normal TX queueing tries to replace queued NOOP zero-copy ACKs by piggybacking their cookie onto an LNet message. Zero-copy ACK queueing tries to piggyback on a carrier TX; v3/v4 can compact ACK cookies or ranges on ACK connections and ignore keepalive PING cookies. Incoming zero-copy requests find a matching ACK-capable connection or allocate a NOOP. Incoming ACKs remove matching TXs from the peer pending zero-copy request list.

## State and persistence
The file does not own global state but mutates connection TX queues, `ksnc_tx_carrier`, message cookie fields, peer zero-copy request lists, connection byte-order flip flags, and TX refs. Protocol tables are static read-only dispatch state.

## Dependencies and integration points
Depends on `socklnd-idl.h`, LNet NID4/NID16 conversion helpers, `lnet_sock_read/write`, `the_lnet.ln_testprotocompat`, and peer/connection helpers from `socklnd_cb.c`.

## Risks and test signals
Compatibility risk is high: v1/v2/v3/v4 peers must parse each other's hello and message formats correctly, including byte-swapped peers and protocol mismatch replies. Zero-copy cookie compaction must not lose or duplicate ACKs. Test mixed protocol negotiation, large-NID v4 peers, checksum-enabled v2 traffic, nonblocking ACK routes, keepalive PINGs, duplicate cookie detection, protocol compatibility injection bits, and typed-connection matching around the bulk threshold.
