# subset-b-009921 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/linked_attributes.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/linked_attributes.py

## Purpose

`linked_attributes.py` is an integration test suite for Samba AD linked-attribute behavior. It exercises ordinary group `member`/`memberOf` links, deleted and deactivated link visibility controls, duplicate handling, replace/delete semantics, one-way and DN-binary linked attributes, self-links, and backlinks that are deliberately hidden from wildcard searches. The suite validates both Windows-compatible LDAP controls and Samba-internal reveal controls.

## Important APIs, Types, and Functions

- `LATests` is the single test case class. `setUp()` opens a privileged `SamDB`, creates `CN=LATests,<domain>`, and `tearDown()` tree-deletes it unless `--no-cleanup` is set.
- `add_object()` and `add_objects()` create test users, groups, containers, `msExchConfigurationContainer`, and `msDS-KeyCredential` objects under the suite container.
- `add_linked_attribute()`, `remove_linked_attribute()`, and `replace_linked_attribute()` build `ldb.Message` instances with `FLAG_MOD_ADD`, `FLAG_MOD_DELETE`, or `FLAG_MOD_REPLACE`.
- `attr_search()`, `assert_links()`, `assert_forward_links()`, and `assert_back_links()` wrap LDAP searches with optional controls such as `show_deleted`, `show_recycled`, `show_deactivated_link`, and `reveal_internals`.
- `get_object_guid()` returns a deleted-object-safe lookup handle used by tests that inspect tombstoned objects via `<GUID=...>`.
- Command-line options control cleanup and internal visibility: `--delete-in-setup`, `--no-cleanup`, and `--no-reveal-internals`.

## Control Flow

Each test creates an isolated object graph below `CN=LATests`. Basic backlink tests add users to multiple groups and assert that forward links on groups and computed backlinks on users stay synchronized. Deletion tests remove groups or users, then compare ordinary searches with searches using deleted/recycled/deactivated-link controls. Link-modification tests verify that adding or removing linked values increments the source object's `uSNChanged` where expected, while deleting a linked target removes visible forward links without bumping the source object USN.

The suite then scales the same contract across multi-valued operations: bulk add, bulk delete, replace, all permutations of member order, relaxed-control modifications, and object creation with initial `member` values. Duplicate linked values are expected to fail with `ldb.ERR_ENTRY_ALREADY_EXISTS`.

The later tests cover schema-specific linked attributes. Real one-way `addressBookRoots` keeps a forward reference to the deleted object's new deleted DN. The "pretend one-way" `addressBookRoots2` behaves like a normal linked attribute and drops the link. `test_self_link()` verifies a group can link to itself and can still be deleted. `test_la_invisible_backlink()` checks backlink visibility rules for `msDS-KeyPrincipalBL` and `msDS-KeyCredentialLink-BL`, including wildcard `*` searches, explicit attribute requests, search filters, and DN-binary link values.

## State and Persistence Behavior

The suite mutates the live directory: it creates a temporary container, adds/removes LDAP objects, modifies linked attributes, deletes objects, and reads tombstoned entries with LDAP controls. All intended persistent changes are scoped under the test container and removed with `tree_delete:1`; PSO-like external state is not touched. If cleanup is disabled or setup cleanup is skipped after a failed run, stale `CN=LATests` objects can affect subsequent runs.

Linked attribute state is stored by the DSDB link infrastructure rather than as ordinary local Python state. Visibility varies by search controls and schema flags. Some assertions intentionally query deleted objects by GUID because their DN changes after deletion.

## Dependencies and Integration Points

The file depends on `samba.samdb.SamDB`, `ldb`, `samba.auth.system_session`, and `samba.dcerpc.misc.GUID`. It integrates with Samba's DSDB linked-attribute module, schema definitions for `member`, `memberOf`, `addressBookRoots`, `addressBookRoots2`, `msDS-KeyPrincipal`, `msDS-KeyPrincipalBL`, `msDS-KeyCredentialLink`, and `msDS-KeyCredentialLink-BL`, plus LDAP controls for deleted/recycled/deactivated links and Samba internal link reveal behavior.

## Risks and Edge Cases

