# subset-b-009922 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/passwords.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/passwords.py

## Purpose

This file is an executable Samba AD DS password-behavior test suite. It validates LDAP password set and change semantics for AD-style password attributes (`unicodePwd`, `userPassword`, `clearTextPassword`, `dBCSPwd`), password history and previous-password simple bind behavior, `dSHeuristics`-controlled `userPassword` handling, policy hint controls, Protected Users handling, empty-value rejection, and edge-case LDIF operation ordering. It is designed to run against Samba and, for many cases, Windows Server when the LDAP connection is sufficiently protected.

The script parses Samba loadparm, credentials, subunit, and host options at import time, forces gensec sealing on command-line credentials, normalizes the host to LDAP/LDAPS/TDB URLs near the bottom, and invokes `TestProgram(module=__name__, opts=subunitopts)`.

## Important APIs, Types, and Functions

The main type is `PasswordTests(PasswordTestCase)`. It inherits shared password-policy helpers from `samba.tests.password_test.PasswordTestCase`, including `allow_password_changes()`. Setup opens an administrative `SamDB` connection as `self.ldb`, creates `cn=testuser,cn=users,<domain>`, establishes an initial password through special `userPassword` delete/add LDIF syntax, enables the account, then opens `self.ldb2` as that user with sealed credentials.

Key helpers:

- `_upwd_encode(password)` wraps a password in double quotes, UTF-16LE encodes it, and base64 encodes the result for `unicodePwd` LDIF.
- `_replace_unicode_pwd(ldb, old=None, new=None, controls=None)` constructs either password-change LDIF (`delete` old then `add` new) or password-reset LDIF (`replace`) against `unicodePwd`, optionally with LDAP controls.
- `_set_pwd_properties()` repeatedly writes `pwdProperties` and polls for convergence to handle Windows timing races.
- `_set_pwd_property_bits()` toggles password-property bits, mainly `DOMAIN_PASSWORD_COMPLEX`.
- `_test_unicodePwd_policy_hints_history()`, `_test_unicodePwd_policy_hints_complexity()`, `_test_unicodePwd_policy_hints_length()`, and `_test_unicodePwd_policy_hints_password_age()` centralize policy-hints behavior across the modern and deprecated control OIDs.

Important test methods cover:

- Hash-based `unicodePwd` and `dBCSPwd` set/change rejection.
- Cleartext `unicodePwd`, `userPassword`, and Samba-only `clearTextPassword` set/change paths.
- Immediate previous password simple-bind acceptance, older password rejection, and history-based reuse rejection, including rename/salt-change cases.
- Protected Users group membership combined with `unicodePwd` set/change.
- Admin reset behavior under policy hints for history, complexity, length, and password age.
- Invalid LDIF shapes and operation ordering in `test_failures()`.
- Empty attribute value handling in `test_empty_passwords()`.
- Plain LDAP `userPassword` attribute storage/readback when `dSHeuristics` disables password-change interpretation.
- Connection-local `dSHeuristics` behavior in `test_modify_dsheuristics_userPassword()`.
- Zero-length password allowance when `minPwdLength` and complexity properties are temporarily relaxed.

## Control Flow

The suite starts by proving invalid initial password-change syntax fails before using a special admin-style `userPassword` delete/add without an old value to set the first password. This setup creates a clean, enabled account and a second bind as the test user. Each test then mutates password-related attributes through `SamDB.modify()`, `modify_ldif()`, `setpassword()`, account group membership changes, or direct domain policy writes.

The control flow is mostly assertion-driven:

- Set/reset tests build `ldb.Message` instances or LDIF strings and call administrative `self.ldb`.
- User-change tests call `self.ldb2` so access checks and old-password validation run as the account itself.
- Expected failures catch `LdbError`, compare the LDAP error code, and sometimes inspect Windows/Samba diagnostic substatus strings such as `00000056`, `0000052D`, `HRES_SEC_E_INVALID_TOKEN`, or `WERR_PASSWORD_RESTRICTION`.
- Policy-hints tests intentionally change domain policy attributes, register cleanup handlers, and then exercise user changes and admin resets with and without controls.
- Teardown removes `testuser` and `testuser2` and drops the secondary connection reference.

## State and Persistence Behavior

The file directly changes persistent directory state in a live AD database: user objects, passwords, group membership, domain password policy attributes (`pwdProperties`, `minPwdLength`, min/max password age), and `dSHeuristics`. It uses `delete_force()` to clean test users in setup and teardown and uses `addCleanup()` for selected policy restoration paths. Some tests deliberately sleep after `dSHeuristics` or policy writes because behavior may be cached per connection or asynchronously visible, especially against Windows.

