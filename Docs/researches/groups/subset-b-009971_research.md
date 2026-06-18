# subset-b-009971 research

Grouped research for Samba `source4/torture` libnet, libnetapi, libsmbclient, local, locktest, and related manpage files in this work item. Each section preserves the source path as its title and is bounded by reconciliation markers for source-tree-aligned split output.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_domain.c -->
# sources/user-network-fs/samba/source4/torture/libnet/libnet_domain.c

## Purpose
`libnet_domain.c` exercises libnet domain open, close, and list operations over both LSA and SAMR. It validates that high-level `libnet_DomainOpen`, `libnet_DomainClose`, and `libnet_DomainList` calls correctly establish RPC connections, cache handles in `libnet_context`, and handle paged enumeration.

## Important APIs, types, and functions
The local helpers `test_opendomain_samr()` and `test_opendomain_lsa()` manually open domain policy handles through generated DCERPC client stubs. Public torture entry points cover LSA open/close, SAMR open/close, and domain listing. Key structures include `libnet_context`, `libnet_DomainOpen`, `libnet_DomainClose`, `libnet_DomainList`, `policy_handle`, `lsa_String`, `samr_Connect`, `samr_LookupDomain`, `samr_OpenDomain`, and `lsa_OpenPolicy2`.

## Control flow
The open tests initialize a libnet context, attach command-line credentials, derive the workgroup from `lp_ctx`, call the libnet open API, then close the returned handle directly through LSA or SAMR RPC. The close tests perform a lower-level manual open first, populate the matching `ctx->lsa` or `ctx->samr` fields, and then ask `libnet_DomainClose` to close the preloaded state. The list test calls `libnet_DomainList` once with the default buffer and once with a deliberately small SAMR buffer to force multi-round enumeration.

## State and persistence behavior
No directory objects are created. Runtime state is the remote RPC connection, domain policy handles cached inside `libnet_context`, and temporary talloc allocations. Cleanup relies on closing remote handles and freeing the libnet context; failed intermediate paths can leave only server-side RPC context handles until connection teardown.

## Dependencies and integration points
The file integrates libnet with generated `ndr_samr_c` and `ndr_lsa_c` RPC clients, `torture_rpc_binding()`, command-line credentials, and Samba loadparm workgroup settings. It also depends on helpers declared in `torture/libnet/proto.h`.

## Risks and edge cases
Tests require a reachable DC and credentials with enough access to open domain policy handles. The close tests are sensitive to correct transfer of talloc-owned domain names and SIDs into `libnet_context`. The domain list path specifically probes paged enumeration and can expose resume-index or buffer-size regressions.

## Test signals
Success means LSA and SAMR domain handles can be opened and closed through both direct RPC and libnet wrappers, and domain enumeration works in one-shot and small-buffer modes. Failure messages include the exact NTSTATUS for connection, lookup, open, close, or list failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_group.c -->
# sources/user-network-fs/samba/source4/torture/libnet/libnet_group.c

## Purpose
This file validates high-level libnet group APIs for create, info lookup, and paged group listing against a live SAMR/LSA-backed domain.

## Important APIs, types, and functions
`torture_groupinfo_api()` creates a temporary `libnetgrouptest` group with low-level SAMR helpers, calls `libnet_GroupInfo`, and deletes it. `torture_grouplist()` calls `libnet_GroupList` with page size 128 until completion. `torture_creategroup()` calls `libnet_CreateGroup` and cleans up through `test_group_cleanup()`. Shared helpers from `utils.c` provide domain open, group create/delete, SAMR close, and context initialization.

## Control flow
The group-info test manually opens the SAMR domain, creates a group, initializes a libnet context with SAMR/LSA pipes, requests info by group name, then deletes the group and closes the domain handle. The list test loops while `STATUS_MORE_ENTRIES` is returned, carrying `resume_index` forward and printing each group SID. The create test uses the high-level libnet API and then verifies cleanup by deleting the created group over SAMR.

## State and persistence behavior
The tests mutate the domain by creating and deleting `libnetgrouptest`. The list test is read-only but opens SAMR/LSA state in `libnet_context`. Cleanup is explicit; a failure between create and cleanup can leave the test group in the domain until a later run removes it.

## Dependencies and integration points
The file depends on `libnet/libnet.h`, generated SAMR/LSA clients, command-line credentials, loadparm workgroup settings, and helper functions declared in `torture/libnet/proto.h`. It is part of the `smbtorture` libnet suite registered elsewhere.

## Risks and edge cases
Existing stale groups are handled by helper cleanup/recreate logic, but insufficient account-management rights will fail create/delete operations. Listing treats `STATUS_MORE_ENTRIES` and `NT_STATUS_NO_MORE_ENTRIES` as expected terminal signals; regressions in resume handling would show up here.

## Test signals
The file signals that high-level libnet group wrappers can create groups, fetch group info by name, enumerate domain groups, close both SAMR and LSA handles, and clean up persistent directory objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_lookup.c -->
# sources/user-network-fs/samba/source4/torture/libnet/libnet_lookup.c

## Purpose
`libnet_lookup.c` checks libnet name and DC discovery helpers: generic NetBIOS lookup, host lookup, PDC/DC enumeration, and SAM account-name lookup.

## Important APIs, types, and functions
Entry points are `torture_lookup()`, `torture_lookup_host()`, `torture_lookup_pdc()`, and `torture_lookup_sam_name()`. They exercise `libnet_Lookup`, `libnet_LookupHost`, `libnet_LookupDCs`, and `libnet_LookupName` using `libnet_context`, `libnet_Lookup`, `libnet_LookupDCs`, and `libnet_LookupName` request structures.

## Control flow
Each test creates a libnet context, attaches command-line credentials, and chooses the host from `torture:host` or an RPC binding. Name lookup requests are then issued synchronously. The PDC test uses the workgroup as the domain and `NBT_NAME_PDC`; the SAM-name test resolves the hard-coded `Administrator` account in the configured domain.

## State and persistence behavior
These are discovery-only tests. They allocate temporary talloc state and may use resolver or network caches, but they do not change remote directory or file state.

## Dependencies and integration points
The file integrates with Samba resolver context behavior through libnet, with `torture_rpc_binding()` for host fallback, and with loadparm workgroup settings. It also relies on a conventional `Administrator` account existing for `libnet_LookupName`.

## Risks and edge cases
Tests are sensitive to NetBIOS/DNS configuration, domain naming, and whether the test environment exposes PDC records. Hard-coding `Administrator` can fail in unusual domains where the account is renamed, hidden, or inaccessible to the test credentials.

