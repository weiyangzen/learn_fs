# subset-b-009900 Research

Grouped research for Samba `source4/auth` GENSEC, Kerberos, NTLM, and Python authentication binding files. Each section preserves the source path and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.c -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.c

Purpose: implements a `tstream_context` adapter that transparently wraps and unwraps a plain stream with an established GENSEC security context. It is used after a mechanism has negotiated signing or sealing and exposes normal async `readv`, `writev`, pending-byte, and disconnect operations over protected PDUs.

Important APIs and types: `_gensec_create_tstream()` allocates `struct tstream_gensec`, validates `GENSEC_FEATURE_SIGN` or `GENSEC_FEATURE_SEAL`, records maximum wrap sizes from `gensec_max_input_size()` and `gensec_max_wrapped_size()`, and installs `tstream_gensec_ops`. `struct tstream_gensec` persists the underlying `plain_stream`, `gensec_security`, sticky `errno` value, write limits, and unread unwrapped bytes. Async state types include `tstream_gensec_readv_state`, `tstream_gensec_writev_state`, and a minimal disconnect state.

Control flow: reads first drain any buffered plaintext from `tgss->read.unwrapped`. If callers still need bytes, `tstream_readv_pdu_send()` asks `tstream_gensec_readv_next_vector()` for a 4-byte little-endian length header and then the wrapped blob. The completion path calls `gensec_unwrap()`, steals the plaintext into the stream object, and loops back to fill the caller vectors. Writes copy caller iovecs into chunks no larger than `max_unwrapped_size`, wrap each chunk via `gensec_wrap()`, prefix a 4-byte length using `RSIVAL`, and send header plus blob over the plain stream.

State and persistence: stream failure is sticky through `tgss->error`; future operations immediately complete with that error. Buffered plaintext is kept across reads with offset and remaining-byte counters. Disconnect only detaches the wrapper from the plain stream and marks `ENOTCONN`; the caller still owns the real lower-level disconnect.

Dependencies and integration: depends on Samba talloc, tevent, tsocket/tstream internals, DATA_BLOB helpers, and GENSEC wrap/unwrap APIs. It integrates with higher-level protocols that want a stream abstraction after SPNEGO/Kerberos/NTLMSSP negotiation.

Risks and test signals: the reader rejects zero and extremely large message lengths above `0x0fffffff`, a key fuzz and interoperability boundary. Tests should cover fragmented reads, multi-iovec writes, partial buffered plaintext, wrap failure causing sticky `EIO`, lower-stream errors, signed-only and sealed mechanisms, and disconnect behavior. The header length is the wrapped blob size, so any peer using a different record framing will fail.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.h -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.h

Purpose: public declaration for the GENSEC-backed `tstream_context` constructor. It keeps callers insulated from the implementation in `gensec_tstream.c` while preserving Samba's location-tracking allocation pattern.

Important APIs and types: forward-declares `struct gensec_context` and `struct tstream_context`, then declares `_gensec_create_tstream(TALLOC_CTX *, struct gensec_security *, struct tstream_context *, struct tstream_context **, const char *location)`. The macro `gensec_create_tstream()` supplies `__location__` automatically so allocation/debug traces identify the call site.

Control flow and state: the header has no runtime state, but its API contract implies the caller provides an already-negotiated GENSEC security object and a live plain tstream. The output pointer receives a wrapper stream that shares or references the lower stream rather than taking over all disconnect responsibility.

Dependencies and integration: consumed by authentication and protocol code that converts a negotiated GENSEC exchange into stream protection. It requires the including translation unit to have `NTSTATUS`, `TALLOC_CTX`, and `struct gensec_security` visible through Samba auth headers.

Risks and test signals: ABI consumers depend on the macro and symbol name. Header tests are build-level: include it from C files with minimal prerequisites, verify autoproto/export visibility, and ensure callers pass a mechanism with sign or seal negotiated because the implementation rejects otherwise.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/pygensec.c -->
# sources/user-network-fs/samba/source4/auth/gensec/pygensec.c

Purpose: Python extension module `samba/gensec.so` exposing Samba's Generic Security interface as `gensec.Security`. It lets Python tests and tools create client/server GENSEC contexts, choose mechanisms, perform update dances, wrap/unwrap packets, sign/check DCE/RPC packets, and inspect session information.

Important APIs and types: class constructors are `Security.start_client(settings=None)` and `Security.start_server(settings=None, auth_context=None)`. `settings_from_object()` expects a Python dict containing `target_hostname` and `lp_ctx`. Methods wrap `gensec_set_target_hostname`, `gensec_set_target_service`, `gensec_set_credentials`, `gensec_start_mech_by_name`, `gensec_start_mech_by_sasl_name`, `gensec_start_mech_by_authtype`, `gensec_update`, `gensec_wrap`, `gensec_unwrap`, `gensec_sign_packet`, `gensec_check_packet`, `gensec_session_info`, and `gensec_session_key`. Module constants mirror `GENSEC_FEATURE_*`.

