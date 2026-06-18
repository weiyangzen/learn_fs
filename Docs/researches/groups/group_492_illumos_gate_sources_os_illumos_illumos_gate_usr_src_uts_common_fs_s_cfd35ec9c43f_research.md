# Group Research: group_492_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_cfd35ec9c43f

Scope: `Docs/research_subset_a.md`

Files researched:
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_crypt.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_negctx.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.h`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_dev.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_iod.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_osdep.h`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.h`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.h`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_sign.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_smb.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_subr.h`

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_crypt.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_crypt.c

## Purpose
Implements SMB3 message privacy for the illumos SMB client: crypto mechanism selection, encryption/decryption key derivation after session setup, and in-place SMB3 transform-header encryption/decryption of STREAMS `mblk_t` message chains.

## Key Elements
`nsmb_crypt_init_mech` selects the kernel crypto mechanism for the negotiated cipher, supporting AES-128/256 GCM and AES-128/256 CCM. `nsmb_crypt_fini_mech` clears the stored mechanism state. `nsmb_crypt_init_keys` derives SMB3 client-to-server and server-to-client encryption keys from the session key using SMB KDF labels. SMB 3.1.1 derives keys with preauthentication hash context and supports AES-256 by using the full session key; older SMB3 dialects derive AES-128 CCM keys with the legacy `SMB2AESCCM` labels.

`smb3_msg_encrypt` prepends a 52-byte SMB3 transform header, generates a serialized nonce from per-VC counters protected by `iod_rqlock`, authenticates transform-header fields after the signature, and encrypts the original SMB2 payload in place. It temporarily appends the transform header signature field to the message chain so the crypto helper can write the authentication tag there, then restores the header and links it before the encrypted body.

`smb3_msg_decrypt` splits and validates the transform header, checks the `0xFD SMB` signature, session ID, flags, and body length, trims excess transport padding, configures GCM or CCM authentication parameters from the transform header, temporarily appends the signature/tag region to the ciphertext chain, decrypts in place, then discards the transform header and returns the plaintext body chain.

## Dependencies
Depends on SMB2/SMB3 protocol constants, `smb_vc` negotiated state and session keys, STREAMS message-block helpers, `mbchain`/`mdchain`, illumos random bytes, and `nsmb_kcrypt` AES-GCM/AES-CCM/KDF helpers. The send side assumes the caller holds `vcp->iod_rqlock` as writer so nonce counters are serialized.

## Behavior/Risks
Nonce uniqueness is critical; callers must preserve the locking assumption around `vc3_nonce_low/high`. Encryption is disabled unless the negotiated capabilities include SMB2 encryption and derived keys are present. Transform header parsing is intentionally strict about signature, session ID, flags, and length, so malformed or cross-session encrypted replies fail before decryption. The temporary header/body chain manipulation is sensitive to pointer restoration and error cleanup; leaks or corrupted `b_rptr`/`b_wptr` values would break subsequent transport parsing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_negctx.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_negctx.c

## Purpose
Encodes and decodes SMB 3.1.1 negotiate contexts for preauthentication integrity and encryption cipher negotiation.

## Key Elements
`smb3_negctxs_encode` aligns the negotiate-context section to 8 bytes and emits two contexts: required `SMB2_PREAUTH_INTEGRITY_CAPABILITIES` with SHA-512 and a random 32-byte salt, and `SMB2_ENCRYPTION_CAPABILITIES` listing enabled ciphers in preference order. The tunable `nsmb_ciphers_enabled` bitmask allows testing with selected ciphers disabled; by default it advertises all four supported AES ciphers, preferring AES-256 and GCM over CCM.

`smb3_negctxs_decode` parses the server's SMB 3.1.1 negotiate-context response, enforcing count bounds, 8-byte context alignment, per-context length sanity, exactly one preauth context, exactly one SHA-512 hash selection, and at most one encryption context. It skips unknown context types and context padding but rejects duplicate required/recognized contexts and invalid lengths. The selected preauth hash ID and encryption cipher are stored in the VC as `vc3_preauth_hashid` and `vc3_enc_cipherid`.

## Dependencies
Uses `mbchain` and `mdchain` binary encoders/decoders, SMB2/SMB3 protocol constants, random salt generation, DTrace probes, SHA-512 definitions from `nsmb_kcrypt`, and negotiated VC state in `smb_conn.h`.

## Behavior/Risks
This is a negotiation trust boundary. Bad alignment, excessive context lengths, missing or duplicate preauth contexts, unsupported preauth hash IDs, and invalid encryption cipher counts abort negotiation. Lack of an encryption context or no acceptable cipher is not fatal by itself; the VC records `SMB3_CIPHER_NONE`, and later tree connect or encrypted-message requirements determine whether the session can continue. Edits must preserve padding/offset accounting because the SMB2 negotiate-context list is 8-byte aligned and may include unknown future contexts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb3_negctx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.c

## Purpose
Implements the SMB client connection object hierarchy: global session manager, virtual circuits/sessions, tree shares, file handles, reference counting, object teardown, reconnect invalidation, and zone shutdown handling.

## Key Elements
The common `smb_connobj` layer provides lock-protected use counts, parent/child lists, `SMBO_GONE` lifecycle state, and `co_gone`/`co_free` callbacks. `smb_co_rele` performs the core teardown sequence: mark gone, call the disconnect callback once, unlink from the parent list, free the object, then release the parent hold. `smb_sm_init`, `smb_sm_idle`, and `smb_sm_done` manage the global VC list and prevent module unload while active VCs remain.

VC support includes `smb_vc_create`, `smb_vc_findcreate`, `smb_vc_hold/rele/kill`, transport allocation, state/CV initialization, request-list initialization, credential/session identity copying, and cleanup of transport state, signing keys, session keys, crypto mechanisms, locks, and CVs. VC matching is zone- and owner-scoped and compares server address, user, and domain case-insensitively.

Share support includes `smb_share_findcreate`, `smb_share_create`, `smb_share_tcon`, `smb_share_invalidate`, and share hold/release/kill wrappers. `smb_share_tcon` serializes concurrent tree-connect attempts with `SMBS_RECONNECTING`, waits interruptibly for another thread's tree connect, and invokes SMB1 or SMB2 tree connect depending on the VC. Share teardown shuts down outstanding share requests and sends tree disconnect.

File-handle support creates handles under shares, marks them valid after successful open, records the VC generation used to open them, and closes them during teardown only when still valid for the current share generation. The zone callbacks kill VCs during zone shutdown and report lingering VCs at zone destroy.

## Dependencies
Depends on illumos locks/CVs/zones/credentials, STREAMS transport descriptors, SMB1/SMB2 protocol helpers, `smb_iod` connection teardown, tree connect/disconnect helpers, file close helpers, UTF-8 case-insensitive comparison, and the password/keychain interface for module lifecycle coordination.

## Behavior/Risks
The parent/child reference model is central to preventing use-after-free; callers rely on external holds from device instances or mounted shares rather than per-request VC holds. `SMBO_GONE` blocks new references and ensures disconnect callbacks run once, so lifecycle flag changes are high risk. Share and file-handle generation checks intentionally make handles stale across reconnect because durable handles are not implemented. Zone shutdown kills connections asynchronously; zone destroy only diagnoses references that should already have been released.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.h

## Purpose
Defines the primary SMB client connection, session, share, file-handle, request-list, and device-instance data structures and declares the connection, IOD, user ioctl, and file-handle APIs used across `netsmb`.

## Key Elements
Defines shared flags for object lifecycle (`SMBO_GONE`), VC behavior (`SMBV_UNICODE`, `SMBV_EXT_SEC`, `SMBV_SIGNING`, `SMBV_SMB2`, file-ID support, write-through quirks), share connection state, and file-handle validity. `smb_connobj` is the common embedded object for the hierarchy `SMBL_SM -> SMBL_VC -> SMBL_SHARE -> SMBL_FH`, with locks, use count, parent pointer, child SLIST, and callbacks.

`smb_sopt` stores negotiated SMB1 and SMB2+ server parameters, including dialect, signing/security mode, max mux, transfer sizes, capabilities, session flags, and server GUID. `smb_iods` stores SMB1 header defaults and signing sequence state. `smb_vc` combines connection identity, transport state, SMB1/2/3 negotiated state, signing/preauth/encryption key material, SMB2 message ID credit windows, IOD thread state, active request queue, session work buffers, and copied session identity.

`smb_share` represents a tree connection with TID/tree ID, share flags/capabilities, reconnect CVs, VC generation, and ioctl-provided share identity. `smb_fh` represents an SMB1 FID or SMB2 durable/volatile FID pair plus granted rights and VC generation. `smb_dev` represents one `/dev/nsmb` open instance and holds VC/share/FH references plus zone and ioctl serialization state.

## Dependencies
Includes illumos locking, queue, UIO, device, and crypto headers plus `smb_dev.h` user-visible ioctl structures. Declares APIs implemented in `smb_dev.c`, `smb_usr.c`, `smb_iod.c`, `smb_conn.c`, and protocol helpers.

## Behavior/Risks
This header is the ABI-like internal contract for the SMB client stack. Structure field changes affect ioctl paths, IOD reconnect logic, SMB2 credit accounting, SMB3 cryptography, mounted smbfs shares, and debug tooling. Several macros alias fields embedded in ioctl/session structures, so renames or layout changes can silently affect multiple modules. Key material is stored directly in `smb_vc`; teardown paths must continue clearing/freeing it carefully.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_dev.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_dev.c

## Purpose
Implements the `/dev/nsmb` pseudo-device driver used by userland SMB tooling and `smbiod` to create sessions, issue ioctls, duplicate device state, and hand mounted smbfs a referenced share.

## Key Elements
Module initialization sets up soft-state storage, device locks, the connection manager, the password keychain, and zone callbacks, then installs the kernel driver. `_fini` refuses unload while active VCs or stored password hashes remain, removes the module, deletes the zone key, and tears down shared state.

The kernel driver exposes clone open/close/ioctl operations. `nsmb_open` allocates a unique minor soft-state instance, marks it open, records the caller zone, and initializes the instance lock. `nsmb_ioctl` validates the soft-state instance, open flag, and same-zone access, then dispatches to `smb_usr_ioctl`. `nsmb_close` releases attached file handle, share, and VC references; if the instance belongs to an IOD, closing it disconnects the VC because no reader remains.

Attach/detach create/remove the `nsmb` character minor node and discover major device numbers for TCP/TCP6 transport opens. Non-kernel wrappers map the same open/close/ioctl behavior for `libfknsmb`. `smb_usr_dup_dev` copies VC/share references from another nsmb file descriptor, incrementing reference counts. `smb_dev2share` validates an nsmb descriptor and returns a held share pointer for mount setup.

## Dependencies
Depends on illumos driver/module/DDI soft-state APIs, zones, credentials, file descriptor lookup, vnode device numbers, transport major lookup, connection/reference APIs, password-keychain lifecycle, and user ioctl dispatcher code in `smb_usr.c`.

## Behavior/Risks
This file is a privilege and namespace boundary for SMB client sessions. Zone checks prevent cross-zone ioctl access to device instances. Clone minor allocation is protected by `dev_lck`; stale soft-state or double-close mistakes would corrupt reference ownership. `smb_usr_dup_dev` and `smb_dev2share` must hold returned VC/share objects because device close can otherwise release them underneath callers. Module unload depends on both connection and password-keychain idleness.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_iod.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_iod.c

## Purpose
Implements the SMB client IOD coordination layer: connection/reconnect state machine, transport connect setup, SMB1/SMB2 request queueing and sending, receive loop, reply matching, SMB2 credit accounting, SMB3 decryption/encryption integration, timeout handling, idle teardown, and share disconnect notifications.

## Key Elements
The IOD model uses one userland `smbiod` agent per VC. Userland drives connect, negotiate, authentication continuation, and then enters `smb_iod_vc_work`, where the kernel records the session key, initializes signing and SMB3 encryption keys, marks the VC active, and runs the receive loop. State transitions are recorded through `smb_iod_newstate` and coordinated with `vc_statechg`, `iod_idle`, and `iod_muxwait`.

Request completion is centralized in `smb_iod_rqprocessed(_LH)`, which records local error/status flags, bumps the reply generation, marks the request notified, and broadcasts its condition variable. `smb_iod_invrq` wakes all outstanding requests with `ENOTCONN` and `SMBR_RESTART` after disconnect/reconnect transitions. `smb_iod_shutdown_share` wakes active requests for a forced-unmounted share with `EIO`.

`smb1_iod_addrq` implements SMB1 mux-limit control using `iod_muxcnt` and `vc_maxmux`, assigns MIDs and signing sequence numbers, queues the request, fills/signs the header, and sends it. `smb2_iod_addrq` implements SMB2 credit-window control using `vc2_next_message_id` and `vc2_limit_message_id`, assigns message IDs across compounded requests, queues every compound member, and sends the compound chain. Both leave one slot/credit for internal requests where possible.

`smb1_iod_sendrq` fills SMB1 headers, signs if required, duplicates the message, and sends through the transport. `smb2_iod_sendrq` determines whether encryption is required by session or share flags, fills/signs headers for top and compounded requests, updates SMB 3.1.1 preauth hashes for negotiate/session setup, builds a compound mblk chain, encrypts with `smb3_msg_encrypt` when needed, and sends it.

`smb_iod_recvall` is the reader loop. It receives NetBIOS/TCP messages, logs server-not-responding after idle ticks with pending requests, sends an echo after continued silence, triggers reconnect after further silence, drops idle connections after the keepalive period if the IOD owns the last reference, and dispatches replies to SMB1 or SMB2 processors. `smb1_iod_process` validates SMB1 headers or the special SMB1-to-SMB2 negotiate response and matches replies by MID. `smb2_iod_process` decrypts SMB3 transform messages, splits compound replies, applies SMB2 credit grants immediately, handles async interim `STATUS_PENDING` responses, and matches final replies by message ID.

Connection-control entry points include `nsmb_iod_connect`, which rebuilds the transport endpoint, sets socket options, binds, connects, and moves to CONNECTED; `nsmb_iod_negotiate`, which resets negotiated state and keys, performs SMB1-to-SMB2 negotiation as needed, then SMB2 negotiate when selected; `nsmb_iod_ssnsetup`, which advances AUTHCONT/AUTHOK/AUTHFAIL based on session setup status; `smb_iod_vc_idle`, which waits for reuse or last-reference destruction; `smb_iod_vc_rcfail`, which throttles failed reconnects and transitions back toward IDLE; and `smb_iod_reconnect`, which requests reconnect and waits for ACTIVE or failure.

## Dependencies
Depends on SMB transport abstraction, TCP transport options, SMB1/SMB2 request builders and parsers, SMB2 compound and signing helpers, SMB3 encryption/decryption/preauth helpers, connection/share structures, STREAMS message manipulation, illumos thread/CV/rwlock/time/zone primitives, DTrace probes, and smbfs callback hooks installed via `smb_fscb_set`.

## Behavior/Risks
This is the highest-concurrency file in the group. `iod_rqlock` protects the active request queue, SMB2 credit/message-ID state, SMB1 mux count, and SMB3 nonce serialization during send; request locks protect per-request completion state. Wait paths must never block the IOD reader thread except through the internal polling variant. Timeout behavior deliberately avoids interrupting sends/receives for operations that could leak server-side FIDs or TIDs if a successful reply is missed. SMB2 credit updates happen before request wakeup, so malformed credit grants can affect sender admission. Reconnect and idle transitions must preserve share invalidation, request wakeups, and generation increments because open handles are not durable.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_iod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_osdep.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_osdep.h

## Purpose
Provides small OS-compatibility definitions inherited from Apple/BSD-origin netsmb code so the illumos SMB client can use expected type names, allocation flags, user-address casts, Unicode conversion flags, and timespec helpers.

## Key Elements
Defines compatibility macros such as `PRIVSYM`, `min`, `CAST_DOWN`, `USER_ADDR_NULL`, and `CAST_USER_ADDR_T`. Provides BSD-style malloc flag names (`M_WAITOK`, `M_NOWAIT`, `M_ZERO`) and UTF/uconv flag constants. Declares `uconv_u8tou16` and aliases legacy integer/user pointer types such as `u_int64_t`, `user_addr_t`, `user_size_t`, and `c_caddr_t`.

The header also provides `timespeccmp`, `timespecadd`, and `timespecsub` macros and a fake-kernel `ddi_get_cred()` mapping.

## Dependencies
Depends on basic illumos integer, size, ssize, credential, and Unicode conversion types being available from surrounding includes.

## Behavior/Risks
This is compatibility glue, not protocol logic. Macro definitions can conflict with platform headers if included in the wrong order or if illumos headers later add equivalent definitions. The timespec arithmetic macros evaluate arguments multiple times and should be used only with simple lvalues.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_osdep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.c

## Purpose
Implements an in-kernel SMB password-hash keychain using an AVL tree keyed by local UID, zone ID, SMB domain/server name, and SMB username.

## Key Elements
The global `smb_ptd` AVL tree stores `smb_passid_t` nodes containing owner UID, zone, server/domain string, username string, LM hash, and NT hash. `smb_pkey_cmp` orders entries by UID, zone, server/domain, then username, with case-insensitive Unicode comparison for strings. `smb_pkey_init`, `smb_pkey_fini`, and `smb_pkey_idle` initialize/destroy the tree and prevent driver unload while hashes remain stored.

`smb_pkey_add` resolves `pk_uid` of `-1` to the caller's real UID or checks privilege for another UID, duplicates the domain/user strings, copies supplied hashes, deletes any existing matching entry, and inserts the new node. `smb_pkey_del` removes a single matching entry. `smb_pkey_deluid` removes all entries for a UID, or all entries when passed `(uid_t)-1`, after a policy check. `smb_pkey_check` looks up an entry and copies only LM/NT hashes back into the ioctl structure.

`smb_pkey_ioctl` dispatches `SMBIOC_PK_ADD`, `SMBIOC_PK_DEL`, `SMBIOC_PK_CHK`, `SMBIOC_PK_DEL_OWNER`, and `SMBIOC_PK_DEL_EVERYONE`, performing copyin/copyout and ensuring string buffers are nul-terminated before use.

## Dependencies
Depends on illumos AVL APIs, kernel memory allocation, credentials and `secpolicy_smbfs_login`, zones, UTF-8 comparison, SMB ioctl structures from `smb_dev.h`, and string allocation helpers.

## Behavior/Risks
Stored credentials are hashes rather than plaintext passwords, but they remain sensitive kernel memory and are intentionally never copied to userland except through the hash-check ioctl path. The tree is zone-scoped as part of the key to avoid cross-zone credential reuse. `smb_pkey_add` has a noted race-prone pattern where it checks and deletes outside one AVL critical section; current locking still protects tree operations individually, but changing this path should make lookup/remove/insert atomic. Unload depends on the tree being empty.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.h

## Purpose
Declares the SMB password-hash keychain data structure and lifecycle functions used by the nsmb driver.

## Key Elements
Defines `smb_passid_t`, the AVL-tree node containing UID, zone ID, server/domain string, username string, and fixed-size LM/NT hash buffers. The comment notes the structure is exposed here mainly so the mdb module can inspect it; otherwise it could be private to `smb_pass.c`.

Declares `smb_pkey_init`, `smb_pkey_fini`, and `smb_pkey_idle`, which are called from driver initialization, finalization, and unload-idle checks.

## Dependencies
Includes illumos AVL definitions and SMB ioctl constants/hash sizes from `smb_dev.h`.

## Behavior/Risks
Because this header exposes credential-cache internals for debugging, structure layout changes can affect mdb/debug tooling as well as the implementation. The stored hash buffers are sensitive and require teardown paths to keep freeing nodes consistently.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.c

## Purpose
Implements SMB request object lifecycle, SMB1 request header construction and reply parsing, simple request/reply execution, SMB1 transaction/transaction2/NT transaction packetization and multi-reply reassembly, and named-pipe transaction helper support.

## Key Elements
`smb_rq_alloc`, `smb_rq_init`, `smb_rq_new`, and `smb_rq_done` manage request objects, embedded request/reply chains, locks, CVs, and protocol-specific header reservations. Requests copy VC/share pointers from an existing held connection object but do not take their own VC holds; callers are responsible for holding the layer through device or mount ownership.

`smb_rq_fillhdr` rewrites the reserved SMB1 header with command, flags, UID, TID, PID, and MID just before send. `smb_rq_wstart/wend` and `smb_rq_bstart/bend` reserve and later fill SMB1 word-count and byte-count fields. `smb_rq_simple_timed` enqueues a normal SMB1 request, waits for a reply, and optionally retries only when the request is marked restartable and retry budget remains. `smb_rq_internal` is the IOD-thread/internal variant that bypasses reconnect logic and returns raw NT status.

`smb_rq_enqueue` handles SMB1 reconnect/tree-connect prerequisites, fills request UID/TID, and submits to the IOD. `smb_rq_reply` waits via the IOD, verifies SMB1 signing when required, parses the SMB header, maps DOS or NT status to errno, and treats `NT_STATUS_BUFFER_OVERFLOW` as nonfatal `SMBR_MOREDATA`. `smb_rq_parsehdr` also detects the special SMB1 negotiate request receiving an SMB2 response and returns `EPROTO` for the negotiate handler.

Transaction support includes `smb_t2_init/done/request`, `smb_nt_init/done/request`, `smb_t2_request_int`, `smb_nt_request_int`, `smb_t2_reply`, and `smb_nt_reply`. These routines fragment large parameter/data payloads across primary and secondary SMB1 transaction requests, use fixed alignment calculations and negotiated `vc_txmax`, collect multi-packet replies into separate parameter/data mdchains, and reject misordered parameter/data fragments. `smb_t2_xnp` wraps a named-pipe transaction and transfers ownership of input/output message chains.

## Dependencies
Depends on connection objects, IOD queueing/wait functions, SMB1 signing verification, SMB status mapping helpers, `mbchain`/`mdchain` and STREAMS mblk operations, SMB1 transaction constants, DTrace probes, and SMB2 negotiate parser hooks.

## Behavior/Risks
The request layer assumes the caller owns the lifetime of the VC/share, so invalid reference discipline outside this file can produce stale pointers. SMB is not safely restartable for most operations; `SMBMAXRESTARTS` is zero to avoid duplicating server-side effects. Multi-packet transaction code is offset/alignment sensitive and intentionally cannot handle misordered fragments despite the protocol allowing them. Operations that could leak server resources set no-interrupt flags in higher-level code so successful replies are not missed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.h

## Purpose
Defines SMB request, transaction2, and NT transaction data structures, request state/flag constants, and request/transaction API declarations.

## Key Elements
Request flags cover allocation, sent state, restartability, interrupt behavior, multi-packet transactions, internal IOD requests, send/receive waiting, no-reconnect requests, more-data status, compound SMB2 requests, async replies, reconnect detection, and encrypted replies. `enum smbrq_state` tracks request lifecycle from not sent through notified.

`struct smb_rq` contains queue linkage, lock/CV, VC/share/owner pointers, SMB1 header fields, SMB2 request fields, compound linkage, message IDs, request and reply chains, credentials, timeout/retry state, local and protocol errors, parsed SMB1 reply fields, and parsed SMB2 reply metadata. `struct smb_t2rq` and `struct smb_ntrq` hold SMB1 transaction and NT transaction setup/parameter/data chains, limits, source layer, current request pointer, share pointer, and preserved raw error details.

The header declares request allocation/init/done, header filling, word/byte count helpers, simple/internal execution, SMB1-to-SMB2 negotiate response parsing, transaction allocation/init/done/request routines, and named-pipe transaction helper `smb_t2_xnp`.

## Dependencies
Includes `mchain.h`, queue definitions, and forward declarations for SMB connection/request structures. Consumers depend on IOD and protocol modules implementing the declared APIs.

## Behavior/Risks
The structure layout is shared across IOD, SMB1 helpers, SMB2 helpers, signing, encryption, and user ioctl paths. Flag semantics are subtle: no-interrupt flags protect server resource accounting, internal requests avoid reconnect recursion, and multi-packet requests remain queued across multiple replies. Compound SMB2 requests require correct linkage and credit/message-ID accounting by the IOD.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_sign.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_sign.c

## Purpose
Implements SMB1 message signing for integrity protection using MD5 over the MAC key, SMB header with sequence number, and message body.

## Key Elements
`smb_sign_init` obtains the MD5 mechanism, copies the SMB1 session key into the VC MAC key buffer, and initializes the SMB1 signing sequence number to 2 after session setup. `smb_compute_MAC` digests the MAC key, an aligned copy of the SMB header with the signature field replaced by the sequence number and zero, and the remainder of the message chain, then returns the first 8 bytes of the MD5 digest as the SMB signature.

`smb_rq_sign` writes either the computed signature into the SMB1 header or the special fake signature value used before SPNEGO/NTLMSSP has produced a MAC key. `smb_rq_verify` recomputes the expected reply signature from `sr_rseqno`, compares it with the header signature, logs failures, and in debug builds can test nearby sequence numbers using `nsmb_signing_fudge`.

## Dependencies
Uses `nsmb_kcrypt` MD5 helpers, VC signing key state, SMB1 request/reply chains, STREAMS mblk traversal, SMB header constants, and debug/error logging helpers.

## Behavior/Risks
Signing sequence numbers must be assigned consistently in the IOD (`sr_seqno` for request and `sr_rseqno` for reply) or all replies fail verification. The code assumes the first mblk contains a contiguous SMB header. Returning success when no MAC key is present allows negotiation/authentication phases to proceed, but once signing is active a bad signature returns `EBADRPC`. Any change to header offsets or sequence handling can break interoperability with SMB1 servers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_sign.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_smb.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_smb.c

## Purpose
Implements core SMB1 protocol operations used by the illumos SMB client: negotiate, session setup, logoff, tree connect/disconnect, NT create, close, print-job open/close, readx/writex, and echo.

## Key Elements
`smb_smb_negotiate` sends an SMB1 negotiate request with NT LM dialects and optionally the magic SMB2 dialect, initializes header flags, decodes server capabilities, determines whether signing is required/enabled, negotiates Unicode and NT status behavior, requires extended security, returns the server security blob to userland authentication buffers, clamps max mux/VC/transfer values, and handles the SMB1-to-SMB2 negotiate response via `smb2_parse_smb1nego_resp`.

`smb_smb_ssnsetup` sends extended-security `SMB_COM_SESSION_SETUP_ANDX` with the userland-provided security blob, records the SMB UID, maps `MORE_PROCESSING_REQUIRED` to `EINPROGRESS`, and returns the next security blob to userland. `smb_smb_logoff` sends logoff with a short no-reconnect timeout.

`smb_smb_treeconnect` builds a UNC path from server/share names, sends `TREE_CONNECT_ANDX` as a VC-level request, includes the share password and service type, uses no-interrupt receive to avoid leaking TIDs, parses returned type/options, and marks the share connected with current VC generation. `smb_smb_treedisconnect` sends a short no-reconnect tree disconnect and clears the TID.

`smb1_smb_ntcreate` sends `NT_CREATE_ANDX`, transfers a prepared path mbchain into the request, parses the returned FID, create action, timestamps, attributes, allocation size, and EOF size. `smb1_smb_close`, print-job open/close, `smb_smb_readx`, and `smb_smb_writex` implement SMB1 file close, printer file operations, large offset reads, and writes. `smb_smb_echo` is an internal IOD echo request used to probe unresponsive connections.

## Dependencies
Depends on request-layer helpers, SMB1 constants, SMB2 negotiate fallback hooks, string encoding helpers, time conversion helpers, SMB status/error mapping, connection/share/file-handle structures, UIO copy helpers, and transport/reconnect behavior provided by the IOD.

## Behavior/Risks
Negotiation policy is security-sensitive: local signing requirements can abort connections, anonymous sessions disable signing, and extended security is mandatory in this implementation. Tree connect and open operations use no-interrupt receive to avoid server-side resource leaks if a successful response is missed. Transfer size calculations are conservative and tied to legacy SMB1 server behavior. The SMB1-to-SMB2 negotiate path is unusual by design and depends on `smb_rq_parsehdr` returning `EPROTO` only for negotiate.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_smb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_subr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_subr.h

## Purpose
Declares shared SMB client utility types, logging macros, timeout tunables, credential helpers, string/time/error conversion helpers, signing/encryption APIs, and SMB1/SMB2/SMB3 protocol operation entry points.

## Key Elements
Provides logging macros (`SMBERROR`, `SMBPANIC`, `SMBSDEBUG`, `SMBIODEBUG`, `NBDEBUG`) built on `smb_errmsg`, debug-entry handling, Unicode type aliases, and `smbfattr_t`, the native-endian file attribute bundle used by create/query paths.

Declares global timeout tunables for SMB1 and SMB2 operations, transport device globals, credential lifecycle helpers, DOS/NT status mapping helpers, SMB string encode/decode routines, socket-address helpers, SMB1 and SMB2 signing initialization/sign/verify helpers, MAC-key derivation helpers, SMB3 crypto mechanism/key/message helpers, SMB1 protocol operations, SMB2 protocol operations, SMB2 IOCTL/read/write/create/close operations, SMB3 preauth and negotiate-context helpers, and SMB time conversion routines.

## Dependencies
Includes kernel cmn_err/lock/note headers, `mchain.h`, and `smb_conn.h`. It acts as the common include surface for many `netsmb` C files.

## Behavior/Risks
This header is the cross-module contract for the SMB client protocol stack. Prototype or type changes ripple through SMB1, SMB2, SMB3 crypto, request, user ioctl, and smbfs mount code. Timeout variables are externally tunable and affect I/O behavior. The declared signing/encryption helpers encode security-critical sequencing and must remain paired with the IOD send/receive paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_subr.h -->