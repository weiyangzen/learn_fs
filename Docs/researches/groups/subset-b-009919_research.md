# Research Group subset-b-009919

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_medley_performance.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_medley_performance.py

Purpose: this is a long-running AD DC performance medley that grows a temporary OU tree, exercises user/group/link churn, runs LDAP searches of different selectivity, and repeatedly performs `samba-tool domain join` against the populated database. It is intended as a performance signal rather than a pure correctness test.

Important APIs/types/functions: option parsing uses Samba, credential, version, and optional `SubunitOptions` groups; the legacy `ANCIENT_SAMBA` path falls back to `subunit.run.SubunitTestRunner`. `UserTests` owns all tests, backed by class-level `GlobalState` counters and `active_links`. Core helpers are `_add_users()`, `_add_users_ldif()`, `_test_join()`, `_test_unindexed_search()`, `_test_indexed_search()`, `_test_base_search()`, `_test_complex_search()`, `_test_member_search()`, `_test_memberof_search()`, `_link_user_and_group()`, `_unlink_user_and_group()`, `_test_link_many_users()`, `_test_link_many_users_batch()`, `_test_ldif_well_linked_group()`, and `_test_delete_many_users()`. The important external types are `SamDB`, `Message`, `MessageElement`, `Dn`, `LdbError`, LDAP scopes, and modify flags.

Control flow: module import parses `<host>`, builds `lp` and `creds`, normalizes a bare host to `ldap://` or `tdb://`, then runs either `TestProgram` or the ancient Samba fallback. Each test opens a new `SamDB`, computes a PID-scoped OU layout, reseeds randomness from the test number, and mutates shared `GlobalState` so later tests depend on earlier additions, links, and deletions. The test ordering is encoded in method names such as `test_00_03_*`, `test_09_02_*`, and `test_24_02_*`.

State and persistence behavior: the script deliberately leaves objects in the target database across test methods. The OU name includes `os.getpid()`, but there is no final tree delete; state persists until manually removed or overwritten by another run. `GlobalState.active_links` is an in-memory model used to avoid duplicate link add/delete operations and to choose victims for removal.

Dependencies and integration points: integrates with Samba Python modules from `bin/python`, the live AD database through `SamDB`, LDB modify/search APIs, and `samba.netcmd.main.samba_tool` for domain joins. `--use-paged-search` injects the `modules:paged_searches` LDB option.

Risks: this is order-dependent, destructive within its PID OU, and expensive. `_test_delete_many_users()` has a suspicious stale-link condition `if s >= x[0] > e` that can never be true for normal `s < e`, leaving `active_links` inaccurate after deletions. The join helper removes its tempdir only on success. Search timings are printed but not bounded by assertions, so regressions are detected by external performance comparison rather than test failures.

Test signals: successful subunit completion means Samba survived the churn, while stderr timing lines for indexed, unindexed, base, member, memberOf, and complex searches are the main performance signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_medley_performance.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_multi_bind.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_multi_bind.py

Purpose: this compact performance/stability test repeatedly binds to the same AD DC and performs a base search, stressing connection setup, authentication, session creation, and cleanup behavior.

Important APIs/types/functions: `UserTests.test_1000_binds()` loops from 1 to 999, constructs a `SamDB(host, credentials=creds, session_info=system_session(lp), lp=lp)`, then searches `samdb.domain_dn()` with `SCOPE_BASE` and `attrs=["*"]`. The module also carries the same `ANCIENT_SAMBA` compatibility harness as the performance tests.

Control flow: parse options and `<host>`, initialize global `lp` and `creds`, normalize host to `tdb://` for files or `ldap://` for names, then execute the single test through `TestProgram` or the old subunit runner. Each iteration creates a fresh `SamDB` object; no connection pool is reused.

State and persistence behavior: the test does not intentionally modify directory state. Persistent impact should be limited to server-side bind/session accounting and logs.

Dependencies and integration points: depends on Samba credential parsing, `system_session`, `SamDB`, LDB base searches, and the Samba subunit runner. It is meaningful against LDAP and local TDB URLs, though bind cost differs substantially.

Risks: it can be slow or noisy against remote DCs and may expose resource leaks only indirectly. It does not assert per-bind latency or verify connection teardown; failures arise from bind/search exceptions.

Test signals: success means 999 consecutive bind/search cycles completed. Runtime and server resource usage are the practical performance indicators.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_multi_bind.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_performance.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_performance.py

