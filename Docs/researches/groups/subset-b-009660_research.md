# Research Group subset-b-009660

This grouped report covers libsmb2 error mapping, HMAC helpers, context initialization/configuration, and Kerberos/GSSAPI authentication glue under `sources/user-network-fs/libsmb2/lib`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/errors.c -->
# sources/user-network-fs/libsmb2/lib/errors.c

## Purpose
`errors.c` is libsmb2's central translation table for SMB2/NTSTATUS failures. It exposes readable NT status names for diagnostics and converts selected server status codes into POSIX `errno` values that higher-level sync and async APIs can return to callers.

## Important APIs, Types, and Functions
The file exports `nterror_to_str(uint32_t status)` and `nterror_to_errno(uint32_t status)`. Both consume status constants from `smb2.h`, primarily `SMB2_STATUS_*` values. `nterror_to_str()` is a large switch returning static string literals. `nterror_to_errno()` maps a curated subset of SMB2 status codes to system errors such as `ENOENT`, `EACCES`, `EBADF`, `EINVAL`, `ENETRESET`, and `EIO`.

## Control Flow
`nterror_to_str()` performs one direct switch over the status code. Known codes return immediately; unknown codes fall through to `"Unknown"`. `nterror_to_errno()` also uses a switch, but groups semantically related statuses: missing path/object statuses become `ENOENT`, invalid handles become `EBADF`, authentication restrictions become `EACCES`, retryable transport/session tear-down statuses become `ENETRESET`, and the default is `EIO`. `SMB2_STATUS_SUCCESS` and `SMB2_STATUS_END_OF_FILE` intentionally map to zero.

## State and Persistence Behavior
The file has no mutable static state and performs no allocation or persistence. All outputs are deterministic for the input status and the platform's `errno` macro definitions. Returned strings are static literals and must not be freed.

## Dependencies and Integration Points
It depends on `errno.h`, optional platform headers from `config.h`, `compat.h`, and libsmb2 status definitions in `smb2.h`. It is used wherever libsmb2 reports protocol errors through `smb2_set_nterror()`, callback statuses, or POSIX-style API return paths.

## Risks and Edge Cases
The string mapper is manually maintained and may lag new status constants. Some returned names include the `SMB2_` prefix while others use Windows-style `STATUS_`, which can matter for logs or tests that compare strings exactly. Unknown status values are collapsed to `"Unknown"` and `EIO`, losing diagnostic precision. A few mappings are policy choices rather than exact POSIX equivalents, such as `STATUS_PATH_NOT_COVERED` to `ENOEXEC` and several disconnect/reset statuses to `ENETRESET` to encourage retry handling.

## Test Signals
Useful tests should cover representative status groups, not every switch arm: success/EOF to zero, missing paths to `ENOENT`, invalid handles to `EBADF`, access failures to `EACCES`, retryable disconnects to `ENETRESET`, unknown values to `EIO`/`"Unknown"`, and exact string names for high-frequency statuses such as `STATUS_ACCESS_DENIED`, `STATUS_LOGON_FAILURE`, `STATUS_SHARING_VIOLATION`, and `STATUS_BAD_NETWORK_NAME`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/errors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/hmac-md5.c -->
# sources/user-network-fs/libsmb2/lib/hmac-md5.c

## Purpose
`hmac-md5.c` implements the RFC 2104 HMAC-MD5 construction used by NTLM/SMB authentication paths that require MD5-based keyed digests. It is a small one-shot helper around the repository's MD5 implementation.

## Important APIs, Types, and Functions
The exported function is `smb2_hmac_md5(unsigned char *text, int text_len, unsigned char *key, unsigned int key_len, unsigned char *digest)`. It uses `struct MD5Context` plus `MD5Init()`, `MD5Update()`, and `MD5Final()` from `md5.h`. The caller supplies the message buffer, key buffer, and a 16-byte digest output buffer.

## Control Flow
If the key is longer than the 64-byte MD5 block size, the function first hashes it to a 16-byte temporary key. It zeroes 65-byte inner and outer pad arrays, copies the key into each, XORs the first 64 bytes with `0x36` and `0x5c`, computes the inner digest over `ipad || text`, then computes the final digest over `opad || inner_digest`.

