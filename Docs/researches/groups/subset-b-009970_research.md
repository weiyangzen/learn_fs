# Research Group subset-b-009970

Grouped research for Samba Kerberos KDC, LDAP/CLDAP/LDB, and libnet torture sources. Each source section is delimited for reconciliation into the corresponding source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/kdc-heimdal.c -->
# sources/user-network-fs/samba/source4/torture/krb5/kdc-heimdal.c

## Purpose

`kdc-heimdal.c` implements Samba torture tests for Kerberos AS-REQ behavior when Samba is built against Heimdal. It validates client/KDC packet sequences, PAC request handling, bad password and clock-skew failures, enctype negotiation for AES/RC4, RODC KVNO expectations, canonicalization-required behavior, and the "Orpheus' Lyre" style server-name mutation cases.

## Important APIs, Types, and Functions

- `enum torture_krb5_test` selects the scenario under test, including plain AS-REQ, PAC request, bad password, clock skew, AES, RC4, AES+RC4, and server-name mutation in requests/replies.
- `struct torture_krb5_context` tracks the torture context, target KDC address, packet counter, decoded `AS_REQ`/`AS_REP`, and optional `krb5-service`/`krb5-hostname` settings.
- `torture_krb5_pre_send_test()` decodes outbound `AS_REQ` packets and optionally rewrites the service principal in the request.
- `torture_check_krb5_error()` decodes `KRB_ERROR`, checks error codes, and can require PA-DATA such as `KRB5_PADATA_ENC_TIMESTAMP` and `KRB5_PADATA_ETYPE_INFO2`.
- `torture_check_krb5_as_rep_enctype()` decodes `AS_REP`, validates ticket version/KVNO, infers the expected reply enctype from PA-ENC-TIMESTAMP or requested etype order, and compares against an allowed list.
- `torture_krb5_post_recv_test()` validates the KDC reply sequence for each test and can rewrite the server name in an incoming `AS_REP`.
- `test_krb5_send_to_realm_override()` is installed with `smb_krb5_set_send_to_kdc_func()` to force TCP to the selected host and inspect/mutate both directions.
- `torture_krb5_as_req_creds()` builds credentials/options and drives `krb5_get_init_creds_password()`.
- `torture_krb5_init()` registers the `krb5.kdc` torture tests and the Heimdal canonicalization sub-suite.

## Control Flow

Initialization reads the `host` torture setting, resolves it as a numeric address, forces port 88, initializes a Samba Heimdal context, and installs `test_krb5_send_to_realm_override()`. Every AS credential acquisition then routes through the override: pre-send decodes or mutates `AS_REQ`, the real network exchange goes through `smb_krb5_send_and_recv_func_forced_tcp()`, and post-receive validates or mutates the reply before Heimdal continues processing.

The plain and PAC flows expect initial preauth-required replies, possible response-too-big handling, and then a valid `AS_REP`. Bad password expects `KRB5KDC_ERR_PREAUTH_FAILED`; clock skew expects `KRB5KRB_AP_ERR_SKEW`. Enctype tests constrain the client etype list and verify the encrypted reply matches the selected allowed enctype. If `kdc require canonicalization` is enabled, these tests expect `KRB5KDC_ERR_C_PRINCIPAL_UNKNOWN` because the client did not request canonicalization.

Server-name mutation has two directions. Outbound mutation changes `req_body.sname` to the configured service/hostname before sending, expecting bad integrity when a hostname is supplied. Inbound mutation rewrites the returned ticket server name to `bad/mallory` before the krb5 library consumes it.

## State and Persistence Behavior

The file does not write persistent state. It holds transient decoded ASN.1 packets in `struct torture_krb5_context` and frees them after validation. The destructor frees the resolved KDC address. It can mutate in-flight packet buffers, but those changes exist only for the test exchange.

## Dependencies and Integration Points

The test depends on Heimdal ASN.1 types/functions (`AS_REQ`, `AS_REP`, `KRB_ERROR`, `decode_*`, `ASN1_MALLOC_ENCODE`), Samba Kerberos helpers (`smb_krb5_init_context`, `smb_krb5_set_send_to_kdc_func`, `principal_from_credentials`), credentials from `samba_cmdline_get_creds()`, loadparm KDC canonicalization settings, and socket/address utilities. It is built into the `TORTURE_KRB5` module by `wscript_build` only when Heimdal is selected.

## Risks and Edge Cases

Packet-count assumptions are fragile across Kerberos library behavior changes, TCP fallback behavior, KDC response-too-big paths, and RODC caching. Enctype inference deliberately skips AES unless canonicalization is present because salt selection matters. Packet mutation touches allocated ASN.1 fields directly; ownership mistakes can leak or corrupt test state. Tests using clock skew depend on krb5 time handling and server configuration.

## Test Signals

Passing signals are successful `smbtorture krb5.kdc` cases: `as-req-cmdline`, `as-req-pac-request`, `as-req-break-pw`, `as-req-clock-skew`, `as-req-aes`, `as-req-rc4`, `as-req-aes-rc4`, and `as-req-change-server-{in,out,both}`. Strong negative signals are wrong KDC error codes, missing preauth PA-DATA, missing KVNO, unexpected RODC high KVNO bits, incorrect enctype, or successful authentication after deliberate server-name tampering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/kdc-heimdal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/kdc-mit.c -->
# sources/user-network-fs/samba/source4/torture/krb5/kdc-mit.c

## Purpose

`kdc-mit.c` is the MIT Kerberos counterpart to the Heimdal KDC torture tests. It validates AS-REQ packet shape, KDC reply sequences, PAC request handling, password and clock failures, reply KVNO semantics, and AES/RC4 enctype selection using MIT krb5 hook APIs.

## Important APIs, Types, and Functions