Control flow: constructors allocate a talloc stackframe, initialize settings or global loadparm defaults, call `gensec_init()`, then `gensec_client_start()` or `gensec_server_start()` and transfer ownership to a pytalloc Python object. `update()` copies the input bytes because lower GENSEC code may mutate its input, returns `(finished, blob_out)`, and treats `NT_STATUS_MORE_PROCESSING_REQUIRED` as a successful nonterminal result. Wrap/unwrap and packet signing allocate a temporary talloc context, call the C API, return Python bytes, and translate NTSTATUS failures into Python exceptions.

State and persistence: Python `Security` instances own a `struct gensec_security` through pytalloc. Target names, credentials, selected mechanism, negotiated features, session keys, and security context state are stored in that native object. Temporary DATA_BLOBs are freed before returning; returned Python bytes own their copies.

Dependencies and integration: depends on Python C API, pytalloc, pyparam, pycredentials, pyrpc_util, pyerrors, tevent, and GENSEC internals. It is built as `samba/gensec.so` by the local wscript and is a primary test and scripting surface for authentication mechanisms.

Risks and test signals: `settings_from_object()` sets specific `ValueError`s but callers in constructors turn a NULL settings result into `PyErr_NoMemory()`, which can mask configuration errors. Packet functions parse `z#` buffers and require correct Python 3 size macro setup. Tests should cover missing settings keys, default loadparm creation, auth context type checking, mechanism selection failures, multi-step updates, sign/seal feature negotiation, and bytes-copy behavior for mutable GENSEC backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/pygensec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/wscript_build -->
# sources/user-network-fs/samba/source4/auth/gensec/wscript_build

Purpose: Waf build declarations for source4 GENSEC support modules and Python bindings.

Important build targets: `gensec_util` builds `gensec_tstream.c` with `tevent-util`, `tevent`, `samba-util`, and `LIBTSOCKET`, producing `gensec_proto.h`. `gensec_krb5` chooses either `gensec_krb5_heimdal.c` or `gensec_krb5_mit.c` depending on `SAMBA_USES_MITKDC`, initializes with `gensec_krb5_init`, and is enabled for AD DC builds. `gensec_krb5_helpers` is also AD DC gated. `gensec_gssapi` builds the GSSAPI mechanism. `pygensec` builds `pygensec.c` as `samba/gensec.so` with pytalloc and pyparam helper libraries.

Control flow and state: no runtime control flow, but build-time feature selection decides which Kerberos implementation is compiled and whether AD DC-only helpers are available. The declarations feed Samba's module registration system through subsystem names, init functions, and internal/external module flags.

Dependencies and integration: integrates auth GENSEC with Samba credentials, authkrb5, GSSAPI, com_err, talloc, Python embedding, and host configuration. Build failures here usually appear as missing generated prototypes, unresolved module init functions, or Python extension load errors.

Risks and test signals: test both MIT and Heimdal configurations, AD DC enabled/disabled builds, static and shared module layouts, and Python import of `samba.gensec`. Dependency drift in pyembed library names or Kerberos config symbols can silently omit features from downstream tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos.h -->
# sources/user-network-fs/samba/source4/auth/kerberos/kerberos.h

Purpose: central source4 Kerberos public header gated by `HAVE_KRB5`. It collects Kerberos wrappers, containers, token identifiers, encryption masks, and PAC creation prototypes used by GENSEC, KDC, and authentication code.

Important APIs and types: `struct ccache_container` binds an `smb_krb5_context` to a `krb5_ccache`; `struct keytab_container` binds the context to a `krb5_keytab` and records whether it is password based. RFC 1964/GSS token IDs are defined for AP-REQ, AP-REP, KRB-ERROR, GETMIC, and WRAP. Encryption masks include `ENC_ALL_TYPES` and `ENC_STRONG_SALTED_TYPES`. Compatibility prototypes cover missing krb5 functions. Exports include `smb_krb5_princ_component()`, `kerberos_encode_pac()`, and `kerberos_create_pac()`.

Control flow and state: the header defines no execution but establishes ownership expectations: ccache/keytab wrappers carry the Kerberos context required for cleanup and operations. PAC APIs take explicit KDC and service keyblocks because PAC checksums have two signing roles.

Dependencies and integration: includes system Kerberos headers, Samba auth headers, `krb5_init_context.h`, generated PAC NDR structures, and Samba krb5 wrappers. It includes generated `auth/kerberos/proto.h`, so implementation exports are collected through autoproto.

Risks and test signals: compile coverage must exercise `HAVE_KRB5` on/off, MIT/Heimdal compatibility macros, and consumers that include this header without unnecessary krb5 exposure. Security tests should verify that encryption masks match supported AD policy behavior and that PAC creation callers provide the correct krbtgt and service keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_credentials.h -->
# sources/user-network-fs/samba/source4/auth/kerberos/kerberos_credentials.h

Purpose: small public header for Kerberos credential helper functions used by GENSEC and authentication callers that need to convert Samba credentials into Kerberos principals or credential caches without including broader internal implementation details.