Purpose: this AD DC performance scenario builds a PID-scoped OU containing users, groups, and memberships, measures common LDAP search patterns, exercises repeated domain joins, and then deletes parts of the data. It is a smaller predecessor to the medley test.

Important APIs/types/functions: `GlobalState` tracks user and link offsets. `UserTests` provides `add_if_possible()`, `_prepare_n_groups()`, `_add_users()`, `_test_join()`, `_test_unindexed_search()`, `_test_indexed_search()`, `_link_user_and_group()`, `_unlink_user_and_group()`, random link helpers, and delete helpers. It uses `SamDB`, `Message`, `MessageElement`, `Dn`, `FLAG_MOD_ADD`, `FLAG_MOD_DELETE`, and `samba_tool`.

Control flow: each test method opens a `SamDB`, creates or reuses OUs, and advances class-level counters. Tests are ordered by numeric names to add 1k batches, link users in several shapes, perform joins and searches, add more users, randomly link users to many groups, then delete groups/users and run a final join. Host normalization and legacy runner handling happen at module tail.

State and persistence behavior: directory objects are intentionally retained across tests in the same run; `add_if_possible()` suppresses duplicate-add errors. There is no complete cleanup of the PID OU, so interrupted runs may leave data behind.

Dependencies and integration points: integrates with Samba's Python test harness, `SamDB` LDB operations, `samba-tool domain join`, the target LDAP/TDB database, and stderr consumers that collect timing output.

Risks: order dependence is high because later tests require earlier user/group counts. Random link tests swallow `LdbError`, so duplicate/invalid modifications can hide details. The tempdir created for joins is removed only after a successful join. Performance output is not converted into pass/fail thresholds.

Test signals: subunit success demonstrates functional survival through the workload; printed timings for indexed and unindexed searches and join duration are the useful regression signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_performance.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_provision_performance.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_provision_performance.py

Purpose: this performance test times and validates several `samba-tool domain provision` entry points and option combinations in temporary target directories.

Important APIs/types/functions: `UserTests.setUp()` creates a tempdir, `tearDown()` removes it, `_test_provision_subprocess()` invokes `bin/samba-tool domain provision` with `--targetdir`, `--realm`, `--domain`, and `--use-ntvfs`, while `test_02_00_provision_cmd_sambatool()` calls the in-process `samba_tool()` API. Other tests cover overwrite, server roles, blank provision, and partitions-only provision.

Control flow: the module parses options and credentials but does not use the supplied host beyond the shared harness. Each test provisions into either the shared tempdir or a named child directory. Test methods execute through `TestProgram` or the ancient subunit fallback.

State and persistence behavior: all provisioned databases and generated files live under the per-test tempdir and are removed during `tearDown()`. The subprocess path may leave partial state if provisioning crashes before cleanup.

Dependencies and integration points: integrates with both the CLI `bin/samba-tool` and Python `samba_tool` command dispatcher. It depends on local build artifacts, the provision subsystem, temp filesystem performance, and optional NTVFS behavior.

Risks: `_test_provision_subprocess()` contains `if options: options.extend(options)` and never appends the provided options to `cmd`, so server-role, blank, and partitions-only subprocess tests do not actually pass their requested options. Provisioning performance can vary heavily with filesystem and build configuration.

Test signals: pass/fail reflects command success. The external harness must measure duration; this file itself does not assert timing thresholds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_provision_performance.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_search_performance.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_search_performance.py

Purpose: this focused performance script creates users and groups, then stresses LDAP filter evaluation for indexed, unindexed, complex, `member`, and `memberOf` searches over linked and unlinked directory data.

Important APIs/types/functions: `UserTests` implements OU setup, `_add_users()`, `_add_users_ldif()`, `_prepare_n_groups()`, `_test_unindexed_search()`, `_test_indexed_search()`, `_test_complex_search()`, `_test_member_search()`, `_link_user_and_group()`, and `_test_link_many_users()`. It uses `itertools.product` to build a search-expression space, `random.sample()` to bound it, and LDB modify/search APIs for link setup and timing.

Control flow: after parsing host/credentials, each test opens `SamDB`, creates PID-scoped OUs if needed, and uses class-level `GlobalState` offsets to build a cumulative data set. Early tests add 1k users and measure searches, middle tests add more users via LDIF and normal adds, then link users to group 0 plus another group before repeating search workloads.

State and persistence behavior: test data persists for the process run and is not cleaned up automatically. Link state is not tracked in a set, so duplicate link attempts would surface as LDB errors, although the deterministic link pattern avoids most duplicates.