- `enum torture_krb5_test` selects plain, PAC, bad-password, clock-skew, AES, RC4, and AES+RC4 scenarios.
- `struct torture_krb5_context` keeps the torture context, MIT `krb5_context`, receive packet count, and decoded `krb5_kdc_req`/`krb5_kdc_rep`.
- External decode/free prototypes wrap MIT private-ish decode helpers for `krb5_error`, AS request/reply, and PA-DATA sequences.
- `torture_check_krb5_as_req()` validates outbound AS-REQ message type and requested keytype count.
- `torture_krb5_pre_send_test()` is installed with `krb5_set_kdc_send_hook()`.
- `torture_krb5_post_recv_test()` is installed with `krb5_set_kdc_recv_hook()` and validates KDC replies.
- `torture_krb5_as_req_creds()` configures credentials, optional PAC request, broken password, clock skew, and etype lists before `krb5_get_init_creds_password()`.
- `torture_krb5_init()` registers the MIT variant and `torture_krb5_canon_mit()`.

## Control Flow

`torture_krb5_init_context()` initializes Samba's MIT krb5 context and attaches send/receive hooks. On send, every scenario decodes the AS request and verifies it is a real `KRB5_AS_REQ` with keytypes. On receive, the packet counter drives expected responses. Plain authentication expects preauth required followed by an AS-REP. PAC request can see response-too-big before preauth and later a final response. Bad password and clock-skew scenarios expect their specific KDC errors. Enctype tests require a preauth reply first and then validate `as_rep->enc_part.enctype`.

The main credential flow builds a principal from the supplied Samba credentials, optionally configures MIT `krb5_get_init_creds_opt`, executes `krb5_get_init_creds_password()`, and asserts success or expected failure. PAC request registration is compiled only when `HAVE_KRB5_GET_INIT_CREDS_OPT_SET_PAC_REQUEST` is available.

## State and Persistence Behavior

There is no persistent state. Decoded request/reply pointers are transient and freed in the receive hook. The test mutates client context time for the clock-skew case and frees krb5 credential contents after successful authentication.

## Dependencies and Integration Points

The file depends on MIT krb5 hook support (`krb5_set_kdc_send_hook`, `krb5_set_kdc_recv_hook`), MIT decode/free functions, Samba Kerberos context helpers, command-line credentials, torture assertions, and build-time feature macros. `wscript_build` selects this file when `SAMBA4_USES_HEIMDAL` is false.

## Risks and Edge Cases

MIT behavior differs from Heimdal in response ordering, hook semantics, PA-DATA decoding, and optional PAC request support. The clock-skew test requires `kdc_timesync 0` in krb5 configuration. The PAC test is skipped for expected RODC cases because Windows behavior for non-cached users needs more investigation. Enctype tests assume MIT chooses the specific expected enctype from the configured list.

## Test Signals

Primary signals are successful `krb5.kdc` MIT tests for command-line AS-REQ, PAC request when compiled, bad password, clock skew, AES, RC4, AES+RC4, and canonicalization subtests. Failures in decoded message type, missing keytypes, wrong KDC error, wrong KVNO high bits, or wrong `enc_part.enctype` indicate regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/kdc-mit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/wscript_build -->
# sources/user-network-fs/samba/source4/torture/krb5/wscript_build

## Purpose

`wscript_build` defines the `TORTURE_KRB5` smbtorture module for AD DC builds and selects the correct KDC test source set for Heimdal or MIT Kerberos.

## Important APIs, Types, and Functions

- `bld.CONFIG_SET('AD_DC_BUILD_IS_ENABLED')` gates the module to AD DC builds.
- `bld.CONFIG_SET('SAMBA4_USES_HEIMDAL')` selects Heimdal sources.
- `bld.SAMBA_MODULE('TORTURE_KRB5', ...)` declares the smbtorture module, `torture_krb5_init` init function, `proto.h` autoproto, and dependencies.

## Control Flow

At build configuration time, the script does nothing unless AD DC support is enabled. For Heimdal builds it compiles `kdc-heimdal.c` and `kdc-canon-heimdal.c`; otherwise it compiles `kdc-mit.c` and `kdc-canon-mit.c`. Both variants become an internal module under the `smbtorture` subsystem.

## State and Persistence Behavior

The script creates build graph state only. It does not affect runtime state or generated test data beyond autoproto output.

## Dependencies and Integration Points

The module depends on `authkrb5`, `torture`, and `KERBEROS_UTIL`. It integrates the C test registration entry point into smbtorture and controls which Kerberos provider-specific implementation is compiled.

## Risks and Edge Cases

Build selection must remain synchronized with provider-specific source APIs. Adding a new KDC test to one provider path but not the other can silently diverge test coverage. The non-Heimdal branch indentation is unusual but syntactically valid Python.

## Test Signals

Build success for both Heimdal and MIT configurations is the core signal. Runtime discovery of the `krb5` torture suite and successful execution of provider-specific canonicalization sub-suites confirms module wiring.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/basic.c -->
# sources/user-network-fs/samba/source4/torture/ldap/basic.c

## Purpose

`basic.c` implements low-level LDAP protocol torture tests against a Samba AD LDAP server. It validates RootDSE searches, substring filter behavior, simple and SASL bind behavior, compare operations, AD-style error message mappings, referral generation, and abandon request handling.

## Important APIs, Types, and Functions

- `test_bind_sasl()` wraps `torture_ldap_bind_sasl()` with command-line credentials.
- `test_multibind()` verifies anonymous bind followed by a simple authenticated bind on the same connection is rejected with `LDAP_STRONG_AUTH_REQUIRED`.
- `test_search_rootDSE()` sends a raw LDAP base-scope RootDSE search and extracts `defaultNamingContext` and `namingContexts`.
- `test_search_rootDSE_empty_substring()` and `test_search_auth_empty_substring()` force an empty substring filter on `objectclass`.
- `test_compare_sasl()` sends an LDAP compare request for `objectClass=domain`.
- `ad_error()` parses Windows hex error prefixes from LDAP error messages.
- `test_error_codes()` sends intentionally invalid add/modify/delete/modifyDN requests and checks LDAP result codes, AD WERRORs, and referrals.
- `test_referrals()` uses an LDB LDAP connection to verify base, onelevel, and subtree referral generation across naming contexts.
- `test_abandon_request()` sends an AbandonRequest for an old message id.
- `torture_ldap_basic()` orchestrates the full test.

