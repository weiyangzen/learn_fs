# Research: subset-b-006174 Ceph client net/ceph transport and monitor files

This grouped report covers the seven source files in `subset-b-006174`. Each file section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/debugfs.c -->
# Research: sources/distributed-fs/ceph-client/net/ceph/debugfs.c

## Purpose

`debugfs.c` implements the debugfs surface for the in-kernel Ceph client library when `CONFIG_DEBUG_FS` is enabled. It creates `/sys/kernel/debug/ceph` and one per-client directory named from the cluster fsid and authenticated client global id, then exposes read-only seq-file views for monitor state, OSD map state, OSD client requests, and libceph client options. When debugfs is disabled, the same init and cleanup entry points compile to no-ops so callers do not need conditional code.

The file is observability-only. It does not persist configuration, mutate cluster state, or participate in protocol logic. Its output is nevertheless operationally important because it makes map versions, active requests, linger registrations, backoffs, and client options visible without tracing.

## Important APIs, Types, and Functions

Exported or externally called entry points:

- `ceph_debugfs_init()` creates the top-level `ceph` debugfs directory during module initialization.
- `ceph_debugfs_cleanup()` removes the top-level directory.
- `ceph_debugfs_client_init(struct ceph_client *client)` creates the per-client directory and files: `monc`, `osdc`, `monmap`, `osdmap`, and `client_options`.
- `ceph_debugfs_client_cleanup(struct ceph_client *client)` removes those per-client dentries.

Seq-file show callbacks:

- `monmap_show()` prints monitor map epoch and monitor entity/address rows under `client->monc.mutex`.
- `osdmap_show()` prints OSD map epoch, barrier, pools, OSD addresses/state/weights/locality, and temporary PG mappings under `osdc->lock`.
- `monc_show()` prints monitor subscription state, fs cluster id, and generic monitor requests from `generic_request_tree`.
- `osdc_show()` prints active OSD requests, linger requests, and OSD backoffs across all known OSD sessions plus the homeless OSD.
- `client_options_show()` delegates to `ceph_print_client_options()`.

Formatting helpers include `dump_spgid()`, `dump_target()`, `dump_request()`, `dump_linger_request()`, `dump_snapid()`, `dump_name_escaped()`, `dump_hoid()`, and `dump_backoffs()`. `DEFINE_SHOW_ATTRIBUTE()` generates the file operations for each seq-file view.

## Control Flow

Initialization is simple: `ceph_debugfs_init()` creates a root dentry and stores it in the static `ceph_debugfs_dir`. For each client, `ceph_debugfs_client_init()` formats a directory name as `%pU.client%lld`, creates that directory beneath the root, and attaches each seq-file to the client object as `private` data.

Each read path is lock-scoped around the subsystem whose state it traverses. `monmap_show()` and `monc_show()` use `monc->mutex` because they read monitor subscription and monmap state. `osdmap_show()` and `osdc_show()` take the OSD client read lock before walking map red-black trees or the OSD session tree; the request, linger, and backoff dumps then take each OSD's mutex while walking per-OSD rbtrees. Cleanup removes files in reverse enough order to detach per-client views before removing the directory.

## State and Persistence Behavior

The only file-local state is `ceph_debugfs_dir`, a debugfs dentry pointer. Per-client dentry pointers are stored in `struct ceph_client`, `struct ceph_mon_client`, and `struct ceph_osd_client`. All other state is read from live Ceph client objects. There is no durable persistence and no cached snapshot: seq-file reads reflect the current in-memory state at read time, subject to the locks held while formatting.

## Dependencies and Integration Points

This file depends on Linux `debugfs` and `seq_file`, libceph client structures, monitor client state, OSD client maps/requests/backoffs, Ceph address formatting via `ceph_pr_addr()`, OSD map helpers, and client option printing. It integrates upward with libceph init/teardown paths and downward with the monitor and OSD clients by storing debugfs dentries in their embedded structs.

## Risks and Edge Cases

The main risks are observability races and output cost rather than protocol corruption. Large OSD maps or many requests can produce large debugfs reads while holding locks, so this path can add diagnostic overhead on busy clients. The code assumes internal rbtrees and request objects remain valid under the documented locks. Name escaping for object identifiers is careful for `%`, `:`, `/`, non-printable bytes, and non-ASCII bytes; malformed or very long object names are bounded by stored lengths but can still make output large. If debugfs creation fails, the kernel debugfs helpers generally return error dentries or null-like entries and the code does not propagate errors; this matches many debugfs call sites but means missing observability is not fatal.