- Tests use a shared fixed container name; interrupted runs need `--delete-in-setup` or manual cleanup.
- Reveal-internals tests are skipped only when `--no-reveal-internals` is passed; environments that reject Samba-only controls need that option.
- Assertions sort link values, so ordering regressions are intentionally ignored while membership-set regressions are caught.
- DN-binary links with duplicate target DNs but different binary prefixes are subtle: backlinks may contain repeated target DNs and must preserve count.
- Deleted-object assertions depend on tombstone visibility and GUID-based lookup behavior.

## Test Signals

Strong signals include duplicate-add failures, exact forward/backlink sets after add/delete/replace, `uSNChanged` changes only on source-side explicit link edits, correct behavior of `show_deactivated_link=0`, visibility differences for hidden backlinks under `*` versus explicit attributes, and successful deletion of self-linked objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/linked_attributes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/login_basics.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/login_basics.py

## Purpose

`login_basics.py` sanity-checks that a normal AD user can authenticate over Kerberos, NTLM, and LDAPS simple bind, that bad passwords update bad-password state, and that password changes through `userPassword` affect subsequent authentication as expected. It reuses the password-lockout test base but focuses on ordinary login and recent-password behavior rather than full lockout cycles.

## Important APIs, Types, and Functions

- `BasicUserAuthTests` extends `BasePasswordTestCase`, inheriting account creation, credential cloning, lockout settings, LDAP/SAMR account validation, and login assertion helpers.
- `setUp()` initializes `host_url`, `host_url_ldaps`, `lp`, `global_creds`, and an admin `SamDB`, then delegates to the base setup that creates `lockout1krb5`, `lockout1ntlm`, and `lockout1simple`.
- `_test_login_basics(creds, simple=False)` is the core scenario used by all three tests.
- `test_login_basics_krb5()`, `test_login_basics_ntlm()`, and `test_login_basics_simple()` select credentials and transport.

## Control Flow

The core scenario picks the LDAP URL and expected `logonCount`/`lastLogon` relations based on the auth mechanism. Kerberos is expected to advance logon counters; NTLM and simple bind keep some counters equal in this test's expectations. It first checks the freshly prepared account state, then attempts a wrong password and expects `badPwdCount=1` and a newer `badPasswordTime`.

After a successful login with the correct password, the test changes the password four times through `userPassword` delete/add modifications on the user's own LDAP connection. It then discards credentials to avoid reusing cached Kerberos state and checks that an older password fails without incrementing `badPwdCount`. For the immediately previous password, Kerberos must fail while NTLM and simple bind are expected to succeed, matching the old-NT-hash grace behavior tested by Samba. Finally it verifies the newest password succeeds, while a too-old password fails and increments bad-password state.

## State and Persistence Behavior

The test mutates live user passwords and authentication metadata for accounts created by `BasePasswordTestCase`. Account attributes checked include `badPwdCount`, `badPasswordTime`, `logonCount`, `lastLogon`, `lastLogonTimestamp`, `userAccountControl`, and `msDS-User-Account-Control-Computed`. The base class restores domain lockout settings and deletes test users via cleanup. Kerberos credential objects are explicitly recreated between password attempts to avoid stale tickets affecting the result.

## Dependencies and Integration Points

The file depends on `password_lockout_base.BasePasswordTestCase`, `SamDB`, Samba credentials, `system_session`, and `UF_NORMAL_ACCOUNT`. It exercises DSDB password-change handling, LDAP bind paths for Kerberos/NTLM/simple bind, LDAPS requirements for simple bind, account metadata generation, and SAMR cross-checks performed inside `_check_account()`.

## Risks and Edge Cases

- Counter expectations differ by auth mechanism; changes in how NTLM/simple bind update `lastLogon` or `logonCount` will cause failures.
- Simple bind requires LDAPS and bind DN setup from the base class.
- Password history and old-password grace semantics are security-sensitive and intentionally asymmetric between Kerberos and NTLM.
- Cached Kerberos tickets can mask password changes if credentials are not recreated.

## Test Signals

The primary signals are wrong-password rejection, reset of `badPwdCount` after successful current-password login, successful chained `userPassword` changes, failure of too-old passwords, Kerberos rejection of the previous password, NTLM/simple acceptance of the previous password, and stable account-control flags throughout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/login_basics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ndr_pack_performance.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ndr_pack_performance.py