## Control Flow

The test connects to `ldap://<host>/`, performs RootDSE discovery, then runs a sequence of independent protocol checks while accumulating `ret`. It first tests RootDSE and substring search handling, then binding rules, then authenticated search and compare. Error-code testing reuses one `ldap_message` object to submit malformed operations and validates both the LDAP result code and Samba's AD-compatible diagnostic text. Referral testing walks every non-root naming context and checks which parent partition searches should or should not emit referral URLs under base, onelevel, and subtree scopes. The connection is closed via a real UnbindRequest through `torture_ldap_close()`.

## State and Persistence Behavior

The test should not intentionally persist directory data. It sends malformed add/modify/delete/rename requests against protected or invalid DNs and expects failure. Referral and search checks are read-only. Connection authentication state changes during anonymous, simple, and SASL bind attempts.

## Dependencies and Integration Points

It uses Samba's raw LDAP client (`ldap_connection`, `ldap_message`, `ldap_request_send`, `ldap_result_one`), LDB LDAP wrapper for referral checks, command-line credentials, torture LDAP helpers from `common.c`, and LDAP/LDB result constants. It is registered as `ldap.basic` in `torture_ldap_init()`.

## Risks and Edge Cases

The expected AD diagnostic WERRORs allow some version-dependent alternatives, but changes in LDAP error text formatting can still break parsing. Referral checks depend on `namingContexts` ordering and URL formatting. The multi-bind expectation relies on server policy requiring stronger auth after anonymous bind. Reusing message objects across malformed operations requires every field to be reset carefully.

## Test Signals

Signals include successful RootDSE extraction, expected failure of second simple bind, successful SASL bind, successful compare request, exact LDAP result/WERROR pairs for malformed operations, required and forbidden referral URLs by scope, successful abandon wait, and clean unbind.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/cldap.c -->
# sources/user-network-fs/samba/source4/torture/ldap/cldap.c

## Purpose

`cldap.c` tests generic connectionless LDAP operations over UDP port 389. It verifies a Samba CLDAP server answers RootDSE searches with common attributes, netlogon attributes, and false filters without transport or protocol errors.

## Important APIs, Types, and Functions

- `ldap_msg_to_ldb()` converts an LDAP search entry to an `ldb_message` for LDIF dumping.
- `cldap_dump_results()` prints CLDAP results through LDB LDIF helpers when debug logging is high.
- `test_cldap_generic()` resolves the target host, creates a `cldap_socket`, and performs several `cldap_search()` calls.
- `torture_cldap()` runs the generic test for the configured `host`.

## Control Flow

The test resolves the NetBIOS server name to an IP, creates a `tsocket_address` for UDP 389, initializes a CLDAP socket, and sends searches for whole RootDSE, selected `currentTime`/`highestCommittedUSN`, those attributes plus `netlogon`, `netlogon` alone, and a false expression involving `highestCommittedUSN=2`. Each request expects `NT_STATUS_OK`; optional debug output dumps entries as LDIF.

## State and Persistence Behavior

The file is read-only and connectionless. All state is per-request search input/output and temporary LDB conversion state for printing.

## Dependencies and Integration Points

Dependencies include `libcli/cldap`, raw LDAP structures, NetBIOS name resolution, `tsocket`, LDB LDIF utilities, and torture LDAP registration. It is exposed as `ldap.cldap`.

## Risks and Edge Cases

False-filter behavior is only checked for transport success, not exact entry count. Result dumping steals LDAP attribute arrays into an LDB message for printing, so it is debug-path sensitive. Resolution failures or UDP filtering can fail the test before server logic is reached.

## Test Signals

The main signal is `NT_STATUS_OK` from every CLDAP search variant. Debug LDIF output can help confirm RootDSE and netlogon attributes are present and decodable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/cldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/cldapbench.c -->
# sources/user-network-fs/samba/source4/torture/ldap/cldapbench.c

## Purpose

`cldapbench.c` is a CLDAP benchmark torture test. It measures how quickly a target can answer parallel netlogon pings and RootDSE CLDAP searches over a configurable time window.

## Important APIs, Types, and Functions

- `struct bench_state` tracks pass/fail counters.
- `request_netlogon_handler()` receives asynchronous `netlogon_pings_send()` completions.
- `bench_cldap_netlogon()` maintains up to 10 outstanding netlogon ping requests and reports queries per second.
- `request_rootdse_handler()` receives asynchronous `cldap_search_send()` completions.
- `bench_cldap_rootdse()` runs the same windowed benchmark for RootDSE CLDAP searches.
- `torture_bench_cldap()` resolves the target and runs both benchmarks.

## Control Flow

The test resolves the configured host to an IP. Each benchmark records a start time and, until `torture:timelimit` expires, keeps no more than 10 requests outstanding. It drives completions with `tevent_loop_once()`, then drains remaining requests and prints pass-rate and failure count. Netlogon uses `netlogon_pings_send()` with `ntversion=6`; RootDSE uses `cldap_search_send()` with `(objectClass=*)`.

## State and Persistence Behavior

No directory state is changed. Runtime state is only outstanding tevent requests, counters, and the CLDAP socket for RootDSE.

## Dependencies and Integration Points

The benchmark depends on tevent, `netlogon_ping` helpers, CLDAP client APIs, name resolution, `tsocket`, loadparm `client netlogon ping protocol`, and torture settings `timelimit` and `progress`. It is registered as `ldap.bench-cldap`.

## Risks and Edge Cases