## Test signals
Passing tests indicate that libnet can resolve host addresses, discover PDC/DC candidates, and resolve an account name to SAM identity data using the configured credentials and domain context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_rpc.c -->
# sources/user-network-fs/samba/source4/torture/libnet/libnet_rpc.c

## Purpose
This file tests `libnet_RpcConnect` across multiple connection levels and interfaces, including expected authentication failures for deliberately bad credentials.

## Important APIs, types, and functions
`test_connect_service()` is the core checker for one interface and connection mode. `torture_rpc_connect()` runs LSA, SAMR, and SRVSVC success cases plus LSA/SAMR bad-credential failures. Public entry points select `LIBNET_RPC_CONNECT_SERVER`, `PDC`, `DC`, `DC_INFO`, or `BINDING`. Key inputs are NDR interface tables for LSARPC, SAMR, and SRVSVC.

## Control flow
The wrapper creates a libnet context with command-line credentials, then calls `libnet_RpcConnect` repeatedly. Success paths expect `NT_STATUS_OK`; bad credential paths rewrite the credential object to `baduser`/`badpassword` and expect `NT_STATUS_LOGON_FAILURE`. The DC-info mode prints returned domain name, SID, realm, and GUID.

## State and persistence behavior
Remote state is not modified. The test mutates the in-memory credential object when checking bad credentials, so later checks in the same context would inherit the bad username/password unless ordered carefully. The current ordering puts bad-credential checks last.

## Dependencies and integration points
The file binds libnet to generated RPC interface tables, `torture_rpc_binding()` for host/binding strings, loadparm workgroup settings for DC/PDC discovery, and Samba credential APIs.

## Risks and edge cases
Credential mutation is intentionally destructive within the test context. Some servers can map authentication failures differently, and environments with anonymous or guest fallback could obscure expected `LOGON_FAILURE`. DC/PDC modes depend on domain discovery rather than a direct server binding.

## Test signals
Passing output shows that libnet can connect to LSA, SAMR, and SRVSVC at each supported selection level, and that authentication failures propagate as expected instead of being treated as transport success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_share.c -->
# sources/user-network-fs/samba/source4/torture/libnet/libnet_share.c

## Purpose
`libnet_share.c` exercises libnet SRVSVC share listing and share deletion, with a direct RPC helper used to create a temporary share before deletion.

## Important APIs, types, and functions
`test_displayshares()` prints `libnet_ListShares` results for SRVSVC info levels 0, 1, 2, 501, and 502. `torture_listshares()` calls `libnet_ListShares` for each level. `test_addshare()` directly calls `dcerpc_srvsvc_NetShareAdd_r` with a `srvsvc_NetShareInfo2`. `torture_delshare()` then calls `libnet_DelShare` for `libnetsharetest`.

## Control flow
The list test resolves the target host from the torture RPC binding, creates a libnet context, and loops through supported enumeration levels. The deletion test connects to SRVSVC, creates a disk-tree share pointing at `C:\WINDOWS\TEMP`, then requests deletion through libnet.

## State and persistence behavior
Listing is read-only. The delete test persists a temporary server share and removes it, so failure after `NetShareAdd` can leave `libnetsharetest` registered on the server. The test assumes a Windows-like path and administrative share-management privileges.

## Dependencies and integration points
The file depends on generated SRVSVC clients, libnet share APIs, command-line credentials, and `torture_rpc_connection()`. It integrates with server service semantics rather than SAMR/LSA domain state.

## Risks and edge cases
`test_addshare()` only checks transport NTSTATUS, not the embedded SRVSVC result field, so share-add semantic failures may be underreported. The hard-coded `C:\WINDOWS\TEMP` path is Windows-centric and may not map on Samba servers without suitable configuration.

## Test signals
The list test confirms each share info level can be fetched and decoded. The delete test confirms libnet can remove a share created by raw SRVSVC calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_user.c -->
# sources/user-network-fs/samba/source4/torture/libnet/libnet_user.c

## Purpose
This file tests high-level libnet user account APIs for create, delete, modify, info, and paged listing against a live domain.

## Important APIs, types, and functions
Entry points are `torture_createuser()`, `torture_deleteuser()`, `torture_modifyuser()`, `torture_userinfo_api()`, and `torture_userlist()`. `set_test_changes()` builds randomized `libnet_ModifyUser` changes for account name, full name, description, home directory/drive, comment, logon script, profile path, expiry, and account flags. Verification uses `libnet_UserInfo` and macros for string, time, and numeric fields.

## Control flow
Create and delete tests combine low-level helper setup with high-level libnet calls. The modify test creates `libnetusertest`, then walks every field in `usertest.h`, applying one change at a time and reading the user back to compare. `torture_userinfo_api()` creates a user and queries it by name through `libnet_UserInfo`. The user-list test pages through `libnet_UserList` with resume indexes and closes both SAMR and LSA handles.

## State and persistence behavior
The tests create, rename, modify, and delete domain users. Because account-name changes can rename the test user, cleanup must use the original RDN-aware helper that can query LDAP for `sAMAccountName`. Failed modification or cleanup can leave test users with randomized attributes in the directory.

## Dependencies and integration points
This file relies on `utils.c` helper functions, `usertest.h` field definitions and test string patterns, SAMR/LSA generated RPC clients, command-line credentials, and loadparm workgroup settings. It validates high-level libnet APIs against direct SAMR-created setup state.

## Risks and edge cases
Randomized field values and account renames make cleanup fragile. Time comparison requires exact round-trip conversion. Account flags must match server-side normalization. Required privileges are high because the tests create, modify, delete, and enumerate users.

## Test signals
The strongest signal is the per-field modify loop: each libnet user modification is immediately checked through `libnet_UserInfo`. Listing also verifies resume-driven account enumeration and handle close behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/libnet_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/python/samr-test.py -->
# sources/user-network-fs/samba/source4/torture/libnet/python/samr-test.py

## Purpose
This Python test verifies the Samba Python `net.SetPassword()` binding for a supplied account and new password.

## Important APIs, types, and functions
The `Libnet_SetPwdTest` class derives from `samba.tests.TestCase` and contains `test_SetPassword()`. It uses `self.get_credentials()` and `samba.net.Net.SetPassword` with `account_name`, the credential domain, the new password, and the current credentials.

## Control flow
At import time the script requires `ACCOUNT_NAME` and `NEW_PASS` environment variables. The test runner supplies credentials, then the single test calls `net.SetPassword()` and relies on exceptions to fail the case.

## State and persistence behavior
The test persistently changes the password of the named account. It does not restore the old password and is therefore intended for controlled accounts only.

