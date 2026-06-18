# subset-b-009661 research

Grouped research for the libsmb2 SMB2 API, NTLMSSP, and MD4/MD5 support files.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/libsmb2.c -->
# sources/user-network-fs/libsmb2/lib/libsmb2.c

## Purpose

`libsmb2.c` is the high-level SMB2 client/server orchestration layer for libsmb2. It exposes async file, directory, metadata, notification, connection, disconnection, and server-loop operations by building SMB2 command request structures, queueing PDUs, and translating completion callbacks into the public callback contract. It also owns SMB2/SMB3 negotiation follow-up, session setup, tree connect, signing/encryption key derivation, SMB 3.1.1 pre-authentication hash updates, and a callback-dispatched SMB2 server path.

## Important APIs, Types, And Functions

The file defines local state carriers for async lifetimes: `struct connect_data` keeps connection callback data, server/share/user strings, UNC strings, auth context, and optional server context; `struct smb2fh` wraps file-id, current offset, EOF, and callback state; additional small structs (`read_data`, `write_data`, `stat_cb_data`, `trunc_cb_data`, `rename_cb_data`, `readlink_cb_data`, `notify_change_cb_data`) preserve callback state across compound requests.

Connection/session APIs include `smb2_connect_share_async`, `connect_cb`, `negotiate_cb`, `send_session_setup_request`, `session_setup_cb`, `tree_connect_cb`, `smb2_disconnect_share_async`, and `smb2_close_context`. These coordinate socket connect, dialect negotiation, SPNEGO/NTLMSSP or Kerberos auth, session-key extraction, signing/encryption key creation, optional tree connect, and teardown.

File and directory APIs include `smb2_opendir_async`, `smb2_readdir`, `smb2_seekdir`, `smb2_telldir`, `smb2_rewinddir`, `smb2_closedir`, `smb2_open_async`, `smb2_open_async_with_oplock_or_lease`, `smb2_close_async`, `smb2_fsync_async`, `smb2_pread_async`, `smb2_read_async`, `smb2_pwrite_async`, `smb2_write_async`, and `smb2_lseek`. Metadata and mutation APIs include `smb2_unlink_async`, `smb2_rmdir_async`, `smb2_mkdir_async`, `smb2_fstat_async`, `smb2_stat_async`, `smb2_statvfs_async`, `smb2_truncate_async`, `smb2_rename_async`, `smb2_ftruncate_async`, and `smb2_readlink_async`.

SMB3 security helpers include `smb2_derive_key`, `smb3_init_preauth_hash`, `smb3_update_preauth_hash`, and `smb2_create_signing_key`. Utility APIs include `smb2_get_max_read_size`, `smb2_get_max_write_size`, `smb2_get_file_id`, `smb2_fh_from_file_id`, `smb2_fd_event_callbacks`, `smb2_oplock_break_notify`, `smb2_decode_filenotifychangeinformation`, and `free_smb2_file_notify_change_information`.

The server side is handled by request callbacks such as `smb2_logoff_request_cb`, `smb2_tree_connect_request_cb`, `smb2_create_request_cb`, `smb2_read_request_cb`, `smb2_write_request_cb`, `smb2_ioctl_request_cb`, `smb2_query_directory_request_cb`, `smb2_query_info_request_cb`, `smb2_set_info_request_cb`, `smb2_session_setup_request_cb`, `smb2_negotiate_request_cb`, plus the listening loop `smb2_serve_port` and accept helper `smb2_serve_port_async`.

## Control Flow

Client share connection starts in `smb2_connect_share_async`: it stores server/share on the context, builds a `\\server\share` UNC in UTF-8 and UTF-16, then calls `smb2_connect_async`. `connect_cb` sends an SMB2 negotiate request with dialects based on configured version and encryption capability when applicable. `negotiate_cb` records server limits, dialect, cipher, and capabilities; enforces requested signing/encryption; auto-selects Kerberos or NTLMSSP from the SPNEGO mechanism list if the security mode was undefined; initializes auth data; and sends session setup. `session_setup_cb` handles `MORE_PROCESSING_REQUIRED` by sending the next auth token, otherwise extracts the session key for NTLMSSP or Kerberos, derives signing and encryption keys, validates a signed final session setup response when present, and issues tree connect unless passthrough mode suppresses it.