It is performance-oriented and not a strict correctness test; it always returns true even with failures counted. Network latency, UDP drops, resolver choice, and event loop behavior affect results. The fixed window of 10 outstanding requests may not stress all servers equally.

## Test Signals

Useful signals are the printed queries-per-second rate and failure count for netlogon and RootDSE. A sharp increase in failures or severe rate regression indicates CLDAP/server/network problems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/cldapbench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/common.c -->
# sources/user-network-fs/samba/source4/torture/ldap/common.c

## Purpose

`common.c` provides shared LDAP torture helpers and registers the LDAP/CLDAP torture suite. It centralizes connection setup, simple/SASL bind wrappers, orderly unbind, and suite membership.

## Important APIs, Types, and Functions

- `torture_ldap_bind()` wraps `ldap_bind_simple()`.
- `torture_ldap_bind_sasl()` wraps `ldap_bind_sasl()`.
- `torture_ldap_connection()` allocates `ldap4_new_connection()` and connects to a URL.
- `torture_ldap_close()` sends an LDAP UnbindRequest and frees the connection.
- `torture_ldap_init()` registers `bench-cldap`, `basic`, `sort`, `cldap`, `netlogon-udp`, `netlogon-tcp`, `netlogon-ping`, `schema`, `uptodatevector`, `nested-search`, and `session-expiry`.

## Control Flow

Helper calls are thin wrappers that print diagnostics on failure and return `NTSTATUS`. Close builds a raw LDAP UnbindRequest, sends it, waits for completion, and frees the connection. Suite initialization creates the `ldap` suite, adds all simple tests, sets the description, and registers it with smbtorture.

## State and Persistence Behavior

This file owns connection lifetime but no persistent server state. `torture_ldap_close()` consumes and frees the connection even on unbind allocation/send failures.

## Dependencies and Integration Points

It depends on the raw LDAP client, torture suite API, loadparm context, command/event context from `struct torture_context`, and prototypes generated for the LDAP torture files. All LDAP tests in this folder integrate through this registration point.

## Risks and Edge Cases

The wrappers expose raw status without retries. `torture_ldap_close()` frees the connection on several error paths, so callers must not use it after close failure. Suite registration must stay synchronized with available test functions and build declarations.

## Test Signals

Build/link success confirms the shared prototypes. Runtime `smbtorture --list` or execution of the `ldap` suite confirms all tests are registered, and individual helpers surface bind/connect/unbind failures as `NTSTATUS` diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/ldap_sort.c -->
# sources/user-network-fs/samba/source4/torture/ldap/ldap_sort.c

## Purpose

`ldap_sort.c` tests LDAP server-side sorting through LDB controls. It queries the `cn=users` subtree sorted by `cn` and validates returned entries are in case-insensitive ascending order with whitespace handling approximating Samba's sort behavior.

## Important APIs, Types, and Functions

- `torture_ldap_sort()` is the only test entry point.
- `ldb_wrap_connect()` creates an authenticated LDAP-backed LDB connection.
- `ldb_server_sort_control` defines the sort key, here `cn`, no ordering rule, not reversed.
- `ldb_build_search_req()`, `ldb_request_add_control()`, `ldb_request()`, and `ldb_wait()` drive the controlled search.

## Control Flow

The test connects to `ldap://<host>/`, builds a subtree search under default basedn plus `cn=users`, attaches a critical `LDB_CONTROL_SERVER_SORT_OID`, executes and waits for completion, then iterates results. For each entry it finds `cn`, prints it, and compares it to the previous value using `toupper_m()` while accounting for repeated leading/trailing spaces.

## State and Persistence Behavior

The test is read-only. Runtime state is the LDB request/result and previous/current `cn` values.

## Dependencies and Integration Points

It depends on LDB controls, LDAP-backed LDB connection setup, Samba UTF/case helpers, command-line credentials, and the LDAP suite registration in `common.c`.

## Risks and Edge Cases

The comparison is intentionally limited to ASCII-ish behavior and ad hoc whitespace handling, while the server may implement richer collation. It requires at least two results for ordering assertions. Missing `cn` attributes fail the test.

## Test Signals

Success means the server accepted the critical sort control, returned search results, every result had `cn`, and the local comparison did not detect descending order. Failures identify sort-control regressions or collation mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/ldap_sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/nested_search.c -->
# sources/user-network-fs/samba/source4/torture/ldap/nested_search.c

## Purpose

`nested_search.c` tests that Samba's LDAP-backed LDB layer can safely issue a nested search from within an outer search callback. It targets RootDSE and compares selected naming-context attributes from the nested result with the outer result.

## Important APIs, Types, and Functions

- `struct nested_search_context` holds the torture context, root DN, LDB context, and accumulated outer result.
- `nested_search_callback()` forwards replies through `ldb_search_default_callback()` and performs a nested RootDSE search on each entry.
- `test_ldap_nested_search()` builds and executes the outer RootDSE search.
- `torture_assert_res` maps assertion failures to LDB callback errors.

## Control Flow

The test connects to `ldap://<host>/`, creates a NULL RootDSE DN, and builds a base-scope search with callback context. The callback handles entry/done/referral replies, temporarily swaps the request context so the default callback stores the outer reply, then for entry replies runs another base-scope RootDSE search requesting root/config/schema/default naming context attributes. It asserts the nested result has one entry and that each nested element also exists in the outer stored message with matching flags and value counts.

## State and Persistence Behavior

The test is read-only. It stresses client-side request/callback state and context switching rather than server persistence.

## Dependencies and Integration Points

It uses LDB request/callback APIs, LDAP-backed `ldb_wrap_connect()`, command-line credentials, and the LDAP torture suite. The test is registered as `ldap.nested-search`.

## Risks and Edge Cases

The nested search assumes the outer result has already been stored before element comparison, which depends on default callback ordering. It compares flags and value counts but not full value contents. Callback error handling must avoid leaking or corrupting request context when nested operations fail.

## Test Signals

