# subset-b-009987 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/remote_pac.c -->
# sources/user-network-fs/samba/source4/torture/rpc/remote_pac.c

## Purpose
This file implements the `rpc.pac` torture sub-suite for remote Kerberos PAC validation through NETLOGON. It verifies that Samba can obtain a PAC through GENSEC/GSSAPI, parse the PAC into session information, validate PAC signatures through `netr_LogonSamLogon` generic information, reject tampered PAC payloads predictably, and preserve user/group details across normal Kerberos, S4U2Self, S4U2Proxy, and SamLogon flows. The tests cover both BDC and workstation secure-channel machine accounts and vary ARCFOUR, AES, and Kerberos-authenticated Netlogon setup paths.

## Important APIs, types, and functions
The local `struct pac_data` holds the raw `DATA_BLOB` PAC plus extracted server and KDC `PAC_SIGNATURE_DATA`. `test_generate_session_info_pac()` is a replacement `auth4_context.generate_session_info_pac` hook: it avoids local SAM token expansion, decodes `kerberos_pac_blob_to_user_info_dc()`, stores signatures in `auth_ctx->private_data`, and calls `auth_generate_session_info()`. `get_pac_buffer()` locates a PAC buffer by `PAC_TYPE`.

`test_PACVerify()` drives a GENSEC GSSAPI client/server exchange, extracts the PAC, checks mandatory PAC buffers such as logon info, logon name, UPN/DNS info, SRV/KDC/ticket/full checksums, and optional PKINIT credential info, then delegates to `netlogon_validate_pac()`. `netlogon_validate_pac()` builds `PAC_Validate`, sends it as `NetlogonGenericInformation`, and checks success plus negative cases for broken signature bytes, malformed length, wrong signature type, and wrong signature length.

Under `SAMBA4_USES_HEIMDAL`, `test_S4U2Self()` compares session info from kinit, S4U2Self, and SamLogon; `check_primary_group_in_validation()` validates the primary group RID is present in Netlogon validation groups. `test_S4U2Proxy()` checks constrained-delegation PAC buffers and `PAC_CONSTRAINED_DELEGATION` contents. `setup_constrained_delegation()` uses LDAP and SAMR to set `msDS-AllowedToDelegateTo` and `ACB_TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`.

## Control flow
The suite factory `torture_rpc_remote_pac()` registers machine-join RPC test cases against `ndr_table_netlogon`. For each secure-channel variant it uses the RPC harness to create a temporary BDC or workstation account, connect to Netlogon, and pass the machine credentials into the PAC test function.

`test_PACVerify()` shallow-copies user and server credentials to isolate Kerberos memory ccaches, optionally loads `pkinit_ccache`, starts GENSEC client and server contexts with GSSAPI, and loops `gensec_update()` until authentication completes. It calls `gensec_session_info()` to trigger the custom PAC hook, parses the PAC with `ndr_pull_PAC_DATA`, validates expected buffer count and buffer presence, then calls `netlogon_validate_pac()`.

`netlogon_validate_pac()` either reconnects using `DCERPC_SCHANNEL | DCERPC_SCHANNEL_KRB5` when `NETLOGON_NEG_SUPPORTS_KERBEROS_AUTH` is requested or negotiates a normal Netlogon credential chain with `test_SetupCredentials2()` and `test_SetupCredentialsPipe()`. It NDR-encodes a `PAC_Validate` containing the server checksum and KDC signature, encrypts SamLogon payloads when appropriate, verifies `NT_STATUS_OK` for the intact PAC, then mutates the payload in controlled ways and asserts `NT_STATUS_LOGON_FAILURE` or `NT_STATUS_INVALID_PARAMETER` while checking credential chaining after each call.

The S4U2Self path performs three independent validations: a normal Kerberos GENSEC exchange, a GENSEC exchange using server credentials with `cli_credentials_set_impersonate_principal()`, and a Netlogon network SamLogon using NTLMv2 response material. It then compares account names, full names, domain SIDs, attributes, primary group presence, and asserted-identity/claims-valid SID behavior. S4U2Proxy prepares impersonation plus a distinct target service, performs a GENSEC exchange, validates a nine-buffer PAC including client claims and constrained delegation, then reuses Netlogon PAC validation.

## State and persistence
The file does not persist local state. Runtime state lives in talloc trees, temporary memory Kerberos ccaches, `auth_ctx->private_data`, Netlogon credential chains, and temporary domain machine accounts created by the harness. S4U2Proxy mutates directory state for the temporary machine account by writing `msDS-AllowedToDelegateTo` over LDAP and setting SAMR account flags; the test-join teardown owns cleanup. Settings that affect behavior include `pkinit_ccache` and `expect_pac_upn_dns_info`.

