# subset-b-009899 Research

Grouped source research for the Samba source3 build scripts and source4 Kerberos/GSSAPI authentication files in `subset-b-009899`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/wscript -->
# sources/user-network-fs/samba/source3/wscript

## Purpose

This Waf script defines the configure-time policy for Samba's `source3` tree. It adds user-facing options for optional subsystems, probes the host OS and dependency surface, decides which features and VFS/passdb/auth/idmap modules are available, and writes the resulting `include/config.h` plus Waf environment values consumed by `source3/wscript_build` and recursive subdirectories.

## Important APIs, Functions, And Data

The two top-level entry points are `options(opt)` and `configure(conf)`. `options()` exposes module placement controls through `--with-static-modules` and `--with-shared-modules`, plus many `samba_add_onoff_option()` toggles such as winbind, ADS, CUPS, PAM, ACLs, quotas, clustering, CephFS, GlusterFS, Spotlight, WSP, regedit, winexe, fake kaserver, profiling, and libarchive.

`configure(conf)` is the main body. It initializes `default_static_modules`, `default_shared_modules`, `required_static_modules`, `forced_static_modules`, and `forced_shared_modules`, then mutates them as feature checks succeed. It relies on Waf/Samba helpers such as `CHECK_HEADERS`, `CHECK_FUNCS`, `CHECK_FUNCS_IN`, `CHECK_CODE`, `CHECK_CFG`, `CHECK_LIB`, `CHECK_STRUCTURE_MEMBER`, `SET_TARGET_TYPE`, `DEFINE`, `CONFIG_SET`, and `SAMBA_CONFIG_H`.

Notable configure outputs include `HAVE_INOTIFY`, `HAVE_KERNEL_OPLOCKS_LINUX`, `HAVE_FAM`, `HAVE_CUPS`, `HAVE_KRB5`, `HAVE_ADS`, `WITH_WINBIND`, `WITH_PAM`, `WITH_PROFILE`, `WITH_QUOTAS`, `CLUSTER_SUPPORT`, `HAVE_CEPH`, `HAVE_GLUSTERFS`, `HAVE_LIBURING`, `WITH_WSP`, `WITH_SPOTLIGHT`, `STRING_STATIC_MODULES`, `STRING_SHARED_MODULES`, `static_decl_<prefix>`, and `static_init_<prefix>(mem_ctx)`.

## Control Flow

Configuration begins with broad libc/kernel probes, then feature-specific blocks. Early code detects platform primitives such as headers, stat fields, file locking, sendfile variants, inotify, Linux leases, netlink, filesystem hints, timestamps, quotas, ACLs, and credential-changing syscalls. Optional library blocks either define usable target types or create empty target placeholders so later dependency declarations can stay uniform.

The ADS/Kerberos block is a central gate. Unless `--without-ads` is used, it checks Kerberos enctypes, ticket APIs, keytab/free functions, GSS PAC extraction, lucid context export, and LDAP transport wrapping. If required Kerberos or LDAP capability is absent, it disables ADS or fails when ADS was explicitly requested. This output directly affects whether `HAVE_KRB5` and `HAVE_ADS` are available to the build.

Late in the script, module lists are populated from defaults and feature gates. Explicit `--with-static-modules` and `--with-shared-modules` are converted to lists, `pdb_ldap` is normalized to `pdb_ldapsam`, `ALL`, `!DEFAULT`, `!FORCED`, and `!module` are applied, and hard constraints prevent required-static modules from being shared or forced modules from moving to the wrong side. The final lists are grouped by prefixes `vfs`, `pdb`, `auth`, `nss_info`, `charset`, `idmap`, and `gpext`, exported into `conf.env`, and used to generate static init macros.

## State And Persistence

This script does not persist runtime application state. Its persistent outputs are build state: Waf `conf.env`, generated configure defines in `include/config.h`, target type declarations for missing optional libraries, and module list strings/macros compiled into source3. The script also controls whether recursive build files will build modules by setting `conf.env['static_modules']`, `conf.env['shared_modules']`, and per-prefix lists such as `VFS_STATIC`/`VFS_SHARED`.

## Dependencies And Integration Points

It depends on Waf's `Options`, `Logs`, and `Errors`, Samba's wafsamba helpers, `build.charset`, `samba_utils.TO_LIST`, and `samba3`. It integrates with `source3/wscript_build` through environment variables such as `with_avahi`, `with_ctdb`, `dmapi_lib`, `legacy_quota_libs`, `with_wsp`, and `spotlight_backend_es`. It also integrates with recursive module `wscript_build` files through `SAMBA3_IS_ENABLED_MODULE()` and the generated static/shared module env lists.

Key external dependencies include POSIX libc, Kerberos/GSSAPI, LDAP, CUPS, PAM, ACL libraries, FAM, libarchive, libevent, DMAPI variants, capabilities, tirpc, CephFS, GlusterFS, liburing, ncurses, mingw, OpenSSL/libcrypto DES, AFS headers, DBus for `vfs_snapper`, gettext/intltool, flex/bison/Jansson/Unicode normalization for Spotlight, and kernel-specific filesystem APIs.

