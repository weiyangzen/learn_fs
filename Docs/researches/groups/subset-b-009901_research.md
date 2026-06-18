# subset-b-009901 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/sam.c -->
# sources/user-network-fs/samba/source4/auth/sam.c

Purpose: core Samba AD authentication/SAM helper code. It defines KDC/account lookup attribute sets, validates account policy, builds `auth_user_info_dc` records from SAMDB rows, expands domain groups, and maintains logon accounting.

Important APIs and functions: `authsam_account_ok()` enforces disabled, locked, expired, must-change, password-expired, workstation, logon-hours, and trust-account restrictions. `authsam_make_user_info_dc()` converts an LDB user record into account metadata, session keys, and SID attributes. `authsam_update_user_info_dc()` expands local-domain nested group SIDs. `sam_get_results_principal()`, `authsam_get_user_info_dc_principal()`, and `authsam_search_account()` locate accounts. `authsam_update_bad_pwd_count()`, `authsam_reread_user_logon_data()`, and `authsam_logon_success_accounting()` implement bad-password and successful-logon updates.

Control flow: authentication callers search by principal, DN, or account name using the exported attribute arrays, validate the resulting account with `authsam_account_ok()`, then build DC-style user info. Group expansion filters out builtin groups for the PAC path, later adding builtin local groups at session-token generation. Failure accounting reads domain/PSO policy, starts an LDB transaction, rereads the user by extended DN/GUID, delegates count/lockout calculation to DSDB, writes modifications with `DSDB_CONTROL_FORCE_RODC_LOCAL_CHANGE`, and records a temporary bad-password indicator. Success accounting first checks that indicator to avoid unnecessary transactions, optionally rereads the account, resets lockout/badPwdCount, updates `lastLogon`, `logonCount`, and `lastLogonTimestamp`, and emits RODC `SendToSAM` reset messages when appropriate.

State and persistence: persistent state lives in SAMDB user/domain attributes (`badPwdCount`, `badPasswordTime`, `lockoutTime`, `lastLogon`, `lastLogonTimestamp`, `logonCount`, account-control computed attributes). A clustered temporary dbwrap database named `bad_password` stores objectSID keys to remember failed-password attempts between failure and success accounting. Transactions are intentionally committed even for expected locked-out rereads to avoid noisy audit failures.

Dependencies and integration: depends on LDB/DSDB/SAMDB helpers, SID/security utilities, NDR LDAP encoders, loadparm, dbwrap, and clustering. It feeds GENSEC/Kerberos paths that need PAC-less user info, NTLM auth, DSDB tokenGroups handling, PAC construction, and session generation.

Risks: policy correctness is security-critical. Time calculations use server UTC for logon hours and randomized lastLogonTimestamp intervals. RODC local changes, temporary bad-password indicators, and transaction retry paths can diverge if objectSID extraction, dbwrap, or LDB controls fail. Shallow-copy code deliberately copies the SID array because later token mutation would be unsafe through talloc references.

Test signals: `auth/tests/sam.c` directly includes this file and wraps LDB/SAMDB/dbwrap calls to verify reread, lockout, transaction commit/cancel, bad-password indicator, and memory ownership behavior. Broader authentication and Kerberos selftests exercise the exported account/session paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/sam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/samba_server_gensec.c -->
# sources/user-network-fs/samba/source4/auth/samba_server_gensec.c

Purpose: central server-side GENSEC bootstrap used by Samba services that authenticate against local Samba configuration and SAM resources.

Important APIs: `samba_server_gensec_start()` creates default `gensec_settings` from loadparm, creates an `auth4_context`, starts a server GENSEC context, attaches server credentials, and optionally sets the target service. `samba_server_gensec_krb5_start()` builds a constrained backend list containing Kerberos5 and SPNEGO before calling the common setup helper.

Control flow: callers pass event/messaging/loadparm contexts and server credentials. The private helper allocates a temporary context, calls `auth_context_create()`, then `gensec_server_start()`, applies credentials and service name, and steals the resulting `gensec_security` into the caller context. Public wrappers reparent the settings object below the returned context so backend settings survive for the GENSEC lifetime.