## Purpose

`ndr_pack_performance.py` is a performance-oriented test module for Samba's Python NDR bindings. It repeatedly packs, unpacks, and round-trips representative security descriptors and a compressed DRS replication sample to catch performance regressions and basic serialization correctness failures.

## Important APIs, Types, and Functions

- `BIG_SD_SDDL`, `LITTLE_SD_SDDL`, `CONDITIONAL_ACE_SDDL`, and `NON_OBJECT_SDDL` provide security descriptor fixtures with many object ACEs, fewer object ACEs, a conditional ACE, and ordinary non-object ACEs.
- `SCALE` multiplies loop counts; the source notes `100` for normal performance runs and `1` for testing the test.
- `UserTests.get_desc()` converts SDDL to `security.descriptor`; `get_blob()` packs a descriptor; `get_file_blob()` reads plain or gzipped binary fixtures.
- `_test_pack()`, `_test_unpack()`, and `_test_pack_unpack()` run tight loops against `__ndr_pack__`, `__ndr_unpack__`, `ndr_pack()`, and `ndr_unpack()`.
- Replication tests use `drsuapi.DsGetNCChangesCtr6` and `testdata/replication-ndrpack-example.gz`.

## Control Flow

The test class first exposes `test_00_00_do_nothing()` as a loop-overhead baseline. For each security descriptor fixture it constructs either an unpacked descriptor or a packed blob, then runs pack-only, unpack-only, and pack-unpack loops. The pack-unpack helper records the initial packed blob and asserts the final loop output still matches, giving a minimal correctness check while measuring repeated conversion cost.

The replication sample tests read a gzipped `DsGetNCChangesCtr6` blob. One test repeatedly unpacks the sample with a lower cycle count, and the other unpacks once then repeatedly packs the generated object. These cases exercise deeper generated NDR structures than the security descriptor tests.

## State and Persistence Behavior

The module is read-only. It reads a fixture under `testdata`, creates transient Python NDR objects and byte strings, and writes no directory or filesystem state. The only durable behavior is test runtime cost, controlled by `SCALE` and per-test cycle counts.

## Dependencies and Integration Points

It depends on `samba.ndr.ndr_pack`, `samba.ndr.ndr_unpack`, `samba.dcerpc.security`, `samba.dcerpc.drsuapi`, `gzip`, and the Samba test runner. It is an integration point for Python bindings generated from IDL, security descriptor SDDL conversion, conditional ACE support, and DRS replication NDR structures.

## Risks and Edge Cases

- The suite is runtime-sensitive; `SCALE=100` can be expensive on slow or instrumented hosts.
- It has limited assertions and is mainly a performance signal, so many semantic NDR bugs would need separate tests.
- Fixture path resolution assumes the test is run from a directory where `testdata/replication-ndrpack-example.gz` is reachable.
- Conditional ACE parsing and object ACE packing are important compatibility edges for security descriptor changes.

## Test Signals

Useful signals are elapsed-time changes per pack/unpack case, successful security descriptor round-trip blob equality, ability to parse conditional ACE SDDL, and successful unpack/pack of `DsGetNCChangesCtr6` replication data without exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ndr_pack_performance.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/notification.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/notification.py

## Purpose

`notification.py` tests Samba LDAP notification search behavior. It verifies that notification searches deliver modified objects, enforce the maximum number of outstanding notification searches, and reject unsupported notification filters and attributes.

## Important APIs, Types, and Functions

- `LDAPNotificationTest.setUp()` opens a `SamDB`, discovers the domain DN, reads rootDSE `tokenGroups`, unpacks a SID, and builds a `<SID=...>` DN for the current user.
- `test_simple_search()` compares normal search results with notification results after modifying `otherLoginWorkstations`.
- `test_max_search()` opens six notification iterators and expects five timeouts plus one admin-limit failure.
- `test_invalid_filter()` enumerates valid notification filter attributes and many invalid filter shapes, then checks every schema attribute other than the allowlist is rejected.
- The tests use `SamDB.search_iterator()` with `controls=["notification:1"]` and `timeout` values to observe asynchronous search behavior through Python iteration and `result()`.