Passing requires the outer search to complete, the nested RootDSE search to succeed inside the entry callback, one nested entry to be returned, and requested naming-context attributes to match the outer message's structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/nested_search.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/netlogon.c -->
# sources/user-network-fs/samba/source4/torture/ldap/netlogon.c

## Purpose

`netlogon.c` tests LDAP and CLDAP netlogon ping behavior. It validates netlogon response semantics across NT version flags, user/domain/GUID/account-control inputs, server-type flags, extra RootDSE attributes with netlogon, no-`NtVer` compatibility, and both CLDAP and LDAP ping transports.

## Important APIs, Types, and Functions

- `struct cldap_netlogon` is the local request/response shape used by generic test functions.
- `request_netlogon_t` and `request_rootdse_t` abstract CLDAP/LDAP request backends.
- `test_ldap_netlogon()` exercises many netlogon filter combinations and expected response commands.
- `test_ldap_netlogon_flags()` prints decoded `server_type` flags.
- `tcp_ldap_rootdse()` maps a raw LDAP base search into `struct cldap_search`-style output.
- `udp_ldap_rootdse()` delegates to `cldap_search()`.
- `test_netlogon_extra_attrs()` verifies netlogon plus additional attributes and wildcard restrictions.
- `test_netlogon_huawei()` covers clients that omit `NtVer` and expects NT5 response.
- `test_netlogon_ping()` adapts `netlogon_pings()` to `struct cldap_netlogon`.
- `torture_netlogon_tcp()`, `torture_netlogon_udp()`, and `torture_netlogon_ping()` are suite entry points.

## Control Flow

The generic netlogon flow starts with a minimal request to learn baseline domain data, scans all 0-255 version values and individual version bits for successful responses, then asserts detailed behavior for null users, known/unknown users, NT5 versus NT5EX response commands, GUID-only searches, incorrect GUID/domain combinations, account-control variations, and field consistency against the baseline response.

TCP and UDP RootDSE tests use the same extra-attribute checks through backend adapters. TCP opens a raw LDAP connection and parses entry/done replies; UDP initializes a CLDAP socket. The ping test resolves the host to an IP, then runs the generic netlogon and flag tests twice through `netlogon_pings()`: once with `CLIENT_NETLOGON_PING_CLDAP` and once with `CLIENT_NETLOGON_PING_LDAP`.

## State and Persistence Behavior

The tests are read-only. They create transient LDAP/CLDAP sockets, parse netlogon blobs, and hold response pointers under request memory contexts.

## Dependencies and Integration Points

Dependencies include `libcli/cldap`, raw LDAP client structures, `ldap_ndr` helpers, `netlogon_ping`, NDR netlogon types, DNS/NetBIOS resolution, DOM SID/GUID parsing, `tsocket`, and loadparm DNS domain/client ping protocol settings. The entry points are registered in `common.c`.

## Risks and Edge Cases

The test encodes many Windows-compatible netlogon expectations, including UNC versus non-UNC PDC names, response command variants, wildcard filter rejection, and no-`NtVer` behavior. Small server-side compatibility changes can break strict assertions. Some status checks inspect output fields even after `NT_STATUS_NOT_FOUND`, so response initialization matters.

## Test Signals

Strong signals are correct status codes for valid and invalid domain/GUID inputs, expected `LOGON_SAM_LOGON_*` command values, stable forest/domain/PDC/site fields, correct extra-attribute behavior, `NETLOGON_NT_VERSION_5` for no-`NtVer`, and successful generic tests over both LDAP and CLDAP ping protocols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/schema.c -->
# sources/user-network-fs/samba/source4/torture/ldap/schema.c

## Purpose

`schema.c` tests reading AD schema data over LDAP and constructing Samba's in-memory `dsdb_schema`. It then reports attribute categories such as not replicated, partial attribute set, constructed, syntax-sorted, and not-in-filtered-replica.

## Important APIs, Types, and Functions

- `struct test_rootDSE` stores default, root, configuration, and schema naming contexts.
- `struct test_schema_ctx` tracks paged-search control state and per-entry callback data.
- `test_search_rootDSE()` discovers naming contexts.
- `test_schema_search_callback()` handles paged LDB replies and updates cookies.
- `test_create_schema_type()` performs paged subtree searches under the schema DN.
- `test_add_attribute()` and `test_add_class()` feed LDAP messages into `dsdb_set_attribute_from_ldb()` and `dsdb_set_class_from_ldb()`.
- `test_create_schema()` builds a `struct dsdb_schema`.
- Dump helpers iterate schema attributes and print categories.
- `torture_ldap_schema()` orchestrates connection, schema construction, and dumps.

## Control Flow

After connecting to `ldap://<host>/`, the test reads RootDSE naming contexts, allocates an empty `dsdb_schema`, and fetches all `attributeSchema` and `classSchema` objects with the critical paged-results control. The callback increments counts, invokes the supplied schema-population callback for entries, and copies returned page cookies until no pending page remains. Dump helpers then iterate the populated linked lists and print attributes matching system flag, partial set, syntax OID, and filtered-replica criteria.

## State and Persistence Behavior

The test is read-only against LDAP. It creates transient in-memory schema state under the LDB context and emits diagnostic output.

## Dependencies and Integration Points

It depends on LDAP-backed LDB, paged-results controls, Samba DSDB schema conversion helpers, RootDSE naming context attributes, and `dsdb_attribute_is_attr_in_filtered_replica()`. It is registered as `ldap.schema`.

## Risks and Edge Cases

Paged-search control handling is sensitive to cookie ownership and request reuse. Schema conversion assumes all required schema attributes are present and compatible with Samba's DSDB parsers. Dump output is diagnostic rather than strictly asserted, so missing categories may not fail unless schema creation fails.

## Test Signals

Primary pass signals are successful RootDSE discovery, successful paged retrieval of attributeSchema/classSchema objects, successful conversion into `dsdb_schema`, and no failures in category iteration. Counts printed for each filter provide regression evidence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/schema.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/session_expiry.c -->
# sources/user-network-fs/samba/source4/torture/ldap/session_expiry.c