Directory enumeration opens a directory with `CREATE`, then loops `QUERY_DIRECTORY` until `SMB2_STATUS_NO_MORE_FILES`. `decode_dirents` converts file-id-full-directory-information records into linked `smb2_dirent_internal` entries with stat-like fields. Once enumeration is complete, a `CLOSE` command finalizes the directory handle and publishes the populated `smb2dir`.

File operations are single request/response flows for open, close, flush, read, write, fstat, and ftruncate. Read and write clamp transfer sizes to negotiated max sizes and available credits, then update `fh->offset` on successful completion. `smb2_lseek` is local-only state mutation based on `fh->offset` and `fh->end_of_file`.

Path operations such as unlink, mkdir, stat, statvfs, truncate, rename, and readlink are compound PDU flows. They typically `CREATE` the target, perform `QUERY_INFO`, `SET_INFO`, `IOCTL`, or `CLOSE` using `compound_file_id`, and aggregate statuses across callbacks before invoking the public callback.

Server mode starts with `smb2_serve_port`, which initializes defaults, binds/listens, accepts clients, allocates an SMB2 context per client, and drives active contexts through `select` and `smb2_service`. Request callbacks dispatch to `server->handlers` when present, build command replies or `STATUS_NOT_IMPLEMENTED`/related errors, set response message IDs to match requests, and queue replies. Negotiation chooses the highest mutually supported dialect, initializes preauth hashing, sets signing/encryption capabilities, emits SPNEGO negotiate data, and prepares the next expected PDU.

## State And Persistence Behavior

This file is almost entirely in-memory state. Persistent external effects are network I/O on SMB sockets and remote filesystem mutations requested through SMB2. `smb2_context` fields mutated here include fd, message/session/tree IDs, server/share/user, negotiated dialect and sizes, credits, signing/sealing flags, preauth hash, session/signing/encryption keys, security mode, client GUID, callbacks, active PDU pointers, and server association. `smb2fh` instances persist remote file IDs and local offsets until close/free. `smb2dir` stores a linked list of decoded directory entries until `smb2_closedir`.

Authentication state is owned indirectly through `connect_data->auth_data` and freed by `free_c_data` using NTLMSSP or Kerberos-specific destructors. `smb2_close_context` closes the fd, notifies fd-change callbacks, clears session/tree IDs, and frees the session key, but does not destroy the whole context. The server loop owns accepted contexts until disconnection, timeout, explicit close, or final cleanup.

## Dependencies And Integration Points

The implementation depends on libsmb2 internal protocol builders/parsers from `libsmb2-raw.h`, `libsmb2-private.h`, SMB2 command modules, `pdu.c`, socket helpers, Unicode conversion, timestamp conversion, error conversion, SPNEGO wrappers, NTLMSSP, optional Kerberos wrappers, signing, HMAC/SHA utilities, and portable endian helpers. Public callers integrate through `libsmb2.h` callbacks and through event-loop fd callbacks registered by `smb2_fd_event_callbacks`. Server users provide `struct smb2_server` handlers for authorization and command-specific filesystem behavior.

## Risks And Edge Cases

Many async allocation failure paths return without freeing previously allocated callback state or request context. Examples include some `smb2_pread_async`, `smb2_pwrite_async`, and `smb2_ftruncate_async` PDU creation failures where newly allocated state may leak. Compound request builders must keep stack request payloads valid only until PDU encoding; this relies on command builders copying input synchronously.

Credit clamping can reduce read/write count to `smb2->credits * 65536`; if credits are unexpectedly zero, requests may be built with zero-length transfers. Directory and file-notify decoders trust decoded offsets and converted names heavily; malformed server replies need fuzz coverage around offset arithmetic and recursive notify decoding.

