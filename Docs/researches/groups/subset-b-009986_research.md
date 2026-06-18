# Research: subset-b-009986

Grouped research for Samba RPC torture sources under `sources/user-network-fs/samba/source4/torture/rpc/`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/netlogon.c -->
# sources/user-network-fs/samba/source4/torture/rpc/netlogon.c

## Purpose

`netlogon.c` is the main Samba RPC torture suite for the Netlogon (`ndr_table_netlogon`) interface. It exercises secure-channel setup, credential chaining, challenge replay handling, password set/get calls, SamLogon, replication-style database APIs, domain-controller locator APIs, trust enumeration, site mapping, workstation domain-info updates, and administrative `LogonControl*` calls.

The file is not a library implementation of Netlogon. It is a broad integration test harness that drives real DC RPC endpoints using Samba torture primitives, machine credentials, generated Netlogon credentials, schannel-protected secondary pipes, and direct SAMDB/LDAP checks where needed.

## Important APIs, Types, and Functions

Key exported helpers are:

- `test_SetupCredentials()`: performs legacy `ServerReqChallenge` plus `ServerAuthenticate`, then falls back to `test_SetupCredentials2()` with AES flags if the server reports downgrade protection.
- `test_SetupCredentials2ex()`, `test_SetupCredentials2()`: perform `ServerAuthenticate2` with caller-supplied negotiation flags, computer name, secure-channel type, and expected status.
- `test_SetupCredentials3()`: performs `ServerAuthenticate3`, returns negotiated flags/RID, validates the server credential, and reissues `ServerReqChallenge` to ensure it does not disturb an established credential chain.
- `test_SetupCredentialsDowngrade()`: verifies zero negotiate flags are rejected with `NT_STATUS_DOWNGRADE_DETECTED`, then retries with ADS/AES flags.
- `test_SetupCredentialsPipe()`: duplicates the current DCERPC binding, enables `DCERPC_SCHANNEL` plus caller flags such as `DCERPC_SIGN | DCERPC_SEAL`, temporarily installs Netlogon credential state into `cli_credentials`, and opens a secured Netlogon pipe.
- `test_netlogon_ops()` and `test_netlogon_capabilities()`: shared helpers used by other tests to validate SamLogon and `LogonGetCapabilities`.

Important static test groups include:

- Challenge and authentication: `test_ServerReqChallenge*`, `test_invalidAuthenticate2()`, `test_ServerAuthenticate2_encrypts_to_zero()`.
- Password handling: `test_SetPassword*`, `test_SetPassword2*`, `test_GetPassword()`, `test_GetTrustPasswords()`, `test_netr_ServerGetTrustInfo*()`.
- Logon: `test_LogonUasLogon()`, `test_LogonUasLogoff()`, `test_SamLogon()`, `test_SamLogon_NULL_domain()`.
- Replication/database APIs: `test_DatabaseSync()`, `test_DatabaseDeltas()`, `test_DatabaseRedo()`, `test_DatabaseSync2()`, `test_AccountDeltas()`, `test_AccountSync()`.
- DC locator/site/trust APIs: `test_GetDcName()`, `test_GetAnyDCName()`, `test_ManyGetDCName()`, `test_DsrEnumerateDomainTrusts()`, `test_netr_NetrEnumerateTrustedDomains*()`, `test_netr_DsRGetDCName*()`, `test_netr_DsRAddressToSitenames*()`, `test_netr_DsrGetDcSiteCoverageW()`.
- Domain-info and admin: `test_GetDomainInfo()`, `test_GetDomainInfo_async()`, `test_LogonControl()`, `test_LogonControl2()`, `test_LogonControl2Ex()`.

The suite constructors are `torture_rpc_netlogon()`, `torture_rpc_netlogon_s3()`, `torture_rpc_netlogon_zerologon()`, and `torture_rpc_netlogon_admin()`.

## Control Flow

Most credential-dependent tests follow the same pattern:

1. Establish or receive a Netlogon DCERPC pipe from the torture framework.
2. Build client and server challenges with `netlogon_creds_random_challenge()` or an intentionally malformed challenge.
3. Call `dcerpc_netr_ServerReqChallenge_r()`.
4. Derive client credential state with `netlogon_creds_client_init()` from the machine password hash, challenges, secure-channel type, and negotiation flags.
5. Authenticate with `ServerAuthenticate`, `ServerAuthenticate2`, or `ServerAuthenticate3`.
6. Validate credential chaining with `netlogon_creds_client_check()` or `netlogon_creds_client_verify()`.
7. For protected calls, open a schannel pipe with `test_SetupCredentialsPipe()` and advance authenticators for each call.