## Dependencies and integration points
It integrates Samba's Python modules, `subunitrun`, and command-line credentials. The usage comment documents expected `PYTHONPATH`, `SUBUNITRUN`, and credential invocation.

## Risks and edge cases
Missing environment variables abort the module before tests run. Running against a real user account changes authentication state. Password policy, account lockout, insufficient rights, or mismatched credential domains can fail the test.

## Test signals
Success indicates that the Python libnet SAMR password-set path can authenticate with supplied credentials and update the target account password.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/python/samr-test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/userinfo.c -->
# sources/user-network-fs/samba/source4/torture/libnet/userinfo.c

## Purpose
`userinfo.c` tests the lower-level `libnet_rpc_userinfo` API, both synchronous and asynchronous, using SID and username inputs.

## Important APIs, types, and functions
`test_userinfo()` calls `libnet_rpc_userinfo` at level 5 by SID and by username. `test_userinfo_async()` calls `libnet_rpc_userinfo_send`/`recv` at level 10 and passes `msg_handler` for monitor messages. `torture_userinfo()` creates the domain/user setup and runs both modes.

## Control flow
The test connects to SAMR, opens the domain, creates `libnetuserinfotest`, derives the user SID by adding the created RID to the domain SID, and queries by SID then name. It deletes the user, repeats the setup, and exercises the async send/recv path.

## State and persistence behavior
The file creates and deletes a domain user twice. Runtime state includes SAMR handles, generated SIDs, composite async contexts, and monitor callbacks. Cleanup is explicit but can leave the test account if a failure occurs before delete.

## Dependencies and integration points
The file uses helpers from `utils.c`, generated SAMR stubs, `libcli/security` SID helpers, and `msg_handler()` for async monitor output. It is a lower-level complement to the high-level user API tests in `libnet_user.c`.

## Risks and edge cases
The SID path depends on correct RID return from SAMR create. Async testing requires the event context and composite context to be valid. The fixed username can collide with stale accounts from prior failed runs.

## Test signals
Passing tests confirm sync and async user-info calls work for SID-based and username-based lookup forms and that monitor callbacks do not break the async path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/userinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/userman.c -->
# sources/user-network-fs/samba/source4/torture/libnet/userman.c

## Purpose
`userman.c` tests lower-level SAMR-backed libnet RPC helpers for user add, async user add, user delete, user modify, and user info comparison.

## Important APIs, types, and functions
The file wraps `libnet_rpc_useradd`, `libnet_rpc_useradd_send`/`recv`, `libnet_rpc_usermod`, `libnet_rpc_userdel`, and `libnet_rpc_userinfo`. `test_usermod()` builds randomized changes with explicit `USERMOD_FIELD_*` flags. `test_compare()` reads info level 21 and checks only fields that were requested to change.

## Control flow
`torture_useradd()` opens a domain, tests sync add and cleanup, reopens, tests async add, and cleans up again. `torture_userdel()` pre-creates a user through raw SAMR and deletes it through `libnet_rpc_userdel`. `torture_usermod()` creates a user, repeatedly applies increasingly many random changes, then compares the resulting SAMR info record against the requested modifications.

## State and persistence behavior
The tests create, delete, rename, and modify a domain user. The current username variable can change when the account-name field is modified, while cleanup still targets the original test RDN via helper logic. Failed cleanup can leave modified domain users behind.

## Dependencies and integration points
This file depends on `usertest.h`, shared libnet torture helpers, SAMR generated clients, `msg_handler` monitor output, and Samba time conversion helpers. It exercises lower-level RPC-oriented libnet APIs rather than the high-level domain-name wrappers.

## Risks and edge cases
Random field selection can skip duplicates through `continue_if_field_set`, making test coverage probabilistic for multi-change calls. Time field round trips can be fragile. Account rename requires later operations to follow the new name accurately.

## Test signals
Success indicates sync/async add, delete, modify, and info APIs work at the RPC helper level and that SAMR info level 21 reflects requested user modifications.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/userman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/usertest.h -->
# sources/user-network-fs/samba/source4/torture/libnet/usertest.h

## Purpose
This header centralizes test usernames, user-modification field enumeration, duplicate-field skipping logic, and string templates shared by libnet user tests.

## Important APIs, types, and functions
It defines `TEST_USERNAME`, `continue_if_field_set(field)`, `USER_FIELD_FIRST`, `USER_FIELD_LAST`, enum `test_fields`, and templates such as `TEST_CHG_ACCOUNTNAME`, `TEST_CHG_DESCRIPTION`, `TEST_CHG_FULLNAME`, `TEST_CHG_COMMENT`, and `TEST_CHG_PROFILEPATH`.

## Control flow
The header has no standalone control flow. `libnet_user.c` and `userman.c` iterate from `USER_FIELD_FIRST` to `USER_FIELD_LAST` and use enum values to choose which account property to modify.

## State and persistence behavior
No state is stored in the header, but its fixed username and generated account-name templates determine persistent domain objects created by the tests.

## Dependencies and integration points
The enum names must match fields and bit flags used by `libnet_ModifyUser` and `libnet_rpc_usermod` test code. The macro assumes the caller is inside a loop with an `i` loop variable.

## Risks and edge cases
The `continue_if_field_set` macro mutates `i`, so it is tightly coupled to callers and can be surprising if reused elsewhere. Fixed names increase collision risk after failed test cleanup.

## Test signals
The header indirectly drives coverage for all user modification fields in the high-level and lower-level libnet user tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/usertest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/utils.c -->
# sources/user-network-fs/samba/source4/torture/libnet/utils.c

## Purpose
`utils.c` provides shared SAMR/LSA and LDAP helper functions for libnet torture tests, including domain open, user/group create and cleanup, handle close, libnet context initialization, and monitor-message printing.

## Important APIs, types, and functions
`test_domain_open()` performs SAMR connect, domain lookup, and open. `_get_account_name_for_user_rdn()` uses LDAP/LDB to find `sAMAccountName` for a user RDN. `test_user_cleanup()` and `test_group_cleanup()` delete accounts through SAMR. `test_user_create()` and `test_group_create()` create accounts and recover from existing stale objects. `test_samr_close_handle()`, `test_lsa_close_handle()`, `test_libnet_context_init()`, and `msg_handler()` support common test setup and async diagnostics.

## Control flow
Domain open establishes a SAMR connection handle, looks up the domain SID, opens a domain handle, optionally returns the SID, and closes the connect handle. Account cleanup resolves names to RIDs, opens the user or group, and deletes it. Create helpers retry by deleting stale users/groups if the server returns already-exists. Context initialization optionally opens SAMR and LSA pipes and stores their binding handles in `libnet_context`.