Security-sensitive paths include signing/encryption key derivation, SMB 3.1.1 preauth hash sequencing, and signature verification during final session setup. A missed preauth update or wrong label/context length can break interoperability or weaken SMB3 validation. In `smb2_oplock_break_notify`, the lease branch uses `memset(&rep_lease, 0, sizeof(rep_oplock))`, which appears to clear using the wrong structure size and should be reviewed.

Server mode is functional but handler-dependent. Unimplemented handlers return protocol errors, and authorization/session establishment correctness depends on `server->handlers`. The select loop is single-threaded and iterates the global active-context list, so destruction during iteration is handled carefully in some places but remains a high-risk area for lifecycle bugs.

## Test Signals

Useful tests include connection negotiation across SMB2.0.2, SMB2.1, SMB3.0, SMB3.0.2, and SMB3.1.1 with signing required, encryption requested, passthrough mode, NTLMSSP, and Kerberos builds. File API tests should cover open flag mapping, lease/oplock create contexts, offset updates after read/write, EOF reads, max-read/write clamping, fstat/stat/statvfs decoding, truncate and rename compounds, readlink on symlink and non-reparse targets, and directory enumeration over multi-response directories. Server tests should exercise each handler dispatch, unsupported command responses, negotiate/session setup state transitions, anonymous versus password auth, tree connect/disconnect cleanup, and fd event notifications. Fuzzing should target directory entry decoding, notify-change decoding, create/query/set compound replies, and SMB3 preauth/signature validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/libsmb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/md4.h -->
# sources/user-network-fs/libsmb2/lib/md4.h

## Purpose

`md4.h` declares the bundled RSA Data Security MD4 API used by libsmb2 for NTLM password hashing. NTLMv1/NTLMv2 derives the NT hash by applying MD4 to the UTF-16LE password, so this header is part of the authentication support surface rather than a general-purpose public crypto API.

## Important APIs, Types, And Functions

`MD4_CTX` stores four 32-bit chaining words, a 64-bit bit count split into two 32-bit words, and a 64-byte block buffer. The declared API is `MD4Init(MD4_CTX *)`, `MD4Update(MD4_CTX *, unsigned char *, unsigned int)`, and `MD4Final(unsigned char[16], MD4_CTX *)`.

## Control Flow

Callers initialize a context, feed one or more byte ranges, then finalize into a 16-byte digest. In this repository the direct consumer is `NTOWFv1` in `ntlmssp.c`, which converts a password to UTF-16 and hashes that buffer.

## State And Persistence Behavior

All state is caller-owned in `MD4_CTX`. The digest API has no file, network, heap, or global persistence. `MD4Final` in the implementation zeroizes the context after producing the digest.

## Dependencies And Integration Points

The header requires `uint32_t` to be available from configuration-driven includes in consumers; `md4c.c` includes `config.h`, `stdint.h`, `compat.h`, and this header. The integration point is NTLMSSP authentication, not SMB2 framing.

## Risks And Edge Cases

The update function accepts a mutable `unsigned char *` instead of `const unsigned char *`, which is an old API shape and can force casts in callers. MD4 is cryptographically broken and must be treated only as a protocol compatibility primitive for NTLM, never as a new integrity or password-storage primitive. Header consumers must ensure `stdint.h` or equivalent definitions are available before `MD4_CTX` is parsed.

## Test Signals

