# subset-b-005762 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smb2status.h -->
# sources/distributed-fs/ceph-client/fs/smb/common/smb2status.h

Purpose: provides the shared SMB2/SMB3 NTSTATUS namespace used by the SMB client/server code to place Windows protocol status values on the wire and to support generated status-to-POSIX error mapping. The file is a protocol constant table, sourced from MS-ERREF, not an executable module.

Important APIs/types/functions: `struct ntstatus` describes the severity/facility/code shape of an NTSTATUS value. `STATUS_SEVERITY_*` constants expose success, informational, warning, and error severity encodings. The bulk of the file is `#define STATUS_*`, `DBG_*`, `RPC_NT_*`, `EPT_NT_*`, and related facility-specific constants as little-endian `__le32` values, with trailing comments naming the Linux errno intended for `smb2_error_map_table` generation. High-use statuses include `STATUS_SUCCESS`, `STATUS_PENDING`, `STATUS_MORE_PROCESSING_REQUIRED`, `STATUS_ACCESS_DENIED`, `STATUS_OBJECT_NAME_NOT_FOUND`, `STATUS_OBJECT_NAME_COLLISION`, `STATUS_INVALID_PARAMETER`, `STATUS_NOT_SUPPORTED`, `STATUS_NETWORK_NAME_DELETED`, and the SMB-specific `STATUS_SMB_NO_PREAUTH_INTEGRITY_HASH_OVERLAP`.

Control flow: there is no runtime control flow in this header. Protocol code includes it and writes these little-endian constants directly into SMB2 headers or compares received status fields against them. The comments are part of a tooling contract: mapping generation reads the status definitions and the annotated POSIX errno comments to build lookup tables elsewhere.

State and persistence behavior: there is no mutable state or persistence. The constants are compile-time ABI data. Because the values are little-endian expressions, consumers should avoid rewrapping them with host-endian conversions except when explicitly comparing numeric CPU-order values.

Dependencies and integration points: depends on Linux endian helper macros and integer types through its includers. It integrates with SMB2 response encoding, error conversion, client/server status handling, DCE/RPC named-pipe status propagation, and any generator that builds `smb2_error_map_table` from the comments.

Risks: mistakes in numeric values or endian form produce wire-incompatible SMB errors. Mistakes in the errno comments can silently degrade generated POSIX mappings even though the C compiler sees only comments. Duplicate or rarely used facility values are intentionally preserved from Microsoft references; cleanup that deduplicates names or rewrites spelling can break compatibility with external specifications. Adding a status without a sensible POSIX comment risks defaulting to overly generic `-EIO` behavior.

Test signals: useful signals are SMB2 error-path interoperability tests for open/create/delete/rename/share conflicts, authentication failures, DFS/referral errors, lease/oplock transitions, encrypted-session negotiation failures, and generated status-to-errno table diffs. Compile-time coverage should catch missing macros used by protocol code, but semantic coverage requires comparing wire statuses against Windows/Samba expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smb2status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smbacl.h -->
# sources/distributed-fs/ceph-client/fs/smb/common/smbacl.h

Purpose: defines shared SMB/CIFS security descriptor, SID, ACL, and ACE wire structures plus constants for ACE types and inheritance/audit flags. It is used by SMB client and server code that translates between Windows security descriptors and Linux ownership/mode/ACL state.

Important APIs/types/functions: constants include `NUM_AUTHS`, `SID_MAX_SUB_AUTHORITIES`, many MS-DTYP ACE type values, ACE flags such as `OBJECT_INHERIT_ACE` and `INHERITED_ACE`, SID string sizing macros, and SID role identifiers such as `SIDOWNER`, `SIDGROUP`, `SIDUNIX_USER`, and `SIDNFS_MODE`. The key packed wire structs are `struct smb_ntsd` for a self-relative NT security descriptor, `struct smb_sid`, `struct smb_acl`, and `struct smb_ace`.

Control flow: there is no executable flow. Consumers parse a security descriptor by reading `struct smb_ntsd`, using the owner/group/SACL/DACL offsets to locate `struct smb_sid` and `struct smb_acl`, and then iterating `struct smb_ace` entries according to the ACL header's `num_aces` and each ACE's `size`.

State and persistence behavior: the header defines transient wire formats. Security information may persist later as Linux ACLs, modes, xattrs, or filesystem metadata, but this file itself owns no state. The packed layout and little-endian fields are the persistence-sensitive pieces.

Dependencies and integration points: integrates with KSMBD ACL handling, CIFS ACL handling, SMB xattr storage for NT security descriptors, and ID/SID mapping code. It depends on Linux fixed-width and endian integer types and the protocol guarantee that SID subauthorities are bounded by `SID_MAX_SUB_AUTHORITIES`.

Risks: the variable-length `sub_auth[num_subauth]` and ACE `size` fields require strict bounds checks in consumers; trusting the packed struct size alone can overread malformed client data. SID string sizing must stay aligned with conversion helpers to avoid truncation. Adding unsupported ACE types without explicit handling can accidentally grant or drop access.

Test signals: exercise parsing and encoding of owner/group SIDs, DACLs with allow/deny entries, inherited ACE flags, oversized or malformed SID subauthority counts, ACLs with unknown ACE types, and round trips through SMB create/get-security/set-security paths with xattr-backed ACL storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smbacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smbfsctl.h -->
# sources/distributed-fs/ceph-client/fs/smb/common/smbfsctl.h

Purpose: centralizes SMB/CIFS/SMB2 FSCTL and IOCTL protocol constants shared by client and server code. These values identify remote filesystem-control operations, named-pipe controls, server-side copy/offload operations, reparse tags, and flags used in SMB2 IOCTL packets.

Important APIs/types/functions: the header defines bit-field masks for FSCTL device, access, function, and method components; many `FSCTL_*` codes including DFS referrals, oplock requests, reparse point management, sparse/zero data, snapshot enumeration, resume keys, `FSCTL_VALIDATE_NEGOTIATE_INFO`, copychunk, and network-interface query; reparse tags such as `IO_REPARSE_TAG_SYMLINK`, `IO_REPARSE_TAG_NFS`, and WSL tags; `IS_REPARSE_TAG_NAME_SURROGATE(tag)`; and `SMB2_0_IOCTL_IS_FSCTL`.

Control flow: there is no local execution. SMB2 IOCTL handlers dispatch on the `CtlCode` field using these constants. Reparse-aware paths use the tag definitions and name-surrogate macro to decide whether an object is a link-like namespace substitution or an application-specific reparse object.

State and persistence behavior: no mutable state is present. Reparse tag values may be persisted in filesystem xattrs or reparse buffers by consumers, so the numeric constants are a wire/storage ABI.

Dependencies and integration points: integrates with SMB2 IOCTL request handling, DFS support, named pipe forwarding, server-side copy, durable/resilient handle support, sparse file management, reparse point handling, and Windows compatibility logic. It intentionally includes codes for operations that may be unimplemented locally so switch statements can reject them with precise statuses.

