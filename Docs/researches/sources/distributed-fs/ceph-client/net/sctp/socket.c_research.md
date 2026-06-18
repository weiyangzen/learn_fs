# Research: sources/distributed-fs/ceph-client/net/sctp/socket.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006277`: lines 1-9373, `Docs/researches/chunks/subset-b-006277_research.md`
- `subset-b-006278`: lines 9374-9729, `Docs/researches/chunks/subset-b-006278_research.md`

## Chunk Research

### subset-b-006277: lines 1-9373

# sources/distributed-fs/ceph-client/net/sctp/socket.c lines 1-9373

## Scope

This chunk covers almost all of `net/sctp/socket.c` in the Ceph client source snapshot, from the file header through the opening of `sctp_wait_for_connect()`. It includes the SCTP socket-layer entry points for bind, connect, send, receive, close, accept, listen, ioctl, setsockopt, getsockopt, association peeloff, port binding, endpoint traversal, socket initialization/destruction, and send/receive buffer wakeups.

The source path is under `sources/distributed-fs/ceph-client`, but this file is generic Linux SCTP networking code. It does not implement CephFS behavior directly.

Line 9373 is the opening brace of `sctp_wait_for_connect()`. The body of that wait helper, plus later accept/close wait helpers and IPv6-specific tail code, belongs to a later chunk.

## Purpose

This file is the SCTP protocol's bottom-half interface to the Linux socket layer. It translates socket operations and SCTP socket API options into endpoint, association, transport, and SCTP state-machine operations.

The implementation supports both one-to-many SCTP sockets (`SOCK_SEQPACKET`, named UDP-style in the code) and one-to-one SCTP sockets (`SOCK_STREAM`, named TCP-style). For one-to-many sockets, a single endpoint can own multiple associations and userspace often selects one with an association ID. For one-to-one sockets, the code usually ignores association IDs and operates on the single association attached to the socket.

Major responsibilities in this chunk are:

- Validate and bind local addresses, including `bindx()` multi-address add/remove and automatic wildcard binding.
- Create or look up associations for `connect()`, `connectx()`, and implicit `sendmsg()` connects.
- Parse SCTP ancillary send controls, build SCTP data messages, account send buffer ownership, and drive protocol primitives such as ASSOCIATE, SEND, SHUTDOWN, ABORT, and ASCONF.
- Receive queued `sctp_ulpevent` SKBs, copy data or notifications to userspace, emit ancillary receive info, and handle partial reads.
- Implement the large SCTP setsockopt/getsockopt ABI surface, including peer address parameters, delayed ACK, RTO, fragmentation, authentication, ASCONF, stream reset/reconfiguration, partial reliability, interleaving, schedulers, UDP encapsulation, PLPMTUD probe interval, and event subscription controls.
- Clone sockets for TCP-style `accept()` and one-to-many association peeloff.
- Initialize and destroy per-socket `struct sctp_sock` and endpoint state.
- Manage SCTP bind buckets, port reuse rules, listen state, polling readiness, and buffer wakeups.

## Important APIs, Types, And Functions

Socket and association lookup:

- `struct sctp_sock` is the SCTP extension area attached to `struct sock`; it stores socket style, endpoint pointer, protocol-family callbacks, default send/receive parameters, feature flags, address auto-ASCONF state, partial-delivery settings, and per-socket tunables inherited by future associations.
- `struct sctp_endpoint` owns local bind address state and the association list for the socket.
- `struct sctp_association` is the live protocol association; this file looks it up, configures it, migrates it, sends primitives to it, and exposes its stats and peer/transport properties.
- `struct sctp_transport` represents one peer path/address and is used for per-path configuration, primary address selection, heartbeat, PMTU, failure thresholds, UDP encapsulation, and PLPMTUD settings.
- `sctp_id2assoc()` maps a userspace association ID to an association. For non-UDP-style sockets it returns the only established/closing association and ignores the ID. For UDP-style sockets it uses the global association IDR under `sctp_assocs_id_lock` and rejects associations on another socket or dead associations.
- `sctp_addr_id2transport()` validates a sockaddr, finds the association by peer address, cross-checks the optional association ID, converts the address back to userspace family form, and returns the selected transport.

Binding and dynamic address reconfiguration:

- `sctp_bind()` locks the socket and allows a single initial bind through `sctp_do_bind()`.
- `sctp_sockaddr_af()` verifies sockaddr family support and length, including IPv6 minimum size and v4-mapped IPv6 handling.
- `sctp_do_bind()` performs protocol-family bind verification, port consistency checks, privileged-port permission checks, duplicate local bind detection, port allocation through `sctp_get_port_local()`, address-list insertion, and socket address updates for `getsockname()`.
- `sctp_bindx_add()` and `sctp_bindx_rem()` walk packed sockaddr arrays, adding or removing bind addresses transactionally by rolling back earlier entries if a later one fails.
- `sctp_send_asconf()`, `sctp_send_asconf_add_ip()`, and `sctp_send_asconf_del_ip()` generate ADD-IP ASCONF chunks for established ASCONF-capable associations, queue them behind an outstanding ASCONF when necessary, and update association local address state and transport routes.
- `sctp_asconf_mgmt()` is used by address-management code to send automatic add/delete ASCONF notifications for endpoint address changes.
- `sctp_setsockopt_bindx()` validates the packed address buffer, applies LSM checks for add, and dispatches bindx add/remove plus optional ASCONF signaling.

Connect and send path:

- `sctp_connect_new_asoc()` creates a new association, autobinds if needed, copies endpoint bind addresses into the association, adds the first peer transport, and applies optional INIT parameters.
- `sctp_connect_add_peer()` validates and adds additional peer addresses for multihomed connect/connectx.
- `__sctp_connect()` implements common connect/connectx behavior: reject already-connected states, validate the first address, create an association, append packed peer addresses with matching ports, optionally assign an association ID, invoke `sctp_primitive_ASSOCIATE()`, update socket peer address fields, and wait for connect completion.
- `__sctp_setsockopt_connectx()`, `sctp_setsockopt_connectx_old()`, `sctp_setsockopt_connectx()`, and `sctp_getsockopt_connectx3()` expose the older and newer connectx ABIs, including returning the association ID to userspace.
- `sctp_msghdr_parse()` parses `IPPROTO_SCTP` control messages for `SCTP_INIT`, `SCTP_SNDRCV`, `SCTP_SNDINFO`, `SCTP_PRINFO`, `SCTP_AUTHINFO`, and destination-address lists, with strict control-message length and flag validation.
- `sctp_sendmsg_parse()` combines send control information into `struct sctp_sndrcvinfo` and enforces send flag rules such as no TCP-style EOF/ABORT, no zero-length plain data send, no EOF with payload, and `SCTP_ADDR_OVER` requiring a destination name.
- `sctp_sendmsg_new_asoc()` supports implicit association creation from `sendmsg()` when a destination address is supplied and no existing association matches.
- `sctp_sendmsg_check_sflags()` handles `SCTP_SENDALL`, graceful EOF shutdown, and user ABORT sends before normal data transmission.
- `sctp_sendmsg_to_asoc()` validates stream IDs, initializes per-stream extension state, enforces fragmentation limits, handles PMTU updates, waits for send buffer space, starts closed associations, builds `struct sctp_datamsg` objects from user data, sets per-chunk ownership/destructor accounting, and invokes `sctp_primitive_SEND()`.
- `sctp_sendmsg()` is the main socket send method. It parses controls, resolves destination or association ID, handles `SCTP_SENDALL`, creates associations when needed, applies default send info, and returns SCTP-specific errors through `sctp_error()`.