Password history and old-password acceptance are central stateful behaviors. The tests assume domain `pwdHistoryLength` is high enough for some history assertions, branch for FL2003-like low-history behavior in policy-hint checks, and verify that renaming an account does not invalidate previous-password history semantics.

## Dependencies and Integration Points

The script integrates with Samba's Python test runner (`samba.tests.subunitrun.TestProgram`), credentials/loadparm option handling, `SamDB`, `ldb.Message` and LDIF modification APIs, domain policy helper methods on `SamDB`, and constants from `samba.dcerpc.security`, `samba.dcerpc.samr`, `samba.hresult`, `samba.werror`, and `ldb`. It depends on encrypted LDAP or LDAPS for password operations and creates both administrative and end-user LDAP sessions.

Integration with Windows compatibility is explicit: comments and assertions allow Windows-specific `ERR_NO_SUCH_ATTRIBUTE` for `clearTextPassword`, mention required `dSHeuristics` settings for `userPassword`, and note races in domain policy propagation.

## Risks and Edge Cases

The suite is intentionally invasive: it changes domain policy and `dSHeuristics`, so cleanup correctness is important. Several paths restore state manually after a successful sequence rather than via `finally`, so an unexpected exception can leave policy changes behind until broader test cleanup or environment reset. Timing sleeps are coarse and can be flaky on slow replication/caching paths. `host_ldaps` is `None` for TDB/non-LDAP hosts, but old-password simple bind tests assume LDAPS is usable; these are effectively LDAP-server tests.

Security-sensitive risk areas are well covered: direct hash writes must remain rejected, empty values must not bypass password handling, malformed multi-operation LDIF must not produce partial unintended state, ordinary users must not reset their own passwords through replace operations, and `dSHeuristics` must not accidentally expose password material on existing connections.

## Test Signals

Successful execution signals that Samba's password modules enforce AD-compatible password set/change contracts, old-password grace and history behavior, LDAP error mapping, policy hints, and `userPassword` handling. Failure signals often identify a regression in password ACL routing, policy enforcement, protected-user support, `dSHeuristics` caching, or compatibility with Windows diagnostic codes. The suite's own assertions are the primary test signal; it does not include separate unit mocks or fixture files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/passwords.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/priv_attrs.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/priv_attrs.py

## Purpose

This executable Samba test suite validates protection around privileged AD object attributes even when generic create-child or write-property permissions are present. It focuses on attributes and `userAccountControl` flag combinations that can grant delegation, domain-controller-like behavior, SID history, Kerberos secondary TGT behavior, or privileged primary group membership. The goal is to ensure unprivileged users cannot set these values during add or modify operations, and that administrators also receive expected denials for attributes that are never valid to set directly in the tested context.

## Important APIs, Types, and Functions

The main test class is `PrivAttrsTests(samba.tests.TestCase)`, decorated with `@DynamicTestCase`. The global `attrs` table is the key test data structure. Each entry describes the LDAP attribute or logical test case, the value to apply, and expected privileged or unprivileged errors. Some logical entries map to `userAccountControl` with flag combinations:

- `UF_TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`
- `UF_TRUSTED_FOR_DELEGATION`
- `UF_SERVER_TRUST_ACCOUNT`
- `UF_PARTIAL_SECRETS_ACCOUNT`
- `UF_WORKSTATION_TRUST_ACCOUNT`
- `UF_NORMAL_ACCOUNT`
- `UF_PASSWD_NOTREQD`

Other protected attributes include `sidHistory`, `msDS-AllowedToDelegateTo`, `msDS-SecondaryKrbTgtNumber`, and `primaryGroupID`.

Important methods:

- `get_creds()` constructs sealed, non-Kerberos credentials for the unprivileged test user.
- `assertGotLdbError()` enforces exact error codes when `STRICT_CHECKING=1`, or only non-success when strict checking is disabled.
- `setUp()` creates an OU, creates an unprivileged user, gathers SIDs, opens admin and unprivileged `SamDB` connections, and prepares `SDUtils`.
- `setUpDynamicTestCases()` generates the Cartesian product of attribute scenario, operation mode, permission mode, security descriptor mode, and object class.
- `add_computer_ldap()`, `add_user_ldap()`, and `add_thing_ldap()` build and add test objects.
- `_test_priv_attr_with_args()` contains the generated test implementation.

## Control Flow

At startup, the script parses a target host, normalizes it to `ldaphost`, obtains sealed credentials, and runs the generated test suite through `SubunitTestRunner`.