Important APIs: `kinit_to_ccache()` obtains Kerberos initial credentials into a supplied ccache using `cli_credentials`, an `smb_krb5_context`, loadparm context, tevent context, and returns credential provenance plus an error string. `principal_from_credentials()` parses the Kerberos principal implied by `cli_credentials` and reports how the credential was obtained.

Control flow and state: the header has no direct state. The API signatures reveal that callers provide the destination cache and event context; the implementation may perform network KDC operations and set event hooks on Heimdal contexts while acquiring tickets.

Dependencies and integration: depends on `struct cli_credentials`, `struct smb_krb5_context`, `struct loadparm_context`, `struct tevent_context`, and Samba credential provenance enum definitions. It bridges auth credential storage with Kerberos ticket acquisition.

Risks and test signals: consumers should check both return code and `error_string`. Tests need password, keyblock/NT-hash, FAST armor, S4U impersonation, missing-principal, and clock-skew cases. Build tests should ensure this header remains light enough for callers that do not otherwise use raw krb5 APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_credentials.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_pac.c -->
# sources/user-network-fs/samba/source4/auth/kerberos/kerberos_pac.c

Purpose: creates, signs, parses, and converts Kerberos PAC data between krb5 PAC buffers and Samba domain-controller auth structures. It is a security-critical bridge between Kerberos tickets and `auth_user_info_dc`.

Important APIs: `kerberos_encode_pac()` computes checksum placeholder lengths, zeroes signatures, NDR-serializes the PAC, signs the server checksum with the service key, signs that checksum with the krbtgt key for the KDC checksum, then serializes final PAC bytes. `kerberos_create_pac()` builds a four-buffer PAC containing LOGON_INFO, LOGON_NAME, SRV_CHECKSUM, and KDC_CHECKSUM from `auth_user_info_dc`. `kerberos_pac_to_user_info_dc()` parses LOGON_INFO and optional UPN_DNS_INFO, converts to `auth_user_info_dc`, optionally extracts server/KDC signatures and resource groups, and infers TGT vs non-TGT from the REQUESTER_SID buffer. `kerberos_pac_blob_to_user_info_dc()` parses a raw blob into a krb5 PAC then calls the converter.

Control flow: creation allocates a `PAC_DATA`, fills buffer descriptors, converts Samba user info to `netr_SamInfo3`, unparses the client principal without realm for LOGON_NAME, sets logon time from TGS auth time, and delegates signing. Parsing pulls krb5 buffers, uses NDR pull helpers, frees krb5-owned data promptly, calls `make_user_info_dc_pac()`, and moves the resulting structures to caller memory.

State and persistence: PAC data and parsed user info are talloc-owned; no global state. The function intentionally steals nested resource-group arrays when returning them. Ticket-type inference persists in `user_info_dc_out->ticket_type`.

Dependencies and integration: depends on Heimdal/MIT PAC APIs, Samba NDR PAC definitions, auth SAM reply conversion, credentials, Kerberos utility wrappers, and PAC checksum helpers. Used by Kerberos session-info generation and KDC ticket paths.

Risks and test signals: checksum order and key choice are security boundaries. Tests should cover missing checksum buffers, invalid NDR, absent UPN_DNS_INFO, optional resource groups, REQUESTER_SID ticket type heuristic, MIT behavior requiring allocated buffer reads, and malformed PAC blobs. Comments note deterministic NDR push assumptions for signing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_pac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_util.c -->
# sources/user-network-fs/samba/source4/auth/kerberos/kerberos_util.c

Purpose: implements Kerberos credential, principal, ccache, and keytab utility functions used across source4 authentication.

Important APIs and types: `struct principal_container` wraps a `krb5_principal` with an `smb_krb5_context` and talloc destructor. `principal_from_credentials()` and the static impersonation helper parse principal strings from `cli_credentials`. `smb_krb5_create_principals_array()` creates krb5 principals from SPNs plus an account/realm principal. `kinit_to_ccache()` obtains tickets into an existing ccache using passwords, S4U2Self/S4U2Proxy-style impersonation, or an RC4 keyblock from an NT hash. `smb_krb5_get_keytab_container()`, `smb_krb5_remove_obsolete_keytab_entries()`, and `smb_krb5_is_exact_entry_in_keytab()` manage keytab handles and entries.

Control flow: principal parsing allocates wrapper state before calling krb5 so cleanup is simple. Ticket acquisition builds get-init-creds options, sets forwardable and canonicalization behavior, optionally configures FAST armor, wraps Heimdal KDC I/O with the caller's tevent context, tries twice for clock-skew recovery, updates krb5 real time when needed, and may retry after wrong-password callbacks refresh credentials. Keytab cleanup enumerates entries, compares against target principals and kvno, releases cursors before deletion, and restarts enumeration after deletion.

State and persistence: krb5 principal and keytab lifetime is tied to talloc destructors. `kinit_to_ccache()` mutates the supplied ccache and may adjust the krb5 context's time offset. Keytab helpers persist changes in the keytab file or memory keytab.

