# Research Report: subset-b-009918

Work item `subset-b-009918` covers two Samba AD DS database ACL test modules. The sections below are intentionally wrapped with reconciliation markers so the guard can split them into the source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/acl.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/acl.py

## Purpose

`acl.py` is a broad Python integration test suite for Samba's LDAP access-control behavior in the AD DC `SamDB` layer. It runs against a live LDAP endpoint supplied on the command line, constructs users, groups, OUs, computer accounts, RODC/DC join objects, security descriptors, and `dSHeuristics` settings, and verifies that Samba returns the same authorization outcomes expected for Active Directory-style ACL evaluation.

The suite covers add, modify, search, delete, rename, control-access-right password changes/resets, extended security descriptor reads, undelete/reanimate tombstone behavior, service principal name validation, and dynamic list/list-object visibility. It is not a unit-only test: it persists real directory objects temporarily and relies on cleanup to remove them.

## Important APIs, Types, and Helpers

- Command-line setup uses `optparse`, `samba.getopt.SambaOptions`, `CredentialsOptions`, `SubunitOptions`, and `TestProgram`. The required positional argument is a host or LDAP URL; plain hosts are converted to `ldap://host`.
- The module-global `lp` and `creds` are obtained once and reused by all tests. Credentials are sealed with `gensec.FEATURE_SEAL`.
- `AclTests` is the shared base class. Its `setUp()` opens an administrative `SamDB`, captures `base_dn`, `domain_sid`, `configuration_dn`, and an `sd_utils.SDUtils` helper, creates anonymous credentials, reads `STRICT_CHECKING`, and enables `DS_HR_ATTR_AUTHZ_ON_LDAP_ADD` by default with `set_heuristic(..., b'11')`.
- `set_heuristic(index, values)` reads the old `dSHeuristics`, registers cleanup to restore it, pads missing values with a default byte string, splices in the requested values, and writes the result back. It is central to tests for attribute authorization on LDAP add, owner implicit rights, userPassword behavior, and list-object mode.
- `get_creds()` and `get_ldb_connection()` create non-admin sealed, non-Kerberos `Credentials` and `SamDB` connections for specific test users. This lets each test exercise access checks as the user under test.
- `sd_utils` APIs are used heavily: `get_object_sid()`, `dacl_add_ace()`, `dacl_delete_aces()`, `get_sd_as_sddl()`, `read_sd_on_dn()`, and `modify_sd_on_dn()`.
- `security.descriptor.from_sddl()` plus `ndr_pack()` are used to build `nTSecurityDescriptor` values for LDAP add/modify and to set selective `sd_flags` controls such as `SECINFO_DACL`, `SECINFO_OWNER`, and `SECINFO_GROUP`.
- LDB primitives include `SamDB.add/modify/modify_ldif/search/delete/rename`, `Message`, `MessageElement`, `Dn`, LDAP scopes, mod flags, controls such as `show_deleted`, `show_recycled`, and `tree_delete`, and expected `LdbError` codes.
- `AclVisibiltyTests` uses `samba.tests.DynamicTestCase` to generate a matrix of visibility tests from environment (`fDoListObject`), allow/deny mode, and `SEC_ADS_LIST` / `SEC_ADS_LIST_OBJECT` combinations.

## Test Class Coverage and Control Flow