## Control Flow

Setup resolves the current authenticated user by token-group SID. `test_simple_search()` first captures that user's baseline message via a SID DN search, then finds the same object under the domain subtree. It modifies `otherLoginWorkstations` to `BEFORE`, starts a notification subtree search with a one-second timeout, modifies the attribute to `AFTER`, iterates notification replies until the target object is observed, and expects `notify1.result()` to end with `ERR_TIME_LIMIT_EXCEEDED`.

`test_max_search()` starts `max_notifications + 1` notification searches. Iterating each handle should either time out or fail with `ERR_ADMIN_LIMIT_EXCEEDED`; exactly one admin-limit failure and five time-limit failures are expected.

`test_invalid_filter()` proves simple presence filters and OR filters over `objectClass`, `objectGUID`, `distinguishedName`, and `name` can be accepted until timeout. It then verifies AND, equality, range, substring, and NOT filters are rejected with `ERR_UNWILLING_TO_PERFORM`. Finally it walks schema `attributeSchema` objects with paged results and checks notification presence filters on non-allowlisted attributes are rejected, including a nonexistent attribute name.

## State and Persistence Behavior

The module mutates only the current user's `otherLoginWorkstations` attribute and deletes that attribute after the simple notification test. Notification search handles are transient server-side operations that consume per-connection or server notification slots until they time out or return an admin-limit error. The tests run only for LDAP URLs; TDB/local URLs are explicitly failed.

## Dependencies and Integration Points

The file depends on `SamDB`, `search_iterator`, LDAP notification controls, LDB error codes, rootDSE token group generation, NDR SID unpacking, schema searches, and paged-results controls. It directly exercises DSDB notification indexing/filter validation and server resource-limit enforcement.

## Risks and Edge Cases

- Notification tests are timing-sensitive because success is expressed as timeout after expected notifications are delivered.
- The max-notification count is hardcoded to five; configuration changes to notification limits require updating the test.
- The simple test modifies a real account attribute on the authenticated user and must clean it up even after failures.
- Valid filter semantics are deliberately narrow; broadening notification support requires revisiting many `ERR_UNWILLING_TO_PERFORM` expectations.

## Test Signals

Signals include receiving exactly one changed target object during notification search, timeout rather than success on accepted notification filters, one admin-limit rejection among six concurrent searches, rejection of unsupported filters and attributes, and correct cleanup of `otherLoginWorkstations`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/notification.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/password_lockout.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/password_lockout.py

## Purpose

`password_lockout.py` is Samba's broad AD account-lockout integration suite. It verifies lockout state transitions for LDAP login failures, `userPassword` and `unicodePwd` password changes with bad old passwords, SAMR password change/set operations, Protected Users behavior, PSO-driven lockout policy, explicit unlock paths, default long-duration settings, and observation-window behavior.

## Important APIs, Types, and Functions

- `PasswordTests` extends `BasePasswordTestCase`, creates admin and user LDAP connections, and adds secondary Kerberos/NTLM users used to perform password changes.
- `use_pso_lockout_settings()` creates a `PasswordSettings` object with lockout settings, applies it to a user, and changes domain defaults to prove the PSO is the effective policy.
- `_reset_samr()` clears `samr.ACB_AUTOLOCK` through SAMR.
- `PasswordTestsWithoutSleep` uses long lockout windows and tests unlock methods without waiting: LDAP `lockoutTime=0`, LDAP `userAccountControl`, SAMR, and `samba-tool user unlock`.
- `_test_userPassword_lockout_with_clear_change()` drives bad old-password changes against `userPassword`.
- `_test_samr_password_change()` drives `Net.change_password()` failures and lockout.
- Protected Users tests modify the domain Protected Users group and check NTLM/SAMR restrictions do not increment lockout.
- `PasswordTestsWithSleep` covers `unicodePwd`, full login lockout/unlock waits, PSO login lockout, and observation-window expiration.
- `PasswordTestsWithDefaults` checks lockout with default-length windows without sleeping until expiry.

## Control Flow