Dependencies and integration: depends on Samba credentials, Kerberos credential wrappers, Heimdal/MIT macros, libkrb5, loadparm, tevent, and Samba keytab comparison helpers. It is called by GENSEC Kerberos, keytab export/update code, and credential cache acquisition.

Risks and test signals: FAST support is feature-macro dependent and returns EINVAL if required but unavailable. S4U impersonation requires a password, not only a keyblock. Keytab kvno comparison masks to 8 bits to handle file formats, so tests must include kvno wraparound. Ticket acquisition tests should cover password, NT-hash keyblock, FAST, skew, wrong-password refresh, missing principal, and cleanup of krb5 objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.c -->
# sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.c

Purpose: wraps krb5 context initialization and, for Heimdal builds, routes Kerberos KDC network I/O through Samba's tevent/socket stack. It also wires Kerberos logging into Samba debug output and sets embedded Heimdal flags from Samba configuration.

Important APIs and types: `struct smb_krb5_socket` holds socket, fd event, status, request/reply blobs, packet parser, and Heimdal host info. `smb_krb5_init_context_basic()` creates a raw krb5 context, applies Samba krb5.conf/default realm on Heimdal, and registers the send-to-KDC plugin once. `smb_krb5_init_context()` allocates `struct smb_krb5_context`, installs a destructor, initializes logging, and applies embedded Heimdal flags. Heimdal-only `smb_krb5_context_set_event_ctx()` and `_remove_event_ctx()` install and restore tevent-aware KDC send functions.

Control flow: UDP reads use `socket_pending()` then `socket_recv()`. TCP uses Samba packet framing with a 4-byte length prefix and strips that prefix on full packets. `smb_krb5_send_and_recv_func_int()` iterates addrinfo entries, creates UDP or TCP sockets, connects, registers fd events and timeout, sends the request, loops tevent until reply or error, copies reply to krb5 memory, and tries the next address on timeout or network error.

State and persistence: `smb_krb5_context` owns `krb5_context`, optional Heimdal log facility, and current tevent reference. A global `smb_krb5_plugin_db` maps krb5 context pointers to per-context send-to-KDC callback state. Destructors remove plugin records and free krb5/log resources.

Dependencies and integration: depends on Samba socket, packet, tsocket, resolve, param, dbwrap_rbt, Kerberos send_to_kdc plugin APIs, and embedded Heimdal internals when available. It is foundational for all source4 Kerberos code.

Risks and test signals: global plugin registration and pointer-keyed dbwrap state are concurrency-sensitive. Tests should cover nested tevent loops, restoring previous event contexts, UDP/TCP fallback, timeout behavior, KDC unreachable mapping, IPv4/IPv6, config-file precedence, realm setting, logging cleanup, and embedded Heimdal PAC/canonical-client flags. MIT builds bypass most plugin code and need separate coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.h -->
# sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.h

Purpose: public declarations for Samba's Kerberos context wrapper.

Important APIs and types: `struct smb_krb5_context` holds the raw `krb5_context`, private log data, and current tevent context. `smb_krb5_init_context_basic()` returns a raw initialized krb5 context configured for Samba. `smb_krb5_init_context()` returns the talloc-managed wrapper. Heimdal builds also expose callback typedefs for send-to-realm and send-to-KDC functions plus event-context install/remove helpers.

Control flow and state: the header defines ownership: callers receive a talloc-owned wrapper whose destructor frees the krb5 context. Heimdal event helpers temporarily associate a tevent loop with Kerberos network operations and restore previous state after use.

Dependencies and integration: requires krb5 types, talloc, tevent, and loadparm declarations. Included by `kerberos.h`, credential helpers, and GENSEC Kerberos code.

Risks and test signals: build tests need MIT, system Heimdal, and embedded Heimdal configurations. Runtime tests should ensure callers do not outlive referenced event contexts and that nested Kerberos operations restore the previous `current_ev`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/srv_keytab.c -->
# sources/user-network-fs/samba/source4/auth/kerberos/srv_keytab.c

Purpose: service keytab creation and update utilities for Samba AD accounts, including group Managed Service Account key extraction.

Important APIs: `keytab_add_keys()` derives keys for each enctype/principal/kvno and avoids adding exact duplicates. `smb_krb5_fill_keytab()` parses the salt principal, maps supported encryption types, adds current keys, and optionally previous keys. `smb_krb5_fill_keytab_gmsa_keys()` reads gMSA managed password data from samdb and populates a keytab with salted AES keys. `smb_krb5_update_keytab()` opens a keytab, builds principals from account/SPNs, removes obsolete entries, and fills current/previous keys. `smb_krb5_create_memory_keytab()` creates a random `MEMORY:` keytab name and delegates update.

Control flow: update resolves the keytab, uppercases realm, creates principal array, removes stale kvnos, optionally validates `saltPrincipal`, and fills the keytab unless this is delete-only mode. gMSA flow re-queries password attributes, builds temporary credentials, sets realm/username/kvno, restricts enctypes to strong salted AES, parses current and previous managed passwords, derives a salt principal, and fills one principal.

