# Research: subset-b-009928

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/sdb_to_kdb.c -->
# sources/user-network-fs/samba/source4/kdc/sdb_to_kdb.c

## Purpose

`sdb_to_kdb.c` converts Samba's internal Kerberos database representation, `struct sdb_entry`, into MIT Kerberos `krb5_db_entry` records. It is the MIT KDB-side companion to the Heimdal HDB conversion path and lets Samba-backed principals, flags, key material, salts, validity times, and private `samba_kdc_entry` context be exposed to MIT KDC code.

## Important APIs, Types, and Functions

The exported API is `sdb_entry_to_krb5_db_entry()`. Supporting helpers are `SDBFlags_to_kflags()` for `SDBFlags` to `KRB5_KDB_*` attributes, `sdb_event_to_kmod()` for modifier principal/time metadata, `sdb_salt_to_krb5_key_data()` for salt slots in `krb5_key_data`, `sdb_key_to_krb5_key_data()` for encrypted keys plus optional salt, and `free_krb5_db_entry()` for local cleanup on partial failure.

## Control Flow

The converter zeroes the target entry, initializes MIT KDB magic/length fields, copies the principal, maps flags, copies lifetime and expiration values, optionally writes modification data from `modified_by` or `created_by`, and then copies each key when `require_hwauth` is not set. Each allocation failure or Kerberos copy failure unwinds through `free_krb5_db_entry()`. On success, `k->e_data` points at the original `struct samba_kdc_entry`, and that private entry receives a back pointer to the generated KDB entry.

## State and Persistence Behavior

This file does not persist database state. It allocates MIT-owned principal, tl-data, key, and salt buffers for the lifetime of the `krb5_db_entry`. Key contents are copied out of the SDB structure and burned before free in the local cleanup path. `e_data` is a borrowed Samba-private pointer, so callers must keep the originating Samba KDC entry alive while MIT KDB code uses the converted entry.

## Dependencies and Integration Points

It depends on MIT KDB headers, Samba `sdb.h`, generated `sdb_kdb.h`, `kdc/samba_kdc.h`, and Kerberos wrapper macros such as `KRB5_KEY_TYPE`, `KRB5_KEY_LENGTH`, and `KRB5_KEY_DATA`. It is built as the `sdb_kdb` subsystem when `HAVE_KDB_H` is available and is consumed by MIT KDC integration targets in `source4/kdc/wscript_build`.

## Risks and Edge Cases

Salt handling always uses `KRB5_KDB_SALTTYPE_SPECIAL` outside disabled code, so salt semantics must match MIT KDC expectations. `require_hwauth` deliberately suppresses password keys to force smart-card/public-key style authentication. The allocation failure path in `sdb_entry_to_krb5_db_entry()` returns the existing `ret` value after a `malloc()` failure for `k->key_data`; because `ret` may still be zero there, this path is worth review. The borrowed `samba_kdc_entry` pointer and back pointer are lifetime-sensitive.

## Test Signals

Build coverage comes from the `sdb_kdb` and MIT KDC targets. Useful behavioral tests include SDB entries with multiple kvno keys, salts, `require_hwauth`, disabled/invalid principals, password expiry, and early/minimal realm lookup entries with no created timestamp. Memory tests should force salt/key allocation failures and confirm key buffers are zeroed on unwind.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/sdb_to_kdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/tests/db-glue-test.c -->
# sources/user-network-fs/samba/source4/kdc/tests/db-glue-test.c

## Purpose

`db-glue-test.c` is a cmocka unit test translation unit for `source4/kdc/db-glue.c`. It includes the implementation directly and verifies how LDAP/SAM database messages are translated into `struct sdb_entry` public-key trust data, certificate mappings, DN reversal, and byte-order reversal helpers.

## Important APIs, Types, and Functions

The file overrides `dsdb_functional_level()`, `lpcfg_strong_certificate_binding_enforcement()`, and `lpcfg_certificate_backdating_compensation()` so tests can run without a full Samba runtime. Test helpers create synthetic `ldb_message` objects with `sAMAccountName`, `objectSid`, `msDS-User-Account-Control-Computed`, `whenCreated`, `msDS-KeyCredentialLink`, and `altSecurityIdentities`. The direct implementation APIs under test include `samba_kdc_message2entry()`, `get_key_trust_public_keys()`, `parse_certificate_mapping()`, `get_certificate_mappings()`, `reverse_dn()`, and `reverse_krb5_data()`.

## Control Flow

`main()` registers a large ordered cmocka list and emits subunit output. Early tests validate empty and minimal `samba_kdc_message2entry()` input. Key trust tests feed binary-DN encoded KeyCredentialLink data for BCRYPT RSA, TPM 2.0, and DER SubjectPublicKeyInfo encodings and assert extracted bit size, modulus, and exponent. Certificate mapping tests parse X509 tags, invalid tags, duplicate fields, hex fields, issuer/subject order, RFC822, SKI, serial, and SHA1 public-key tags. Final utility tests cover DN component reversal and in-place byte reversal.