## State and Persistence Behavior
The function keeps all state on the stack and writes only to the caller-provided `digest`. It performs no heap allocation and no persistence. Temporary key and pad buffers contain key material until the stack frame is reused; they are not explicitly wiped.

## Dependencies and Integration Points
It depends on `compat.h`, `md5.h`, optional `strings.h`, and the declaration in `hmac-md5.h`. In libsmb2 this is part of the legacy NTLM crypto support surface alongside MD4/MD5/HMAC-SHA helpers and is expected to produce exactly 16 bytes.

## Risks and Edge Cases
The API accepts mutable pointers even though the text and key are not intentionally modified. `text_len` is signed while the MD5 update API receives the value as a length, so negative lengths from callers would be hazardous. The function assumes non-NULL buffers and an adequately sized digest. MD5 is cryptographically obsolete outside protocols such as NTLM that require it for compatibility.

## Test Signals
Use RFC 2104 HMAC-MD5 known-answer vectors, a key longer than 64 bytes, an empty message, an empty key, and a normal NTLM-sized key/message. Memory-safety tests should include NULL/invalid caller behavior at API boundaries if the surrounding library promises defensive checks elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/hmac-md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/hmac-md5.h -->
# sources/user-network-fs/libsmb2/lib/hmac-md5.h

## Purpose
`hmac-md5.h` declares libsmb2's HMAC-MD5 helper and provides compatibility typedef setup needed by the bundled MD5 code on supported platforms.

## Important APIs, Types, and Functions
The public declaration is `smb2_hmac_md5(...)`, which computes a 16-byte MD5 HMAC into a caller-owned buffer. The header conditionally includes `config.h`, `string.h`, `sys/types.h`, and `stdint.h`, defines `WORDS_BIGENDIAN` for big-endian or Xbox builds, and defines `UWORD32` as `uint32_t` unless excluded for PS2 or Pico platforms.

## Control Flow
There is no runtime control flow. Preprocessor branches select platform configuration and C++ linkage. The `extern "C"` block makes the function callable from C++ translation units without name mangling.

## State and Persistence Behavior
The header has no runtime state. Its main persistent effect is compile-time: it can define `WORDS_BIGENDIAN` and `UWORD32_DEFINED`, which may affect included or neighboring crypto compilation units.

## Dependencies and Integration Points
It is included by callers that need the one-shot MD5 HMAC routine implemented in `hmac-md5.c`. The `UWORD32` and endian definitions are compatibility glue for the MD5 implementation rather than SMB protocol logic.

## Risks and Edge Cases
The comment says `RFC1204` although HMAC-MD5 is normally associated with RFC 2104. The endian macro relies on `__BYTE_ORDER`/`__BIG_ENDIAN` being available from prior configuration headers. Because the function signature does not use `const`, callers may be forced to cast const buffers even though the implementation does not mutate them.

## Test Signals
Compile tests should cover C and C++ consumers, big-endian macro paths, platforms without `stdint.h`, and callers that include the header before MD5-related headers. API tests should verify the digest size contract through `smb2_hmac_md5()` known-answer vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/hmac-md5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/hmac.c -->
# sources/user-network-fs/libsmb2/lib/hmac.c

## Purpose
`hmac.c` implements RFC 2104 HMAC over the SHA family described by the repository's RFC 4634-style SHA abstraction. It supports one-shot and streaming HMAC computation for SHA-1, SHA-224, SHA-256, SHA-384, and SHA-512 through the `USHA` interface.

## Important APIs, Types, and Functions
The exported API includes `hmac()`, `hmacReset()`, `hmacInput()`, `hmacFinalBits()`, and `hmacResult()`. The main state type is `HMACContext`, defined with SHA context fields in `sha.h`. The code uses `SHAversion`, `USHAContext`, `USHABlockSize()`, `USHAHashSize()`, `USHAReset()`, `USHAInput()`, `USHAFinalBits()`, and `USHAResult()`.

## Control Flow
`hmac()` is a one-shot wrapper that resets a stack context, feeds the entire message, and finalizes the digest. `hmacReset()` validates the context, records the selected SHA variant, hashes overlong keys down to the selected hash length, builds inner and outer pads for the selected block size, stores the outer pad in `ctx->k_opad`, and starts the inner SHA pass with the inner pad. `hmacInput()` streams message bytes into the inner SHA context. `hmacFinalBits()` forwards final non-byte-aligned bits. `hmacResult()` finalizes the inner digest into the caller's digest buffer, reinitializes SHA, hashes the outer pad plus inner digest, and writes the final HMAC.