The ZeroLogon-focused suite branches from this normal flow by feeding all-zero or repeated-byte challenges and by constructing password buffers that encrypt to zero-like values. It asserts `NT_STATUS_ACCESS_DENIED` or `NT_STATUS_WRONG_PASSWORD` in those paths and accepts success only for the four-byte repeated challenge boundary case.

Password tests first authenticate, then build `samr_Password` or `samr_CryptPassword` buffers, encrypt them with the negotiated Netlogon credential state and the binding auth level, call `ServerPasswordSet` or `ServerPasswordSet2`, check the return authenticator, update local `cli_credentials` to the new password/hash, and prove the change by re-authenticating.

Replication tests use a static `sequence_nums[3]` cache. `DatabaseSync()` discovers per-database sequence numbers, and `DatabaseDeltas()` consumes them to request changes. `DatabaseRedo()` iterates a large in-file table of change-log cases across SAM, BUILTIN, and LSA databases, asserting expected status, result count, and delta types.

DC locator and site tests call locator APIs with DNS and flat domain names, verify returned flags, and in some cases call `DsRGetSiteName` on the returned DC UNC. Site-address tests build IPv4 and optionally IPv6 sockaddr buffers, then repeat with too-short buffers and invalid address families to assert null site/subnet outputs.

`test_GetDomainInfo()` is stateful and multi-phase. It opens a sealed schannel pipe, optionally binds LDAP to the target DC's SAMDB, sends `LogonGetDomainInfo` with workstation OS/DNS/SPN flags, sleeps briefly for updates, checks AD attributes, then repeats with changed DNS names, missing OS fields, inbound-trust flags, null DNS hostnames, extra flags, and optionally no workstation info when dangerous tests are enabled.

Suite registration wires these functions into separate torture suites. The main suite runs broad Netlogon coverage; `netlogon-s3` is narrower and Samba3-oriented; `netlogon.zerologon` isolates CVE-2020-1472 regression tests; `netlogon.admin` tests BDC, workstation, and unauthenticated/admin `LogonControl*` behavior.

## State and Persistence Behavior

This file deliberately mutates external test state:

- Machine account passwords are changed repeatedly by `ServerPasswordSet` and `ServerPasswordSet2`; local `cli_credentials` are updated after successful changes so later tests can continue.
- `test_GetDomainInfo()` may update or verify AD attributes on the torture machine account, including `operatingSystem`, `operatingSystemServicePack`, `operatingSystemVersion`, `dNSHostName`, and `servicePrincipalName`.
- `sequence_nums[3]` is a process-global cache shared from `DatabaseSync()` to `DatabaseDeltas()`.
- Netlogon credential chains are mutable state; each authenticator call advances the chain and must be verified against the returned authenticator.
- Temporary secondary pipes are created for schannel, LSA-over-Netlogon, and DC locator stress paths and then released via talloc ownership.

The tests assume a disposable torture machine account named `torturetest`. Running these against a non-disposable account or production DC would be risky.

## Dependencies and Integration Points

The file depends on Samba's torture framework, generated NDR clients for Netlogon and LSA, libcli credential/auth helpers, Netlogon credential crypto helpers, event handling, command-line credentials, loadparm configuration, LDB/SAMDB access, socket address definitions, and DCERPC binding APIs.

Important integration points include:

- `torture_suite_add_machine_bdc_rpc_iface_tcase()` and `torture_suite_add_machine_workstation_rpc_iface_tcase()` create machine-account contexts for secure-channel tests.
- `dcerpc_*_r()` generated client calls provide synchronous RPC execution.
- `dcerpc_netr_LogonGetDomainInfo_r_send/recv()` and `tevent` provide async request coverage.
- `ldb_wrap_connect()`, `gendb_search()`, and `samdb_search_string()` validate server-side AD state after Netlogon calls.
- `dcerpc_secondary_auth_connection()` verifies LSA behavior over named-pipe associations and stress-tests interaction between Netlogon and LSA pipes.

## Risks and Edge Cases