## State and Persistence Behavior

The tests allocate isolated talloc trees per test and free generated SDB entries with `sdb_entry_free()`. The only cross-test mutable state is the two global configuration override integers for certificate binding enforcement and backdating compensation. No real database writes occur; LDB contexts are in-memory scaffolding used to satisfy parser and message conversion paths.

## Dependencies and Integration Points

The unit includes `../db-glue.c`, `krb5-protos.h`, LDB, SAMDB, SDB, talloc, data blob, debug, and cmocka. It is built as `test_db_glue` by `source4/kdc/wscript_build` when Samba is built with Heimdal. It directly protects PKINIT/key-trust behavior consumed later by SDB-to-HDB conversion and KDC public-key authentication.

## Risks and Edge Cases

Because the implementation is included directly, tests can cover static helpers but can also mask link-time integration issues. The test data intentionally covers malformed KeyCredentialLink structures, duplicate Key Material and Key Usage entries, invalid key usage, and unsupported RSA private-key magic. Certificate mapping behavior is subtle: duplicate tags keep the last value, issuer DNs are reversed, serial numbers are byte-reversed from hex, and only certain tag combinations are considered strong mappings. One helper adds `altSecurityIdentifiers` rather than `altSecurityIdentities` for the empty attribute case, which appears intentional for "missing usable attribute" behavior but is easy to misread.

## Test Signals

Strong signals are successful `test_db_glue` subunit output, assertions for BCRYPT/TPM/DER public key extraction, rejection of non-hex and odd-length hex values, mapping of enforcement/backdating into `entry.mappings`, and DN reversal handling with empty, leading, trailing, repeated comma, newline, carriage-return, and mixed delimiters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/tests/db-glue-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/tests/sdb_to_hdb_test.c -->
# sources/user-network-fs/samba/source4/kdc/tests/sdb_to_hdb_test.c

## Purpose

`sdb_to_hdb_test.c` is a cmocka test file for the Heimdal conversion implementation in `source4/kdc/sdb_to_hdb.c`. It validates that SDB public-key trust and certificate mapping structures are encoded into Heimdal HDB extension ASN.1 structures correctly.

## Important APIs, Types, and Functions

The implementation APIs under test are `sdb_pub_key_to_hdb_key_trust_val()`, `sdb_cert_mapping_to_hdb_key_trust_val()`, and `sdb_certificate_mappings_to_hdb_ext()`. The main output types are `struct HDB_Ext_KeyTrust_val`, `struct HDB_Ext_CertificateMapping`, and `HDB_Ext_CertificateMappings`. Tests use `DATA_BLOB` constants and Heimdal free helpers such as `free_HDB_Ext_CertificateMapping()`.

## Control Flow

`main()` registers subunit cmocka tests. The public-key tests encode an empty RSA key, a modulus/exponent whose high bit requires a leading zero byte in DER integer encoding, and a normal modulus/exponent. Certificate mapping tests start with an empty SDB mapping and then independently populate subject name, issuer name, serial number, public key, RFC822, SKI, all fields together, and collections containing zero, one, or two mappings.

## State and Persistence Behavior

The test does not persist state. It allocates output blobs from the conversion routines, validates them byte-for-byte, and frees Heimdal-generated structures. Inputs are stack-local structures or constant data blobs.

## Dependencies and Integration Points

The file includes `../sdb_to_hdb.c` directly, `hdb_asn1.h`, cmocka, and Samba data blob helpers. It is built as `test_sdb_to_hdb` by the KDC build script under Heimdal builds. These tests are a bridge between Samba KDC database parsing and Heimdal's HDB extension encoding expected by PKINIT/key-trust consumers.

## Risks and Edge Cases

DER integer encoding is the key risk: modulus or exponent values with the top bit set must receive a leading zero byte so they are not encoded as negative integers. Empty inputs intentionally encode a valid RSA public-key sequence with zero-valued modulus and exponent. Mapping collection tests assert metadata propagation for `valid_certificate_start` and `enforcement_mode`, but they do not deeply inspect every encoded mapping in multi-entry arrays.

## Test Signals

Useful signals are exact DER byte comparisons for the three public-key cases, null-field assertions for empty certificate mappings, strong-mapping flag propagation, and correct allocation/free behavior under ASAN or valgrind when converting one and multiple certificate mappings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/tests/sdb_to_hdb_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/wdc-samba4.c -->
# sources/user-network-fs/samba/source4/kdc/wdc-samba4.c

## Purpose

`wdc-samba4.c` implements Samba's Heimdal KDC plugin table for Windows domain controller behavior. It supplies PAC generation, PAC verification/update, client access checks, supported encryption type padata, referral policy, and hardware-auth policy hooks.

## Important APIs, Types, and Functions

The exported symbol is `struct krb5plugin_kdc_ftable kdc_plugin_table`. Important hooks include `samba_wdc_get_pac()`, `samba_wdc_verify_pac()`, `samba_wdc_reget_pac()`, `samba_wdc_check_client_access()`, `samba_wdc_finalize_reply()`, `samba_wdc_referral_policy()`, and `samba_wdc_hwauth_policy()`. Support helpers include `samba_wdc_is_s4u2self_req()`, `samba_wdc_verify_pac2()`, `get_netbios_name()`, and `samba_kdc_build_supported_etypes()`.