Receive path:

- `sctp_recvmsg()` handles MSG_ERRQUEUE, optional busy-polling, TCP-style connection-state checks, blocking/nonblocking receive via `sctp_skb_recv_datagram()`, data copy, notification/message source address reporting, optional `SCTP_NXTINFO`, `SCTP_RCVINFO`, and deprecated `SCTP_SNDRCVINFO` ancillary output, partial-read requeue, receive-window increment, and SKB/event release.
- `sctp_skb_pull()` removes bytes across an SKB and its frag list so partially copied messages can be put back at the receive queue head.
- `sctp_wait_for_packet()` and `sctp_skb_recv_datagram()` are SCTP-specific datagram wait/dequeue helpers. They honor socket errors, shutdown, association/listen state, signals, nonblocking timeout, and release/reacquire the socket lock while sleeping.
- `sctp_sock_rfree()` provides receive-memory accounting for cloned data SKBs using the owning `sctp_ulpevent`'s recorded receive memory length.
- `sctp_data_ready()` wakes waiters and async readers when data is queued.

Socket options and user ABI:

- `sctp_setsockopt()` and `sctp_getsockopt()` are large SOL_SCTP dispatchers. Non-SOL_SCTP options are delegated to the address-family-specific implementation.
- Setters validate user buffer sizes after copying through `memdup_sockptr()`, run under `lock_sock()`, and usually apply changes to a selected association, current associations, future association defaults, or all associations depending on the association ID selector.
- Getters read `optlen`, hold the socket lock, copy selector structs from userspace when needed, fill endpoint/association/transport values, update returned lengths, and copy results back.
- Important setter families include `sctp_setsockopt_peer_addr_params()`, delayed ACK, INITMSG, default send parameters, primary address, RTO, association retransmission/cookie parameters, mapped-v4 behavior, max segment size, peer primary ASCONF, receive context, fragment interleave, partial delivery point, max burst, AUTH chunk/HMAC/key operations, auto-ASCONF, peer address thresholds, receive-info toggles, PR-SCTP defaults, reconfiguration and stream reset, stream scheduler and per-stream values, interleaving support, SCTP reuse-port, event subscription, ASCONF/AUTH/ECN support toggles, PF exposure, UDP encapsulation port, and PLPMTUD probe interval.
- Important getter families include status, peer address info, local/peer address enumeration, peeloff/peeloff-flags, peer address parameters, delayed ACK, INITMSG, default send params, primary address, RTO/assoc info, context, maxseg, maxburst, HMAC/auth chunk/key state, association count and ID list, path thresholds, association stats, receive-info toggles, PR-SCTP status, reconfiguration/stream reset, scheduler, interleaving, reuse-port, event subscription, feature toggles, PF exposure, UDP encapsulation, and PLPMTUD probe interval.
- `sctp_bpf_bypass_getsockopt()` identifies getsockopts that should bypass BPF interception because they create fds or perform connectx side effects.

Socket lifecycle, listen, accept, peeloff, and exported traversal:

- `sctp_close()` performs graceful shutdown or ABORT for all associations on a socket, based on unread data, reassembly/lobby queues, and SO_LINGER; it waits for TCP-style close when requested and then releases the socket while respecting the net SCTP address workqueue lock ordering.
- `sctp_clone_sock()` clones the Linux socket state, resets multicast and IPv6 list pointers, creates a new SCTP endpoint, migrates the association with `sctp_sock_migrate()`, and applies SCTP security clone hooks.
- `sctp_accept()` waits for a queued association on a TCP-style listening socket, then clones a new socket to own that association.
- `sctp_do_peeloff()`, `sctp_getsockopt_peeloff_common()`, `sctp_getsockopt_peeloff()`, and `sctp_getsockopt_peeloff_flags()` branch a one-to-many association into a new socket and return an fd to userspace.
- `sctp_init_sock()` initializes SCTP defaults from per-net sysctls, chooses UDP-style or TCP-style based on socket type, allocates the endpoint, initializes queues and feature flags, installs the destructor, and updates socket/object accounting.
- `sctp_destroy_sock()` removes the socket from auto-ASCONF lists if needed, frees the endpoint, and drops accounting references.
- `sctp_shutdown()` initiates SCTP shutdown for TCP-style SEND_SHUTDOWN.
- `sctp_get_sctp_info()` exports compact socket or association info for diagnostics.
- `sctp_transport_walk_start()`, `sctp_transport_walk_stop()`, `sctp_transport_get_next()`, `sctp_transport_get_idx()`, `sctp_for_each_endpoint()`, `sctp_transport_lookup_process()`, and `sctp_transport_traverse_process()` expose controlled endpoint/transport iteration for other SCTP consumers.

Port binding, listen, poll, and buffer accounting:

- `sctp_get_port_local()` is the SCTP port bind allocator and conflict checker. It searches ephemeral ranges, respects reserved ports, uses per-net SCTP bind hash buckets, enforces address conflicts against existing endpoint bind lists, and maintains `fastreuse`/`fastreuseport` state.
- `sctp_get_port()` wraps `sctp_get_port_local()` using an address synthesized from the socket.
- `sctp_listen_start()` autobinds if necessary, moves the socket to LISTENING, sets backlog, and hashes the endpoint.
- `sctp_inet_listen()` validates listen state, forbids peeled-off sockets from listening, supports backlog zero as disabling listen, updates existing backlog, or starts listening.
- `sctp_poll()` reports readable accept queues for TCP-style listeners, error/shutdown/hangup readiness, receive-queue readability, and writability based on `sctp_writeable()`.
- `sctp_set_owner_w()` and `sctp_wfree()` hold the association and optional auth key for outbound chunks, charge socket/association memory, and release those references when the SKB is freed.
- `__sctp_write_space()`, `sctp_wake_up_waiters()`, `sctp_write_space()`, and `sctp_writeable()` wake association and socket waiters when send buffer space becomes available. The code supports both per-association and per-socket send-buffer accounting policies.
- `sctp_wait_for_sndbuf()` waits on an association-specific waitqueue for enough send-buffer space while holding association/transport references and handling dead associations, dead transports, socket errors, shutdown, signals, timeout, and possible association migration.

## Control Flow

Bind flow starts at `sctp_bind()` or bindx. A single address goes through `sctp_do_bind()`, which verifies the sockaddr and protocol-family policy, normalizes the port, checks privileged-port capability, rejects duplicate local binds, allocates or reuses a port bucket through `sctp_get_port_local()`, and appends the address to the endpoint bind list. Bindx first validates the packed sockaddr list, then performs each operation in sequence and rolls back already-applied entries if one fails. When ASCONF is enabled, bindx add/remove also sends ADD-IP or DEL-IP ASCONF chunks to each established peer that supports the relevant parameter.

Connect flow uses the first destination address to create a new association and first peer transport. Additional connectx addresses are parsed from the same packed buffer and added as peer transports only if their port matches the first address. The association is assigned an ID if the ABI requires one, then `sctp_primitive_ASSOCIATE()` starts protocol negotiation. The call stores peer port/address fields for `getpeername()` and waits for connect completion through a helper whose implementation begins after this chunk.

Send flow starts by parsing SCTP control messages into send info and flags. For one-to-many `SCTP_SENDALL`, the code iterates the endpoint association list, validates control flags for each association, sends to each one, then rewinds the iov iterator after each successful send so every association receives the same payload. For normal sends, a destination address selects or creates an association; without a destination, the association ID selects the target. Data sends validate stream and fragmentation constraints, prune PR-SCTP data if possible, wait for sndbuf space, optionally start a closed association, build a datamsg from the user iterator, attach memory-accounted chunk ownership, and pass the datamsg to the SCTP state machine.

Receive flow dequeues an `sctp_ulpevent` SKB from `sk_receive_queue`, blocking in `sctp_wait_for_packet()` unless MSG_DONTWAIT or timeout forbids it. The caller copies up to the requested byte count. If userspace's buffer is smaller than the SCTP message, the SKB is pulled by the copied length, returned to the queue head, MSG_EOR is cleared, and receive-window space is increased only for the bytes consumed. Complete messages and notifications free their event unless the caller used MSG_PEEK.

Close/shutdown flow distinguishes user-visible socket close from protocol shutdown. `sctp_close()` marks the socket closing, purges unread receive data, then walks all endpoint associations. Unread data, incomplete reassembly/lobby data, or zero linger force ABORT; otherwise SHUTDOWN is sent. TCP-style sockets may wait up to linger time before the socket is released. `sctp_shutdown()` is narrower and only initiates SEND_SHUTDOWN for TCP-style sockets.

Setsockopt/getsockopt flow is serialized by the socket lock. Most options share the same selector pattern: look up an association by ID, reject invalid UDP-style IDs, apply to the association when present, otherwise update future defaults or every current association for `SCTP_FUTURE_ASSOC`, `SCTP_CURRENT_ASSOC`, and `SCTP_ALL_ASSOC`. Per-address options first resolve a transport with `sctp_addr_id2transport()` and then apply path-specific state. Feature options such as ASCONF, AUTH, ECN, PR-SCTP, reconfiguration, and interleaving toggle endpoint capability flags that influence subsequent association negotiation.

Peeloff and accept both clone socket state and migrate an association. Accept is TCP-style only and takes the first association from the listener endpoint's association list as the accept queue. Peeloff is one-to-many only, creates a lite socket/fd, migrates the selected association to UDP-high-bandwidth style, and installs the new file descriptor only after successful userspace result copying.

Port/listen flow uses `sctp_get_port_local()` to allocate an ephemeral or requested port. For requested ports, all existing sockets in the same bind bucket are checked for address conflicts unless reuse or reuseport rules allow sharing. Listen autobinds wildcard if the endpoint has no port, hashes the endpoint, and treats backlog zero as unhashing and returning to closed state.

Buffer wakeup flow is tied to outbound chunk SKB destructors. `sctp_set_owner_w()` charges the association and socket when chunks are queued; `sctp_wfree()` uncharges memory, releases auth keys and association references, may generate AUTH_FREE_KEY events, then wakes the right waiters. With per-association sndbuf accounting only that association is woken. With per-socket accounting the wakeup loop rotates through the endpoint association list to avoid always waking the same association first.

## State And Persistence Behavior

All state in this chunk is in-memory kernel networking state. There is no filesystem persistence.

Important state includes:

- Per-socket SCTP defaults in `struct sctp_sock`: default stream, PPID, flags, context, TTL/PR policy, RTO and association parameters, heartbeat/PMTU/SACK parameters, max burst, max segment, receive info toggles, feature support flags, event subscriptions, scheduler default, UDP encapsulation and probe interval defaults, and partial delivery settings.
- Per-endpoint state: bind address list, local port, association list, auto-ASCONF linkage, authentication material, negotiated feature defaults, and listen hash membership.
- Per-association state: SCTP protocol state, stream counts and stream scheduler, default send/receive context, bind address list, peer transports, primary path, retransmission/cookie/RTO parameters, PR-SCTP counters, stats, capability flags, ASCONF queues, pending address deletion, send-buffer usage, and waitqueues.
- Per-transport state: peer address, congestion state, heartbeat interval, SACK delay/frequency, path MTU, PMTU discovery flags, path failure thresholds, RTO/RTT estimates, DSCP/flowlabel, UDP encapsulation port, PLPMTUD probe interval, and route/source-address cache.
- Global/per-net state used here: SCTP bind hash buckets, transport rhashtable, endpoint hash buckets, per-net local address list, per-net SCTP sysctl defaults, and auto-ASCONF socket list.
- Socket queues and counters: `sk_receive_queue`, `sk_error_queue`, `sk_wmem_queued`, `sk_wmem_alloc`, `sk_rmem_alloc`, association `sndbuf_used`, per-association ULP queues (`lobby`, `reasm`, `reasm_uo`), and per-association wait queues.

