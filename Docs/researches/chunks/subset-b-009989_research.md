# sources/user-network-fs/samba/source4/torture/rpc/samr.c lines 1-8638

## Scope

This chunk covers lines 1-8638 of `sources/user-network-fs/samba/source4/torture/rpc/samr.c`. It is the bulk of Samba's SAMR RPC torture test implementation: includes, shared constants, context type definitions, helpers for SAMR/LSA strings and password crypto buffers, most SAMR object tests for users/groups/aliases/domains, password-change test flows, bad-password and lockout policy tests, enumeration/display-info checks, and the beginning of the large-object stress helper.

The chunk stops inside `test_ManyObjects()`. Domain-open, connect, suite registration, and some wrappers begin after this chunk and are intentionally not described as if they were complete here.

## Purpose

The file exercises Microsoft SAMR server behavior through generated DCE/RPC client stubs and Samba's torture framework. This chunk validates that a server implements the expected semantics for:

- SAMR handle lifecycle, security descriptor query/set, shutdown and DSRM password endpoints.
- User, group, alias, and domain object creation, deletion, lookup, open, query, and mutation.
- User information class behavior across many SAMR info levels, including `SetUserInfo`, `SetUserInfo2`, `QueryUserInfo`, and `QueryUserInfo2`.
- Password setting and password changing through old LM/NT hash formats, RC4-encrypted SAMR password buffers, extended/confounded buffers, and newer AES password formats.
- Password policy effects on `pwdLastSet`, password history, password complexity/length, `badPwdCount`, and account lockout.
- Cross-protocol integration between SAMR, Netlogon, and LSA policy/account-rights state.
- Enumeration coherency between `EnumDomain*`, `LookupNames`, `LookupRids`, `QueryDisplayInfo*`, and domain counters.
- Large domain behavior by creating many users, groups, or aliases, then checking enumeration/display counts.

The tests are behavioral, not unit-local. They mutate a live test domain, compare observed `NTSTATUS` values with Windows-compatible expectations, and restore some domain policy state after invasive password tests.

## Important APIs, Types, And Helpers

The core context type in this chunk is `struct torture_samr_context`, which carries a SAMR connect handle, machine credentials for Netlogon-authenticated checks, an `enum torture_samr_choice` selector, and `num_objects_large_dc` for large-domain stress runs. `enum torture_samr_choice` controls whether created objects are only smoke-tested or receive password, attribute, privilege, bad-password, lockout, or many-object coverage.

Small initialization helpers populate generated NDR structures:

- `init_lsa_String()`, `init_lsa_StringLarge()`, and `init_lsa_BinaryString()` set string/binary fields expected by SAMR and LSA RPC calls.
- `samr_rand_pass_silent()`, `samr_rand_pass()`, `samr_very_rand_pass()`, and `samr_rand_pass_fixed_len()` generate passwords for policy-sensitive tests, including UTF-16 random-byte password blobs.

Common SAMR wrappers include:

- `test_samr_handle_Close()` for handle close assertions.
- `test_QuerySecurity()` and `test_SetSecurity()` for security descriptor round trips.
- `test_LookupName()` and `test_OpenUser_byname()` for name-to-RID-to-handle setup.
- `test_SetDomainInfo()`, `test_SetDomainInfo_ntstatus()`, and `test_QueryDomainInfo2_level()` for policy backup, mutation, and expected-error checks.

User information coverage is concentrated in `test_SetUserInfo()`, `test_QueryUserInfo()`, `test_QueryUserInfo2()`, and many password-specific setters:

- `test_SetUserPass()` tests level 24 RC4-style password setting.
- `test_SetUserPass_23()`, `_25()`, and `_32()` test field-present password levels and deliberately broken session keys/password buffers.
- `test_SetUserPass_31()` and `test_SetUserPassEx()` test AES and extended encrypted password info levels.
- `test_SetUserPass_18()` and `_21()` test hash-level updates, including session-key encryption of LM/NT hashes and invalid length rejection.
- `test_SetUserPass_level_ex()` is the generic backend used by the `pwdLastSet` matrix; it prepares levels 18, 21, 23, 24, 25, 26, 31, and 32 and can dispatch through either `SetUserInfo` or `SetUserInfo2`.