## State and persistence behavior
The helpers mutate persistent directory state by creating and deleting users and groups. `_get_account_name_for_user_rdn()` opens an LDAP connection to the configured host but is read-only. Handles are remote state and must be explicitly closed; helper failures can leave accounts or handles until connection teardown.

## Dependencies and integration points
The file integrates SAMR/LSA generated RPC clients, `ldb_wrap_connect`, command-line credentials, torture RPC connection helpers, loadparm settings, and monitor message types from libnet. It is the foundation for most files in `source4/torture/libnet`.

## Risks and edge cases
Cleanup correctness depends on LDAP lookup finding the right `sAMAccountName`, especially after account renames. Recreate-on-exists logic is useful for stale state but dangerous if a fixed test name collides with a real account. Context setup returns partially initialized state on connection failures only after freeing the context.

## Test signals
Helper success is a prerequisite for user, group, and domain libnet tests. The functions also verify direct SAMR create/delete/open/close behavior while supporting higher-level libnet API checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnet/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi.c -->
# sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi.c

## Purpose
This file initializes libnetapi torture support and registers the `netapi` smbtorture suite.

## Important APIs, types, and functions
`torture_libnetapi_init_context()` loads the torture smb.conf, loads interfaces, retrieves command-line credentials, and calls `libnetapi_net_init`. `torture_libnetapi_initialize()` checks that `libnetapi_init()` succeeds when a context is already set up. `torture_libnetapi_init()` registers server, group, user, and initialize tests.

## Control flow
Context initialization first forces `lp_load_global()` using the test config path, then creates a source3 libnetapi context bound to the source4 torture loadparm context and credentials. Suite initialization builds a `torture_suite`, adds simple tests, sets a description, and registers it.

## State and persistence behavior
The file mainly manages in-memory context state. It may affect process-global configuration by loading smb.conf and interfaces. It does not directly mutate remote server state.

## Dependencies and integration points
It bridges source4 `smbtorture` to source3 `libnetapi`, `netapi_private`, command-line credentials, and global loadparm/interface initialization. Other libnetapi test files depend on `torture_libnetapi_init_context()`.

## Risks and edge cases
Incorrect config loading can cause all NetAPI tests to fail before network calls. The function's return type is `bool` but returns `W_ERROR_V(WERR_GEN_FAILURE)` on one failure path, which works as truthiness only if interpreted carefully.

## Test signals
The initialize test confirms that pre-initialized libnetapi contexts can be passed through `libnetapi_init` without losing the context, and suite registration exposes all NetAPI subtests under `smbtorture`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_group.c -->
# sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_group.c

## Purpose
`libnetapi_group.c` tests source3 NetAPI group management from smbtorture: add/delete, enumeration, info query/set, membership add/delete/set, and buffer alignment.

## Important APIs, types, and functions
Alignment helpers check `GROUP_INFO_0..3` and `GROUP_USERS_INFO_0..1`. `test_netgroupenum()`, `test_netgroupgetusers()`, and `test_netgroupsetusers()` wrap paged enumeration and membership APIs. `torture_libnetapi_group()` orchestrates `NetGroupAdd`, `NetGroupEnum`, `NetGroupGetInfo`, `NetGroupSetInfo`, `NetGroupAddUser`, `NetGroupDelUser`, `NetGroupSetUsers`, `NetUserDel`, and `NetGroupDel`.

## Control flow
The test deletes stale user/group names, creates a group, verifies a second add fails, enumerates the new group across levels 0-3, queries info levels, optionally renames the group via level 0 set-info, creates a user using `test_netuseradd()`, checks non-membership, adds and removes membership, sets membership explicitly, deletes the user and group, then verifies the group no longer exists.

## State and persistence behavior
It persistently creates and deletes `torture_test_group`, optional `torture_test_group2`, and `torture_test_user`. Cleanup occurs at the beginning and during normal success flow; failures can leave objects behind until a later run's initial cleanup.

## Dependencies and integration points
The file uses public `<netapi.h>` calls, libnetapi error formatting, the shared `torture_libnetapi_init_context()`, `test_netuseradd()` from `libnetapi_user.c`, and alignment helpers from `lib/util/alignment.h`.

## Risks and edge cases
Some NetAPI calls are accepted as unsupported/not implemented for specific levels, so status handling must distinguish expected gaps from failures. Membership checks are case-insensitive. Alignment checks guard ABI correctness of returned buffers.

## Test signals
Passing tests show group lifecycle and membership APIs work across several info levels, returned buffers are correctly aligned, resume handles enumerate all results, and deleted groups become unqueryable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_server.c -->
# sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_server.c

## Purpose
This file provides a small NetAPI server test focused on `NetRemoteTOD`.

## Important APIs, types, and functions
`torture_libnetapi_server()` initializes a libnetapi context, fetches the target host from torture settings, calls `NetRemoteTOD` once, then calls it ten more times while freeing each returned buffer with `NetApiBufferFree`.

## Control flow
After context initialization, the test performs the time-of-day call, validates status, frees the buffer, loops ten times to catch repeated allocation/free or connection reuse issues, and reports a formatted libnetapi error on failure.

## State and persistence behavior
The test is read-only on the remote server. It allocates and frees NetAPI buffers and a libnetapi context.

## Dependencies and integration points
It depends on `<netapi.h>`, `torture_libnetapi_init_context()`, and `libnetapi_get_error_string()`. It is registered by `libnetapi.c` as the `server` subtest.

## Risks and edge cases
The test requires the target host setting and server support for remote time-of-day queries. Repeated calls mainly catch memory-management or context reuse regressions.

## Test signals
Success means `NetRemoteTOD` works reliably through libnetapi and returned buffers can be freed repeatedly without API errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_user.c -->
# sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_user.c

## Purpose
`libnetapi_user.c` tests source3 NetAPI user management from smbtorture, including add/delete, enumeration, info query/set, group membership lookup, and user modals.

## Important APIs, types, and functions
`test_netuserenum()` enumerates users for levels 0, 1, 2, 3, 4, 10, 11, 20, and 23. `test_netuseradd()` creates a normal user with `USER_INFO_1`. `test_netusermodals()` gets levels 0-3, writes level 0 back, and verifies the struct is unchanged. `test_netusergetgroups()` validates group-list returns for levels 0 and 1. `torture_libnetapi_user()` drives the full lifecycle.

