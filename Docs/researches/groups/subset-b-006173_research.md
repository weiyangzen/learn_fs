<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/transport.c -->
# sources/distributed-fs/ceph-client/net/can/j1939/transport.c

## Purpose
Implements SAE J1939 transport protocol handling for CAN: simple single-frame sends, TP connection-managed and broadcast transfers, and ETP extended transfers. It segments outgoing payloads into 7-byte data packets, reassembles incoming multi-packet payloads, handles RTS/CTS/DPO/EOMA/ABORT control frames, and reports transport progress or failure back to J1939 sockets.

## Important APIs, Types, and Functions
The file operates on `struct j1939_session`, `struct j1939_priv`, `struct j1939_sk_buff_cb`, and socket-owned `sk_buff` queues. Exported or externally used entry points include `j1939_tp_send()`, `j1939_session_activate()`, `j1939_tp_recv()`, `j1939_simple_recv()`, `j1939_cancel_active_session()`, `j1939_tp_init()`, `j1939_session_get()`, `j1939_session_put()`, `j1939_session_skb_queue()`, and `j1939_session_timers_cancel()`. Internal control paths include `j1939_session_tx_rts()`, `j1939_session_tx_cts()`, `j1939_session_tx_dpo()`, `j1939_session_tx_dat()`, `j1939_session_tx_eoma()`, `j1939_xtp_rx_rts()`, `j1939_xtp_rx_cts()`, `j1939_xtp_rx_dpo()`, `j1939_xtp_rx_dat()`, `j1939_xtp_rx_eoma()`, and `j1939_xtp_rx_abort()`. `enum j1939_xtp_abort` maps wire abort reasons to Linux errno values.

## Control Flow
Outgoing payloads enter through `j1939_tp_send()`, which rejects reserved TP/ETP PGNs, chooses `J1939_SIMPLE`, `J1939_TP`, or `J1939_ETP` by size, forbids broadcast ETP, fixes address-claim state, creates a refcounted session, and sets packet counters. `j1939_session_activate()` inserts the session into `priv->active_session_list` unless another active session with the same address tuple and direction exists. Timers drive transmission: simple sessions clone and send the original skb, TP/ETP transmitters send RTS, react to CTS/DPO, transmit data packets, and finish on EOMA. Receivers allocate a fresh skb sized to the advertised payload, validate size and PGN, send CTS windows, copy incoming data into the reassembly skb, and complete on BAM final data or EOMA.

Incoming frames enter through `j1939_tp_recv()`. The PGN selects data or control handling and sets TP versus ETP type. `j1939_tp_cmd_recv()` dispatches control commands in both local directions because looped-back frames can confirm local sends. Bad PGNs, duplicate sequence/control frames, unexpected data, timeouts, and resource limits trigger aborts and timer-driven cleanup.

## State and Persistence
Session state is in memory only. Sessions are kref-managed; timers take references and release them from callbacks. Active sessions are protected by `priv->active_session_list_lock`; queued skb fragments use the skb queue lock. Important mutable fields include `state`, `err`, `last_cmd`, `last_txcmd`, `transmission`, `tskey`, `pkt.total`, `pkt.rx`, `pkt.tx`, `pkt.tx_acked`, `pkt.last`, `pkt.block`, and `pkt.dpo`. Static tunables `j1939_tp_block`, `j1939_tp_packet_delay`, and `j1939_tp_padding` influence packet windowing, inter-packet delay, and padding. There is no persistent storage; hardware/bus effects are CAN frames already transmitted.

## Dependencies and Integration Points
Depends on PF_CAN/J1939 private helpers in `j1939-priv.h`, CAN skb extensions, address-claim fixups, J1939 socket queues/error queues, `j1939_send_one()`, and network-device registration state. It integrates with local loopback semantics, socket timestamp keys, per-interface J1939 private state, and netdevice shutdown cancellation.

## Risks
The high-risk areas are refcount/timer interactions, active-session list races, handling of locally looped-back frames, and wire-state validation. Duplicate RTS handling intentionally forces receiver deactivation in one corner case to avoid an abort timer being canceled without restart. Miscomputed packet offsets can read/write outside a queued skb, guarded by explicit overflow checks. Broadcast sessions do not send aborts, so receiver resource failures are less visible. Error values sometimes store positive errno constants rather than negative values, matching existing error-queue conventions but worth review when consumed by callers.

## Test Signals
Strong signals include multi-packet unicast TP success with RTS/CTS/EOMA, BAM broadcast receive completion, ETP transfers over the TP maximum, ETP broadcast rejection, timeout-to-abort paths, CTS(0) hold behavior, duplicate/bad-sequence aborts, concurrent same-address session rejection, CAN TX queue `-ENOBUFS` retry behavior, local loopback confirmation for simple and segmented sends, netdevice unregister cancellation, and socket error-queue events for TX/RX ACK and abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/proc.c -->
# sources/distributed-fs/ceph-client/net/can/proc.c

## Purpose
Provides `/proc/net/can` visibility for the PF_CAN core. It exposes aggregate CAN frame statistics, a reset trigger, and receiver-list dumps for all-device and per-device CAN receive lists.

## Important APIs, Types, and Functions
Key public functions are `can_init_proc()`, `can_remove_proc()`, and timer callback `can_stat_update()`. Internal helpers include `can_init_stats()`, `calc_rate()`, `can_stats_proc_show()`, `can_reset_stats_proc_show()`, `can_rcvlist_proc_show()`, `can_rcvlist_sff_proc_show()`, `can_rcvlist_eff_proc_show()`, `can_print_rcvlist()`, and `can_print_recv_banner()`. The code reads `struct can_pkg_stats`, `struct can_rcv_lists_stats`, `struct can_dev_rcv_lists`, `struct receiver`, and per-net `net->can` proc entry pointers.

## Control Flow
`can_init_proc()` creates `/proc/net/can` and entries for `stats`, `reset_stats`, and each receiver-list view. `stats` prints total frame counters, matched frame counters, receive-list counts, and rate/ratio values when the stats timer is active. `reset_stats` sets a global `user_reset` flag; if the timer is inactive, it resets immediately. Receiver-list proc handlers enter an RCU read-side section, first print the all-device receive list, then iterate registered CAN netdevices and print their matching list buckets.

`can_stat_update()` runs once per second when enabled. It handles user reset, jiffies wrap, and counter overflow by reinitializing stats; otherwise it calculates total and current TX/RX rates, match ratios, maximums, clears delta counters, and re-arms the timer.

## State and Persistence
Statistics are per network namespace in `net->can.pkg_stats` and `net->can.rcv_lists_stats`. Proc dentries are stored in `net->can.pde_*`. `user_reset` is a file-global flag rather than per-net state, so reset requests are process-visible across namespaces until consumed. No data persists beyond runtime memory.