Risks: incorrect FSCTL numbers or device/access/method bits break interoperability. Some constants are listed for future or partial support; implementing a dispatcher case without validating input/output buffer contracts can expose kernel memory or return malformed protocol data. Reparse tag handling is security-sensitive because name-surrogate tags affect path traversal semantics.

Test signals: cover IOCTL dispatch for supported FSCTLs, explicit `STATUS_NOT_SUPPORTED` or `STATUS_INVALID_DEVICE_REQUEST` for unsupported ones, DFS referral behavior, validate-negotiate integrity checks, sparse/zero range controls, reparse tag query/set/delete, named-pipe controls, and copychunk/resume-key behavior against Windows and Samba clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smbfsctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smbglob.h -->
# sources/distributed-fs/ceph-client/fs/smb/common/smbglob.h

Purpose: declares shared SMB dialect capability metadata and small NetBIOS/RFC1001 length helpers used by SMB client and server code. It is a lightweight common header rather than a runtime module.

Important APIs/types/functions: `struct smb_version_values` captures dialect-specific strings, protocol IDs, lock command encodings, capability flags, maximum read/write/transaction sizes, credits, lock type constants, header and response sizes, signing policy, and create-context sizes. `get_rfc1002_len()` extracts the 24-bit length from the 4-byte stream header, while `inc_rfc1001_len()` increments that header. Version strings include SMB 1.0, SMB 2.0, 2.1, 3.0, 3.0.2, 3.1.1, default, and SMB3-any aliases.

Control flow: callers use the selected dialect's `smb_version_values` after negotiate to size requests and responses and to encode command-specific fields. Receive paths use `get_rfc1002_len()` before allocating a request buffer; response builders use `inc_rfc1001_len()` as iovecs are appended.

State and persistence behavior: there is no state in the header. The structure instances live in dialect tables elsewhere and become per-connection configuration once negotiation completes.

Dependencies and integration points: depends on endian helpers. Integrates with SMB dialect negotiation, stream transport framing, request-size checks, credit accounting, locking behavior, signing policy, and create-context parsing.

Risks: RFC1002 length helpers assume a 4-byte accessible buffer and operate on big-endian stream headers; using them on an SMB header pointer instead of the transport header corrupts parsing. Dialect values control maximum I/O sizes and create-context lengths, so stale metadata can cause undersized buffers or noncompliant negotiation.

Test signals: negotiate each supported dialect, validate stream length parsing for boundary values, build compound responses with multiple iovecs, verify advertised max I/O sizes and credits, and test signing-required/enabled behavior across dialect versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smbglob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/Kconfig -->
# sources/distributed-fs/ceph-client/fs/smb/server/Kconfig

Purpose: exposes kernel configuration for KSMBD, the in-kernel SMB3 server, including base server support, optional SMB Direct/RDMA transport, optional capability gating for server control, and Kerberos support.

Important APIs/types/functions: `config SMB_SERVER` is a tristate that depends on `INET`, `MULTIUSER`, and `FILE_LOCKING`, selects NLS, UTF-8/UCS-2 helpers, crypto primitives, AEAD modes, ASN.1/OID support, and CRC32, and builds the module as `ksmbd`. `config SMB_SERVER_SMBDIRECT` enables RDMA/SMB Direct when InfiniBand support is compatible. `config SMB_SERVER_CHECK_CAP_NET_ADMIN` controls network-admin capability checks for starting the server. `config SMB_SERVER_KERBEROS5` enables Kerberos 5 authentication support.

Control flow: Kconfig selection determines which source files and code paths compile. Enabling `SMB_SERVER` pulls in the core server and required crypto/parser dependencies. `SMB_SERVER_SMBDIRECT` adds RDMA transport objects through the Makefile. `SMB_SERVER_KERBEROS5` changes authentication header sizing and compiles Kerberos IPC paths.

State and persistence behavior: no runtime state exists in Kconfig. The selected options shape the kernel image/module and therefore the available protocol features after boot.

Dependencies and integration points: integrates with the Linux build system, KSMBD userspace tooling (`ksmbd-tools`), crypto API, ASN.1 compiler, OID registry, network stack, NLS/unicode handling, and optional InfiniBand/RDMA stack.

Risks: missing selected crypto or ASN.1 dependencies would lead to link or runtime negotiation failures. Enabling SMB_SERVER without a matching userspace daemon leaves login/share configuration unavailable. The RDMA dependency expression must avoid impossible module/built-in combinations. Disabling the CAP_NET_ADMIN check lowers the barrier for local server-control attempts.

Test signals: build as built-in and module, with and without Kerberos, with and without RDMA, and verify startup through ksmbd-tools, NTLM/Kerberos session setup, SMB3 encryption/signing negotiation, and module load/unload dependency cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/Makefile -->
# sources/distributed-fs/ceph-client/fs/smb/server/Makefile

Purpose: defines the KSMBD module object composition and generated ASN.1 dependencies for the SMB3 server build.

Important APIs/types/functions: `obj-$(CONFIG_SMB_SERVER) += ksmbd.o` builds the aggregate module. `ksmbd-y` includes unicode, auth, VFS/cache, server, NDR, misc, oplock, connection, work, crypto context, management objects, SMB common/protocol handlers, IPC/TCP transports, ACL code, generated SPNEGO ASN.1 objects, and `asn1.o`. Conditional additions include `transport_rdma.o` for `CONFIG_SMB_SERVER_SMBDIRECT` and `proc.o` for `CONFIG_PROC_FS`.

Control flow: kbuild links all listed objects into `ksmbd.o`. Explicit dependencies ensure `asn1.o` sees generated SPNEGO token headers and that generated ASN.1 C/header pairs are built before their objects.

State and persistence behavior: no runtime state is defined. The Makefile controls which compiled code is present in the module.

Dependencies and integration points: integrates with kbuild, the kernel ASN.1 compiler for `ksmbd_spnego_negtokeninit.asn1` and `ksmbd_spnego_negtokentarg.asn1`, optional procfs reporting, and optional RDMA transport support.

Risks: missing an object from `ksmbd-y` can compile individual code but break link-time symbols or runtime features. Incorrect ASN.1 dependencies can create parallel-build races where generated headers are absent. Conditional objects must stay aligned with Kconfig and `#ifdef` guards.

Test signals: parallel kernel builds, module link checks, clean rebuilds after touching ASN.1 files, builds for all combinations of procfs/RDMA/Kerberos, and smoke tests that exercise negotiation, session setup, tree connect, VFS operations, and unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/asn1.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/asn1.c

Purpose: parses SPNEGO ASN.1/BER security blobs for SMB session setup and builds SPNEGO-wrapped NTLMSSP response blobs. It connects generated ASN.1 decoders to KSMBD connection authentication state.

Important APIs/types/functions: `ksmbd_decode_negTokenInit()` and `ksmbd_decode_negTokenTarg()` run generated `asn1_ber_decoder()` instances against client security blobs. `build_spnego_ntlmssp_neg_blob()` builds a negTokenTarg containing a negotiation result, NTLMSSP OID, and NTLMSSP challenge token. `build_spnego_ntlmssp_auth_blob()` builds the final authentication result token. Decoder callbacks include `ksmbd_gssapi_this_mech()`, `ksmbd_neg_token_init_mech_type()`, `ksmbd_neg_token_init_mech_token()`, and `ksmbd_neg_token_targ_resp_token()`.

