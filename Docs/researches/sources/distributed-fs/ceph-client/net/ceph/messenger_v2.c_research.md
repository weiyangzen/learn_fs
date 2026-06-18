# Research: sources/distributed-fs/ceph-client/net/ceph/messenger_v2.c

## Purpose

`messenger_v2.c` implements the Ceph msgr2 protocol for the kernel client. It provides framed control/message transport, msgr2 banner and feature negotiation, authentication exchange, session connect/reconnect, keepalive and ack frames, plain CRC mode, secure AES-GCM mode, HMAC authentication signatures, sparse reads, and revocation handling. It is the modern protocol counterpart to `messenger_v1.c` and is invoked by the generic messenger when `ceph_msgr2()` is true.

The file handles two significantly different on-wire modes: CRC mode, where control and payload integrity are protected by CRC fields, and secure mode, where frame heads and tails are protected/encrypted with GCM using keys returned by the auth layer.

## Important APIs, Types, and Functions

Externally used hooks:

- `ceph_con_v2_try_read()` drives reading through the v2 state machine.
- `ceph_con_v2_try_write()` initiates v2 connections and drains the outgoing iterator.
- `ceph_con_v2_revoke()` and `ceph_con_v2_revoke_incoming()` repair or skip partial frames after message revocation.
- `ceph_con_v2_opened()`, `ceph_con_v2_reset_session()`, and `ceph_con_v2_reset_protocol()` expose and reset v2 session/protocol state.

Frame and wire helpers:

- `init_frame_desc()`, `encode_preamble()`, and `decode_preamble()` describe and validate frame tag, segment count, segment lengths, alignments, and preamble CRC.
- `head_onwire_len()`, `tail_onwire_len()`, `padded_len()`, and related helpers compute plain or secure frame sizes.
- `encode_epilogue_plain()`, `encode_epilogue_secure()`, `decode_epilogue()`, and `verify_epilogue_crcs()` finalize and validate message tails.
- `fill_header()` converts msgr2 headers to generic `ceph_msg_header`; `fill_header2()` converts generic headers to msgr2 message headers.

Crypto and scatter-gather helpers:

- `setup_crypto()` prepares HMAC and optional AES-GCM contexts from auth session keys and connection secrets.
- `con_hmac_sha256()` signs handshake transcript buffers.
- `gcm_crypt()` encrypts/decrypts and increments GCM nonces.
- `setup_message_sgs()` builds scatterlists over front, middle, data, padding, and epilogue for secure tail encryption/decryption.

Handshake and control-frame helpers:

- `prepare_banner()`, `prepare_hello()`, `prepare_auth_request()`, `prepare_auth_request_more()`, `prepare_auth_signature()`, `prepare_client_ident()`, and `prepare_session_reconnect()` generate outbound handshake frames.
- `process_banner_prefix()`, `process_banner_payload()`, `process_hello()`, `process_auth_bad_method()`, `process_auth_reply_more()`, `process_auth_done()`, `process_auth_signature()`, `process_server_ident()`, `process_session_reconnect_ok()`, `process_session_retry()`, `process_session_retry_global()`, and `process_session_reset()` process inbound handshake/session frames.

Message data helpers:

- `prepare_read_tail_plain()`, `prepare_read_tail_secure()`, `prepare_read_data()`, `prepare_sparse_read_data()`, `handle_epilogue()`, and `process_message_header()` handle inbound message bodies.
- `prepare_message_plain()`, `prepare_message_secure()`, `queue_data()`, `queue_data_cont()`, `queue_enc_page()`, and `finish_message()` handle outbound message bodies.

## Control Flow

`ceph_con_v2_try_write()` is responsible for opening from `CEPH_CON_S_PREOPEN`. It verifies the peer address type is msgr2, obtains a new global sequence, increments connect sequence if reconnecting, prepares to read the banner prefix, queues the local banner, and initiates the TCP connect. It then repeatedly populates and sends `con->v2.out_iter`, corking the TCP socket while draining batches.

`ceph_con_v2_try_read()` expects an already populated inbound iterator. It calls `ceph_tcp_recv()` until the iterator is satisfied, then calls `populate_in_iter()` to process what was read and schedule the next read. Early states read banner prefix and payload, validate msgr2 feature compatibility, send `HELLO`, then read framed control messages. Once `HELLO` succeeds, the client sends auth requests through monitor/connection auth callbacks. `AUTH_DONE` returns global id, selected connection mode, session key, and connection secret; `setup_crypto()` prepares HMAC and possibly GCM. Both sides then validate transcript HMACs with `AUTH_SIGNATURE`. The client either sends `CLIENT_IDENT` for a new session or `SESSION_RECONNECT` when it has server cookies.