## Dependencies and Integration Points
Depends on procfs, seq_file, RCU, CAN receive-list internals from `af_can.h`, CAN core multi-list helpers, and netdevice iteration. It is compiled into the PF_CAN core path and assumes receiver lists are RCU-safe while printed.

## Risks
The main design risk is the global `user_reset` flag in otherwise per-net code. Proc output exposes function and user-data pointers through `%pK`, subject to kernel pointer restrictions. Rate calculations rely on periodic timer cadence and integer arithmetic, so very high counters force resets to avoid overflow. `can_init_proc()` does not unwind partially created entries if a later `proc_create_net_single()` fails.

## Test Signals
Useful signals are creation/removal of all proc entries per network namespace, accurate stats reset behavior with timer enabled and disabled, stable output under concurrent CAN filter registration/unregistration, correct all-device and per-interface receiver-list dumps, jiffies-wrap/overflow reset coverage, and no RCU or lockdep warnings while reading proc files under CAN traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/raw.c -->
# sources/distributed-fs/ceph-client/net/can/raw.c

## Purpose
Implements the PF_CAN raw socket protocol (`CAN_RAW`). It lets users bind raw sockets to a CAN interface or all interfaces, configure CAN ID and error filters, opt into CAN FD and CAN XL frames, control loopback and own-message reception, send frames, and receive matched CAN datagrams.

## Important APIs, Types, and Functions
The central type is `struct raw_sock`, which embeds `struct sock` and stores bound device state, filter arrays, error masks, CAN FD/XL enable flags, CAN XL VCID options, loopback settings, notifier linkage, and per-CPU duplicate-suppression state (`struct uniqframe`). Key functions are `raw_init()`, `raw_release()`, `raw_bind()`, `raw_setsockopt()`, `raw_getsockopt()`, `raw_sendmsg()`, `raw_recvmsg()`, `raw_rcv()`, `raw_enable_filters()`, `raw_disable_filters()`, `raw_enable_errfilter()`, `raw_notify()`, and `raw_notifier()`. Protocol registration is through `raw_can_proto`, `raw_proto`, and `raw_ops`.

## Control Flow
Socket creation initializes one default catch-all filter stored in `dfilter`, allocates per-CPU duplicate tracking, and links the socket into `raw_notifier_list`. Binding validates `sockaddr_can`, resolves an optional CAN netdevice, registers current filters against either the device or all devices, then unregisters old filters and updates held device references. `setsockopt()` replaces filters and error masks with register-new-then-unregister-old ordering for bound sockets; other options mutate local flags.

Receive callbacks are invoked by the CAN core for each matching filter. `raw_rcv()` drops unwanted looped-back frames, disallowed FD/XL frames, and CAN XL frames failing VCID policy. It suppresses duplicate deliveries from multiple matching filters, or with `CAN_RAW_JOIN_FILTERS` waits until all filters matched. Accepted frames are cloned, annotated with `sockaddr_can` and message flags in `skb->cb`, and queued to the socket. `sendmsg()` obtains the target device, rejects read-only devices, copies user frame bytes into an skb, validates CAN/FD/XL size and device capability, applies CAN XL VCID transmit policy, handles control messages, and calls `can_send()`.

## State and Persistence
All state is socket-local except the global notifier list and the transient `raw_busy_notifier` reentrancy guard. `ro->dev` is refcounted with a `netdevice_tracker` while bound. `ro->filter` either points at inline `dfilter`, a dynamically allocated filter array, or NULL when zero filters are configured. No state is persisted beyond socket lifetime.

## Dependencies and Integration Points
Depends on the CAN core receive registry (`can_rx_register()`/`can_rx_unregister()`), CAN skb extensions, CAN frame validators, netdevice notifier API, socket layer datagram queues, control message parsing, and CAN capability bits (`CAN_CAP_CC`, `CAN_CAP_FD`, `CAN_CAP_XL`, `CAN_CAP_RO`). It registers as protocol `CAN_RAW` / `can-proto-1`.

## Risks
Filter replacement is sensitive to lock ordering (`rtnl_lock()` plus socket lock) and to cleanup on partial registration failure. The notifier loop intentionally drops the spinlock while notifying sockets and uses `raw_busy_notifier` to avoid freeing a socket being notified. Per-CPU duplicate suppression relies on skb pointer and hash stability across callback invocations. CAN XL VCID policy has deny-by-default behavior for tagged RX frames unless a filter is enabled, which can surprise callers. Send path must keep frame-size validation aligned with CAN core helpers.

## Test Signals
Cover default receive-all binding, zero filters receiving nothing, multi-filter duplicate suppression, join-filter behavior, error mask registration, device unregister/down notifications, bind-to-all versus bind-to-device, CAN FD opt-in, CAN XL opt-in and VCID RX/TX options, read-only send rejection, capability-based frame-size rejection, own-message flags (`MSG_CONFIRM`/`MSG_DONTROUTE`), and module register/unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/Kconfig -->
# sources/distributed-fs/ceph-client/net/ceph/Kconfig

## Purpose
Defines build-time configuration for the in-kernel Ceph core library used by CephFS and RBD. It also exposes optional debug-output formatting and in-kernel DNS resolver support.

## Important APIs, Types, and Functions
This is Kconfig data rather than C code. `CEPH_LIB` is a tristate depending on `INET` and selecting CRC, crypto, keyring, AES-CBC/GCM, KRB5, SHA-256, and generic crypto support. `CEPH_LIB_PRETTYDEBUG` enables file:line debug output. `CEPH_LIB_USE_DNS_RESOLVER` selects `DNS_RESOLVER` for monitor hostname resolution.

## Control Flow
The selected options drive what objects the Makefile builds and which optional code paths compile. Enabling `CEPH_LIB` makes `libceph.o` available built-in or as a module. The DNS option compiles code expecting kernel DNS resolver integration elsewhere in libceph.

## State and Persistence
There is no runtime state in this file. Its effects persist in the kernel configuration and compiled object set.

## Dependencies and Integration Points
Integrates with the kernel Kconfig system, CephFS/RBD consumers, the kernel crypto API, keyrings, and networking. The crypto selections match the auth and messenger code in this directory, especially CephX and secure messenger modes.

## Risks
Dependency drift is the main risk: auth/crypto code assumes selected algorithms and keyring support are present. Selecting broad crypto dependencies increases kernel size. Pretty debug can enlarge code and slow dynamic-debug-enabled paths. DNS resolver support depends on correct runtime resolver configuration outside this file.

## Test Signals
Build `CEPH_LIB` as built-in and module, confirm all selected crypto/key symbols resolve, enable pretty debug and verify debug format changes, enable DNS resolver and mount with hostname monitor addresses, and verify disabled `CEPH_LIB` excludes libceph consumers unless they select it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/Makefile -->
# sources/distributed-fs/ceph-client/net/ceph/Makefile

