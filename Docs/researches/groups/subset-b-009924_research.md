# Research Report: subset-b-009924

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/sec_descriptor.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/sec_descriptor.py

## Purpose

`sec_descriptor.py` is a Samba AD DS integration test suite for security descriptor behavior on directory objects. It connects to a live or local `SamDB`, creates users, groups, OUs, schema classes, and configuration objects, then validates owner/group selection, DACL inheritance, `sd_flags` read/write semantics, constructed effective-rights attributes, and auto-inheritance side effects. The tests are not unit-isolated pure Python checks; they exercise Samba's LDAP/DSDB security descriptor stack, including SDDL parsing, NDR descriptor storage, ACL inheritance, and domain functional-level differences.

## Important APIs, Types, and Functions

The file uses `samba.samdb.SamDB` for directory operations, `samba.sd_utils.SDUtils` for security descriptor reads and mutation, `samba.dcerpc.security.descriptor` for SDDL-to-binary conversion, and `ndr_pack`/`ndr_unpack` for binary descriptor handling. `DescriptorTests` is the shared base class. It provides `get_users_domain_dn()`, helpers to create schema/configuration objects with optional `nTSecurityDescriptor`, `get_ldb_connection()` for non-admin user binds, and setup of `base_dn`, `configuration_dn`, `schema_dn`, `domain_sid`, and `sd_utils`.

`OwnerGroupDescriptorTests` creates eight users with different combinations of Enterprise Admins, Domain Admins, Schema Admins, and regular membership. Its large `self.results` table encodes expected `O:<owner>G:<group>` prefixes for Windows 2003-like and Windows 2008+ domain controller behavior. `DaclDescriptorTests` focuses on inherited ACE propagation. `SdFlagsDescriptorTests` validates `sd_flags` control behavior for owner, group, DACL, and SACL components. `RightsAttributesTests` validates constructed attributes `sDRightsEffective`, `allowedChildClassesEffective`, and `allowedAttributesEffective`. `SdAutoInheritTests` checks that explicit descriptor updates on parent/child OUs result in inherited ACE materialization and `uSNChanged` advancement.

## Control Flow

The module parses Samba, credential, and Subunit options, normalizes the host into `tdb://` or `ldap://`, enables sealing on credentials, and uses `TestProgram`. For remote LDAP it sets `ldb_options = ["modules:paged_searches"]` before the base class opens `SamDB`.

Each test class creates and deletes its own live directory objects. The owner/group tests run repeated patterns: bind as a test user, create an object in Domain, Schema, or Configuration naming contexts, fetch the resulting SDDL, extract the owner/group prefix with a regex, and compare it to the expected behavior table. Some tests first add creator rights to a parent DACL so a non-default principal can create children. Custom descriptor cases pass explicit SDDL or binary descriptors during object creation.

The DACL tests first create a clean protected OU by stripping inherited ACEs and setting protected flags. They then add parent ACEs with combinations of `CI`, `OI`, `IO`, `NP`, `ID`, generic rights, creator-owner SID, object attribute GUIDs, and object-class GUIDs. A child group or OU is created and the resulting SDDL is checked for exact transformed ACEs. Most tests also modify the child descriptor afterward to ensure inherited ACEs persist across descriptor rewrites.

## State and Persistence Behavior

The suite mutates persistent AD state: users, groups, OUs, schema class objects, configuration containers, display specifiers, DACLs on the schema NC root, and child security descriptors. Cleanup uses `delete_force()` and per-class `deleteAll()` methods, but failures can leave schema or configuration objects behind. Random schema class names reduce collisions but make leftover artifacts harder to inspect manually. The tests depend on domain controller functional level via `domainControllerFunctionality`, so expected owner/group SDDL changes across deployments.

## Dependencies and Integration Points

This file integrates with Samba's LDB modules, DSDB access checks, SDDL parser, NDR security descriptor representation, inherited ACL computation, object creation paths for `newuser`, `newgroup`, `create_ou`, raw LDIF adds, and LDAP controls such as `sd_flags`. It relies on well-known SIDs and constants from `samba.dcerpc.security`, `DS_DOMAIN_FUNCTION_2008`, and live membership in built-in administrative groups. It also assumes command-line credentials have enough privilege to create users, mutate schema/configuration descriptors, and read SACLs where needed.