The highest-risk areas are the ones the tests intentionally stress: credential downgrade handling, challenge reuse across pipes/global caches, zero/repeated challenge rejection, all-zero encrypted password buffers, empty machine passwords, ARC4/AES negotiation differences, return-authenticator chain advancement, and AD state updates from workstation info.

Environment sensitivity is high. Some branches skip or loosen expectations for Samba3/Samba4 settings, native mode servers, dangerous tests, local transports, lack of IPv6, Windows behavior around empty passwords, and unimplemented Netlogon APIs.

There is a notable implementation hazard in `test_GetDomainInfo_async()`: it calls `test_SetupCredentials3(p, ...)` before `p` is assigned, even though the function parameter is `p1`. Since `test_SetupCredentials3()` returns false when passed `NULL`, this path appears to fail before opening the schannel pipe unless surrounding build or call context masks it. That should be reviewed before relying on async coverage.

The tests print generated passwords in torture comments. This is acceptable for disposable torture accounts but is a logging risk if run with real machine credentials.

## Test Signals

Passing signals include exact NTSTATUS/WERROR assertions, successful credential-chain checks, expected `ServerAuthenticate*` downgrade or denial statuses, successful re-authentication after password mutations, expected database delta counts/types, expected DC locator flags, expected site/subnet nulling for invalid addresses, and AD attribute matches after `LogonGetDomainInfo`.

Failing signals are intentionally precise: unexpected `NT_STATUS_OK` for forbidden ZeroLogon-style inputs, mismatched return authenticators, unsupported AES negotiation when required, changed DNS/SPN state when it should stick, unexpected `LogonControl*` access/error codes, or inability to reconnect with newly set machine credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/netlogon.h -->
# sources/user-network-fs/samba/source4/torture/rpc/netlogon.h

## Purpose

`netlogon.h` is a small local header that exposes selected Netlogon torture helper functions implemented in `netlogon.c` for reuse by sibling RPC torture files. It avoids duplicating the secure-channel bootstrap logic in tests that need authenticated Netlogon state.

## Important APIs, Types, and Functions

The header declares:

- `test_SetupCredentials2()`: authenticate using `ServerAuthenticate2` with caller-supplied negotiate flags and secure-channel type.
- `test_SetupCredentials3()`: authenticate using `ServerAuthenticate3` with caller-supplied negotiate flags.
- `test_SetupCredentialsPipe()`: open a second DCERPC pipe using existing Netlogon credential state and additional DCERPC auth options.

The declarations use `struct dcerpc_pipe`, `struct torture_context`, `struct cli_credentials`, and `struct netlogon_creds_CredentialState`. The secure-channel argument in `test_SetupCredentials2()` is an `int` in the header, while the implementation uses `enum netr_SchannelType`; callers should pass the enum-compatible values from Samba credential helpers.

## Control Flow

The header has no runtime control flow. Its role is compile-time linkage: consumers include it, call a setup helper to establish credential state, then optionally call `test_SetupCredentialsPipe()` to get a schannel-protected pipe for subsequent RPC operations.

## State and Persistence Behavior

No state is stored in the header. The declared functions operate on caller-owned pipes and credentials. `test_SetupCredentialsPipe()` is stateful through `cli_credentials_set_netlogon_creds()` in the implementation, but the header itself only exposes the contract.

## Dependencies and Integration Points

The file assumes the including translation unit already has compatible Samba type declarations available. It integrates Netlogon helper routines across the `source4/torture/rpc` test area.

## Risks and Edge Cases

The declarations are not protected by an include guard in this file. In practice it is small and likely included once, but adding another include path could cause repeated declaration warnings only if signatures drift. The `int` versus enum secure-channel parameter should be kept ABI-compatible with the implementation.

## Test Signals

There are no standalone tests for this header. Its health is signaled by successful compilation of consumers and by runtime success of tests that use the declared helpers to establish Netlogon credential chains and schannel pipes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/netlogon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/netlogon_crypto.c -->
# sources/user-network-fs/samba/source4/torture/rpc/netlogon_crypto.c

## Purpose

`netlogon_crypto.c` defines a focused FIPS/weak-crypto torture suite for Netlogon secure-channel authentication. It verifies that AES negotiation succeeds and that RC4/ARCFOUR negotiation is rejected or unavailable when weak crypto is not allowed.

## Important APIs, Types, and Functions