## Purpose
Builds the `libceph.o` composite object when `CONFIG_CEPH_LIB` is enabled.

## Important APIs, Types, and Functions
The key build rule is `obj-$(CONFIG_CEPH_LIB) += libceph.o`. `libceph-y` lists the component objects: common client setup, messenger v1/v2, message pools, buffers, pagelists, monitor and OSD clients, OSD maps, CRUSH, striping, debugfs, auth backends, crypto/armor, strings/hashes, page vectors, snapshots, and string tables.

## Control Flow
Kbuild compiles each listed object and links them into `libceph.o`. The order matters only where init/exit references require symbols to be linked into the composite object; runtime init order is in `ceph_common.c`.

## State and Persistence
No runtime state. It persists build composition in generated objects and modules.

## Dependencies and Integration Points
Integrates with Kbuild and `Kconfig`. The file defines the library surface available to CephFS and RBD by including protocol, crypto, placement, and client-control objects in one module.

## Risks
Missing an object from `libceph-y` causes link failures or feature loss. Adding objects with init/exit side effects requires checking `init_ceph_lib()` ordering. Build composition should stay synchronized with Kconfig crypto and networking selections.

## Test Signals
Build libceph built-in and as a module, run `modinfo`/symbol checks for exported auth, crypto, CRUSH, and client helpers, and verify no unresolved symbols under common CephFS/RBD configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/armor.c -->
# sources/distributed-fs/ceph-client/net/ceph/armor.c

## Purpose
Provides Ceph's small base64-like armor and unarmor helpers for encoding binary secrets into printable strings and decoding them back.

## Important APIs, Types, and Functions
The exported local APIs are `ceph_armor()` and `ceph_unarmor()`, declared here and in `crypto.h`. Internal helpers `encode_bits()` and `decode_bits()` map six-bit values to the `A-Z a-z 0-9 + /` alphabet and accept `=` padding.

## Control Flow
`ceph_armor()` consumes bytes from `src` to `end`, emits 4-byte base64 groups, inserts `=` padding for one- and two-byte tails, and inserts a newline after every 64 encoded characters. It returns the encoded byte count, including newlines, but does not NUL-terminate. `ceph_unarmor()` skips newline characters, requires complete 4-character groups, validates each character, writes one to three decoded bytes according to padding, and returns decoded length. Invalid characters or incomplete groups return `-EINVAL`.

## State and Persistence
The only state is the static alphabet string. The functions mutate caller-provided buffers and do not allocate or persist data.

## Dependencies and Integration Points
Used by `ceph_crypto_key_unarmor()` to decode mount `secret=` values. Depends only on errno definitions and caller-managed buffer sizing.

## Risks
There is no destination-size parameter, so callers must provision enough output space. `ceph_unarmor()` treats `=` as a non-negative six-bit value and stops on padding positions; malformed padding in odd positions relies on the group logic. The encoder does not append a terminator, which is correct for binary output but can surprise string callers.

## Test Signals
Round-trip binary keys of lengths 0, 1, 2, 3, and larger than 48 bytes, verify newline insertion at 64 encoded characters, reject invalid characters and truncated groups, decode padded strings correctly, and run with KASAN or fortified buffers to validate caller sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/armor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth.c -->
# sources/distributed-fs/ceph-client/net/ceph/auth.c

## Purpose
Implements the generic Ceph authentication client dispatcher for monitor auth and messenger v2 authentication. It negotiates protocol selection, serializes auth requests, decodes replies, owns the auth mutex, and delegates protocol-specific behavior to `auth_none` or CephX ops.

## Important APIs, Types, and Functions
Core APIs include `ceph_auth_init()`, `ceph_auth_destroy()`, `ceph_auth_reset()`, `ceph_auth_build_hello()`, `ceph_handle_auth_reply()`, `ceph_build_auth()`, `ceph_auth_is_authenticated()`, `__ceph_auth_get_authorizer()`, `ceph_auth_get_authorizer()`, `ceph_auth_add_authorizer_challenge()`, `ceph_auth_verify_authorizer_reply()`, `ceph_auth_handle_reply_more()`, `ceph_auth_handle_reply_done()`, `ceph_auth_handle_bad_method()`, `ceph_auth_handle_svc_reply_more()`, `ceph_auth_handle_svc_reply_done()`, and `ceph_auth_handle_bad_authorizer()`. It manipulates `struct ceph_auth_client`, `struct ceph_auth_client_ops`, and `struct ceph_auth_handshake`.

## Control Flow
`ceph_auth_init()` creates a negotiating client with name, optional key, and preferred/fallback connection modes. Monitor v1 auth begins with `ceph_auth_build_hello()`, which encodes supported protocols and entity name. `ceph_handle_auth_reply()` decodes monitor replies, initializes or switches protocol handlers during negotiation, sets global id through the backend, and builds a follow-up request on `-EAGAIN`. `ceph_build_auth()` emits later requests if the selected backend says authentication is needed.

For msgr2, `ceph_auth_get_request()` initializes the expected protocol directly from key presence, encodes connection modes, entity name, and global id. Reply-more/done functions delegate backend payload handling. Service authorization uses `__ceph_auth_get_authorizer()` to create or update authorizers, then wraps authorizer length/mode metadata. Bad-method handlers decide whether errors are retryable with different auth settings or fatal.

## State and Persistence
`struct ceph_auth_client` holds global id, selected protocol, backend private state, key pointer, wanted service keys, and mode preferences. All mutable auth state is protected by `ac->mutex`. There is no disk persistence; tickets and secrets live in backend memory and are destroyed with the auth client.

## Dependencies and Integration Points
Depends on Ceph protocol encoders/decoders, monitor request headers, `ceph_auth_none_init()`, `ceph_x_init()`, messenger connection modes, and exported helpers used by monitor, OSD, MDS, and messenger code. The service-authorizer callbacks integrate with msgr2 challenge/reply and message-signature hooks.

## Risks
Protocol switching during negotiation destroys existing backend state; callers must not hold stale authorizers across reset/invalidation. Buffer encoding uses explicit bounds but relies on correct caller-provided lengths. `ceph_auth_get_request()` warns if protocol and key-derived expectation diverge. Bad-method handling must match server-allowed protocol/mode arrays or clients can retry when they should fail. Global-id changes are logged but still assigned.

## Test Signals
Exercise auth-none monitor flow, CephX multi-step monitor flow, msgr2 request/reply-more/reply-done, backend `-EAGAIN` follow-up generation, bad method with disallowed protocol or mode, authorizer create/update/invalidate paths, malformed reply bounds, global-id assignment, and concurrent callers under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_none.c -->
# sources/distributed-fs/ceph-client/net/ceph/auth_none.c