## Risks and Edge Cases

The highest risk is environmental coupling. Tests alter security descriptors on high-value naming contexts and create schema objects; cleanup must run reliably. Several assertions are string-based SDDL exact matches, which is useful for regression coverage but sensitive to canonical ACE ordering and formatting changes. Some tests contain commented-out modify-inheritance checks marked as failing, showing known behavioral gaps. `ldb_options` is only assigned for LDAP hosts, but `DescriptorTests.setUp()` always passes it; this depends on the script's host normalization path assigning it before tests run in the exercised environments. The random schema class helper uses `self.ldb_admin.search()` rather than its `_ldb` argument when probing for collisions, which is intentional enough for admin discovery but couples helper behavior to the admin connection.

## Test Signals

Useful pass signals are exact owner/group prefixes across functional levels, preservation or removal of inherited ACEs according to Windows-compatible flag rules, correct `sd_flags` partial descriptor reads and writes, `nTSecurityDescriptor` presence only when requested or included by wildcard search semantics, effective rights changing after ACE grants, filtering read-only attributes out of `allowedAttributesEffective`, and `uSNChanged` increasing after DACL modifications. Failures here indicate regressions in authorization, descriptor canonicalization, inheritance propagation, LDAP control handling, or constructed security attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/sec_descriptor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/sites.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/sites.py

## Purpose

`sites.py` tests Samba AD site and subnet management helpers against a live directory. It validates `samba.sites` site creation/deletion semantics, `samba.subnets` subnet creation, deletion, rename, and site reassignment, permission failures for non-admin users, and a large Windows-compatible CIDR validation matrix for IPv4 and IPv6 subnet names.

## Important APIs, Types, and Functions

`SitesBaseTests` opens a system-session `SamDB`, captures the domain DN, domain SID, and configuration DN, and provides `get_user_dn()`. `SimpleSitesTests` calls `sites.create_site()` and `sites.delete_site()` and expects `SiteAlreadyExistsException`, `SiteNotFoundException`, and `SiteServerNotEmptyException` in duplicate, missing, and non-empty-site cases. `SimpleSubnetTests` creates two temporary sites in a transaction, removes them in teardown, and exercises `subnets.create_subnet()`, `delete_subnet()`, `rename_subnet()`, and `set_subnet_site()`.

The helper `get_user_and_ldb()` creates a temporary non-admin user, constructs sealed non-Kerberos `Credentials`, binds a separate `SamDB`, and registers cleanup for the user. It is used to assert that subnet create, rename, and delete operations fail with `ERR_INSUFFICIENT_ACCESS_RIGHTS`.

## Control Flow

The script parses a host, normalizes it to LDAP when needed, opens `SamDB` with command-line credentials and `system_session`, then runs Subunit tests. Site tests perform simple create/delete operations. Subnet tests set up two sites, create subnets under the configuration NC, search by `objectclass=subnet` and `cn=<cidr>`, and verify either object disappearance or updated `siteObject`.

CIDR validation is the largest control-flow block. `test_create_bad_ranges()` iterates invalid values, expecting `subnets.SubnetInvalid`; any accepted CIDR is deleted and recorded as a failure. `test_create_good_ranges()` iterates valid values, expects creation, verifies exactly one matching subnet exists, and deletes it. The matrices include network-bit alignment, mask range, address octet range, malformed strings, embedded NULs, type errors, leading zeros, RFC5952 canonicalization, IPv4-embedded IPv6 behavior, reserved ranges, and Windows-specific exclusions such as bitmask-looking IPv4 addresses.

## State and Persistence Behavior

The file creates and removes AD Sites container children and Subnets container children in the configuration partition. The setup transaction creates `testsite` and `testsite2`, and teardown deletes them. Individual subnet tests delete created subnets explicitly. Non-admin tests create `notadmin` under `CN=Users` and remove it via cleanup. Because test CIDRs are reused, failed cleanup can affect later test runs.