Dependencies and integration points: depends on Samba `SamDB`, LDB `Message`/`MessageElement`, LDAP search scopes, Samba test runner compatibility, and stderr timing collection.

Risks: all performance checks are wall-clock printouts without thresholds. Search samples are deterministic because the random seed is reset, but server data from previous runs can still affect timings if PID OUs collide or cleanup is incomplete. Complex filters include comparison operators that can stress parser and index behavior differently across backends.

Test signals: successful completion plus timing lines for each filter family provide regression evidence for AD search performance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_search_performance.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/asq.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/asq.py

Purpose: this correctness test validates LDAP Attribute Scoped Query (ASQ) control behavior, including combinations with paged results, server-side sort, and VLV.

Important APIs/types/functions: `ASQLDAPTest.setUp()` builds a random OU, twenty first-level groups, twenty second-level groups whose `member` values point to the first level, and one top group whose `member` values point to the second level. `test_asq()`, `test_asq_paged()`, and `test_asq_vlv()` assert that a base search with `controls=["asq:1:member"]` returns the referenced objects. `test_asq_vlv_paged()` expects `ERR_UNSUPPORTED_CRITICAL_EXTENSION` when ASQ, VLV, sort, and paged results are combined.

Control flow: the module parses host/credentials, creates a `samba.Ldb` connection in each test, force-deletes any stale OU, creates fixture entries, runs the control-specific search, and deletes the OU via tree delete in `tearDown()`.

State and persistence behavior: fixture state is isolated under a randomized OU and cleaned after each test. Only failed setup/teardown can leave state behind.

Dependencies and integration points: integrates with LDAP controls `asq`, `paged_results`, `server_sort`, and `vlv`, Samba's LDB wrapper, credential handling, and subunit runner. It checks behavior expected from Windows for the unsupported ASQ+VLV+paged combination.

Risks: ASQ transforms a base search into multi-entry output, so result counting and DN assertions are important. Random OU names reduce collisions but make failed leftovers harder to inspect. Imported symbols such as `ndr_unpack`, `Credentials`, and some LDB error constants are unused.

Test signals: tests assert exact result count, exclude the top DN, verify returned DNs are second-level member targets, validate nested members, and assert the unsupported-critical-extension error for the conflicting controls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/asq.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/attr_from_server.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/attr_from_server.py

Purpose: this test covers a corner case for the mandatory `fromServer` Object(DS-DN) attribute on `nTDSConnection`: an existing valid link can become dangling after the referenced server is deleted and tombstone-expunged, and unrelated modifications to the connection should still succeed.

Important APIs/types/functions: `FromServerAttrTest` connects to a local SamDB path with `samba.tests.connect_samdb()`. Helpers `set_attribute()` and `get_object_guid()` wrap LDB modify/search work. `test_dangling_server_attr()` creates a temporary server, an `nTDSDSA` object using `relax:0`, an `nTDSConnection` under the test DC from `os.environ["SERVER"]`, validates bad replacement failure, deletes the temporary server, expunges tombstones via `garbage_collect_tombstones()`, and modifies `description` again.

Control flow: the script accepts a local LDB filepath rather than a host URL because it needs system-only object creation. It builds configuration/site/server DNs from `DEFAULTSITE`, then executes one targeted test under `TestProgram`.

State and persistence behavior: the connection object is registered with `addCleanup(self.ldb.delete, ntds_conn)`, but the temporary server is deleted during the scenario. Tombstone garbage collection mutates persistent database state and intentionally removes the deleted server object.

Dependencies and integration points: integrates with Samba provision constants, `misc.GUID`, local SamDB internals, `relax` control, `show_deleted`, tombstone garbage collection, and the `SERVER` environment variable.

Risks: this must run against a local database, not a remote LDAP URL. It depends on wall-clock `time.sleep(1)` and manual tombstone lifetime `0`. Missing `SERVER` or unexpected site topology breaks DN construction. The test deliberately creates an inconsistent link state.

Test signals: it asserts valid modification before deletion, `ERR_CONSTRAINT_VIOLATION` for setting `fromServer` to a never-existing DN, visibility then expunging of the deleted server by GUID, and successful unrelated modification after the link target is gone.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/attr_from_server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/confidential_attr.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/confidential_attr.py

Purpose: this security regression suite verifies that confidential, RODC-filtered, and ACL-denied attributes cannot be disclosed by LDAP search filters, returned attributes, DirSync, deleted-object searches, or timing differences.