Test with RFC 1320 MD4 vectors, split updates versus one-shot updates, empty input, inputs around 55/56/63/64/65 bytes, and NTLM known password-to-NT-hash vectors through `ntlmssp.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/md4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/md4c.c -->
# sources/user-network-fs/libsmb2/lib/md4c.c

## Purpose

`md4c.c` is a bundled RFC 1320 MD4 implementation. It supplies the `MD4Init`, `MD4Update`, and `MD4Final` functions declared by `md4.h`, primarily so NTLMSSP can derive NT password hashes without depending on an external crypto library.

## Important APIs, Types, And Functions

The public functions are `MD4Init`, `MD4Update`, and `MD4Final`. Internal helpers include `MD4Transform` for the three MD4 compression rounds, `Encode` and `Decode` for little-endian 32-bit word conversion, and local loop-based `MD4_memcpy`/`MD4_memset`. Macros `F`, `G`, `H`, `ROTATE_LEFT`, `FF`, `GG`, and `HH` implement the MD4 round functions and rotations.

## Control Flow

`MD4Init` seeds the standard MD4 initial chaining state and clears the bit count. `MD4Update` updates the bit count, fills any partial 64-byte block, transforms full blocks, and stores remaining bytes in the context buffer. `MD4Final` encodes the original bit length, pads to 56 bytes modulo 64, appends the length, encodes the final state into a 16-byte digest, and zeroizes the context. `MD4Transform` decodes one 64-byte block into sixteen 32-bit words, runs all 48 MD4 operations over three rounds, adds the result back into the chaining state, and clears the temporary word array.

## State And Persistence Behavior

The only persistent state is the caller-provided `MD4_CTX` between calls. Static `PADDING` is read-only padding data. Finalization wipes the context and transform wipes the local decoded block. No heap allocations, file I/O, or network state are used.

## Dependencies And Integration Points

The file includes `config.h` when available, `stdint.h` when configured, `compat.h`, and `md4.h`. Its main integration is `NTOWFv1` in `ntlmssp.c`, which passes UTF-16 password bytes to `MD4Update`. It is built as part of the libsmb2 library.

## Risks And Edge Cases

MD4 is obsolete and collision-prone; the risk is acceptable only for NTLM protocol compatibility. The implementation assumes 32-bit arithmetic wraparound on `uint32_t`, which is standard for unsigned C integers. The API length type is `unsigned int`, so extremely large single updates depend on repeated calls and the split 64-bit count. The helper signatures are non-const for input buffers, reflecting the original implementation style.

## Test Signals

Use known MD4 vectors for empty string, `a`, `abc`, `message digest`, alphabet strings, and long numeric strings. Include incremental update tests that split input at every byte position around block boundaries. NTLM integration tests should verify the MD4 digest of UTF-16LE passwords matches known NT hashes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/md4c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/md5.c -->
# sources/user-network-fs/libsmb2/lib/md5.c

## Purpose

`md5.c` is a bundled Colin Plumb public-domain MD5 implementation. In this source set it supports NTLMSSP-related HMAC-MD5 operations indirectly through the library's MD5/HMAC code, not SMB2 packet framing by itself.

## Important APIs, Types, And Functions

The public API is `MD5Init`, `MD5Update`, `MD5Final`, and `MD5Transform`. On big-endian builds, `byteSwap` converts words between host order and MD5 little-endian order; on little-endian builds it is a no-op macro. Internal macros `F1` through `F4` and `MD5STEP` implement the four MD5 rounds.

## Control Flow

`MD5Init` seeds the four standard MD5 chaining words and clears the byte counter. `MD5Update` accumulates bytes into `ctx->in`, transforms a completed first partial block, processes all full 64-byte blocks, and stores the tail. `MD5Final` appends `0x80`, zero padding, and the 64-bit bit count, transforms the final block, byte-swaps the digest words if needed, copies 16 digest bytes to the caller, and clears the context. `MD5Transform` performs the full 64-step compression function over one 512-bit block.

## State And Persistence Behavior

All mutable state lives in the caller-provided `struct MD5Context`: four digest words, a two-word byte count, and a sixteen-word input block. `MD5Final` clears the context after digest extraction. There is no heap allocation, global mutable state, file I/O, or network behavior.

## Dependencies And Integration Points

The file includes optional `config.h`, `sys/types.h`, `compat.h`, and `md5.h`. `md5.h` supplies `UWORD32`, `md5byte`, endianness configuration, and the context layout. NTLMSSP uses HMAC-MD5 via `hmac-md5.c`, which depends on this MD5 implementation.

## Risks And Edge Cases

MD5 is cryptographically broken for collision resistance and should only be used where the protocol requires it, such as NTLMv2 HMAC-MD5 compatibility. The byte counter is two 32-bit words and update length is `unsigned`, so very large streams rely on correct carry behavior across repeated calls. Endianness behavior depends on `__BYTE_ORDER` and platform defines from configuration; big-endian and unusual console targets need explicit build/test coverage. Context clearing in `MD5Final` helps but does not wipe caller copies of input or digest.

## Test Signals

Use RFC 1321 MD5 vectors, split update tests around 56- and 64-byte boundaries, long multi-block inputs, and big-endian byte-swap tests where possible. Integration tests should verify HMAC-MD5 outputs used by NTLMv2 response generation and verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/md5.h -->
# sources/user-network-fs/libsmb2/lib/md5.h

## Purpose

`md5.h` declares the bundled MD5 context and functions used by libsmb2 crypto helpers, especially HMAC-MD5 for NTLMSSP. It preserves the Colin Plumb public-domain MD5 API while adapting integer and endian definitions to this project's portability layer.

## Important APIs, Types, And Functions

The header defines `md5byte` as `unsigned char`, `UWORD32` as `uint32_t` when not already defined and not on excluded targets, and `struct MD5Context` with `buf[4]`, `bytes[2]`, and `in[16]`. It declares `MD5Init`, `MD5Update`, `MD5Final`, and `MD5Transform`, with C++ linkage guards.

## Control Flow

Consumers allocate a `struct MD5Context`, initialize it, call `MD5Update` for one or more byte ranges, and finalize into a 16-byte digest. `MD5Transform` is exposed for code that wants direct block compression, though normal callers should use the streaming API.

## State And Persistence Behavior

The header defines only caller-owned in-memory state. No persistent storage or global state is introduced. The implementation clears the context during finalization.

## Dependencies And Integration Points

The header includes `config.h` when available, optional `netinet/in.h`, `string.h`, `sys/types.h`, and `stdint.h`. It derives `WORDS_BIGENDIAN` from `__BYTE_ORDER` or `XBOX_360_PLATFORM`. Its direct integration is `md5.c`; higher-level use is through HMAC-MD5 and NTLMSSP response generation/verification.

## Risks And Edge Cases

The preprocessor expression for `WORDS_BIGENDIAN` depends on platform macros being defined consistently. Targets without `uint32_t` or with `PS2_IOP_PLATFORM` need compatible `UWORD32` definitions elsewhere. MD5 is legacy cryptography and should not be exposed as a recommended hashing primitive outside protocol compatibility code.

## Test Signals

Compile on little-endian, big-endian, C, and C++ builds. Verify MD5 known vectors through the public API and run HMAC-MD5/NTLMSSP integration tests to ensure the context layout and endian settings match `md5.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/md5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ntlmssp.c -->
# sources/user-network-fs/libsmb2/lib/ntlmssp.c