## Dependencies and integration points
This test depends on Samba auth, credentials, GENSEC, Kerberos/PAC parsing, Netlogon RPC, SAMR RPC, LDAP/SAMDB, and the torture RPC join helpers. It integrates with `rpc.c` through `torture_suite_add_machine_bdc_rpc_iface_tcase()`, `torture_suite_add_machine_workstation_rpc_iface_tcase()`, `torture_rpc_tcase_add_test_creds()`, and `torture_rpc_tcase_add_test_join()`. It is registered into the global `rpc` suite by `torture_rpc_init()` in `rpc.c`.

## Risks
The tests are security-sensitive and compatibility-sensitive. Expected PAC buffer counts can change when KDC PAC contents evolve; the file partially gates this through `expect_pac_upn_dns_info` and PKINIT handling. Netlogon PAC validation still asserts ARCFOUR support for `PACValidate`, so negotiation changes can make AES/Kerberos cases fail before semantic validation. The S4U tests are compiled only with Heimdal support and assume constrained-delegation LDAP/SAMR mutations are permitted. Many assertions depend on exact SID ordering with special skips for asserted identity and claims-valid SIDs, so changes in PAC SID ordering may require corresponding test changes.

## Test signals
Strong pass signals are successful GENSEC handshakes, parsed PAC version `0`, expected PAC buffer counts, non-null checksum/signature buffers, `NetlogonGenericInformation` success for the intact PAC, and expected failure statuses for tampered payloads. S4U2Self additionally signals correctness through matching names, group SIDs, attributes, primary group inclusion, and expected authority/service asserted identity plus `SID_CLAIMS_VALID` counts. S4U2Proxy signals correctness by finding `PAC_TYPE_CONSTRAINED_DELEGATION`, expected proxy target, and one transited service before successful Netlogon PAC validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/remote_pac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/rpc.c -->
# sources/user-network-fs/samba/source4/torture/rpc/rpc.c

## Purpose
This file is the central DCE/RPC torture harness and registry for Samba's `rpc` suite. It turns the user-supplied `binding` torture setting into connected `dcerpc_pipe` objects, provides standard RPC test-case setup/teardown variants, wraps RPC test callbacks into the generic torture framework, supports temporary workstation and BDC domain joins for machine-account tests, and registers all RPC sub-suites and simple tests.

## Important APIs, types, and functions
`torture_rpc_binding()` parses the `binding` setting into a `dcerpc_binding`. `torture_rpc_connection()` and `torture_rpc_connection_with_binding()` initialize DCE/RPC support and connect to a generated NDR interface with command-line credentials. `torture_rpc_connection_transport()` adjusts transport, association group, and extra binding flags before connecting.

Setup helpers include `torture_rpc_setup()`, `torture_rpc_setup_anonymous()`, `torture_rpc_setup_machine_workstation()`, and `torture_rpc_setup_machine_bdc()`. They populate `struct torture_rpc_tcase_data` with credentials, joined machine context where needed, and a connected pipe. `torture_rpc_teardown()` leaves any joined domain and frees case data.

Test registration helpers include `torture_suite_init_rpc_tcase()`, `torture_suite_add_rpc_iface_tcase()`, `torture_suite_add_anon_rpc_iface_tcase()`, `torture_suite_add_machine_workstation_rpc_iface_tcase()`, `torture_suite_add_machine_bdc_rpc_iface_tcase()`, `torture_rpc_tcase_add_test()`, `torture_rpc_tcase_add_test_creds()`, `torture_rpc_tcase_add_test_join()`, `torture_rpc_tcase_add_test_ex()`, `torture_rpc_tcase_add_test_setup()`, and `torture_suite_add_rpc_setup_tcase()`.

## Control flow
Generic RPC cases start by parsing the binding string, connecting to the target NDR table with `samba_cmdline_get_creds()`, and storing the pipe in case data. Anonymous cases use `cli_credentials_init_anon()`. Machine-account cases call `torture_join_domain()` with `ACB_WSTRUST` or `ACB_SVRTRUST`, update the credential pointer with joined machine credentials, then connect using those credentials. Teardown reverses joined-machine setup through `torture_leave_domain()`.

Each `torture_rpc_tcase_add_*` function allocates a `struct torture_test`, records the real callback in `test->fn`, selects an adapter such as `torture_rpc_wrap_test_creds()`, and appends it to the case list with `DLIST_ADD_END()`. The adapters recover the active `torture_rpc_tcase_data`, then call the typed callback with the pipe plus optional credentials, join context, userdata, or per-test setup/teardown data.

`torture_rpc_init()` creates the top-level `rpc` suite, calls `ndr_table_init()`, adds many simple and nested tests for LSA, SAMR, Netlogon, PAC, SRVSVC, SPOOLSS, WINREG, DRSUAPI, SMB/RPC bind edge cases, and other interfaces, sets the suite description, and registers it with `torture_register_suite()`.