State and persistence: no durable state. Lifetime state is talloc-owned GENSEC settings, backend arrays, auth context, credentials, and target-service metadata.

Dependencies and integration: integrates `auth4`, `gensec`, server credentials, loadparm GENSEC settings, tevent, and imessaging. Services use it to ensure uniform server authentication setup rather than each service selecting backends and auth callbacks by hand.

Risks: backend restriction in the Kerberos variant depends on successful `gensec_init()` and OID lookup. Ownership is subtle: freeing settings too early would break the returned context, hence explicit `talloc_reparent()`. Missing target-service metadata can affect service-principal selection.

Test signals: no direct unit test in this subset; build coverage comes from `samba_server_gensec` subsystem users and Kerberos/GENSEC selftests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/samba_server_gensec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/session.c -->
# sources/user-network-fs/samba/source4/auth/session.c

Purpose: converts DC-style authentication data into runtime session and security-token data, handles session transport forwarding, and lazily converts Windows claims formats.

Important APIs: `anonymous_session()`, `auth_generate_security_token()`, `auth_generate_session_info()`, `auth_session_info_from_transport()`, `auth_session_info_transport_from_session()`, `authsam_get_session_info_principal()`, `auth_session_info_debug()`, `encode_claims_set()`, `claims_data_from_encoded_claims_set()`, `claims_data_from_claims_set()`, `claims_data_encoded_claims_set()`, and `claims_data_security_claims()`.

Control flow: `auth_generate_session_info()` references account metadata from `auth_user_info_dc`, copies the session key, calls `auth_generate_security_token()`, assigns a random unique session token, and preserves ticket type. Token generation first expands user and optional device SID lists with default/authentication/NTLM/organization SIDs according to flags, then optionally expands builtin local groups from SAMDB. Transport conversion steals forwarded session info and imports/export delegated GSS credentials when the platform provides `gss_import_cred()`/`gss_export_cred()`. Claims helpers translate between encoded PAC claim blobs, `CLAIMS_SET`, and token-ready security attributes on demand.

State and persistence: session state is in-memory and talloc-owned. `unique_session_token` is random per generated session. Claims data caches decoded/encoded/security forms with flags marking which views are valid. No database writes occur here.

Dependencies and integration: uses security token creation, DSDB nested-group expansion, winbind client headers, Samba credentials, Kerberos/GSSAPI, generated claims NDR, and claims conversion helpers. It bridges auth subsystem results to SMB/RPC access checks and delegated credential forwarding.

Risks: SID expansion must preserve primary SID ordering and reject unexpected `This Organization` input. Talloc references avoid deep copies for account info but require source lifetime discipline. Claims decoding handles untrusted PAC data and maps NDR errors to NTSTATUS. GSS credential import/export availability is compile-time dependent.

Test signals: indirect coverage from authentication, PAC, claims, and named-pipe forwarding tests. No direct unit test in this file, so regressions often appear as token membership or access-check failures elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/session.h -->
# sources/user-network-fs/samba/source4/auth/session.h

Purpose: public interface for Samba authentication session construction, token generation, anonymous/system/admin sessions, transport serialization, and claims conversion.

Important APIs and types: declares `enum claims_data_present`, `struct claims_data`, `struct auth_claims`, and all major session entry points: `system_session()`, `auth_anonymous_user_info_dc()`, `auth_generate_security_token()`, `auth_generate_session_info()`, `auth_anonymous_session_info()`, transport conversion functions, `authsam_get_session_info_principal()`, `anonymous_session()`, `admin_session()`, and claims encode/decode helpers.

Control flow and integration: this header is included by auth, service, RPC, and utility code that needs a complete `auth_session_info` or just a `security_token`. It keeps SAMDB and loadparm parameters optional for callers that do not need local privileges or local group expansion.

State and persistence: defines in-memory structures only. `claims_data.flags` documents cached representations of the same claim source: encoded PAC bytes, decoded claims set, and converted security claims.