## Purpose

`ntlmssp.c` implements NTLMSSP authentication blob generation, parsing, and verification for libsmb2 client and server modes. It generates NTLM negotiate, challenge, and authenticate messages, optionally wraps/unwraps them in SPNEGO, derives NTLMv2 responses and exported session keys, and verifies client authenticate blobs on the server side.

## Important APIs, Types, And Functions

The central private type is `struct auth_data`, which stores the current output buffer, parsed NTLM challenge copy, user/domain/password/workstation strings, target name/info, client and server challenges, SPNEGO wrapping flag, authentication result, timestamp, and exported session key.

Public functions include `ntlmssp_init_context`, `ntlmssp_destroy_context`, `ntlmssp_set_spnego_wrapping`, `ntlmssp_get_spnego_wrapping`, `ntlmssp_get_authenticated`, `ntlmssp_generate_blob`, `ntlmssp_authenticate_blob`, `ntlmssp_get_session_key`, and `ntlmssp_get_message_type`. `ntlmssp_get_utf16_field` is externally visible in the C file but not declared in the header.

Important private helpers include `encoder` for append-only output buffer construction, `encode_ntlm_negotiate_message`, `ntlm_decode_challenge_message`, `ntlm_convert_password_hash`, `NTOWFv1`, `NTOWFv2`, `encode_temp`, `encode_ntlm_auth`, and `encode_ntlm_challenge`.