Reference counting is central. Outbound chunks hold their association and optional shared auth key until the SKB destructor runs. Transport traversal holds transports and endpoints while callbacks execute. Peeloff and socket clone paths carefully allocate a new endpoint, migrate the association, and repair socket accounting after `sk_clone()`'s generic reference/accounting behavior.

RCU appears in transport table walking, local address enumeration, and socket wakeup waitqueue dereferencing. Socket lock serialization protects most endpoint association lists and option state. Port bind buckets use spinlocks with bottom halves disabled.

## Dependencies And Integration Points

This file depends on Linux socket core APIs (`struct sock`, `struct socket`, poll, wait queues, SKBs, socket memory accounting, `sk_common_release()`, `sk_clone()`, and fd/file allocation), inet/IPv6 helpers, RPS, busy polling, and the security hooks for SCTP bind/connect/clone.

It integrates with SCTP core through:

- State-machine primitives such as `sctp_primitive_ASSOCIATE()`, `sctp_primitive_SEND()`, `sctp_primitive_SHUTDOWN()`, `sctp_primitive_ABORT()`, `sctp_primitive_ASCONF()`, and `sctp_primitive_REQUESTHEARTBEAT()`.
- Association, endpoint, bind-address, transport, stream, auth, ASCONF, stream reset, scheduler, partial reliability, and ULP event helpers defined elsewhere under `net/sctp`.
- Address-family callback tables (`struct sctp_pf`, `struct sctp_af`) for address validation, conversion, binding, socket address storage, IPv4/IPv6 option delegation, and family-specific copy behavior.
- Per-net SCTP configuration such as retransmission defaults, heartbeat interval, cookie lifetime, max burst, address lists, UDP encapsulation defaults, PMTU probing defaults, and feature enablement.

It integrates with userspace through the SCTP sockets API and the Linux SOL_SCTP option namespace. It also has compatibility handling for older connectx and delayed-ack/maxseg/maxburst ABI shapes and explicit BPF bypass decisions for getsockopts with fd-creating or side-effecting behavior.

It integrates with diagnostics and external SCTP users through exported helpers: `sctp_get_sctp_info()`, endpoint/transport traversal helpers, and lookup/process helpers. These avoid exposing core internals directly while allowing proc/debug or other modules to inspect SCTP state safely.

## Risks And Edge Cases

Packed sockaddr parsing is a recurring attack surface. Bindx and connectx walk user-provided packed address arrays by family-specific lengths. Every step must validate that `sa_family_t` and the full sockaddr fit in the copied buffer, or later pointer arithmetic can read beyond the user-provided data.

Association ID selectors are subtle. TCP-style sockets ignore IDs, while UDP-style sockets must reject invalid positive IDs. Future/current/all association selectors have different meanings across options. A new option that gets this wrong can silently update defaults instead of a live association, or expose the wrong association's state.

Address and port binding must preserve SCTP multihoming semantics. `sctp_get_port_local()` combines port reuse flags, UID checks for reuseport, bound device checks, wildcard-vs-specific address conflict detection, and namespace-specific bind buckets. Small changes can create duplicate binds, false `EADDRINUSE`, or cross-netns leakage.

ASCONF address deletion has special last-address handling. When deleting the only remaining association address, the code may stash the address in `asconf_addr_del_pending` and mark `src_out_of_asoc_ok`; route/source recalculation follows. This is a delicate area for source-address selection and peer-visible address state.

`SCTP_SENDALL` rewinds the user iov iterator after each association send. If a send path returns a byte count that does not match the consumed iterator state, later associations can see corrupt or truncated data.

Send buffer accounting is split between socket and association policies. `sctp_set_owner_w()` and `sctp_wfree()` must stay paired exactly; missing destructor ownership, double orphaning, or incorrect truesize accounting would cause stuck writers, memory leaks, or negative accounting warnings.

Wait paths intentionally drop and reacquire the socket lock. `sctp_wait_for_sndbuf()` revalidates association/socket relationships after sleeping; callers that hold raw association pointers across sleep points need equivalent care because associations can be peeled off or freed.

Peeloff and accept migrate associations between sockets. The code must move queued transmit and receive data, endpoint ownership, security state, socket accounting, and address state consistently. A partial clone or migration failure can leak endpoints or leave association queues attached to the wrong socket.

Getsockopt functions that create fds or initiate connects have side effects unlike ordinary getters. This is why `sctp_bpf_bypass_getsockopt()` special-cases peeloff and connectx3. Instrumentation or filtering layers need to preserve these semantics.

Authentication key handling contains sensitive material. `sctp_setsockopt_auth_key()` validates variable key length and calls `memzero_explicit()` before returning. Any alternate path handling copied key material must preserve explicit zeroing.

Several options support deprecated ABI layouts. Compatibility paths for integer maxseg/maxburst and `struct sctp_assoc_value` delayed ACK are retained with warnings. Removing or changing these would break older userspace.