## Risks And Edge Cases

The file has many execute-time configure tests; cross-compilation and restricted build sandboxes can change outcomes. Optional dependencies sometimes default to required behavior, for example libarchive is required by default and ACL support fails the build unless disabled. ADS is particularly sensitive to Kerberos/GSSAPI feature coverage. Module resolution is order-independent by design, but incorrect entries in `--with-static-modules` or `--with-shared-modules` can conflict with required/forced placement and raise Waf errors. Empty target placeholders are useful but can hide disabled optional features until link or runtime behavior is inspected.

## Test Signals

Useful validation signals are successful `./configure`/Waf configure on representative platforms, generated `include/config.h` defines, logged static/shared module lists, and builds of optional feature combinations. Selftest and developer builds exercise extra modules. Focused test matrices should cover `--without-ads`, explicit ADS failure, ACL disabled/enabled, libarchive disabled with selftest, quota/sendfile variants, CephFS/GlusterFS presence and absence, Spotlight backends, and static/shared module override syntax.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/wscript -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/wscript_build -->
# sources/user-network-fs/samba/source3/wscript_build

## Purpose

This Waf build script declares the `source3` build graph. It maps source3 libraries, subsystems, binaries, Python extension modules, tests, generated build options, and recursive subdirectories into Samba build targets. It consumes the configure results from `source3/wscript` and other top-level checks to decide which source files and targets are included.

## Important APIs, Functions, And Targets

The file is declarative and uses Waf/Samba build methods on `bld`: `SAMBA_BLDOPTIONS`, `SETUP_BUILD_GROUPS`, `SAMBA3_LIBRARY`, `SAMBA3_SUBSYSTEM`, `SAMBA3_BINARY`, `SAMBA_BINARY`, `SAMBA_LIBRARY`, `SAMBA_SUBSYSTEM`, `SAMBA3_PYTHON`, `RECURSE`, `ENFORCE_GROUP_ORDERING`, and `CHECK_PROJECT_RULES`.

Core library/subsystem declarations include `netapi`, `gse`, `msrpc3`, `AVAHI`, `GROUPDB`, `TLDAP`, `samba-passdb`, `pdb`, `SMBREGISTRY`, `REG_FULL`, `KRBCLIENT`, `samba3util`, `samba-cluster-support`, `TDB_LIB`, `samba3core`, `auth_generic`, `libsmb`, `secrets3`, `smbldap`, `ads`, `SMBCONF_PARAM`, `smbconf`, `sysquotas`, `smbd_base`, `LOCKING`, `PROFILE`, printing subsystems, `LIBNET`, `LIBNMB`, RPC client helpers, `samba3-util`, `CHARSET3`, and error mapping subsystems.

Binary and test targets include `smbd/smbd`, `client/smbclient`, `smbspool`, `smbspool_krb5_wrapper`, `smbspool_argv_wrapper`, `smbconftort`, `test_tldap`, `test_registry_regfio`, `test_adouble`, `test_mdsparser_es`, `versiontest`, `timelimit`, `vlp`, `samba-bgqd`, and `spotlight2es`. Python extension modules include `pysmbd`, `pylibsmb`, `pymdscli`, and `pys3smbconf`.

## Control Flow

The build starts by generating `smbd/build_options.c` and setting build groups. It then declares low-level libraries and subsystems, higher-level server/client components, binaries, Python bindings, and finally recurses into subdirectories such as `auth`, `libgpo/gpext`, `librpc`, `libsmb`, `modules`, `param`, `passdb`, `rpc_server`, `script`, `winbindd`, examples, utilities, `nmbd`, and torture tests.

The script composes several target source lists conditionally. `SAMBA_CLUSTER_SUPPORT_SOURCES` and dependencies switch between CTDB implementations and dummy cluster support based on `bld.env.with_ctdb`. `NOTIFY_SOURCES` and `NOTIFY_DEPS` add inotify and FAM notification implementations when configure set the corresponding variables. `SMB1_SOURCES` is included only when `WITH_SMB1SERVER` is configured. `PROFILE` switches between real profiling and a dummy source based on `WITH_PROFILE`.

## State And Persistence

No runtime state is stored here. The file produces build-system state: target declarations, dependency edges, install paths, ABI metadata, public headers, pkg-config files, selftest-only flags, and recursive traversal order. Some targets become empty or disabled indirectly through configure variables such as `HAVE_LDAP`, `HAVE_CUPS`, `HAVE_INOTIFY`, `SAMBA_FAM_LIBS`, `WITH_SMB1SERVER`, `WITH_PROFILE`, `HAVE_CEPH`, and `spotlight_backend_es`.

## Dependencies And Integration Points