## Control Flow

Client-side generation starts with `ntlmssp_generate_blob` receiving `input_buf == NULL`, which emits a negotiate message and optionally SPNEGO-wraps it. When a challenge blob arrives, `ntlmssp_get_message_type` unwraps SPNEGO if needed and identifies the NTLMSSP message type. For a challenge, `ntlm_decode_challenge_message` copies selected challenge fields, appends a target-name AV pair, and stores target info. If no domain was configured, the target name can become the SMB2 domain and trigger password lookup from file. `encode_ntlm_auth` then computes the NTLMv2 response using `NTOWFv2`, the server challenge, timestamp, client challenge, and target info; builds an authenticate message with domain/user/workstation fields; and stores the exported session key.

Server-side generation receives a negotiate message and calls `encode_ntlm_challenge`, which emits a challenge message, target info, timestamp, and server challenge. When an authenticate message arrives, `ntlmssp_generate_blob` calls `ntlmssp_authenticate_blob`, marks `is_authenticated` based on the verification result, and optionally emits a SPNEGO auth result.

Verification in `ntlmssp_authenticate_blob` parses UTF-16 domain/user/workstation fields, updates the SMB2 context identity, asks `server->handlers->authorize_user` for authorization/password data, supports anonymous if allowed, extracts the NTLMv2 response and temp blob, recomputes `ResponseKeyNT` and `NTProofStr`, compares it to the response, derives the exported session key, and wipes the SMB2 password after use.

## State And Persistence Behavior

`auth_data` owns heap buffers and strings for the lifetime of an authentication exchange. `encoder` grows `auth_data->buf` geometrically and appends protocol fields. The exported session key remains in `auth_data->exported_session_key` until copied by `ntlmssp_get_session_key`, which allocates a fresh key buffer for the caller. Server verification writes user/domain/workstation into the `smb2_context`, and clears the password string after computing the proof. No disk persistence is performed directly, though client generation can call `smb2_set_password_from_file` after learning a domain.

## Dependencies And Integration Points

The file depends on endian helpers, UTF-16 conversion, SMB2 time conversion, SMB2 context setters, SPNEGO wrapper functions, MD4, MD5, and HMAC-MD5. It integrates tightly with `libsmb2.c` session setup: client negotiation calls `ntlmssp_generate_blob` for outgoing tokens and `ntlmssp_get_session_key` for signing/encryption keys; server session setup calls `ntlmssp_get_message_type`, `ntlmssp_generate_blob`, `ntlmssp_get_authenticated`, and `ntlmssp_get_session_key`.

## Risks And Edge Cases

This is security-sensitive code. The server challenge in `encode_ntlm_challenge` is deterministic bytes `1..8`, which is unsuitable for real authentication because NTLM challenges must be unpredictable to prevent replay/precomputation attacks. `ntlmssp_init_context` unconditionally copies eight bytes from `client_challenge`, so callers must never pass NULL. Several challenge parsing paths perform partial bounds checks but still rely on offsets from untrusted blobs; malformed SPNEGO/NTLM inputs need fuzzing, especially target-name and target-info offsets.

The code uses MD4 and MD5/HMAC-MD5 because NTLM requires them; they should not be generalized. Endian conversions in some parse paths use host-to-little macros where little-to-host would be clearer, which is harmless on little-endian but risky on big-endian. The `ntlm:` password-hash shortcut validates only length/prefix and then converts hex characters without rejecting non-hex input. Password and key material is partly cleared (`smb2_set_password(smb2, "")`, context frees), but not all temporary arrays are explicitly zeroized.