## Purpose
Implements the `CEPH_AUTH_NONE` backend for clusters or connections that do not use a secret. It provides a minimal monitor auth state and service authorizer containing the client entity name and global id.

## Important APIs, Types, and Functions
The public initializer is `ceph_auth_none_init()`. Backend ops are `reset()`, `destroy()`, `is_authenticated()`, `should_authenticate()`, `build_request()`, `handle_reply()`, and `ceph_auth_none_create_authorizer()`. `ceph_auth_none_build_authorizer()` encodes the authorizer into `struct ceph_none_authorizer`.

## Control Flow
Initialization allocates `struct ceph_auth_none_info`, marks it starting, sets protocol to `CEPH_AUTH_NONE`, and installs `ceph_auth_none_ops`. There is no auth request payload. On monitor reply, `handle_reply()` clears `starting` and records the generic decoded global id. Service authorizer creation allocates a small object, encodes version byte, entity name, and global id, then exposes the buffer through `struct ceph_auth_handshake`.

## State and Persistence
State is limited to the `starting` boolean in `ac->private` and one allocated authorizer per handshake. The authorizer buffer is fixed at 128 bytes. No secrets or persistent tickets exist.

## Dependencies and Integration Points
Depends on generic auth encoding, Ceph entity-name encoding, and the generic authorizer destroy callback contract. It is selected by `auth.c` when protocol `CEPH_AUTH_NONE` is chosen.

## Risks
The fixed authorizer buffer assumes client names remain small enough after entity encoding. `build_request()` always returns 0, so protocol peers must accept an empty monitor payload. This backend provides identity but no cryptographic authentication or message signing.

## Test Signals
Authenticate without a key, verify `should_authenticate()` transitions from true to false after reply, create authorizers for monitor/OSD/MDS peer types, test long client names against the 128-byte buffer, and confirm secure-mode or signature requirements reject auth-none when the server disallows it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_none.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_none.h -->
# sources/distributed-fs/ceph-client/net/ceph/auth_none.h

## Purpose
Declares private types and initializer for the auth-none backend.

## Important APIs, Types, and Functions
`struct ceph_none_authorizer` wraps `struct ceph_authorizer`, a 128-byte encoded buffer, and its length. `struct ceph_auth_none_info` stores the backend `starting` flag. `ceph_auth_none_init()` is the initializer consumed by `auth.c`.

## Control Flow
The header has no executable flow. It defines the data layout used by `auth_none.c` to create authorizers and track monitor-auth progress.

## State and Persistence
No standalone state. The declared structs are allocated by `auth_none.c` for each auth client and authorizer.

## Dependencies and Integration Points
Includes Ceph generic auth declarations and slab helpers. It is private to the libceph auth implementation, not a UAPI header.

## Risks
Changing the fixed buffer size or struct layout requires checking `ceph_auth_none_build_authorizer()` bounds and all authorizer users. The header comment accurately states this is null security mode, so callers must not infer confidentiality or integrity from it.

## Test Signals
Compile coverage with `auth_none.c`, authorizer buffer-size tests, and backend init/destroy tests that verify `ac->private` lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_none.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_x.c -->
# sources/distributed-fs/ceph-client/net/ceph/auth_x.c

## Purpose
Implements the CephX authentication backend. It obtains and renews service tickets, builds encrypted authorizers, handles server challenges and replies, extracts session/connection secrets, and signs or verifies Ceph messages.

## Important APIs, Types, and Functions
The public initializer is `ceph_x_init()`. Backend ops include `ceph_x_is_authenticated()`, `ceph_x_should_authenticate()`, `ceph_x_build_request()`, `ceph_x_handle_reply()`, `ceph_x_create_authorizer()`, `ceph_x_update_authorizer()`, `ceph_x_add_authorizer_challenge()`, `ceph_x_verify_authorizer_reply()`, `ceph_x_invalidate_authorizer()`, `ceph_x_reset()`, `ceph_x_destroy()`, `ceph_x_sign_message()`, and `ceph_x_check_message_signature()`. Internal helpers manage ticket handlers in an rbtree (`get_ticket_handler()`, `process_one_ticket()`, `ceph_x_proc_ticket_reply()`), encryption wrappers (`ceph_x_encrypt()`, `ceph_x_decrypt()`), and authorizer buffers (`ceph_x_build_authorizer()`, `encrypt_authorizer()`).

## Control Flow
Initialization clones the client secret, prepares key usage transforms, sets `starting`, initializes the ticket-handler tree, and installs ops. The first monitor reply is a server challenge; the backend stores it and returns `-EAGAIN`. The next request either asks for an auth session key using the client secret and challenge-derived proof, or asks for principal service tickets using an AUTH authorizer. Ticket replies decrypt a "blob for me" into a session key and validity window, decode or decrypt the service ticket blob, update the handler, and set `have_keys`.

Service connections create a `ceph_x_authorizer` from the relevant service ticket: part A is clear metadata and ticket blob, part B is encrypted nonce/challenge data. A server challenge decrypts to a challenge value and causes the authorizer to be re-encrypted with `challenge+1`. The final reply decrypts `nonce+1` and optional connection secret; mismatch returns `-EPERM`. Message signing derives a 64-bit signature from encrypted or HMACed CRC/length blocks, with v1/v2 feature-dependent formats.

## State and Persistence
`struct ceph_x_info` holds the cloned client secret, start/challenge state, bitmask of service keys, an rbtree of `struct ceph_x_ticket_handler`, and a reusable AUTH authorizer. Each ticket handler owns a session key, ticket blob, secret id, expiration, and renewal time. Authorizers own cloned service session keys and `ceph_buffer` payloads. State is memory-only and destroyed by `ceph_x_destroy()`.

## Dependencies and Integration Points
Depends on `crypto.c` for AES/AES256KRB5 operations, `buffer.c` for ticket blobs, Ceph protocol encoders, Ceph feature bits, messenger message/footer layout, and generic auth callbacks. Key usage arrays must match `auth_x_protocol.h` constants and prepared crypto transform slots.

## Risks
CephX is sensitive to buffer offsets that differ between AES and AES256KRB5, key usage slot ordering, ticket expiration arithmetic, and zeroing decrypted secrets. `process_one_ticket()` updates handler state only after successful decode, but intermediate key material must be destroyed on errors. Signature behavior is disabled by `NOMSGSIGN`, so configuration can reduce integrity. Ticket-handler rbtree mutations assume caller holds `ac->mutex` through generic auth.

## Test Signals
Test initial challenge/request, auth ticket acquisition, service ticket acquisition, ticket renewal after `renew_after`, expiration clearing, malformed encrypted headers/magic, service challenge-response, nonce mismatch rejection, connection secret length limits and zeroing, message signing/checking with and without `CEPHX_V2`, AES and AES256KRB5 keys, authorizer update after secret-id change, and backend reset/destroy leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_x.h -->
# sources/distributed-fs/ceph-client/net/ceph/auth_x.h