Password-change protocol coverage includes `test_ChangePasswordUser()`, `test_OemChangePasswordUser2()`, `test_ChangePasswordUser2()`, `test_ChangePasswordUser2_ntstatus()`, `test_ChangePasswordUser3()`, `test_ChangePasswordUser4()`, and `test_ChangePasswordRandomBytes()`. These build LM/NT hashes via `E_deshash()` and `E_md4hash()`, old/new password verifiers via `E_old_pw_hash()`, SAMR encrypted password buffers via `init_samr_CryptPassword*()`, and AES/PBKDF2 payloads via GnuTLS and Samba crypto helpers.

Object helpers cover aliases, users, groups, and domains:

- Alias helpers: `test_CreateAlias()`, `test_alias_ops()`, `test_QueryAliasInfo()`, `test_SetAliasInfo()`, `test_GetMembersInAlias()`, `test_AddMemberToAlias()`, `test_AddMultipleMembersToAlias()`, `test_GetAliasMembership()`, and delete-by-name/delete-handle variants.
- User helpers: `test_CreateUser()`, `test_CreateUser2()`, `test_user_ops()`, `test_OpenUser()`, `test_DeleteUser()`, and `test_DeleteUser_byname()`.
- Group helpers: `test_CreateDomainGroup()`, `test_QueryGroupInfo()`, `test_SetGroupInfo()`, `test_QueryGroupMember()`, `test_AddGroupMember()`, `test_OpenGroup()`, `test_DeleteDomainGroup()`, and `test_DeleteGroup_byname()`.
- Domain helpers: `test_QueryDomainInfo()`, `test_QueryDomainInfo2()`, `test_RidToSid()`, `test_GetBootKeyInformation()`, `test_TestPrivateFunctionsDomain()`, and `test_RemoveMemberFromForeignDomain()`.

Cross-protocol helpers are also important. `setup_schannel_netlogon_pipe()` binds Netlogon with schannel/sign/seal flags, while `test_SamLogon()` and `test_SamLogon_with_creds()` verify passwords through `netr_LogonSamLogonEx`. `test_DeleteUser_with_privs()` opens an LSA pipe, grants account rights to a user SID, deletes the SAMR user, then checks that LSA account-rights state persists until explicitly deleted.

## Control Flow

Most flows are organized around opening a domain handle, creating a temporary object, running selector-specific operations, and deleting the object unless the test intentionally transfers ownership to another cleanup path.

`test_user_ops()` is the main per-user dispatcher. It first resolves the test account RID, then switches on `enum torture_samr_choice`:

- `TORTURE_SAMR_USER_ATTRIBUTES` probes security, query levels, writable fields, password info, private functions, and a level-24 password set.
- `TORTURE_SAMR_PASSWORDS` runs machine-account password policy exceptions, field-present password-set levels 23/25/32, AES level 31, classic password changes, hash-level sets, and final query checks for expected account flags/RID.
- `TORTURE_SAMR_PASSWORDS_PWDLASTSET` enters the `test_SetPassword_pwdlastset()` matrix.
- `TORTURE_SAMR_PASSWORDS_BADPWDCOUNT` and `TORTURE_SAMR_PASSWORDS_LOCKOUT` enter domain-policy mutation wrappers that backup policies, run logon/password-change sequences, and restore policies.
- `TORTURE_SAMR_USER_PRIVILEGES` opens LSARPC and checks interaction between SAMR user deletion and LSA account rights.
- `TORTURE_SAMR_OTHER` and many-object selectors only require the account to exist.

`test_ChangePassword()` chains the major password-change entry points for one account: handle-bound `ChangePasswordUser`, server/account `ChangePasswordUser2`, LM-only OEM change, `ChangePasswordUser3` reject-reason checks for reused/simple/too-short/too-early passwords, two successful `ChangePasswordUser3` verifications, and the AES-based `ChangePasswordUser4` path.

`test_SetPassword_pwdlastset()` performs a nested matrix over password info levels, `fields_present` combinations, password-expired values, and query/set API variants. Each iteration sets a password, queries `pwdLastSet`, optionally verifies the new password through Netlogon, sleeps to avoid timestamp granularity issues, and checks when `pwdLastSet` should be zero, equal, or increasing. Samba3/Samba4 get a longer delay because of coarser timestamp granularity.