## State and Persistence Behavior
HMAC state is fully caller-owned through `HMACContext`. The context persists the selected SHA version, block/hash sizes, inner SHA state, and outer pad between reset and result. The one-shot wrapper uses only stack state. Temporary keys and pads are not wiped after use.

## Dependencies and Integration Points
The file depends on `compat.h`, `sha.h`, optional `config.h`, `stdint.h`, and `stdlib.h`. It is a generic crypto primitive for libsmb2 signing/key derivation paths that require HMAC-SHA, especially SMB2/SMB3 authentication and session security code elsewhere in the library.

## Risks and Edge Cases
Most functions check only for a NULL context, not NULL key, text, or digest pointers. Error propagation relies on logical OR chaining; callers receive the first nonzero SHA error but not detailed stage context. `hmacResult()` uses the caller's digest buffer as a temporary inner digest, so the buffer must be at least `USHAMaxHashSize` or at least the selected hash size as required by the SHA API. Key material remains in stack/context memory until overwritten.

## Test Signals
Use RFC 4231/RFC 4634 HMAC-SHA known-answer vectors across SHA-1/SHA-256/SHA-512, including long keys, empty messages, streaming input split across several calls, `hmacFinalBits()`, NULL context returns, and digest agreement between one-shot `hmac()` and reset/input/result sequences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/hmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/init.c -->
# sources/user-network-fs/libsmb2/lib/init.c

## Purpose
`init.c` owns libsmb2 context creation, destruction, URL parsing, error storage, credential setters, active-context tracking, I/O vector helpers, and miscellaneous context configuration APIs. It is the lifecycle and configuration entry point for most client-side libsmb2 users.

## Important APIs, Types, and Functions
Key public functions include `smb2_parse_url()`, `smb2_destroy_url()`, `smb2_init_context()`, `smb2_destroy_context()`, `smb2_active_contexts()`, `smb2_context_active()`, `smb2_free_iovector()`, `smb2_add_iovector()`, `smb2_set_error()`, `smb2_set_nterror()`, `smb2_get_error()`, `smb2_get_nterror()`, `smb2_set_client_guid()`, credential setters/getters, security/sign/seal/version/timeout setters, passthrough and oplock callback setters, and `smb2_delegate_credentials()`. The private parser `smb2_parse_args()` handles URL query arguments.

## Control Flow
`smb2_parse_url()` validates the `smb://` prefix and maximum URL size, parses query arguments, then splits optional `domain;user@server/share/path` components into an allocated `smb2_url`. `smb2_parse_args()` mutates the query string in place, recognizes `seal`, `sign`, `ndr3264`, `ndr32`, `ndr64`, endian flags, `sec=krb5|krb5cc|ntlmssp`, dialect `vers=...`, and `timeout=...`, and rejects incompatible `seal` use with non-SMB3 dialects. `smb2_init_context()` seeds pseudo-random client challenge/salt/guid data, defaults the user from `getlogin_r()` or `Guest`, initializes transport and negotiation defaults, and links the context into the global active list. `smb2_destroy_context()` closes sockets, cancels queued/current/waiting PDUs with shutdown/cancel statuses, frees buffers and credentials, releases optional GSS credentials, unlinks the context, and frees it. Setter functions replace owned strings with `strdup()` copies and trigger password-file lookup where relevant.

## State and Persistence Behavior
The file maintains a process-global `active_contexts` singly linked list. Each `smb2_context` owns socket descriptors, connecting file descriptors, queued PDUs, input vectors, error strings, NT status, session keys, encryption state, credentials, callbacks, and optional delegated GSS credentials. `smb2_set_password_from_file()` reads the `NTLM_USER_FILE` environment variable and loads a matching `domain:user:password` line, using empty-domain entries as defaults. No repository files are written, but credentials can be loaded from an external user file and retained in the context.

## Dependencies and Integration Points
It depends on `libsmb2.h`, `libsmb2-private.h`, `smb2.h`, `slist.h`, `compat.h`, socket/time/errno/unistd headers, and optional GSS/Kerberos symbols behind `HAVE_LIBKRB5`. Other libsmb2 modules rely on this file for context allocation, cleanup callbacks, error reporting, URL parsing, authentication mode selection, and pass-through credential delegation.

