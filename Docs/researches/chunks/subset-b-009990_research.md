# sources/user-network-fs/samba/source4/torture/rpc/samr.c lines 8639-9474

## Scope

This chunk is the final slice of Samba's SAMR RPC torture test source. It starts in the cleanup and count-check tail of `test_ManyObjects()` and then contains the domain-level test dispatcher, domain lookup/enumeration helpers, SAMR connect-version coverage, the `samr_ValidatePassword` test, and the public torture entry points/suite builders for the main SAMR, user, password, large-DC, and password-policy scenarios.

The surrounding declarations matter for this chunk: `struct torture_samr_context` carries the active SAMR connect handle, optional machine credentials, the selected `enum torture_samr_choice`, and the large-DC object count. The constants `TEST_ACCOUNT_NAME`, `TEST_ACCOUNT_NAME_PWD`, `TEST_ALIASNAME`, and `TEST_GROUPNAME` provide fixed object names for user/group/alias creation and cleanup.

## Purpose

The chunk wires many lower-level SAMR operation tests into executable torture flows. Each top-level function opens a DCERPC connection to `ndr_table_samr`, creates a context selecting one test family, connects to SAMR, enumerates domains, runs domain-specific checks, and closes the resulting handle.

The main behavioral themes are:

- Verifying SAMR connect procedure variants from `samr_Connect` through `samr_Connect5`.
- Enumerating SAM domains and proving that lookup, domain password info, and domain-open paths work for every advertised domain.
- Dispatching domain tests by selected scenario, including user creation/attributes/password behavior, large object enumeration, alias/group/member tests, domain info queries, display info, private functions, RID-to-SID conversion, and boot key info.
- Exercising handle lifetime behavior by opening a domain, closing the parent connect handle, running domain tests, and then reconnecting the parent handle.
- Creating and deleting temporary users, aliases, groups, and bulk objects, while treating Samba3 mode differently where some objects are only closed rather than deleted.
- Providing suite constructors for machine-backed tests that require BDC/machine credentials, including `pwdLastSet`, privileged-user deletion, bad-password count, and lockout cases.
- Testing `samr_ValidatePassword` as its own suite and skipping cleanly when the server lacks that RPC procedure.

## Important APIs, Types, And Functions

Key local functions in this chunk:

- `test_OpenDomain(struct dcerpc_pipe *p, struct torture_context *tctx, struct torture_samr_context *ctx, struct dom_sid *sid)`: opens a domain with `samr_OpenDomain`, closes the parent connect handle to test server reference counting, dispatches the selected test family, deletes any remaining test handles, closes the domain handle, and reconnects SAMR.
- `test_LookupDomain(...)`: validates `samr_LookupDomain` error semantics for a NULL domain name and a known-bad domain name, looks up a real domain name from enumeration, calls `test_GetDomPwInfo()`, and enters `test_OpenDomain()`.
- `test_EnumDomains(...)`: calls `samr_EnumDomains`, iterates `struct samr_SamArray` entries, calls `test_LookupDomain()` for each, and then repeats enumeration once more.
- `test_Connect(...)`: executes `samr_Connect`, `samr_Connect2`, `samr_Connect3`, `samr_Connect4`, and `samr_Connect5` in sequence, closing the previously successful handle whenever a newer variant succeeds. The last successful handle is returned through `*handle`.
- `test_samr_ValidatePassword(...)`: sends `samr_ValidatePassword` level `NetValidatePasswordReset` requests for several sample passwords against a deliberately non-existent account, reporting whether the server policy allowed or refused each password.
- Top-level tests: `torture_rpc_samr()`, `torture_rpc_samr_users()`, `torture_rpc_samr_passwords()`, `torture_rpc_samr_pwdlastset()`, `torture_rpc_samr_users_privileges_delete_user()`, `torture_rpc_samr_many_accounts()`, `torture_rpc_samr_many_groups()`, `torture_rpc_samr_many_aliases()`, `torture_rpc_samr_badpwdcount()`, and `torture_rpc_samr_lockout()`.
- Suite builders: `torture_rpc_samr_passwords_pwdlastset()`, `torture_rpc_samr_user_privileges()`, `torture_rpc_samr_large_dc()`, `torture_rpc_samr_passwords_badpwdcount()`, `torture_rpc_samr_passwords_lockout()`, and `torture_rpc_samr_passwords_validate()`.