State and persistence: file keytabs are modified in place; memory keytabs persist under generated `MEMORY:<random>` names while handles remain open. Old keys may be retained for kvno-1 depending on cleanup findings and `include_historic_keys`. Principal arrays and salt principals are explicitly freed.

Dependencies and integration: uses Samba credentials, credentials_krb5, Kerberos utility functions, gMSA NDR/DSDB helpers, samdb, and Kerberos enctype conversion helpers. It supports domain exportkeytab, machine account keytab refresh, and gMSA service operation.

Risks and test signals: key derivation depends on the correct salt principal and enctype mask. gMSA intentionally drops RC4 because UTF16-munged to UTF8 conversion can corrupt RC4 password material. Tests should cover duplicate suppression, old-key retention, delete-only mode, missing salt principal, SPN plus account principal generation, gMSA missing password/kvno/enctype attributes, memory keytab creation, and error strings on failed keytab writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/srv_keytab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/wscript_build -->
# sources/user-network-fs/samba/source4/auth/kerberos/wscript_build

Purpose: Waf build declarations for source4 Kerberos support.

Important build targets: `KRB_INIT_CTX` builds `krb5_init_context.c` with `gssapi`, `krb5samba`, `dbwrap`, and `samba-util`. Private library `authkrb5` builds `kerberos_pac.c`, generates `proto.h`, exposes public dependencies on generated PAC NDR, `krb5samba`, Samba sockets, and resolve code, and links packet/NDR/LDB/KRB5 PAC/error helpers. `KERBEROS_UTIL` builds `kerberos_util.c` with generated `kerberos_util.h` and credential/Kerberos dependencies. `KERBEROS_SRV_KEYTAB` builds `srv_keytab.c` with generated `kerberos_srv_keytab.h`.

Control flow and state: no runtime behavior; build-time configuration decides whether Kerberos code is compiled through `HAVE_KRB5` and related Samba feature macros in the C sources. The target graph controls availability for GENSEC Kerberos, KDC, keytab export, and authentication code.

Dependencies and integration: integrates `krb5_init_context.c`, `kerberos_pac.c`, `kerberos_util.c`, and `srv_keytab.c` into distinct build products used by GENSEC, KDC, auth, and keytab code. Header-only files such as `kerberos.h`, `kerberos_credentials.h`, and `krb5_init_context.h` are consumed by those compiled units rather than listed as sources here.

Risks and test signals: both MIT and Heimdal builds should verify this target pulls the correct compatibility dependencies. AD DC disabled builds, static builds, and generated-prototype cleanup are important signals because many consumers include `auth/kerberos/proto.h`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth.c

Purpose: core NTLM/auth4 framework: creates auth contexts, manages challenges, runs configured auth backends, logs auth events, creates session info, and registers auth modules.

Important APIs and types: `auth_context_set_challenge()` and `auth_get_challenge()` manage fixed or random 8-byte challenges. `auth_check_password_send/recv()` drives the async backend chain; `auth_check_password()` is the synchronous poll wrapper. `auth_context_create_methods()`, `auth_context_create()`, and `auth_context_create_for_netlogon()` build `auth4_context` objects with selected methods. `auth_register()`, `auth_backend_byname()`, `auth_interface_version()`, and `auth4_init()` implement module registration. Session wrappers include `auth_generate_session_info_wrapper()` and PAC-based `auth_generate_session_info_pac()`.

Control flow: password checking maps missing `mapped` names from client names, ensures a challenge, then walks `auth_method_context` entries. A backend may decline with `NT_STATUS_NOT_IMPLEMENTED` or non-authoritative failure, allowing the next method. The receive path logs success or failure with audit info and returns `auth_user_info_dc`. Session generation marks non-guest users authenticated, calls `auth_generate_session_info()`, and optionally fills Unix token info.

State and persistence: `auth4_context` stores event/message/loadparm/sam contexts, start time, challenge data, method list, netlogon flag, and function pointers used by upper layers. Backend registrations live in static global `backends` and `num_backends` initialized once.

Dependencies and integration: depends on tevent, Samba modules, samdb, winbind client, credentials, Kerberos PAC conversion, roles, auth logging, and Unix token helpers. It is the central integration point for anonymous, SAM, winbind, developer, LDAP simple bind, NTLMSSP, and GENSEC consumers.

Risks and test signals: the source declares `struct auth_check_password_wrapper *state` in `auth_check_password_wrapper_send()` while the actual state type is `struct auth_check_password_wrapper_state`; this is a build-time risk if not hidden by other declarations. Tests should cover backend ordering, non-authoritative fallback, challenge reuse, fixed challenge setup, audit logging, PAC session generation, role-specific default methods, netlogon-only method selection, duplicate backend registration, and static init idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_anonymous.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_anonymous.c

Purpose: implements the `anonymous` auth4 backend, which accepts only empty anonymous credentials and produces anonymous `auth_user_info_dc`.