This script is tightly coupled to `source3/wscript` for configured feature variables and module decisions. It also depends on common Samba build helpers, generated NDR targets, Kerberos/GSSAPI libraries, LDAP, talloc/tevent/tdb, DB wrap libraries, CUPS, archive, Jansson, cmocka, Python embed helper names, and many internal source3/source4 subsystems.

Important integration points are `gse` depending on `krb5samba gensec smbconf KRBCLIENT secrets3`, `msrpc3` depending on GENSEC and Schannel/NTLM pieces, `libsmb` depending on `auth_generic`, `KRBCLIENT`, SPNEGO parsing, CLDAP, and SMB client common code, `ads` depending on LDAP/Kerberos/RPC/netlogon/passdb, and `smbd_base` depending on VFS, passdb, RPC, locking, leases, notification, quotas, and SMB1/SMB2 server source sets.

## Risks And Edge Cases

Because the file is a large dependency graph, regressions often appear as link-order issues, missing generated targets, unexpected enabled/disabled optional subsystems, or circular dependency problems. Comments explicitly warn that `smbconf` should be the only direct consumer of some registry/config subsystems to avoid cycles, and that `secrets3` must not depend on high-level PDB code. Conditional source concatenation means configure variables must be set consistently; missing empty target placeholders from configure can break otherwise optional dependency edges.

## Test Signals

Signals include a clean Waf build, target availability for configured options, `CHECK_PROJECT_RULES()` success, selftest targets building only under `for_selftest`, ABI checks for public libraries, successful recursive builds in all listed subdirectories, and focused link tests for `smbd`, `smbclient`, `ads`, `gse`, `smbd_base`, notification variants, CUPS-dependent wrappers, Spotlight ES tests, and Python extension modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/auth.h -->
# sources/user-network-fs/samba/source4/auth/auth.h

## Purpose

This header defines the Samba4 authentication backend interface and exports the core auth/session helpers used by source4 services and GENSEC integration. It standardizes how auth modules advertise password-check operations, how auth contexts are created, and how authenticated users are converted into `auth_session_info`.

## Important APIs, Types, And Functions

The primary interface type is `struct auth_operations`, with `name`, `want_check()`, `check_password_send()`, and `check_password_recv()` members. `want_check()` lets a backend claim or decline a supplied login attempt. The send/recv pair implements asynchronous password verification through `tevent_req`, returning interim domain controller user info, client/server audit records, and an authoritative flag.

`struct auth_method_context` links a backend into an auth context and stores `auth_ctx`, `ops`, recursion `depth`, and backend `private_data`. `struct auth_critical_sizes` records ABI-sensitive structure sizes and the `AUTH4_INTERFACE_VERSION`, which is currently zero for the unstable Samba4 interface.

Exported helpers include `encrypt_user_info()`, `auth_get_challenge()`, `authsam_account_ok()`, `authsam_make_user_info_dc()`, `authsam_update_user_info_dc()`, `authsam_shallow_copy_user_info_dc()`, `auth_system_session_info()`, `auth_context_create_methods()`, `auth_methods_from_lp()`, `auth_context_create()`, `auth_context_create_for_netlogon()`, synchronous and asynchronous `auth_check_password()` variants, `auth_context_set_challenge()`, `auth4_init()`, `auth_register()`, `server_service_auth_init()`, LDAP simple bind authentication send/recv/sync helpers, and `samba_server_gensec_start()`/`samba_server_gensec_krb5_start()`.

## Control Flow

The header itself has no executable flow, but it defines the expected flow. Server code creates an `auth4_context` from configured methods, asks each backend whether it wants to check the supplied info, starts an asynchronous password check, and receives an `auth_user_info_dc` result plus audit metadata. Session creation helpers then turn account data, PAC data, or system credentials into `auth_session_info`.

GENSEC server setup flows through `samba_server_gensec_start()` or the Kerberos-specific wrapper, passing event/messaging/loadparm contexts, server credentials, and target service into the GENSEC layer.

## State And Persistence

State is carried in caller-owned contexts and talloc-owned structures: auth contexts, method contexts, supplied user info, interim domain user info, session info, and backend `private_data`. The header does not define persistent storage, but declared functions integrate with SAM/ldb, generated NDR types, loadparm configuration, credentials, challenges, and audit structures.

## Dependencies And Integration Points

The header includes PAC and auth NDR definitions plus common auth declarations, then pulls in session, Unix token, system session, and security headers. Forward declarations connect it to `ldb`, `loadparm_context`, `imessaging_context`, `gensec_security`, `cli_credentials`, `smb_krb5_context`, and tsocket addresses. It is included by GENSEC Kerberos implementations to generate session information after ticket/PAC verification and by source4 services that need password or LDAP bind authentication.

## Risks And Edge Cases