## Control Flow

PAC generation detects S4U2Self and PKINIT freshness flags, initializes a PAC, gets any device PAC, and calls `samba_kdc_get_pac()`, carrying server audit info and NTSTATUS e-data back into the Heimdal request. PAC verification checks RODC/trust conditions, rejects untrustworthy delegated-proxy tickets without a local/signing krbtgt key, fetches a signing krbtgt when the PAC signature RODC id differs from the ticket header, verifies KDC/ticket signatures when needed, and then calls Samba PAC validation. PAC update creates a replacement PAC with potentially refreshed groups, delegated proxy data, device data, and audit status. Client access checks device policy first, then workstation/password-change/account policy, and lets Heimdal continue standard checks by returning `KRB5_PLUGIN_NO_HANDLE` on success.

## State and Persistence Behavior

The plugin itself has no persistent private state; init stores `NULL`, and fini is a no-op. It mutates request-scoped state by attaching audit info and NTSTATUS through `hdb_samba4_set_*()` helpers, by replacing PAC contents, and by setting ticket-expiry or policy-related error outcomes. It allocates temporary talloc contexts per hook and frees them before return.

## Dependencies and Integration Points

The file integrates Heimdal KDC plugin APIs, Samba KDC glue, HDB/SDB conversion, PAC glue, authentication policy utilities, generated auth NDR types, krb5 local APIs, and filesystem replacement headers. It is built as `WDC_SAMBA4` and linked into the Heimdal `service_kdc` module. It relies on `struct samba_kdc_entry` being attached to HDB entry contexts by the database glue.

## Risks and Edge Cases

PAC validation is security-critical. RODC-issued PAC handling must distinguish local RODC keys, writable DC behavior, and untrusted server-encrypted evidence tickets. The S4U2Proxy path verifies signatures based on checksum type and may return `HDB_ERR_NOT_FOUND_HERE` to force proxying. `samba_wdc_reget_pac()` has an early `return EINVAL` when a delegated proxy is present but `krbtgt` is not a krbtgt, bypassing the common `out` cleanup for `mem_ctx`. The TGT-vs-kpasswd lifetime heuristic rejects tickets with at most `CHANGEPW_LIFETIME` remaining. SASL/client policy failures depend on NTSTATUS-to-Kerberos error mapping.

## Test Signals

Coverage should include AS-REQ PAC generation, PKINIT with freshness and reply key, S4U2Self, S4U2Proxy with RODC and writable DC signatures, device claims, constrained delegation, trust TGTs, near-expiry kpasswd ticket confusion, smart-card-required accounts, and canonicalize requests that should receive `KRB5_PADATA_SUPPORTED_ETYPES`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/wdc-samba4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/wscript_build -->
# sources/user-network-fs/samba/source4/kdc/wscript_build

## Purpose

`source4/kdc/wscript_build` declares the Samba KDC build graph. It selects Heimdal or MIT KDC service modules, builds KDC/PAC/database subsystems, and wires the KDC unit tests for database glue and SDB-to-HDB conversion.

## Important APIs, Types, and Functions

The script uses waf helpers such as `bld.SAMBA_MODULE()`, `bld.SAMBA_BINARY()`, `bld.SAMBA_LIBRARY()`, `bld.SAMBA_SUBSYSTEM()`, and `bld.RECURSE()`. Key targets are `service_kdc`, `HDB_SAMBA4`, `HDB_SAMBA4_PLUGIN`, `KDC-SERVER`, `KPASSWD-SERVICE`, `KDC-GLUE`, `WDC_SAMBA4`, `sdb`, `sdb_hdb`, `sdb_kdb`, `PAC_GLUE`, `db-glue`, `ad_claims`, `authn_policy_util`, `KPASSWD_GLUE`, `MIT_KDC_IRPC`, `MIT_SAMBA`, `samba4ktutil`, `test_db_glue`, and `test_sdb_to_hdb`.

## Control Flow

At configure/build time it chooses include paths from bundled Heimdal headers or system KDC headers. If `SAMBA4_USES_HEIMDAL` is set, it builds the Heimdal KDC service and cmocka tests. If `SAMBA_USES_MITKDC` is set, it builds the MIT service module and MIT IRPC support. Optional subsystems are gated on `HAVE_KDB_H`, `USING_SYSTEM_KRB5`, `USING_SYSTEM_HDB`, and Heimdal/MIT feature flags. The script recurses into `mit-kdb` after declaring local targets.

## State and Persistence Behavior

The file does not run runtime state. It persists build metadata into waf's configured target graph and generated autoproto headers such as `sdb_hdb.h` and `sdb_kdb.h`.

## Dependencies and Integration Points