Base setup creates primary lockout users. `PasswordTests.setUp()` adds secondary users and binds as them. Cleartext `userPassword` tests start from a clean account, attempt password changes with wrong old passwords until `badPwdCount` reaches the threshold, and assert transition from Windows error `00000056` to lockout error `00000775`. Once locked, both wrong and correct old-password changes must fail. The test then proves password reset alone does not unlock the account, verifies locked users appear in `samba-tool user list --locked-only`, unlocks via the selected method, and confirms bad-password counters and `lockoutTime` reset.

SAMR tests use `samba.net.Net` as another user. A correct change proves the path works, then repeated bad old passwords must return `NT_STATUS_WRONG_PASSWORD` until the threshold and `NT_STATUS_ACCOUNT_LOCKED_OUT` after lockout. Unlocking through SAMR must reset bad counts and allow a subsequent successful change.

Protected Users tests add the test user to the Protected Users group. NTLM logins with wrong passwords must fail but keep `badPwdCount=0` and avoid `lockoutTime`. SAMR change/set password operations for protected users must return `NT_STATUS_ACCOUNT_RESTRICTION` without lockout, while LDAP password changes remain possible where expected.

`unicodePwd` tests mirror the cleartext path with UTF-16LE quoted base64 password values and include checks that SAMR unlock has no effect before actual lockout. Login lockout tests are inherited from the base class and run with sleeps to observe computed unlock after duration and bad-count decay after the observation window. The default class repeats key login lockout checks with long default durations but stops once lockout is reached.

## State and Persistence Behavior

The module heavily mutates domain and account state: lockout policy attributes, PSOs, test users, user passwords, `badPwdCount`, `badPasswordTime`, `lockoutTime`, `lastLogon`, `lastLogonTimestamp`, group membership, and SAMR account flags. Cleanup from the base class restores domain lockout settings and deletes test users; PSOs are cleaned with `addCleanup`. Some tests temporarily modify Protected Users membership and store an LDAP diff for cleanup or manual reversal.

Lockout state is persisted in LDAP attributes but also exposed through generated `msDS-User-Account-Control-Computed` and SAMR `acct_flags`. The tests distinguish stored `badPwdCount` from effective bad-password count after lockout duration or observation-window expiry.

## Dependencies and Integration Points

The suite depends on `password_lockout_base`, `SamDB`, LDB errors, `samba.dsdb` flags, `samr`, `security`, `PasswordSettings`, `Net`, `samba_tool`, `subprocess`, `ntstatus`, and UTF-16LE/base64 `unicodePwd` encoding. It integrates LDAP bind/authentication, DSDB password modification modules, PSO resultant policy, SAMR Query/SetUserInfo, Net password RPCs, command-line `samba-tool`, and special Protected Users restrictions.

## Risks and Edge Cases

- Timing-sensitive sleeps can flap on slow systems; no-sleep classes use long windows to reduce this.
- The file assumes error data strings such as `00000056`, `00000775`, and `0000052D` remain stable.
- Tests mutate Protected Users membership and user passwords; interrupted runs may leave accounts in altered states until cleanup.
- Kerberos and NTLM have different counter expectations, especially `logonCount` and `lastLogon`.
- PSO tests intentionally set domain lockout policy to different values; failures in cleanup can affect unrelated authentication tests.
- `samba-tool` subprocess tests depend on `bin/samba-tool` and command-line credential formatting.

## Test Signals

Important signals are exact bad-password count progression, `lockoutTime` creation and clearing, `msDS-User-Account-Control-Computed` lockout bit, SAMR `ACB_AUTOLOCK`, distinction between stored and effective bad counts, correct unlock behavior for all methods, PSO policy overriding domain policy, Protected Users avoiding lockout, expected NTSTATUS/LDB error codes, and successful post-unlock password changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/password_lockout.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/password_lockout_base.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/password_lockout_base.py

## Purpose

`password_lockout_base.py` provides the shared test harness for lockout and login tests. It creates test users, configures domain lockout policy, provides credential factories and login assertions, and most importantly cross-checks LDAP account attributes against SAMR account information so higher-level tests validate both directory and RPC views of account state.

## Important APIs, Types, and Functions