Important APIs/types/functions: `ConfidentialAttrCommon` builds the shared OU/users, modifies schema `searchFlags`, opens sealed admin and user `SamDB` connections, and defines assertion helpers for exact-match, wildcard, inverse, and negative searches. `ConfidentialAttrTest` covers confidential attributes and allow/neutral ACEs. `ConfidentialAttrTestDenyAcl` covers object and object-attribute deny ACEs. `ConfidentialAttrTestDirsync` adapts assertions to `dirsync:1:1:1000`, deleted objects, preserve-on-delete, and timing-attack checks. `RodcFilteredAttrDirsync` adds `GUID_DRS_GET_CHANGES` and uses `dirsync:1:0:1000` to test RODC-filtered attributes.

Control flow: setup creates an OU, one secret-bearing user, one unprivileged user, and additional users with the tested attribute. Tests first prove normal visibility, then set `SEARCH_FLAG_CONFIDENTIAL` or other flags, apply DACLs through `SDUtils`, and repeat searches as user and admin. DirSync tests search from the naming context base and add filters to restrict results to the fixture. The timing test creates `msFVE-RecoveryInformation`, crafts slow matching-rule filters, and compares timing uncertainty ranges.

State and persistence behavior: this suite mutates schema `searchFlags`, user objects, DACLs, deleted objects, and default confidential data. Cleanup restores searchFlags where registered and tree-deletes the OU. Failed runs can leave schema flags or DACL changes, so the setup includes a defensive reset for the selected attribute flags.

Dependencies and integration points: depends on Samba DSDB constants, LDB modify/search APIs, `sd_utils`, sealed GENSEC connections, NT security descriptors, DirSync controls, deleted-object filtering, and Windows-compatible confidential attribute semantics.

Risks: schema mutation is global and high impact. Timing assertions may be noisy on slow or loaded systems. Some negative-search expected behavior is documented as Windows-like hiding and varies by access rights. The host parsing branch uses `host.lstrip(start + 3)`, which is not a correct way to remove a URL prefix and is fragile if later code relies on bare `host`.

Test signals: result counts for filter families, attribute presence/absence checks for `None`, `*`, and specific attrs, admin sanity checks, expected no-results behavior for hidden DirSync attrs, deleted-object non-disclosure, and overlapping user timing ranges all signal correct protection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/confidential_attr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/deletetest.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/deletetest.py

Purpose: this deletion correctness suite verifies AD delete protection, tree-delete behavior, tombstone attributes, RDN mangling, preserved attributes, parent GUIDs, and deleted-object container placement for domain and configuration objects.

Important APIs/types/functions: `BaseDeleteTests` provides `GUID_string()`, `search_guid()`, and `search_dn()` using `show_deleted:1`. `BasicDeleteTests` checks delete protection and helper assertions `del_attr_values()`, `preserved_attributes_list()`, `check_rdn()`, and `delete_deleted()`. `BasicTreeDeleteTests.setUp()` creates users, a group with members, a site subtree, captures live objects and deleted-container GUIDs, then `test_all()` and `test_tree_delete()` perform deletion variants and call `check_all()`.

Control flow: after host parsing and `SamDB` setup, `test_delete_protection()` creates a non-leaf container and verifies plain delete fails while tree delete succeeds; it then checks protected DC, RID set, crossRef, Users, and Computers objects reject deletion as expected. Tree tests create fresh timestamped objects, delete them individually or via tree delete, then repeatedly search by GUID and validate tombstone metadata.

State and persistence behavior: test fixtures are persistent AD objects. Timestamped names reduce collisions, and `delete_force()` clears prior objects during setup. Deleted objects remain in deleted-object containers or under deleted parents as tombstones; this is intentional and inspected.

Dependencies and integration points: depends on Samba `SamDB`, LDB error constants, tree-delete and show-deleted controls, DSDB well-known deleted-object container GUIDs, and `schema_format_value` for objectGUID strings.

Risks: this test is destructive in the target domain/config partitions and should not run against production directories. It assumes specific AD protection rules and deleted-object placement. The repeated large assertions duplicate checks, making maintenance noisy but explicit.

Test signals: expected LDB errors (`ERR_NOT_ALLOWED_ON_NON_LEAF`, `ERR_UNWILLING_TO_PERFORM`, `ERR_NO_SUCH_OBJECT`), `isDeleted=TRUE`, absence of stripped attributes, preserved metadata, `name`/RDN `DEL:<GUID>` formatting, parent GUIDs, and rejected deletion of already-deleted DNs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/deletetest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/dirsync.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/dirsync.py