For each dynamic case, `_test_priv_attr_with_args()`:

1. Resolves the real LDAP attribute name and whether the protected value should be present during add or later modification.
2. Chooses either the admin connection or unprivileged connection. For unprivileged create-child testing, it grants object-specific `CC` ACEs for user and computer classes on the test OU.
3. Optionally includes an `ntSecurityDescriptor` on the new object that grants the unprivileged user read/write property and change-password rights, simulating an admin-created object with broad write-property access.
4. Runs add-time checks, including Windows compatibility filters for object-class-only cases (`only-1`, `only-2`) and expected admin denials (`priv-error`).
5. For modify cases, first creates a baseline object and then attempts either delete/add or replace against the protected attribute as the unprivileged user.
6. Verifies that the resulting LDAP error matches the scenario's expected denial.

## State and Persistence Behavior

Each test creates and deletes a dedicated OU under the domain naming context: `OU=test_priv_attrs,<base_dn>`. It then creates an unprivileged user inside that OU and may create additional user or computer objects named `privattrs`. Security descriptors on the OU and newly created objects are modified to grant controlled permissions. `delete_force(..., controls=["tree_delete:0"])` removes the OU at setup time and cleanup handlers remove the unprivileged user.

The generated tests repeatedly mutate DACLs on the test OU and create objects in the same OU. Because setup recreates the OU per test case, the intended persistence scope is one generated test method.

## Dependencies and Integration Points

The file uses Samba command-line option parsing, `SamDB` LDAP operations, `samba.tests.DynamicTestCase`, `SubunitTestRunner`, `sd_utils.SDUtils`, NDR packing of security descriptors and SIDs, and LDAP constants from `ldb`. It integrates with AD security descriptor syntax through SDDL strings and object-specific ACE GUIDs for user/computer create-child permissions. It intentionally disables Kerberos for the unprivileged account because repeated `kinit` use is too expensive in this dynamic matrix.

## Risks and Edge Cases

The generated matrix is broad and expensive: `len(attrs) * 3 operation modes * 2 permission modes * 2 SD modes * 2 object classes`. Its correctness depends on the `attrs` metadata matching AD behavior. `STRICT_CHECKING=0` weakens exact-code assertions and can hide compatibility drift by accepting any failure. Some entries encode Windows behavior quirks with `only-1` and `only-2`, so a new directory implementation may need explicit review before changing those expectations.

The test intentionally grants powerful-looking write permissions and create rights. The core risk under test is that generic ACL success must not override attribute-specific privilege checks for delegation, DC/RODC account flags, SID history, or primary group elevation.

## Test Signals

A passing run means unprivileged users cannot set protected attributes during add, delete/add modify, or replace modify, even with create-child rights or write-property ACEs. It also signals that privileged/admin attempts fail where Samba expects schema or system-only restrictions. Failures identify either an authorization bypass, an object-class validation mismatch, or a changed LDAP error-code contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/priv_attrs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/rodc.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/rodc.py

## Purpose

This script tests direct LDAP write behavior against a read-only domain controller. It verifies that add, modify, and delete attempts that should be handled by a writable DC are rejected by the RODC with LDAP referrals, and that those referrals point to a concrete writable DC rather than only the domain DNS name. It also verifies that deleting a nonexistent object returns `ERR_NO_SUCH_OBJECT` instead of referral.

## Important APIs, Types, and Functions

The main class is `RodcTests(samba.tests.TestCase)`. `setUp()` opens a `SamDB` connection to `HOST` with system session and command-line credentials, stores the domain DN, reads `dsServiceName` from the rootDSE, and creates a unique UUID tag for temporary object names.

Test methods:

- `test_add_replicated_objects()` attempts to add an OU, user, group, and `NTDSConnection` object through the RODC. Each add must fail with `ERR_REFERRAL`; the test extracts the referred `ldap://...` URL, connects to it, proves the same operation works there, and deletes the created object.
- `test_modify_replicated_attributes()` attempts to modify replicated attributes (`carLicense`, `middleName`) on the Guest account and expects referrals. It then applies the modification on the referred DC.
- `test_modify_nonreplicated_attributes()` attempts to modify non-replicated logon/counter attributes (`badPwdCount`, `lastLogon`, `lastLogoff`). Windows refers these too, so Samba is expected to refer them.
- `test_modify_nonreplicated_reps_attributes()` reads and unpacks `repsFrom`, mutates `result_last_attempt`, repacks it, and verifies the attempted replace is referred.
- `test_delete_special_objects()` tries to delete Guest and expects referral.
- `test_no_delete_nonexistent_objects()` ensures nonexistent delete is a local `ERR_NO_SUCH_OBJECT`.
- `main()` parses host/options, normalizes bare host or file paths to LDAP/TDB URLs, and runs `TestProgram`.