Important APIs: `anonymous_want_check()` decides whether a request is anonymous by checking empty account name and empty plaintext/hash/response credentials. `anonymous_check_password_send/recv()` returns `auth_anonymous_user_info_dc()` output through tevent. `auth4_anonymous_init()` registers the backend.

Control flow: nonempty account names or password material return `NT_STATUS_NOT_IMPLEMENTED`, allowing later backends to try. Empty acceptable anonymous input creates a tevent request, builds anonymous user info with the configured NetBIOS name, posts completion, and returns the interim info in recv.

State and persistence: no global state beyond backend registration. Each request stores only a temporary `auth_user_info_dc`. Audit info outputs are NULL.

Dependencies and integration: depends on `auth/auth.h`, generated auth prototypes, loadparm NetBIOS name, tevent, and tevent NTSTATUS helpers. Default auth method lists put this backend first so anonymous logons are handled consistently.

Risks and test signals: the LM response special case permits a single zero byte as anonymous but rejects other nonempty responses. Tests should cover plaintext empty vs nonempty, hash pointers present/absent, NT response length, no account name, backend registration collision, and ordering before SAM/winbind.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_anonymous.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_developer.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_developer.c

Purpose: developer-only auth backend `name_to_ntstatus` for testing obscure NTSTATUS values and status-to-DOS mappings. It is enabled only in developer builds by the wscript.

Important APIs: `name_to_ntstatus_want_check()` accepts all requests. `name_to_ntstatus_check_password()` interprets the username as either an `NT_STATUS...` symbolic code or a hexadecimal status value, returns that failure if non-OK, or builds a minimal anonymous-like successful `auth_user_info_dc` when the status is OK. Async send/recv wrappers expose it as an auth backend. `auth4_developer_init()` registers it.

Control flow: password material is ignored. The username controls the returned status. On success it allocates user info, sets one anonymous SID with default group flags, zero session keys, domain/account fields, empty profile/home strings, timestamps and counters at zero, and normal account flags.

State and persistence: no persistent state except backend registration. It intentionally manufactures auth state for tests rather than consulting SAM or winbind.

Dependencies and integration: depends on auth structures, security SID definitions, tevent, and NTSTATUS string conversion. Built as `auth4_developer` only when `DEVELOPER_MODE` is true.

Risks and test signals: this backend must never be enabled in production configurations. Tests should assert build gating, username-to-status parsing, successful fabricated session shape, and backend registration. Because `want_check` always accepts, method ordering can mask real auth backends in developer mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_developer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_sam.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_sam.c

Purpose: implements local SAM-backed NTLM authentication backends `sam` and `sam_ignoredomain`, including password validation, account policy checks, bad-password accounting, protected-user restrictions, authentication policy enforcement, RODC replication triggers, and previous-password grace behavior.

Important APIs: `authsam_password_ok()` validates plaintext/hash/response credentials against NT hashes or AES256 Kerberos supplemental credentials. `authsam_password_check_and_record()` obtains current and historical secrets, checks lockout, tries previous passwords within policy windows, updates badPwdCount, and sets non-authoritative on RODC. `authsam_authenticate()` applies interactive restrictions, authentication policies, password checks, netlogon trust server policy, account restrictions, and success accounting. `authsam_check_password_internals()` resolves UPNs, searches SAM, builds `auth_user_info_dc`, rejects Protected Users for NTLM, and attaches session keys. `authsam_want_check()` decides domain ownership and forest routing. `auth4_sam_init()` registers `sam` and `sam_ignoredomain`.

Control flow: the backend first decides whether it owns the mapped domain/account. For AD DC UPNs it may use trust routing and later crack names to NT4 form. It loads the account, creates preliminary user info, enforces Protected Users restrictions, authenticates secrets, updates accounting, reparents audit info, and returns completed user info. Wrong passwords continue into history checks before bad-password updates; successful previous-password network auth can be allowed during configured grace periods.

State and persistence: reads and writes SAM LDB state: password hashes/supplemental credentials, account control, badPwdCount/lockout, logon accounting, and gMSA current time. It may send IRPC messages to winbind or dreplsrv for zero-password and secret-replication handling.

Dependencies and integration: depends on DSDB/SAMDB, NTLM check helpers, Kerberos AES key extraction, GKDI/gMSA utilities, authn policy utilities, winbind/drepl IRPC, roles/trust routing, and auth SAM reply conversion.

Risks and test signals: security-sensitive boundaries include constant-time hash comparisons, hiding invalid historical hashes, Protected Users denying NTLM, smartcard-required behavior, old-password grace, gMSA five-minute skew, RODC non-authoritative fallback, and authentication policy audit info. Tests should cover standalone/member/DC domain matching, UPN cracking, cross-forest rejection, no secrets on RODC, AES-only accounts, bad-password accounting failure, trust account policy, and generated session keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_sam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_server_service.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_server_service.c

Purpose: minimal service module initializer for the auth service.

Important API: `server_service_auth_init(TALLOC_CTX *ctx)` simply calls `auth4_init()` to register built-in auth4 modules when the Samba service subsystem initializes the internal `service_auth` module.