This file is the integration point between KDC source files and the rest of Samba: host configuration, credentials, GENSEC, PAC glue, auth policy, LDB/SAMDB, RPC NDR, messaging, kpasswd service, Heimdal HDB, and MIT KDB libraries. Test binaries are marked `for_selftest=True`.

## Risks and Edge Cases

The build matrix is sensitive to Heimdal vs MIT and bundled vs system Kerberos combinations. A target may compile only in one matrix, so changes to shared files such as `db-glue.c`, `sdb_to_hdb.c`, or `sdb_to_kdb.c` need cross-matrix validation. Include path selection deliberately avoids depending on the KDC binary while still using KDC headers, so system header drift can expose portability issues.

## Test Signals

Signals include successful builds under Heimdal and MIT configurations, execution of `test_db_glue` and `test_sdb_to_hdb` in selftest, generated autoproto freshness for conversion APIs, and successful linkage of `service_kdc`, `MIT_SAMBA`, and `samba4ktutil`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_backend.c -->
# sources/user-network-fs/samba/source4/ldap_server/ldap_backend.c

## Purpose

`ldap_backend.c` maps decoded LDAP protocol operations onto Samba's LDB/SAM database backend. It initializes per-connection SAMDB handles, translates LDB errors into LDAP/Windows-flavored diagnostics, queues encoded LDAP replies, implements search/add/modify/delete/rename/compare/abandon handling, and dispatches decoded LDAP calls.

## Important APIs, Types, and Functions

Public entry points are `ldapsrv_backend_Init()`, `ldapsrv_init_reply()`, `ldapsrv_queue_reply()`, and `ldapsrv_do_call()`. Major internal handlers are `ldapsrv_SearchRequest()`, `ldapsrv_ModifyRequest()`, `ldapsrv_AddRequest()`, `ldapsrv_DelRequest()`, `ldapsrv_ModifyDNRequest()`, `ldapsrv_CompareRequest()`, `ldapsrv_AbandonRequest()`, and `ldapsrv_expired()`. Backend helpers include `map_ldb_error()`, mutation wrappers with controls, `ldap_server_search_callback()`, and forced reply queuing for size-limit error packets.

## Control Flow

`ldapsrv_backend_Init()` opens `sam.ldb` for the connection session, marks encrypted-connection state when TLS, SASL seal, or LDAPI is active, and stores supported SASL mechanisms in LDB opaque state. `ldapsrv_do_call()` first checks ticket expiry and critical controls, optionally logs anonymous authorization, dispatches by LDAP tag, and schedules notification retries after successful mutating/extended calls. Search builds an LDB request, maps scope and attributes, applies global-catalog or no-global-catalog controls, handles extended DN and notification controls, sets timeouts, waits synchronously, queues entries/referrals through the callback, optionally updates gMSA keys from controls, and emits a final `SearchResultDone`. Mutations translate LDAP request structs into LDB messages, run transaction-wrapped LDB requests, and queue LDAP result replies.

## State and Persistence Behavior

Connection state is stored in `conn->ldb`, LDB opaque values, `conn->session_info`, `pending_calls`, and notification generation fields. Add, modify, delete, and rename operations persist to SAMDB through LDB transactions unless the connection is on a global catalog port. Search can trigger persistent gMSA key updates after successful reads that return `DSDB_CONTROL_GMSA_UPDATE_OID`. Reply blobs are encoded and retained on the call until the server write path drains them.

## Dependencies and Integration Points

The file integrates LDAP protocol structures, GENSEC/SASL discovery, Samba auth session info, SAMDB/LDB modules and controls, gMSA utilities, stream service state, talloc, tsocket addresses, and authorization logging. It depends on `ldap_server.h` for connection/call structures and on bind/extended handlers declared via generated prototypes.

## Risks and Edge Cases

Search response memory is capped at `LDAP_SERVER_MAX_REPLY_SIZE` and write chunks at 25 MiB, but large searches still allocate queued encoded replies until the cap is hit. Mutation operations are synchronous and transaction-wrapped, so long LDB module work blocks the call queue. Notification searches stay in `pending_calls` and are retried by generation. `CompareRequest` builds a filter with raw `%*s` value formatting, so escaping semantics depend on LDB filter formatting behavior. Expired Kerberos sessions send an unsolicited notice and return `NT_STATUS_NETWORK_SESSION_EXPIRED`.

## Test Signals

Tests should cover LDB-to-LDAP error strings, critical unknown controls, global catalog write rejection, search scope validation, extended DN output, size-limit behavior, notification retry behavior, Add/Modify/Delete/ModifyDN transaction rollback, Compare true/false, Abandon removing pending notifications, anonymous authorization logging, encrypted opaque state for TLS/SASL/LDAPI, and ticket-expiry unsolicited response.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_backend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_bind.c -->
# sources/user-network-fs/samba/source4/ldap_server/ldap_bind.c

## Purpose

`ldap_bind.c` implements LDAP Bind and Unbind handling for Samba's LDAP server. It supports simple binds, SASL binds through GENSEC, optional SASL sign/seal stream wrapping, strong-auth policy, channel bindings over TLS, backend reinitialization under the authenticated session, and local disconnect behavior for Unbind.

