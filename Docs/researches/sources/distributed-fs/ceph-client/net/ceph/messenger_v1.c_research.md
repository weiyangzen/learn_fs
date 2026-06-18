# Research: sources/distributed-fs/ceph-client/net/ceph/messenger_v1.c

## Purpose

`messenger_v1.c` implements the original Ceph messenger wire protocol over TCP. It supplies the v1 read/write state machine, banner and connect negotiation, ack/keepalive handling, message framing with header/front/middle/data/footer sections, CRC and optional signature verification, and stream repair hooks for revoking partially transmitted or received messages.

This file is version-specific glue under the generic messenger in `messenger.c`: the core workqueue calls `ceph_con_v1_try_read()` and `ceph_con_v1_try_write()` whenever the client is configured for msgr1.

## Important APIs, Types, and Functions

Externally used v1 hooks:

- `ceph_con_v1_try_read(struct ceph_connection *con)` consumes available socket data through handshake, tags, acks, keepalive acks, and messages.
- `ceph_con_v1_try_write(struct ceph_connection *con)` initiates connect when needed and drains queued control/message data to the socket.
- `ceph_con_v1_revoke()` patches the outgoing stream after current outgoing message revocation by accounting bytes that must be zero-filled/skipped.
- `ceph_con_v1_revoke_incoming()` converts a current incoming message into a skip of the remaining frame.
- `ceph_con_v1_opened()`, `ceph_con_v1_reset_session()`, and `ceph_con_v1_reset_protocol()` expose protocol session state to the core.

Key private helpers:

- TCP wrappers `ceph_tcp_recvmsg()`, `ceph_tcp_recvpage()`, `ceph_tcp_sendmsg()`, and `ceph_tcp_sendpage()` translate `-EAGAIN` to `0` and handle page splice eligibility.
- `prepare_write_banner()`, `prepare_write_connect()`, `process_banner()`, and `process_connect()` implement the v1 connection handshake.
- `prepare_write_message()`, `write_partial_kvec()`, `write_partial_message_data()`, and `prepare_write_message_footer()` serialize messages and CRCs.
- `read_partial_message()` parses message headers, validates sequence numbers and CRCs, allocates incoming messages, reads data, and verifies signatures.
- `process_ack()` discards acked sent or requeued messages.

## Control Flow

Write-side connection setup starts in `ceph_con_v1_try_write()` when the generic connection state is `CEPH_CON_S_PREOPEN`. The v1 code changes state to `CEPH_CON_S_V1_BANNER`, queues the banner and encoded local address, prepares to read the peer banner, sets the tag state to ready, and calls `ceph_tcp_connect()`. After TCP establishment and banner exchange, `ceph_con_v1_try_read()` processes the peer banner, verifies the peer address/nonce, learns the local address if it was blank, moves to `CEPH_CON_S_V1_CONNECT_MSG`, queues the connect message, and prepares to read the connect reply.

`process_connect()` handles authentication challenge/retry, bad feature/protocol responses, bad authorizer, session reset, retry-session, retry-global, ready/seq, and wait/error tags. On `READY` or `SEQ`, it verifies required features, opens the connection, sets peer features and global sequence, increments `connect_seq`, clears auth retry, and either prepares a final seq write/read or starts reading normal tags.

Normal read flow is tag-driven. `CEPH_MSGR_TAG_MSG` prepares and reads a full message; `CEPH_MSGR_TAG_ACK` reads an ack and discards messages; `CEPH_MSGR_TAG_KEEPALIVE2_ACK` updates `last_keepalive_ack`; `CEPH_MSGR_TAG_CLOSE` closes the socket. `read_partial_message()` first reads and CRC-checks the fixed header, validates lengths against maximums, checks monotonically increasing sequence numbers, allocates or skips the message, reads front and optional middle buffers, reads data through normal, sparse, or bounce paths, then reads and validates the footer. If `CEPH_FEATURE_MSG_AUTH` is negotiated, it also verifies the message signature through the connection operations.

Normal write flow drains pending kvecs, skip/zero bytes, and current message payload data. Once current data is complete, it queues the footer. If the connection is open and no current message remains, it prioritizes keepalive, then queued messages, then acks. With no work left, it clears `CEPH_CON_F_WRITE_PENDING`.

## State and Persistence Behavior

The v1 protocol state lives in `con->v1`: outgoing kvec arrays and cursor fields, input base position and tag, auth handshake pointer/retry count, connect sequence, peer global sequence, temporary ack/keepalive storage, incoming header/reply buffers, and skip counters. Persistent state is only in-memory per connection. Session reset clears `connect_seq` and `peer_global_seq`; protocol reset clears partial outgoing skip.

Messages are persisted across reconnect by the generic `out_queue`/`out_sent` lists and sequence fields. V1-specific acks are 64-bit sequence numbers encoded after `ACK` or final `SEQ` tags.

## Dependencies and Integration Points

The file depends on Linux socket send/recv APIs, page sending, CRC32C, Ceph feature bits, Ceph auth/authorizer callbacks, generic message data cursor helpers, and generic connection queueing/refcounting. It uses `con->ops` for authorizer acquisition/challenge/verification, message allocation, sparse reads, signature checks, and peer reset callbacks.

## Risks and Edge Cases

The most sensitive logic is partial framing. `in_base_pos` doubles as a byte offset and a negative skip counter, so incorrect arithmetic can desynchronize the stream. Revoking a message while it is partially queued requires subtracting trailing kvec entries and adding skip bytes so the peer sees a well-framed abort/zero sequence. Sequence-number checks distinguish old duplicate messages, which are skipped, from future gaps, which fault the connection. CRC behavior changes with `NOCRC`; bounce-page behavior changes with `RXBOUNCE`; sparse read callbacks may return a buffer or direct cursor extent. Authorizer retry is bounded, and failures invalidate authorizers after fault handling.

## Test Signals

Validation should cover msgr1 handshake success, bad banner, wrong peer address/nonce, feature mismatch, protocol mismatch, bad authorizer retry then failure, session reset with `peer_reset()`, retry-session/global, final seq exchange, ack discard, keepalive2 timestamp update, partial socket read/write returning zero, CRC failures for header/front/middle/data, signature failures, sparse read receive, RXBOUNCE receive, message revocation in every send phase, incoming revoke/skip, and reconnect preserving or discarding messages according to ack/reconnect sequence.