## Control Flow

Most tests follow the same pattern: attempt a write through `self.samdb`, catch `LdbError`, require `ldb.ERR_REFERRAL`, parse the referred LDAP URL with a regex, and reject referrals that lack a concrete DC host. Add and replicated-attribute modify tests additionally connect to the referral target and prove the write works on that target. Non-replicated and delete tests only validate referral shape.

The `repsFrom` test adds NDR-specific flow: it reads the binary replication metadata, unpacks it with `ndr_unpack(drsblobs.repsFromToBlob, ..., allow_remaining=True)`, changes a field, and repacks with `ndr_pack()` before attempting the modify.

## State and Persistence Behavior

The test is intended to avoid durable state on the RODC. Successful referred add tests create temporary objects on a writable DC and delete them immediately. Replicated attribute modifications against Guest are applied to the referral target and are not restored by this script, so they can persist until overwritten by later tests or environment reset. The unique UUID tag reduces naming collision risk for add/delete objects.

## Dependencies and Integration Points

The script depends on Samba's `SamDB`, `system_session`, subunit test runner, `ldb` error constants and message APIs, NDR packing/unpacking, and DRS replication blob structures. It integrates with AD topology via rootDSE `dsServiceName`, domain DNS name detection, and referral URLs returned by the server.

## Risks and Edge Cases

Referral parsing is regex-based and assumes the server returns an `ldap://...>` substring. A referral format change can fail the test even if semantic referral behavior is correct. The check `address.lower().startswith(self.samdb.domain_dns_name())` is intended to reject nonspecific referrals, but URL formatting differences could affect it. The test writes to Guest attributes on the referred writable DC without cleanup, which is acceptable in isolated test environments but risky in shared directories.

## Test Signals

Passing results show that an RODC refuses writes by referral, that referrals target an actual writable DC, and that nonexistent deletes are resolved locally as no-such-object. Failures indicate regressions in RODC write routing, referral construction, DRS metadata protection, or LDAP error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/rodc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/rodc_rwdc.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/rodc_rwdc.py

## Purpose

This executable integration suite tests credential, password, lockout, replication, and referral behavior between a read-only domain controller and a writable domain controller. It verifies that RODC credential caching, reveal-on-demand policy, password changes on the RWDC, logon forwarding, lockout counters, replicated object visibility, and LDAP simple/SASL authentication remain consistent across forced replication boundaries.

## Important APIs, Types, and Functions

Top-level helpers:

- `adjust_cmd_for_py_version(parts)` prepends `$PYTHON` to subprocess commands when requested.
- `passwd_encode(pw)` encodes quoted UTF-16LE passwords for LDIF-style `unicodePwd` use.
- `make_creds(username, password, kerberos_state=None, simple_dn=None)` creates sealed credentials based on global command-line credentials, optionally forcing Kerberos/NTLM or setting a simple-bind DN.
- `set_auto_replication(dc, allow)` runs `bin/samba-tool drs options` to enable or disable inbound/outbound replication on a DC. It tolerates LDAP referral errors when the target behaves as an RODC.
- `preload_rodc_user(user_dn)` temporarily enables RWDC replication, runs `samba-tool rodc preload`, then disables replication again.
- `get_server_ref_from_samdb(samdb)` resolves a DC server object's `serverReference`.

There are two main test classes, both derived from `password_lockout_base.BasePasswordTestCase`:

- `RodcRwdcCachedTests` focuses on cached credentials, password cache flushing, SendToSam behavior, and lockout propagation for users whose secrets are preloaded or not revealed.
- `RodcRwdcTests` focuses on regular RODC/RWDC replication, referred/replicated object behavior, LDAP password changes, reveal-on-demand interactions, and base password-lockout/multiple-logon flows through an RODC.

Both classes implement `force_replication()` with `samba-tool drs replicate RODC RWDC <base> --sync-forced`, maintain `rodc_db` and `rwdc_db` `SamDB` connections, wire BasePasswordTestCase fields (`lp`, `global_creds`, `host`, `host_url`, `ldb`), and restore automatic replication in teardown.

## Control Flow

The module parses `<rodc host> <rwdc host>`, obtains sealed credentials, turns automatic replication on before and after `TestProgram`, and each test setup disables RWDC automatic replication to make synchronization explicit.

`RodcRwdcCachedTests` setup first initializes against the RWDC for shared lockout fixture creation, then switches the host URLs to the RODC. It caches original `dSHeuristics`, sets `000000001`, disables auto replication, and forces initial sync. Its tests:

- `test_cache_and_flush_password()` proves preloading exposes a user's `unicodePwd` to local system search, then changing the password on RWDC and forced replication removes the cached secret.
- `test_login_lockout_krb5()` and `test_login_lockout_ntlm()` preload a user, add it to the RODC reveal-on-demand group, optionally adjust lockout timing, and run `_test_login_lockout_rodc_rwdc()`.
- `test_login_lockout_not_revealed()` verifies a preloaded but non-revealed user can report bad-password state to the RWDC while RODC-local `badPwdCount` resets on successful authentication.
- `_test_login_lockout_rodc_rwdc()` performs a long sequence of wrong and correct password attempts, asserting `badPwdCount`, `badPasswordTime`, `lockoutTime`, `msDSUserAccountControlComputed`, `lastLogon`, and effective counter behavior before, during, and after lockout and observation-window expiry.

`RodcRwdcTests` setup similarly creates RODC/RWDC connections and then points BasePasswordTestCase operations at the RODC. Its test flow includes:

- `_test_add()` proving objects added to RWDC are absent on RODC before replication and present after forced replication, including optional cross-NC searches with `search_options:1:2`.
- Add/modify/delete replication tests for OUs, users, groups, `NTDSConnection`, regular replicated attributes, and object deletion.
- `_new_user()` creating and enabling a user on RWDC with a starting password.
- `_test_ldap_change_password()` changing a user's password repeatedly on RWDC, then checking old and new credentials against RODC and RWDC before and after replication, including NTLM and simple bind invalid-credential expectations.
- `_test_ldap_change_password_reveal_on_demand()` adding a new user to the RODC reveal-on-demand group, preloading the secret, changing password on RWDC, and verifying the cached old password and forwarded new-password behavior.
- Lockout and multiple-logon tests that preload fixture users, seed failure/success authentication through the RODC, then delegate to `BasePasswordTestCase` helpers.

## State and Persistence Behavior

The suite manipulates live DC replication state. It disables and re-enables inbound/outbound replication options, runs forced replication, preloads RODC secrets, changes domain `dSHeuristics`, creates users and directory objects on the RWDC, modifies reveal-on-demand group membership, changes passwords, and adjusts lockout policy fields. Teardown restores RWDC `dSHeuristics`, sets credentials back to non-Kerberos in `RodcRwdcTests`, and re-enables auto replication.

State visibility is intentionally staged: tests often assert absence on the RODC before `force_replication()` and presence afterward. Credential cache state is checked through a local system `SamDB` search for `unicodePwd`; password changes on the RWDC are expected to flush RODC-cached secrets after replication. Time sleeps account for delayed SendToSam/Kerberos bad-password propagation and lockout windows.

## Dependencies and Integration Points

The file depends on Samba's `SamDB`, credentials stack, gensec sealing, SAMR RPC client, DSDB constants, `password_lockout_base.BasePasswordTestCase`, `samba-tool drs` and `samba-tool rodc preload` subprocesses, LDAP/LDAPS authentication behavior, reveal-on-demand RODC attributes, and AD replication topology. It integrates Python test code with external command-line replication controls, making it a full system integration test rather than a unit test.

## Risks and Edge Cases

The suite is sensitive to environment topology: it requires a real RODC/RWDC pair, working `bin/samba-tool`, credentials with rights to change replication options and preload secrets, and predictable replication timing. Subprocess failures raise a generic `RodcRwdcTestException` after printing stdout/stderr, so diagnostics rely on test logs. Several tests sleep for fixed periods to wait for SendToSam or lockout windows; slow or overloaded test environments can be flaky.

Because automatic replication is disabled during tests, teardown failure can leave replication options altered. Tests also modify reveal-on-demand group membership, password policy, users, and temporary objects. The code uses unique tags and BasePasswordTestCase cleanup, but the blast radius is larger than pure LDAP unit tests.

Security-sensitive risks under test include stale RODC password caches after RWDC password changes, unauthorized SendToSam updates for users outside reveal policy, divergent lockout counters between RODC and RWDC, and authentication accepting too-old passwords after multiple changes.

## Test Signals

Passing results signal that RODC credential caching, password-cache invalidation, reveal-on-demand policy, lockout propagation, LDAP authentication forwarding, and object replication behave coherently across forced RWDC-to-RODC synchronization. Failures point to regressions in replication control, secret preloading, SendToSam, password history visibility, lockout computation, referral/replication behavior, or RODC/RWDC authentication routing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/rodc_rwdc.py -->