## Test Signals

Useful validation is mostly runtime and integration-oriented: build with and without `CONFIG_DEBUG_FS`; mount or initialize a Ceph client and verify the expected files appear; read each file while monitor subscriptions, OSD requests, linger requests, and backoffs are active; run lockdep while reading debugfs under concurrent map updates and request completion; check that client cleanup removes all dentries without use-after-free reports. Output-specific tests should exercise object names requiring escaping, empty maps, missing monmap/osdmap pointers, and clients with no active OSD sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/decode.c -->
# Research: sources/distributed-fs/ceph-client/net/ceph/decode.c

## Purpose

`decode.c` centralizes Ceph entity address decoding and encoding for the kernel client. It handles both legacy address encodings and versioned `entity_addr_t` / `entity_addrvec_t` encodings used by msgr2-aware peers. The key job is to safely decode wire-format monitor and peer addresses into `struct ceph_entity_addr`, select the address type appropriate for msgr1 or msgr2, and encode the client's own address back into the modern versioned form.

## Important APIs, Types, and Functions

Public functions:

- `ceph_decode_entity_addr(void **p, void *end, struct ceph_entity_addr *addr)` reads a marker byte and dispatches to versioned marker `1` or legacy marker `0` decoding.
- `ceph_decode_entity_addrvec(void **p, void *end, bool msgr2, struct ceph_entity_addr *addr)` decodes marker `2`, walks all embedded addresses, and selects exactly one address matching either `CEPH_ENTITY_ADDR_TYPE_MSGR2` or `CEPH_ENTITY_ADDR_TYPE_LEGACY`.
- `ceph_entity_addr_encoding_len(const struct ceph_entity_addr *addr)` computes the modern encoded size for the address family.
- `ceph_encode_entity_addr(void **p, const struct ceph_entity_addr *addr)` emits marker `1`, an encoding block, address type, nonce, sockaddr length, family, and sockaddr data.

Private helpers:

- `ceph_decode_entity_addr_versioned()` uses `ceph_start_decoding()` to respect a bounded structured block and skips unknown tail fields by advancing to `struct_end`.
- `ceph_decode_entity_addr_legacy()` handles the old layout, maps old clients' `TYPE_NONE` style to `CEPH_ENTITY_ADDR_TYPE_LEGACY`, and converts sockaddr family from big-endian legacy wire order.
- `get_sockaddr_encoding_len()` selects IPv4, IPv6, or generic sockaddr storage size for encoding.

## Control Flow

The decode paths all advance a caller-owned buffer pointer and validate against an end pointer through Ceph safe-decode macros. For a single address, `ceph_decode_entity_addr()` consumes the marker, then either decodes a structured block or the legacy fields. The versioned path validates `addr_len` against the storage size, zeroes the destination sockaddr, copies only the encoded length, fixes the sockaddr family endian, and skips any future fields in the encoding block.

For an address vector, `ceph_decode_entity_addrvec()` requires marker `2`, decodes the count, then decodes each member using the single-address routine. It picks the type required by the caller's messenger mode and rejects duplicate matches. A vector with no entries, or a single all-zero decoded address, is treated as an empty address slot and succeeds without filling a meaningful target. A non-empty vector with no matching address returns `-ENOENT`.

Encoding is the inverse modern path: determine sockaddr length from the address family, write the marker and block header, copy `type` and `nonce`, write `addr_len`, encode the family as little-endian, and copy the remainder of `sockaddr_storage.__data`.

## State and Persistence Behavior

There is no persistent state and no allocation. The functions mutate only the passed buffer pointer and destination address. Error handling returns negative errno values and leaves the buffer pointer wherever the safe-decode macro stopped; callers should treat failure as fatal for the current message or map decode.

## Dependencies and Integration Points

The file depends on Ceph decode helpers from `linux/ceph/decode.h`, address structures from `linux/ceph/messenger.h`, and kernel sockaddr definitions. `ceph_decode_entity_addrvec()` is used by monitor map decoding in `mon_client.c` and by msgr2 session identity processing in `messenger_v2.c`. `ceph_encode_entity_addr()` is used by msgr2 hello/client-ident/reconnect frame preparation.

