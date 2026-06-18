# Research: subset-b-009991

Grouped research for Samba RPC torture sources under `sources/user-network-fs/samba/source4/torture/rpc`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samr_accessmask.c -->
# sources/user-network-fs/samba/source4/torture/rpc/samr_accessmask.c

## Purpose

This file defines two SAMR torture suites. `torture_rpc_samr_accessmask()` checks the server-side interpretation of access masks on SAMR connect handles, domain lookup/open calls, domain enumeration, and policy-handle security descriptors. `torture_rpc_samr_workstation_auth()` verifies that a machine workstation account can perform common read-oriented SAMR queries while requesting `SEC_FLAG_MAXIMUM_ALLOWED`, matching winbind and other Samba client behavior.

The tests are protocol compatibility and authorization tests rather than unit tests. They exercise a live SAMR endpoint, create temporary accounts, authenticate with user or machine credentials, and assert specific `NTSTATUS` results for access-mask combinations.

## Important APIs, Types, and Functions

- Local helpers `torture_samr_Close()` and `torture_samr_Connect5()` wrap `dcerpc_samr_Close_r()` and `dcerpc_samr_Connect5_r()` and return the operation result after transport success.
- `test_samr_accessmask_Connect5()` iterates one-bit masks and asserts which bits can obtain a connect handle.
- `test_samr_accessmask_EnumDomains()`, `test_samr_accessmask_LookupDomain()`, and `test_samr_accessmask_OpenDomain()` verify that only specific connect-handle rights allow those follow-up operations.
- `test_samr_connect_user_acl()` reads the SAMR policy security descriptor, attempts to add a deny ACE for a test user with `SAMR_ACCESS_CONNECT_TO_SERVER`, verifies the user can still connect, and verifies the descriptor did not change despite `SetSecurity` success.
- `test_samr_connect_user_acl_enforced()` authenticates as the test user and expects a request for `SAMR_ACCESS_SHUTDOWN_SERVER` to fail.
- `test_samr_domain()`, `test_samr_users()`, `test_samr_groups()`, and `test_samr_aliases()` enumerate and query domain objects for the workstation-auth suite.
- The suite builders use `torture_suite_add_rpc_iface_tcase()` for ordinary SAMR tests and `torture_suite_add_machine_workstation_rpc_iface_tcase()` for machine-authenticated SAMR tests.

## Control Flow

The accessmask suite registers five tests. The bitmask tests all follow a similar pattern: loop through 33 one-bit masks, call `Connect5`, branch on the bit position, then either require the connect/open/query call to succeed or require `NT_STATUS_ACCESS_DENIED`. Successful handles are explicitly closed. `OpenDomain` first obtains the current domain SID via a maximum-allowed connect handle, then repeats the bitmask loop using that SID.

The ACL tests run through `test_samr_connect()`. A temporary normal user is created with `torture_create_testuser()`, credentials are assembled with `cli_credentials_*`, and the user SID is read from the join context. The test then checks that `SetSecurity` on a SAMR connect handle does not persistently modify the server descriptor and that the descriptor is still enforced for an ordinary user's requested access. Cleanup is via `torture_leave_domain()`.

The workstation-auth suite starts with a machine workstation tcase. `torture_rpc_samr_workstation_query()` opens a SAMR connection, opens the workgroup domain, queries domain info, walks display-info users, domain groups, and aliases, and opens/queries each object where applicable.

## State and Persistence Behavior

The file intentionally mutates external server state by creating and deleting `samr_testuser` and by creating a temporary workstation account named from `TEST_MACHINENAME`. It also calls `samr_SetSecurity` against a connect handle, but the expected behavior is that this does not persistently change the SAMR policy descriptor. Handles are closed after successful paths, and test-user cleanup relies on Samba torture join helpers.

No local persistent state is written. All durable effects are on the target server under test, so failed or interrupted runs can leave temporary domain accounts until the test harness cleanup runs.

## Dependencies and Integration Points

This file depends on generated SAMR NDR client bindings (`ndr_samr_c.h`), torture RPC helpers (`torture_rpc.h`), loadparm/workgroup settings, and security descriptor helpers from `libcli/security/security.h`. It integrates with the Samba torture suite registry through exported suite constructors and relies on common test join helpers for user and machine account lifecycle. It also uses `lpcfg_workgroup()` and `torture_setting_string()` to bind assertions to the active test domain.

