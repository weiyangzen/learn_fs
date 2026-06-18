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