- `AclAddTests` creates two domain admins, regular users, and nested OUs, then tests `Add` authorization for users, groups, computers, optional attributes, system-must-contain attributes, password attributes, and explicit `nTSecurityDescriptor` on add. It verifies create-child (`CC`), write-property (`WP`), self-write (`SW`), write-DAC (`WD`), write-owner (`WO`), SACL privilege errors, invalid owner errors, owner/group/DACL/SACL handling under `BlockOwnerImplicitRights`, and anonymous add denial.
- `AclModifyTests` creates several users/groups, then covers ordinary property writes, multi-attribute atomic failure, `PRINCIPAL_SELF`, self-membership, `sDRightsEffective`, `nTSecurityDescriptor` DACL/owner/group modifications with `sd_flags`, owner implicit rights for computer accounts, and extensive `dNSHostName`/SPN validated-write behavior. The DNS tests compare validated write (`GUID_DRS_DNS_HOST_NAME`) with normal write-property rights, validate prefix/suffix/case/account-name rules, update `msDS-AllowedDNSSuffixes` with cleanup, and check multi-operation ordering when DNS host names and SPNs are modified together.
- `AclSearchTests` builds controlled OU trees with inheritance stripped/protected and verifies anonymous rootDSE behavior, anonymous subtree denial unless `dSHeuristics` permits anonymous access, list-contents (`LC`) visibility, explicit deny behavior, creator visibility, attribute filtering by `Read Property`, filter behavior when attributes are unreadable, and special always-visible attributes.
- `AclDeleteTests` checks default delete denial, delete allowed through authenticated-users or user-SID `SD` rights, and anonymous delete denial.
- `AclRenameTests` validates same-OU and cross-OU rename rights. It checks combinations of RDN attribute `WP`, delete-child/delete (`DC`/`SD`), create-child (`CC`) on destination containers, inherited rights, object-SID grants, and explicit deny for domain admins.
- `AclCARTests` changes `dSHeuristics` and `minPwdAge` to allow password-focused testing, then distinguishes write-property rights from control access rights for changing and resetting `unicodePwd`, `userPassword`, and `dBCSPwd`. It checks default change-password ACE removal, reset-password CAR, explicit WP denies, uneven delete/add modify sequences, and known Windows/domain-level variations.
- `AclExtendedTests` verifies that `Read Property` and `Read Control` alone do not expose `nTSecurityDescriptor` to an ordinary user, while a domain admin can read it.
- `AclUndeleteTests` creates users, deletes them, locates deleted objects by GUID with `show_deleted`, and exercises undelete via `isDeleted` deletion plus `distinguishedName` replacement. It verifies RDN write-property denial, irrelevant `isDeleted`/DN write-property denies, additional attribute writes during undelete, destination create-child denial, delete-right irrelevance, and Reanimate-Tombstone CAR denial.
- `AclSPNTests` provisions a workstation computer plus synthetic RWDC/RODC join objects using `DCJoinContext`, then verifies SPN modifications under full admin write-property and validated-SPN (`GUID_DRS_VALIDATE_SPN`) rights. It distinguishes workstation, RWDC, RODC, and user-object behavior, including disallowed SPN add/delete sequences.
- `AclVisibiltyTests` dynamically generates many list/list-object cases. For each generated case it rewrites OU DACLs, computes expected visibility from parent/object allow/deny bits and `fDoListObject`, runs base/onelevel/subtree searches as admin and user, and verifies both object presence and whether the `name` attribute is readable.

## State and Persistence Behavior

The file mutates a live Samba AD database. It creates and deletes users, groups, OUs, computer accounts, deleted-object tombstones, DC/RODC join artifacts, domain attributes, and security descriptors. Most classes use `tearDown()` plus `delete_force()` to remove test objects. `addCleanup()` is used for restoring global state such as `dSHeuristics`, `minPwdAge`, `msDS-AllowedDNSSuffixes`, and the administrative connection.

Persistence-sensitive behaviors include:

- `dSHeuristics` is repeatedly changed; failures before cleanup can leave global access-check knobs modified.
- `msDS-AllowedDNSSuffixes` is temporarily replaced or deleted and restored.
- `PasswordCommon.allow_password_changes()` and explicit `minPwdAge` changes alter password-policy-sensitive state.
- `DCJoinContext.join_add_objects()` creates DC/RODC objects that are cleaned via `cleanup_old_join()`.
- Deleted-object tests intentionally leave objects in deleted state until undelete/cleanup paths run.

## Dependencies and Integration Points

The suite depends on Samba's Python bindings and an operational AD DC test target. It integrates with:

- `samba.samdb.SamDB` for LDAP CRUD, domain metadata, DNS domain names, user/group helpers, and policy reads/writes.
- `samba.dsdb` GUID constants, account-control flags, group type constants, and `dSHeuristics` indexes.
- `samba.dcerpc.security`, `drsuapi`, and `misc` for SDDL parsing, access masks, SPN/DNS validated-write GUIDs, and DC join channel/replication flags.
- `samba.join.DCJoinContext` for synthetic DC/RODC account creation.
- LDB error codes and message APIs for expected LDAP failures.
- `samba.tests.subunitrun.TestProgram` for subunit-compatible execution.
- Environment variable `STRICT_CHECKING`, which tightens expected error messages/codes for some checks.

## Risks and Maintenance Notes

- This is a high-blast-radius integration test. A mid-test crash can leave global directory state altered, especially `dSHeuristics`, password policy, domain allowed DNS suffixes, and joined DC/RODC artifacts.
- Many expected results encode AD-compatible edge cases and Windows-version variations. Some assertions intentionally allow alternate error codes when `STRICT_CHECKING` is false.
- Tests use hard-coded object names. Parallel execution against the same domain would collide unless isolated per target.
- The top-level host URL parsing uses `host.lstrip(start + 3)`, which appears suspicious because `str.lstrip()` expects a string of characters rather than an integer index. In ordinary plain-host use the branch is not exercised; URL input should be treated carefully.
- Several tests rely on ordering of multi-valued LDB results or generated dynamic test names; small LDAP behavior changes may require updating test expectations.
- The suite assumes sealed LDAP and disables Kerberos for tight loops; authentication or transport changes can alter performance and failure modes.

## Test Signals