## Dependencies and Integration Points

The suite integrates with `samba.sites`, `samba.subnets`, `SamDB`, LDB searches, Samba credentials, GENSEC sealing, and LDAP access control enforcement. It depends on configuration partition schema and default `CN=Sites` layout. It also depends on `subnets` helper exception contracts, not just raw LDAP errors, so it is a regression test for helper API behavior.

## Risks and Edge Cases

The CIDR tests encode exact Samba/Windows compatibility choices that differ from general IP library acceptance rules. Updating validation code to follow only RFC behavior can break these tests. The non-admin username is fixed, so leftover objects can cause setup noise if cleanup fails. The tests assume enough administrative privilege to create sites and subnets and assume `Default-First-Site-Name` contains servers. Some malformed inputs are non-string Python objects; validation must reject before string-specific operations crash unexpectedly.

## Test Signals

Pass signals include duplicate and missing site/subnet operations raising the documented Samba exceptions, non-admin operations failing specifically with `ERR_INSUFFICIENT_ACCESS_RIGHTS`, rename leaving no old subnet object, site reassignment changing `siteObject`, all invalid CIDRs being rejected, and all valid CIDRs creating exactly one LDAP subnet object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/sites.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/sort.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/sort.py

## Purpose

`sort.py` validates Samba LDAP server-side sort behavior for AD user attributes. It creates a configurable number of test users with deliberately varied values, requests results through the `server_sort` control, and compares returned order against expected files generated from known behavior. It covers simple ASCII-ish data and a Unicode-heavy set intended to match Windows Server 2012 R2 ordering for difficult strings.

## Important APIs, Types, and Functions

The module uses `SamDB.search()` with controls like `server_sort:1:<reverse>:<attr>` and `server_sort:1:<reverse>:<attr>:<matching-rule-oid>`. `norm()` decodes bytes as UTF-8 when needed, normalizes with Unicode NFKC, and uppercases before comparison. `FIENDISH_TESTS` is a curated list of strings containing whitespace, fractions, combining-looking characters, embedded NULs, fullwidth text, case variants, diacritics, punctuation, and CJK text.

`BaseSortTests` owns test data creation, expected-result loading, cleanup, and shared assertions. `create_user()` constructs user attributes that exercise binary, numeric, timestamp, and locale-like sort behavior. `SimpleSortTests` sets `avoid_tricky_sort = True` and uses `simplesort.expected`; `UnicodeSortTests` uses full Unicode data and `unicodesort.expected`.

## Control Flow

At startup the script requires `DATA_DIR` for expected result files and `SERVER` for the host. Test setup opens `SamDB`, creates `ou=sort,<base_dn>`, creates `opts.elements` users, partitions attributes into binary-sorted, numeric-sorted, timestamp, int64, and locale-sorted sets, computes expected binary order directly in Python, and loads locale expected order from the results file.

`_test_server_sort_default()` loops over locale-sorted attributes and forward/reverse directions, requesting only the sorted attribute and comparing normalized returned values to expected order. `_test_server_sort_binary()` compares binary-like attributes with Python string order. `_test_server_sort_us_english()` repeats locale sorting with the AD matching rule OID `1.2.840.113556.1.4.1499`. `_test_server_sort_different_attr()` sorts by one attribute while returning a different attribute, computes expected pairs locally with binary, locale, or numeric comparators, and asserts the sort attribute is not returned unless requested.

## State and Persistence Behavior

Every test setup creates an OU and `opts.elements` users in the target directory. Teardown deletes the OU with `tree_delete:1`. The suite persists no files, but it reads expected files from `DATA_DIR`. The test data includes embedded NULs and non-ASCII values in AD attributes, so storage and retrieval paths must preserve those values enough for sort comparison.

## Dependencies and Integration Points

This file integrates with the LDAP server-side sort control implementation, schema syntax handling for binary/numeric/time attributes, matching-rule OID handling, LDB controls, Samba's `cmp` compatibility helper, Python locale collation, and external expected-result fixtures. It also uses `system_session(lp)` for privileged setup and cleanup.