SPNEGO wrapping state is inferred from incoming blobs and carried in `auth_data->spnego_wrap`; mismatches between wrapped and raw tokens can break negotiation. Anonymous behavior depends on server policy and empty user/password semantics. `ntlmssp_get_utf16_field` checks the descriptor offset but not that `field_off + field_len` stays within `input_len`, creating a malformed-input risk.

## Test Signals

Client tests should cover raw NTLMSSP and SPNEGO-wrapped negotiate/challenge/authenticate flows, configured domain versus domain learned from challenge target name, password-file lookup after domain discovery, anonymous auth, `ntlm:<hash>` credentials, and exported session-key use for SMB signing. Server tests should cover handler authorization success/failure, anonymous allowed/disallowed, malformed authenticate fields, wrong password proof, and session key extraction. Security tests should require random server challenges before production server use. Fuzz tests should target `ntlmssp_get_message_type`, `ntlm_decode_challenge_message`, `ntlmssp_get_utf16_field`, and `ntlmssp_authenticate_blob` with truncated and offset-corrupt blobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ntlmssp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ntlmssp.h -->
# sources/user-network-fs/libsmb2/lib/ntlmssp.h

## Purpose

`ntlmssp.h` declares libsmb2's NTLMSSP authentication interface used by SMB2 session setup in both client and server modes. It hides `struct auth_data` internals and exposes blob generation, authentication verification, SPNEGO wrapping controls, message-type parsing, and session-key extraction.

## Important APIs, Types, And Functions

The header defines NTLMSSP message constants `NEGOTIATE_MESSAGE`, `CHALLENGE_MESSAGE`, and `AUTHENTICATION_MESSAGE`, forward-declares `struct auth_data`, and declares `ntlmssp_init_context`, `ntlmssp_destroy_context`, `ntlmssp_set_spnego_wrapping`, `ntlmssp_get_spnego_wrapping`, `ntlmssp_get_message_type`, `ntlmssp_generate_blob`, `ntlmssp_authenticate_blob`, `ntlmssp_get_authenticated`, and `ntlmssp_get_session_key`.

## Control Flow

Callers create an auth context with user/password/domain/workstation/client-challenge data, optionally set SPNEGO wrapping, then exchange blobs through `ntlmssp_generate_blob`. Server session setup can call `ntlmssp_authenticate_blob` directly or via `ntlmssp_generate_blob` handling of an authentication message, then query authenticated state and session key. `ntlmssp_get_message_type` is used to detect raw or SPNEGO-wrapped NTLMSSP tokens before choosing the auth path.

## State And Persistence Behavior

The header exposes an opaque heap-owned context lifetime: `ntlmssp_init_context` allocates it, `ntlmssp_destroy_context` releases it, and `ntlmssp_get_session_key` returns a newly allocated key buffer to the caller. There is no persistent storage contract in the header.

## Dependencies And Integration Points

The header includes optional `config.h`, defines `_GNU_SOURCE`, supports C++ linkage, and references `struct smb2_context` and `struct smb2_server` types supplied by libsmb2 internal headers in including translation units. Its main integration is `libsmb2.c` session setup.

## Risks And Edge Cases

The API requires callers to manage ownership carefully: output blobs point at `auth_data` internal storage, while session keys are separately allocated for the caller. `client_challenge` is typed as `const char *` but semantically must point to at least eight binary bytes. The header name guard `_GSSAPI_WRAPPER_H_` does not match the NTLMSSP header name, which can confuse maintainers and risks collision with an actual GSSAPI wrapper guard.

## Test Signals

Compile tests should include C and C++ consumers and all security configurations. API tests should verify context creation/destruction, SPNEGO flag round trips, raw and wrapped message-type parsing, blob exchange sequencing, authenticated-state reporting, and ownership of returned session keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ntlmssp.h -->