`test_Password_badpwdcount_wrap()` and `test_Password_lockout_wrap()` follow the same policy discipline: query original domain password and lockout policy, mutate them for the scenario, run enabled/disabled plus network/interactive credential cases, then restore original policy information. The bad-password path constructs password history and verifies when old passwords should or should not increment `badPwdCount`. The lockout path checks lockout threshold/duration validation, account lockout status via multiple `QueryUserInfo` levels, post-expiry unlock behavior, and `ChangePasswordUser2` behavior while locked.

Enumeration flows open or validate each enumerated object. `test_EnumDomainUsers_all()` iterates account-flag masks, checks mask filtering by reopening users and querying level 16, then tests reverse lookup with `LookupNames` and `LookupRids`. Group and alias enumeration helpers similarly open each returned RID. Display-info helpers page through `QueryDisplayInfo`, compare display rows with `QueryUserInfo` level 21, and check continuation/index behavior.

`test_ManyObjects()` begins at the end of this chunk. Within the covered lines it queries announced domain counts, creates `num_objects_large_dc` users/groups/aliases depending on `ctx->choice`, enumerates totals, and queries display info for users/groups. The cleanup/count assertions continue beyond line 8638.

## State And Persistence Behavior

These tests intentionally mutate server-side persistent account database state:

- Temporary users, groups, and aliases are created with fixed test prefixes such as `samrtorturetest`, `samrtorturetestgroup`, and `samrtorturetestalias`.
- Existing leftover test objects are deleted and recreated when `*_EXISTS` statuses are returned.
- User attributes such as names, comments, full names, profile/home paths, workstations, parameters, country/code page, expiry, logon hours, and account flags are changed and re-queried.
- Passwords are repeatedly reset and changed. The active password is tracked in a local `char **password` and verified through subsequent password-change calls and Netlogon logon attempts.
- Domain password and lockout policies are changed by some tests. Wrappers preserve `DomainPasswordInformation` and `DomainLockoutInformation` and restore them after their scenario loops.
- LSA account rights may outlive SAMR user deletion. `test_DeleteUser_with_privs()` explicitly validates this persistence and then removes the LSA account object.

Local state uses talloc contexts heavily. Per-user create loops allocate short-lived child contexts so generated NDR output and temporary strings can be released after each object. Policy handles are closed with `test_samr_handle_Close()` unless an RPC delete call consumes or clears the handle. The code checks `ndr_policy_handle_empty()` before deleting in some paths to avoid double use after helper operations.

Some tests are gated by torture settings because they are destructive or server-family-specific. `dangerous` is required for shutdown and the async enumeration stress test. Samba3/Samba4 settings skip or relax known-incompatible behavior around security descriptor setting, multi-member alias operations, group member attributes, and timestamp granularity. Builtin-domain SID checks expect create operations to be refused.

## Dependencies And Integration Points

This chunk depends on generated RPC/NDR interfaces for SAMR, LSA, and Netlogon: `dcerpc_samr_*_r`, `dcerpc_lsa_*_r`, and `dcerpc_netr_LogonSamLogonEx_r`. It also relies on Samba's torture framework assertions and reporting (`torture_assert*`, `torture_comment`, `torture_result`, `torture_skip`, `torture_fail`) to turn protocol responses into test outcomes.

Credential and authentication integration comes from `cli_credentials`, Netlogon schannel credentials, and DCE/RPC binding auth metadata. `test_SamLogon()` constructs either interactive password-logon data or NTLM network-logon responses, encrypts the Netlogon payload with the machine account credential state, and accepts either validation level 6 or a fallback to level 3.

Cryptographic dependencies are central:

- `E_md4hash()`, `E_deshash()`, and `mdfour()` produce NT, LM, or raw-byte password hashes.
- `E_old_pw_hash()` links old/new password hashes for verifier fields.
- `sess_crypt_blob()`, `samba_gnutls_arcfour_confounded_md5()`, and GnuTLS ARCFOUR encrypt legacy buffers.
- `init_samr_CryptPassword()`, `init_samr_CryptPasswordEx()`, and `init_samr_CryptPasswordAES()` build SAMR password info-level payloads.
- `gnutls_pbkdf2()` and `samba_gnutls_aead_aes_256_cbc_hmac_sha512_encrypt()` build the `ChangePasswordUser4` AES payload.