Control flow: session setup passes the security blob to the appropriate decode function. The generated decoder calls back for the GSS mechanism OID, offered mechanism types, and embedded mech tokens. Valid OIDs update `conn->auth_mechs` and `conn->preferred_auth_mech`; token callbacks duplicate the mech token into `conn->mechToken`. Response construction computes ASN.1 header lengths, emits nested context-specific/sequence/octet-string fields, copies the NTLMSSP payload, and returns the allocated buffer and length to SMB2 session setup code.

State and persistence behavior: no stable state is kept. Runtime side effects are on `struct ksmbd_conn`: authentication mechanism bitmasks, preferred mechanism, `mechToken`, and `mechTokenLen`. Allocated response blobs are caller-owned. `conn->mechToken` is later freed by connection teardown.

Dependencies and integration points: depends on Linux ASN.1 BER decoder, OID registry, generated SPNEGO decoder headers, `connection.h`, `auth.h`, and KSMBD allocation/debug helpers. It integrates directly with NTLMSSP and Kerberos selection during SMB2 SESSION_SETUP.

Risks: length encoding is hand-built and must match BER definite-length rules; off-by-one errors produce security blobs that clients reject. Decoder callbacks must reject unexpected OIDs and zero-length tokens to avoid ambiguous authentication state. Repeated token allocation without prior cleanup would leak unless session setup code controls call ordering. Large token lengths can increase allocation pressure.

Test signals: NTLMSSP-over-SPNEGO negotiation, Kerberos-capable mechanism lists, unsupported OID rejection, malformed BER input, zero-length token rejection, client validation of challenge/final SPNEGO blobs, and leak checks on failed session setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/asn1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/asn1.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/asn1.h

Purpose: declares the KSMBD SPNEGO ASN.1 parse/build entry points used by authentication and SMB2 session setup code.

Important APIs/types/functions: exports `ksmbd_decode_negTokenInit()`, `ksmbd_decode_negTokenTarg()`, `build_spnego_ntlmssp_neg_blob()`, and `build_spnego_ntlmssp_auth_blob()`. The decode functions take a security blob and mutate a `struct ksmbd_conn`; the builders allocate a returned buffer and set a 16-bit length.

Control flow: callers decode client-provided SPNEGO tokens before deciding whether to run NTLMSSP or Kerberos authentication. They call the builder helpers when returning NTLMSSP challenge or final session-setup status inside a SPNEGO envelope.

State and persistence behavior: the header declares functions only. State is in the connection and caller-owned allocated buffers.

Dependencies and integration points: relies on forward visibility of `struct ksmbd_conn` from includers and integrates with `auth.c`, generated ASN.1 decoders, and SMB2 session setup response construction.

Risks: the builder APIs allocate memory through output parameters; callers must free on every response/error path. `u16 *buflen` limits practical output length and must match SMB session-setup security buffer sizing.

Test signals: compile coverage for authentication paths, SPNEGO NTLM challenge/final response generation, malformed token decode errors, and memory cleanup on failed session setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/asn1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/auth.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/auth.c

Purpose: implements KSMBD authentication and cryptographic message protection: NTLMv2 validation, optional Kerberos delegation to userspace, SMB2/SMB3 signing, SMB3 key derivation, preauthentication integrity hashing, and SMB3 transform encryption/decryption.

Important APIs/types/functions: authentication entry points include `ksmbd_copy_gss_neg_header()`, `ksmbd_decode_ntlmssp_neg_blob()`, `ksmbd_build_ntlmssp_challenge_blob()`, `ksmbd_decode_ntlmssp_auth_blob()`, `ksmbd_auth_ntlmv2()`, and `ksmbd_krb5_authenticate()`. Signing/key APIs include `ksmbd_sign_smb2_pdu()`, `ksmbd_sign_smb3_pdu()`, `ksmbd_gen_smb30_signingkey()`, `ksmbd_gen_smb311_signingkey()`, `ksmbd_gen_smb30_encryptionkey()`, `ksmbd_gen_smb311_encryptionkey()`, and `ksmbd_gen_preauth_integrity_hash()`. `ksmbd_crypt_message()` performs AEAD encryption/decryption over SMB3 transform iovecs.

Control flow: NTLMSSP negotiate records client flags on the connection. Challenge generation chooses server flags, creates a random challenge, adds NetBIOS/DNS target info, and returns the challenge blob length. Authenticate parsing validates offsets/lengths, converts the domain name from UTF-16, computes the NTLMv2 response from the stored user passkey and connection challenge, derives the session key, and optionally RC4-decrypts an exchanged secondary key. Kerberos builds an IPC request to userspace, validates returned status/blob/session-key lengths, allocates or validates the session user, and copies the AP-REP output token. Signing hashes all response/request iovecs with HMAC-SHA256 for SMB2 or AES-CMAC for SMB3. SMB3 key derivation applies the SMB KDF labels/contexts for dialect 3.0 and 3.1.1, using preauth hashes for 3.1.1 and channel signing keys for binding. Encryption/decryption selects GCM or CCM from the crypto context pool, sets the session encryption/decryption key, builds a scatterlist over associated data, payload, and signature, derives the IV from the transform header nonce, and invokes the crypto AEAD operation.

State and persistence behavior: no stable storage is owned. Runtime secrets live in `conn->ntlmssp.cryptkey`, `sess->sess_key`, `sess->smb3signingkey`, per-channel `smb3signingkey`, `sess->smb3encryptionkey`, `sess->smb3decryptionkey`, and preauth hash buffers. User/password material is supplied by userspace login responses and freed through session teardown. AEAD transform objects are borrowed from `crypto_ctx.c` and returned after use.

Dependencies and integration points: depends on Linux crypto primitives (MD5/HMAC-MD5, SHA-256 HMAC, SHA-512, AES-CMAC, AEAD GCM/CCM, ARC4), random bytes, scatterlists, NLS/Unicode conversion, KSMBD connection/session/user management, transport IPC, and SMB2 transform/header definitions. It integrates with session setup, negotiate preauth state, signing verification/response signing, encrypted transport handling, and multichannel binding.

Risks: this file is security critical. Wire blob offsets must be checked before dereference; NTLMv2 is disabled under FIPS, so deployments relying on NTLM must handle `-EOPNOTSUPP`. RC4 key exchange is legacy-sensitive and must not overrun `sess->sess_key`. KDF labels and contexts are dialect-specific; a wrong label breaks interoperability or weakens channel binding. Scatterlist construction must handle vmalloc and linear buffers correctly. Encryption key lookup must avoid using an invalid session, especially on decrypt paths that search all bound sessions.

Test signals: NTLMv2 success/failure, bad signatures and truncated NTLMSSP blobs, FIPS mode behavior, Kerberos userspace IPC success/failure and oversized blobs, SMB2 HMAC signing, SMB3 AES-CMAC signing, SMB3.1.1 preauth hash updates, channel binding signing keys, AES-128/256 CCM and GCM encryption/decryption, vmalloc-backed large reads/writes, and interop with Windows/Samba clients under signing/encryption-required modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/auth.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/auth.h