## Risks and Edge Cases

The explicit `locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))` can fail on systems without that locale. The script requires environment variables rather than using the positional host argument for the final host value; missing `DATA_DIR` or `SERVER` exits before tests. Expected ordering is intentionally Windows-specific and can diverge from Python or Samba's local collation. Timestamp sorting has a documented Windows failure note in the diagnostic path. Embedded NUL values and Unicode normalization make this a sensitive regression test for string handling.

## Test Signals

Passing tests show that Samba's server-side sort returns the same ordered values as the expected fixtures for default and US English matching-rule sorts, handles binary-like and numeric attributes separately, honors reverse sorting, supports sorting by an attribute not returned in the result set, and keeps the unrequested sort attribute out of returned entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/sort.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/subtree_rename.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/subtree_rename.py

## Purpose

`subtree_rename.py` tests Samba AD behavior when an OU subtree is renamed while objects inside or outside the subtree are connected by linked attributes. It verifies that forward links, backlinks, and binary DN links are rewritten or preserved correctly after subtree moves and later deletes. It also includes a larger timing-oriented scenario that stresses rename performance after many links.

## Important APIs, Types, and Functions

`SubtreeRenameTests` opens `SamDB`, creates three OU DNs (`subtree1`, `subtree2`, `subtree3`), and provides helpers for object creation and linked-attribute mutation. `add_object()` and `add_objects()` create users, groups, and computers. `add_linked_attribute()`, `remove_linked_attribute()`, and `replace_linked_attribute()` build `ldb.Message` modifications over attributes like `member`. `add_binary_link()` constructs a binary DN value in `B:<hexlen>:<hexdata>:<dn>` form for `msDS-RevealedUsers`, and backlink checks inspect `msDS-RevealedDSAs`.

Assertion helpers `attr_search()`, `assert_links()`, `assert_forward_links()`, and `assert_back_links()` retrieve attributes with optional controls, normalize values to strings, sort, and compare expected link sets. `get_object_guid()` reads `objectGUID` and formats it through `misc.GUID`.

## Control Flow

Setup creates two source OUs and optionally deletes leftovers when `--delete-in-setup` is passed. Most tests create users, groups, and computers in different combinations across `ou1` and `ou2`, add normal group membership links plus binary revealed-user links, rename `ou1` to `ou3`, update expected DN strings with `.replace(self.ou1, self.ou3)`, delete one linked object, and assert final forward/backlink state.

The scenarios differ by which classes are moved: a whole tree, only groups, only users, non-computers while computers stay elsewhere, and a larger tree with 50 users, 10 groups, and 7 computers. The larger test records link and rename timings to stderr but does not assert elapsed time.

## State and Persistence Behavior

The suite mutates live directory state by creating OUs, users, groups, computers, normal links, and binary DN links. Teardown deletes all three test OUs with `tree_delete:1` unless `--no-cleanup` is used. Some tests delete moved objects after rename to ensure backlinks are cleaned. Because the DN replacement strategy assumes simple string substitution, object names are chosen so the OU suffix is the only relevant part replaced.

## Dependencies and Integration Points

The tests exercise Samba's subtree rename implementation, linked-attribute module, backlink maintenance, binary DN parsing and rewriting, `msDS-RevealedUsers`/`msDS-RevealedDSAs` semantics, LDB modify operations, and tree-delete behavior. They also integrate with debug coloring via `samba.colour` and use `binascii.hexlify` to construct binary DN prefixes.

## Risks and Edge Cases

Binary DN removal has a different formatting path than addition and appears less exercised by the current tests. The assertion helper permits duplicate backlink values, which matters because multiple binary links from one computer to one target can produce repeated backlinks. `assertRaisesLdbError(20, ...)` for duplicate binary link creation depends on the specific LDB error code. Cleanup can be intentionally disabled for debugging, leaving state that affects later runs. The big test is primarily a smoke/performance signal and lacks explicit post-rename correctness assertions.

## Test Signals