## Control flow
The main test deletes stale users, adds `torture_testuser`, confirms enumeration at all supported levels, queries info levels, checks group lookup, modifies the comment using `USER_INFO_1007`, queries again, renames using `USER_INFO_0`, deletes the renamed account, verifies it is gone, then tests user modals.

## State and persistence behavior
It creates, renames, modifies, and deletes `torture_testuser` and `torture_testuser2`. The modal test reads and writes domain user policy level 0 back to the server, which should be idempotent but is still a persistent write path.

## Dependencies and integration points
The file uses public NetAPI calls from `<netapi.h>`, libnetapi context/error helpers, and exposes `test_netuseradd()` for group tests. It depends on account-management privileges and host configuration.

## Risks and edge cases
Info levels returning status 124 are treated as acceptable unimplemented cases. The fixed password must satisfy server policy. User rename and modal set operations require more privilege than read-only enumeration.

## Test signals
Passing tests show NetUser lifecycle operations, enumeration levels, comment mutation, rename/delete semantics, group lookup, and modal get/set round trips function through libnetapi.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/wscript_build -->
# sources/user-network-fs/samba/source4/torture/libnetapi/wscript_build

## Purpose
This Waf build fragment defines the internal smbtorture module for libnetapi tests.

## Important APIs, types, and functions
It calls `bld.SAMBA_MODULE('TORTURE_LIBNETAPI', ...)` with sources `libnetapi.c`, `libnetapi_user.c`, `libnetapi_group.c`, and `libnetapi_server.c`, autogenerates `proto.h`, sets subsystem `smbtorture`, and names `torture_libnetapi_init` as the init function.

## Control flow
At build configuration time, Waf consumes this module declaration to compile the listed sources into an internal smbtorture module.

## State and persistence behavior
The file does not manage runtime state. Build artifacts and generated prototypes are its persistent output.

## Dependencies and integration points
Declared dependencies are `netapi` and `CMDLINE_S4`, which connect these source4 torture tests to source3 libnetapi and command-line credential support.

## Risks and edge cases
Missing a source file or dependency here would make tests unavailable or fail at link time. The module is internal, so it is expected to be loaded through smbtorture rather than installed as a standalone binary.

## Test signals
Successful build and module registration expose the `netapi` suite and ensure all three functional NetAPI test files are compiled together.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libnetapi/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libsmbclient/libsmbclient.c -->
# sources/user-network-fs/samba/source4/torture/libsmbclient/libsmbclient.c

## Purpose
This large smbtorture module validates the public `libsmbclient` C API: context lifecycle, configuration setters, URL parsing, directory enumeration, file operations, metadata, xattrs, no-anonymous behavior, rename semantics, and SMB3 POSIX extension behavior.

## Important APIs, types, and functions
`torture_libsmbclient_init_context()` creates and configures an `SMBCCTX` with command-line workgroup/user, auth callback, debug settings, and optional client protocol. Pure API tests cover `smbc_version`, `smbc_new_context`, `smbc_init_context`, `smbc_setLogCallback`, `smbc_setConfiguration`, basic getters/setters, and many `smbc_setOption*`/`smbc_getOption*` pairs. Network tests use `smbc_opendir`, `smbc_readdir`, `smbc_readdirplus`, `smbc_readdirplus2`, `smbc_getdents`, `smbc_telldir`, `smbc_lseekdir`, `smbc_creat`, `smbc_open`, `smbc_close`, `smbc_unlink`, `smbc_mkdir`, `smbc_rmdir`, `smbc_stat`, `smbc_fstat`, `smbc_utimes`, `smbc_rename`, `smbc_getxattr`, and `smbc_fgetxattr`.

## Control flow
The module registers many simple tests under the `libsmbclient` suite. Some tests are local API checks; others require `torture:smburl`. Directory tests create temporary files, enumerate shares or directories, verify returned entries, test seeking back to saved directory offsets, and compare `readdir`, `getdents`, `readdirplus`, `readdirplus2`, and `stat` results. Metadata tests verify `utimes`, missing-file `ENOENT`, xattr sizing, and POSIX extension xattrs. The POSIX hardlink test opens a prepared file and checks its POSIX stat info reports three hardlinks.

## State and persistence behavior
The suite creates and deletes files and directories on the configured SMB share, including `test_readdirplus.txt`, `rd_seek` with 100 files, `src`, `dst`, `getxattr`, and POSIX fixture paths. `smbc_setConfiguration()` temporarily mutates process-global loadparm settings and restores the default config file afterward. Context state is process-local and freed per test.

## Dependencies and integration points
The file depends on `<libsmbclient.h>`, command-line credentials, loadparm globals, dynamic config paths, SMB protocol constants, and smbtorture helpers. It integrates with actual SMB server behavior through `torture:smburl` and with POSIX extension support through SMB3 xattrs.

## Risks and edge cases
Many tests require a writable share and sufficient credentials. Directory-order seeking assumes an open handle's in-memory list remains stable. The rename test documents a prior SMB2 overwrite bug. POSIX tests require a server/share prepared with POSIX extensions and a file with expected hardlink count. Some cleanup paths free contexts but do not always close every possible handle after early assertion failures.

## Test signals
Passing tests provide broad confidence that libsmbclient context APIs work, network file operations round-trip correctly, directory cursor APIs are consistent, stat metadata matches `readdirplus2`, xattr behavior reports sizes and errors properly, anonymous fallback can be disabled, and SMB3 POSIX extension metadata is exposed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libsmbclient/libsmbclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libsmbclient/wscript_build -->
# sources/user-network-fs/samba/source4/torture/libsmbclient/wscript_build

## Purpose
This Waf build fragment defines the internal smbtorture module for libsmbclient API tests.

## Important APIs, types, and functions
It declares `bld.SAMBA_MODULE('TORTURE_LIBSMBCLIENT', ...)` with source `libsmbclient.c`, generated `proto.h`, subsystem `smbtorture`, init function `torture_libsmbclient_init`, and dependencies `smbclient CMDLINE_S4`.

## Control flow
During build, Waf compiles the libsmbclient torture source and links it into smbtorture as an internal module.

## State and persistence behavior
No runtime state is handled. Persistent outputs are build artifacts and generated prototypes.

## Dependencies and integration points
The declared `smbclient` dependency supplies libsmbclient APIs, while `CMDLINE_S4` supplies torture command-line credential integration.

## Risks and edge cases
If the dependency list misses libraries used by POSIX, loadparm, or credentials code, the module can fail at link time. Since all tests are in one source file, excluding it removes the entire suite.

## Test signals
Successful module build and registration expose the `libsmbclient` suite in smbtorture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/libsmbclient/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/dbspeed.c -->
# sources/user-network-fs/samba/source4/torture/local/dbspeed.c