## Risks and Edge Cases

The bit-position expectations encode default SAMR ACL semantics and may be sensitive to server policy changes, Samba3 behavior, or non-standard domain ACLs. The test explicitly skips `test_samr_connect()` against Samba3. The workstation-auth path assumes a domain with exactly one non-builtin domain when auto-enumerating, well-formed display info, and queryable users/groups/aliases.

The loop uses `uint32_t mask` and shifts through 33 iterations; after bit 31, the next shift wraps to zero. The tests are written around bit positions rather than symbolic rights, making maintenance error-prone when SAMR rights change. Several failure paths return before closing handles or freeing temporary pipes, which is acceptable for a terminating torture test but can complicate repeated in-process runs.

## Test Signals

Strong pass signals are exact `NTSTATUS` matches for access-denied cases, successful close calls on opened handles, unchanged security descriptor size after `SetSecurity`, successful ordinary-user denial for shutdown access, and successful workstation-authenticated enumeration/query of users, groups, aliases, and domain info. Failures indicate regressions in access-mask mapping, SAMR policy descriptor handling, machine-account authorization, or compatibility with Windows/Samba SAMR semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samr_accessmask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samr_handletype.c -->
# sources/user-network-fs/samba/source4/torture/rpc/samr_handletype.c

## Purpose

This file defines the `samr.handletype` torture suite, focused on validating SAMR policy-handle context typing. It checks that operations fail with `NT_STATUS_RPC_SS_CONTEXT_MISMATCH` when a policy handle has the right wire shape but either a tampered context UUID or an incorrect `handle_type` field.

## Important APIs, Types, and Functions

- `enum samr_handle` mirrors the SAMR handle-type values used by the test: connect, domain, user, group, and alias.
- `torture_samr_Close()` wraps `dcerpc_samr_Close_r()`.
- `torture_samr_Connect5()` opens a SAMR connect handle for a requested mask.
- `test_samr_handletype_OpenDomain()` is the only test body. It exercises `LookupDomain`, `OpenDomain`, `OpenUser`, and `OpenGroup` with both valid and deliberately corrupted handles.
- `torture_rpc_samr_handletype()` registers the suite and an RPC tcase for `ndr_table_samr`.

## Control Flow

The test first connects with `SEC_FLAG_MAXIMUM_ALLOWED`, looks up the configured workgroup domain SID, and then reconnects with a minimal access mask. It copies the valid connect handle into `bad`, changes the UUID to a random GUID, and asserts that `OpenDomain` returns `NT_STATUS_RPC_SS_CONTEXT_MISMATCH`. It then changes the copied handle type to `SAMR_HANDLE_USER` and expects the same mismatch.

After confirming a valid domain open, the test copies the domain handle and changes its type before `OpenUser` and `OpenGroup`. `OpenUser` with `SAMR_HANDLE_ALIAS` must fail with context mismatch; resetting the type to `SAMR_HANDLE_DOMAIN` must allow opening RID 501. `OpenGroup` with `SAMR_HANDLE_GROUP` as the domain handle type must fail; resetting to domain type must allow opening RID 513. Opened user/group/connect handles are closed.

## State and Persistence Behavior

The test does not create accounts or modify domain state. It uses fixed well-known RIDs and transient policy handles. The only state mutation is local tampering of copied `policy_handle` structures before sending requests.

## Dependencies and Integration Points

The file depends on generated SAMR NDR bindings, the torture RPC framework, loadparm workgroup configuration, GUID generation, and `NTSTATUS` assertion helpers. It integrates as a single test named `OpenDomainHandleType` under the `samr.handletype` suite.

## Risks and Edge Cases

The test assumes RID 501 and RID 513 exist and are openable in the target domain. It also assumes the client-visible `policy_handle` structure exposes and honors `uuid` and `handle_type` in a way that can be safely tampered for negative tests. One assertion after `OpenGroup` checks `ou.out.result` rather than `og.out.result`, which can mask an `OpenGroup` result failure after a successful transport call.

## Test Signals