Pass signals include group `member` values following renamed DNs, `memberOf` backlinks reflecting surviving groups only, binary forward links rewritten to the new subtree DN, binary backlinks containing the expected source computers with duplicates where multiple binary values exist, deleted linked objects disappearing from backlinks, and large linked subtrees renaming without exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/subtree_rename.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/token_group.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/token_group.py

## Purpose

`token_group.py` verifies that Samba's constructed token group attributes and group-membership APIs agree with independent token calculations. It compares LDAP `tokenGroups` and `tokenGroupsGlobalAndUniversal`, internally computed `security_token` SIDs, Kerberos PAC SIDs, a manual transitive closure over group membership and primary groups, and SAMR `GetGroupsForUser` results.

## Important APIs, Types, and Functions

The module uses `SamDB`, `samba.auth.user_session()`, `AuthContext`, `gensec.Security`, `ndr_unpack(dom_sid, ...)`, `samba.dcerpc.samr`, and group type constants such as `GTYPE_SECURITY_GLOBAL_GROUP` and `GTYPE_SECURITY_UNIVERSAL_GROUP`. The recursive `closure(vSet, wSet, aSet)` helper expands membership edges. `StaticTokenTest` validates the current command-line user. `DynamicTokenTest` creates a controlled user and nested group graph, then validates token behavior under that graph.

`DynamicTokenTest.filtered_closure()` rebuilds membership edges from LDAP, adds primary-group edges, filters vertices by group type, and expands closure. This models the MS-ADTS/MS-DRSR algorithms used by `tokenGroupsGlobalAndUniversal` and SAMR checks.

## Control Flow

The script requires explicit Kerberos mode rather than `AUTO_USE_KERBEROS`, sets sealing on credentials, normalizes URL after class definitions, and runs Subunit tests. `StaticTokenTest.setUp()` reads rootDSE `tokenGroups`, constructs a `<SID=...>` DN for the user, computes a local session token with flags for default groups, authenticated identity, simple privileges, and NTLM when appropriate, and appends Kerberos-only asserted identity/claims SIDs when needed.

`DynamicTokenTest.setUp()` creates one user and seven groups: direct domain-local, global, and universal groups; a universal chain from global group to universal groups; a domain-local group containing a universal group; and another domain-local direct group. It binds as the test user, discovers the user's SID DN, and computes the session token. Tests compare rootDSE tokenGroups, DN tokenGroups subset behavior, Kerberos PAC groups, manual full tokenGroups closure, filtered global/universal closure, and SAMR output.

## State and Persistence Behavior

Dynamic tests create persistent users and groups under `CN=Users` and remove them in teardown with `delete_force()`. A separate no-member SAMR test creates and deletes `tokengroups_user2` inside the test. Group nesting is real AD state, so failures before teardown can leave objects that collide with later runs. Static tests do not create state but depend on the credentials used to run the test.

## Dependencies and Integration Points

The file covers LDAP constructed attributes, auth session construction, NTLM/Kerberos SID differences, GENSEC client/server Kerberos exchange, PAC parsing through `session_info()`, SAMR RPC over sealed `ncacn_ip_tcp`, primary group lookup, group type filtering, and SID-to-DN LDAP resolution. It depends on command-line credentials, machine credentials for the GENSEC server side, and an LDAP URL for rootDSE and SAMR host discovery.

## Risks and Edge Cases

Kerberos and NTLM add different extra SIDs, so expected missing sets must track authentication mode. Some tests call `self.fail()` when URL is not LDAP rather than skipping. `closure()` is recursive and mutates sets in place; it is fine for these small graphs but not cycle-optimized for arbitrary large domains. In `test_samr_GetGroupsForUser`, the condition after `res3 = ...` checks `len(res)` instead of `len(res3)`, which looks like a typo and can mask filtering mistakes. The manual algorithms depend on `memberOf` visibility and correct primaryGroupID SID resolution.

## Test Signals