- `BasePasswordTestCase` extends `samba.tests.password_test.PasswordTestCase`.
- `_open_samr_user()` unpacks `objectSid`, verifies the domain SID, and opens the user by RID over SAMR.
- `_check_attribute()` implements comparison modes: `equal`, `greater`, `less`, `present`, `absent`, `ignore`, and `None` for missing.
- `_check_account_initial()` and `_check_account()` validate LDAP state and SAMR `QueryUserInfo` levels 3, 5, 16, and 21.
- `update_lockout_settings()` writes `lockoutDuration`, `lockoutThreshold`, and `lockOutObservationWindow` on the domain DN using negative 100ns tick values.
- `_readd_user()` deletes/recreates a user, sets an initial password, enables the account, performs a failure/success cycle to seed `badPasswordTime`, and supports simple-bind setup.
- `assertLoginFailure()` and `assertLoginSuccess()` wrap `SamDB` bind attempts.
- `setUp()` stores original domain lockout settings for cleanup, applies test policy, opens SAMR handles, and creates Kerberos, NTLM, and simple-bind test users.
- `_test_login_lockout()` and `_test_multiple_logon()` are reusable scenarios consumed by `password_lockout.py`.

## Control Flow

Setup begins by enabling sealed credentials, constructing a template credential object, reading current domain lockout attributes, and registering a cleanup LDIF to restore them. It applies a threshold of three, short duration/window defaults unless subclasses override them, calls `allow_password_changes()`, opens SAMR domain handles, and recreates three test users. `_readd_user()` initializes each account through LDAP, validates the all-zero account state, deliberately fails one login to create `badPasswordTime`, then performs a successful bind to reset counters.

`_check_account()` sleeps briefly to avoid timestamp-resolution races, searches LDAP for account state, validates requested attributes, opens the matching SAMR user, and maps `userAccountControl` plus computed flags to expected SAMR account flags. It then checks bad-password count, last-logon, and logon-count values across SAMR info classes and re-reads LDAP to ensure SAMR queries did not mutate directory state.

`_test_login_lockout()` drives the canonical login lockout sequence: wrong password, correct password reset, repeated wrong passwords until threshold, extra wrong/correct attempts while locked, optional sleep past lockout duration, correct login after computed unlock, observation-window expiry, and final correct login reset. `_test_multiple_logon()` checks repeated successful logons do not create bad-password state and update counters according to auth mechanism.

## State and Persistence Behavior

The base class writes domain lockout policy and test user objects in the live directory. It persists and later restores original domain settings with cleanup handlers. It creates LDAP connections and SAMR handles as test state, deletes the main LDAP connection in cleanup, and relies on inherited cleanup to run even after assertions. Account state under test includes stored LDAP attributes, generated computed flags, and SAMR's derived account-info fields.

## Dependencies and Integration Points

The file depends on Samba credentials, GENSEC sealing, `SamDB`, LDB primitives, `samba.dsdb`, `samr`, `security.dom_sid`, `ndr_unpack`, `delete_force`, and `PasswordTestCase`. It integrates domain policy writes, password modification modules, LDAP bind authentication, generated account-control computation, and SAMR RPC views of the same users.

## Risks and Edge Cases

- Short sleep windows are vulnerable to slow hosts or coarse timestamp behavior.
- Cleanup correctness is critical because domain lockout policy is global.
- `_check_account()` assumes a one-to-one mapping between LDAP state and SAMR info classes; intentional SAMR behavior changes require test updates.
- Kerberos and NTLM/simple bind have different expected logon counter behavior.
- Simple bind requires LDAPS and bind DN handling in `_readd_user()`.

## Test Signals

The strongest signals are LDAP/SAMR agreement, restoration of domain policy after tests, correct computed lockout and password-expired flags, stored versus effective bad-password count behavior, successful creation/reset of test users, and stable logon metadata across failure and success sequences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/password_lockout_base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/password_settings.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/password_settings.py

## Purpose

`password_settings.py` tests AD Password Settings Objects (PSOs), resultant PSO calculation, and related domain password policy behavior. It covers PSO precedence, direct versus group application, nested groups, equal-precedence GUID tie-breaking, invalid PSO locations, min/max password age, built-in and primary groups, permissions, user-add behavior, complexity, minimum length, and password history.

## Important APIs, Types, and Functions