Important generated RPC/NDR types used directly:

- `struct samr_OpenDomain`, `struct samr_LookupDomain`, `struct samr_EnumDomains`.
- `struct samr_Connect`, `samr_Connect2`, `samr_Connect3`, `samr_Connect4`, and `samr_Connect5`.
- `union samr_ConnectInfo`, used at connect level 1 with `client_version = 0` and `supported_features = 0`.
- `struct samr_ValidatePassword`, `union samr_ValidatePasswordReq`, and `union samr_ValidatePasswordRep`.
- `struct policy_handle`, `struct dom_sid`, `struct dom_sid2`, `struct lsa_String`, and `struct samr_SamArray`.

Important harness and utility APIs:

- `torture_rpc_connection()` opens a SAMR DCERPC pipe against `ndr_table_samr`.
- `torture_suite_create()`, `torture_suite_add_rpc_iface_tcase()`, `torture_suite_add_machine_bdc_rpc_iface_tcase()`, `torture_rpc_tcase_add_test()`, `torture_rpc_tcase_add_test_ex()`, and `torture_rpc_tcase_add_test_creds()` register test cases.
- `torture_assert_ntstatus_ok()`, `torture_assert_ntstatus_equal()`, `torture_assert()`, `torture_result()`, `torture_comment()`, and `torture_skip()` provide failure, skip, and diagnostic behavior.
- `talloc_zero()`, `talloc_get_type_abort()`, and `talloc_free()` manage context-owned state.
- `ndr_policy_handle_empty()` prevents delete calls on never-opened handles.

## Control Flow

The ordinary top-level SAMR flow is:

1. A public entry point such as `torture_rpc_samr()` calls `torture_rpc_connection(torture, &p, &ndr_table_samr)` and extracts `p->binding_handle`.
2. It allocates a `struct torture_samr_context` and sets `ctx->choice` to the requested scenario.
3. It calls `test_Connect()`, which probes connect procedure versions and leaves `ctx->handle` set to the newest successful connect handle.
4. Some broad tests query security first, except when the `samba3` torture setting is enabled.
5. `test_EnumDomains()` enumerates domains, calls `test_LookupDomain()` for every advertised domain, and reissues `EnumDomains` as a final sanity check.
6. `test_LookupDomain()` checks invalid-parameter and no-such-domain paths before resolving the real domain SID, obtaining domain password info, and calling `test_OpenDomain()`.
7. `test_OpenDomain()` opens the domain, closes `ctx->handle`, runs the selected domain test branch, cleans up created object handles, closes the domain handle, then reconnects `ctx->handle` with `test_Connect()`.
8. The top-level entry point may run dangerous-only shutdown/DSRM password probes and then closes `ctx->handle`.

`test_OpenDomain()` is the central dispatcher. Its switch on `ctx->choice` maps scenarios as follows:

- `TORTURE_SAMR_PASSWORDS` and `TORTURE_SAMR_USER_PRIVILEGES`: optionally run `test_CreateUser2()` outside Samba3 mode, then create a standard user through `test_CreateUser()`.
- `TORTURE_SAMR_USER_ATTRIBUTES`: does the same user creation and then requires `test_QueryDisplayInfo()` because the attribute test path needs richer users to validate display state.
- `TORTURE_SAMR_PASSWORDS_PWDLASTSET`, `TORTURE_SAMR_PASSWORDS_BADPWDCOUNT`, and `TORTURE_SAMR_PASSWORDS_LOCKOUT`: pass `ctx->machine_credentials` into `test_CreateUser2()`/`test_CreateUser()` so password policy state can be driven with machine-backed credentials.
- `TORTURE_SAMR_MANY_ACCOUNTS`, `TORTURE_SAMR_MANY_GROUPS`, and `TORTURE_SAMR_MANY_ALIASES`: call `test_ManyObjects()` to create, enumerate/display-query, and clean up a configurable number of objects.
- `TORTURE_SAMR_OTHER`: creates a baseline user and then runs a broad domain API sweep, including security query/set outside Samba3 mode, foreign-domain member removal, alias/group creation, alias membership, domain info variants, user/group/alias enumeration, async user enumeration, display-info variants and continuation, display enumeration index tests outside Samba4 mode, group list, private functions, RID-to-SID, and boot key info.