Purpose: declares authentication, signing, key-derivation, and encryption helpers for the KSMBD server and centralizes authentication-related constants.

Important APIs/types/functions: defines `AUTH_GSS_LENGTH`/`AUTH_GSS_PADDING` depending on Kerberos support, NTLM hash/session key sizes, SMB1 signature/session-key sizes, and `KSMBD_AUTH_*` mechanism bits for NTLMSSP, Kerberos, Microsoft Kerberos, and Kerberos user-to-user. It declares NTLMSSP decode/build/auth functions, optional Kerberos authentication, SMB2/SMB3 signing helpers, SMB3.0/3.1.1 signing and encryption key generation, `ksmbd_gen_preauth_integrity_hash()`, and `ksmbd_crypt_message()`.

Control flow: SMB negotiate/session-setup code includes this header to select offered mechanisms, copy the GSS header, validate NTLM/Kerberos authentication, derive keys once a session is authenticated, and protect subsequent PDUs.

State and persistence behavior: the header owns no state; declared functions operate on `struct ksmbd_conn`, `struct ksmbd_session`, and `struct ksmbd_work` runtime objects.

Dependencies and integration points: includes `ntlmssp.h` and forward-declares core KSMBD structs. It links authentication code to SMB2 session setup, transform encryption, signing verification, and negotiated dialect/cipher policy.

Risks: constants such as GSS length and key sizes must match protocol structs in `ntlmssp.h` and session setup response sizing. Callers must respect that many functions return negative errno and may leave output buffers uninitialized on failure.

Test signals: build both Kerberos and non-Kerberos configs, compile all signing/encryption users, and exercise NTLMSSP, Kerberos, SMB2/SMB3 signing, preauth, and transform encryption paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/connection.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/connection.c

Purpose: manages KSMBD connection objects, the per-connection receive loop, request accounting, global connection tracking, transport initialization/destruction, procfs client reporting, and deferred final connection release.

Important APIs/types/functions: lifecycle APIs include `ksmbd_conn_alloc()`, `ksmbd_conn_free()`, `ksmbd_conn_get()`, `ksmbd_conn_put()`, `ksmbd_conn_wq_init()`, and `ksmbd_conn_wq_destroy()`. Request APIs include `ksmbd_conn_enqueue_request()`, `ksmbd_conn_try_dequeue_request()`, `ksmbd_conn_wait_idle()`, `ksmbd_conn_wait_idle_sess_id()`, `ksmbd_conn_write()`, `ksmbd_conn_rdma_read()`, and `ksmbd_conn_rdma_write()`. Transport/server APIs include `ksmbd_conn_handler_loop()`, `ksmbd_conn_transport_init()`, `ksmbd_conn_transport_destroy()`, `ksmbd_conn_init_server_callbacks()`, and `ksmbd_all_conn_set_status()`.

Control flow: allocation initializes dialect negotiation state, NLS/unicode maps, counters, request lists, locks, async IDA, and session xarray. The handler loop owns the connection thread: it enforces max in-flight requests, reads the 4-byte RFC1002 header, validates PDU length against SMB limits and negotiated write size, allocates a request buffer, reads the full PDU, validates SMB1/SMB2 minimum sizes, and invokes the registered protocol process callback. On exit it marks the connection releasing, waits for request references, unloads Unicode/NLS state, calls the terminate callback, disconnects the transport, and drops the module reference. Transport destroy stops listeners and iteratively shuts down all live sessions/connections.

State and persistence behavior: runtime state is held in the global `conn_list` hashtable under `conn_list_lock`, each `struct ksmbd_conn`'s status, request queues, async queues, xarray of sessions, credits, locks, NLS/unicode state, auth fields, preauth table, and transport pointer. Nothing is persisted; shutdown removes connections and frees transports. Final freeing is queued to `ksmbd-conn-release` because transport/socket teardown can sleep and may be triggered from non-sleeping put contexts.

Dependencies and integration points: depends on TCP/RDMA transport ops, server configuration, SMB protocol parsing helpers, KSMBD work/request handling, session management, procfs helper creation, Linux workqueues/freezer/module references, NLS/unicode subsystems, and IDA/xarray/list primitives.

Risks: receive-loop length validation is externally exposed; accepting oversized lengths can overallocate, while underestimating negotiated limits can reject legal large writes. Request counters and wait queues gate shutdown/reconnect and must stay balanced. The global connection lock protects hash membership but not all per-connection state. Deferred release requires the workqueue lifetime to outlive all possible references. `stop_sessions()` deliberately walks one target at a time; regressions can race with connection self-release.

Test signals: connect/disconnect storms, max-inflight throttling, malformed RFC1002 lengths, SMB1/SMB2 minimum PDU checks, large write bounds after negotiation, shutdown while requests are active, multichannel/session reconnect idle waits, procfs clients output, TCP and RDMA transports, module unload after oplock/file references, and leak/refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/connection.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/connection.h

Purpose: defines the central KSMBD connection and transport abstractions plus status helpers and exported connection-management APIs.

Important APIs/types/functions: `enum KSMBD_SESS_*` status values describe connection negotiation/setup/good/reconnect/exiting/releasing states. `struct ksmbd_conn` aggregates dialect ops/values, transport pointer, address, request buffers, NLS/unicode state, session xarray, request/async queues, credit state, stats, client GUID, NTLMSSP/preauth/auth negotiation state, async IDA, cipher/compression/signing/multichannel flags, refcount, and release work. `struct ksmbd_conn_ops` provides protocol callbacks. `struct ksmbd_transport_ops` abstracts disconnect/shutdown/read/writev/RDMA/free operations. Inline helpers test and set connection status with `READ_ONCE`/`WRITE_ONCE`.

Control flow: transport code allocates a `ksmbd_conn`, attaches transport ops, and starts `ksmbd_conn_handler_loop()`. Protocol code uses the ops and status helpers during negotiate/session setup. Request code queues/dequeues work through the declared APIs and writes responses through the selected transport.

State and persistence behavior: all fields are volatile per-connection state. Session membership is per-connection in an xarray but can also be represented globally for multichannel. Refcounted final release is asynchronous via `release_work`.

Dependencies and integration points: includes SMB common definitions, KSMBD work state, Linux socket/network/kthread/NLS/unicode/workqueue headers, and transport-specific RDMA descriptor forward declarations. It is included broadly by server, transport, auth, session, and protocol handlers.

Risks: `status` is noted as a temporary multi-session hack, so code assuming per-session status can behave incorrectly under multichannel/reconnect. Transport ops must be complete for the selected transport; NULL RDMA ops are handled by wrappers but other ops are required. Consumers must hold appropriate locks around request lists, session xarrays, and global connection hash traversal.

Test signals: compile both IPv4/IPv6 and RDMA configs, exercise status transitions through negotiate/setup/reconnect/shutdown, test transport write/read wrappers, validate refcounting under async references, and inspect connection procfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/connection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/crypto_ctx.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/crypto_ctx.c