## Purpose
Declares private CephX backend data structures and the `ceph_x_init()` initializer.

## Important APIs, Types, and Functions
`struct ceph_x_ticket_handler` stores one service ticket in an rbtree node, including service id, session key, `have_key`, secret id, ticket blob, renewal time, and expiration time. `struct ceph_x_authorizer` wraps the generic authorizer, a cloned session key, encoded buffer, service id, nonce, secret id, and aligned 128-byte encryption scratch buffer. `struct ceph_x_info` stores the client secret, starting state, server challenge, key bitmask, ticket-handler tree, and reusable AUTH authorizer. `CEPHX_AU_ENC_BUF_LEN` sizes small encrypted blobs.

## Control Flow
No executable flow. These structs are allocated and mutated by `auth_x.c` under the generic auth mutex.

## State and Persistence
All declared state is per-auth-client or per-authorizer memory. Ticket blobs are refcounted Ceph buffers; crypto keys require explicit destruction.

## Dependencies and Integration Points
Includes generic Ceph auth types, crypto private declarations, rbtree support, and CephX wire protocol structures. The layout is internal to libceph.

## Risks
The fixed 128-byte authorizer encryption scratch buffer must remain large enough for all encrypted challenge/signature blocks. Adding key usages beyond three requires updating `struct ceph_crypto_key` transform capacity in `crypto.h`. State lifetime requires matching cleanup in `ceph_x_destroy_authorizer()` and `ceph_x_destroy()`.

## Test Signals
Compile with CephX enabled, KASAN/KMEMLEAK tests for ticket and authorizer lifetime, encrypted blob size tests against `CEPHX_AU_ENC_BUF_LEN`, and reset/destroy tests with multiple service tickets in the rbtree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_x_protocol.h -->
# sources/distributed-fs/ceph-client/net/ceph/auth_x_protocol.h

## Purpose
Defines CephX wire-protocol constants and packed message structures shared by the CephX backend.

## Important APIs, Types, and Functions
Constants include request opcodes `CEPHX_GET_AUTH_SESSION_KEY`, `CEPHX_GET_PRINCIPAL_SESSION_KEY`, `CEPHX_GET_ROTATING_KEY`, key usage numbers for auth connection secrets, ticket session keys, ticket blobs, authorizers, challenges, and replies, plus `CEPHX_ENC_MAGIC`. Packed structs describe ticket blobs, request/reply headers, server challenge, authenticate request, service ticket request, challenge proof blob, authorizer parts A and B, authorize challenge/reply, and encrypted bundle header.

## Control Flow
No code runs here. `auth_x.c` fills, encrypts, decrypts, and validates these layouts while constructing monitor and service auth messages.

## State and Persistence
No runtime state. The definitions are ABI contracts for on-wire message layout and must remain byte-stable.

## Dependencies and Integration Points
Used by `auth_x.c` and `auth_x.h`. The packed little-endian fields integrate with Ceph protocol encoders and monitor/service peers.

## Risks
Changing struct layout, packing, field order, or key usage constants would break interoperability. The comments distinguish client-auth, ticket, and service-authorizer encryption contexts; using the wrong usage value weakens or breaks authentication. `CEPHX_ENC_MAGIC` is a key validation signal after decryption.

## Test Signals
Wire-compatibility tests against userspace Ceph, decode/encode tests for every struct version, encrypted-header magic validation, and cross-version tests for Nautilus-era authenticate/service-ticket behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/auth_x_protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/buffer.c -->
# sources/distributed-fs/ceph-client/net/ceph/buffer.c

## Purpose
Provides refcounted variable-size buffers for libceph payloads such as decoded ticket blobs and authorizers.

## Important APIs, Types, and Functions
APIs are `ceph_buffer_new()`, `ceph_buffer_release()`, and `ceph_decode_buffer()`. The implementation uses `struct ceph_buffer`, `struct kref`, `kvmalloc()`/`kvfree()`, and Ceph decode helpers.

## Control Flow
`ceph_buffer_new()` allocates the metadata with `kmalloc`, allocates a data vector with `kvmalloc`, initializes the kref and lengths, and returns the buffer. `ceph_buffer_release()` frees the vector and metadata when the kref reaches zero. `ceph_decode_buffer()` decodes a u32 length, bounds-checks the source, allocates a new buffer with `GFP_NOFS`, copies decoded bytes into it, and advances the decode pointer.

## State and Persistence
Buffers are heap objects with kref-managed lifetime. There is no global state or persistence.

## Dependencies and Integration Points
Used by Ceph auth, OSD maps, and other libceph decoders that need refcounted byte vectors. Depends on `linux/ceph/buffer.h`, decode helpers, and libceph `kvmalloc` context.

## Risks
Large decoded lengths can allocate significant memory after only a bounds check against the incoming message. `ceph_decode_buffer()` leaves cleanup to the caller after success and returns `-ENOMEM` or `-EINVAL` on failure. Callers must use `ceph_buffer_put()` or equivalent to release refs.

## Test Signals
Decode zero-length, small, page-sized, and vmalloc-sized buffers; simulate allocation failures; verify kref release under KMEMLEAK; and fuzz truncated length/data combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/ceph_common.c -->
# sources/distributed-fs/ceph-client/net/ceph/ceph_common.c

## Purpose
Provides libceph module initialization, client lifecycle management, mount/session option parsing and printing, fsid handling, compatibility reporting, and common helpers exported to CephFS/RBD.

## Important APIs, Types, and Functions
Important exported APIs include `libceph_compatible()`, `ceph_msg_type_name()`, `ceph_check_fsid()`, `ceph_compare_options()`, `ceph_parse_fsid()`, `ceph_alloc_options()`, `ceph_destroy_options()`, `ceph_parse_mon_ips()`, `ceph_parse_param()`, `ceph_print_client_options()`, `ceph_client_addr()`, `ceph_client_gid()`, `ceph_create_client()`, `ceph_destroy_client()`, `ceph_reset_client_addr()`, `__ceph_open_session()`, `ceph_open_session()`, and `ceph_wait_for_latest_osdmap()`. Module hooks are `init_ceph_lib()` and `exit_ceph_lib()`.

## Control Flow
Options are allocated with defaults, parsed through `fs_parameter_spec` tables, and destroyed by freeing names, keys, monitor addresses, and CRUSH location trees. Secret options either unarmor inline key material or request a `ceph` key from the kernel keyring. Client creation waits for randomness, allocates `struct ceph_client`, sets feature masks, initializes messenger, monitor client, and OSD client. Opening a session starts the monitor session, waits for auth, monmap, and osdmap using `auth_wq` and configured timeout, then initializes debugfs. Destroying a client stops OSD and monitor clients, finalizes messenger, cleans debugfs, destroys options, and frees memory.