The chunk boundary is itself a research risk: calls to `sctp_wait_for_connect()`, `sctp_wait_for_accept()`, and `sctp_wait_for_close()` appear in this chunk, but their full implementations are after line 9373 and should be analyzed in the subsequent chunk.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build coverage with IPv4, IPv6, SCTP auth, ASCONF, stream reset/reconfiguration, PR-SCTP, interleaving, UDP encapsulation, BPF getsockopt interception, and namespace support enabled.
- Bind tests for duplicate bind rejection, wildcard/specific-address conflicts, privileged ports, ephemeral range exhaustion, reserved local ports, SO_REUSEADDR, SCTP_REUSE_PORT, SO_REUSEPORT UID behavior, bound device conflicts, IPv6 v4-mapped handling, and bindx rollback after partial failure.
- Connect/connectx tests for invalid packed buffers, mixed address families, mismatched peer ports, peeled-off address rejection, duplicate association detection (`EISCONN`/`EALREADY`), autobind failure, association ID return, nonblocking `EINPROGRESS`, and connectx3 userspace copyout.
- Sendmsg tests for all supported CMSGs, strict cmsg length validation, invalid flag combinations, implicit association creation, `SCTP_ADDR_OVER`, `SCTP_SENDALL` iterator rewind, EOF and ABORT behavior, stream ID bounds, fragmentation disabled/maxseg limits, PMTU pending sync, PR-SCTP pruning, and AUTH key send events.
- Receive tests for blocking and nonblocking dequeue, MSG_PEEK refcount behavior, MSG_ERRQUEUE delegation, notification vs data flags, receive ancillary info toggles, partial read requeue and receive-window growth, TCP-style not-connected errors, shutdown behavior, and busy-poll path coverage.
- Setsockopt tests for every association selector mode: future, current, all, explicit valid association, explicit invalid association on UDP-style sockets, and ignored IDs on TCP-style sockets.
- Peer address option tests for heartbeat demand, heartbeat enable/disable, PMTUD enable/disable and fixed MTU bounds, SACK delay/frequency bounds, DSCP/IPv6 flowlabel propagation, PF/PS thresholds, encapsulation port, and PLPMTUD probe interval reset behavior.
- AUTH tests for feature enablement, HMAC list bounds, invalid authenticated chunk IDs, variable key length validation, active/delete/deactivate key errors, per-association vs endpoint updates, and explicit key buffer zeroing.
- ASCONF tests for bindx add/remove signaling, outstanding ASCONF queueing, peer capability masks, last local address deletion, route/source-address recomputation, peer primary address validation, and auto-ASCONF list membership under address workqueue locking.
- Getters for status, info, local/peer addresses, auth chunks, association IDs, and stats should be tested with too-small buffers, exact buffers, oversized buffers, invalid userspace pointers, and partially populated backward-compatible structs.
- Peeloff and accept tests for fd allocation errors, copyout failures, SOCK_CLOEXEC/SOCK_NONBLOCK flags, netns mismatch rejection, TCP-style accept queue behavior, UDP high-bandwidth listen rejection, association migration, and no leaked socket accounting on clone failure.
- Listen/poll tests for autobind listen, listen backlog update, backlog zero unhash, poll readability for TCP-style listeners, receive/error/shutdown/hup readiness, and writable readiness race handling.
- Memory and wakeup tests for sndbuf exhaustion, per-association vs per-socket sndbuf policy, waiter fairness across associations, destructor uncharge, shared-key AUTH_FREE_KEY notification generation, and wakeups after association death.

### subset-b-006278: lines 9374-9729

# sources/distributed-fs/ceph-client/net/sctp/socket.c lines 9374-9729

## Scope

This chunk covers the final SCTP socket helpers and protocol operation tables in `sources/distributed-fs/ceph-client/net/sctp/socket.c`. The requested line range begins inside `sctp_wait_for_connect()` and runs through the end of the IPv6 SCTP `struct proto` definition. For complete control-flow context, the enclosing function signatures and nearby callers were also inspected.

The source tree path is under a Ceph client snapshot, but this code is generic Linux SCTP networking socket infrastructure. It does not implement CephFS behavior directly.

## Purpose

This code closes out the SCTP socket implementation by providing the wait/migration primitives that connect user-facing socket operations to SCTP association lifetime, then registering the SCTP protocol callbacks with the kernel socket layer.

The wait helpers translate SCTP association state transitions into standard socket blocking behavior:

- `sctp_wait_for_connect()` waits for an active association setup to reach `ESTABLISHED`, fail, be interrupted, or remain in progress for nonblocking callers.
- `sctp_wait_for_accept()` waits for a TCP-style SCTP listening endpoint to have an association available on the endpoint association list, which is treated as the accept queue.
- `sctp_wait_for_close()` implements TCP-style close linger waiting until all endpoint associations are gone or the timeout/signal condition ends the wait.

The migration helpers support SCTP's two ways to split an association onto a new socket: TCP-style `accept()` and UDP-style peeloff. `sctp_sock_migrate()` is the main handoff routine. It attaches the cloned socket to the same port binding, duplicates bind addresses, moves queued receive data for the selected association, preserves partial-delivery state, retargets queued receive and transmit skb ownership, moves the association's `base.sk`, and marks the new socket as established or closed.

The `sctp_prot` and `sctpv6_prot` tables are the integration boundary with the generic socket/proto layer. They bind SCTP-specific implementations for close, connect/disconnect, accept, bind, send, receive, getsockopt, setsockopt, backlog processing, hashing, memory accounting, and sysctl memory limits. The IPv6 table mirrors the IPv4/dual-stack table but uses `struct sctp6_sock`, exposes `ipv6_pinfo_offset`, and wraps initialization so IPv6 sockets use `inet6_sock_destruct()`.

## Important APIs, Types, And Functions

- `sctp_wait_for_connect(struct sctp_association *asoc, long *timeo_p)`: waits on `asoc->wait` while holding a temporary association reference. It releases the socket lock before sleeping with `schedule_timeout()` and reacquires it after waking. It returns `0` for success/acceptable exit, `-EINPROGRESS` for immediate nonblocking progress, `sock_intr_errno()` for interrupted waits, `-ECONNREFUSED` for setup failure before exhausting init attempts, and `-ETIMEDOUT` once init attempts are exhausted.
- `sctp_wait_for_accept(struct sock *sk, long timeo)`: waits on `sk_sleep(sk)` until `sctp_sk(sk)->ep->asocs` is non-empty. It validates the socket is still SCTP listening and not receive-shutdown, then returns `0`, `-EINVAL`, `-EAGAIN`, or an interrupt error.
- `sctp_wait_for_close(struct sock *sk, long timeout)`: waits on `sk_sleep(sk)` until the endpoint association list becomes empty, a signal arrives, or the timeout expires. It intentionally returns no status; close already proceeds with later socket release cleanup.
- `sctp_skb_set_owner_r_frag(struct sk_buff *skb, struct sock *sk)`: recursively walks skb fragments with `skb_walk_frags()` and applies `sctp_skb_set_owner_r()` to every skb fragment and the parent skb. This is used when receive-side ownership is moved from an old socket to a newly accepted or peeled-off socket.
- `sctp_sock_migrate(struct sock *oldsk, struct sock *newsk, struct sctp_association *assoc, enum sctp_socket_type type)`: populates the cloned SCTP socket state and migrates one association plus its queued data to the clone. It is called from `sctp_clone_sock()`, which is used by both `sctp_accept()` and UDP-style peeloff.
- `sctp_prot`: the SCTP `struct proto` for non-IPv6 object layout, using `struct sctp_sock` as `obj_size` and exposing the userspace-copy region from `subscribe` through `initmsg`.
- `sctp_v6_destruct_sock(struct sock *sk)`: IPv6-specific destructor wrapper that calls `inet6_sock_destruct()`.
- `sctp_v6_init_sock(struct sock *sk)`: calls the common `sctp_init_sock()` and, on success, installs the IPv6 destructor.
- `sctpv6_prot`: the IPv6 SCTP `struct proto`, compiled only when `CONFIG_IPV6` is enabled. It uses `struct sctp6_sock`, sets `ipv6_pinfo_offset`, and uses the same SCTP operation callbacks as IPv4 except for initialization and object layout.