Purpose: implements a small pool of reusable AEAD crypto contexts for SMB3 encryption/decryption, reducing repeated allocation of AES-GCM/AES-CCM transform objects under request load.

Important APIs/types/functions: internal `struct crypto_ctx_list` tracks a spinlock, available context count, idle context list, and waitqueue. Public APIs are `ksmbd_crypto_create()`, `ksmbd_crypto_destroy()`, `ksmbd_crypto_ctx_find_gcm()`, `ksmbd_crypto_ctx_find_ccm()`, and `ksmbd_release_crypto_ctx()`. Helpers allocate/free AEAD transforms for `gcm(aes)` and `ccm(aes)`.

Control flow: module initialization calls `ksmbd_crypto_create()` to initialize the pool and seed one idle context. Encryption code calls a find function, which removes an idle context if available or allocates a new context while the count is at or below `num_online_cpus()`. If the pool is over the CPU-count cap, callers wait for an idle context. The requested AEAD transform is lazily allocated within the borrowed context. Release returns contexts to the idle list when under the cap or frees them when above it. Destroy frees idle contexts during shutdown.

State and persistence behavior: `ctx_list` is process-wide runtime state. It persists only while the module/server is initialized. Individual `struct ksmbd_crypto_ctx` objects cache AEAD transform pointers for reuse across requests; keys are set per operation by `auth.c`, so no stable key material should persist as pool state beyond crypto transform internals.

Dependencies and integration points: depends on Linux crypto AEAD API, spinlocks, waitqueues, CPU count, lists, and KSMBD allocation flags. It is consumed by `ksmbd_crypt_message()` for SMB3 transform handling.

Risks: wait paths assume a context will eventually be returned; leaks in encryption error paths can stall future requests. `avail_ctx` accounting must remain balanced across allocation failure, wait, release, and destroy. Context reuse requires every operation to set key/authsize before use. Destroy only walks idle contexts, so shutdown ordering must ensure no borrowed contexts remain.

Test signals: concurrent encrypted I/O across more workers than CPUs, allocation-failure injection, both AES-GCM and AES-CCM paths, AES-128 and AES-256 key setting, server shutdown while encrypted requests drain, and lockdep/refcount/leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/crypto_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/crypto_ctx.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/crypto_ctx.h

Purpose: declares KSMBD's reusable AEAD crypto context type and pool APIs for SMB3 encryption.

Important APIs/types/functions: enum values identify `CRYPTO_AEAD_AES_GCM`, `CRYPTO_AEAD_AES_CCM`, and `CRYPTO_AEAD_MAX`. `struct ksmbd_crypto_ctx` contains a list node and an array of cached `struct crypto_aead *`. `CRYPTO_GCM(ctx)` and `CRYPTO_CCM(ctx)` select the cached transform. Public functions create/destroy the pool, acquire GCM/CCM-capable contexts, and release borrowed contexts.

Control flow: callers initialize the pool at server startup, acquire a context for each encrypted/decrypted message, use the transform selected by cipher type, then release the context after the crypto request completes.

State and persistence behavior: the header declares a runtime cache object only. Contexts are not persistent storage and should not be assumed to retain request-specific keying safely.

Dependencies and integration points: depends on `<crypto/aead.h>` and list infrastructure through includers. It integrates with `auth.c` and KSMBD server startup/shutdown.

Risks: enum values start at 16, so the `ccmaes` array is sparse; any code iterating or sizing must use `CRYPTO_AEAD_MAX`, not a count of two. Callers must handle NULL acquisition on unsupported IDs or allocation failure.

Test signals: build coverage, encrypted SMB3 requests for CCM and GCM, pool create/destroy paths, and failure injection around transform allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/crypto_ctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/glob.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/glob.h

Purpose: provides server-local global definitions for KSMBD: debug categories, printk prefix formatting, Unicode length helper, and the default GFP allocation mask.

Important APIs/types/functions: `ksmbd_debug_types` is the external debug bitmask. Debug bits cover SMB, AUTH, VFS, OPLOCK, IPC, CONN, RDMA, and ALL. `ksmbd_debug(type, fmt, ...)` conditionally emits `pr_info()` when the corresponding bit is enabled. `UNICODE_LEN(x)` returns UTF-16 byte length for a character count. `KSMBD_DEFAULT_GFP` is `GFP_KERNEL | __GFP_RETRY_MAYFAIL`.

Control flow: server files include this header and call `ksmbd_debug()` in hot and error-adjacent paths. The macro compiles to a bit test plus `pr_info()` call, with `pr_fmt` adjusted to include `ksmbd` and optional submodule names.

State and persistence behavior: only the external debug mask is mutable runtime state. No persistent storage is defined.

Dependencies and integration points: includes character helpers, KSMBD Unicode and VFS cache headers, and Linux printk/GFP conventions through includers. It is one of the most widely included KSMBD local headers.

Risks: debug output can be noisy in hot paths if broad bits are enabled. `KSMBD_DEFAULT_GFP` may retry under memory pressure, so allocation sites using it must be able to sleep and tolerate latency. `UNICODE_LEN` assumes UTF-16 two-byte units and is not a complete conversion helper.

Test signals: build with different `SUBMOD_NAME` definitions, enable each debug category, run memory-pressure tests over request paths, and verify UTF-16 buffer sizing in auth/share/session code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/glob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_netlink.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_netlink.h

Purpose: defines the Generic Netlink userspace ABI between the KSMBD kernel server and the ksmbd userspace IPC daemon. It carries startup/shutdown configuration, heartbeat, login data, share configuration, tree connect authorization, RPC forwarding, Kerberos SPNEGO authentication, and user-extension payloads.

Important APIs/types/functions: ABI identifiers include `KSMBD_GENL_NAME` and `KSMBD_GENL_VERSION`. Packed request/response structs cover `ksmbd_heartbeat`, `ksmbd_startup_request`, `ksmbd_shutdown_request`, login request/response and extension, share config request/response, tree connect request/response/disconnect, logout, `ksmbd_rpc_command`, and SPNEGO auth request/response. `ksmbd_share_config_path()` locates the share path behind an optional veto list in a variable payload. `enum ksmbd_event` defines request/response event numbers. The header also defines global flags, user flags, share flags, tree-connect flags/statuses, RPC method/status flags, and config option values.

Control flow: kernel code sends a request event with a handle, userspace replies with the paired response event, and management/auth code converts the payload into runtime users, shares, sessions, or RPC results. Startup populates global server configuration. Login responses feed `ksmbd_user`. Share responses feed `ksmbd_share_config`. Tree connect responses authorize and flag `ksmbd_tree_connect`. Kerberos requests outsource SPNEGO validation and session key generation to userspace.

State and persistence behavior: this header owns no state, but it defines the ABI for state imported into the kernel. Userspace owns durable account/share configuration; kernel caches selected users, shares, sessions, tree connections, and RPC handles. Packed layouts and reserved fields preserve ABI compatibility.