## Risks and Edge Cases

Address selection is strict: duplicate matching address types are rejected to avoid ambiguous peer endpoints. Empty vectors are tolerated for unused OSD slots, and a weird single zeroed address is also treated as empty. The legacy path intentionally rewrites type to `LEGACY` for forward compatibility, which is important for clients that never supported address type metadata. Versioned decode validates `addr_len`, but encoding uses the current sockaddr family, so callers must ensure the address family is set consistently before encoding. Endian handling differs between legacy and modern layouts, making regression tests around family conversion valuable.

## Test Signals

Good test signals include decoding legacy IPv4/IPv6 addresses, versioned IPv4/IPv6 addresses, msgr2 and legacy address vectors, duplicate matching vector entries, no-match vectors, zero-entry vectors, truncated buffers at each field, oversized `addr_len`, and encode/decode round trips. Integration tests should cover monmap decoding in both msgr1 and msgr2 modes and msgr2 handshake identity validation with an address vector containing both legacy and msgr2 addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/decode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/messenger.c -->
# Research: sources/distributed-fs/ceph-client/net/ceph/messenger.c

## Purpose

`messenger.c` is the protocol-independent core of the kernel Ceph messenger. It owns connection lifetime, TCP socket callback wiring, the per-connection workqueue engine, generic fault and reconnect behavior, message queueing and acknowledgement handling, message allocation/refcounting, data-payload cursor logic, address parsing/formatting, and messenger instance initialization. The version-specific files `messenger_v1.c` and `messenger_v2.c` plug into this core through `ceph_con_v[12]_try_read()`, `ceph_con_v[12]_try_write()`, revoke, opened, and reset hooks.

The messenger promises ordered reliable delivery over TCP where possible. It tolerates disconnects, CRC/signature failures, and protocol faults by resetting the socket/protocol state, requeueing unacknowledged messages, and retrying with exponential backoff unless the connection is lossy or idle enough to enter standby.

## Important APIs, Types, and Functions

Connection and messenger lifecycle:

- `ceph_msgr_init()`, `ceph_msgr_exit()`, and `ceph_msgr_flush()` create/destroy/flush the global message slab, zero page reference, and `ceph-msgr` workqueue.
- `ceph_messenger_init()`, `ceph_messenger_fini()`, and `ceph_messenger_reset_nonce()` initialize a client messenger instance, manage its network namespace, and update the encoded local address.
- `ceph_con_init()`, `ceph_con_open()`, `ceph_con_close()`, `ceph_con_opened()`, `ceph_con_reset_session()`, and the private `ceph_con_reset_protocol()` manage an individual `struct ceph_connection`.

Socket and workqueue operations:

- `ceph_tcp_connect()` creates a kernel TCP socket, installs callbacks, optionally enables `TCP_NODELAY`, and starts a nonblocking connect.
- `ceph_con_close_socket()` shuts down and releases the socket and clears `CEPH_CON_F_SOCK_CLOSED`.
- `ceph_sock_data_ready()`, `ceph_sock_write_space()`, and `ceph_sock_state_change()` translate socket events into queued connection work.
- `ceph_con_workfn()` is the central worker: handle socket-close and backoff flags, dispatch version-specific read/write loops, and invoke fault handling on errors.

Message and queue operations:

- `ceph_con_send()` consumes a message reference and appends it to `out_queue`.
- `ceph_con_get_out_msg()` moves the next queued message to `out_sent`, assigns sequence numbers, and optionally calls `ops->reencode_message`.
- `ceph_con_discard_sent()` and `ceph_con_discard_requeued()` release messages acknowledged by the peer or already handled before reconnect.
- `ceph_msg_revoke()` and `ceph_msg_revoke_incoming()` remove or skip outgoing/incoming messages, delegating protocol-specific stream repair to v1/v2 hooks.
- `ceph_msg_new2()`, `ceph_msg_new()`, `ceph_msg_get()`, `ceph_msg_put()`, and `ceph_msg_dump()` allocate, retain, release, and debug-dump `struct ceph_msg`.

Data payload cursor APIs:

- `ceph_msg_data_add_pages()`, `ceph_msg_data_add_pagelist()`, `ceph_msg_data_add_bio()`, `ceph_msg_data_add_bvecs()`, and `ceph_msg_data_add_iter()` attach payload segments.
- `ceph_msg_data_cursor_init()`, `ceph_msg_data_next()`, and `ceph_msg_data_advance()` drive page-by-page send/receive over pages, pagelists, bios, bvecs, and iov_iters.
- `ceph_crc32c_page()` maps a page to compute CRC32C.

Address helpers:

- `ceph_pr_addr()`, `ceph_addr_is_blank()`, `ceph_addr_port()`, `ceph_addr_set_port()`, and `ceph_parse_ips()` format and parse Ceph entity addresses, including optional DNS resolver support.

## Control Flow

The connection state model has two layers. `con->state` tracks Ceph protocol states such as `CLOSED`, `PREOPEN`, v1/v2 handshake phases, `OPEN`, and `STANDBY`. `con->sock_state` separately tracks TCP socket state transitions from closed to connecting, connected, closing, and closed using atomic exchange helpers that warn on unexpected transitions.

Opening starts in `ceph_con_open()`, which sets peer identity/address and queues work. `ceph_con_workfn()` runs under `con->mutex`. If the connection is `PREOPEN`, the version-specific write path initiates the TCP connect and handshake. Each work iteration tries reads first, then writes, using msgr2 selection from `ceph_msgr2(from_msgr(con->msgr))`. A negative read/write result marks a fault unless it is `-EAGAIN`, which loops because the callback path may have dropped the mutex and state changed.

Socket callbacks are intentionally small. Data readiness and write-space events call `queue_con()` if the messenger is not stopping and data or write capacity is relevant. TCP close/close-wait marks the socket closing, sets `CEPH_CON_F_SOCK_CLOSED`, and queues work. The worker later converts the asynchronous socket flag into a controlled fault under `con->mutex`.

Outgoing message flow is `ceph_con_send()` -> `out_queue` -> `ceph_con_get_out_msg()` -> version-specific serialization -> `out_sent` until acknowledged. Assigning the message sequence happens only the first time a message leaves `out_queue`, so requeued messages retain their original sequence. Incoming flow is version-specific parsing -> `ceph_con_in_msg_alloc()` -> `ceph_con_process_message()`. Allocation temporarily drops `con->mutex` while invoking `ops->alloc_msg()`, then rechecks that the connection is still open.

Fault handling resets protocol state, closes the socket, drops current in/out messages, and calls the selected protocol reset hook. Lossy connections close permanently. Non-lossy connections splice `out_sent` back to `out_queue`; if no outbound work or keepalive remains, the connection enters `STANDBY`, otherwise it returns to `PREOPEN`, increases `delay` up to `MAX_DELAY_INTERVAL`, sets `CEPH_CON_F_BACKOFF`, and queues later work. `con_fault_finish()` runs outside the connection mutex and notifies `ops->fault()`.

## State and Persistence Behavior

All state is in memory. Global module state includes the message slab cache, workqueue pointer, zero page reference, and a small rotating address-format buffer. Per-messenger state includes global sequence, local entity address and name, stopping flag, and network namespace. Per-connection state includes flags, peer identity/address, socket pointer/state, current protocol state, backoff delay, message queues, sequence counters, current input/output messages, bounce page, and protocol-specific v1/v2 substructures.

Message lifetime is reference counted with `kref`. A message may hold a connection reference through `msg_con_set()`, a middle buffer, and one or more data items. When a pooled message reaches zero references, `ceph_msg_release()` returns it to its pool via `ceph_msgpool_put()`; otherwise it frees the front buffer, data array, and slab object.

## Dependencies and Integration Points

This file integrates with Linux kernel sockets, workqueues, namespaces, DNS resolver, TCP helpers, bio/iov APIs, CRC32C, and Ceph protocol headers. It depends on connection operation callbacks supplied by monitor, OSD, MDS, or other clients: `get`, `put`, `alloc_msg`, `dispatch`, `fault`, `peer_reset`, `reencode_message`, and authentication/signature hooks used by protocol versions. It exports the generic APIs consumed by the monitor client (`mon_client.c`), OSD client, CephFS, and RBD.