The central helper is `test_ServerAuth3Crypto()`. It performs a complete `ServerReqChallenge` and `ServerAuthenticate3` flow, but parameterizes the negotiate flags and whether client-side RC4 should be forced. It uses `netlogon_creds_client_init()` for credential derivation, `GNUTLS_FIPS140_SET_LAX_MODE()`/`GNUTLS_FIPS140_SET_STRICT_MODE()` around forced RC4, and `lpcfg_weak_crypto()` to adapt assertions to the configured weak-crypto policy.

The public suite factory is `torture_rpc_netlogon_crypto_fips()`. It registers:

- `test_AES_Crytpo`: requests ADS flags plus `NETLOGON_NEG_SUPPORTS_AES` and expects success.
- `test_RC4_Crytpo_Fail`: requests ADS flags plus `NETLOGON_NEG_ARCFOUR` and expects client credential initialization to fail when weak crypto is disabled.
- `test_RC4_Crytpo_Force`: forces lax FIPS mode client-side so the server response can be tested; when weak crypto is disabled, the expected server result is `NT_STATUS_DOWNGRADE_DETECTED` with negotiated flags cleared.

## Control Flow

Each test receives a machine-backed Netlogon pipe from `torture_suite_add_machine_bdc_rpc_iface_tcase()`. The helper generates a client challenge, calls `ServerReqChallenge`, hashes the machine password with `E_md4hash()`, prepares `ServerAuthenticate3`, derives client credential state, and calls the RPC. It then validates server credential chaining and negotiated flags.

The RC4 paths invert the normal success condition: if RC4 setup or authentication fails for the expected policy reason, the test wrapper returns success. If RC4 unexpectedly succeeds while weak crypto is disabled, the wrapper fails.

## State and Persistence Behavior

The file does not persist server state or change account passwords. It temporarily changes the process crypto mode with GnuTLS FIPS helpers during forced RC4 client credential creation, then restores strict mode. The main mutable state is the local Netlogon credential state and negotiated flags.

## Dependencies and Integration Points

The file depends on Samba generated Netlogon RPC clients, libcli auth helpers, loadparm weak-crypto policy, GnuTLS FIPS-mode macros exposed through Samba headers, and the torture machine-account RPC testcase helper.

It complements the larger `netlogon.c` suite by isolating crypto-policy behavior under a separate `fips.netlogon.crypto` suite name.

## Risks and Edge Cases

The expected result depends on `lpcfg_weak_crypto(tctx->lp_ctx)`. In environments where weak crypto is explicitly allowed, RC4 behavior will differ from hardened/FIPS expectations.

The helper intentionally relaxes FIPS mode to manufacture a forced-RC4 client request. A failure to restore strict mode would leak process crypto policy into later tests, but the code unconditionally calls `GNUTLS_FIPS140_SET_STRICT_MODE()` after credential initialization.

The registered test names contain `Crytpo` rather than `Crypto`; this affects test naming/discovery but not behavior.

## Test Signals

Success is signaled by AES negotiation including `NETLOGON_NEG_SUPPORTS_AES`, by client-side RC4 credential initialization failing when weak crypto is prohibited, or by server-side forced RC4 returning `NT_STATUS_DOWNGRADE_DETECTED`. Credential-chain validation is the main integrity signal for successful authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/netlogon_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/ntsvcs.c -->
# sources/user-network-fs/samba/source4/torture/rpc/ntsvcs.c

## Purpose

`ntsvcs.c` defines a compact RPC torture suite for the Windows Plug and Play/NT services RPC interface represented by `ndr_table_ntsvcs`. It probes a small set of PNP calls and validates basic marshalling, expected error codes, and buffer sizing behavior.

## Important APIs, Types, and Functions

The suite factory is `torture_rpc_ntsvcs()`, which registers four tests:

- `test_PNP_GetVersion()`: calls `PNP_GetVersion` and expects version `0x400`.
- `test_PNP_GetDeviceListSize()`: calls `PNP_GetDeviceListSize` first with a null device/service name expecting `WERR_CM_INVALID_POINTER`, then with `"Spooler"` expecting success.
- `test_PNP_GetDeviceList()`: calls `PNP_GetDeviceList` with a null filter expecting `WERR_CM_INVALID_POINTER`; then queries `"Spooler"`, handles `WERR_CM_BUFFER_SMALL` by asking for the required length, allocates the buffer, and retries.
- `test_PNP_GetDeviceRegProp()`: queries `DEV_REGPROP_DESC` for a hard-coded ACPI path and retries with the reported `needed` size if the first call reports `WERR_CM_BUFFER_SMALL`.