Module init sets up debugfs, crypto key type, messenger, and OSD client support in that order; exit reverses those layers after checking Ceph string-table cleanup.

## State and Persistence
Runtime state is held in `struct ceph_options` and `struct ceph_client`. Options contain flags, timeouts in jiffies, monitor addresses, optional key, client name, connection modes, and CRUSH locations. Client state includes messenger instance, monc, osdc, feature bits, auth waitqueue, mount mutex, and fsid. No persistent storage is written.

## Dependencies and Integration Points
Depends on fs parser, keyrings, Ceph crypto, messenger, monitor client, OSD client, debugfs, CRUSH location parsing, IP parsing, namespaces, and feature constants. It is the main libceph module boundary consumed by CephFS and RBD.

## Risks
Option comparison uses a raw memcmp up to `mon_addr`, so struct layout changes must keep comparable fields before that offset. Secret parsing must avoid leaking keys; `secret=<hidden>` is printed. Session opening depends on waitqueue wakeups from monitor/OSD paths and can time out or be interrupted. Init/exit ordering must match dependencies. `ceph_check_fsid()` returns `-1` rather than a conventional negative errno.

## Test Signals
Parse every mount option including negated flags, invalid ranges, fsid strings, monitor IPs, keyring failures, and CRUSH locations. Compare shared versus non-shared client options across namespaces. Create/destroy clients under failure injection at monc/osdc init. Open sessions with successful maps, auth errors, timeout, and signal interruption. Build/load/unload libceph with debugfs, crypto, messenger, and osdc cleanup checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/ceph_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/ceph_hash.c -->
# sources/distributed-fs/ceph-client/net/ceph/ceph_hash.c

## Purpose
Implements Ceph string hash algorithms used by cluster metadata and protocol structures.

## Important APIs, Types, and Functions
Public APIs are `ceph_str_hash_rjenkins()`, `ceph_str_hash_linux()`, `ceph_str_hash()`, and `ceph_str_hash_name()`. The `mix()` macro implements Bob Jenkins' 32-bit mixing routine. Supported algorithm ids are `CEPH_STR_HASH_LINUX` and `CEPH_STR_HASH_RJENKINS`.

## Control Flow
`ceph_str_hash_rjenkins()` consumes input in 12-byte blocks, mixes three 32-bit accumulators, folds remaining bytes with fallthrough cases, mixes again, and returns accumulator `c`. `ceph_str_hash_linux()` applies the historical dcache-style byte loop. `ceph_str_hash()` dispatches by type and returns `-1` cast to unsigned for unknown types. `ceph_str_hash_name()` returns printable names.

## State and Persistence
No mutable state. Hash output stability is part of Ceph's distributed metadata contract.

## Dependencies and Integration Points
Depends on Ceph type constants and exports dispatcher/name functions to other libceph modules.

## Risks
Changing algorithm details would remap Ceph objects or metadata. Unknown hash types returning unsigned `-1` may be a sentinel but should not be used as a valid placement hash. Endianness is fixed by explicit byte assembly in the Jenkins path.

## Test Signals
Known-answer tests for both hash types, unknown-type behavior, empty and short strings, 12-byte boundary lengths, cross-endian consistency, and compatibility with userspace Ceph hash outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/ceph_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/ceph_strings.c -->
# sources/distributed-fs/ceph-client/net/ceph/ceph_strings.c

## Purpose
Maps Ceph numeric protocol constants to readable names for logging, debugging, and option/error messages.

## Important APIs, Types, and Functions
Functions are `ceph_entity_type_name()`, `ceph_auth_proto_name()`, `ceph_con_mode_name()`, `ceph_osd_op_name()`, `ceph_osd_watch_op_name()`, and `ceph_osd_state_name()`. Only `ceph_entity_type_name()` is exported from this file, while the others are used within libceph.

## Control Flow
Each function is a switch statement over Ceph constants. `ceph_osd_op_name()` expands `__CEPH_FORALL_OSD_OPS()` to stay aligned with the central OSD op list.

## State and Persistence
No state. Returned string literals have static lifetime.

## Dependencies and Integration Points
Depends on `linux/ceph/types.h` for constants and module export support. Used by auth, OSD, and debug/logging paths.

## Risks
New protocol constants can print as `???` or `unknown` until the mapping is updated. These helpers are diagnostic only and should not be used for protocol decisions.

## Test Signals
Compile-time coverage when constants are added, unit checks for known names, and log-path tests that confirm unknown values remain safe printable strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/ceph_strings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/cls_lock_client.c -->
# sources/distributed-fs/ceph-client/net/ceph/cls_lock_client.c

## Purpose
Implements kernel client helpers for Ceph RADOS object-class lock operations: acquire, unlock, break, set cookie, query lock info, free decoded lockers, and assert a lock as part of an OSD request.

## Important APIs, Types, and Functions
Exported APIs are `ceph_cls_lock()`, `ceph_cls_unlock()`, `ceph_cls_break_lock()`, `ceph_cls_set_cookie()`, `ceph_cls_lock_info()`, `ceph_free_lockers()`, and `ceph_cls_assert_locked()`. Internal decoders are `decode_locker()` and `decode_lockers()`. It uses `struct ceph_osd_client`, `struct ceph_object_id`, `struct ceph_object_locator`, `struct ceph_locker`, `struct ceph_entity_name`, and OSD class request helpers.

## Control Flow
Each mutating helper computes the encoded request size, rejects payloads over one page, allocates a page with `GFP_NOIO`, starts a versioned encoding block, encodes lock name, type, cookies, tag, description, locker identity, expiration, or flags as required, and calls `ceph_osdc_call()` with class `"lock"` and the relevant method. `ceph_cls_lock_info()` allocates request and reply pages, calls `"get_info"`, then decodes lockers, lock type, and tag from the reply. `ceph_cls_assert_locked()` initializes a class op in an existing OSD request and attaches a one-page encoded assertion payload.

## State and Persistence
The file owns no long-lived state. It allocates transient pages and decoded locker arrays/strings. Lock state itself persists in the RADOS object/class on the Ceph cluster, not in kernel memory.

## Dependencies and Integration Points
Depends on Ceph OSD client calls, class method names, Ceph encoding/decoding helpers, page-vector helpers, and exported lock client headers. It is used by higher-level Ceph clients needing distributed object locks.

## Risks
String lengths are taken with `strlen()`, so inputs must be NUL-terminated. All request payloads must fit in a single page; long descriptions or tags return `-E2BIG`. Decode paths must free partially decoded lockers on error. `decode_locker()` skips description after reading a length and depends on prior bounds checks in decode helpers. Cluster-side method compatibility depends on versioned encoding block layout.