The ABI/interface version is explicitly unstable, so modules compiled against this interface are sensitive to structure changes. Async auth implementations must return authoritative information correctly; mistakes can cause fallback or lockout behavior to be wrong. Session key and PAC integration is security-sensitive because downstream SMB/RPC signing and authorization depend on correct `auth_session_info`. LDAP simple bind APIs must preserve TLS and remote/local address context for policy and auditing.

## Test Signals

Good signals include unit and integration tests for auth module registration, configured method ordering, challenge generation, password check send/recv behavior, LDAP simple binds with and without TLS, account policy checks, SAM-derived session info, system sessions, netlogon-specific contexts, and GENSEC server startup using Kerberos credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_gssapi.c -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_gssapi.c

## Purpose

This file implements Samba's real GSSAPI-backed GENSEC Kerberos mechanisms. It registers SPNEGO-over-GSSAPI, Kerberos-over-GSSAPI, and SASL GSSAPI mechanisms, handles client/server security context negotiation, enforces optional channel binding, negotiates SASL security strength, exposes wrap/unwrap and packet sign/seal operations, extracts session keys and PAC/session information, and tracks credential expiry.

## Important APIs, Functions, And State

The public entry point is `gensec_gssapi_init(TALLOC_CTX *ctx)`, which registers `gssapi_spnego`, `gssapi_krb5`, and `gssapi_krb5_sasl` security ops. Major internal functions are `gensec_gssapi_start()`, `gensec_gssapi_server_start()`, `gensec_gssapi_sasl_server_start()`, `gensec_gssapi_client_creds()`, `gensec_gssapi_client_start()`, `gensec_gssapi_sasl_client_start()`, `gensec_gssapi_update_internal()`, update send/recv wrappers, `gensec_gssapi_wrap()`, `gensec_gssapi_unwrap()`, packet seal/unseal/sign/check helpers, `gensec_gssapi_have_feature()`, `gensec_gssapi_expire_time()`, `gensec_gssapi_session_key()`, `gensec_gssapi_session_info()`, `gensec_gssapi_sig_size()`, and `gensec_gssapi_final_auth_type()`.

State lives in `struct gensec_gssapi_state` from `gensec_gssapi.h`: GSS context, server/client names, requested and negotiated flags, delegated credential handle, expiry time, selected mechanism OID, input channel bindings, Kerberos context, client/server credential containers, SASL mode and stage, SASL protection bits, max wrap buffer size, exchange count, cached signature size, and target principal string.

## Control Flow

Start-up allocates state, copies optional channel bindings from `gensec_security`, chooses requested GSS flags from settings and wanted GENSEC features, selects SPNEGO or Kerberos OID based on DCERPC auth type, initializes a Samba Kerberos context, and sets defaults for credentials and SASL state. Heimdal builds also set default realm and disable DNS canonicalization.

Client update flow first obtains client GSS credentials, builds or imports the target service principal, and calls `gss_init_sec_context()`. MIT builds include a fallback path for external trusts: they first try the client realm and on `KRB5KDC_ERR_S_PRINCIPAL_UNKNOWN` can derive the server realm from the hostname and retry. Heimdal builds temporarily route KDC traffic through Samba's event-aware send function.

Server update flow calls `gss_accept_sec_context()` with server credentials and optional channel bindings, captures client name and delegated credentials, and maps missing or bad channel-binding flags to `NT_STATUS_BAD_BINDINGS` when bindings are required. Successful non-SASL negotiation moves directly to `STAGE_DONE`; SASL mechanisms move to `STAGE_SASL_SSF_NEG` for a second negotiation.

SASL negotiation wraps a four-byte proposal/acceptance token with GSS. The server advertises supported `NEG_SEAL`, `NEG_SIGN`, and `NEG_NONE` plus max wrap size. The client intersects that with requested GENSEC features and returns accepted protection and max size. The server validates the accepted bits and both sides finish in `STAGE_DONE`.

## State And Persistence

The GSS context and names persist only for the lifetime of the `gensec_security` talloc tree. The destructor releases delegated credentials, deletes the GSS security context, and releases GSS names. Delegated client credentials may be transferred into `session_info->credentials`, after which the state clears its handle to avoid double release. Expiry time is stored as NTTIME after successful negotiation. No disk persistence is performed.

## Dependencies And Integration Points

The implementation depends on system GSSAPI, Samba Kerberos wrappers, credential containers, GENSEC registration, tevent, tsocket channel binding data, PAC utilities, session generation, loadparm settings, and DCE/RPC auth type constants. It integrates with SMB/RPC signing and sealing through GENSEC ops, with LDAP SASL through the `sasl_name = "GSSAPI"` mechanism, with SPNEGO through the SPNEGO OID, and with authorization through `gssapi_obtain_pac_blob()` plus `gensec_generate_session_info_pac()`.

## Risks And Edge Cases