## Purpose

`session_expiry.c` verifies that a Kerberos-authenticated LDAP session fails after a deliberately short requested GSSAPI ticket lifetime.

## Important APIs, Types, and Functions

- `torture_ldap_session_expiry()` is the single entry point.
- `cli_credentials_set_kerberos_state(... CRED_USE_KERBEROS_REQUIRED ...)` forces Kerberos authentication.
- `lpcfg_set_option("gensec_gssapi:requested_life_time=4")` requests a four-second lifetime.
- `ldb_wrap_connect()` opens the authenticated LDAP-backed LDB connection.
- Repeated `ldb_search()` calls test behavior until expiry.

## Control Flow

The test builds `ldap://<host>/`, forces Kerberos credentials, sets the GSSAPI requested lifetime to four seconds, connects, performs an initial RootDSE search, then loops once per second for up to ten seconds. It stops when a search fails and asserts the final error is `LDB_ERR_PROTOCOL_ERROR`.

## State and Persistence Behavior

The test is read-only. It mutates process/test credential and loadparm state by forcing Kerberos and setting a GSSAPI lifetime option. Runtime state is the LDAP session and repeated search result allocation.

## Dependencies and Integration Points

It depends on Samba credentials, GENSEC GSSAPI options, LDAP-backed LDB, event context, RootDSE search behavior, and the LDAP suite registration.

## Risks and Edge Cases

Timing-sensitive behavior can be affected by KDC ticket policy, server clock, client retries, and LDAP/GSSAPI error mapping. The test expects protocol error after expiry, so changes to LDB's error translation can break it even if expiry still works.

## Test Signals

The expected signal is an initial successful RootDSE search, followed within ten seconds by `LDB_ERR_PROTOCOL_ERROR`. Continued success beyond the deadline or a different error indicates a regression or environment mismatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/session_expiry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/uptodatevector.c -->
# sources/user-network-fs/samba/source4/torture/ldap/uptodatevector.c

## Purpose

`uptodatevector.c` tests that local modifications to partition root metadata do not unexpectedly change `replUpToDateVector`. It covers default, configuration, and schema naming contexts.

## Important APIs, Types, and Functions

- `test_check_uptodatevector()` reads a partition root, decodes `replUpToDateVector`, modifies `description` twice, rereads the vector, and compares raw blob stability.
- `ndr_pull_replUpToDateVectorBlob()` decodes the vector for validation/debug printing.
- `torture_ldap_uptodatevector()` connects and runs the check for three partition roots.

## Control Flow

For each partition DN, the helper searches base-scope for `uSNChanged`, `replUpToDateVector`, and `description`, decodes the current vector if present, then performs two `ldb_modify()` calls replacing `description`. After each modify it rereads the same attributes, decodes the vector, compares presence, length, and bytes against the original, prints status, and marks failure if the vector changed.

## State and Persistence Behavior

This test intentionally modifies the `description` attribute on partition root objects. It does not restore the previous description. It expects `uSNChanged` and description to change while `replUpToDateVector` remains stable.

## Dependencies and Integration Points

It depends on LDAP-backed LDB, command-line credentials with write access, DSDB partition base DN helpers, NDR DRS blob decoding, and the LDAP suite registration.

## Risks and Edge Cases

Because it writes partition root descriptions and does not restore them, it can leave visible test values. Required permissions are higher than read-only LDAP tests. Vector absence/presence and raw byte ordering must remain stable across expected local metadata updates.

## Test Signals

Success is printed as `replUpToDateVector[not changed: ok]` for both modifications on all three partitions. Any decoded vector change, decode error, search count mismatch, or modify failure is a regression signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldap/uptodatevector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldb/ldb.c -->
# sources/user-network-fs/samba/source4/torture/ldb/ldb.c

## Purpose

`ldb.c` is a local smbtorture suite for Samba-specific LDB behavior. It tests Samba LDIF syntax handlers, extended DN syntax, DN comparison/validation, binary pack/unpack formats, corrupt unpack handling, LDIF round trips, attribute filtering, and a pack/unpack performance smoke test.

## Important APIs, Types, and Functions

- Static fixtures define SID/GUID/prefixMap strings and binary/LDIF representations of a real directory record.
- `torture_ldb_attrs()` validates `objectSid`, `objectGUID`, and `prefixMap` LDIF read/write/compare handlers.
- `torture_ldb_dn_attrs()` validates extended DN syntax handlers for SID and GUID in clear and hex forms.
- `torture_ldb_dn_extended()` validates parsing, serialization, component removal, and setting of extended GUID/SID components.
- `torture_ldb_dn()` validates normal DN construction/comparison, special DN comparisons, and invalid control characters.
- `torture_ldb_dn_invalid_extended()` validates malformed extended DN rejection.
- `helper_ldb_message_compare()` compares unpacked/parsed messages while skipping known SDDL round-trip differences.
- `torture_ldb_unpack()`, `torture_ldb_unpack_flags()`, `torture_ldb_parse_ldif()`, and `torture_ldb_unpack_and_filter()` validate binary record formats against LDIF.
- `torture_ldb_unpack_data_corrupt()` mutates selected bytes and checks expected unpack success/failure.
- `torture_ldb_pack_data_v2()` and `torture_ldb_pack_data_v2_special()` assert exact v2 packing bytes.
- `torture_ldb_pack_format_perf()` times repeated pack/unpack operations on a large member list.
- `torture_ldb()` registers the local `ldb` suite.

## Control Flow

Most tests initialize a local Samba LDB context with Samba handlers and UTF8 comparison functions, then exercise one API family with fixed fixtures. The binary-format tests use two known packed records, unpack them into `ldb_message`, serialize to LDIF, parse LDIF back, and compare memory forms. The corrupt-data test walks byte ranges classified as corruptible or tolerated, flips bytes, and checks `ldb_unpack_data()` return codes. Suite registration adds simple tests and data-driven cases for both v1 and v2 binary fixtures.