## Purpose
`dbspeed.c` benchmarks and sanity-checks TDB and LDB lookup performance for SID/UID-style records in local smbtorture tests.

## Important APIs, types, and functions
`tdb_add_record()` inserts string key/value pairs. `test_tdb_speed()` creates `test.tdb`, inserts SID-to-UID and UID-to-SID records, repeatedly fetches random pairs, and stores global `tdb_speed`. `ldb_add_record()` inserts one SID DN with a UID attribute. `test_ldb_speed()` creates `test.ldb`, adds an index, inserts records, performs base and indexed subtree searches, checks talloc block counts, and reports speed relative to TDB. `torture_local_dbspeed()` registers both tests.

## Control flow
The TDB test runs first and sets `tdb_speed`. The LDB test then computes its own rate and prints the LDB/TDB ratio. Both use `torture_entries` and `torture:timelimit` to control dataset size and duration.

## State and persistence behavior
The tests create local `test.tdb` and `test.ldb` files in the current directory and unlink them on success or failure. The only cross-test state is the global `tdb_speed`.

## Dependencies and integration points
The file depends on tdb, ldb, `ldb_wrap_connect`, `tdb_wrap_open`, loadparm TDB flags, and smbtorture local suite registration.

## Risks and edge cases
The LDB ratio assumes the TDB test ran first. Performance results depend on filesystem, random seed, `torture_entries`, and `timelimit`. The talloc block-count leak heuristic is coarse and can break if LDB internals change allocation behavior.

## Test signals
Passing tests show records can be inserted and fetched through TDB and LDB, UID indexing works for subtree searches, and no obvious allocation growth occurs during add/search loops.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/dbspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/fsrvp_state.c -->
# sources/user-network-fs/samba/source4/torture/local/fsrvp_state.c

## Purpose
This file tests persistence and retrieval of File Server Remote VSS Protocol state used by Samba's FSRVP server.

## Important APIs, types, and functions
It builds `fss_global`, `fss_sc_set`, `fss_sc`, and `fss_sc_smap` structures, then calls `fss_state_store()` and `fss_state_retrieve()`. Helper constructors create random GUID-backed shadow-copy sets, shadow copies, and share mappings. Compare helpers validate GUIDs, strings, states, contexts, timestamps, counts, and linked-list membership.

## Control flow
`test_fsrvp_state_empty()` stores and retrieves an empty state file. `test_fsrvp_state_single()` builds a one-set/one-copy/one-share-map hierarchy and compares after retrieval. `test_fsrvp_state_multi()` builds multiple sets, copies, and mappings and compares order-insensitively by GUID/share name. `test_fsrvp_state_none()` retrieves from a missing state path and expects an empty result. `torture_local_fsrvp()` registers the cases.

## State and persistence behavior
Each test creates a temporary directory with `mkdtemp`, writes an FSRVP TDB state file named by `FSS_DB_NAME`, retrieves it into a fresh memory context, then unlinks the file and removes the directory. The persisted state includes IDs, state enums, context values, volume paths, timestamps, and share mappings.

## Dependencies and integration points
The file depends on `source3/rpc_server/fss/srv_fss_private.h`, FSRVP NDR types, dlinklist helpers, NTSTATUS assertions, and smbtorture local registration. It directly validates private FSS state serialization used by the RPC server.

## Risks and edge cases
The tests require temporary directory cleanup to succeed and use wall-clock `time(NULL)` for timestamps. Comparisons rely on unique GUIDs/share names to match list entries. `torture_local_fsrvp()` creates a stackframe because dbwrap uses `talloc_tos()`.

## Test signals
Passing tests indicate empty, absent, simple, and complex FSRVP state trees survive store/retrieve cycles with structure and values intact.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/fsrvp_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/local.c -->
# sources/user-network-fs/samba/source4/torture/local/local.c

## Purpose
`local.c` is the registration hub for Samba-specific local smbtorture suites.

## Important APIs, types, and functions
The `suite_generators` array lists local suite factory functions for binding strings, crypto, messaging, utility libraries, NDR/TDR, registry, NSS, FSRVP, mdspkt, and many others. `torture_local_init()` creates the top-level `local` suite, adds direct `talloc`, `replace`, and `crypto.md4` tests, then adds every generated sub-suite.

## Control flow
Smbtorture calls `torture_local_init()` during module initialization. The function iterates until the NULL sentinel in `suite_generators`, attaches each child suite, sets a description, and registers the top-level suite.

## State and persistence behavior
This file only builds suite metadata in memory. Runtime state and persistence belong to the child tests.

## Dependencies and integration points
It integrates many local test subsystems through generated proto headers and module init registration. It is the single entry point for the `TORTURE_LOCAL` module built by `local/wscript_build`.

## Risks and edge cases
Adding a generator without linking its implementation breaks the module. The order matters where child suites have implicit dependencies, such as dbspeed's TDB result before LDB ratio inside that child suite.

## Test signals
Successful initialization means all listed local test suites are reachable under `smbtorture local`, providing broad local coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/mdspkt.c -->
# sources/user-network-fs/samba/source4/torture/local/mdspkt.c

## Purpose
This file tests mdssvc packet unmarshalling for a fixture containing an empty CNID file-metadata structure.

## Important APIs, types, and functions
The fixture bytes are `mdspkt_empty_cnid_fm`, with expected textual dump `mdspkt_empty_cnid_fm_dump`. `test_mdspkt_empty_cnid_fm()` uses `dalloc_new`, `sl_unpack`, `dalloc_get`, `dalloc_size`, and `dalloc_dump`. `torture_local_mdspkt()` registers the test.

## Control flow
The test unpacks the fixture into a DALLOC tree, retrieves the `sl_cnids_t` node, asserts the CNID array has size zero, dumps the tree, and compares the dump exactly against the expected string.

## State and persistence behavior
No persistent state is written. All state is an in-memory DALLOC tree allocated under the torture context and freed at the end.

## Dependencies and integration points
It depends on `mdssvc/marshalling.h`, DALLOC helpers, Samba data-blob utilities, and the local smbtorture suite.

## Risks and edge cases
The exact dump string makes the test sensitive to formatting changes in `dalloc_dump`, not just decoding behavior. The fixture specifically covers empty CNIDs, so non-empty packet cases are not exercised here.

## Test signals
Passing confirms the mdssvc marshaller can parse the fixture, represent empty CNID arrays correctly, and emit the expected diagnostic tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/mdspkt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/nss_tests.c -->
# sources/user-network-fs/samba/source4/torture/local/nss_tests.c