The key signal is exact `NT_STATUS_RPC_SS_CONTEXT_MISMATCH` for random-GUID and wrong-handle-type requests, followed by successful operation with the same handle restored to the expected domain type. A failure indicates the server accepts mismatched SAMR contexts, returns a different context error, or no longer supports the assumed well-known objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samr_handletype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samr_priv.c -->
# sources/user-network-fs/samba/source4/torture/rpc/samr_priv.c

## Purpose

This file defines the `samr.priv` torture suite. It tests two authorization-sensitive SAMR behaviors: user-info caching after account deletion and access control for a non-privileged domain user attempting administrative SAMR operations.

## Important APIs, Types, and Functions

- `struct torture_user` describes a test user's identity, optional builtin memberships, and privilege intent.
- `struct torture_access_context` carries the authenticated SAMR pipe, user metadata, and join context for access tests.
- Basic SAMR helpers wrap name lookup, user creation, user open, domain open, connect, and `QueryUserInfo`.
- `torture_rpc_samr_caching()` creates a user, repeatedly opens and queries it on a second connection, deletes it, and then repeatedly verifies lookup/open behavior after deletion.
- `torture_rpc_samr_access_setup()` creates a normal test user, builds credentials, optionally adds builtin alias memberships, and opens an authenticated SAMR pipe as that user.
- `torture_rpc_samr_access()` attempts to create another user through the non-privileged pipe and requires failure.
- `torture_rpc_samr_priv()` registers `caching` and `access` under an SAMR RPC tcase.

## Control Flow

The caching test creates `guru0000`, then calls `test_samr_userinfo_getinfo()` twenty times with `expected=false`. Each iteration opens a new secondary SAMR connection, connects, opens the configured domain, opens the user by lookup RID, queries general user info, closes handles, and frees the pipe. After deleting the user, it repeats twenty calls with `expected=true`; the helper treats name lookup failure as success in that mode, checking that stale cache data does not allow a deleted user to be opened and queried.

The access test allocates a `torture_access_context`, creates a normal user `guru0100`, opens a SAMR connection authenticated as that user, and tries to create `guru0200` with `SEC_FLAG_MAXIMUM_ALLOWED`. The call must return false. Setup includes optional builtin alias membership code, but the registered access test does not populate memberships, so the membership branch is normally unused.

## State and Persistence Behavior

The file creates and deletes live domain users. It uses `torture_create_testuser()` and `torture_delete_testuser()` in the caching path, and `torture_create_testuser()` in the access path. The access path stores its join context but does not explicitly call a leave/delete helper in `torture_rpc_samr_access()`, so cleanup depends on talloc destructors or the broader torture join cleanup behavior. All other state is transient RPC handles and pipes.

## Dependencies and Integration Points

Dependencies include generated SAMR bindings, `dcerpc_pipe_connect()`, common torture RPC helpers, credential construction via `cli_credentials_*`, domain settings via `torture_setting_string()` and `lpcfg_workgroup()`, and shared `test_samr_handle_Close()` from the broader SAMR torture support. It integrates with the live domain account database and must run with initial credentials that can create/delete test accounts.

## Risks and Edge Cases

The caching test has fixed account names and can collide with stale accounts from prior failed runs. The `expected` parameter in `test_samr_OpenUser()` is counterintuitive: lookup failure returns true only when failure is expected. The optional builtin membership helper appears to zero `alias_handle` immediately before `samr_AddAliasMember`, which would invalidate the handle if that branch is exercised. The access test's lack of explicit cleanup is a persistence risk if join cleanup is not automatic.

## Test Signals

Caching passes when repeated query operations succeed before deletion and fail after deletion, indicating that server-side user caches invalidate deleted accounts. Access passes when an authenticated non-privileged user cannot create another account. Failures point to stale SAMR object caching, incorrect privilege enforcement, broken test-account lifecycle, or cleanup leakage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samr_priv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samsync.c -->
# sources/user-network-fs/samba/source4/torture/rpc/samsync.c

## Purpose

This file implements the `torture_rpc_samsync()` Netlogon SAM database synchronization test. It creates BDC, workstation, and normal-user test accounts; opens Netlogon secure channels; runs `DatabaseSync`, `DatabaseDeltas`, and `DatabaseSync2`; decrypts returned deltas; and cross-checks those deltas against live SAMR, LSA, and SamLogon observations.