## Important APIs, Types, and Functions

The exported entry points are `ldapsrv_BindRequest()` and `ldapsrv_UnbindRequest()`. Internal flows include `ldapsrv_BindSimple()`, `ldapsrv_BindSimple_done()`, `ldapsrv_BindSASL()`, `ldapsrv_BindSASL_done()`, `ldapsrv_setup_gensec()`, `ldapsrv_sasl_postprocess_send/recv()`, `ldapsrv_bind_wait_setup()`, and `ldapsrv_unbind_wait_setup()`. `ldapsrv_bind_error_msg()` builds Windows-compatible LDAP diagnostic strings.

## Control Flow

Simple bind rejects non-empty DN/password attempts without TLS when strong auth requires transport protection, then starts `authenticate_ldap_simple_bind_send()`. Completion steals the returned session info into the connection, marks authorization logged, drops the old LDB handle, reinitializes the backend, and queues `BindResponse`. SASL bind lazily creates a GENSEC server for the requested mechanism, feeds the client's secblob to `gensec_update_send()`, returns `LDAP_SASL_BIND_IN_PROGRESS` on continuation, and on success enforces sign/seal or TLS requirements. If sign/seal is negotiated, it creates a GENSEC tstream and schedules socket replacement as postprocessing after the successful response is written. Unbind clears pending calls and installs a wait hook that returns `NT_STATUS_LOCAL_DISCONNECT`.

## State and Persistence Behavior

Bind mutates connection-level authentication state: `conn->gensec`, `conn->session_info`, `conn->ldb`, `conn->authz_logged`, `conn->limits.expire_time`, and optionally `conn->sockets.sasl`/`active`. It does not persist directory data directly, but it changes the credentials used by subsequent backend operations. GENSEC contexts are destroyed after authentication unless transferred under the SASL tstream for sign/seal.

## Dependencies and Integration Points

It depends on Samba auth, service state, LDB errors, SAMDB backend reinitialization, GENSEC and `gensec_tstream`, TLS channel binding helpers, loadparm strong-auth policy, tevent NTSTATUS helpers, and `ldap_server.h` call wait/postprocess hooks. It works with `ldap_server.c`, which honors those hooks after call dispatch and after reply write.

## Risks and Edge Cases

Bind is forbidden while `pending_calls` exists, returning `LDAP_BUSY`. Strong-auth policy has multiple compatibility modes, including optional channel bindings for legacy settings. SASL sign/seal is refused over TLS and refused if a SASL encrypted stream is already active. RFC 4513 cancellation of in-progress SASL on new mechanisms/simple bind is noted as TODO. Error strings intentionally mimic Windows DSID/data formats, so changes can affect client compatibility.

## Test Signals

Coverage should include simple bind success/failure, simple bind without TLS under strong-auth yes, SASL multi-leg negotiation, bad channel bindings, SASL sign/seal stream activation, SASL over TLS refusal with sign/seal, backend reinitialization failures, pending request `LDAP_BUSY`, Unbind disconnect, and ticket expire time propagation from GENSEC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_extended.c -->
# sources/user-network-fs/samba/source4/ldap_server/ldap_extended.c

## Purpose

`ldap_extended.c` implements LDAP ExtendedRequest operations supported by Samba's LDAP server, currently StartTLS and WhoAmI. It queues the appropriate extended response and, for StartTLS, arranges the TLS handshake as postprocessing after the success response is sent.

## Important APIs, Types, and Functions

The exported entry point is `ldapsrv_ExtendedRequest()`. Operation handlers are represented by `struct ldapsrv_extended_operation` entries in `extended_ops[]`. Internal handlers include `ldapsrv_StartTLS()`, `ldapsrv_whoami()`, and the StartTLS postprocess send/recv/done functions.

## Control Flow

`ldapsrv_ExtendedRequest()` initializes an `ExtendedResponse`, steals the requested OID into the reply, finds a matching handler, and lets that handler either queue its own successful reply or return an LDAP-coded error. StartTLS rejects sessions that already have TLS, already have SASL wrapping, or have pending calls. On success it queues an LDAP success response and registers a postprocess hook that runs `tstream_tls_accept_send()` on the raw stream, then switches `conn->sockets.active` to `conn->sockets.tls`. WhoAmI returns `u:DOMAIN\account` for non-anonymous sessions and success with no value for anonymous sessions.

## State and Persistence Behavior

StartTLS mutates connection stream state by creating `conn->sockets.tls` and setting it active after the response write completes. WhoAmI only reads `conn->session_info` and does not persist state. Unsupported or failed extended operations only queue a response.

## Dependencies and Integration Points

The file depends on LDAP server call postprocess hooks, tstream TLS parameters, service stream state, generated auth NDR types, and security token helpers. It is compiled into the `service_ldap` module with `ldap_server.c`, `ldap_backend.c`, and `ldap_bind.c`.

## Risks and Edge Cases