## Risks and Edge Cases
`smb2_parse_url()` leaks the allocated `smb2_url` if it fails after allocation because some error paths return NULL without calling `smb2_destroy_url()`. Query parsing writes NUL bytes into the local URL copy and assumes options with required values actually have `value`; malformed `sec`, `vers`, or `timeout` arguments without `=` can lead to NULL dereferences. `smb2_get_libsmb2Version()` assigns `patch_version` from `LIBSMB2_MAJOR_VERSION`, which looks suspicious. Random material is generated with `srandom/random`, suitable for protocol nonces only if the broader library accepts that strength. The global active list is not synchronized, so multi-threaded context create/destroy/enumerate needs external discipline.

## Test Signals
Tests should cover valid and invalid URL forms, query combinations, seal with SMB2 rejection and SMB3 acceptance, credential file matching by domain/server/default, setter replacement/free behavior, destroy callbacks for outqueue/current/waitqueue PDUs, active-list membership before and after destroy, iovector capacity overflow cleanup, error callback invocation, and Kerberos credential delegation when compiled with and without `HAVE_LIBKRB5`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/krb5-wrapper.c -->
# sources/user-network-fs/libsmb2/lib/krb5-wrapper.c

## Purpose
`krb5-wrapper.c` implements libsmb2's Kerberos/GSSAPI bridge when `HAVE_LIBKRB5` is enabled. It creates client initiator credentials, server acceptor credentials, drives GSS security-context token exchange for SMB session setup, extracts SMB session keys, supports keytab-backed server caches, and optionally saves delegated credentials for pass-through/proxy scenarios.

## Important APIs, Types, and Functions
The main lifecycle functions are `krb5_negotiate_reply()`, `krb5_session_request()`, `krb5_session_get_session_key()`, `krb5_init_server_client_cred()`, `krb5_session_reply()`, `krb5_init_server_credentials()`, `krb5_renew_server_credentials()`, `krb5_free_server_credentials()`, and `krb5_free_auth_data()`. Support functions include `display_status()`, `krb5_set_gss_error()`, token accessors, non-Apple `establish_contexts()`/`init_accept_sec_context()` for S4U/proxy credential setup, and `krb5_can_do_ntlmssp()`. Shared state is held in `struct private_auth_data`.

## Control Flow
The client path starts with `krb5_negotiate_reply()`: it builds a `cifs@host` service name, imports target and user names, optionally consumes a delegated credential from `smb2->cred_handle`, optionally creates a private MEMORY credential cache for `krb5cc` password mode, acquires initiator credentials, and may constrain SPNEGO negotiation to Kerberos or NTLMSSP. `krb5_session_request()` releases any previous output token, wraps an incoming server token if present, and calls `gss_init_sec_context()` with sequence, mutual, and replay flags to generate the next session setup token. `krb5_session_get_session_key()` queries `GSS_C_INQ_SSPI_SESSION_KEY` and copies the first returned key into `smb2->session_key`.

The server path uses `krb5_init_server_credentials()` to prepare keytab-backed server state and a private memory ccache, then `krb5_renew_server_credentials()` to kinit from the keytab into that cache. Per client, `krb5_init_server_client_cred()` imports the server SPN and acquires acceptor or both-way credentials, optionally using `gss_acquire_cred_from()` with the keytab and ccache from server auth data. `krb5_session_reply()` accepts a client token with `gss_accept_sec_context()`, returns continuation status through `more_processing_needed`, displays and splits the authenticated `user@domain` into the SMB context, optionally performs S4U2Self-style impersonation when proxy credentials are required, and stores or releases delegated credentials depending on `smb2->passthrough`.

## State and Persistence Behavior
`private_auth_data` owns a GSS context, credential handle, imported user and target names, selected mechanism OID, current output token, optional service string, optional krb5 context, memory ccache, principal, keytab, and server credentials. Client memory ccaches are destroyed in `krb5_free_auth_data()`, so they do not persist across process lifetime. Server keytab paths are external; the code stores credentials into a private memory cache and refreshes them from the keytab. `smb2->session_key`, `smb2->user`, `smb2->domain`, and `smb2->cred_handle` are mutated as authentication completes.