The test is a broad consistency harness for replication data, Netlogon credential chaining, SAMR object reads, LSA secrets/accounts/trusted domains, and encrypted secret handling.

## Important APIs, Types, and Functions

- `test_SamLogon()` builds NT/LM network responses from hashes and calls `netr_LogonSamLogon`, checking returned authenticators.
- `struct samsync_state` holds replication sequence numbers, domain names/SIDs, secure-channel creds, SAMR/LSA/Netlogon pipes, and lists of secrets/trusted domains discovered during sync.
- `samsync_open_domain()`, `samsync_query_samr_sec_desc()`, and `samsync_query_lsa_sec_desc()` provide cross-protocol lookup and security descriptor reads.
- `samsync_handle_domain()`, `policy()`, `user()`, `alias()`, `group()`, `secret()`, `trusted_domain()`, and `account()` validate individual `netr_DELTA_ENUM` payloads against SAMR, LSA, or SamLogon.
- `test_DatabaseSync()` performs full sync over domain, builtin, and privs databases and dispatches each delta to a handler after `samsync_fix_delta()`.
- `test_DatabaseDeltas()` requests deltas starting slightly before recorded sequence numbers.
- `test_DatabaseSync2()` repeats sync through the newer Netlogon operation.

## Control Flow

The top-level function creates a server-trust machine account (`samsynctest$`), workstation account (`samsynctest2$`), and normal user. It opens a SAMR pipe from the BDC join context, connects to SAMR, opens the workgroup domain, and changes OEM domain info to force a visible sequence update. It then opens LSA policy with maximum access.

Next it binds to Netlogon with `DCERPC_SCHANNEL | DCERPC_SIGN` as the BDC account and stores the resulting Netlogon credential state. It creates a second signed secure-channel Netlogon pipe as the workstation account for SamLogon validation. With both secure channels ready, it runs full sync, delta sync, and sync2. All paths end at a `failed:` label that leaves the created domain accounts and frees the top-level talloc context.

During `DatabaseSync`, each returned delta array is processed in a loop until no `STATUS_MORE_ENTRIES` remains. Delta payloads are decrypted/fixed with `samsync_fix_delta()`. Domain deltas cache names, SIDs, handles, sequence numbers, and compare domain info levels and security descriptors. User deltas open the user via SAMR, compare level 21 fields, compare group membership, parse optional private key material, and validate password hashes via workstation Netlogon SamLogon when possible. Secret deltas open the LSA secret, retrieve current/old values, decrypt them with the LSA transport session key, and compare data and mtimes.

## State and Persistence Behavior

This test intentionally mutates the domain. It creates three accounts and changes domain OEM information via `samr_SetDomainInfo` level 4. It records sync sequence numbers in memory and stores discovered secrets/trusted domains in talloc-owned linked lists. It does not write local files. Cleanup attempts to leave all created accounts even after failures, but the domain OEM info mutation is not restored.

## Dependencies and Integration Points

Dependencies include Netlogon, SAMR, LSA generated NDR bindings; secure-channel credential code; `libcli/samsync/samsync.h` for delta decryption; security descriptor comparison; MD4/SMBOWF crypto helpers; GnuTLS error mapping; and the torture join/account helpers. Integration is cross-protocol: Netlogon replication output is treated as source data, then checked against SAMR domain/user/group/alias reads, LSA secret/account/trusted-domain reads, and Netlogon SamLogon authentication.

## Risks and Edge Cases

The test is environment-sensitive and high impact: it needs privileges to create machine accounts, read secrets/privileges, open LSA objects, and perform BDC-style synchronization. Some checks accept Windows compatibility differences, such as unavailable trusted-domain level 8 info, access-denied LSA secrets, missing old secret values, or password-change timing ambiguity. The domain OEM info mutation is durable. A duplicated `NT_STATUS_NOLOGON_INTERDOMAIN_TRUST_ACCOUNT` branch in user logon handling is harmless but redundant.

Because it walks all sync deltas and may validate password material, failures can arise from policy, ACL, crypto negotiation, or timing rather than just code defects. Interrupted runs can leave test machine/user accounts. The test assumes domain data ordering supplies domain information before user/group/alias deltas for that database.