All calls are generated DCERPC client calls against `struct dcerpc_binding_handle *b = p->binding_handle`.

## Control Flow

Each test initializes the relevant NDR request structure, fills in input and output pointer fields, performs the generated RPC call, and asserts both transport-level NTSTATUS and operation-level WERROR. Buffer-sized calls intentionally start with minimal buffers to exercise the server's size-reporting path before retrying with allocated storage.

## State and Persistence Behavior

The tests are read-only from the server's perspective. They allocate temporary buffers from `tctx` with talloc and do not store process-global state. The only mutable values are local output scalars such as `version`, `size`, `length`, `needed`, and registry data type.

## Dependencies and Integration Points

The file depends on the Samba torture RPC framework and generated `ndr_ntsvcs_c.h` bindings. It integrates into the RPC torture registry under suite name `ntsvcs` and uses `torture_suite_add_rpc_iface_tcase()` for a plain RPC interface testcase.

## Risks and Edge Cases

The hard-coded `"Spooler"` service and `ACPI\\ACPI0003\\1` device path are environment-sensitive. The tests mostly assert call mechanics and some known Windows-compatible behavior, but device-registry data may vary by target.

`test_PNP_GetDeviceRegProp()` returns true after retrying and does not assert the final WERROR; it primarily guards transport success and buffer-retry behavior rather than property presence.

## Test Signals

Useful signals include exact `WERR_CM_INVALID_POINTER` for null device/filter inputs, successful size and list calls for `"Spooler"`, successful handling of `WERR_CM_BUFFER_SMALL`, and `PNP_GetVersion` returning `0x400`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/ntsvcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/object_uuid.c -->
# sources/user-network-fs/samba/source4/torture/rpc/object_uuid.c

## Purpose

`object_uuid.c` tests whether DCERPC requests carrying arbitrary object UUIDs are accepted for selected RPC interfaces. It verifies that Samba's DCERPC client path can pass a non-null object UUID through `dcerpc_binding_handle_call()` without breaking normal server dispatch for DS setup and LSA calls.

## Important APIs, Types, and Functions

The only test body is `test_random_uuid()`. It opens two RPC pipes, one to `ndr_table_dssetup` and one to `ndr_table_lsarpc`, generates random GUIDs with `GUID_random()`, and calls:

- `NDR_DSSETUP_DSROLEGETPRIMARYDOMAININFORMATION` with `dssetup_DsRoleGetPrimaryDomainInformation`.
- `NDR_LSA_GETUSERNAME` with `lsa_GetUserName`.

The suite factory `torture_rpc_object_uuid()` registers this as `random-uuid`.

## Control Flow

The test opens the DS setup pipe, opens the LSA pipe, generates a random object UUID, calls DS role information through the generic binding-handle call API, asserts transport success and WERROR success, generates another random UUID, then calls LSA `GetUserName` and asserts transport and operation NTSTATUS success.

The test deliberately uses `dcerpc_binding_handle_call()` instead of the generated convenience wrappers so it can pass the object UUID parameter explicitly.

## State and Persistence Behavior

The test is read-only. It creates transient pipe handles, local GUIDs, request structures, and output string pointers. It does not mutate server state or retain any process-global state.

## Dependencies and Integration Points

The file depends on generated NDR metadata for DS setup and LSA, the Samba torture RPC connection helper, GUID generation, and the generic DCERPC binding-handle call path. It integrates into the torture suite namespace as `objectuuid`.

## Risks and Edge Cases

The test assumes the target accepts arbitrary object UUIDs for these calls. A server or transport that enforces object UUID filtering more strictly could fail even if the operations themselves work through generated wrappers.

The failure messages for the LSA call say `"lsaClose failed"` even though the operation is `GetUserName`; this is only diagnostic text but can make failure triage less direct.

## Test Signals

Success is transport-level `NT_STATUS_OK` plus operation-level success for both DS setup and LSA calls while a random object UUID is present. This signals that object UUID marshalling and dispatch interaction are functioning for the tested interfaces.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/object_uuid.c -->