## Risks and Edge Cases

The highest-risk areas are concurrency and partial I/O. `con->mutex` protects most connection state, but socket callbacks set flags asynchronously and message allocation/dispatch temporarily drops the mutex. State is rechecked after those drops, and refcounting through `ops->get()` prevents queued work from racing teardown. Cursor code has many `BUG_ON()` invariants; callers must attach valid data items matching declared lengths before sending or receiving payloads. Revoke paths depend on v1/v2 stream repair to preserve framing after a partially sent or received message is abandoned. Fault handling must not lose unacknowledged messages, must avoid resending acked messages, and must put idle connections into standby without starving future keepalives or sends.

Address parsing accepts IPv4, bracketed IPv6, optional ports, and optional DNS names. It sets addresses to `LEGACY` initially because msgr mode may be parsed later; callers adjust type later. DNS resolver availability changes behavior under `CONFIG_CEPH_LIB_USE_DNS_RESOLVER`.

## Test Signals

Important tests include connection open/close under concurrent socket callbacks, reconnect with out_sent requeue and acknowledgement discard, lossy connection fault closure, standby wakeup by send/keepalive, partial message send/receive revocation, incoming allocation races where connection closes while `alloc_msg` runs, data cursor traversal across pages/pagelists/bios/bvecs/iov_iters, CRC over highmem pages, DNS/IP parsing including malformed ports and bracketed IPv6, and module init/exit leak checks. Runtime lockdep, KASAN, refcount warnings, and fault-injection around socket I/O and memory allocation are strong signals for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/messenger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/messenger_v1.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/messenger_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/messenger_v2.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/messenger_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/mon_client.c -->
# Research: sources/distributed-fs/ceph-client/net/ceph/mon_client.c

## Purpose

`mon_client.c` implements the kernel Ceph monitor client. It maintains a session with one monitor, hunts for a replacement monitor on fault, authenticates the client, subscribes to cluster maps, handles map updates, provides synchronous/asynchronous monitor requests such as `statfs`, `mon_get_version`, monitor command, and blocklist add, and supplies monitor-specific connection operations to the generic messenger.

The monitor client is the bootstrap and control-plane path for libceph. It discovers and refreshes the monmap, receives OSD maps, manages authentication state, and wakes waiters that need map epochs or auth completion.

## Important APIs, Types, and Functions

Public monitor-client APIs:

- `ceph_monc_init()` and `ceph_monc_stop()` allocate/free monitor client state, auth state, preallocated messages, connection, delayed work, and monmap.
- `ceph_monc_open_session()` starts a monitor session and requests monmap and OSD map subscriptions.
- `ceph_monc_reopen_session()` forces hunting for a new monitor.
- `ceph_monc_want_map()`, `ceph_monc_got_map()`, and `ceph_monc_renew_subs()` manage map subscription intent and progress.
- `ceph_monc_wait_osdmap()` waits for an OSD map epoch.
- `ceph_monc_do_statfs()`, `ceph_monc_get_version()`, `ceph_monc_get_version_async()`, and `ceph_monc_blocklist_add()` issue generic monitor requests.
- `ceph_monc_validate_auth()` requests auth renewal when needed.

Monmap and session helpers:

- `ceph_monmap_decode()` decodes monitor maps, including v6 `mon_info_t` entries with address vectors.
- `build_initial_monmap()` builds a temporary monmap from mount options.
- `pick_new_mon()`, `__open_session()`, `__close_session()`, `reopen_session()`, `finish_hunting()`, and `delayed_work()` implement hunting, reconnect, backoff, keepalive, and subscription renewal.

Generic request helpers:

- `alloc_generic_request()`, `register_generic_request()`, `send_generic_request()`, `finish_generic_request()`, `wait_generic_request()`, and `get_generic_reply()` maintain an rb-tree of outstanding requests keyed by TID.
- Reply handlers include `handle_statfs_reply()`, `handle_get_version_reply()`, and `handle_command_ack()`.

Connection operations:

- `mon_alloc_msg()` preallocates or dynamically allocates incoming messages.
- `mon_dispatch()` routes monitor messages to auth, subscribe ack, statfs, version, command, monmap, OSD map, or extra dispatch handlers.
- `mon_fault()` hunts for a new monitor when the messenger reports a fault.
- msgr2 auth callbacks `mon_get_auth_request()`, `mon_handle_auth_reply_more()`, `mon_handle_auth_done()`, and `mon_handle_auth_bad_method()` bridge v2 frames to the Ceph auth subsystem.