## Test Signals

Pass signals include valid Netlogon credential chaining on every sync call, decryptable deltas, matching SAMR/LSA security descriptors and object fields, successful or correctly rejected SamLogon attempts based on account flags, matching secret ciphertext-derived values after session-key decryption, and acceptable `DatabaseDeltas` results including `NT_STATUS_SYNCHRONIZATION_REQUIRED`. Failures indicate replication inconsistency, broken secure-channel crypto, incorrect SAMR/LSA object state, or insufficient test privileges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/samsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/scanner.c -->
# sources/user-network-fs/samba/source4/torture/rpc/scanner.c

## Purpose

This file implements `torture_rpc_scanner()`, a generic RPC endpoint scanner for Samba torture. It iterates every locally registered NDR interface, maps or binds to the interface on the target server, asks the RPC management interface for advertised interface IDs, and probes procedure numbers with raw calls to estimate how many calls are available.

## Important APIs, Types, and Functions

- `test_num_calls()` is the callback used by management interface enumeration. It connects to an interface syntax ID, sends synthetic raw calls with a 1000-byte `0xFF` stub body, and stops on out-of-range, access-denied, protocol-error, disconnect, or 200 calls.
- `torture_rpc_scanner()` retrieves the base binding, loops through `ndr_table_list()`, maps endpoints over TCP with `dcerpc_epm_map_binding()` or sets named-pipe endpoint/abstract syntax directly, connects to the `mgmt` interface, and calls `test_inq_if_ids()`.
- `ndr_table_by_syntax()` is used to match advertised syntaxes back to local IDL metadata; unknown syntaxes are represented by a synthetic table with `UINT32_MAX` calls.

## Control Flow

The scanner obtains the torture binding and determines transport. It skips local tables with zero calls and the management interface itself. For each remaining local interface it prints the pipe name, maps or rewrites the binding for that interface, stores the binding string back into `torture:binding`, connects to `ndr_table_mgmt`, and calls `test_inq_if_ids()`.

For each syntax ID returned by management, `test_num_calls()` opens a pipe to that syntax. If the interface is unknown locally, it constructs a temporary table using the original interface as a template but with the advertised syntax ID. It then repeatedly calls `dcerpc_binding_handle_raw_call()` for opnums 0 through 199. `NT_STATUS_RPC_PROCNUM_OUT_OF_RANGE` ends the count. Access denied and disconnect stop early. Protocol errors are reported but scanning continues. The final count is compared with local IDL `num_calls` when known.

## State and Persistence Behavior

The scanner does not mutate server state intentionally, but raw calls with invalid stubs may still reach server-side dispatch paths. Local state is limited to temporary talloc loop contexts, binding-string updates inside the torture loadparm context, and printed diagnostic output.

## Dependencies and Integration Points

It depends on generated management RPC bindings, the global NDR interface registry, endpoint mapper support, raw DCERPC call support, and `test_inq_if_ids()` from the management torture helpers. It is transport-aware and handles `NCACN_IP_TCP` differently from named-pipe style transports.

## Risks and Edge Cases

The probe sends malformed input to every discovered opnum, so it can trigger server bugs, noisy logs, or disconnects. A hard 200-call limit may undercount very large interfaces. Access-denied results stop a scan even if later opnums would be visible. The scanner mutates the shared `torture:binding` setting while iterating, which can surprise code that assumes it remains the original binding.

## Test Signals

The main signal is diagnostic rather than strict assertion: for each interface, it reports the discovered call count and whether it matches local IDL. The function returns false on binding/setup failures or failed management enumeration, but many per-interface connection failures are printed and treated as non-fatal so the scanner can continue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/scanner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/schannel.c -->
# sources/user-network-fs/samba/source4/torture/rpc/schannel.c

## Purpose

This file contains secure-channel torture tests for Netlogon, SAMR, and LSA RPC. It verifies that workstation and server-trust machine accounts can establish Schannel-protected connections with sign/seal and different crypto modes, that credential chaining survives secondary connections and fresh sockets, that SamLogonEx validation keys decrypt correctly, that anonymous password-set attempts fail, and that multiple Schannel connections can operate concurrently.