Dependencies and integration points: depends on Linux integer types and Generic Netlink transport code elsewhere. It integrates with `transport_ipc.c`, `auth.c`, `mgmt/user_config.c`, `mgmt/share_config.c`, `mgmt/tree_connect.c`, `mgmt/user_session.c`, server startup/shutdown, and named-pipe RPC handling.

Risks: this is a stable ABI boundary. Changing struct layout, packing, event numbering, flag values, or payload ordering can break ksmbd-tools. Variable payload fields (`____payload`, veto list, path, group list, SPNEGO blobs) require strict length validation by consumers. User/group IDs and password hashes are trusted from userspace IPC, so daemon authentication and capability checks matter. Reserved fields should remain zero-compatible.

Test signals: netlink compatibility tests with current and older ksmbd-tools, startup config import, heartbeat timeout behavior, login success/failure/extension groups, share path plus veto list parsing, tree connect authorization flags, named-pipe RPC open/read/write/close, Kerberos SPNEGO exchange, and fuzzing of payload sizes and event types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_work.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_work.c

Purpose: implements allocation, freeing, queueing, and response-iovec construction for KSMBD request work items.

Important APIs/types/functions: `ksmbd_work_pool_init()`/`ksmbd_work_pool_destroy()` manage the `ksmbd_work_cache` slab. `ksmbd_workqueue_init()`/`ksmbd_workqueue_destroy()` manage the per-CPU `ksmbd-io` workqueue. `ksmbd_alloc_work_struct()` and `ksmbd_free_work_struct()` allocate/free `struct ksmbd_work`. `ksmbd_queue_work()` queues protocol work. `ksmbd_iov_pin_rsp()`, `ksmbd_iov_pin_rsp_read()`, and `allocate_interim_rsp_buf()` build response buffers.

Control flow: request processing allocates a zeroed work object, initializes compound FIDs to `KSMBD_NO_FID`, list heads, default iovec capacity, and a kvec array. Protocol handlers fill request/session/tree state and queue the embedded work item. Response building ensures the first iovec contains a 4-byte RFC1002 length field, appends response buffers and optional auxiliary read buffers, increments the stream length, and tracks auxiliary buffers for later cleanup. Freeing releases response/request buffers, transform buffers, iovecs, auxiliary read buffers, async IDs, and the slab object.

State and persistence behavior: all state is per-request and transient. The slab cache and workqueue persist while the server is running. Async message IDs are allocated from the connection IDA and released when the work object is freed.

Dependencies and integration points: depends on KSMBD server/connection state, IDA helpers, Linux slab/workqueue/list memory APIs, and common RFC1001 length helpers. It integrates with SMB2 command handlers, connection request queues, async cancellation, read response construction, and transport writev.

Risks: iovec growth and RFC1002 length increments must stay synchronized or clients receive malformed responses. Auxiliary read buffers are owned by the work object after pinning; double-free or missed list insertion causes memory bugs. `saved_cred` must be reverted before freeing, enforced by a warning. Async IDs must be released exactly once.

Test signals: simple and compound responses, large read responses with auxiliary buffers, iovec reallocation, interim responses, async request/cancel cleanup, error paths after partial response construction, and slab/workqueue leak checks on disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_work.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_work.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_work.h

Purpose: defines the per-request `struct ksmbd_work` context and declares work-pool, workqueue, and response-iovec helper APIs.

Important APIs/types/functions: `enum KSMBD_WORK_*` describes active/cancelled/closed work state. `struct aux_read` tracks extra read buffers attached to response iovecs. `struct ksmbd_work` contains connection/session/tree pointers, request and response buffers, response iovecs, compound request/response offsets, compound FIDs, saved credentials, credits granted, transform buffer, state bits for encrypted/async/no-response/RDMA invalidation, async cancel metadata, embedded `work_struct`, request/async/file list entries, and auxiliary read list. Inline helpers return current/next SMB2 request/response buffer pointers.

Control flow: connection/protocol code allocates a work item, parses command buffers using the inline offset helpers, processes the command on the KSMBD workqueue, builds iovecs, writes the response, dequeues the work, and frees it.

State and persistence behavior: work items are transient request state. Compound offsets and FIDs persist only for the lifetime of one SMB request chain. Saved credentials must be reverted before destruction.

Dependencies and integration points: depends on Linux workqueues, ctype helpers, KSMBD connection/session/tree types, SMB protocol definitions, async cancellation, RDMA response metadata, and VFS/file operation paths that attach `fp_entry`.

Risks: pointer arithmetic assumes response/request buffers include the 4-byte RFC1002 prefix and valid compound offsets. Incorrect async state can leave cancellation callbacks or async IDs dangling. The struct is central and shared across protocol handlers, so field lifetime conventions must be maintained.

Test signals: command parsing for compound chains, async create/ioctl/read paths, encrypted requests, cancelled requests, RDMA read/write responses, saved credential warning coverage, and workqueue cleanup at server shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ksmbd_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/ksmbd_ida.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/ksmbd_ida.c

Purpose: wraps Linux IDA allocation for SMB-visible identifiers: tree IDs, user/session IDs, async message IDs, and generic internal IDs.

Important APIs/types/functions: `ksmbd_acquire_smb2_tid()` allocates SMB2 tree IDs from 1 through `0xFFFFFFFE`. `ksmbd_acquire_smb2_uid()` allocates SMB2 user/session IDs from 1 while avoiding reserved `0xFFFE`. `ksmbd_acquire_async_msg_id()` allocates async IDs from 1. `ksmbd_acquire_id()` and `ksmbd_release_id()` provide generic allocation/free wrappers.

Control flow: session and tree-connect management call these helpers during creation and release IDs during disconnect/session teardown. The UID helper retries if IDA returns the reserved LAN Manager value.

State and persistence behavior: ID state is stored in caller-owned `struct ida` instances, such as the global session IDA and per-session tree-connection IDAs. IDs are volatile and not persisted across server restart.

Dependencies and integration points: depends on Linux IDA and KSMBD allocation flags. It integrates with session creation, tree connect creation, async request handling, and RPC/IPC ID allocation wrappers elsewhere.

Risks: leaking IDs on error paths can exhaust per-session or global ID spaces. Returning `0xFFFE` handling in UID allocation retries once; callers still must handle negative allocation errors. TID allocation starts at 1 even though SMB2 permits zero, which is a deliberate compatibility choice that callers should not assume is exhaustive.

Test signals: repeated session/tree connect create/destroy, reserved UID avoidance, ID exhaustion/failure injection, async request ID release, and reconnect after many prior allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/ksmbd_ida.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/ksmbd_ida.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/ksmbd_ida.h

Purpose: declares KSMBD IDA helper APIs and documents SMB2 TID/UID reserved-value rules.

Important APIs/types/functions: exposes `ksmbd_acquire_smb2_tid()`, `ksmbd_acquire_smb2_uid()`, `ksmbd_acquire_async_msg_id()`, `ksmbd_acquire_id()`, and `ksmbd_release_id()`. Comments cite SMB2 TID and UID constraints, especially reserved TID `0xFFFF` and UID `0xFFFE`.

Control flow: management code includes this header to allocate identifiers at object creation and release them at object destruction.