## Purpose
`nss_tests.c` validates NSS wrapper/user-group lookup consistency for passwd and group APIs, reentrant variants, membership expansion, and duplicate names.

## Important APIs, types, and functions
Helpers copy and print `struct passwd` and `struct group`, wrap `getpwnam`, `getpwnam_r`, `getpwuid`, `getpwuid_r`, `getgrnam`, `getgrnam_r`, `getgrgid`, `getgrgid_r`, `getpwent`, `getpwent_r`, `getgrent`, `getgrent_r`, and `getgrouplist`. Assertion helpers compare passwd/group records. Top-level tests cover enumeration, reentrant enumeration, cross-checks between reentrant and non-reentrant APIs, membership, and duplicate detection.

## Control flow
The enumeration tests require `NSS_WRAPPER_PASSWD` and `NSS_WRAPPER_GROUP`; otherwise they skip. They enumerate all users/groups, then verify each enumerated item can be retrieved by name and ID with matching fields. Membership compares `getgrouplist()` output to group membership lists, with documented skips for known local users and only full support for `ENVNAME=ad_member_idmap_rid:local`.

## State and persistence behavior
The tests are read-only against NSS databases. They allocate copied passwd/group records under the torture context and rely on environment variables pointing at wrapper files.

## Dependencies and integration points
The file depends on system NSS APIs through Samba replacement headers, optional platform macros for reentrant enumeration, environment variables from the selftest harness, and the local suite registry.

## Risks and edge cases
Behavior varies by platform: macOS may lack reentrant enumeration and Solaris has different function signatures. Membership tests document known AD member discrepancies and skip unsupported environments. Duplicate detection is O(n^2) but acceptable for test fixtures.

## Test signals
Passing tests show NSS wrapper enumeration is internally consistent, reentrant and non-reentrant calls agree, group membership expansion matches group lists for supported environments, and no duplicate user or group names are present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/nss_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/smbtorture_fullname.c -->
# sources/user-network-fs/samba/source4/torture/local/smbtorture_fullname.c

## Purpose
This tiny file creates a deliberately nested local smbtorture suite to exercise full test-name handling.

## Important APIs, types, and functions
`test_smbtorture_always_pass()` always returns true. `torture_local_smbtorture()` creates suites `smbtorture`, `level1`, `level2`, and `level3`, nests them, and adds `always_pass` at the deepest level.

## Control flow
Suite construction creates a three-level hierarchy, attaches child suites from deepest to top-level, and returns the root suite to `local.c`.

## State and persistence behavior
Only in-memory suite metadata is created. No external state is read or written.

## Dependencies and integration points
The file integrates with the local suite registry and smbtorture's naming/reporting logic.

## Risks and edge cases
The useful behavior is in the harness: regressions would show as incorrect fully qualified names or failure to run nested tests.

## Test signals
The always-pass test confirms deeply nested suite registration and reporting can execute a leaf test successfully.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/smbtorture_fullname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/torture.c -->
# sources/user-network-fs/samba/source4/torture/local/torture.c

## Purpose
`torture.c` tests core smbtorture utility behavior: temporary directory creation and bare domain provisioning.

## Important APIs, types, and functions
`test_tempdir()` calls `torture_temp_dir()` and verifies `directory_exist()`. `test_provision()` builds a `provision_settings` struct and calls `provision_bare()`, then checks the returned domain DN. `torture_local_torture()` registers both tests.

## Control flow
The tempdir test requests a named temporary directory under the torture context. The provision test creates a temp target directory, fills domain/realm/site/machine settings, provisions a bare database, and validates `result.domaindn`.

## State and persistence behavior
Both tests create local filesystem state under temporary directories. The provision test creates a bare Samba provision tree/database in its temp target, owned by the test context.

## Dependencies and integration points
The file depends on raw SMB utility headers only lightly, `torture/util.h`, and `param/provision.h`. It is registered under the local smbtorture suite.

## Risks and edge cases
Provisioning depends on Python/build support and local filesystem permissions. Settings are minimal and use hard-coded domain values; failures can indicate provision code regressions rather than harness issues.

## Test signals
Passing tests show the torture harness can allocate temp directories and that bare provisioning produces the expected domain DN.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/torture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/verif_trailer.c -->
# sources/user-network-fs/samba/source4/torture/local/verif_trailer.c

## Purpose
This file tests DCE/RPC security verification trailer parsing and presentation-context validation using a captured FSRVP verification trailer blob.

## Important APIs, types, and functions
It defines fixture `test_vt`, expected abstract and transfer syntax strings, and `test_verif_trailer_pctx()`. The test uses `ndr_pull_init_blob`, `ndr_pop_dcerpc_sec_verification_trailer`, `ndr_print_dcerpc_sec_verification_trailer`, `ndr_syntax_id_from_string`, and `dcerpc_sec_verification_trailer_check`.

## Control flow
The test wraps the byte fixture in a `DATA_BLOB`, pulls an NDR verification trailer, prints it through an NDR printer, builds expected syntax IDs, and checks that the trailer matches the expected presentation context.

## State and persistence behavior
All state is in-memory fixture data and parsed NDR structures. No files or remote state are touched.

## Dependencies and integration points
It depends on DCE/RPC NDR definitions, RPC common verification-trailer helpers, and local smbtorture suite registration. The fixture originated from an FSRVP request.

## Risks and edge cases
The test only covers one trailer shape. It checks parsing and context matching but not negative cases or malformed trailers.

## Test signals
Passing confirms the verification trailer parser can decode the fixture and that presentation-context verification accepts the expected abstract and transfer syntaxes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/verif_trailer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/wscript_build -->
# sources/user-network-fs/samba/source4/torture/local/wscript_build

## Purpose
This Waf build fragment declares the `TORTURE_LOCAL` internal smbtorture module and its broad source/dependency set.

## Important APIs, types, and functions
It computes the embedded Python provision library name, defines `TORTURE_LOCAL_SOURCE` with many utility, auth, registry, LDB, DSDB, FSRVP, NSS, mdspkt, and local test sources, defines `TORTURE_LOCAL_DEPS`, and calls `bld.SAMBA_MODULE('TORTURE_LOCAL', ...)` with init function `torture_local_init`.

## Control flow
At build time, Waf expands the source/dependency strings, generates `proto.h`, and builds the module only when `bld.PYTHON_BUILD_IS_ENABLED()` is true.

## State and persistence behavior
The file does not manage runtime state. It affects persistent build outputs and generated prototypes.