## Important APIs, Types, and Functions

- `test_netlogon_ex_ops()` builds NTLM network logon responses for the command-line user, calls `netr_LogonSamLogonEx` at validation levels 6, 2, and 3, decrypts encrypted validation keys with `netlogon_creds_decrypt_samlogon_validation()`, and compares them with level 6 when available.
- `test_netlogon_ex_bug14932()` is a regression variant using a fixed NTLMv2 timestamp/names blob pattern associated with Samba bug 14932.
- `test_samr_ops()` performs SAMR connect/open and repeated `GetDomPwInfo` calls over a Schannel binding.
- `test_lsa_ops()` calls `lsa_GetUserName` and checks whether Schannel maps to anonymous or to explicit credentials, with Samba3 tolerance.
- `test_schannel()` is the main scenario for one machine account and one Schannel flag combination.
- `test_schannel_anonymous_setPassword()` attempts `ServerPasswordSet` or `ServerPasswordSet2` with anonymous credentials and requires a non-OK operation result.
- `torture_rpc_schannel()`, `torture_rpc_schannel_anon_setpw()`, `torture_rpc_schannel2()`, and `torture_rpc_schannel_bench1()` are externally registered torture entry points.
- `struct torture_schannel_bench` and `struct torture_schannel_bench_conn` hold benchmark state for async `LogonSamLogonEx` loops.

## Control Flow

`torture_rpc_schannel()` loops through workstation and server-trust account types and Schannel modes: auto, 128-bit, AES, and Kerberos variants, each with sign or seal. For each case, `test_schannel()` joins a machine account, parses the configured binding, sets Schannel flags, connects to SAMR, runs SAMR operations, maps the binding to Netlogon, and creates a secondary authenticated Netlogon connection. It checks capabilities, ordinary Netlogon operations, SamLogonEx, and the bug 14932 regression. It then switches transports for LSA operations: named pipe for policy-style LSA, TCP for LookupSids3-style behavior, then restores the original transport.

The same test drops sockets and reconnects to verify that Schannel credentials remain usable across fresh SAMR and Netlogon connections without an explicit new ServerAuthenticate. It then deliberately disables Schannel flags for one Netlogon connection: SamLogonEx must fail as unsafe, while traditional Netlogon operations without a new ServerAuth are still expected to work. Finally it leaves the joined domain.

`torture_rpc_schannel2()` opens two Schannel Netlogon pipes from shallow-copied credentials with independent netlogon credential state cleared, then alternates SamLogonEx calls on both pipes. `torture_rpc_schannel_bench1()` creates one or two workstation joins, opens configurable parallel Schannel Netlogon connections, changes one workstation password after connections are established, verifies new credentials can connect, and runs asynchronous SamLogonEx loops until a time limit expires.

## State and Persistence Behavior

The tests create and delete machine accounts based on `TEST_MACHINE_NAME` plus suffixes. The benchmark changes a workstation account password and updates local credentials. Runtime state includes Schannel credential chains stored in `cli_credentials`, per-pipe Netlogon credential state, async request counters, and temporary NTLM response buffers. No local files are persisted.

Cleanup uses `torture_leave_domain()` for successful paths. Some assertion failures can bypass cleanup in the immediate function scope, relying on the broader torture framework to unwind talloc state and cleanup join contexts.

## Dependencies and Integration Points

The file depends on generated Netlogon, LSA, and SAMR NDR clients; credential and Kerberos helpers; Schannel auth helpers; Netlogon operation helpers from the broader `netlogon.c` torture code; LSA lookup helpers; endpoint mapper and DCERPC binding APIs; and tevent async request handling. It integrates deeply with Samba's machine-account join helpers and with the active test domain's Schannel policy.

## Risks and Edge Cases

These tests are highly policy-sensitive. Kerberos Schannel is skipped for `ncalrpc` and NT4-style domains without a realm. Some LSA identity expectations differ when Schannel maps to anonymous and when testing Samba3. Validation level 6 is only compared when privacy makes it available; otherwise key comparison is skipped.