StartTLS must not switch streams before the success response is fully written; the postprocess hook enforces that ordering. RFC 4513 behavior for StartTLS during an in-progress SASL bind is noted as TODO. StartTLS over an existing SASL wrapped session and StartTLS with pending operations correctly return LDAP errors. WhoAmI assumes authenticated session info contains user info when the token is non-anonymous.

## Test Signals

Tests should cover StartTLS success, StartTLS when TLS already exists, StartTLS after SASL wrapping, StartTLS with pending notification/search calls, failed TLS accept, anonymous WhoAmI, authenticated WhoAmI formatting, and unsupported OID diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_extended.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_server.c -->
# sources/user-network-fs/samba/source4/ldap_server/ldap_server.c

## Purpose

`ldap_server.c` is the transport, task, and event-loop implementation for Samba's LDAP service. It accepts LDAP/LDAPS/GC/LDAPI sockets, manages per-connection streams and limits, reads and decodes LDAP PDUs, serializes call execution through a queue, writes encoded replies in bounded chunks, handles notifications, and registers the LDAP server service.

## Important APIs, Types, and Functions

The exported symbols are `ldapsrv_recv()`, `ldapsrv_notification_retry_setup()`, and `server_service_ldap_init()`. Important internal functions include `ldapsrv_accept()`, `ldapsrv_accept_tls_done()`, `ldapsrv_call_read_next()`, `ldapsrv_call_read_done()`, `ldapsrv_process_call_send/recv/trigger()`, `ldapsrv_call_process_done()`, `ldapsrv_call_wait_done()`, `ldapsrv_call_writev_start/done()`, `ldapsrv_call_postprocess_done()`, `ldapsrv_terminate_connection()`, `add_socket()`, `ldap_reload_certs()`, `ldapsrv_task_init()`, `ldapsrv_post_fork()`, `ldapsrv_before_loop()`, `ldapsrv_check_packet_size()`, and `ldapsrv_packet_check()`.

## Control Flow

Task init verifies the server role is AD DC, creates service state and TLS params, binds LDAP/LDAPS and GC sockets per interface or wildcard, creates LDAPI sockets, and registers IRPC and messaging handlers. Accept converts the socket to a `tstream`, initializes anonymous or system session state, detects GC ports, creates server credentials, initializes the backend, loads query limits, and starts TLS immediately for LDAPS ports or begins reading. The read path uses `tstream_read_pdu_blob_send()` with `ldap_full_packet()` checks, enforces request size limits, decodes ASN.1/LDAP, queues the call globally, runs `ldapsrv_do_call()`, waits for async bind/unbind hooks if present, writes replies through `tstream_writev_queue_send()`, runs postprocess hooks for TLS/SASL stream switching, and then reads the next PDU.

## State and Persistence Behavior

Service state tracks TLS params, call queue, active connections, notification generation/retry timer, loadparm, messaging, event context, and optional per-child SAMDB context. Connection state tracks raw/TLS/SASL streams, active call, pending notification calls, LDB/session state, query limits, idle/initial/expiry timers, and termination reason. Runtime changes include TLS certificate reloads via messaging, notification retry generation changes, and socket stream replacement after StartTLS or SASL sign/seal.

## Dependencies and Integration Points

The file integrates Samba service/task/process model APIs, stream server setup, tevent/tstream, TLS, LDAP ASN.1 encode/decode, auth session helpers, IRPC name registration, server ID database, SAMDB, network interface binding, loadparm limits, and messaging for `MSG_RELOAD_TLS_CERTIFICATES`. It calls backend, bind, and extended handlers through generated prototypes and shared `ldap_server.h` structures.

## Risks and Edge Cases

`ldapsrv_recv()` and `ldapsrv_send()` panic because direct stream callbacks should not be used after the socket is converted to tstream. Connection termination performs staged disconnects from active TLS/SASL then raw stream. Request size limits differ for anonymous and authenticated sessions. Notification calls remain allocated while busy and are retried by generation, so cancellation and connection termination must clear them. Writev is capped by both `LDAP_SERVER_MAX_CHUNK_SIZE` and `IOV_MAX`, requiring repeated writes for large reply lists. The LDAPI bind error logs use `ldapi_path` after it is freed in the failure branch, which is a diagnostic lifetime risk.

## Test Signals

Coverage should include LDAP and LDAPS accept, StartTLS stream switch after response write, SASL postprocess stream switch, anonymous/authenticated request size limits, initial and idle timeouts, expired Kerberos-session unsolicited disconnect, notification retry scheduling, TLS certificate reload propagation to prefork workers, GC port binding, LDAPI privileged and nonprivileged sockets, and large search reply chunking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_server.h -->
# sources/user-network-fs/samba/source4/ldap_server/ldap_server.h

## Purpose

`ldap_server.h` defines the shared state structures and constants for Samba's LDAP server implementation. It is the common contract between transport handling, backend request dispatch, bind logic, and extended operations.

## Important APIs, Types, and Functions