Security-sensitive risks include incorrect channel-binding enforcement, accepting a context without integrity when signing/session key features are required, mishandling SASL max wrap sizes, failing to release GSS buffers/names/contexts, or misreporting negotiated features. Kerberos realm fallback differs between MIT and Heimdal. Old encryption types intentionally suppress `GENSEC_FEATURE_NEW_SPNEGO`, so changes to key type logic can affect compatibility. Delegation handling must avoid both credential leaks and double frees.

## Test Signals

Useful signals include Kerberos client/server GENSEC handshakes, SPNEGO handshakes, SASL GSSAPI LDAP binds with sign/seal/none options, channel-binding required and optional cases, external trust principal fallback on MIT, delegated credential sessions, PAC-backed and no-PAC session info generation, packet sign/check and seal/unseal tests, max wrap size limits, expired credential handling, and final auth type/session key extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_gssapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_gssapi.h -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_gssapi.h

## Purpose

This header exposes the private state layout for the GSSAPI GENSEC implementation. It is kept visible enough for tests, especially RPC/PAC tests, to inspect the PAC-related GSSAPI context state.

## Important APIs, Types, And Constants

`enum gensec_gssapi_sasl_state` defines the negotiation stages: `STAGE_GSS_NEG`, `STAGE_SASL_SSF_NEG`, `STAGE_SASL_SSF_ACCEPT`, and `STAGE_DONE`. `NEG_SEAL`, `NEG_SIGN`, and `NEG_NONE` encode SASL security-layer choices.

`struct gensec_gssapi_state` is the central per-security-context state. It stores `gssapi_context`, imported `server_name` and accepted `client_name`, wanted/got GSS flags, delegated credential handle, expiry time, selected GSS OID, channel-binding structures, Samba Kerberos context, client/server GSS credential containers, SASL enablement and state, negotiated SASL protection, max wrap size, exchange count, cached signature size, and target principal.

## Control Flow

The header has no executable flow, but the enum drives `gensec_gssapi_update_internal()` in `gensec_gssapi.c`. Normal GSS negotiation progresses from `STAGE_GSS_NEG` to `STAGE_DONE`; SASL mode progresses from `STAGE_GSS_NEG` to `STAGE_SASL_SSF_NEG`, then on the server to `STAGE_SASL_SSF_ACCEPT`, and finally to `STAGE_DONE`.

## State And Persistence

All fields are in-memory and talloc-owned through the associated `gensec_security` object. GSS handles must be released by the C file destructor. `max_wrap_buf_size`, `sasl_protection`, `gss_got_flags`, and `sig_size` are cached negotiation results that later wrap/sign/seal calls trust.

## Dependencies And Integration Points

The type uses GSSAPI types (`gss_ctx_id_t`, `gss_name_t`, `gss_cred_id_t`, `gss_OID`, channel bindings), Samba `NTTIME`, `smb_krb5_context`, and `gssapi_creds_container`. It is included by the implementation and test code that needs direct inspection.

## Risks And Edge Cases

Because this is a private-but-visible state structure, field changes can break tests or any internal code that inspects it. Negotiation correctness depends on the enum and bit constants matching the C implementation. Stale cached `sig_size` or mismatched SASL protection bits would affect subsequent packet sizing and security decisions.

## Test Signals

Tests should inspect stage transitions, negotiated `sasl_protection`, `gss_got_flags`, selected OID, channel binding pointer setup, delegated credential transfer, and cached wrap/sign sizing after successful GSSAPI and SASL handshakes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_gssapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5.c -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5.c

## Purpose

This file implements Samba's raw Kerberos GENSEC backend plus a disabled fake-GSSAPI Kerberos wrapper mode used for compatibility. It creates AP-REQ/AP-REP tokens with the Kerberos library, accepts raw Kerberos tickets from clients, exposes session keys and PAC-backed session information, supports `krb5_mk_priv` sealing for the raw mode, and registers the `krb5` and `fake_gssapi_krb5` GENSEC mechanisms.

## Important APIs, Functions, And State

The public entry point is `gensec_krb5_init(TALLOC_CTX *ctx)`. Major internal functions include `gensec_krb5_start()`, server/client start wrappers, `gensec_krb5_common_client_creds()`, `gensec_gssapi_gen_krb5_wrap()`, `gensec_gssapi_parse_krb5_wrap()`, `gensec_krb5_update_internal()`, update send/recv wrappers, `gensec_krb5_session_key()`, Heimdal and MIT variants of `gensec_krb5_session_info()`, `gensec_krb5_wrap()`, `gensec_krb5_unwrap()`, `gensec_krb5_have_feature()`, and `gensec_krb5_final_auth_type()`.

State is `struct gensec_krb5_state` from `gensec_krb5_internal.h`: state-machine position, Samba Kerberos context, Kerberos auth context, encoded ticket, long-term keyblock for PAC verification, decoded ticket, fake-GSSAPI flag, and AP-REQ options.

## Control Flow

Startup obtains credentials from GENSEC, allocates state, fetches or creates a Kerberos context through credentials, initializes a `krb5_auth_context`, enables sequence handling, translates optional local and remote tsocket addresses into Kerberos addresses, and stores them on the auth context.