Purpose: this is the primary DirSync LDAP control regression suite for Samba AD, covering access rights, cookies, naming-context behavior, attribute filtering, deleted objects, linked attributes, extended DN formatting, confidential attributes, and RODC-filtered attributes.

Important APIs/types/functions: `DirsyncBaseTests` creates admin, simple, dirsync, and admin users, grants `GUID_DRS_GET_CHANGES`, and opens sealed no-Kerberos user connections. `SimpleDirsyncTests` covers normal DirSync behavior, errors, attributes, deltas, linked attributes, range retrieval, cookies, deleted items, and `extended_dn`. `SpecialDirsyncTests` mutates schema flags and provides shared confidential/filtered setup. `ConfidentialDirsyncTests`, `FilteredDirsyncTests`, and `ConfidentialFilteredDirsyncTests` assert visibility/empty-element behavior for `SEARCH_FLAG_CONFIDENTIAL`, `SEARCH_FLAG_RODC_ATTRIBUTE`, and both combined.

Control flow: setup builds a dedicated OU and test users, stores base/config DNs, grants DRS rights, and registers cleanup. Simple tests execute DirSync searches with controls such as `dirsync:1:0:1`, `dirsync:1:1:1`, large page sizes, incrementally updated cookie strings, and the linked-attribute flag `2147483648`. Special tests set schema `searchFlags`, add a confidential value, then compare normal LDAP, object-security DirSync, and GET_CHANGES DirSync outcomes.

State and persistence behavior: the suite mutates OUs, group membership, DACLs on the domain base, schema flags, and deleted objects. Cleanup tree-deletes OUs, removes DACL ACEs, and restores searchFlags for special tests. DirSync cookies are parsed and repacked with NDR/base64 for one compatibility case.

Dependencies and integration points: integrates with LDB controls, `SamDB`, `sd_utils`, DRSUAPI security GUIDs, `drsblobs.ldapControlDirSyncCookie`, `ndr_pack`/`ndr_unpack`, `delete_force`, and Samba's credential/test harness.

Risks: high global impact if cleanup fails, especially schema flags and domain DACL changes. Tests assume Windows-compatible DirSync edge semantics, including insufficient-access and unwilling-to-perform distinctions. Some assertions accept either missing or empty attributes unless `insist_on_empty_element` is requested, reflecting backend compatibility needs.

Test signals: exact LDB errors, required operational attributes (`objectGUID`, `parentGUID`, `instanceType`, `nTSecurityDescriptor`), empty deltas from reused cookies, deleted-object visibility, linked attribute range names, extended DN byte formats, and confidential/filtered attribute suppression or visibility under the correct rights.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/dirsync.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/dsdb_schema_info.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/dsdb_schema_info.py

Purpose: this schema regression test verifies that Samba updates the `schemaInfo` blob revision and invocation ID correctly when schema attributes or classes are added and renamed.

Important APIs/types/functions: `SchemaInfoTestCase` keeps a static `sam_db` connection. `_getSchemaInfo()` reads `schemaInfo` from the schema DN, unpacks it as `schemaInfoBlob`, and synthesizes revision 0 if absent. `_checkSchemaInfo()` expects revision increment and invocation ID stability. `_ldap_schemaUpdateNow()` triggers schema reload. `_make_attr_ldif()` and `_make_class_ldif()` generate schema LDIF with random OID suffixes. Tests are `test_AddModifyAttribute()`, `test_AddModifyClass()`, and `test_AddModifyClassLocalRelaxed()`.

Control flow: setup connects to `ldap://$DC_SERVER`, reads rootDSE for schema/base/forest details, and records the local invocation ID. Tests snapshot schemaInfo, add a schema object, call schemaUpdateNow, verify revision increment, rename the object, and verify again. The relaxed local test reconnects to `lp.samdb_url()` and passes `relax:0`.

State and persistence behavior: tests add and rename schema objects permanently; there is no deletion cleanup. The static connection persists across test methods, except the relaxed test overwrites `self.sam_db` with a local connection.

Dependencies and integration points: depends on environment variables described in the header, Samba test connection helpers, `schemaInfoBlob` NDR decoding, DRSUAPI/misc GUID support, schema update controls, and local/remote SamDB behavior.

Risks: schema changes are persistent and globally visible. Random OID suffixes reduce collisions but do not remove test artifacts. `_checkSchemaInfo()` always compares against the original pre-change blob in each test, so after a second schema modification it still expects `before + 1`, which may hide or expose revision semantics depending on server behavior.