Control flow and state: there is no per-request state. The only runtime effect is triggering auth backend static initialization through `auth4_init()`, which is idempotent in `auth.c`.

Dependencies and integration: depends on `auth/auth.h` and is declared as an internal `service` subsystem module by the NTLM wscript. It ensures authentication backends are ready during server startup.

Risks and test signals: tests are startup/build oriented: loading `service_auth` should register expected auth backends exactly once and tolerate repeated initialization. Failures here would surface as missing auth backends in services rather than direct auth errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_server_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_simple.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_simple.c

Purpose: implements LDAP simple bind authentication on top of the auth4 password-check and session-info framework.

Important APIs: `authenticate_ldap_simple_bind_send()` builds an auth context, maps a DN or principal to NT4 domain/account with `crack_auto_name_to_nt4_name()`, prepares plaintext `auth_usersupplied_info`, and starts `auth_check_password_send()`. `authenticate_ldap_simple_bind_recv()` returns generated `auth_session_info`. The completion callback creates session info and logs authorization success with transport protection details.

Control flow: send allocates request state, records TLS use, remote/local addresses, service/auth descriptions, plaintext password, case-insensitive and no-Unix-account flags, and logon parameters allowing cleartext supplied passwords and trust accounts. Name cracking failures are logged immediately as authentication events. On password success, the callback sets default group/authenticated flags, calls `generate_session_info`, logs successful authz with TLS vs none, and completes.

State and persistence: per-request state holds auth context, user info, TLS flag, and resulting session info. It reads SAM through auth methods and may update accounting through `auth_sam.c`.

Dependencies and integration: depends on tevent, auth4, samdb name cracking, loadparm, tsocket addresses, and authz logging. It is the LDAP server's bridge from simple bind inputs to Samba authorization sessions.

Risks and test signals: cleartext password handling must be constrained by transport policy outside this function; this code records but does not enforce TLS. Tests should cover DN mapping, bad DN logging, TLS/non-TLS audit strings, trust-account logon parameters, wrong password, generated session flags for guest vs authenticated users, and remote/local address propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_util.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_util.c

Purpose: utility for converting user-supplied password material between plaintext, NT/LM hash, and NTLM challenge-response forms.

Important API: `encrypt_user_info(TALLOC_CTX *, struct auth4_context *, enum auth_password_state to_state, const struct auth_usersupplied_info *, const struct auth_usersupplied_info **out)` is the main exported helper. It creates shallow copies of `auth_usersupplied_info` with talloc references to preserve original lifetime while replacing password fields.

Control flow: conversion to response first converts plaintext to hashes if needed, gets the auth challenge, and then produces either NTLMv2 responses using `SMBNTLMv2encrypt_hash()` and generated names blob or NTLMv1/LM responses using `SMBOWFencrypt()` depending on loadparm client auth settings. Conversion to hash computes LM hash when possible with `E_deshash()` and NT hash with `E_md4hash()`. Unsupported conversions return `NT_STATUS_INVALID_PARAMETER`.

State and persistence: no global state. Returned user-info copies and generated blobs live under the provided memory context. Challenge data is obtained from `auth_context`, which may generate and persist a random challenge.

Dependencies and integration: used by SAM and winbind backends to normalize credentials before local checks or Netlogon SamLogon. Depends on libcli auth crypto, GnuTLS error mapping, loadparm NTLM policy, and challenge helpers.

Risks and test signals: there appears to be a likely bug in the LM branch where `SMBOWFencrypt()` writes into `blob.data` rather than `lm_blob.data`; tests should verify LM response bytes when LM auth is enabled. Other tests should cover NTLMv2 enabled/disabled, plaintext-to-hash, hash-to-response, missing LM hash fallback to NT response, crypto error mapping, invalid target states, and lifetime of shallow-copied strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_winbind.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_winbind.c

Purpose: implements the `winbind` auth4 backend, forwarding authentication to the winbind server over IRPC/Netlogon SamLogon.

Important APIs: `winbind_want_check()` accepts nonempty mapped accounts. `winbind_check_password_send()` initializes an imessaging client, binds to `winbind_server`, converts supplied credentials to either Netlogon interactive password info or network challenge-response info, fills `winbind_SamLogon`, and sends `dcerpc_winbind_SamLogon_r_send()`. `winbind_check_password_done()` converts Netlogon validation into `auth_user_info_dc`, performs local success accounting if the returned domain is local, expands local group memberships with `authsam_update_user_info_dc()`, and completes. `auth4_winbind_init()` registers the backend.

Control flow: netlogon auth contexts set `WB_SAMLOGON_FOR_NETLOGON`. Interactive logons use hash conversion and logon level 1; network logons use response conversion, current challenge, and logon level 2. The binding timeout is set to 120 seconds to allow trusted-domain and RODC scenarios. `NT_STATUS_IO_TIMEOUT` maps to `NT_STATUS_NO_LOGON_SERVERS`; non-authoritative winbind failures propagate that flag to the auth chain.

State and persistence: per-request state stores request parameters, user info, output user info, and authoritative flag. It may update local SAM logon accounting for local-domain accounts and group expansion can mutate returned token information.