Client start rejects missing hostnames, IP addresses, and `localhost`, then sets `GENSEC_KRB5_CLIENT_START`, `AP_OPTS_USE_SUBKEY`, and optional mutual authentication. `gensec_krb5_common_client_creds()` acquires a ccache, optionally installs Heimdal event routing, and builds an AP-REQ either for an explicit parsed target principal with `krb5_get_credentials()`/`krb5_mk_req_extended()` or for service/hostname with `krb5_mk_req()`.

`gensec_krb5_update_internal()` is the handshake state machine. In client-start state it emits the encoded ticket, optionally wrapped as a GSS Kerberos application token, and either finishes or waits for mutual auth. In mutual-auth state it unwraps an AP-REP if fake-GSSAPI mode is active and validates it with `krb5_rd_rep()`. In server-start state it obtains a keytab, derives or nulls the acceptor principal based on credential specificity and password-backed keytabs, unwraps optional fake-GSS tokens, calls `smb_krb5_rd_req_decoded()`, stores decoded ticket and keyblock, emits AP-REP raw or wrapped, and moves to done.

Session info differs by Kerberos provider. Heimdal uses `krb5_ticket_get_client()` and `krb5_ticket_get_authorization_data_type()`. MIT copies `ticket->enc_part2->client` and finds PAC authdata via `krb5_find_authdata()`. Both decode and verify the PAC with the stored long-term keyblock, call `gensec_generate_session_info_pac()`, and attach the Kerberos session key.

## State And Persistence

All state is per-handshake memory under `gensec_security`. The destructor frees encoded tickets, decoded tickets, keyblocks, and auth contexts. Credentials, ccache, keytab, ticket, keyblock, auth context sequence numbers, and AP options persist only while the GENSEC object is live. There is no disk persistence beyond Kerberos libraries' normal ccache/keytab usage.

## Dependencies And Integration Points

The implementation depends on Samba credentials, Kerberos wrappers, PAC utilities, ASN.1 helpers for fake-GSS wrapping, GENSEC registration, tevent, tsocket, DCE/RPC constants, and `smb_krb5_rd_req_decoded()` from the Heimdal/MIT compatibility files. It integrates with `auth.h` through session-info generation, with Kerberos credentials/keytab/ccache providers, and with GENSEC feature probing for session key/sign/seal.

## Risks And Edge Cases

Risk areas include hostname validation, address binding failures, ccache and KDC error mapping, fake-GSS wrapper parsing accepting malformed tokens, mutual-auth state handling, provider-specific ticket/PAC access, keytab principal matching behavior, long-term key selection for PAC verification, and feature advertising. Raw `krb5` reports signing/sealing through `krb5_mk_priv`, while fake-GSSAPI mode disables sign/seal features; callers must select the correct mechanism.

## Test Signals

Useful tests cover client AP-REQ generation with explicit principal and service/hostname, server AP-REQ acceptance with keytab principal and match-by-key paths, fake-GSS wrapper encode/decode, mutual authentication success and failure, ccache/KDC error mapping, PAC present and absent session info, MIT and Heimdal builds, session key extraction after done state, wrap/unwrap seal behavior, and feature flags for raw versus fake-GSS mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5.h -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5.h

## Purpose

This header declares a provider-normalized helper used by the raw Kerberos GENSEC backend to accept and decode AP-REQ tokens while also retrieving the decoded ticket and long-term key needed for PAC verification.

## Important API

`smb_krb5_rd_req_decoded()` takes a Kerberos context, auth context pointer, input AP-REQ data, keytab, optional acceptor principal, output AP-REP data, decoded ticket output, and keyblock output. It returns a Kerberos error code. The function is implemented differently for Heimdal and MIT in neighboring files but exposes a single signature to `gensec_krb5.c`.

## Control Flow

The header has no executable flow. At runtime, `gensec_krb5_update_internal()` calls this helper during server AP-REQ processing after it has acquired a keytab and chosen an acceptor principal. On success the caller stores the ticket/keyblock and sends the AP-REP output.

## State And Persistence

The helper fills caller-provided output pointers. The caller owns and later frees the decoded ticket, keyblock, and output buffer according to Kerberos provider rules. No persistent storage is defined here.

## Dependencies And Integration Points

It depends on Kerberos types from `system/kerberos.h` and Samba Kerberos helpers. It is the abstraction boundary between provider-specific Heimdal/MIT ticket decoding and the common raw GENSEC Kerberos implementation.

## Risks And Edge Cases

The contract is security-sensitive because PAC verification depends on receiving the correct long-term keyblock. Provider implementations must initialize outputs to safe defaults and free partial results on failure. A mismatch between MIT/Heimdal semantics could cause leaks, failed mutual authentication, or PAC verification with the wrong key.

## Test Signals