Directory/security dependencies include `dom_sid_*` helpers for RID/SID construction and comparison, `global_sid_Builtin`, account flag constants such as `ACB_NORMAL`, `ACB_WSTRUST`, `ACB_DISABLED`, and domain policy constants such as `DomainPasswordInformation`, `DomainLockoutInformation`, and `DOMAIN_PASSWORD_COMPLEX`.

## Risks And Maintenance Notes

The tests are highly stateful and can leave domain policy or account objects changed if a hard failure exits before restore logic runs. The bad-password and lockout wrappers restore policies at the end, but they do not use a single structured cleanup block around every assertion. New assertions in those paths should be placed carefully or paired with cleanup-safe control flow.

Password tests rely on live policy timing, random password generation, and server-specific behavior. Min password age, password complexity, history length, timestamp granularity, and lockout windows can make failures environment-dependent. The code already accepts `NT_STATUS_PASSWORD_RESTRICTION` as non-fatal in some places and has Samba3/Samba4 conditionals; expanding coverage should preserve these compatibility allowances.

Several paths intentionally submit malformed cryptographic data and expect exact failures such as `NT_STATUS_WRONG_PASSWORD`, `NT_STATUS_INVALID_PARAMETER`, `NT_STATUS_ACCESS_DENIED`, or `NT_STATUS_ACCOUNT_LOCKED_OUT`. These are protocol-compatibility tests; changing expected statuses can mask regressions in Windows-compatible semantics.

Legacy LM/OEM password paths use weak algorithms because the protocol requires them. They should remain test-only and should not be copied into production authentication logic except through existing Samba protocol helpers.

Fixed test names create collision risk when previous runs fail. Most create helpers handle object-exists statuses by deleting stale objects, but concurrent test runs against the same domain can still interfere with one another. Large-object tests also stress enumeration counts and can be expensive or disruptive depending on `num_objects_large_dc`.

The chunk includes many server-family conditionals. Removing a skip or relaxing condition without testing against Windows, Samba3, Samba4 AD DC, and builtin-domain handles risks converting known differences into false regressions.

## Test Signals

Important positive signals from this chunk are:

- SAMR calls return transport `NT_STATUS_OK` and expected operation statuses for every queried/set info level.
- Created users, groups, and aliases have expected account flags, primary groups, RIDs, membership state, and deletion behavior.
- Password set/change methods produce passwords that work through subsequent `ChangePasswordUser3` or Netlogon checks.
- Deliberately broken password buffers return expected failure statuses and do not update local `password` state.
- `pwdLastSet` is zero when forced expired, nonzero and increasing after password updates, or unchanged for field-present updates that do not include a password or expired flag.
- `badPwdCount` increments, resets, or remains unchanged according to enabled/disabled state, interactive/network logon type, and password-history recency.
- Lockout state appears consistently across `QueryUserInfo` levels 3, 5, 16, and 21, and authentication returns `NT_STATUS_ACCOUNT_LOCKED_OUT` while the account is locked.
- `EnumDomainUsers`, `EnumDomainGroups`, `EnumDomainAliases`, `QueryDisplayInfo*`, `LookupNames`, and `LookupRids` remain coherent.
- LSA account rights remain after SAMR user deletion until the LSA account object is deleted.
- Large-object creation and enumeration counts increase by the expected number for the selected object type; final count assertions continue after this chunk boundary.

Useful regression indicators include unexpected `NT_STATUS_INVALID_INFO_CLASS` on supported levels, missing returned arrays with nonzero counts, display-info entries that disagree with `QueryUserInfo`, failure to restore domain policy, stale test objects that cannot be deleted, and password-policy failures that report the wrong extended reject reason.

## Chunk Boundary Notes

Lines 1-8638 define all helper families needed by later suite entry points, but this chunk does not include the final connect/open-domain orchestration or public torture suite registration functions. The merge lane should combine this document with later chunks before making whole-file claims about top-level test registration or the complete `test_ManyObjects()` cleanup and count-validation path.