Key types are `enum ldap_server_referral_scheme`, `struct ldapsrv_connection`, `struct ldapsrv_call`, nested `struct ldapsrv_reply`, and `struct ldapsrv_service`. The header defines `LDAP_SERVER_MAX_REPLY_SIZE` at 256 MiB and `LDAP_SERVER_MAX_CHUNK_SIZE` at 25 MiB. It includes the generated `ldap_server/proto.h` prototypes.

## Control Flow

There is no runtime control flow in the header. Its structure fields enable the control flow in other files: connection stream selection, backend handles, wait hooks for async bind/unbind, postprocess hooks for StartTLS/SASL stream changes, reply lists, notification state, and service-level retry/call queue state.

## State and Persistence Behavior

`ldapsrv_connection` owns per-client state: loadparm, stream connection, GENSEC, session info, service pointer, credentials, LDB handle, raw/TLS/SASL streams, authentication/authorization flags, referral scheme, limits, active call, deferred expiry disconnect, and pending calls. `ldapsrv_call` owns one decoded LDAP request, encoded replies, write iovecs, optional wait/postprocess callbacks, and notification state. `ldapsrv_service` owns process-wide LDAP service state.

## Dependencies and Integration Points

The header depends on LDAP client protocol types, socket/packet/network headers, and loadparm definitions. It is included by `ldap_server.c`, `ldap_backend.c`, `ldap_bind.c`, and `ldap_extended.c`, making it the central ABI for this service module.

## Risks and Edge Cases

The structs are tightly coupled to asynchronous lifetime rules: callbacks store private pointers under `ldapsrv_call`, while streams and backend handles live under `ldapsrv_connection`. Incorrect ownership transfer can leave active stream pointers stale. The reply and chunk limits are defensive constants; changing them affects memory pressure and client-visible size-limit behavior.

## Test Signals

Compile coverage across all LDAP server files catches structural drift. Runtime tests should exercise every hook field: simple bind wait, unbind wait, StartTLS postprocess, SASL postprocess, notification busy calls, multi-reply search writes, and connection termination with raw/TLS/SASL streams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/ldap_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/wscript_build -->
# sources/user-network-fs/samba/source4/ldap_server/wscript_build

## Purpose

`source4/ldap_server/wscript_build` declares the LDAP server service module target for Samba's AD DC build.

## Important APIs, Types, and Functions

The script contains a single `bld.SAMBA_MODULE()` call for `service_ldap`. It compiles `ldap_server.c`, `ldap_backend.c`, `ldap_bind.c`, and `ldap_extended.c`, generates `proto.h`, registers the module under the `service` subsystem, and sets `server_service_ldap_init` as the init function.

## Control Flow

At build time waf evaluates `bld.AD_DC_BUILD_IS_ENABLED()`. When enabled, the LDAP service module is built as a non-internal service module with dependencies on credentials, CLI LDAP, SAMDB, process model, GENSEC, host config, server GENSEC, and common auth.

## State and Persistence Behavior

The file has no runtime persistence. It persists build graph metadata and generated prototypes used by the LDAP server translation units.

## Dependencies and Integration Points

This is the build integration point tying LDAP server code to Samba service infrastructure and AD DC-only builds. Its dependency list must cover authentication, database, LDAP protocol, and process-model symbols used by all four source files.

## Risks and Edge Cases

Because the module is gated by AD DC build enablement, non-AD configurations will not compile this code and may miss regressions. Missing dependencies usually surface as link failures in `service_ldap` or missing prototypes in generated `proto.h`.

## Test Signals

Signals include successful AD DC builds, generated `ldap_server/proto.h`, service module registration through `server_service_ldap_init`, and selftest coverage that starts Samba with LDAP/LDAPS listeners.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ldap_server/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/events/events.h -->
# sources/user-network-fs/samba/source4/lib/events/events.h

## Purpose

`events.h` is the small public header for Samba4 event context helpers. It declares the Samba4-specific tevent initialization API and default-event setter.

## Important APIs, Types, and Functions

The header declares `struct tevent_context *s4_event_context_init(TALLOC_CTX *mem_ctx)` and `void s4_event_context_set_default(struct tevent_context *ev)`. It includes `<tevent.h>` and uses a normal include guard.

## Control Flow

There is no runtime flow in this header. It allows callers to initialize a tevent context with Samba-specific behavior and, where implemented elsewhere, set a default event context.

## State and Persistence Behavior

The header itself holds no state. The declared APIs affect tevent context allocation and default event context state in implementation files.

## Dependencies and Integration Points

It is included by `tevent_s4.c` and other Samba4 code that needs event context initialization. The API bridges Samba utilities and the public tevent library.

## Risks and Edge Cases

The header declares `s4_event_context_set_default()` but this listed implementation file only defines `s4_event_context_init()`, so callers rely on another object or legacy symbol for the setter. Prototype drift would be caught at compile/link time.

## Test Signals

Compile coverage for event users and link coverage for both declared functions are the key signals. Runtime checks should confirm initialized contexts have Samba debug handling and support nested loops where required.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/events/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/events/tevent_s4.c -->
# sources/user-network-fs/samba/source4/lib/events/tevent_s4.c