## Dependencies and integration points
This is the build integration point for the local suite registered by `local.c`. Dependencies include NDR/RPC support, crypto, registry, LDB/SAMDB, replacement tests, RPC FSS state, and provision support.

## Risks and edge cases
Python build disablement disables the entire local torture module. Missing sources or dependencies can silently drop coverage or fail compilation/linking. The source list spans multiple directories, making path drift a common maintenance risk.

## Test signals
Successful build exposes the `local` smbtorture suite and all source files included in `TORTURE_LOCAL_SOURCE`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/local/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/locktest.c -->
# sources/user-network-fs/samba/source4/torture/locktest.c

## Purpose
`locktest.c` is a standalone randomized byte-range lock differential tester. It runs the same generated lock/unlock/reopen sequence against two SMB shares and reports behavioral differences.

## Important APIs, types, and functions
Global knobs include `numops`, `showall`, `analyze`, `hide_unlock_fails`, `use_oplocks`, `lock_range`, `lock_base`, `min_length`, `exact_error_codes`, and `zero_zero`. `struct record` stores one operation. `connect_one()`, `reconnect()`, `open_files()`, `close_files()`, `test_one()`, `retest()`, and `test_locks()` implement connection management, sequence generation, execution, and minimization. `main()` handles popt options, credentials, loadparm, events, gensec, and random seeding.

## Control flow
`main()` parses two UNC paths plus credentials, initializes Samba client state, seeds the random generator, and calls `test_locks()`. `test_locks()` generates `numops` records across two connections and two open file handles per server, opens `\locktest.dat` on both targets, and replays the sequence. On mismatch with `--analyse`, it repeatedly excludes chunks of records to minimize the reproducer, then prints the reduced sequence.

## State and persistence behavior
The program creates and deletes `\locktest.dat` on both target shares. It maintains in-memory connection arrays, file-number arrays, credential objects, and a malloc-backed operation log. Remote byte-range lock state is changed repeatedly and reset by closing/reopening files and reconnecting.

## Dependencies and integration points
It uses Samba client libraries (`smbcli_full_connection`, `smbcli_open`, `smbcli_lock`, `smb_raw_lock`, `smbcli_unlock`, `smbcli_close`, `smbcli_unlink`), command-line credential parsing, loadparm, resolver, event context, and gensec. It is documented by `man/locktest.1.xml`.

## Risks and edge cases
The `use_oplocks` option is parsed but not materially used in the visible lock flow. Large-file capability switches between old lock calls and `RAW_LOCK_LOCKX`. Error comparison normalizes `FILE_LOCK_CONFLICT` to `LOCK_NOT_GRANTED` unless exact errors are requested. `lock_range <= 1` would make random range generation unsafe. Differential failures can reflect timing, server policy, or dialect differences, not just bugs.

## Test signals
Exit code zero means both servers returned equivalent statuses for all generated operations. Nonzero output includes the first mismatch and, with analysis, a minimized operation sequence for reproducing lock semantic differences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/locktest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/man/gentest.1.xml -->
# sources/user-network-fs/samba/source4/torture/man/gentest.1.xml

## Purpose
This DocBook manpage documents `gentest`, a random generic SMB operation differential tester for comparing two SMB servers.

## Important APIs, types, and functions
The XML defines a `refentry` for section 1 with metadata, synopsis, description, options, version, see-also, and author sections. Options documented include two `-U user%pass` credentials, seed, operation count, print operations, backtrack analysis, ignore-field file, oplocks, preset seed file, preset seed usage, fast reconnect, continuous analysis, and analyzing successful runs.

## Control flow
The document explains that `gentest` generates a random operation set, runs it against `//server1/share1` and `//server2/share2`, and displays differences in responses.

## State and persistence behavior
As documentation, the file has no runtime state. It describes a tool that can mutate files on target shares depending on generated SMB operations and seed choices.

## Dependencies and integration points
It uses DocBook XML 4.2 and integrates with Samba's manpage build. The documented semantics should match the `gentest` binary/options.

## Risks and edge cases
Documentation drift is possible: short options may not match current popt names if the program changed. The page is versioned as Samba 4.0 and may omit newer behavior.

## Test signals
Build-time XML validation and generated manpage output indicate structural correctness; user-facing accuracy depends on option parity with the executable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/man/gentest.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/man/locktest.1.xml -->
# sources/user-network-fs/samba/source4/torture/man/locktest.1.xml

## Purpose
This DocBook manpage documents `locktest`, the randomized locking differential tester implemented by `locktest.c`.

## Important APIs, types, and functions
The XML defines section 1 metadata, synopsis, description, options, version, see-also, and author sections. It documents server/share arguments, optional repeated credentials, seed, operation count, print operations, analysis, oplocks, hide unlock failures, exact error codes, zero/zero locks, lock range/base/min length, and Kerberos.

## Control flow
The page states that the tool runs the same random set of locking operations against two SMB servers and displays response differences.

## State and persistence behavior
The document itself has no state. It describes a tool that creates a test file and manipulates byte-range locks on target shares.

## Dependencies and integration points
It integrates with the Samba DocBook manpage build and should track `locktest.c` command-line options.

## Risks and edge cases
There is visible option-name drift: the source uses long options such as `--num-ops`, `--hidefails`, `--showall`, `--analyse`, and credential-specific `--user1/--user2`, while the manpage documents several short options. Keeping this page aligned with current popt definitions is important for users.

## Test signals
XML build success verifies document structure. Manual comparison with `locktest --help` is the best signal for option accuracy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/man/locktest.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/man/masktest.1.xml -->
# sources/user-network-fs/samba/source4/torture/man/masktest.1.xml

## Purpose
This DocBook manpage documents `masktest`, a utility for comparing Samba wildcard matching behavior with a remote SMB server.

## Important APIs, types, and functions
The XML defines a section 1 `refentry` with synopsis and options for target share, credentials, debug level, workgroup, loop count, seed, operation printing, abort-on-difference, max protocol, filename character set, mask character set, and verbosity.

## Control flow
The description says `masktest` generates random filenames and masks, compares local Samba matching with the remote server's behavior, and displays differences.

## State and persistence behavior
The document is static. The described tool can create and test filenames on a remote share depending on generated inputs.

## Dependencies and integration points
It depends on DocBook XML processing in Samba's documentation build and should match the `masktest` command-line interface.

## Risks and edge cases
As with the other manpages, the Samba 4.0 version note and legacy short-option style may drift from current source behavior. The description contains awkward wording around matching files "on the remote file" that could confuse users.

## Test signals
XML validation/manpage generation proves structural validity; functional accuracy should be checked against the current `masktest --help` and behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/man/masktest.1.xml -->