## State and Persistence Behavior

The suite is local and in-memory. It does not connect to LDAP or persist database files. It allocates temporary LDB contexts/messages and frees them through talloc lifetimes. The performance test constructs a large transient LDIF with 10,000 `member` values.

## Dependencies and Integration Points

It depends on LDB core, Samba LDB wrappers, Samba LDIF handlers, DSDB/SAMDB initialization helpers, security descriptor LDIF formatting, UTF8 casefold functions, and the local torture suite registration path. It exercises behavior used by SAMDB storage and replication code.

## Risks and Edge Cases

Exact byte-layout tests are intentionally brittle across LDB packing format changes. `nTSecurityDescriptor` is skipped in deep compare due to known SDDL type-bit differences. DN validation around newlines is currently warning-only for one case. PrefixMap, SID, GUID, and extended DN syntax changes can break many Samba database consumers.

## Test Signals

Signals include successful syntax round trips, rejection of malformed extended DNs, exact packed bytes for v2 records, expected corrupt-byte return codes, LDIF equality for fixture unpacking, reduced LDIF equality after filtering, and successful registration of all v1/v2 data-driven cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ldb/ldb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/domain.c -->
# sources/user-network-fs/samba/source4/torture/libnet/domain.c

## Purpose

`domain.c` tests the libnet convenience API for opening a SAMR domain handle and then closing it through raw SAMR.

## Important APIs, Types, and Functions

- `test_domainopen()` prepares `struct libnet_DomainOpen` with the workgroup domain name and `SEC_FLAG_MAXIMUM_ALLOWED`.
- `test_cleanup()` closes the returned domain handle with `dcerpc_samr_Close_r()`.
- `torture_domainopen()` initializes a libnet context, connects to SAMR, and runs open/close.

## Control Flow

The test creates a memory context and libnet context, opens an RPC connection to the SAMR interface, uses `lpcfg_workgroup()` as the domain name, calls `libnet_DomainOpen()`, stores the returned handle, and closes it via SAMR.

## State and Persistence Behavior

No persistent domain state is changed. The only server-side state is a transient SAMR policy handle, which the test closes.

## Dependencies and Integration Points

It depends on `libnet_context_init()`, `libnet_DomainOpen()`, SAMR NDR client bindings, `torture_rpc_connection()`, and loadparm workgroup configuration. It is registered as `net.domopen` by `libnet.c`.

## Risks and Edge Cases

The test assumes the configured workgroup names a SAMR domain reachable over the torture RPC connection. Failure to close handles would leak server resources until connection teardown. Access mask or domain name behavior changes in libnet can break the test.

## Test Signals

Success is `NT_STATUS_OK` for the SAMR connection, libnet domain open, and SAMR close result. Diagnostics identify domain-open or close failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/groupinfo.c -->
# sources/user-network-fs/samba/source4/torture/libnet/groupinfo.c

## Purpose

`groupinfo.c` tests `libnet_rpc_groupinfo()` by creating a temporary SAMR group, querying it by SID and by group name, and cleaning it up.

## Important APIs, Types, and Functions

- `TEST_GROUPNAME` is `libnetgroupinfotest`.
- `test_groupinfo()` builds a group SID from the domain SID and RID, then queries level 5 by SID and by name.
- `torture_groupinfo()` connects to SAMR, opens the domain, creates the test group, runs the groupinfo checks, and deletes the group.
- Shared helpers `test_domain_open()`, `test_group_create()`, and `test_group_cleanup()` come from other libnet torture support.

## Control Flow

After a SAMR RPC connection, the test opens the configured workgroup domain, creates the temporary group and captures its RID, calls `libnet_rpc_groupinfo()` with the SID string, resets the request, calls it again with `groupname`, then cleans up the group and frees memory.

## State and Persistence Behavior

The test creates and deletes a SAMR group. If it fails before cleanup, the group named `libnetgroupinfotest` may remain in the domain.

## Dependencies and Integration Points

It depends on SAMR RPC, libnet groupinfo API, domain SID manipulation (`dom_sid_add_rid`, `dom_sid_string`), loadparm workgroup, and shared group test helpers. It is registered as `net.groupinfo`.

## Risks and Edge Cases

Cleanup is skipped if earlier setup fails before reaching the cleanup call. Level 5 is hard-coded and noted as needing extension. Existing groups with the same name can collide with the test.

## Test Signals

Passing requires domain open, group create, groupinfo by SID, groupinfo by name, and cleanup all to return `NT_STATUS_OK` or true from helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/groupinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/groupman.c -->
# sources/user-network-fs/samba/source4/torture/libnet/groupman.c

## Purpose

`groupman.c` tests the libnet RPC group-add convenience function against SAMR and verifies cleanup through shared helpers.

## Important APIs, Types, and Functions

- `test_groupadd()` calls `libnet_rpc_groupadd()` with a domain handle and group name.
- `torture_groupadd()` connects to SAMR, opens the domain, adds `TEST_GROUPNAME`, and cleans it up.
- `TEST_GROUPNAME` comes from `grouptest.h` as `libnetgrptest`.

## Control Flow

The test opens a SAMR RPC connection, opens the configured workgroup domain through shared helper code, calls the libnet group-add wrapper, and deletes the group with `test_group_cleanup()` before freeing the memory context.

## State and Persistence Behavior

It creates and deletes one SAMR group. A failure after creation but before cleanup can leave `libnetgrptest` in the directory.

## Dependencies and Integration Points

Dependencies include SAMR RPC bindings, `libnet_rpc_groupadd()`, shared domain/group helper prototypes, loadparm workgroup, and the `net.groupadd` suite registration in `libnet.c`.

## Risks and Edge Cases