Important data structures and fields:

- `struct sctp_association`: provides `base.sk`, `state`, `base.dead`, `wait`, `init_err_counter`, `max_init_attempts`, `ulpq`, `peer`, and association queues used by wait and migration paths.
- `struct sctp_sock`: SCTP per-socket extension reached via `sctp_sk(sk)`, including `ep`, `type`, `bind_hash`, `pd_lobby`, `pd_mode`, `subscribe`, and `initmsg`.
- `struct sctp_endpoint`: owns `asocs`, the endpoint association list. In TCP-style listen sockets this list is used as the accept queue.
- `struct sk_buff` and `struct sctp_ulpevent`: receive messages in `sk_receive_queue` and `pd_lobby` are associated with an SCTP association through `sctp_skb2event(skb)->asoc`.
- `struct sctp_bind_bucket` and `struct sctp_bind_hashbucket`: the migration path attaches `newsk` to the same SCTP port bind bucket as `oldsk` under the bind hash bucket spinlock.
- `struct proto`: the kernel protocol-operation table consumed by inet registration code in `net/sctp/protocol.c` and `net/sctp/ipv6.c`.

## Control Flow

### Connect Wait

`sctp_wait_for_connect()` is entered after active association setup has been started, such as through the `__sctp_connect()` path. The caller passes the remaining send timeout by pointer. The helper first takes an association reference with `sctp_association_hold()` so that the association cannot disappear while the task sleeps.

The loop registers the current task on `asoc->wait` as an exclusive interruptible waiter. It then checks immediate exit conditions in priority order. A zero timeout produces `-EINPROGRESS`, which is the expected nonblocking-connect result. Receive shutdown exits the wait with the current `err` value. Socket errors, association shutdown-pending-or-later state, or a dead association enter the error mapping path. Pending signals return `sock_intr_errno(*timeo_p)`. If the association is already `ESTABLISHED`, the loop succeeds.

When the association is not yet established, the helper releases the socket lock, sleeps with `schedule_timeout(current_timeo)`, reacquires the socket lock, and writes the remaining timeout back through `timeo_p`. On all exits it removes the wait entry with `finish_wait()` and drops the temporary association reference.

The state-machine side wakes this queue when an association reaches `ESTABLISHED`, `CLOSED`, or `SHUTDOWN_RECEIVED`, so connect waiters see both successful and failed setup transitions.

### Accept Wait

`sctp_wait_for_accept()` is used by `sctp_accept()` after the caller has already verified TCP-style listening state and computed the receive timeout. It uses the endpoint association list as the readiness condition. If `ep->asocs` is empty, it releases the socket lock, calls `schedule_timeout(timeo)`, and reacquires the lock.

After each sleep opportunity, it revalidates that the socket is still listening and not receive-shutdown. This matters because another thread can close or disconnect the listening socket while the accept path sleeps. If an association is now present, it returns success. Otherwise, a pending signal returns `sock_intr_errno(timeo)`, and an exhausted timeout returns `-EAGAIN`.

On success, the caller takes the first association from `sctp_sk(sk)->ep->asocs` and calls `sctp_clone_sock(sk, asoc, SCTP_SOCKET_TCP)`. The clone path creates a new endpoint and then delegates the actual association and skb migration to `sctp_sock_migrate()`.

### Close Wait

`sctp_wait_for_close()` is called during `sctp_close()` for TCP-style sockets with a linger timeout. It waits on the socket sleep queue while the endpoint association list is non-empty. The loop releases the socket lock around `schedule_timeout(timeout)` so state-machine and receive/backlog work can progress. It stops when all associations are gone, a signal is pending, or the timeout reaches zero. The helper does not report a result because close cleanup continues regardless.

### Receive skb Ownership Migration

`sctp_skb_set_owner_r_frag()` handles receive-side socket accounting for both ordinary skbs and fragmented skbs. If an skb has `data_len`, each fragment is visited recursively and retargeted before the parent skb is retargeted. This prevents receive-memory accounting and destructor behavior from remaining tied to `oldsk` after queued data has moved to `newsk`.

### Association Migration

`sctp_sock_migrate()` assumes `newsk` was cloned from `oldsk` and already has a freshly allocated SCTP endpoint. Because cloning copied the old `struct sctp_sock`, the first step restores `newsp->ep` to that new endpoint.

The new socket is then attached to the same SCTP bind bucket as the old socket. The code computes the bind hash bucket from the old socket net namespace and local port, takes `head->lock`, adds `newsk` to `pp->owner`, records `newsk`'s `bind_hash`, copies `inet_num`, and unlocks. This keeps the accepted or peeled-off socket bound to the same local SCTP port.

Next, the new endpoint receives a duplicate of the original endpoint bind address list through `sctp_bind_addr_dup()`. This is required for restart handling and local address awareness. Failure returns immediately before association migration. On success, `sctp_auto_asconf_init(newsp)` initializes automatic address-configuration state for the new SCTP socket.

Queued receive events are then split by association. The old socket receive queue is scanned with `sctp_skb_for_each()`. Any skb whose `sctp_ulpevent` points at the migrating association is unlinked from `oldsk->sk_receive_queue`, appended to `newsk->sk_receive_queue`, and has its receive owner changed recursively.

Partial delivery receives special handling. The new socket's `pd_mode` is set from `assoc->ulpq.pd_mode`. If the old socket is in partial-delivery mode, skbs in `oldsp->pd_lobby` for the migrating association are moved either to `newsp->pd_lobby` when this association itself remains in partial delivery, or to `newsk->sk_receive_queue` when the migrating association is not the partial-delivery association. In the former case, `sctp_clear_pd(oldsk, NULL)` clears the old socket partial-delivery state for skbs waiting behind the migration.

The helper also retargets receive skbs still held inside the association ULP queues (`ulpq.lobby`, `ulpq.reasm`, and `ulpq.reasm_uo`) via `sctp_for_each_rx_skb()`.

After data queues are handled, `newsp->type` is set to the requested socket type: TCP style for `accept()` or high-bandwidth UDP style for peeloff. The new socket is then locked with `lock_sock_nested(newsk, SINGLE_DEPTH_NESTING)` before the association object is moved. This deliberately marks the new socket in use so packets racing with the migration are queued to the backlog rather than processed concurrently.