## Test Signals
Exercise each class method against a test cluster, overlong string rejection, allocation failure paths, malformed `get_info` replies, multiple lockers decode/free, assert-locked class op composition inside multi-op requests, shared/exclusive lock types, break-lock target identity, and cookie update semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/cls_lock_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crush/crush.c -->
# sources/distributed-fs/ceph-client/net/ceph/crush/crush.c

## Purpose
Provides common CRUSH map helpers for bucket algorithm naming, bucket item weight lookup, and memory destruction for CRUSH maps, buckets, and rules.

## Important APIs, Types, and Functions
Functions include `crush_bucket_alg_name()`, `crush_get_bucket_item_weight()`, `crush_destroy_bucket_uniform()`, `crush_destroy_bucket_list()`, `crush_destroy_bucket_tree()`, `crush_destroy_bucket_straw()`, `crush_destroy_bucket_straw2()`, `crush_destroy_bucket()`, `crush_destroy()`, and `crush_destroy_rule()`. It handles `struct crush_bucket` and algorithm-specific bucket structs.

## Control Flow
Weight lookup checks index bounds and switches by bucket algorithm to return the correct weight source. Destroy helpers free each algorithm's auxiliary arrays, then the common item array and bucket object. `crush_destroy()` iterates bucket and rule arrays, destroys populated entries, frees arrays, clears kernel-only name/choose-arg tables, and frees the map.

## State and Persistence
No global state. The functions tear down heap state created by CRUSH map decoding. CRUSH maps are in-memory representations of cluster placement data.

## Dependencies and Integration Points
Depends on kernel CRUSH structs and kernel-only cleanup helpers such as `clear_crush_names()` and `clear_choose_args()`. Used by OSD map lifecycle code.

## Risks
Destruction assumes algorithm tags match allocation layout. New bucket algorithms require updates to both weight lookup and cleanup. `crush_get_bucket_item_weight()` returns 0 for unknown algorithms or out-of-range indexes, which can mask invalid maps if callers do not validate earlier.

## Test Signals
Decode and destroy maps containing every bucket algorithm, run KASAN/KMEMLEAK on failure paths, verify weight lookup for each algorithm and out-of-range positions, and test unknown/invalid algorithm handling during map validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crush/crush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crush/crush_ln_table.h -->
# sources/distributed-fs/ceph-client/net/ceph/crush/crush_ln_table.h

## Purpose
Provides fixed-point lookup tables used by CRUSH straw2 selection to approximate logarithms without floating-point arithmetic.

## Important APIs, Types, and Functions
The header defines static arrays `__RH_LH_tbl` and `__LL_tbl`. `__RH_LH_tbl` stores reciprocal/log high-part pairs; `__LL_tbl` stores low-part `log2(1 + k/2^15)` values. There are no functions.

## Control Flow
`mapper.c` includes this header and `crush_ln()` indexes the tables to compute a fixed-point logarithm for straw2 draw values.

## State and Persistence
The tables are static read-only data after compilation. They contain no mutable runtime state.

## Dependencies and Integration Points
Depends on kernel or userspace CRUSH integer type definitions. Its values are part of the deterministic CRUSH placement algorithm and must match userspace Ceph.

## Risks
Any table value change alters straw2 placement results. Because the arrays are `static` in a header, each translation unit including it would get a copy; currently it is included by `mapper.c`. The LGPL comment differs from surrounding GPL-only source and should remain consistent with upstream provenance.

## Test Signals
Known-answer tests for `crush_ln()` and straw2 placement, cross-check kernel versus userspace CRUSH mappings, and table-index boundary tests for hash values near 0 and 0xffff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crush/crush_ln_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crush/hash.c -->
# sources/distributed-fs/ceph-client/net/ceph/crush/hash.c

## Purpose
Implements deterministic CRUSH hash functions used by bucket selection and device-out checks.

## Important APIs, Types, and Functions
Public functions are `crush_hash32()`, `crush_hash32_2()`, `crush_hash32_3()`, `crush_hash32_4()`, `crush_hash32_5()`, and `crush_hash_name()`. Internal functions implement the `CRUSH_HASH_RJENKINS1` variant for one through five 32-bit inputs. `crush_hashmix` is the Jenkins mixing macro and `crush_hash_seed` is the fixed seed.

## Control Flow
Each dispatcher switches on hash type and calls the matching Jenkins function or returns 0 for unknown types. The Jenkins variants combine the fixed seed and arguments, then apply several mixing rounds with constants to produce a 32-bit deterministic result.

## State and Persistence
No mutable state. Hash stability is required for placement consistency.

## Dependencies and Integration Points
Used by `mapper.c` bucket selection, permutation generation, straw/straw2 draws, and `is_out()` probability checks. Must match userspace CRUSH exactly.

## Risks
Unknown hash types silently return 0, which can bias placement if invalid maps pass validation. Any arithmetic or seed change causes cluster-wide remapping. The code relies on unsigned 32-bit wraparound semantics.

## Test Signals
Known-answer vectors for all arities, unknown type behavior, cross-implementation comparison with userspace Ceph, and placement regression tests using real CRUSH maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crush/hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crush/mapper.c -->
# sources/distributed-fs/ceph-client/net/ceph/crush/mapper.c

## Purpose
Implements the core CRUSH placement rule interpreter and bucket-selection algorithms. Given a CRUSH map, rule, input hash value, device weights, and workspace, it deterministically maps objects to OSD/device ids while avoiding out devices and collisions.

## Important APIs, Types, and Functions
Public APIs are `crush_find_rule()`, `crush_init_workspace()`, and `crush_do_rule()`. Bucket algorithms include `bucket_perm_choose()`, `bucket_uniform_choose()`, `bucket_list_choose()`, `bucket_tree_choose()`, `bucket_straw_choose()`, and `bucket_straw2_choose()`. Placement helpers include `crush_bucket_choose()`, `is_out()`, `crush_choose_firstn()`, and `crush_choose_indep()`. Straw2 uses `crush_ln()` and lookup tables from `crush_ln_table.h`. It uses `struct crush_map`, `struct crush_rule`, `struct crush_bucket`, `struct crush_work`, `struct crush_work_bucket`, and optional `struct crush_choose_arg`.

## Control Flow
`crush_find_rule()` scans rules for a ruleset/type/size mask match. `crush_init_workspace()` lays out per-bucket work pointers and permutation arrays inside caller-provided memory; callers must rerun it when map layout changes. `crush_do_rule()` interprets rule steps: TAKE seeds the working set, SET_* steps adjust retry and chooseleaf behavior, CHOOSE/CHOOSELEAF FIRSTN or INDEP expands buckets using the selected algorithm, and EMIT copies working items into the result.