Name collisions with existing `libnetgrptest` groups can fail creation or cleanup. The test only verifies the add call succeeds, not group attributes beyond existence. Cleanup must be reliable to avoid persistent test artifacts.

## Test Signals

Passing signals are successful RPC connection, domain open, `libnet_rpc_groupadd()` status, and group cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/groupman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/grouptest.h -->
# sources/user-network-fs/samba/source4/torture/libnet/grouptest.h

## Purpose

`grouptest.h` defines the shared group name used by libnet group management tests.

## Important APIs, Types, and Functions

- `TEST_GROUPNAME` is defined as `libnetgrptest`.

## Control Flow

There is no control flow. Including files use the macro when creating and cleaning up temporary groups.

## State and Persistence Behavior

The header does not manage state. Its macro names a persistent directory object that tests may create and delete.

## Dependencies and Integration Points

It is included by `groupman.c` and can be used by other libnet group tests needing a common temporary group name.

## Risks and Edge Cases

Because this is a global test object name, concurrent tests or stale objects can collide. Changing the macro affects cleanup expectations across including tests.

## Test Signals

Build success confirms macro visibility. Runtime signals appear in group creation/cleanup tests that use this name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/grouptest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet.c -->
# sources/user-network-fs/samba/source4/torture/libnet/libnet.c

## Purpose

`libnet.c` registers the smbtorture suite for Samba's libnet convenience interface tests.

## Important APIs, Types, and Functions

- `torture_net_init()` creates the `net` suite, adds simple tests, sets a description, registers the suite, and returns `NT_STATUS_OK`.
- Registered tests cover user management, domain open/close, group management, lookup APIs, RPC connection APIs, share APIs, LSA/SAMR domain operations, BecomeDC, and domain listing.

## Control Flow

Suite initialization is linear: create `net`, add each test by name and function pointer, assign the description, call `torture_register_suite()`, and return success.

## State and Persistence Behavior

The file itself has no persistent state. It exposes tests that may create users, groups, shares, joins, or replicated databases depending on the selected case.

## Dependencies and Integration Points

It depends on smbtorture suite APIs, DCERPC/libnet headers, generated LSA types, and generated prototypes for all libnet torture entry points. It is the integration point that makes the files in this folder runnable.

## Risks and Edge Cases

Registration names are public test selectors, so renames can break automation. The file must remain synchronized with available functions and build inclusion. It mixes destructive and read-only tests under one suite, so callers must select carefully.

## Test Signals

`smbtorture --list` should show `net.*` entries. Link failures catch missing prototypes/functions, while running individual tests validates each registered API path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_BecomeDC.c -->
# sources/user-network-fs/samba/source4/torture/libnet/libnet_BecomeDC.c

## Purpose

`libnet_BecomeDC.c` tests the libnet BecomeDC workflow. It joins a machine account as a workstation, runs the vampire replication callbacks to build a local private database, marks the replicated RootDSE synchronized, commits, reopens the SAM database with system credentials, verifies schema loading, and then optionally un-becomes/unjoins.

## Important APIs, Types, and Functions

- `torture_net_become_dc()` is the test entry point.
- `torture_temp_dir()` creates an isolated target directory.
- `torture_join_domain()` creates a temporary workstation trust account and returns `struct test_join`.
- `libnet_vampire_cb_state_init()` prepares callback state and local database paths.
- `libnet_BecomeDC()` performs the replication workflow using callbacks `check_options`, `prepare_db`, `schema_chunk`, `config_chunk`, and `domain_chunk`.
- `libnet_vampire_cb_ldb()` and `libnet_vampire_cb_lp_ctx()` expose the replicated LDB and loadparm context.
- `samdb_connect()`, `dsdb_uses_global_schema()`, and `dsdb_get_schema()` verify the resulting database.
- `libnet_UnbecomeDC()` and `torture_leave_domain()` perform cleanup unless disabled by a torture option.

## Control Flow

The test creates a temp directory, chooses a destination DC NetBIOS name from `become dc:smbtorture dc` or defaults to `smbtorturedc`, resolves the source DC host, and joins the domain as a workstation trust account. It initializes vampire callback state with the joined domain names and output location, creates a libnet context using command-line credentials, fills `libnet_BecomeDC` input domain/source/destination fields, and runs BecomeDC.

After successful replication, it modifies `@ROOTDSE` to set `isSynchronized=TRUE`, commits the LDB transaction, detaches and reopens `sam.ldb` from the generated private directory as system, asserts the reopened DB does not use the global schema, and fetches a loaded `dsdb_schema`. Cleanup calls `libnet_UnbecomeDC()`, leaves the domain, and frees callback state unless `become dc:do not unjoin` is set.

## State and Persistence Behavior

This is a stateful integration test. It creates a temporary machine account in the domain, writes replicated database and secrets under a temp private directory, modifies local `@ROOTDSE`, commits an LDB transaction, and normally unjoins/removes the machine account. If `do not unjoin` is enabled or a failure interrupts cleanup, domain and filesystem artifacts may remain.

## Dependencies and Integration Points

It integrates libnet join, BecomeDC/UnbecomeDC, DRSUAPI/DRS blob structures, vampire callbacks, SAMDB/DSDB schema loading, auth system session, loadparm private-dir override, name resolution, and torture RPC/join helpers. It is registered as `net.api.become.dc`.

## Risks and Edge Cases

The test has a large blast radius: network resolution, domain join rights, replication permissions, local private directory setup, transaction commit, schema load, and cleanup all must work. Cleanup assertions run even after failures, so missing context from early setup can complicate failure handling. The `do not unjoin` option intentionally leaves state behind for debugging.

## Test Signals

Strong success signals are successful name resolution, workstation join, `libnet_BecomeDC()`, RootDSE modification, transaction commit, reopened `sam.ldb`, `dsdb_uses_global_schema()` returning false, non-null `dsdb_schema`, successful `libnet_UnbecomeDC()`, and successful domain leave.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_BecomeDC.c -->