Transmit data chunks need socket ownership retargeting too. Before moving the association, `sctp_for_each_tx_datachunk(assoc, true, sctp_clear_owner_w)` clears ownership on chunks that still point to the old association socket. `sctp_assoc_migrate(assoc, newsk)` updates the association's socket binding. A second pass, `sctp_for_each_tx_datachunk(assoc, false, sctp_set_owner_w)`, assigns write ownership for chunks that now need to point to the new socket. This covers transmitted, retransmit, sacked, abandoned, and unsent output-queue chunks through the helper defined earlier in the file.

Finally, socket state is published. A closed association accepted from a TCP-style listening socket sets `SCTP_SS_CLOSED` and `RCV_SHUTDOWN`; otherwise the new socket is marked `SCTP_SS_ESTABLISHED`. The new socket lock is released and migration succeeds.

### Protocol Table Registration

The `sctp_prot` table is a static operation vector consumed when SCTP is registered with the inet protocol layer. It wires common socket operations to SCTP implementations:

- Lifetime and connection: `sctp_close`, `sctp_disconnect`, `sctp_accept`, `sctp_init_sock`, `sctp_destroy_sock`, `sctp_shutdown`.
- Userspace APIs: `sctp_ioctl`, `sctp_setsockopt`, `sctp_getsockopt`, `sctp_bpf_bypass_getsockopt`, `sctp_sendmsg`, `sctp_recvmsg`, `sctp_bind`, `sctp_bind_add`.
- Internal networking hooks: `sctp_backlog_rcv`, `sctp_hash`, `sctp_unhash`.
- Socket allocation and accounting: `obj_size`, `useroffset`, `usersize`, SCTP memory sysctls, memory-pressure counters, forward-allocation counters, and sockets-allocated counters.

The IPv6 table is compiled under `IS_ENABLED(CONFIG_IPV6)` and mirrors these callbacks. Its key differences are object layout (`struct sctp6_sock`), IPv6 private-info offset, and `sctp_v6_init_sock()`, which installs `sctp_v6_destruct_sock()` after common initialization succeeds.

## State And Persistence Behavior

All state in this chunk is in-memory kernel networking state. There is no filesystem or durable persistence.

Important state transitions and ownership effects include:

- Association references: `sctp_wait_for_connect()` holds the association across sleeps and releases it on every exit path.
- Wait queues: connect waits use `asoc->wait`, while accept and close waits use `sk_sleep(sk)`. State-machine code wakes these queues when association state changes.
- Socket locks: all three wait helpers release the socket lock before sleeping and reacquire it after wakeup. This is necessary for SCTP state-machine, backlog, close, and receive paths to make progress.
- Endpoint association list: `sctp_wait_for_accept()` and `sctp_wait_for_close()` treat `sctp_sk(sk)->ep->asocs` as the durable in-memory readiness/lifetime condition.
- Bind state: migrated sockets are added to the same bind bucket owner list and copy `inet_num`, so the new socket remains bound to the original local SCTP port.
- Bind addresses: the new endpoint receives a duplicate bind-address list from the old endpoint. This persists local address state across peeloff/accept and supports restart/address-management behavior.
- Receive queue state: skbs for the migrated association are moved from old socket queues to new socket queues, with skb owner/accounting rewritten for parent and fragment skbs.
- Partial-delivery state: `pd_mode` is copied from the association to the new socket, and `pd_lobby` entries are moved or released according to whether the migrating association is the active partial-delivery association.
- Association socket pointer: `sctp_assoc_migrate()` moves the association from `oldsk` to `newsk`; queued transmit chunks have write owners cleared and restored around this change.
- Socket state: migration publishes `SCTP_SS_ESTABLISHED` for normal accepted/peeled-off associations and `SCTP_SS_CLOSED` plus `RCV_SHUTDOWN` for already-closed TCP-style associations.
- Protocol accounting state: the `struct proto` tables bind SCTP sockets to global/per-net memory accounting counters, sysctl memory thresholds, and socket allocation counters.

## Dependencies And Integration Points

This chunk depends on core SCTP socket, endpoint, association, ULP event, and queue helpers defined earlier in the same file and in SCTP headers:

- Association state and references: `sctp_state()`, `sctp_association_hold()`, `sctp_association_put()`, `sctp_assoc_migrate()`.
- Socket and endpoint accessors: `sctp_sk()`, `sctp_style()`, `sctp_sstate()`, `inet_sk_set_state()`, `sk_sleep()`, `lock_sock()`, `release_sock()`.
- Queue/event helpers: `sctp_skb_for_each()`, `sctp_skb2event()`, `sctp_skb_set_owner_r()`, `sctp_clear_pd()`, `sctp_for_each_rx_skb()`, `sctp_for_each_tx_datachunk()`, `sctp_clear_owner_w()`, `sctp_set_owner_w()`.
- Bind/address helpers: `sctp_phashfn()`, `sctp_port_hashtable`, `sk_add_bind_node()`, `sctp_bind_addr_dup()`, `sctp_auto_asconf_init()`.
- Linux wait and scheduling primitives: `DEFINE_WAIT`, `prepare_to_wait_exclusive()`, `prepare_to_wait()`, `finish_wait()`, `schedule_timeout()`, `TASK_INTERRUPTIBLE`, and `signal_pending()`.
- Socket error/timeout conventions: `sock_intr_errno()`, `sock_rcvtimeo()`, `sock_sndtimeo()`, nonblocking `-EINPROGRESS`/`-EAGAIN`, and shutdown flags such as `RCV_SHUTDOWN`.
- Memory/accounting integration: skb owner APIs, `sk_wmem_queued`, protocol memory-pressure counters, SCTP sysctl memory arrays, and proto `useroffset`/`usersize` support.
- IPv6 integration: `inet6_sock_destruct()`, `struct sctp6_sock`, `struct ipv6_pinfo`, and `CONFIG_IPV6` registration paths.

Important external callers and registration points:

- `__sctp_connect()` starts association setup and calls `sctp_wait_for_connect()` with send-timeout semantics.
- `sctp_accept()` calls `sctp_wait_for_accept()`, selects the first endpoint association, and calls `sctp_clone_sock()`, which delegates to `sctp_sock_migrate()`.
- UDP-style peeloff calls `sctp_do_peeloff()`, which validates namespace/style/association ID, creates a lightweight socket, clones the SCTP socket, and relies on `sctp_sock_migrate()` to move the association.
- `sctp_close()` calls `sctp_wait_for_close()` for TCP-style sockets when linger waiting is requested.
- `net/sctp/protocol.c` registers `sctp_prot` for IPv4/inet SCTP operation, and `net/sctp/ipv6.c` registers `sctpv6_prot` when IPv6 support is enabled.
- SCTP state-machine side effects in `sm_sideeffect.c` wake `asoc->wait` and `sk->sk_state_change()` so these socket waiters observe association transitions.