## Purpose

`tevent_s4.c` provides Samba4's event-context initializer. It wraps common Samba tevent initialization with Samba4-specific debug naming and nested-loop allowance.

## Important APIs, Types, and Functions

The file implements `s4_event_context_init(TALLOC_CTX *mem_ctx)`. It calls `samba_tevent_context_init()`, `samba_tevent_set_debug(ev, "s4_tevent")`, and `tevent_loop_allow_nesting(ev)`.

## Control Flow

Callers request a tevent context with a talloc parent. If allocation succeeds, the helper sets the debug handler/name and enables nested event loops before returning the context. If allocation fails, it returns `NULL`.

## State and Persistence Behavior

The allocated tevent context lives under the supplied talloc parent. The function mutates that context's debug and nesting configuration but does not persist global state.

## Dependencies and Integration Points

It includes `includes.h`, enables deprecated tevent declarations with `TEVENT_DEPRECATED`, and includes `lib/events/events.h`. It is built into the private `events` library with public dependency on tevent and private dependency on `samba-util`.

## Risks and Edge Cases

Nested event loops can hide reentrancy bugs in callers, but this is a deliberate Samba4 compatibility behavior. Callers must check for `NULL`. Debug naming is useful for tracing event failures and should stay stable enough for diagnostics.

## Test Signals

Signals include successful creation under normal memory conditions, `NULL` under allocation failure injection, debug output labeled `s4_tevent`, and components that require nested loops operating without tevent nesting assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/events/tevent_s4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/events/wscript_build -->
# sources/user-network-fs/samba/source4/lib/events/wscript_build

## Purpose

`source4/lib/events/wscript_build` declares the private Samba4 `events` library target.

## Important APIs, Types, and Functions

The script uses `bld.SAMBA_LIBRARY()` to build `events` from `tevent_s4.c`, with `samba-util` as a private dependency and `tevent` as a public dependency. The library is marked `private_library=True`.

## Control Flow

At build time waf registers this library so internal Samba4 targets can link against the `s4_event_context_init()` implementation.

## State and Persistence Behavior

The file has no runtime state. It persists target metadata in the build graph.

## Dependencies and Integration Points

It ties the local event wrapper to the external/public tevent API and Samba utility support. Consumers include services and libraries needing Samba4 event-loop initialization.

## Risks and Edge Cases

Because the library is private, external consumers should not depend on it directly. Dependency visibility matters: code including `events.h` needs tevent headers available through the public dependency.

## Test Signals

Signals are successful build and link of internal event users, plus runtime initialization tests through services that create Samba4 event contexts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/events/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/irpc.h -->
# sources/user-network-fs/samba/source4/lib/messaging/irpc.h

## Purpose

`irpc.h` defines the public header contract for Samba's internal RPC-over-messaging layer. It lets services register NDR-backed server functions, obtain DCERPC binding handles to server IDs or named tasks, associate security tokens with handles, and manage messaging names.

## Important APIs, Types, and Functions

The central request type is `struct irpc_message`, which carries sender server ID, private data, IRPC header, NDR pull context, reply flags, messaging context, IRPC registration list, and decoded data pointer. `irpc_function_t` is the server callback signature. `IRPC_REGISTER()` wraps `irpc_register()` with generated NDR table and call constants. Declared APIs include `irpc_register()`, `irpc_binding_handle()`, `irpc_binding_handle_by_name()`, `irpc_binding_handle_add_security_token()`, `irpc_add_name()`, `irpc_servers_byname()`, `irpc_all_servers()`, `irpc_remove_name()`, and `irpc_send_reply()`.

## Control Flow

There is no implementation flow in the header. At runtime, services register callbacks for NDR interface calls, clients obtain binding handles by server ID or registered name, calls travel over the messaging subsystem, and server callbacks optionally defer or suppress replies before `irpc_send_reply()`.

## State and Persistence Behavior

IRPC state is held by the messaging context and registration/name records, not by this header. `IRPC_CALL_TIMEOUT` defaults calls to 10 seconds, while `IRPC_CALL_TIMEOUT_INF` represents no timeout. `struct irpc_message` fields such as `defer_reply` and `no_reply` influence reply lifecycle for one incoming call.

## Dependencies and Integration Points

The header depends on Samba messaging, WERROR utilities, and generated IRPC NDR definitions. It is used by services such as LDAP, which registers the `ldap_server` name, and by other Samba internal task-to-task RPC paths.

## Risks and Edge Cases

Callback signatures use `void *r` for generated request/response unions, so type correctness depends on matching NDR table/call IDs. Deferred replies require careful lifetime management of `struct irpc_message`. Name registration and lookup depend on live messaging/server-id database state, so stale process records can affect binding by name.

## Test Signals

Coverage should include callback registration through `IRPC_REGISTER`, name add/remove and lookup, binding by server ID and by name, security token attachment, normal replies, deferred replies, no-reply calls, timeout behavior, and behavior when named servers disappear.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/messaging/irpc.h -->