When `SERVER_IDENT` is accepted, the code validates peer address, required features, peer global id/seq, lossy flag/cookie consistency, stores peer features and server cookie, clears handshake transcript buffers, frees temporary connection buffers, resets backoff, and marks the connection open. Reconnect may also produce `SESSION_RECONNECT_OK`, `SESSION_RETRY`, `SESSION_RETRY_GLOBAL`, or full `SESSION_RESET`, each updating sequence/cookie state or falling back to a fresh client ident.

Once open, inbound frames are parsed by preamble and tag. Non-message tags go to `process_control()`. `FRAME_TAG_MESSAGE` goes through `process_message_header()`, sequence validation, ack discard, generic incoming allocation, and either immediate dispatch for empty messages or tail reading. Plain mode reads front/middle/data directly and checks epilogue CRCs. Secure mode reads encrypted tail pages and decrypts the whole tail through scatterlists before dispatch. Sparse reads can direct data into callback-provided buffers or into data cursor pages.

Outbound open-state priority is keepalive, queued messages, then ack. `prepare_message()` builds a `FRAME_TAG_MESSAGE`, fills msgr2 header2 including piggyback ack, and chooses plain or secure preparation. Plain mode can stream data pages directly and computes CRCs incrementally. Secure mode must allocate encrypted pages for the whole tail because kernel AEAD is not used in streaming mode.

## State and Persistence Behavior

All v2 state is in `con->v2`. Session-persistent fields include `client_cookie`, `server_cookie`, `global_seq`, `connect_seq`, and `peer_global_seq`; these determine whether reconnect can resume a session. Protocol-transient fields include inbound/outbound iterators, kvec arrays, sign transcript kvecs, connection buffers, frame descriptors, in/out state enums, data cursors, encrypted page vectors, zero-fill counters, connection mode, GCM nonces, HMAC key state, and crypto transform/request pointers.

`ceph_con_v2_reset_session()` clears cookies and sequence values, forcing a future fresh session. `ceph_con_v2_reset_protocol()` truncates iterators, clears zero-fill state, drops sign buffers and temporary connection buffers, releases encrypted page vectors, resets connection mode, zeroes GCM nonces and HMAC key material, and frees crypto API resources.

## Dependencies and Integration Points

The file depends on Linux kernel sockets, `iov_iter`, scatterlists, page vectors, CRC32C, TCP corking, crypto AEAD `gcm(aes)`, SHA-256 HMAC helpers in Ceph `crypto.h`, and common messenger data cursors from `messenger.c`. It uses `decode.c` address encode/decode functions. Authentication is delegated through `con->ops->get_auth_request()`, `handle_auth_reply_more()`, `handle_auth_done()`, and `handle_auth_bad_method()`, which the monitor client supplies for monitor sessions. Message allocation and dispatch are still generic `con->ops` responsibilities.

## Risks and Edge Cases

The highest risks are frame length validation, iterator state transitions, and crypto buffer lifetime. Preamble validation bounds control/front/middle/data lengths and rejects empty trailing segments. Secure mode needs careful padding and scatterlist construction for vmalloc buffers, page arrays, data cursors, and epilogue/auth tags. GCM nonces must advance exactly once per encrypted/decrypted unit, including skipped secure messages. Revocation in secure mode is effectively a no-op for already encrypted outbound frames, while plain mode actively zero-fills residual front/middle/data and marks the epilogue aborted with adjusted CRCs.

Temporary connection buffers are allocated throughout handshake and freed when the session opens, on retry, or on reset. Many operations temporarily drop `con->mutex` for auth callbacks and must recheck protocol state afterward. Secure mode may allocate up to the full message tail as encrypted pages, so memory pressure and allocation-failure paths are important. Sparse reads are complex because callbacks can return direct buffers or cursor extents and because CRC accounting differs between plain and secure paths.

## Test Signals

Strong tests include msgr2 banner compatibility, peer speaking msgr1 to a v2 client, missing required msgr2 features, hello peer type mismatch, address learning when local address is blank, auth-more loops, auth-bad-method, auth-done in CRC and secure modes, bad auth signatures, server-ident feature/address/cookie validation, reconnect ok/retry/retry-global/session-reset, ack discard, keepalive timestamp update, message sequence duplicate/gap handling, plain CRC failures, secure auth tag failures for preamble/control/tail, sparse reads in plain and secure mode, RXBOUNCE receive, memory allocation failure in encrypted tail setup, and revoke paths for each in/out state.