Dependencies: exposes `DATA_BLOB`, generated security/netlogon/auth NDR types, WERROR/NT time definitions, and forward declarations for loadparm/tevent/LDB types.

Risks: this header is a cross-module contract; changing flags, ownership expectations, or optional parameter semantics affects many Samba services. Claims comments clarify that converted security claims are a product, not authoritative source data.

Test signals: build-time consumers and tests for session construction, PAC/claims, and system/anonymous/admin sessions validate this API surface indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/system_session.c -->
# sources/user-network-fs/samba/source4/auth/system_session.c

Purpose: constructs synthetic privileged, domain-admin, and anonymous session identities without reading SAMDB user objects.

Important APIs: `system_session()` returns a static unfreeable SYSTEM session. `auth_system_session_info()` builds SYSTEM session info and attaches pending machine-account credentials. `auth_system_user_info_dc()` creates SYSTEM DC user info. `admin_session()` and its helpers create a synthetic Administrator token for a supplied domain SID. `auth_anonymous_session_info()` and `auth_anonymous_user_info_dc()` create anonymous session/user info.

Control flow: synthetic `auth_user_info_dc` structures are populated with well-known or domain-derived SIDs, zeroed 16-byte session keys, display/logon path fields, account flags, and user flags. They are then converted through `auth_generate_session_info()` using privilege/default/authentication flags appropriate to the identity. SYSTEM and anonymous sessions also allocate `cli_credentials` and configure machine or anonymous credential state.

State and persistence: no durable state. `system_session()` caches one static process-lifetime `auth_session_info` and sets a destructor returning `-1` to prevent accidental free. All other sessions are caller-owned talloc allocations.

Dependencies and integration: depends on security SID constants, credential helpers, loadparm names/workgroup, and `auth_session` token creation. Used by internal services, SAMDB access, CLDAP startup, and tests that need privileged or anonymous auth context.

Risks: synthetic tokens carry high privilege and bypass SAMDB lookup, so SID composition must match Samba/Windows expectations. The static SYSTEM session is shared and should not be mutated by callers. Zero session keys are intentional but must not be confused with authenticated user key material.

Test signals: indirect service startup and auth tests; CLDAP in this subset uses `system_session()` to open SAMDB.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/system_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/tests/heimdal_unwrap_des.c -->
# sources/user-network-fs/samba/source4/auth/tests/heimdal_unwrap_des.c

Purpose: cmocka regression tests for Samba's bundled Heimdal GSSAPI DES3 unwrap path, focused on malformed token length handling and memory-safety boundaries.

Important APIs and helpers: wrappers for `krb5_auth_con_getlocalsubkey`, `krb5_crypto_init`, `krb5_decrypt`, `krb5_decrypt_ivec`, `krb5_verify_checksum`, `krb5_crypto_destroy`, `der_get_length`, `ct_memcmp`, and `malloc` validate parameters and bounds. `get_input_buffer()` pads input data and records valid/invalid memory ranges. Tests call `_gsskrb5_unwrap()` with crafted RFC 1964 tokens.

Control flow: setup initializes a GSS acceptor context and mock key/crypto objects. Each test builds a token, sometimes marks the context `GSS_C_DCE_STYLE`, registers expectations for crypto/checksum calls when valid, invokes unwrap, and asserts major status, confidentiality state, QOP, and output length/content.

State and persistence: only process-local test globals track valid buffer ranges and dummy crypto/key state. No persistence.

Dependencies and integration: compiles only for the Heimdal/internal GSSAPI path per `wscript_build`. It includes Heimdal internal headers and tests the implementation behind GENSEC Kerberos unwrap behavior.

Risks covered: missing payloads, truncated headers, missing eight-byte DES blocks, padding truncation, sealed versus unsealed tokens, DCE style, and integer underflow leading to oversized malloc or out-of-range `ct_memcmp`. The wrappers are designed to fail on reads beyond the declared input length even when padded bytes exist.

Test signals: this file is itself a targeted selftest binary, `test_heimdal_gensec_unwrap_des`, with subunit cmocka output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/tests/heimdal_unwrap_des.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/tests/kerberos.c -->
# sources/user-network-fs/samba/source4/auth/tests/kerberos.c