State and persistence behavior: the header owns no state. State lives in the caller-provided `struct ida`.

Dependencies and integration points: depends on Linux slab/IDR headers and integrates with user session, tree connect, and async work management.

Risks: callers must use the protocol-specific helper for protocol-visible IDs instead of the generic allocator, or reserved values may leak onto the wire.

Test signals: compile coverage and identifier allocation tests around reserved values, release/reuse, and exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/ksmbd_ida.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/share_config.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/share_config.c

Purpose: obtains, validates, caches, references, and frees KSMBD share configuration imported from the userspace IPC daemon.

Important APIs/types/functions: public APIs are `ksmbd_share_config_get()`, `ksmbd_share_config_put()` through the header, `ksmbd_share_config_del()`, `__ksmbd_share_config_put()`, and `ksmbd_share_veto_filename()`. Internals include the `shares_table` hashtable keyed by `jhash(name)`, `shares_table_lock`, `struct ksmbd_veto_pattern`, `parse_veto_list()`, `share_config_request()`, and `kill_share()`.

Control flow: lookup first tries the in-kernel cache under a read lock and increments the share refcount if present. On miss, `share_config_request()` asks userspace for the share, rejects invalid flags or mismatched casefolded share names, allocates a `ksmbd_share_config`, copies flags/masks/force uid-gid/name, parses veto patterns, normalizes trailing slashes from the path, temporarily overrides fsids for path lookup, and caches the share under a write lock unless another racing lookup already inserted it. Share updates from tree-connect responses delete the stale cache entry so a fresh request is made.

State and persistence behavior: runtime share configs are cached in `shares_table` with atomic refcounts. Disk path state is pinned by `struct path vfs_path` and released with `path_put()`. Veto patterns, share name, and path strings are kernel allocations. Persistent share definitions remain in userspace configuration.

Dependencies and integration points: depends on transport IPC, user/session context for fsuid/fsgid override, Unicode casefolding, VFS path lookup, wildcard matching, KSMBD share flag ABI, and tree-connect management.

Risks: variable payload parsing from userspace must keep veto-list and path lengths consistent. Path lookup under overridden fsids is security-sensitive and must always revert credentials. Cache races are handled by rechecking under the write lock; missed refcounting would use freed share configs. Share update invalidation must not drop a share still referenced by active tree connections.

Test signals: share cache hits/misses, case-insensitive share name matching, invalid userspace responses, disk and IPC pipe shares, veto list matching, trailing slash normalization, inaccessible path handling, forced modes/uid/gid, share update flag behavior, concurrent tree connects to the same share, and cleanup after disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/share_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/share_config.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/share_config.h

Purpose: defines the in-kernel KSMBD share configuration object and helper APIs used by tree connects and VFS operations.

Important APIs/types/functions: `struct ksmbd_share_config` stores name, path, path size, share flags, veto list, pinned VFS path, refcount, hash node, create/directory masks, forced modes, and forced uid/gid. `KSMBD_SHARE_INVALID_UID/GID` mark absent forced IDs. Inline helpers `share_config_create_mode()` and `share_config_directory_mode()` apply mask/force rules, while `test_share_config_flag()` checks share flags. APIs include get/put/delete and veto filename matching.

Control flow: tree-connect code obtains a referenced share config, VFS code consults flags/modes/path, and disconnect code drops references. The put helper decrements the atomic refcount and calls the full deletion/free path on the last reference.

State and persistence behavior: share configs are runtime cache entries, not durable config. `vfs_path` pins the resolved path while the share object is alive. Mode masks and force IDs are copied from userspace and remain fixed until cache invalidation/update.

Dependencies and integration points: depends on Linux workqueue/hashtable/path/unicode headers, KSMBD netlink share flags, and VFS/share-management code.

Risks: mode helper behavior treats zero POSIX mode as all bits before masking, so callers must pass zero only when they want default mask behavior. Put/delete ordering must not remove an object still reachable without a refcount.

Test signals: file and directory create mode calculations, read-only/writeable/pipe flag behavior, refcounted share lifetime across multiple tree connects, and veto filename checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/share_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/tree_connect.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/tree_connect.c

Purpose: manages SMB tree connections that bind an authenticated session to a configured share, including userspace authorization, per-session xarray registration, lookup, disconnect, and session logoff cleanup.

Important APIs/types/functions: `ksmbd_tree_conn_connect()` creates a tree connection. `ksmbd_tree_conn_lookup()` returns a referenced connected tree by ID. `ksmbd_tree_conn_disconnect()` removes one tree connection. `ksmbd_tree_conn_session_logoff()` disconnects all trees for a session. `ksmbd_tree_connect_put()` drops a reference. Internal `__ksmbd_tree_conn_disconnect()` sends the IPC disconnect and releases IDs/counters.

Control flow: connect obtains the share config, allocates a tree object, allocates a TID from the session, sends a userspace tree-connect request with session/share/peer data, checks the returned status, optionally refreshes stale share config when the update flag is set, initializes flags/user/share/state/refcount, stores the object in `sess->tree_conns`, and increments the tree counter. Disconnect erases the tree from the session xarray, sends userspace disconnect, releases the TID, decrements counters, drops share refs, and frees on final ref. Lookup only returns trees in `TREE_CONNECTED` state and increments the refcount.

State and persistence behavior: tree connections are per-session runtime objects stored in `sess->tree_conns` under `tree_conns_lock`. They hold a referenced share config and user pointer. Userspace receives connect/disconnect notifications but durable state remains outside this file.

Dependencies and integration points: depends on IPC transport, connection peer address, user session state, share config cache, IDA helpers, xarray, and KSMBD stats counters. Protocol handlers use tree lookup for TID validation before VFS operations.

Risks: tree state transitions must align with SMB2 TREE_CONNECT/TREE_DISCONNECT and session logoff; lookups deliberately reject non-connected states. Error paths must release TIDs and share refs. Share update handling deletes stale cache entries while active references may exist, so refcounts must be correct. Session logoff iterates while erasing xarray entries and must avoid double-disconnect.

Test signals: successful and failed tree connects, host denied/no share/no user statuses, stale share update flag, lookup before and after marking connected/disconnected, disconnect notification to userspace, logoff with multiple shares, concurrent file operations holding tree refs, and stats counter balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/tree_connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/tree_connect.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/tree_connect.h

Purpose: declares KSMBD tree-connection state, flags, status wrapper, and management APIs.

Important APIs/types/functions: enum values `TREE_NEW`, `TREE_CONNECTED`, and `TREE_DISCONNECTED` track tree lifecycle. `struct ksmbd_tree_connect` stores TID, flags, referenced share config, user pointer, list node, maximal access, POSIX extension state, refcount, and state. `struct ksmbd_tree_conn_status` returns both a status code and optional tree pointer from connect. `test_tree_conn_flag()` checks KSMBD tree flags. APIs cover connect, put, disconnect, lookup, and session logoff.

Control flow: SMB2 tree-connect code calls connect and later moves state to connected when the protocol response succeeds. Request handlers look up trees by TID, use share config and flags, then put references. Tree disconnect/logoff code removes objects.