Server-side Kerberos GENSEC tests should confirm that both MIT and Heimdal builds produce a decoded ticket, keyblock, AP-REP, and clean failure behavior for bad tickets, missing keytab entries, and principal mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_heimdal.c -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_heimdal.c

## Purpose

This Heimdal-specific file implements `smb_krb5_rd_req_decoded()` for the raw Kerberos GENSEC backend using Heimdal APIs. It preserves Heimdal license attribution because the code is derived from Heimdal acceptor logic.

## Important API And Functions

The sole function is `smb_krb5_rd_req_decoded()`. It uses Heimdal `krb5_rd_req_in_ctx` and `krb5_rd_req_out_ctx` objects, `krb5_rd_req_in_set_keytab()`, `krb5_rd_req_ctx()`, `krb5_rd_req_out_get_ticket()`, `krb5_rd_req_out_get_keyblock()`, and `krb5_mk_rep()`.

## Control Flow

The function initializes output pointers and AP-REP buffer to null/zero, allocates an input context, attaches the keytab, and calls `krb5_rd_req_ctx()` with the input token and optional acceptor principal. After successful acceptance it extracts the decoded ticket and keyblock from the output context, frees the output context, then creates an AP-REP with `krb5_mk_rep()`. On any error after outputs are allocated, it frees ticket, keyblock, and output data before returning the Kerberos error.

## State And Persistence

No long-lived state is created. The decoded ticket, keyblock, and AP-REP data are returned to the caller for storage in `gensec_krb5_state`. Temporary Heimdal contexts are freed before return.

## Dependencies And Integration Points

It depends on Heimdal Kerberos APIs, Samba Kerberos includes, and the common declaration in `gensec_krb5.h`. It is selected in Heimdal builds and called from `gensec_krb5.c` server-side AP-REQ processing.

## Risks And Edge Cases

Memory ownership is the main risk: partial ticket/keyblock/outbuf outputs must be freed on failure. The input context must always be freed after use. The helper assumes Heimdal can return the keyblock directly from `krb5_rd_req_out_get_keyblock()`, unlike the MIT implementation that looks up a long-term key separately.

## Test Signals

Heimdal builds should test successful AP-REQ accept, generated AP-REP, PAC verification using the returned keyblock, bad keytab or principal errors, and leak checks around failure paths after ticket or keyblock extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_heimdal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_helpers.c -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_helpers.c

## Purpose

This helper file exposes a small inspection API for the raw `krb5` GENSEC mechanism. It allows callers to determine whether the accepted Kerberos ticket has the initial-ticket flag set.

## Important APIs And Functions

`get_private_state()` validates that the current GENSEC mechanism name is exactly `krb5` and returns `private_data` as `struct gensec_krb5_state`. `gensec_krb5_initial_ticket()` returns `1` if the stored ticket has the initial flag, `0` if it does not, and `-1` if the mechanism is not raw krb5 or no ticket is available.

## Control Flow

`gensec_krb5_initial_ticket()` first calls `get_private_state()`. If no state or no ticket is present, it returns `-1`. Otherwise it reads the provider-specific flag location: Heimdal uses `ticket->ticket.flags.initial`; MIT uses `ticket->enc_part2->flags & TKT_FLG_INITIAL`.

## State And Persistence

The helper reads existing state only. It does not allocate, mutate, or persist data. It depends on `gensec_krb5_state->ticket` having been populated by server-side `smb_krb5_rd_req_decoded()`.

## Dependencies And Integration Points

It includes `auth/auth.h`, `auth/gensec/gensec.h`, `gensec_internal.h`, `gensec_krb5_internal.h`, Kerberos headers, and its public helper header. It integrates with code paths that need to distinguish initial tickets from non-initial service tickets after GENSEC authentication.

## Risks And Edge Cases

The mechanism-name check intentionally excludes `fake_gssapi_krb5`, even though it shares some raw Kerberos state shape. Calling before authentication completes returns `-1`. Provider-specific ticket layouts must stay aligned with MIT/Heimdal structures.

## Test Signals

Tests should call the helper after successful raw krb5 authentication with initial and non-initial tickets, before a ticket is accepted, and on non-krb5 mechanisms to verify `1`, `0`, and `-1` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_helpers.h -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_helpers.h

## Purpose

This header declares the raw Kerberos helper that reports whether the accepted ticket is an initial Kerberos ticket.

## Important API

`int gensec_krb5_initial_ticket(const struct gensec_security *gensec_security)` returns `1` for an initial ticket, `0` for a non-initial ticket, and `-1` for errors such as wrong mechanism or missing ticket. The header forward-declares `struct gensec_security` so callers do not need the full GENSEC definition just to see the prototype.

## Control Flow

There is no executable flow. The implementation in `gensec_krb5_helpers.c` validates the mechanism, reads private Kerberos state, and checks provider-specific ticket flags.

## State And Persistence

No state is defined by the header. The function observes the existing GENSEC Kerberos state created by a completed authentication exchange.