Purpose: cmocka tests for Kerberos keytab cleanup, specifically `smb_krb5_remove_obsolete_keytab_entries()`.

Important APIs/functions: `internal_obsolete_keytab_test()` creates an in-memory keytab, adds multiple principals and key version numbers, validates initial ordering, calls `smb_krb5_remove_obsolete_keytab_entries()`, and verifies only the expected previous kvno remains. Public tests cover one principal/two kvnos and many principals/four kvnos.

Control flow: the helper initializes a krb5 context, resolves a `MEMORY:` keytab, constructs principals under `samba.example.com`, inserts entries, iterates the keytab to assert order, removes obsolete entries using target `kvno`, then iterates again. Heimdal and MIT differ in memory-keytab insertion order, so the test uses conditional iteration direction.

State and persistence: uses memory keytabs only; no filesystem keytab is modified. Talloc owns the principal array and temporary context.

Dependencies and integration: depends on Samba Kerberos utility wrappers, credentials Kerberos headers, cmocka, and the platform krb5 implementation. It validates keytab maintenance used by machine-account/service-principal key rotation.

Risks: ordering differs between Heimdal and MIT, so assertions are conditional. The test verifies cleanup does not delete the immediately previous kvno needed during rollover.

Test signals: registered as `test_kerberos` in `auth/wscript_build` for selftest.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/tests/kerberos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/tests/sam.c -->
# sources/user-network-fs/samba/source4/auth/tests/sam.c

Purpose: cmocka unit tests for `source4/auth/sam.c`, especially logon accounting, bad-password persistence, transaction behavior, and memory ownership.

Important APIs/helpers: the test directly includes `auth/sam.c`, wraps `dsdb_search_dn` and `samdb_msg_add_int64`, and provides mock implementations for LDB transactions, LDB modification requests, DSDB bad-password updates, RODC detection, `ldb_get_opaque`, clustered dbwrap open/store/exists/delete, and message allocation. Helpers build user/domain/PSO results, add binary objectSIDs, and compare extended DNs.

Control flow: setup resets all mock return values and creates loadparm/db contexts. Reread tests cover search failure, missing computed account-control, locked accounts, and successful rereads. Bad-password update tests cover domain/PSO lookup, transaction start/cancel/commit failures, locked-out rereads, DSDB count update failures, no-op updates, LDB request/control/wait failures, and indicator storage. Success-accounting tests cover RODC detection, transaction retry after deciding a write is needed, lastLogonTimestamp write failures, request failures, commit/rollback failures, and a spurious bad-password indicator. Indicator-specific tests cover missing loadparm, db open failure, missing objectSID, store/delete errors, and delete-not-found normalization.

State and persistence: all SAMDB and dbwrap state is mocked. Tests assert `in_transaction`, `transaction_cancelled`, and `transaction_committed`, and compare `talloc_total_size()` before/after operations to catch leaks.

Dependencies and integration: depends on cmocka, LDB, NDR security SID encoding, and the implementation under test. Linked with wrap ldflags from `wscript_build`.

Risks covered: account lockout races, audit-noise avoidance, objectSID-keyed temporary indicators, RODC local controls, error mapping, transaction leaks, and memory leaks. It does not exercise real SAMDB modules or cluster DB behavior.