Test signals: valid `schemaInfo` length/marker, revision increment, unchanged invocation ID equal to the DC invocation ID, and successful schema object rename.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/dsdb_schema_info.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/key_credential_link.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/key_credential_link.py

Purpose: this ACL suite validates access checks and constraints around writes to `msDS-KeyCredentialLink`, especially differences between normal Write Property and the validated write for computer objects.

Important APIs/types/functions: `AclTests` sets strict checking, opens admin `SamDB`, configures `dSHeuristics` for attribute authorization on LDAP add and owner rights behavior, and supplies credential/connection helpers. `AclKeyCredentialLinkTests` creates a user and computer, generates RSA public keys, builds `KeyCredentialLinkDn` values with `key_credential_link.create_key_credential_link()`, and exercises `_test_key_cred_link()`. Tests cover add, delete, replace, multiple values, malformed values, self vs other-object writes, computer vs user targets, and expected `ERR_INSUFFICIENT_ACCESS_RIGHTS` or `ERR_CONSTRAINT_VIOLATION`.

Control flow: setup deletes/recreates fixed test user/computer, sets the computer password, and opens user/computer-bound SamDB connections. Each test applies allow or deny ACEs for the schema attribute Write Property and validated write GUID, then attempts an LDB modify with `FLAG_MOD_ADD`, `FLAG_MOD_REPLACE`, or `FLAG_MOD_DELETE`.

State and persistence behavior: the suite mutates `dSHeuristics`, object DACLs, test users/computers, passwords, and `msDS-KeyCredentialLink` values. Cleanup restores `dSHeuristics`, deletes admin connection helpers, and force-deletes the test objects in `tearDown()`.

Dependencies and integration points: depends on Samba DSDB GUID constants, `BinaryDn`, key credential link helpers, `cryptography` RSA key generation, sealed GENSEC credentials, no-Kerberos user binds, and `SDUtils` DACL manipulation.

Risks: fixed object names can conflict with concurrent runs. DACL changes are layered during tests and rely on object deletion for cleanup. RSA generation adds CPU cost. A module-level `ldb = SamDB(...)` creates an extra admin connection outside the test classes and is not otherwise used.

Test signals: expected success/failure of LDAP modify operations under precise ACE combinations. The key behavioral signal is that Write Property permits broad mutation, while validated write is constrained to computer self-write, one value, valid format, no existing value, and no user/non-computer target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/key_credential_link.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/large_ldap.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/large_ldap.py

Purpose: this LDAP stress suite verifies Samba behavior for very large result sets, large attributes, iterator search error propagation, IOV/result size boundaries, and query timeout enforcement.

Important APIs/types/functions: `ManyLDAPTest.setUpClass()` creates one OU with 2000 child OUs and `test_unindexed_iterator_search()` iterates 2001 matching results through `search_iterator()`. `LargeLDAPTest.setUpClass()` creates 200 users with 2 MiB `jpegPhoto` values and distinct DACLs. `test_unindexed_iterator_search()` and `test_iterator_search()` compare small-attribute searches with searches that exceed response size limits. `test_timeout()` temporarily lowers `MaxQueryDuration` in the default query policy and verifies an expensive OR filter times out.

Control flow: fixtures are class-scoped for cost reasons. Tests first require an LDAP URL, then stream iterator replies, assert each reply is an `ldb.Message`, call `result()` where expected, and catch `LdbError` for size/time limit cases. Timeout testing modifies `lDAPAdminLimits`, opens a fresh connection so limits reload, runs a slow filter, and relies on `addCleanup()` to restore the policy message.

State and persistence behavior: class setup creates large persistent objects under randomized OUs and class teardown tree-deletes them. Timeout testing mutates a configuration policy and restores the original `lDAPAdminLimits` via cleanup.

Dependencies and integration points: depends on LDAP transport, `SamDB.search_iterator`, LDB size/time limit errors, `sd_utils` for per-object DACL churn, default query policy layout, and server-side chunking behavior.

Risks: resource intensive: roughly hundreds of MiB of attribute payload plus DACL work. Old Samba may drop sockets, so teardown recreates the connection. One size-limit path documents a client bug where the second iterator exception may not be raised, so the test accepts partial results instead of failing.

Test signals: exact counts for small searches, partial counts plus `ERR_SIZE_LIMIT_EXCEEDED` for oversized `jpegPhoto` searches, successful 100-result chunked large-attribute search, `ERR_TIME_LIMIT_EXCEEDED`, and duration bounded around the configured timeout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/large_ldap.py -->