## Dependencies And Integration Points

The header is included by callers that need ticket-type information after raw Kerberos authentication. It depends only on the `gensec_security` forward declaration and is implemented against internal Kerberos state.

## Risks And Edge Cases

Consumers must handle `-1` distinctly from a valid non-initial result. A caller that treats any non-`1` value as non-initial would conflate unavailable state with an authenticated non-initial ticket.

## Test Signals

Compile coverage for consumers and runtime coverage for all three return classes are the useful signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_internal.h -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_internal.h

## Purpose

This private header defines the raw Kerberos GENSEC state machine enum and per-context state structure shared by `gensec_krb5.c` and helper code.

## Important Types

`enum GENSEC_KRB5_STATE` defines `GENSEC_KRB5_SERVER_START`, `GENSEC_KRB5_CLIENT_START`, `GENSEC_KRB5_CLIENT_MUTUAL_AUTH`, and `GENSEC_KRB5_DONE`.

`struct gensec_krb5_state` stores the current state, `smb_krb5_context`, `krb5_auth_context`, encoded ticket `enc_ticket`, long-term `keyblock`, decoded `ticket`, whether fake GSSAPI wrapping is active, and AP request options.

## Control Flow

The enum controls `gensec_krb5_update_internal()`. Client instances start in `CLIENT_START`, emit AP-REQ, optionally wait in `CLIENT_MUTUAL_AUTH`, then reach `DONE`. Server instances start in `SERVER_START`, accept AP-REQ and produce AP-REP, then reach `DONE`. Any update after done is invalid.

## State And Persistence

The struct is allocated under the GENSEC security context and released by the destructor in `gensec_krb5.c`. It owns Kerberos objects that require provider-specific free functions. It stores enough ticket/key material to generate session info and verify PAC data after the handshake.

## Dependencies And Integration Points

It includes Samba and Kerberos headers and is used by the raw Kerberos implementation and helper inspection code. It connects the GENSEC state machine to Kerberos credentials, AP options, ticket parsing, PAC verification, session key extraction, and fake-GSS wrapping.

## Risks And Edge Cases

Ownership and state transitions are sensitive. If `state_position` is wrong, clients may skip mutual auth or servers may accept extra updates. If `keyblock` or `ticket` is missing after server authentication, PAC/session-info generation fails. If `gssapi` is incorrectly set, tokens may be wrapped or unwrapped in the wrong format and feature advertising changes.

## Test Signals

Good tests cover client and server state transitions, destructor cleanup after partial failures, fake-GSS and raw token paths, session-info access after done, and invalid update calls after completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_mit.c -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_mit.c

## Purpose

This MIT Kerberos-specific file implements `smb_krb5_rd_req_decoded()` for the raw Kerberos GENSEC backend. It accepts an AP-REQ with MIT APIs, retrieves a long-term key from the keytab for PAC verification, and creates the AP-REP reply.

## Important APIs And Functions

`smb_krb5_get_longterm_key()` looks up a keytab entry for the ticket server principal, key version, and enctype with `krb5_kt_get_entry()`, copies the keyblock with `krb5_copy_keyblock()`, and frees the keytab entry.

`smb_krb5_rd_req_decoded()` calls `krb5_rd_req()` to accept the request, uses `smb_krb5_get_longterm_key()` to obtain the keyblock, and calls `krb5_mk_rep()` to produce the reply.

## Control Flow

Outputs are initialized to null/zero. The function accepts the AP-REQ with `krb5_rd_req()`, passing the auth context, optional acceptor principal, keytab, AP options output, and ticket output. It then retrieves the long-term key using the accepted ticket's server principal, kvno `0` for latest key, and ticket enctype. Finally it creates an AP-REP with `krb5_mk_rep()`. Failures after ticket allocation free the ticket; failures after key allocation free both ticket and keyblock.

## State And Persistence

No persistent state is stored. On success, ownership of `ticket`, `keyblock`, and `reply` transfers to the caller. The helper deliberately retrieves the long-term key from the keytab, not merely a subkey, because PAC signature verification needs it.

## Dependencies And Integration Points

It depends on MIT Kerberos APIs, Samba Kerberos includes, and the common `gensec_krb5.h` declaration. `gensec_krb5.c` uses this function in server-side raw Kerberos authentication on MIT builds.

## Risks And Edge Cases

The comment notes a FIXME around using `ticket->enc_part.kvno`; the code passes `0` to get the latest kvno because this fixes a winbind PAC AD member test. That is a compatibility tradeoff and could matter in key rollover scenarios. Keytab lookup failures prevent PAC verification and abort authentication. Memory cleanup on each failure path is security and stability sensitive.

## Test Signals

MIT builds should test AP-REQ accept, AP-REP generation, PAC verification with the returned long-term key, key rollover/latest kvno behavior, missing keytab entries, wrong enctype/principal, and leak-free failure after ticket or keyblock allocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_mit.c -->