Test signals: selftest binary `test_auth_sam` provides focused coverage for the most failure-prone code paths in `auth/sam.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/tests/sam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/unix_token.c -->
# sources/user-network-fs/samba/source4/auth/unix_token.c

Purpose: converts Windows security-token/session data into UNIX uid/gid/group identity data for filesystem/process access.

Important APIs: `security_token_to_unix_token()` maps token SIDs to UNIX ids. `fill_unix_info()` creates `auth_user_info_unix` names. `auth_session_info_fill_unix()` fills both UNIX token and info from a session. `auth_session_info_set_unix()` manually sets uid/gid without winbind lookup.

Control flow: SYSTEM tokens get a zeroed `security_unix_token`, implying uid/gid 0. Normal tokens must contain primary user and group SIDs. The code builds an `id_map` array for all SIDs, calls `wbc_sids_to_xids()`, derives uid from primary user SID, gid from primary group SID, and group list from all GID-capable SIDs. Name filling combines domain, winbind separator, and account name, then creates a sanitized original username.

State and persistence: no persistent writes. Results are talloc-owned under the session or caller context.

Dependencies and integration: depends on security token helpers, winbind client SID-to-XID mapping, and loadparm's winbind separator. Used after authentication when Samba needs POSIX credentials for local file operations.

Risks: access is denied for tokens lacking primary SID slots. Any unmappable primary user/group or remaining group SID fails with `NT_STATUS_INVALID_SID` after debug logging the whole token. Manual set path avoids winbind and therefore must only be used by trusted callers that already know correct uid/gid values.

Test signals: indirect coverage from authentication/session and file-service tests; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/unix_token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/wscript_build -->
# sources/user-network-fs/samba/source4/auth/wscript_build

Purpose: Waf build definitions for the source4 authentication components, tests, and Python auth module.

Important build targets: recurses into `gensec`, `kerberos`, and `ntlm`; defines `auth_session`, private `auth_unix_token`, `samba_server_gensec`, `auth_system_session`, and `auth4_sam`; builds selftest binaries `test_kerberos`, `test_auth_sam`, and conditionally `test_heimdal_gensec_unwrap_des`; builds Python module `pyauth` as `samba/auth.so`.

Control flow: subsystem/library declarations specify source files, autoproto headers, public headers/dependencies, and private dependencies. Test binaries use cmocka and targeted linker wrapping; `test_auth_sam` wraps DSDB/search and integer timestamp add functions, while the Heimdal unwrap test wraps crypto/parser/memory functions.

State and persistence: build metadata only. It generates autoproto headers and build products through Waf but stores no runtime state.

Dependencies and integration: connects the files in this subset to Samba credentials, SAMDB, security, LDB, tevent, GENSEC, auth4, winbind client, Kerberos, Python embedding, and conditional Heimdal/system-GSSAPI config symbols.

Risks: dependency declarations shape ABI visibility and test availability. Conditional Heimdal test gating means DES unwrap regression coverage is absent with system GSSAPI or non-Heimdal builds. Linker wrap flags are platform-sensitive.

Test signals: the file is the registration point for all three auth tests studied here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/wscript_configure -->
# sources/user-network-fs/samba/source4/auth/wscript_configure

Purpose: Waf configure checks for PAM availability in the auth area.

Important checks: `conf.CHECK_HEADERS('security/pam_appl.h')` checks for the PAM application header, and `conf.CHECK_FUNCS_IN('pam_start', 'pam', checklibc=True)` checks for `pam_start` in libpam or libc.

Control flow: executed during configure to populate config symbols consumed by auth-related build code elsewhere.

State and persistence: writes configure results into Samba's generated configuration cache/headers; no runtime state.

Dependencies and integration: integrates platform PAM discovery with authentication modules that may be built conditionally outside this exact file list.

Risks: platform-specific PAM layout can affect whether PAM-dependent auth code is compiled. This tiny file has no local validation beyond Waf's check helpers.

Test signals: configure/build success is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/wscript_configure -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/cldap_server/cldap_server.c -->
# sources/user-network-fs/samba/source4/cldap_server/cldap_server.c

Purpose: implements the CLDAP server task for Samba AD DC locator/rootDSE queries over UDP/389.

Important APIs/functions: `server_service_cldapd_init()` registers the service. `cldapd_task_init()` validates role/interfaces, opens SAMDB, and starts sockets. `cldapd_startup_interfaces()` chooses wildcard and interface-specific binds. `cldapd_add_socket()` binds a CLDAP socket and installs the incoming handler. `cldapd_request_handler()` validates incoming LDAP message shape. `cldap_error_reply()` sends error responses.

Control flow: service startup loads interfaces and refuses standalone/member-server roles. On AD DCs it creates `cldapd_server`, opens SAMDB with `system_session()`, binds wildcard addresses unless `bind interfaces only` is set, then binds each configured interface. Runtime handling ignores AbandonRequest, rejects non-search requests, non-empty base DN, and non-base scope with LDAP operations errors, and dispatches valid requests to `cldapd_rootdse_request()`.

State and persistence: `struct cldapd_server` holds task and SAMDB context for the service lifetime. No writes are performed here.

Dependencies and integration: uses Samba service/task registration, CLDAP library, tsocket, network interface helpers, SAMDB, loadparm role config, system session auth, and IRPC naming.

Risks: binding UDP/389 can fail per-interface; wildcard failure is tolerated only if at least one wildcard bind succeeds. Request validation is intentionally strict because CLDAP clients retry on silence. The shared SAMDB context relies on rootDSE code clearing request-specific opaque state.

Test signals: service startup and domain-controller CLDAP integration tests cover this path; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/cldap_server/cldap_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/cldap_server/cldap_server.h -->
# sources/user-network-fs/samba/source4/cldap_server/cldap_server.h

Purpose: declares CLDAP server shared structures and imports generated prototypes.

Important types: `struct cldapd_server` contains the owning `task_server` and the SAMDB `ldb_context`. It forward-declares `struct ldap_SearchRequest` and includes `cldap_server/proto.h`.

Control flow and integration: used by `cldap_server.c` and `rootdse.c` to share the service context and function prototypes. It includes CLDAP and LDAP client/server types needed by handler signatures.

State and persistence: defines the in-memory service state only; persistence is whatever SAMDB context points at.

Dependencies: `libcli/cldap/cldap.h`, `libcli/ldap/libcli_ldap.h`, and generated autoproto output from the build.

Risks: the small context structure is shared across synchronous request handling; adding per-request state here would risk leakage across clients. Generated proto inclusion means build ordering must produce `proto.h`.

Test signals: compile coverage through `service_cldap` and `CLDAPD` targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/cldap_server/cldap_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/cldap_server/rootdse.c -->
# sources/user-network-fs/samba/source4/cldap_server/rootdse.c

Purpose: handles valid CLDAP rootDSE search requests by synchronously querying SAMDB and returning LDAP search entries/results.

Important APIs/functions: `cldapd_rootdse_request()` is the external request entry point. `cldapd_rootdse_fill()` builds and executes the LDB search and converts the result to `ldap_SearchResEntry`.

Control flow: selected requested attributes are copied into a NULL-terminated array. An LDB base-scope search request is built against `cldapd->samctx` with the incoming LDAP filter tree and timeout. At most one result is accepted. Returned LDB message attributes are moved/stolen into the LDAP response entry unless attributes-only mode suppresses values. The caller sets `remoteAddress` opaque on the shared SAMDB context before the synchronous fill and clears it immediately after, then sends a CLDAP reply.

State and persistence: no database writes. It temporarily stores client address in SAMDB opaque state for audit/logging context and explicitly clears it to avoid contaminating later internal operations.

Dependencies and integration: uses tevent/LDB APIs, SAMDB, LDAP/CLDAP structures, NDR misc, and service task context. It is the query implementation called by `cldapd_request_handler()`.

Risks: synchronous use of a shared SAMDB context makes clearing `remoteAddress` essential. Attribute value ownership uses talloc stealing from LDB results into LDAP response structures. Error mapping mixes LDAP and LDB result codes, so callers see LDB errors as result codes in some paths.

Test signals: integration tests for DC locator/rootDSE CLDAP behavior are the expected coverage; no direct cmocka test here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/cldap_server/rootdse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/cldap_server/wscript_build -->
# sources/user-network-fs/samba/source4/cldap_server/wscript_build

Purpose: Waf build definitions for the CLDAP service module and helper subsystem.

Important targets: `service_cldap` builds `cldap_server.c` as a `service` module with init function `server_service_cldapd_init`, external/internal module metadata, and deps `CLDAPD process_model netif`. `CLDAPD` builds `rootdse.c`, generates `proto.h`, and depends on `cli_cldap` and `ldbsamba`.

Control flow: the service target registers startup logic; the subsystem target supplies rootDSE request handling and generated prototypes consumed by the header.

State and persistence: build metadata only.

Dependencies and integration: links CLDAP service code to Samba's process model, network-interface handling, CLDAP client/server library, and LDB Samba helpers.

Risks: missing `CLDAPD` dependency or autoproto generation would break `cldap_server.h` consumers. Module metadata determines whether the service can be loaded by Samba's service framework.

Test signals: build success and AD DC service startup tests validate this wiring.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/cldap_server/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/cifsdd.c -->
# sources/user-network-fs/samba/source4/client/cifsdd.c

Purpose: main program for `cifsdd`, a dd-like copy utility that can read/write local paths or SMB UNC paths using Samba client libraries.

Important APIs/functions: argument helpers `set_arg_argv()`, `set_arg_val()`, `check_arg_bool()`, `check_arg_numeric()`, and `check_arg_pathname()` manage dd-style options. `copy_files()` performs block copying. `open_file()` applies direct/sync/oplock/write flags and delegates to `dd_open_path()`. `print_transfer_stats()` and `dd_handle_signal()` provide dd-like runtime behavior. `main()` initializes Samba command-line state, parses popt plus dd options, validates input/output, installs signal handlers, and runs the copy.

Control flow: defaults set 4096-byte `bs/ibs/obs`, unlimited count, zero skip/seek, and no IO flags. Popt parses Samba connection/credential options, remaining `name=value` args configure dd options, and `bs=` updates both `ibs` and `obs`. Copying allocates a buffer twice the larger block size, opens input/output handles with negotiated max transmit size, seeks by block counts, loops until SIGINT/count/EOF, fills enough input for an output block with `dd_fill_block()`, flushes output through `dd_flush_block()`, and prints stats at EOF or SIGINT. SIGUSR1 prints stats and continues.

State and persistence: global `dd_stats` records block/byte counters; signal counters are simple globals. File/SMB contents are modified through the output IO handle.

Dependencies and integration: uses Samba cmdline/popt, loadparm SMB client options, resolver, GENSEC settings, tevent event context, and IO abstractions declared in `cifsdd.h` and implemented elsewhere.

Risks: `count` defaults to `uint64_t)-1`, so multiplication with `ibs` is intentionally huge but can overflow for extreme block sizes. Seek return values are ignored. `set_arg_val()` duplicates path strings without freeing old values, acceptable for process lifetime but not reusable library style. Signal counters are not `sig_atomic_t`.

Test signals: client tests outside this subset (`source4/client/tests/test_cifsdd.sh`) likely cover CLI behavior; no direct C unit test here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/cifsdd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/cifsdd.h -->
# sources/user-network-fs/samba/source4/client/cifsdd.h

Purpose: declares shared argument, statistics, and IO abstraction types for the `cifsdd` utility.

Important APIs/types: `enum argtype` and `struct argdef` describe dd-style options. `set_arg_argv()`, `set_arg_val()`, and `check_arg_*()` expose argument storage. `struct dd_stats_record` holds full/partial block and byte counters for input/output. `dd_seek_func`, `dd_read_func`, `dd_write_func`, and `struct dd_iohandle` abstract local or SMB IO. Flags define EOF, direct IO, sync IO, write mode, and oplock. `dd_open_path()`, `dd_fill_block()`, and `dd_flush_block()` are the core IO helpers implemented outside `cifsdd.c`.

Control flow and integration: `cifsdd.c` configures args and opens handles through this interface; lower-level IO code can provide local or SMB implementations behind the function pointers.

State and persistence: declares global `PROGNAME` and `dd_stats`; runtime state is held in IO handles and counters. Persistence is performed only by implementations behind write handles.

Dependencies: forward declares Samba client option/session/event/GENSEC-related types so the header can stay lightweight while still exposing `dd_open_path()`.

Risks: the IO function pointer contract relies on implementations setting `DD_END_OF_FILE` and updating `dd_stats` consistently. `io_flags` mixes capability/configuration bits with EOF state.

Test signals: exercised by `cifsdd` CLI/integration tests and any tests of the lower-level IO implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/client/cifsdd.h -->