The file itself is a large test signal for Samba ACL enforcement. Strong pass signals include exact `LdbError` code assertions (`ERR_INSUFFICIENT_ACCESS_RIGHTS`, `ERR_CONSTRAINT_VIOLATION`, `ERR_OPERATIONS_ERROR`, `ERR_NO_SUCH_OBJECT`, `ERR_UNWILLING_TO_PERFORM`), SDDL substring checks, `sDRightsEffective` comparisons, search result count/DN checks, and successful/failed modify/add/delete/rename operations under controlled ACEs. Run through Samba's Python test harness with a live AD DC host, for example by invoking the script with the target host and Samba/subunit options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/acl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/acl_modify.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/acl_modify.py

## Purpose

`acl_modify.py` is a focused Samba AD DC LDAP ACL regression test for deleting `dNSHostName` from a computer account. It verifies that an ordinary authenticated user who can bind to LDAP cannot delete the `dNSHostName` attribute, whether the delete is submitted as a structured `Message` or as LDIF, and whether the delete specifies the old value or deletes all values.

This file overlaps conceptually with the broader `acl.py` DNS hostname modify tests but narrows the scenario to deletion denial.

## Important APIs, Types, and Helpers

- Command-line parsing mirrors other Samba Python tests: `SambaOptions`, `CredentialsOptions`, `SubunitOptions`, and `TestProgram` require one host argument and create `ldaphost`.
- Module globals `lp` and sealed `creds` are shared across tests.
- `AclTests.setUp()` opens an administrative `SamDB` with `system_session(lp)` and records `base_dn`.
- `AclTests.get_ldb_connection()` builds sealed non-Kerberos credentials for a named user and returns a user-bound `SamDB`.
- `AclModifyTests.setup_computer_with_hostname(account_name)` creates a temporary user, binds as that user, creates an OU and computer account as admin, sets the computer's `dNSHostName` as admin, registers cleanup for the user and OU tree, and returns `(host_name, dn)`.
- The four tests use `Message`, `MessageElement`, `Dn`, `FLAG_MOD_REPLACE`, `FLAG_MOD_DELETE`, and `modify_ldif()` to exercise both LDB object-message and LDIF code paths.
- Assertions use `assertRaisesLdbError(ERR_INSUFFICIENT_ACCESS_RIGHTS, ...)`.

## Control Flow

Each test derives an `account_name` from the test id and truncates it to 63 characters, then calls `setup_computer_with_hostname()`. The setup helper creates `OU=<account_name>,<base_dn>`, creates `CN=<account_name>` below it as a computer with `sAMAccountName=<account_name>$`, computes `<account_name>.<domain_dns_name>`, and writes that value to `dNSHostName` as admin.

The tests then attempt deletion as the ordinary user:

- `test_modify_delete_dns_host_name_specified()` sends a `MessageElement(host_name, FLAG_MOD_DELETE, 'dNSHostName')`.
- `test_modify_delete_dns_host_name_unspecified()` sends a `MessageElement([], FLAG_MOD_DELETE, 'dNSHostName')`.
- `test_modify_delete_dns_host_name_ldif_specified()` sends LDIF with `delete: dNSHostName` followed by the concrete hostname value.
- `test_modify_delete_dns_host_name_ldif_unspecified()` sends LDIF with `delete: dNSHostName` and no value.

All four are expected to fail with insufficient access rights.

## State and Persistence Behavior

The test mutates a live LDAP directory. For each test it creates a user named `mouse`, creates an OU named after the test method, creates one computer account, and writes `dNSHostName`. `addCleanup()` removes the user with `deleteuser` and deletes the OU using `tree_delete:0`, which should remove the computer below it. The module also creates a global admin `SamDB` named `ldb` at the bottom, though the tests primarily use `self.ldb_admin`.

Because `mouse` is reused in every test, concurrent execution against the same domain could collide. The OU/account names are derived from test ids and are more isolated.

## Dependencies and Integration Points

The file depends on Samba's Python runtime, an AD DC LDAP endpoint, LDB message APIs, and Samba test harness helpers. Its main integration point is the directory server ACL path that evaluates delete operations for `dNSHostName` on computer objects. It also indirectly depends on `SamDB.domain_dns_name()` to construct a valid hostname before attempting deletion.

## Risks and Maintenance Notes

- The helper imports `samba.dsdb` but does not use it; this is harmless but not necessary for the current tests.
- Like `acl.py`, URL host parsing uses `host.lstrip(start + 3)`, which is suspicious for URL input.
- Cleanup depends on `tree_delete:0`; if the server refuses tree delete or the connection fails, temporary OUs/computers can remain.
- The fixed user name `mouse` makes these tests unsuitable for parallel runs against a shared domain without additional isolation.
- The tests only assert the LDAP error code, not the diagnostic string, so they are robust to server message text changes but may miss more subtle diagnostic regressions.

## Test Signals

The strongest signal is that all four delete attempts consistently raise `ERR_INSUFFICIENT_ACCESS_RIGHTS`. Together they cover both specified-value and all-values deletion through both programmatic `modify()` and text `modify_ldif()` interfaces. A pass confirms that the deny behavior is enforced below the API surface and is not an artifact of only one client-side request representation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/acl_modify.py -->