The visible tail of `test_ManyObjects()` handles cleanup after bulk object creation and enumeration. For Samba3-mode tests it closes every non-empty bulk handle. Otherwise it deletes users, groups, or aliases according to `ctx->choice`. It frees the handle array and, for the many-accounts case only, reports unexpected enumeration and display-info counts when the observed count is not the original domain count plus the number created.

The large-DC suite constructor creates one shared `torture_samr_context`, defaults `num_objects_large_dc` to `150`, and registers `many_aliases`, `many_groups`, and `many_accounts`. Each test updates the shared context choice and optionally overrides the object count from the `large_dc` torture setting before connecting and enumerating domains.

The password-policy suite constructors use `torture_suite_add_machine_bdc_rpc_iface_tcase()` with `TEST_ACCOUNT_NAME_PWD`, then register credential-aware callbacks. These callbacks all establish a fresh SAMR connection and store `machine_credentials` in `ctx` before domain enumeration dispatches into the corresponding password-state test branch.

## State And Persistence Behavior

This chunk does not define persistent storage, but it intentionally mutates server-side SAM database state during tests:

- `test_OpenDomain()` may create temporary users, aliases, and groups and then deletes them before returning.
- The bulk large-DC paths create many users, groups, or aliases using deterministic names derived from the test constants and a zero-padded index. They either delete them or, under Samba3 mode, only close handles.
- Password scenarios can change user password-related state such as password last set, bad password count, and lockout state through lower-level helpers invoked by `test_CreateUser()` and `test_CreateUser2()`.
- `test_SetDsrmPassword()` and `test_Shutdown()` are called by broad entry points, but they are guarded by the `dangerous` torture setting in their implementations. In normal runs they skip rather than changing dangerous machine state.

Handle state is a major part of the test:

- `test_Connect()` may open up to five SAMR connect handles but closes the previous handle whenever a later connect variant succeeds.
- `test_OpenDomain()` deliberately closes the main connect handle while retaining the domain handle. This verifies that the server keeps the domain object alive independently of the parent connection handle.
- At the end of each domain run, `test_OpenDomain()` closes object handles through delete helpers when they are not empty, closes the domain handle, and reconnects the main context handle so the outer enumeration loop can continue.

Memory lifetime is owned by the torture context or suite context through talloc. `test_ManyObjects()` frees its bulk handle array explicitly. The chunk relies on talloc cleanup for per-test contexts and generated RPC output buffers.

## Dependencies And Integration Points

Primary dependencies are Samba's generated SAMR client stubs from `librpc/gen_ndr/ndr_samr_c.h` and the DCERPC binding/pipe layer:

- `dcerpc_samr_OpenDomain_r`
- `dcerpc_samr_LookupDomain_r`
- `dcerpc_samr_EnumDomains_r`
- `dcerpc_samr_Connect_r`
- `dcerpc_samr_Connect2_r`
- `dcerpc_samr_Connect3_r`
- `dcerpc_samr_Connect4_r`
- `dcerpc_samr_Connect5_r`
- `dcerpc_samr_ValidatePassword_r`

The chunk depends heavily on earlier helpers in `samr.c`:

- Creation/deletion helpers: `test_CreateUser()`, `test_CreateUser2()`, `test_DeleteUser()`, `test_CreateAlias()`, `test_DeleteAlias()`, `test_CreateDomainGroup()`, `test_DeleteDomainGroup()`.
- Domain tests: `test_QuerySecurity()`, `test_RemoveMemberFromForeignDomain()`, `test_GetAliasMembership()`, `test_QueryDomainInfo()`, `test_QueryDomainInfo2()`, `test_EnumDomainUsers_all()`, `test_EnumDomainUsers_async()`, `test_EnumDomainGroups_all()`, `test_EnumDomainAliases_all()`, `test_QueryDisplayInfo()`, `test_QueryDisplayInfo2()`, `test_QueryDisplayInfo3()`, `test_QueryDisplayInfo_continue()`, `test_GetDisplayEnumerationIndex()`, `test_GetDisplayEnumerationIndex2()`, `test_GroupList()`, `test_TestPrivateFunctionsDomain()`, `test_RidToSid()`, and `test_GetBootKeyInformation()`.
- Bulk enumeration helpers: `test_EnumDomainUsers()`, `test_EnumDomainGroups()`, `test_EnumDomainAliases()`, and `test_QueryDisplayInfo_level()`.
- Setup/teardown helpers: `test_samr_handle_Close()`, `test_SetDsrmPassword()`, and `test_Shutdown()`.