The benchmark has code risks: `extra_user2` is parsed into `user1_creds` instead of `user2_creds`, and totals are accumulated after `s->conns` is freed, which is a use-after-free pattern. The main Schannel test also resets `tctx->last_result` after an intentional failure path, so later result handling depends on that manual cleanup. As with other domain-joining torture tests, interrupted runs can leave machine accounts or changed machine passwords.

## Test Signals

Pass signals include successful Schannel SAMR/LSA/Netlogon operations across all configured flag combinations, valid Netlogon credential chaining, matching decrypted SamLogonEx session keys between validation levels, expected failure for unsafe non-Schannel SamLogonEx, non-OK anonymous password-set results, independent operation of two Schannel pipes, and sustained async benchmark requests without request errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/schannel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/session_key.c -->
# sources/user-network-fs/samba/source4/torture/rpc/session_key.c

## Purpose

This file defines the `lsa.secrets` torture suite. It verifies that LSA secret encryption and decryption work correctly for many RPC binding/authentication combinations by creating a secret, encrypting a string with the DCERPC transport session key, storing it through `lsa_SetSecret`, querying it back, and decrypting it.

## Important APIs, Types, and Functions

- `init_lsa_String()` initializes generated LSA string wrappers.
- `test_CreateSecret_basic()` creates an LSA secret, obtains the transport session key with `dcerpc_binding_handle_transport_session_key()`, encrypts/decrypts secret values with `sess_encrypt_string()` and `sess_decrypt_string()`, verifies corrupt encrypted data returns `NT_STATUS_UNKNOWN_REVISION`, and validates the round trip.
- `struct secret_settings` carries per-test DCERPC bind flags and NTLMSSP option toggles.
- `test_secrets()` applies settings to loadparm, connects to LSARPC, opens policy, runs the secret round-trip, and deletes the created secret when possible.
- `add_test()` builds descriptive test case names.
- `torture_rpc_lsa_secrets()` registers the full cross product of bind options and boolean auth settings.

## Control Flow

The suite constructor iterates all combinations of `keyexchange`, `ntlm2`, and `lm_key`, and for each combination adds three bind modes: big-endian push, sealed RPC, and no special bind flag. Each tcase calls `test_secrets()` with immutable settings.

`test_secrets()` writes NTLMSSP client options into the torture loadparm context, gets the base binding, applies the requested DCERPC flags, and connects to `ndr_table_lsarpc` using command-line credentials. It opens policy with the shared `test_lsa_OpenPolicy2()` helper, then calls `test_CreateSecret_basic()`.

The secret test creates a random `torturesecret-%08x` name, calls `lsa_CreateSecret`, obtains the session key, encrypts a fixed string, and stores it as the new value. It then mutates the encrypted blob and expects `lsa_SetSecret` to reject the broken value with `NT_STATUS_UNKNOWN_REVISION`. Finally it queries the secret, decrypts the returned buffer with the same session key, and checks the plaintext matches. After the test, `test_secrets()` deletes the secret object if a valid handle remains.

## State and Persistence Behavior

The file creates a live LSA secret on the target server for every test case. It attempts to delete each secret through `lsa_DeleteObject` after validation and warns rather than failing if deletion fails. Local state is transient talloc memory, RPC handles, and loadparm command-line overrides for NTLMSSP options.

## Dependencies and Integration Points

Dependencies include generated LSA RPC bindings, shared LSA policy-open helpers, command-line credentials, loadparm/cmdline configuration, DCERPC binding flag manipulation, and session-key crypto helpers from `libcli/auth`. It integrates with LSARPC policy and secret objects and requires credentials with enough access to create/query/delete secrets.

## Risks and Edge Cases

The test changes global-ish loadparm settings inside the torture context for each case, so ordering matters if future tests reuse the same context without resetting those values. Secret names use `random()` and can theoretically collide. If deletion fails, secrets persist on the server and only a warning is emitted. Some auth combinations may not be accepted by hardened servers, making failures policy-dependent rather than purely functional.

## Test Signals

The strongest signal is successful secret round-trip equality across bind/auth combinations. The corrupt encrypted blob must fail with `NT_STATUS_UNKNOWN_REVISION`; if it succeeds, the server accepted invalid secret crypto framing. Connection/open failures indicate unsupported auth options, missing privileges, or transport-session-key regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/session_key.c -->