Pass signals include exact rootDSE tokenGroups equality with internal session SIDs, DN tokenGroups being the expected subset of full token SIDs, Kerberos PAC SIDs matching internal token SIDs, manual closure matching LDAP constructed attributes, global/universal filtering matching `tokenGroupsGlobalAndUniversal`, SAMR returning the primary group plus expected global/universal memberships with default attributes, and a no-member user returning only the primary group.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/token_group.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/tombstone_reanimation.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/tombstone_reanimation.py

## Purpose

`tombstone_reanimation.py` validates Samba AD deleted-object restoration. It covers basic undelete operations, forbidden rename paths, restoration with attribute modifications, same-NC versus cross-NC constraints, and detailed attribute plus replication metadata expectations for users, password-bearing users, groups, OUs, and containers.

## Important APIs, Types, and Functions

`RestoredObjectAttributesBaseTestCase` connects with `samba.tests.connect_samdb_env()`, captures domain, schema, and configuration DNs, and calls `PasswordCommon.allow_password_changes()` so password tests can set user passwords. It provides `search_guid()` using `<GUID=...>` with `show_deleted:1`, `search_dn()` using `show_recycled:1`, `_create_object()`, attribute comparison helpers, `_check_metadata()`, and the static `restore_deleted_object()` helper.

`restore_deleted_object()` performs reanimation by modifying the deleted object DN with `show_deleted:1`, deleting `isDeleted`, replacing `distinguishedName`, and optionally replacing additional attributes. The metadata checks unpack `drsblobs.replPropertyMetaDataBlob` and compare ordered `(attid, version)` pairs using many `DRSUAPI_ATTID_*` constants.

## Control Flow

Basic restore tests create users or containers, capture GUIDs, delete objects, locate deleted objects by GUID, then restore by LDAP modify. Negative cases assert `ERR_NO_SUCH_OBJECT` without `show_deleted`, `ERR_UNWILLING_TO_PERFORM` for renaming a deleted object, `ERR_ENTRY_ALREADY_EXISTS` when the target DN is occupied, and `ERR_OPERATIONS_ERROR` when trying to restore across naming contexts.

The object-specific classes define expected attribute dictionaries and metadata arrays. `RestoreUserObjectTestCase` validates initial add state, deleted/recycled state, and restored state for a user without password. `RestoreUserPwdObjectTestCase` does the same with password and supplemental credential metadata, restoring with a replacement `userPassword`. Group tests ensure plain groups restore with expected defaults and that deleted group membership is not restored. Container tests ensure OUs and containers restore expected naming/category attributes while excluding attributes Windows does not restore, such as OU `description` and container `showInAdvancedViewOnly`.

## State and Persistence Behavior

The suite creates and deletes live AD objects and intentionally searches deleted/recycled objects. Restored objects retain original GUIDs and SIDs where expected. The recycle-bin enable helper exists but is not called by the visible tests; nevertheless tests expect `isRecycled` on deleted objects, so the target environment must support the relevant deletion behavior. Password tests modify password-related replicated attributes and permit password changes during setup.

## Dependencies and Integration Points

This file integrates with Samba's delete-object path, Deleted Objects container, recycled object visibility controls, LDAP modify semantics for reanimation, password handling, schema formatting for GUIDs, DRS replication metadata encoding, and Windows-compatible attribute stripping/restoration rules. It uses `ldb` error constants to verify exact failure modes.

## Risks and Edge Cases

The metadata assertions are intentionally strict about attid ordering and version numbers, with `None` used only where version variance is tolerated. Changes in replication metadata ordering, default attributes, password policy side effects, or Windows compatibility choices can break tests even if high-level restore works. Some local variables such as `orig_attrs` and `del_attrs` are computed but not used in a few tests, indicating historical comparison logic was simplified. Fixed object names can collide after interrupted runs, although many paths call `delete_force()` before creation.

## Test Signals

Pass signals include deleted objects being restorable by modify but not by rename, target-DN collisions and cross-NC restores failing with exact LDB errors, restored users retaining GUID/SID and expected account defaults, password-user metadata showing password-related version increments, groups restoring without `member`, OUs/containers restoring with expected `lastKnownParent`, and replication metadata matching the expected add/delete/restore transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/tombstone_reanimation.py -->