Torture settings influence behavior:

- `samba3`: skips some `test_CreateUser2()` and security calls, and changes bulk cleanup from deletion to handle close in `test_ManyObjects()`.
- `samba4`: skips display enumeration index tests in the broad `SAMR-OTHER` path.
- `large_dc`: overrides the large-DC object count.
- `dangerous`: controls shutdown and DSRM password side-effect tests in helper functions called by this chunk.

The suite constructors are integration points for Samba's torture registry. The non-suite public functions (`torture_rpc_samr`, `torture_rpc_samr_users`, and `torture_rpc_samr_passwords`) are direct RPC torture entry points. The suite-returning functions create named suites that can be selected independently, especially for machine-credential-backed password behavior.

## Risks And Maintenance Notes

- `test_OpenDomain()` closes `ctx->handle` and later reconnects it. If any branch returns early after the close or if cleanup assertions abort, subsequent outer-domain enumeration state may be invalid. The current function mostly accumulates failures in `ret` and centralizes cleanup, which is important to preserve.
- The large-DC tests share a single `struct torture_samr_context` among three test registrations. Sequential torture execution makes this workable, but parallel execution of those tests would race on `ctx->choice`, `ctx->handle`, and `ctx->num_objects_large_dc`.
- `test_EnumDomains()` checks `if (!*r.out.sam)` after `r.out.sam = &sam`; this assumes the RPC stub initializes `sam`. A malformed server response with success but a NULL array returns false rather than asserting with a clear diagnostic.
- `test_ManyObjects()` only compares expected enumeration/display counts for the many-accounts path. Many-groups and many-aliases paths still validate RPC success, but not exact count deltas in this visible tail.
- The many-accounts count mismatch only logs comments and still returns true. This makes count drift diagnostic rather than a hard failure.
- The `samr_ValidatePassword` test only comments when transport is not `NCACN_IP_TCP`; it does not skip or fail solely on transport mismatch. The subsequent RPC result determines behavior.
- `test_samr_ValidatePassword()` assumes a non-NULL validation reply after successful RPC/result status. If a server returns success with a NULL reply pointer, the diagnostic dereference would be unsafe.
- `test_Connect()` closes previous handles without folding close failures into `ret`. A server that succeeds connects but mishandles close could be underreported by this specific function, though broader handle-close tests may catch it elsewhere.
- Several paths mutate real SAMR state. The deterministic object names reduce leak ambiguity, but failed cleanup can leave users, groups, or aliases behind and can affect later runs.
- The broad `TORTURE_SAMR_OTHER` path chains many tests with `ret &= ...`, so it continues after failures. This improves coverage per run but can make the first failing API harder to isolate without reading the emitted torture messages.

## Test Signals

Useful signals for this chunk include:

- `samr` should connect through at least one connect variant and leave a valid context handle after `test_Connect()`.
- `samr_Connect3`, `samr_Connect4`, and `samr_Connect5` failures are reported as explicit torture failures, while older connect failures are logged and reflected in the boolean result.
- `samr_EnumDomains` must return at least one `samr_SamArray` entry; each entry should survive lookup, password-info probing, domain open, branch-specific tests, and reconnect.
- Domain handle reference counting is validated when branch tests continue to work after the parent connect handle is closed.
- `LookupDomain(NULL)` should return `NT_STATUS_INVALID_PARAMETER`, and lookup of `"xxNODOMAINxx"` should return `NT_STATUS_NO_SUCH_DOMAIN`.
- The broad `SAMR-OTHER` run should cover user creation/deletion, alias/group creation/deletion, domain info, display info, enumeration, group/RID helpers, and boot key information, with Samba3/Samba4 settings changing only the documented skips.
- `samr.large-dc` should create and clean up the configured number of objects for aliases, groups, and accounts, defaulting to 150 when `large_dc` is unset.
- Password-policy suites should run under machine BDC RPC test cases and pass machine credentials into their branch-specific user operations.
- `samr.passwords.validate` should either skip on `NT_STATUS_RPC_PROCNUM_OUT_OF_RANGE` or return successful SAMR validation replies for all sample passwords, emitting allow/refuse status codes.
- Final cleanup should leave no non-empty created user, alias, group, domain, or connect handles unclosed in successful non-Samba3 paths.