- `PasswordSettingsTestCase` extends `PasswordTestCase`.
- `setUp()` connects to `SERVER_IP`, creates a temporary OU, allows password changes, snapshots domain defaults as `PasswordSettings(None, self.ldb)`, and tracks external objects for cleanup.
- `add_group()`, `add_user()`, `set_attribute()`, and `add_obj_cleanup()` are local object-management helpers.
- `assert_password_invalid()` and `assert_password_valid()` validate password set outcomes and expected `0000052D` policy errors.
- `assert_PSO_applied()` checks `msDS-ResultantPSO` and then verifies complexity, minimum length, and history enforcement for that PSO.
- `PSO_with_lowest_GUID()` implements equal-precedence tie expectation by fetching and sorting `objectGUID`.
- `get_ldb_connection()` creates a sealed LDAP connection as a regular test user for permissions checks.
- `format_password_for_ldif()` encodes quoted UTF-16LE `unicodePwd` values.

## Control Flow

Basic PSO tests create several PSOs with different precedence and password policy values, apply them to groups and users, then move group memberships and direct applies to prove the expected resultant PSO wins. Nested-group tests build membership chains and verify PSOs flow through nested groups; changing precedence and deleting PSOs must change the result. Equal-precedence tests apply PSOs with identical precedence and expect the lowest GUID to win, first through group membership and then through direct user application.

Invalid-location tests prove PSOs and Password Settings Containers cannot be created under an OU, and that a PSO placed under an invalid container outside the official Password Settings Container has no effect even if applied. Min-age tests sleep until `password_age_min` expires. Max-age tests compare `msDS-UserPasswordExpiryTimeComputed` against domain expiry using one-day deltas.

Special-group tests apply PSOs to `Domain Users`, `Domain Guests`, `Domain Admins`, and builtin groups, checking builtin groups are excluded while primary-group and nested-domain-group membership can influence resultant PSO. None-applied tests verify non-users, non-normal accounts, and `krbtgt` do not expose a resultant PSO. Permissions tests bind as an ordinary user and verify PSO creation, modification, and attribute reads are denied while admin operations succeed.

The add-user test demonstrates that a Domain Users PSO does not apply during a one-step LDAP add with `unicodePwd`, but does apply once the user exists and the password is modified. Domain history tests directly change `pwdHistoryLength` and confirm history enforcement, including transitions from zero to nonzero.

## State and Persistence Behavior

The suite creates a temporary OU and deletes it with `tree_delete:1`. PSOs and invalid containers live outside the OU, so their DNs are tracked in `test_objs` and deleted in `tearDown()`. Some tests modify domain `pwdHistoryLength`, but register cleanup to restore it. User password history and resultant PSO are real directory state, so helper `TestUser` mirrors old password lists to know which values should be valid after history length changes.

## Dependencies and Integration Points

The file depends on `samba.tests.pso.PasswordSettings`, `TestUser`, `PasswordTestCase`, `connect_samdb`, `create_test_ou`, `env_get_var_value("SERVER_IP")`, LDB modify flags, `samba.dsdb`, credentials/GENSEC sealing, and `unicodePwd` encoding. It integrates DSDB resultant-PSO computation, group expansion, primary group handling, schema superior rules, ACLs for PSO objects, password policy enforcement, generated expiry-time computation, and domain password-history attributes.

## Risks and Edge Cases

- Tests that sleep for min-age can flap if time resolution or scheduling is poor.
- GUID tie-breaking assumes byte-sort behavior from `objectGUID` values.
- Builtin group exclusion and primary-group inclusion are subtle and easy to regress in group expansion code.
- Permissions checks rely on default ACLs for the Password Settings Container.
- One-step user-add behavior intentionally mirrors Windows even though it may appear counterintuitive.
- Cleanup must remove PSOs outside the OU and restore `pwdHistoryLength`.

## Test Signals

Signals include exact `msDS-ResultantPSO` DN, accepted/rejected passwords for complexity, length, age, and history, PSO precedence changes after membership/preference changes, lowest-GUID tie-breaking, invalid-container no-op behavior, ordinary-user access denials, expected user-add policy behavior, and domain history enforcement when `pwdHistoryLength` changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/password_settings.py -->