## State and persistence
The harness maintains per-test-case state only for the duration of the case: connected pipe, credential pointer, and optional `test_join` context. It mutates the target domain when machine-account cases join temporary workstation or BDC accounts, and teardown is responsible for cleanup. The local process stores no durable data. The `binding` torture setting is mandatory for most RPC tests.

## Dependencies and integration points
This file is the integration point between the generic torture framework, Samba command-line credentials, DCE/RPC binding/pipe APIs, NDR interface tables, and domain-join helpers. It exposes public helper functions used by many files in `source4/torture/rpc/`, including `remote_pac.c` and the Samba3 suite. It depends on `torture/rpc/torture_rpc.h` for shared structs and prototypes and on generated NDR table symbols for each registered RPC interface.

## Risks
Because this file centralizes setup, connection, and wrapper behavior, changes can affect many RPC torture tests at once. Failure to parse the binding setting cleanly prevents broad suite execution. Machine-account setup uses real domain joins, so missing teardown can leave temporary accounts. The wrapper functions rely on callback signatures matching the selected add helper; a mismatched cast compiles through `void *` storage patterns but fails at runtime. `torture_rpc_wrap_test_setup()` does not call its teardown callback if the test function itself fails, so custom setup tests must be careful about externally persistent state.

## Test signals
Primary signals are successful binding parsing, `dcerpc_pipe_connect_b()` success, correct test callback invocation, and clean teardown of joined machine accounts. At suite level, the signal is that `torture_rpc_init()` registers `rpc` and includes expected nested suites such as `netlogon`, `remote_pac`, `samba3`, DRSUAPI, SRVSVC, SPOOLSS, WINREG, and bind/auth tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samba3rpc.c -->
# sources/user-network-fs/samba/source4/torture/rpc/samba3rpc.c

## Purpose
This file implements the `rpc.samba3` torture sub-suite, a broad compatibility test bed for Samba3-style DCE/RPC over SMB named pipes. It exercises RPC binding over SMB1 and SMB2 IPC$, auth context behavior, SAMR account creation and machine join flows, Netlogon secure-channel operations, share enumeration/security, LSA identity lookup, spoolss, wkssvc, winreg-backed configuration, SMB reauthentication with open RPC pipes, pipe-name syntax, pending pipe reads, and pipe/interface restrictions.

## Important APIs, types, and functions
Named-pipe helpers are `pipe_bind_smb()`, `pipe_bind_smb2()`, and `pipe_bind_smb_auth()`, which open a DCE/RPC pipe over an existing SMB1 or SMB2 tree and bind either anonymously or with explicit auth type/level. Auth and join helpers include `get_usr_handle()`, `create_user()`, `delete_user()`, `join3()`, `auth2()`, `schan()`, `leave()`, `test_join3()`, and `torture_samba3_sessionkey()`.

Identity and share helpers include `name2sid()`, `whoami()`, `secondary_tcon()`, `get_sharesec()`, `set_sharesec()`, and exported `try_tcon()`. Service-specific tests include `torture_samba3_rpc_srvsvc()`, `torture_samba3_rpc_lsa()`, `torture_samba3_rpc_spoolss()`, `torture_samba3_rpc_wkssvc()`, `torture_samba3_rpc_winreg()`, `torture_samba3_regconfig()`, and `torture_samba3_getaliasmembership_0()`.

Transport and pipe edge cases are covered by `torture_bind_authcontext()`, `torture_bind_samba3()`, `torture_samba3_rpc_randomauth2()`, `torture_rpc_smb_reauth1()`, `torture_rpc_smb_reauth2()`, `torture_rpc_smb2_reauth1()`, `torture_rpc_smb2_reauth2()`, `torture_rpc_smb1_pipe_name()`, `torture_rpc_smb2_pipe_name()`, `torture_rpc_smb2_pipe_read_close()`, `torture_rpc_smb2_pipe_read_tdis()`, `torture_rpc_smb2_pipe_read_logoff()`, `torture_rpc_lsa_over_netlogon()`, and `torture_rpc_pipes_supported_interfaces()`.

## Control flow
The suite factory `torture_rpc_samba3()` registers simple tests under the `samba3` nested suite. Most tests first establish an SMB connection to `IPC$` using `torture_setting_string(..., "host")`, command-line credentials or test credentials, and local SMB client options/session options. They then open named pipes via `pipe_bind_*()` and make generated RPC calls through the resulting binding handle.

Auth-binding coverage opens LSA over SMB and performs `OpenPolicy2`, `QueryInfoPolicy`, and `Close` with NTLMSSP and SPNEGO at integrity and privacy levels. `torture_bind_authcontext()` intentionally swaps an SMB1 tree's session VUID to an anonymous session after an LSA bind and expects the RPC connection to disconnect while the underlying SMB transport remains alive.