## Control Flow

Initialization builds an initial monmap from configured monitor addresses, creates the auth client with desired key types, allocates reusable auth and subscription messages, initializes the embedded messenger connection with `mon_con_ops`, and sets initial hunting/backoff state.

Opening a session records interest in monmap and OSD map, calls `__open_session()`, and schedules delayed work. `__open_session()` randomly chooses a monitor, sets `hunting`, increases hunting backoff after previous connections, expires subscription renewal, opens the messenger connection, and queues a keepalive. For msgr1, it immediately builds and sends an auth hello message. For msgr2, auth is initiated through messenger v2 auth callbacks.

Authentication replies are handled either as normal `CEPH_MSG_AUTH_REPLY` messages in msgr1 or as msgr2 auth frames through callbacks. `finish_auth()` clears pending auth, records auth errors, sets the messenger entity name from the authenticated global id on first success, sends subscriptions, resends outstanding generic requests, and logs session establishment. `finish_hunting()` marks the monitor as found, reduces backoff, and reschedules delayed work.

Subscriptions are encoded by `__send_subscribe()` from `monc->subs[]`, always including monmap. Continuous subscriptions advance their start epoch after maps arrive; one-time subscriptions clear their want flag. Legacy monitor subscription acks determine `sub_renew_after` for periodic renewal if the peer lacks `CEPH_FEATURE_MON_STATEFUL_SUB`.

Generic requests allocate request and reply messages, register a TID in `generic_request_tree`, fill the request body, send it, and either wait for completion or return for async callback. Replies look up by TID, copy/decode results, remove the request from the tree, revoke request/reply messages from the connection, and complete the waiter or callback. On monitor reconnect, `__resend_generic_request()` revokes in-flight request/reply messages and resends all pending request messages.

Delayed work runs periodically. While hunting it reopens sessions. Otherwise it checks keepalive expiry, reopens on timeout, sends keepalive, validates auth, reduces hunting backoff, and renews subscriptions for old monitors when needed.

## State and Persistence Behavior

The monitor client keeps live state in `struct ceph_mon_client`: current monmap, current monitor index, hunting flags, hunt multiplier, subscription table, subscription renewal timestamps, auth state, reusable messages, generic request rb-tree, last TID, fs cluster id, embedded connection, and delayed work. There is no durable persistence; monmap and auth/session state are memory-only and rebuilt or reacquired after init/reconnect.

Generic requests are reference counted with `kref`. The rb-tree holds a reference while a request is active. Waiters or async users hold their own reference until completion. Request cancellation on interrupted waits removes the request if still active.

## Dependencies and Integration Points

This file is tightly integrated with the generic messenger, msgr1/msgr2 auth callbacks, Ceph auth subsystem, libceph options, OSD client map handling, debugfs state, and monitor protocol structs. It uses Linux delayed work, completions, wait queues, rbtrees, random monitor selection, and memory allocation helpers. `mon_dispatch()` passes `CEPH_MSG_OSD_MAP` directly to `ceph_osdc_handle_map()` and unknown extra messages to `client->extra_mon_dispatch`.

## Risks and Edge Cases

Monitor hunting and request resend must avoid losing control-plane requests during reconnect. `__close_session()` revokes reusable auth/subscription messages and resets auth; `__resend_generic_request()` handles outstanding generic requests after new auth. The monitor address in the initial monmap may have a bogus monitor entity number until a real monmap is decoded. `ceph_monmap_decode()` must handle modern and older monmap structures, skip unknown feature sections, and choose address type according to msgr mode. Subscription renewal has compatibility logic for monitors without stateful subscriptions.

Generic reply matching has a special workaround for old OSDs/monitors that omit `tid` in `MON_GET_VERSION_REPLY`, allocating a fresh message when tid is zero. Monitor command formatting uses a fixed 256-byte request message and `vsprintf()`, so command strings are expected to fit the preallocated buffer. `ceph_monc_blocklist_add()` retries the old `"blacklist"` command name if the modern `"blocklist"` command returns `-EINVAL`.