`crush_choose_firstn()` performs depth-first selection for replicas, retrying local bucket choices, fallback permutations, or full descents when items collide or are out. With chooseleaf, it recursively descends to leaves and writes final leaves through `out2`. `crush_choose_indep()` is the positionally stable breadth-first variant, filling undefined slots independently. Bucket selection dispatches by algorithm: uniform uses cached random permutation, list/tree use weight-proportional choices, straw uses straw lengths, and straw2 uses logarithmic draws divided by per-position weights with optional choose args.

## State and Persistence
The mapper is deterministic and owns no global mutable state. Temporary state is in caller-provided workspace and result arrays. `crush_work_bucket` caches permutations per bucket and input `x`. Device out-ness is supplied by the caller's weight vector, with weights below `0x10000` interpreted probabilistically.

## Dependencies and Integration Points
Depends on CRUSH map structures, CRUSH hash functions, fixed-point logarithm tables, and OSD map code that supplies weights, rules, and choose args. Kernel and userspace builds share the same algorithmic source style, so compatibility is critical.

## Risks
Any change affects data placement and can cause large remaps. Workspace sizing/layout must match `map->working_size`; `BUG_ON` catches mismatches. Invalid maps can produce bad bucket ids, empty buckets, unknown algorithms, or unknown hash types; this code often skips or returns fallback items rather than fully validating. Retry parameters strongly influence collision resolution and undersized results. Choose-arg indexing uses `-1 - bucket->id`, so bucket ids must be valid negative ids.

## Test Signals
Use known CRUSH map vectors from userspace Ceph, all bucket algorithms, firstn and indep rules, chooseleaf stable/vary-r modes, local and fallback retries, out-device probabilities, zero-weight devices, empty buckets, choose args with per-position weights and ids, workspace reinitialization after map changes, and result-size truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crush/mapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crypto.c -->
# sources/distributed-fs/ceph-client/net/ceph/crypto.c

## Purpose
Implements libceph cryptographic key handling, Ceph keyring integration, AES-CBC and AES256-KRB5 encryption/decryption wrappers, HMAC support, and registration of the kernel `ceph` key type.

## Important APIs, Types, and Functions
Public APIs are `ceph_crypto_key_prepare()`, `ceph_crypto_key_clone()`, `ceph_crypto_key_decode()`, `ceph_crypto_key_unarmor()`, `ceph_crypto_key_destroy()`, `ceph_crypt()`, `ceph_crypt_data_offset()`, `ceph_crypt_buflen()`, `ceph_hmac_sha256()`, `ceph_crypto_init()`, and `ceph_crypto_shutdown()`. Internal helpers include `set_aes_tfm()`, `set_krb5_tfms()`, `setup_sgtable()`, `teardown_sgtable()`, `ceph_aes_crypt()`, `ceph_krb5_encrypt()`, `ceph_krb5_decrypt()`, and key-type callbacks `ceph_key_preparse()`, `ceph_key_free_preparse()`, `ceph_key_destroy()`.

## Control Flow
Key preparation dispatches by type: none is a no-op, AES allocates `cbc(aes)` and sets the key, AES256KRB5 prepares HMAC state and per-usage AEAD transforms. Key decode reads type, creation timestamp, length, validates `CEPH_MAX_KEY_LEN`, copies key bytes, and zeroes the source. Unarmor base64-decodes a string then decodes a key from the binary payload.

`ceph_crypt()` dispatches encryption/decryption. AES applies PKCS#7-like padding on encrypt, builds an sg table over kmalloc or vmalloc buffers, runs synchronous skcipher CBC with a fixed Ceph IV, and strips padding on decrypt. KRB5 encryption/decryption builds sg tables and calls crypto KRB5 helpers, accounting for a confounder offset and HMAC length. HMAC-SHA256 returns zeros for none/AES and computes real HMAC for AES256KRB5. Module crypto init registers the `ceph` key type; shutdown unregisters it.

## State and Persistence
`struct ceph_crypto_key` owns key bytes and prepared transform pointers. The global `key_type_ceph` is registered during libceph init. Key material is freed with `kfree_sensitive()` and HMAC state is explicitly zeroed. No persistent storage is written.

## Dependencies and Integration Points
Depends on the kernel crypto API, KRB5 crypto helpers, scatterlist helpers, keyring API, Ceph armor/decode helpers, and libceph auth paths. CephX relies on usage-slot ordering when preparing keys.

## Risks
AES uses a fixed IV for protocol compatibility, so callers must understand the security model. `setup_sgtable()` handles vmalloc and linear buffers but returns `-EINVAL` for zero length. AES decrypt validates only padding shape. KRB5 transform preparation has a fixed transform array size; too many usages return `-EINVAL`. Key decode mutates input by zeroing decoded key bytes, so callers must not expect immutable input buffers.

## Test Signals
Decode and unarmor valid/invalid keys, enforce maximum key length, prepare AES and AES256KRB5 keys, encrypt/decrypt round trips over kmalloc and vmalloc buffers, padding edge cases at block boundaries, malformed padding rejection, KRB5 usage-slot bounds, keyring add/request/destroy lifecycle, failure injection for crypto allocation, and secret-zeroing checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crypto.h -->
# sources/distributed-fs/ceph-client/net/ceph/crypto.h

## Purpose
Declares libceph crypto key structures, size limits, cryptographic helper APIs, armor helpers, and crypto module init/shutdown hooks.

## Important APIs, Types, and Functions
Constants are `CEPH_MAX_KEY_LEN` and `CEPH_MAX_CON_SECRET_LEN`. `struct ceph_crypto_key` stores key type, creation time, length, key bytes, and either an AES skcipher transform or AES256-KRB5 HMAC/KRB5 transform state. Declared functions cover key prepare/clone/decode/unarmor/destroy, `ceph_crypt()`, buffer offset/length helpers, `ceph_hmac_sha256()`, `ceph_crypto_init()`, `ceph_crypto_shutdown()`, `ceph_armor()`, and `ceph_unarmor()`.

## Control Flow
No executable flow. The header defines contracts implemented by `crypto.c` and `armor.c`, and consumed by auth and common option parsing.

## State and Persistence
The declared key struct owns sensitive heap state and crypto transforms when instantiated. Callers are responsible for zero-initializing before decode/clone and for `ceph_crypto_key_destroy()` cleanup.

## Dependencies and Integration Points
Depends on SHA-2 helper types, Ceph type definitions, and `struct ceph_buffer`. Included by auth-none/CephX/common crypto users.

## Risks
The KRB5 transform array has three slots, so all usage arrays must fit. Increasing `CEPH_MAX_KEY_LEN` or connection secret length affects protocol validation and stack/user buffers. The union means cleanup must branch on key type correctly.

## Test Signals
Compile all crypto users, static checks for usage array sizes, key lifecycle tests for each key type, and ABI review when changing struct fields or constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/crypto.h -->