SAMR/Netlogon coverage creates or opens accounts with `samr_Connect2`, `EnumDomains`, `LookupDomain`, `OpenDomain`, `CreateUser2` or `OpenUser`, then sets passwords and account flags through encrypted SAMR password buffers. `join3()` models Samba3 machine join behavior at info levels 24 or 25 and verifies `last_password_change` semantics. `auth2()` performs Netlogon challenge/authenticate and stores negotiated credential state in the workstation credentials. `schan()` binds Netlogon with SCHANNEL privacy, performs network and interactive SamLogon, verifies credential chaining, and changes the workstation password.

Share and identity coverage checks anonymous and authenticated `lsa_GetUserName`, creates a temporary normal user, maps the returned name back to a SID, and compares it to the SAMR-created SID. SRVSVC tests enumerate shares at multiple info levels and queries one share at levels 0, 1, 2, 501, 502, 1004, 1005, 1006, 1007, and 1501. Share-security tests create a low-privilege user, grant `SeDiskOperatorPrivilege`, read and rewrite share security descriptors through SRVSVC, and verify tree-connect and mkdir results for zero, read-only, and full access masks.

Spoolss tests find print shares through SRVSVC, get the server name through RAP, open the server and first printer through SPOOLSS, read printer info levels, and compare printer counts from SPOOLSS and SRVSVC. WKSSVC compares `NetWkstaGetInfo` server name against RAP. WINREG recursively enumerates HKLM keys and values; regconfig creates a Samba registry share key, sets a `comment` value, verifies SRVSVC sees it, then deletes the key.

Reauthentication tests keep an LSA pipe open across SMB1 or SMB2 session setup changes to anonymous and back to the original user, asserting that the bound RPC context identity remains stable. Pipe-name tests assert exact SMB1 and SMB2 named-pipe path acceptance/rejection rules. Pending-read tests issue an async SMB2 read against `lsarpc`, then close the handle, tree-disconnect, or log off and require `NT_STATUS_PIPE_BROKEN`. The final interface tests verify LSA over the Netlogon pipe remains possible and that inappropriate NDR interfaces cannot bind on unrelated SMB pipe names.

## State and persistence
The file mutates remote server state heavily but intends to clean it up. It creates and deletes users such as `sharesec_user` and `torture_username`, creates workstation machine accounts using `wksname`, changes workstation passwords during Netlogon SCHANNEL tests, grants privileges, adjusts share security descriptors, creates/removes registry-backed share configuration under `software\samba\smbconf\blubber`, and creates/removes `sharesec_testdir` on test shares. Local state is talloc-scoped client, pipe, session, and credential objects.

## Dependencies and integration points
This file depends on Samba's raw SMB1 client, SMB2 client, SMB composite session setup, RAP, DCE/RPC core, generated NDR clients for LSA/SAMR/Netlogon/SRVSVC/SPOOLSS/WINREG/WKSSVC/SVCCTL, registry helpers, security descriptor/SID helpers, credential APIs, Netlogon credential crypto, and `source3/rpc_client/init_samr.h` password encryption helpers. It is registered under the top-level `rpc` suite by `torture_rpc_init()` in `rpc.c`.

## Risks
The suite is integration-heavy and assumes a writable, Samba3-compatible server environment with `IPC$`, a configured test share, admin-capable credentials for user/privilege/share operations, optional printers for spoolss, and `wksname` for join tests. Cleanup failures can leave users, machine accounts, registry share keys, modified share security descriptors, or directories. Reauthentication and pending-read tests are timing and transport sensitive. Some tests deliberately expect legacy quirks, such as non-null zero-length alias RID arrays, exact named-pipe path syntax statuses, and LSA bind availability over the Netlogon pipe. Those expectations may fail against non-Samba servers or after intentional compatibility changes.

## Test signals
Important signals include successful named-pipe opens and binds, expected auth-level behavior, correct Netlogon credential chaining, expected `NT_STATUS_NO_TRUST_SAM_ACCOUNT` for random workstation auth, stable `lsa_GetUserName` identity across reauth, correct SID comparisons for created users, SRVSVC share enumeration/get-info success at all tested levels, share-security access outcomes matching `try_tcon()` expectations, spoolss/SRVSVC printer count agreement, WKSSVC/RAP server-name agreement, winreg enumeration and registry-config reflection into SRVSVC, expected pipe-name status codes, `NT_STATUS_PIPE_BROKEN` for canceled pending reads, and `NT_STATUS_RPC_UNSUPPORTED_NAME_SYNTAX` for unsupported interface/pipe combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samba3rpc.c -->