## Dependencies and Integration Points
The file depends on GSSAPI/Kerberos headers, Apple GSS framework variants, `libsmb2.h`, `libsmb2-raw.h`, `libsmb2-private.h`, `smb2.h`, `slist.h`, and OIDs declared in `krb5-wrapper.h`. It integrates with SMB session setup token exchange, SMB3 signing/encryption key derivation via `smb2->session_key`, server pass-through mode, `sec=krb5`, `sec=krb5cc`, and optional NTLMSSP-over-GSS support when the platform GSS stack provides the NTLM mechanism.

## Risks and Edge Cases
Several allocation/error paths return without fully freeing partially initialized `auth_data`, especially after imported names or generated service strings. `krb5_free_auth_data()` assumes a non-NULL pointer and is called with NULL in one allocation-failure path, which would dereference NULL if reached. `gss_inquire_sec_context_by_oid()` failure paths do not release any partially returned buffer set, and replacing `smb2->session_key` does not free an existing key first. `ret_delegated_cred_handle` in `krb5_session_reply()` is not initialized before `gss_accept_sec_context()` and should only be trusted according to returned flags/status. Apple paths lack several proxy/NTLMSSP capabilities. The code uses process-global GSS ccache selection calls, so concurrent authentication using different ccaches may need scrutiny.

## Test Signals
Test with Kerberos enabled and disabled builds; client initiator auth using default ccache, password-created MEMORY ccache, delegated credentials, and forced `sec=krb5`/`sec=ntlmssp`; multi-token mutual-auth exchanges; session-key extraction failure and success; server acceptor auth with default credentials and keytab-backed credentials; keytab renewal; proxy/pass-through delegated credential retention and release; Apple vs non-Apple capability paths; and malformed/expired credentials with clear `smb2_get_error()` text.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/krb5-wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/krb5-wrapper.h -->
# sources/user-network-fs/libsmb2/lib/krb5-wrapper.h

## Purpose
`krb5-wrapper.h` declares the Kerberos/GSSAPI authentication interface used by libsmb2 and defines the private authentication state shared between SMB client/server session setup and the implementation in `krb5-wrapper.c`.

## Important APIs, Types, and Functions
The key type is `struct private_auth_data`, which contains GSS context and credential handles, user and target names, mechanism selection, request flags, current output token, proxy/SPNEGO flags, a service-name string, krb5 context/cache/principal/keytab handles, and stored server credentials. The header declares token accessors, client negotiation/session functions, server credential/session functions, GSS error formatting, NTLMSSP capability probing, and cleanup helpers.

## Control Flow
There is no runtime control flow in the header. Preprocessor guards expose all declarations only when `HAVE_LIBKRB5` is defined. Non-Apple builds include `gssapi_ext.h` and define a SPNEGO OID; all builds define Kerberos and NTLMSSP mechanism OID descriptors used by the implementation to constrain or detect mechanisms.

## State and Persistence Behavior
The header defines ownership-bearing fields but does not allocate them. The implementation is responsible for releasing GSS buffers, names, contexts, creds, krb5 ccaches, keytabs, principals, and `g_server`. Because the struct is private to the libsmb2 build rather than a stable public ABI, field changes must be coordinated with all internal users.

## Dependencies and Integration Points
It depends on `config.h`, `krb5/krb5.h`, Apple `GSS/GSS.h` or standard `gssapi.h`/`gssapi_ext.h`, and forward declarations for `struct smb2_context`/`struct smb2_server` from included SMB headers in translation units. It is the contract between SMB session setup code and Kerberos support.

## Risks and Edge Cases
The header exposes `static const gss_OID_desc` objects in every including translation unit, which is fine for internal use but means pointer identity is per translation unit. Some prototypes reference `struct smb2_context` and `struct smb2_server` without declaring them locally, so include order must provide those types. The declared `krb5_negotiate_request()` is not implemented in the inspected `krb5-wrapper.c`, suggesting either a stale prototype or an implementation elsewhere that should be verified during link tests.

## Test Signals
Compile coverage should include `HAVE_LIBKRB5` on/off, Apple and non-Apple GSS headers, C++ inclusion, and link checks for every declared function. Runtime tests are driven through `krb5-wrapper.c`: token accessors, cleanup ownership, mechanism selection, server credential initialization, and NTLMSSP capability probing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/krb5-wrapper.h -->