## Test Signals

Useful tests include initial monmap construction for msgr1 and msgr2 address types, monmap decode for v3/v6 maps and malformed buffers, random monitor repick avoiding the current monitor, msgr1 auth reply loop, msgr2 auth callbacks, auth failure wakeups, subscription encode/ack/renew behavior, OSD map wait timeout and interrupt, statfs/version/command request completion and cancellation, async version callback, monitor fault while hunting versus established, delayed keepalive timeout reopen, request resend after reconnect, blocklist fallback command, and teardown with pending work flushed and no rb-tree leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/mon_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/msgpool.c -->
# Research: sources/distributed-fs/ceph-client/net/ceph/msgpool.c

## Purpose

`msgpool.c` implements a small mempool wrapper for reusable `struct ceph_msg` objects. It lets Ceph subsystems preallocate a bounded pool of messages of a known type, front-buffer size, and maximum data item count, reducing allocation failure risk in reclaim-sensitive paths while still falling back to fresh allocation when a caller needs a larger message.

## Important APIs, Types, and Functions

Public APIs:

- `ceph_msgpool_init(struct ceph_msgpool *pool, int type, int front_len, int max_data_items, int size, const char *name)` initializes metadata and creates a kernel mempool backed by `msgpool_alloc()` / `msgpool_free()`.
- `ceph_msgpool_destroy(struct ceph_msgpool *pool)` destroys the mempool.
- `ceph_msgpool_get(struct ceph_msgpool *pool, int front_len, int max_data_items)` returns a message from the pool if the requested shape fits, or allocates a fresh message otherwise.
- `ceph_msgpool_put(struct ceph_msgpool *pool, struct ceph_msg *msg)` resets a pooled message and returns it to the mempool.

Private mempool callbacks:

- `msgpool_alloc()` creates messages using `ceph_msg_new2()` with the pool's configured type/front/data shape and marks `msg->pool = pool`.
- `msgpool_free()` clears `msg->pool` and drops the message reference with `ceph_msg_put()` when the mempool releases an element.

## Control Flow

Initialization stores the fixed message shape and creates a mempool of the requested size. Getting a message first checks whether the caller's requested front length or data item count exceeds the pool shape. If it does, the code rate-limited-warns, triggers `WARN_ON_ONCE()`, and attempts a non-pooled `ceph_msg_new2()` with the requested dimensions. Otherwise it calls `mempool_alloc()` with `GFP_NOFS`.

Returning a pooled message resets only the fields needed to restore its reusable shape: front iov length, header front length, total data length, data item count, and kref. It then calls `mempool_free()`. When the message's normal `ceph_msg_put()` path reaches zero references, `ceph_msg_release()` in `messenger.c` detects `m->pool` and calls back into `ceph_msgpool_put()` rather than freeing the object.

## State and Persistence Behavior

The pool stores fixed configuration (`type`, `front_len`, `max_data_items`, `name`) and the underlying `mempool_t`. Pooled message objects keep their allocated front buffer and data array across uses. There is no durable persistence.

## Dependencies and Integration Points

The file depends on Linux mempool APIs and the generic messenger allocation/refcounting APIs. It is included by `messenger.c` for pooled release, and Ceph clients such as the OSD client use `struct ceph_msgpool` to preallocate operation and reply messages. The reset behavior assumes `ceph_msg_release()` has already destroyed active data items and middle buffers before returning the object to the pool.

## Risks and Edge Cases

The main risk is returning a message with stale state. This file resets length/count fields and kref, while `ceph_msg_release()` handles connection detachment, middle buffers, and data item destruction before calling into the pool. If future fields are added to `struct ceph_msg`, the release/reset split must remain complete. Oversized requests intentionally bypass the pool, but a warning indicates that the configured pool shape may not match real use. Mempool destruction must happen only after all borrowed messages have been returned.

## Test Signals

Tests should cover pool init/destroy, get/put of correctly sized messages, fallback allocation for oversized front length or data item count, repeated reuse preserving type/front allocation while clearing data state, pooled release through `ceph_msg_put()`, and teardown under leak detection. Fault injection around `ceph_msg_new2()` and `mempool_create()` is useful to verify `-ENOMEM` paths and warning-only fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/msgpool.c -->