State and persistence behavior: declared objects are runtime per-session state only. Share configuration is separately refcounted.

Dependencies and integration points: includes KSMBD netlink flag/status definitions and integrates with user session, share config, and protocol command handlers.

Risks: `user` is a raw pointer to the session user; tree lifetime must not outlive session destruction. `maximal_access` and `posix_extensions` must be initialized by protocol paths before use.

Test signals: state transitions, flag checks for guest/read-only/writeable/admin/update, POSIX extension behavior, maximal-access reporting, and refcounted lookup/put under disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/tree_connect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_config.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_config.c

Purpose: imports user account data from the userspace IPC daemon and converts login responses into in-kernel `ksmbd_user` objects used by authentication and authorization.

Important APIs/types/functions: `ksmbd_login_user()` requests account data and optional extension data from userspace. `ksmbd_alloc_user()` allocates/copies name, flags, uid/gid, password hash, and supplementary groups. `ksmbd_free_user()` sends logout notification and frees user memory. `ksmbd_anonymous_user()` and `ksmbd_compare_user()` provide simple identity checks.

Control flow: authentication code calls `ksmbd_login_user()` or, for Kerberos, allocates a user from a login response embedded in the SPNEGO response. Login rejects missing responses and responses without `KSMBD_USER_FLAG_OK`; if the extension flag is set, it requests supplementary groups. Allocation copies all relevant fields into kernel memory. Freeing notifies userspace that the account logged out.

State and persistence behavior: `ksmbd_user` is runtime session state. Persistent account data and password hashes remain owned by userspace configuration. The copied passkey and supplementary group array live until session destruction.

Dependencies and integration points: depends on transport IPC and KSMBD netlink login structures. It integrates with NTLMv2 hash validation, Kerberos session setup, VFS credential override, tree connect authorization, and session reconnect identity checks.

Risks: extension payload length must be trustworthy or validated by IPC code; this file copies `ngroups * sizeof(gid_t)`. `ksmbd_compare_user()` compares passkeys using `u1->passkey_sz` and assumes sizes match from caller context, so callers should check sizes when needed. Passkeys are freed with `kfree`, not explicitly scrubbed in this file.

Test signals: valid/invalid login responses, guest and anonymous users, extension supplementary groups, allocation failure paths, logout notifications, NTLM passkey use, and session reuse attempts with same/different user credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_config.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_config.h

Purpose: defines KSMBD's runtime user object and small helpers for user flags, identity fields, and passkey access.

Important APIs/types/functions: `struct ksmbd_user` stores flags, uid, gid, account name, password hash/passkey size, supplementary group count, and supplementary group IDs. Inline helpers include `user_guest()`, `set_user_flag()`, `test_user_flag()`, `user_passkey()`, `user_name()`, `user_uid()`, and `user_gid()`. Declared APIs cover login, allocation, free, anonymous check, and comparison.

Control flow: authentication populates a `ksmbd_user`, sessions hold it, VFS paths use uid/gid/groups for credential override, and logoff frees it through `ksmbd_free_user()`.

State and persistence behavior: user objects are transient copies of userspace account data. Passkeys remain in memory for session lifetime because NTLMv2 validation needs them.

Dependencies and integration points: includes KSMBD globals and netlink user flag definitions through includers. It integrates with auth, sessions, share config, and VFS credential handling.

Risks: `set_user_guest()` is a no-op, so code must set guest status via flags rather than that helper. Accessors expose mutable pointers to name/passkey; callers must not retain them past user lifetime.

Test signals: guest flag behavior, anonymous user name handling, VFS uid/gid use, supplementary group propagation, and cleanup after failed or completed sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_session.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_session.c

Purpose: manages authenticated SMB2 session lifecycle, global/per-connection session lookup, multichannel channel lists, tree-connection cleanup, named-pipe RPC handle tracking, preauthentication session state, reconnect/expiration logic, and procfs session reporting.

Important APIs/types/functions: session lifecycle functions include `ksmbd_smb2_session_create()`, `ksmbd_session_register()`, `ksmbd_session_destroy()`, `ksmbd_sessions_deregister()`, `ksmbd_user_session_get()`, and `ksmbd_user_session_put()`. Lookup APIs include `ksmbd_session_lookup()`, `ksmbd_session_lookup_slowpath()`, `ksmbd_session_lookup_all()`, `__session_lookup()`, and `is_ksmbd_session_in_connection()`. Reconnect/preauth helpers are `destroy_previous_session()`, `ksmbd_preauth_session_alloc()`, and `ksmbd_preauth_session_lookup()`. Tree ID wrappers call IDA helpers. RPC APIs include `ksmbd_session_rpc_open()`, `ksmbd_session_rpc_close()`, and `ksmbd_session_rpc_method()`. Procfs helpers render session/channel/share state when enabled.

Control flow: session creation allocates a `ksmbd_session`, initializes file table, tree connection IDA, xarrays for tree connections/channels/RPC handles, locks, sequence number, state, and refcount, allocates an SMB2 UID, inserts the session into the global hash, and creates procfs state. Registration copies dialect and client GUID from the connection, expires stale sessions on that connection, and stores the session in `conn->sessions`. Lookup first checks the connection xarray and, for binding connections, can use the global hash while ensuring the connection is in the session channel list. Deregistration removes a connection's channels and destroys sessions once no channels/refcounts remain. `destroy_previous_session()` validates same user credentials, marks all connections for reconnect, waits for idle, destroys the old file table, marks the previous session expired, and launches durable-handle scavenging. RPC open maps pipe names to userspace method flags, allocates IPC IDs, stores them in a session xarray, and sends open/close calls to userspace.

State and persistence behavior: runtime state is split between the global `sessions_table` under `sessions_table_lock`, per-connection `conn->sessions`, per-session channel xarray, tree-connection xarray, RPC handle xarray, preauth session list on the connection, file table, signing/encryption keys, preauth hash, and refcount. Persistent durable handle semantics are coordinated through file table cleanup and scavenger launch, but this file itself stores no durable data.

Dependencies and integration points: depends on IDA helpers, user config, tree connect, share config, transport IPC/RPC helpers, connection management, VFS cache/file-table management, stats counters, procfs helpers, xarray/rwsem/hashtable/list primitives, and SMB2 capability/cipher/signing definitions.

Risks: locking order across global sessions, connection session locks, channel locks, tree locks, and RPC locks is delicate. Refcount initial value and put paths must match hash/xarray/channel references to avoid leaks or premature destruction. Multichannel lookup must not let a binding connection access a session unless it is recorded in the channel list. Reconnect waits can time out and must restore connection status. RPC handles are userspace-backed and need cleanup on session destroy. Procfs show paths take references while walking nested state.

Test signals: session setup/logoff, expired in-progress session cleanup, multichannel bind/unbind, reconnect with same and different users, previous-session destruction with active requests, durable handle scavenger triggering, tree connection cleanup on logoff, named-pipe RPC open/read/write/close for srvsvc/wkssvc/samr/lsarpc/LANMAN, procfs session output, and lockdep/refcount tests under disconnect races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_session.c -->