Dependencies and integration: depends on winbind generated RPC, imessaging/IRPC, libwbclient, auth SAM reply conversion, local SAM search/accounting, and auth credential conversion utilities. It handles domain-member and trusted-domain authentication paths in the default method chain.

Risks and test signals: winbind server absence must produce `NO_LOGON_SERVERS`, not crashes. Tests should cover interactive vs network inputs, timeout mapping, non-authoritative fallback, local-domain accounting reset, group expansion on RODC/trusted users, netlogon internal flag, and correct use of client domain/account rather than mapped fields in Netlogon identity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_winbind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/wscript_build -->
# sources/user-network-fs/samba/source4/auth/ntlm/wscript_build

Purpose: Waf build declarations for auth4 NTLM backends, core auth4 library, and service initializer.

Important build targets: modules include `auth4_sam_module`, `auth4_anonymous`, `auth4_winbind`, `auth4_developer`, and internal service module `service_auth`. The private library `auth4` builds `auth.c`, `auth_util.c`, and `auth_simple.c` with generated `auth_proto.h`. `auth4_sam_module` is AD DC gated; `auth4_developer` is developer-mode gated.

Control flow and state: build declarations determine which backends are compiled and registered through `STATIC_auth4_MODULES`. Runtime method availability depends on these targets and configuration gates.

Dependencies and integration: links SAM backend to samdb, NTLMSSP common code, hostconfig, IRPC/messaging, db glue, and authn policy utilities. Winbind backend links generated winbind RPC, messaging, and wbclient. Core auth4 links Samba security, credentials, tevent, old wbclient, Unix token, modules, and Kerberos utilities.

Risks and test signals: test AD DC enabled/disabled, developer-mode enabled/disabled, static module registration, generated prototype coverage, and service module initialization. Dependency omissions here surface as missing backends, unresolved authn policy symbols, or failed LDAP simple bind/session generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/pyauth.c -->
# sources/user-network-fs/samba/source4/auth/pyauth.c

Purpose: Python extension module `samba/auth.so` exposing session-info helpers and an `AuthContext` object for Samba authentication and authorization scripting/tests.

Important APIs: module functions include `system_session(lp_ctx=None)`, `admin_session(lp_ctx, sid)`, `user_session(ldb, lp_ctx=None, principal=None, dn=None, session_info_flags=0)`, `session_info_fill_unix(session_info, user_name, lp_ctx=None)`, `session_info_set_unix(session_info, user_name, uid, gid, lp_ctx=None)`, and `copy_session_info(session_info)`. `AuthContext.__new__(lp_ctx=None, ldb=None, methods=None)` creates an auth4 context with default or explicit methods. The module exports `AUTH_SESSION_INFO_*` constants.

Control flow: session functions validate Python NDR/pytalloc types, convert Python loadparm and LDB objects, allocate talloc frames, call native auth/session helpers, and convert results back via `py_return_ndr_struct()`. `py_auth_context_new()` creates loadparm, optional LDB, a Samba event context, default or explicit methods, then calls `auth_context_create()` or `auth_context_create_methods()`. It talloc-references loadparm and event context to keep them alive with the auth context.

State and persistence: Python objects wrap talloc-owned native `auth_session_info` or `auth4_context`. Some session objects are stolen to NULL before returning to Python. `AuthContext` retains references to `lp_ctx` and event context but exposes no methods in this file beyond construction.

Dependencies and integration: depends on Python C API, pytalloc, pyldb, pyparam, pycredentials, security helpers, auth/session APIs, Samba events, and pyrpc utilities. It is a key Python test fixture for auth/session construction.

Risks and test signals: type validation paths should raise Python exceptions without leaking frames. `system_session()` calls `system_session(lp_ctx)` then frees the temporary loadparm context, so tests should verify returned NDR object owns needed memory. AuthContext tests should cover explicit method lists, supplied LDB vs default samdb connection, invalid SID/DN/session types, Unix token fill/set failures, and exported constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/pyauth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/pyauth.h -->
# sources/user-network-fs/samba/source4/auth/pyauth.h

Purpose: small Python-auth binding header exposing conversion helpers for `auth_session_info` Python objects.

Important APIs and types: includes pytalloc and `auth/session.h`, defines `PyAuthSession_AsSession(obj)` as a direct pytalloc extraction of `struct auth_session_info`, and declares `PyObject_AsSession(PyObject *obj)`.

Control flow and state: no runtime flow in the header. The macro assumes callers have already validated or are willing to receive NULL from pytalloc if the Python object does not wrap the expected type.

Dependencies and integration: used by C extension modules that need to accept or return Samba auth session objects. It ties Python bindings to the native `auth_session_info` layout.

Risks and test signals: because the macro does not raise Python exceptions itself, callers must perform type checks and error reporting. Build tests should ensure C files including this header have Python and pytalloc types visible. Python binding tests should exercise invalid object conversion through functions that use `PyObject_AsSession()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/pyauth.h -->