## Risks And Edge Cases

- Sleep paths must always release the socket lock before `schedule_timeout()`. Holding it while sleeping would block the state-machine and backlog work needed to satisfy the wait condition.
- `sctp_wait_for_connect()` checks the original timeout pointer before sleeping and writes back the remaining `current_timeo` after wakeup. Callers depend on this remaining-time behavior for connect timeout semantics.
- Connect failure mapping depends on `init_err_counter + 1 > max_init_attempts`. Changing init retry accounting can alter whether userspace sees `-ECONNREFUSED` or `-ETIMEDOUT`.
- Accept readiness is represented by `ep->asocs`, not a separate accept queue object. Any code that adds or removes associations from a TCP-style listening endpoint must preserve the wakeup and list invariants expected here.
- `sctp_wait_for_accept()` can sleep with zero timeout, but `schedule_timeout(0)` returns immediately and the later timeout check returns `-EAGAIN`. This preserves nonblocking accept behavior but is easy to misread.
- `sctp_wait_for_close()` ignores the final reason for wakeup. That is intentional for close, but callers cannot distinguish clean association drain from signal/timeout based on this helper alone.
- Socket migration has several ownership domains that must move together: bind-hash membership, endpoint bind addresses, receive queues, partial-delivery lobby, association ULP queues, association socket pointer, and transmit skb owners. Missing one can leak memory accounting, deliver data on the wrong descriptor, or leave retransmission chunks charged to the wrong socket.
- The bind-hash insertion happens before `sctp_bind_addr_dup()`. If address duplication fails, cleanup relies on the caller's `sk_common_release(newsk)` path to unwind the partially attached clone correctly.
- Receive skb migration filters by `event->asoc == assoc`. Any skb queued without a valid SCTP ULP event association would not migrate and could remain attached to the old socket.
- Fragment ownership is recursive. A future change that only retargets the parent skb would leave fragment memory ownership inconsistent.
- Partial delivery is subtle. If the migrated association is in partial delivery, its lobby must remain in the new socket's partial-delivery lobby; if not, its skbs should become ordinary receive-queue data. Incorrect handling can stall partial delivery or reorder user-visible data.
- Lock ordering during migration is constrained. The old socket is already locked by the caller, and the newly allocated socket is locked with `SINGLE_DEPTH_NESTING`. The code relies on the new socket not being reachable by other paths yet, preventing lock-order inversions.
- The migration code deliberately locks `newsk` before `sctp_assoc_migrate()` so packets arriving after the association socket pointer changes go to backlog. Removing this would reopen a race between old-socket backlog processing and new-socket packet processing.
- Transmit chunk owner retargeting must bracket `sctp_assoc_migrate()`. If ownership is set before association migration or not restored after it, send-buffer accounting and write-space wakeups can be wrong.
- Closed associations can still be accepted from a TCP-style listening socket. The migration path sets `RCV_SHUTDOWN` for this case; callers and tests must not assume accept always returns an established live association.
- `struct proto.useroffset` and `usersize` expose a contiguous region of SCTP socket state for userspace-copy handling. Layout changes to `struct sctp_sock` or `struct sctp6_sock` must keep this range intentional.
- IPv6 sockets depend on `sctp_v6_init_sock()` replacing the destructor only after common SCTP initialization succeeds. Installing it too early or failing to install it can break IPv6 private-state cleanup.
- Protocol table changes are broad blast-radius changes. A wrong callback, object size, memory counter, or hash/unhash hook can affect all SCTP sockets, including both Ceph-adjacent kernels and unrelated SCTP applications.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage with SCTP enabled both with and without `CONFIG_IPV6`, verifying that `sctp_prot` and `sctpv6_prot` register with the expected object sizes and callbacks.
- Active connect tests for blocking connect success, nonblocking connect returning `-EINPROGRESS`, interrupted connect returning the expected restart/interrupted errno, setup refusal, and timeout after exhausting init attempts.
- Connect race tests where the association reaches `ESTABLISHED`, `CLOSED`, `SHUTDOWN_RECEIVED`, shutdown-pending, or dead state while a task sleeps in `sctp_wait_for_connect()`.
- Lockdep and scheduling tests that exercise connect, accept, and close waits under load, ensuring no socket lock is held across blocking sleeps and no waitqueue entries leak.
- TCP-style accept tests for blocking accept, nonblocking accept returning `-EAGAIN`, interrupted accept, accept after listener shutdown returning `-EINVAL`, and accepting an already-closed association with `RCV_SHUTDOWN` set on the new socket.
- Close/linger tests where associations drain before timeout, timeout expires with associations still present, and a signal interrupts the close wait.
- UDP-style peeloff tests for valid association ID, invalid association ID, wrong socket style, already peeled-off sockets, and namespace mismatch rejection.
- Migration tests that queue receive data for multiple associations on a UDP-style socket, peel off one association, and confirm only that association's events move to the new socket.
- Fragmented receive skb tests confirming parent and fragment skb receive ownership/accounting move to `newsk`.
- Partial-delivery tests covering migration of the active partial-delivery association, migration of a non-partial association while the old socket is in partial-delivery mode, and clearing of old partial-delivery state.
- ULP reassembly/lobby tests verifying skbs in `assoc->ulpq.lobby`, `reasm`, and `reasm_uo` have ownership retargeted during accept or peeloff.
- Transmit queue tests with chunks in transmitted, retransmit, sacked, abandoned, and unsent queues during migration, checking send-buffer accounting, retransmission behavior, and write-space wakeups after migration.
- Bind/address tests confirming accepted and peeled-off sockets retain the original local port, bind hash membership, and bind address list, including multihoming/restart scenarios.
- Concurrency tests with packets arriving during `sctp_sock_migrate()`, verifying they queue to the new socket backlog and are not processed concurrently on old and new sockets.
- Security/LSM integration tests around `sctp_clone_sock()` and migration, ensuring later `security_sctp_sk_clone()` sees the migrated association and new socket state expected by policy.
- IPv6 SCTP socket lifecycle tests confirming `sctp_v6_init_sock()` uses the common SCTP initialization path and that IPv6 socket destruction releases IPv6 private state.
- Memory diagnostics with KASAN/KCSAN/KMEMLEAK/refcount debugging around accept, peeloff, connect timeout, and close to catch use-after-free, leaked association references, bind bucket leaks, or skb accounting mismatches.
