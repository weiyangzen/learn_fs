# subset-b-009968 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/repl_rodc.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/repl_rodc.py

## Purpose
`repl_rodc.py` is a Samba DRS torture test module for replication involving a read-only domain controller (RODC), with emphasis on secret replication, password-replication policy, and `msDS-RevealedUsers` metadata. It creates a temporary RODC account and joins enough RODC objects to exercise `DsGetNCChanges` as both administrator and RODC machine credentials.

## Important APIs, Types, And Functions
- `drs_get_rodc_partial_attribute_set()` builds a `drsuapi.DsPartialAttributeSet` by walking `attributeSchema`, excluding constructed, non-replicated, and RODC-filtered attributes, converting names through a temporary RODC schema.
- `DrsRodcTestCase` extends `drs_base.DrsBaseTestCase` and relies on `_ds_bind()`, `_getnc_req10()`, `_exop_req8()`, LDAP handles, and common DRS helpers from that base.
- `_create_rodc()` configures `DCJoinContext` fields for an RODC join, including never-reveal and reveal SIDs, `UF_PARTIAL_SECRETS_ACCOUNT`, RODC secure channel type, and DRS special secret processing flags.
- `_assert_in_revealed_users()` decodes `msDS-RevealedUsers` binary DN values using `BinaryDn` and `ndr_unpack(drsblobs.replPropertyMetaData1)` to check expected secret ATTIDs.

## Control Flow
`setUp()` creates a test OU, constructs a randomized RODC identity, creates RODC directory objects through `DCJoinContext`, opens a temporary samdb for schema ATTID conversion, builds RODC machine credentials, and binds DRS twice: once as admin and once as the RODC. Each test then creates users, sets passwords, optionally changes password-replication group membership, builds a `DsGetNCChanges` request for `DRSUAPI_EXOP_REPL_SECRET`, and asserts either success or `ERROR_DS_DRA_SECRETS_DENIED` (`8630`). The suite also tests follow-on requests that attempt to switch from a permitted chunked request to a secret request.

## State And Persistence Behavior
The test mutates live directory state: it creates a test OU, users, password values, RODC computer objects, local allow/deny attributes (`msDS-RevealOnDemandGroup`, `msDS-NeverRevealGroup`), and `msDS-RevealedUsers`. Cleanup delegates RODC object removal to `cleanup_old_join()` and base cleanup. State validation focuses on metadata versions and USNs in revealed-user entries, including password changes that should update `replPropertyMetaData1`.

## Dependencies And Integration Points
This file integrates Python bindings for `drsuapi`, `drsblobs`, `security`, `misc`, `ldb`, `Credentials`, `DCJoinContext`, Samba test helpers, and Samba DRS base helpers. It exercises server-side DRS secret handling, RODC PRP logic, ATTID mapping, binary DN metadata, and the join code path used to materialize RODC directory objects.

## Risks
The tests are timing-sensitive around metadata update visibility and include a five-second sleep noted as still flaky against Windows. They depend on exact ATTID lists and sorted PAS behavior. Several tests use broad exception handling, which can mask unexpected failures. The RODC setup mutates sensitive directory structures and must always clean up correctly to avoid later test contamination.

## Test Signals
Strong signals include denial with error `8630`, successful admin override, RODC success only when allowed by PRP, PAS ignored for secret replication, mismatch denial when one RODC tries to use another RODC's destination DSA, and `msDS-RevealedUsers` entries containing the five expected password-secret ATTIDs with correct version/USN changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/repl_rodc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/repl_schema.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/repl_schema.py

## Purpose
`repl_schema.py` tests schema naming-context replication between two writable DCs. It dynamically creates `classSchema` and `attributeSchema` objects, forces schema and domain replication, and verifies that schema cache updates, custom attributes, linked attributes, binary DN links, inheritance, and renames replicate correctly.

## Important APIs, Types, And Functions
- `DrsReplSchemaTestCase` extends `drs_base.DrsBaseTestCase`.
- `_schema_new_class()` and `_schema_new_attr()` create schema objects with randomized OIDs and call `_ldap_schemaUpdateNow()`.
- `_exop_req8()` builds a level-8 `DsGetNCChanges` request for targeted replication-object checks.
- `_check_object()` confirms an object exists on both DCs, treating `ERR_NO_SUCH_OBJECT` on DC2 as a test failure.

## Control Flow
`setUp()` disables automatic replication on both DCs, forces a clean bidirectional sync, and initializes a shared name prefix. Test cases create schema elements on DC1, update schema now, explicitly replicate the relevant NC to DC2, and verify expected objects. Specialized flows add custom attributes to classes, instantiate custom classes on domain OUs, test a link attribute's returned linked-attribute ATTID against `msDS-IntId`, create binary DN forward/back links, delete linked targets, and rename schema objects.

## State And Persistence Behavior
The module intentionally persists schema changes into the test domain for the lifetime of the environment. It avoids collisions with a timestamp prefix and random OID suffixes but does not remove schema objects, which is typical for AD schema tests because schema deletions are constrained. It temporarily disables automatic replication and restores it in `tearDown()`. Domain OU instances created for domain-NC tests are explicitly deleted where practical.

## Dependencies And Integration Points
It depends on `ldb`, DRSUAPI Python bindings, `misc.GUID`, `samba.dsdb` constants, `drs_DsBind`, and base helpers for replication and schema update. Integration points include the LDAP schema update path, DRS schema NC replication, DRS linked attribute encoding, and schema cache lookup by `attributeID_id` versus `msDS-IntId`.

## Risks
Schema tests are high impact because schema changes are effectively permanent. Random OIDs and names reduce collisions but can still fail if schema constraints or functional level differ. The link attribute test branches on `domainFunctionality` and assumes `msDS-IntId` exists only above Windows 2000 functionality. Replication ordering between schema NC and domain NC is critical for tests that instantiate newly defined classes.

## Test Signals
Signals are existence of new schema objects on both DCs, custom attributes available on newly created classes/OUs, linked attributes not returned with `msDS-IntId` in the schema NC object-replication path, binary DN links surviving replication and target deletion, and renamed classSchema objects visible on DC2 after forced schema replication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/repl_schema.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/repl_secdesc.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/repl_secdesc.py

## Purpose
`repl_secdesc.py` verifies security descriptor inheritance across DRS replication. It focuses on inherited ACE propagation for new objects, existing objects, renamed objects, moved subtrees, and conflict-renamed children.

## Important APIs, Types, And Functions
- `ReplAclTestCase` extends `drs_base.DrsBaseTestCase`.
- `sd_utils.SDUtils` is used to add ACEs and read SDDL from both DCs.
- The important SDDL fragments are `mod` (`(A;CIOI;GA;;;SY)`), `mod_becomes` (`(A;OICIIO;GA;;;SY)`), and `mod_inherits_as` (`(A;OICIIOID;GA;;;SY)`).
- Tests rely on `_disable_all_repl()`, `_net_drs_replicate()`, and `_enable_all_repl()` to control replication points.

## Control Flow
`setUp()` creates a parent OU, initializes SD helpers for both DCs, disables replication, and synchronizes both DCs. Individual tests add inheritable ACEs either before or after child creation and before or after replication. Rename tests create OUs outside the protected parent, replicate them, add parent ACEs, move them under the parent, then force replication and compare SDDL. The conflict test creates a same-name child on DC2, applies inherited ACLs and a rename on DC1, replicates to trigger conflict handling, then replicates back.

## State And Persistence Behavior
The test mutates OU trees and their `nTSecurityDescriptor` values. The parent test OU is deleted with `tree_delete:1` during teardown. Replication is disabled during test setup and restored afterward. The important persistent state under assertion is the normalized SDDL on DC1 and DC2 after DRS applies inherited ACEs.

## Dependencies And Integration Points
This file integrates with Samba ACL/security descriptor helpers, LDB object creation and rename operations, and DRS replication metadata handling. It tests the DSDB/repl metadata path that recalculates inherited security descriptors when parent ACLs arrive, objects are moved, or conflict DNs are produced.

## Risks
The function names contain the misspelling `inheirt`, which is harmless but affects test discovery names. The tests assume SDDL normalization is stable and identical between DCs. Conflict tests depend on replication winner behavior and may be sensitive to object versioning and ordering. Cleanup must remove nested OUs or later tests may see inherited ACL residue.

## Test Signals
Expected signals include parent SDDL containing `mod_becomes`, child SDDL containing `mod_inherits_as`, byte-for-byte SDDL equality between DC1 and DC2, `ERR_NO_SUCH_OBJECT` before expected replication, and inherited ACLs preserved after subtree moves and conflict resolution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/repl_secdesc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/replica_sync.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/replica_sync.py

## Purpose
`replica_sync.py` is a broad blackbox suite for `DsReplicaSync` and `samba-tool drs replicate` behavior. It verifies enabled/disabled inbound replication, forced replication, local replication, DN conflict resolution, LostAndFound placement, rename sequencing, deletion propagation, and reanimation conflicts.

## Important APIs, Types, And Functions
- `DrsReplicaSyncTestCase` extends `drs_base.DrsBaseTestCase`.
- `_create_ou()` creates OUs below a test root and returns object GUIDs.
- `_check_deleted()` searches by GUID with `show_deleted:1` and verifies tombstone location under Deleted Objects.
- `reanimate_object()` removes `isDeleted` and replaces `distinguishedName` to simulate object reanimation.
- Base helpers drive inbound replication settings and `samba-tool drs replicate` invocations.

## Control Flow
Setup creates a top-level OU and forces initial two-way sync. Simple tests toggle inbound replication and verify normal, blocked, forced, and local replication. Conflict tests disable inbound replication on both DCs, create same-DN objects or rename collisions with sleeps to force timestamp ordering, replicate in a chosen direction, and assert which GUID receives a `CNF:<guid>` conflict RDN. Cleanup deletes by GUID and forces replication so both sides see tombstones. Later tests cover LostAndFound when children arrive under deleted parents, complex rename ordering across parent moves, and a reanimated tombstone colliding with a new object.

## State And Persistence Behavior
The suite creates and deletes OUs on both DCs, disables inbound replication, and restores it in teardown. It tracks two primary GUIDs in `self.ou1` and `self.ou2`, with additional child GUIDs scoped to tests. Deletion checks explicitly inspect tombstones rather than merely absence, ensuring replicated delete metadata is present.

## Dependencies And Integration Points
It depends on Samba test OU helpers, LDB GUID binding syntax, `samba-tool drs replicate`, and base helpers for LostAndFound and Deleted Objects DNs. It exercises replication conflict algorithms, local replication mode, full-sync override behavior, high-watermark behavior indirectly, and command-line error reporting for disabled sinks.

## Risks
Conflict winner expectations depend on time ordering, so the tests use `time.sleep(1)` and can be timing-sensitive on slow or clock-skewed environments. Some tests print diagnostic names, which is useful but noisy. Because many tests disable replication, teardown restoration is essential. Name conflicts are intentional and must be isolated under the per-test root OU.

## Test Signals
Signals include `WERR_DS_DRA_SINK_DISABLED` for non-forced disabled inbound replication, successful forced/local replication, exact `CNF:<guid>` naming of losing objects, non-placement in LostAndFound for simple conflicts, placement in LostAndFound for orphaned children, RDN/name equality after conflict resolution, and tombstones under Deleted Objects on both DCs after cleanup replication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/replica_sync.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/replica_sync_rodc.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/replica_sync_rodc.py

## Purpose
`replica_sync_rodc.py` tests negative conflict behavior for single-object local replication into an RODC. It ensures Samba refuses replication cases where accepting a single object or rename would leave the RODC high-watermark inconsistent with an unresolved local DN conflict.

## Important APIs, Types, And Functions
- `DrsReplicaSyncTestCase` extends `drs_base.DrsBaseTestCase`.
- `_create_ou()` creates an OU in the domain NC and returns a string GUID through `get_string()`.
- `_check_deleted()` mirrors the writable-DC helper but expects string `TRUE` values.
- Tests use `_net_drs_replicate()` with `local=True`, `single=True`, and `forced=True`.

## Control Flow
Setup disables replication on DC1 and assumes DC2 is the RODC from the environment. Each test first fully replicates from DC1 to the RODC. `test_ReplConflictsRODC()` creates an object, single-replicates it to the RODC, deletes it on DC1 without replicating that deletion, creates a new same-DN object, and expects the next single-object replication to fail. `test_ReplConflictsRODCRename()` follows the same shape but collides by renaming a second object into the first object's DN after the RODC already has the old object.

## State And Persistence Behavior
The file mutates domain OUs on DC1 and relies on the RODC retaining a prior view. It deliberately avoids replicating delete state before introducing the conflict. It restores replication on DC1 in teardown but does not maintain a large cleanup framework because the success path is failure of replication, with cleanup attempts in exception paths.

## Dependencies And Integration Points
This integrates DRS local/single replication with RODC behavior. It depends on the test environment providing `DC2` as an RODC, Samba's GUID binding syntax, and base replication helpers. The integration point under test is protection against advancing replication state when a single-object update cannot safely resolve an RODC-side DN conflict.

## Risks
The tests intentionally expect exceptions and treat a non-exception as failure. Broad `except` blocks mean the exact failure code is not asserted, only that replication fails. If environment `DC2` is not an RODC, the semantics may not hold. Cleanup is less comprehensive than in `replica_sync.py`, so failures can leave test objects behind.

## Test Signals
The expected signal is failure of the final single-object local replication. A successful final replication is a hard test failure because it would imply the RODC accepted an update that could incorrectly advance the high-watermark.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/replica_sync_rodc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/ridalloc_exop.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/ridalloc_exop.py

## Purpose
`ridalloc_exop.py` tests RID allocation through `DsGetNCChanges` extended operation `DRSUAPI_EXOP_FSMO_RID_ALLOC`, plus offline RID master seizure and RID Set repair behavior. It also contains two replication-link tests for locally deleted objects in joined databases.

## Important APIs, Types, And Functions
- `DrsReplicaSyncTestCase` extends `drs_base.DrsBaseTestCase`.
- `_determine_fSMORoleOwner()` discovers RID FSMO owner/non-owner metadata, server account DNs, and RID Set DNs.
- `_check_exop_failed()` validates level-6 EXOP failure replies.
- `_test_join()` and `_test_force_demote()` create and remove temporary DC joins.
- Tests use `SamDB`, `dbcheck`, `drs_utils.drs_Replicate`, `system_session`, `admin_session`, `ndr_pack(security.dom_sid(...))`, and command wrappers for `fsmo seize`, `domain join`, and `domain demote`.

## Control Flow
The first tests build level-8 EXOP requests using base `_exop_req8()`, bind to the FSMO owner, and validate either unknown-caller failure for an invalid destination DSA or a successful three-object response containing RID Manager, target RID Set, and target server account. Role-transfer tests modify `becomeRidMaster`, allocate from the new master, and restore the original role in `finally`. Offline tests join a temporary DC, open its local `sam.ldb`, manipulate `fSMORoleOwner`, inspect or repair `rIDSetReferences`, and verify RID Set creation through `fsmo seize`, `dbcheck`, or `newuser()`. Later tests inject out-of-range object SIDs and verify `dbcheck` advances `rIDNextRid` and handles range rollover after seizure.

## State And Persistence Behavior
The test creates temporary joined DC directories under `self.tempdir`, modifies offline databases, seizes roles inside those local DBs, creates users/groups, and force-demotes corresponding server accounts from the live domain. It also temporarily transfers the live RID Master and restores it. Temporary directories are removed with `shutil.rmtree()`.

## Dependencies And Integration Points
Integration points include DRSUAPI EXOP replies, RID Manager FSMO state, Samba domain join/demote tooling, offline SamDB mutation, `dbcheck` RID Set repair, SID allocation, and replication metadata when linked attributes reference locally deleted objects. The final tests set `DSDB_FULL_JOIN_REPLICATION_COMPLETED_OPAQUE_NAME` to distinguish transaction-time full-join replication behavior.

## Risks
This is a high-risk test module because it changes FSMO role ownership, creates temporary DCs, seizes RID roles, and manipulates RID pools. Cleanup through demotion and role restoration must run even on assertion failure. Some checks assume exact object counts in DRS EXOP replies, except linked attribute counts are relaxed because RODCs can add links to server account objects. Duplicate user names in the rollover test may be environment-sensitive.

## Test Signals
Signals include level-6 EXOP responses, `DRSUAPI_EXOP_ERR_UNKNOWN_CALLER` for invalid DSA, `DRSUAPI_EXOP_ERR_SUCCESS` with three expected objects for valid RID allocation, `rIDSetReferences` appearing after seizure/dbcheck/user creation, `dbcheck` reporting fixed RID Set errors, `rIDNextRid` moving to injected high SID values, RID pool rollover after seizure, transaction commit failure before setting the full-join opaque, and success after setting it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/ridalloc_exop.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs.py

## Purpose
`samba_tool_drs.py` is a blackbox test suite for the `samba-tool drs` command family. It validates bind, KCC, options, replicate variants, local replication semantics, machine credentials, and `clone-dc-database` behavior with and without secrets.

## Important APIs, Types, And Functions
- `SambaToolDrsTests` extends `drs_base.DrsBaseTestCase`.
- `_get_rootDSE()` opens LDAP or local LDB SamDB connections and returns rootDSE attributes.
- `runsubcmd()`, `check_output()`, `_run_drs_kcc()`, `_net_drs_replicate()`, and inbound replication toggles come from the base/test framework.
- Local helper `get_num_obj_links()` parses object/link counts from `samba-tool drs replicate --local` output.

## Control Flow
Setup reads `DC1` and `DC2` environment variables and builds explicit command-line credentials. Basic tests run individual `samba-tool drs` subcommands and assert success text. Replicate tests cover synchronous/asynchronous DRS replication, `--local-online`, `--local`, full versus incremental counts, and `-P` or implicit machine credentials. The local replication test creates a temporary joined DC, performs full and incremental local pulls, creates a linked group/user change, verifies that pulling from the source sends objects plus one link, then verifies pulling from a peer with an up-to-dateness vector sends zero. Clone tests build a local clone, inspect rootDSE identity, verify secrets are excluded unless `--include-secrets`, and test demoting another DC out of the cloned database.

## State And Persistence Behavior
The file creates temporary join databases under `self.tempdir`, local `etc/private/state` directories, groups, users, and cloned `sam.ldb` databases. It disables inbound replication in one local replication scenario and restores it in teardown. TearDown also removes common Samba runtime files and directories from the working directory.

## Dependencies And Integration Points
This module integrates Samba command-line tools, live LDAP, local LDB databases, domain join/demote, replication metadata, up-to-dateness vectors, linked attribute replication, and secret-filtering behavior. It acts as end-to-end coverage from CLI parsing through DRS internals and database mutation.

## Risks
Assertions on command output text can break on wording changes even when behavior remains correct. Parsing object/link counts by scanning integers is brittle. Temporary joins must use unique NetBIOS names to avoid collisions. Clone/demote tests mutate local databases heavily and depend on exact object layout for server, NTDS Settings, machine, and optional DNS account objects.

## Test Signals
Signals include expected output fragments (`Site GUID`, `Repl epoch`, `successful`, `was started`, `Current DSA options`), full replication returning more objects than incremental replication, linked local replication returning at least two objects and one link, second pull returning zero objects/links, cloned rootDSE matching source server identity, `krbtgt` password absent unless secrets are included, successful removal of the other DC from a clone, and clone without `--targetdir` failing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_critical.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_critical.py

## Purpose
`samba_tool_drs_critical.py` is a focused blackbox regression test for `samba-tool drs clone-dc-database` when critical objects depend on a non-critical parent chain. It targets server behavior around `DRSUAPI_DRS_GET_ANC` combined with `DRSUAPI_DRS_CRITICAL_ONLY`.

## Important APIs, Types, And Functions
- `SambaToolDrsTests` extends `drs_base.DrsBaseTestCase`.
- The only test, `test_samba_tool_drs_clone_dc_critical_object_chain()`, uses live LDAP to move the Administrator object under a randomly named non-critical OU, then clones the DC database.
- Cleanup callbacks restore Administrator and delete the temporary OU.

## Control Flow
Setup collects `DC1`, `DC2`, and command credentials. The test connects to DC1 over LDAP, reads rootDSE, creates a random `OU=not-critical...` under the domain NC, renames the domain Administrator account (`SID-500`) into that OU, runs `samba-tool drs clone-dc-database`, opens the cloned local `sam.ldb`, and searches for `cn=administrator`. The final assertion requires the cloned Administrator DN to match the non-critical OU path.

## State And Persistence Behavior
The test temporarily moves the built-in Administrator object in the live domain, which is a significant directory mutation. `addCleanup()` restores Administrator to `CN=Users` and deletes the temporary OU. The clone is created in `self.tempdir` and cleanup removes generated Samba runtime directories.

## Dependencies And Integration Points
It depends on Samba LDAP helpers, SID binding rename syntax, `samba-tool drs clone-dc-database`, and local LDB inspection. The integration point is critical-object replication closure: a clone limited to critical objects must still replicate required ancestors so critical descendants have valid DNs.

## Risks
Moving Administrator is intrusive; cleanup correctness is essential. The test assumes the Administrator account has RID 500 and can be renamed in the test environment. Failures during clone could leave Administrator under the temporary OU until cleanup runs. It is sensitive to access control and protected-object behavior.

## Test Signals
The key signal is successful clone completion and exactly one Administrator object in the local clone, with DN equal to `cn=administrator,<temporary non-critical OU>`. Any clone failure or Administrator landing elsewhere indicates broken ancestor handling for critical-only replication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_critical.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_no_dns.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_no_dns.py

## Purpose
`samba_tool_drs_no_dns.py` tests building a joined DC database without DNS partitions and then adding ForestDNSZones and DomainDNSZones later through local DRS replication, `samba_upgradedns`, and `dbcheck`. It runs the same scenario for TDB and MDB backends.

## Important APIs, Types, And Functions
- `SambaToolDrsNoDnsTests` extends `drs_base.DrsBaseTestCase`.
- `_get_rootDSE()` returns both rootDSE and the connected SamDB.
- `_test_samba_tool_replicate_local_no_dns()` is parameterized by `self.backend`.
- Uses `BlackboxProcessError` handling because `dbcheck --fix` may return nonzero while still reporting checked/fixed entries.

## Control Flow
Each public test sets `self.backend` (`tdb` or `mdb`) and calls the shared helper. The helper joins a temporary DC with `--dns-backend=NONE`, full-sync replicates the escaped ForestDNSZones and DomainDNSZones NCs locally into the new database, verifies `msDS-hasMasterNCs` links are initially absent, runs `samba_upgradedns`, verifies those forward links appear, checks `msDS-NC-Replica-Locations` backlinks are initially absent, runs `samba-tool dbcheck --cross-ncs --fix --yes`, validates a clean cross-NC dbcheck, compares selected attributes with `ldapcmp`, verifies forward/back links for both DNS NCs, and demotes the temporary DC.

## State And Persistence Behavior
The test creates a temporary joined DC database and associated config under `self.tempdir`, adds DNS NCs after initial no-DNS provisioning, and repairs cross-NC references. The live domain sees a temporary DC account, which is removed through `domain demote --remove-other-dead-server`. Local runtime directories are removed in teardown.

## Dependencies And Integration Points
Integration spans `samba-tool domain join`, `samba-tool drs replicate --local --full-sync`, `samba_upgradedns`, `samba-tool dbcheck --cross-ncs`, `samba-tool ldapcmp`, LDB binary DN escaping, and both supported local backend stores. It validates interactions between NC replication and DNS upgrade/repair tools.

## Risks
The test assumes the environment can provision both TDB and MDB stores and can run DNS upgrade tooling. It depends on exact forward/backlink repair behavior and can fail if `dbcheck` output or return-code behavior changes. Demotion cleanup is required to avoid stale temporary DC objects.

## Test Signals
Signals include successful no-DNS join, successful local full-sync of both DNS NCs, zero `msDS-hasMasterNCs` and replica-location links before repair, one expected link/backlink after `samba_upgradedns` and `dbcheck`, clean cross-NC dbcheck, successful `ldapcmp` with filtered master/replica attributes, and successful demotion of the temporary DC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_no_dns.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_showrepl.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_showrepl.py

## Purpose
`samba_tool_drs_showrepl.py` is a blackbox suite for `samba-tool drs showrepl`. It validates human-readable output, JSON output, all-good pull-summary output including color behavior, and failure summary output when replication is deliberately disabled.

## Important APIs, Types, And Functions
- `SambaToolDrsShowReplTests` extends `drs_base.DrsBaseTestCase`.
- Regex constants describe GUID, hex option, and DN formats expected in command output.
- `_force_all_reps()` uses `drs_utils.drsuapi_connect()`, `DsReplicaGetInfo`, LDAP searches, and `_net_drs_replicate()` to force inbound or outbound replication with non-RODC live partners.
- Tests use `json`, `os.environ["NO_COLOR"]`, and `BlackboxProcessError` inspection.

## Control Flow
The text-output test runs KCC, forces bidirectional replication for config/domain/schema NCs, runs `showrepl`, splits output into header/inbound/outbound/KCC sections, and matches each section with regexes. The JSON test parses `--json` output and validates top-level keys and value types. The all-good summary test enables replication, forces all neighbor replication, then checks `--pull-summary` with plain, verbose, color yes/always/never/auto, and `NO_COLOR` combinations. The failure test disables replication on DC1, creates many unreplicated users under DC-specific OUs, repeatedly calls `--summary -v` until the command fails, and checks the failure report.

## State And Persistence Behavior
The suite mutates replication topology by running KCC, enabling/disabling replication, and creating temporary OUs/users. Cleanup callbacks remove created OUs and re-enable replication. It temporarily modifies `NO_COLOR` and restores it in `finally`.

## Dependencies And Integration Points
This integrates CLI showrepl formatting, DRS replica-info RPC, LDAP inspection of NTDS Settings/server objects, KCC connection objects, replication status counters, ANSI color policy, and summary failure detection. It also filters RODCs and deleted DCs in `_force_all_reps()`.

## Risks
Output-format tests are intentionally brittle and will fail on legitimate formatting changes. DN regexes are domain-shape-specific (`DC=com`), which may limit portability. The forced-failure test loops up to 100 changes and relies on replication status noticing disabled replication in time. Environment color behavior can vary if terminal detection changes.

## Test Signals
Signals include exact section headers, header GUID/option regex matches, inbound/outbound neighbor blocks for config/domain/schema NCs, KCC connection object details, JSON keys `repsFrom`, `repsTo`, `NTDSConnections`, and `dsa`, type/regex validation for JSON fields, `[ALL GOOD]` with or without ANSI green according to color settings, and forced failure output containing `There are failing connections`, `WERR_DS_DRA_SINK_DISABLED` or `WERR_DS_DRA_SOURCE_DISABLED`, and `consecutive failure(s).`
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_showrepl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/rpc/dssync.c -->
# sources/user-network-fs/samba/source4/torture/drs/rpc/dssync.c

## Purpose
`dssync.c` is a C torture suite for DRSUAPI `DsGetNCChanges` and `DsGetNT4ChangeLog`. It binds as administrator and as a simulated new DC, fetches naming contexts over DRS, converts replicated objects into DSDB/LDB form, and compares them against LDAP reads of the same objects.

## Important APIs, Types, And Functions
- `struct DsSyncTest` stores DRS bindings, LDAP context, naming-context DNs, old/new DC metadata, and credentials.
- `test_create_context()` parses the binding, enables sign/seal, resolves the server, initializes bind-info extension sets, and creates LDAP URL state.
- `_test_DsBind()` handles DRS bind, peer bind-info normalization across lengths 24/28/32/48/52, and policy handles.
- `test_LDAPBind()` creates an LDB connection with Samba handlers and paged searches.
- `test_analyse_objects()` loads schema from the DRS prefix map, converts replicated objects with `dsdb_replicated_objects_convert()`, fetches corresponding LDAP objects with show-deleted and extended-DN controls, normalizes messages, and compares differences.
- `test_GetNCChanges()`, `test_FetchData()`, and `test_FetchNT4Data()` implement the replication and NT4 changelog tests.

## Control Flow
The fixture creates context, binds admin DRS, binds LDAP, discovers domain/config/schema DNs, and binds as the simulated new DC. `test_FetchData()` selects either a configured partition or domain/config/schema and calls `test_GetNCChanges()` for each. `test_GetNCChanges()` builds level-5 or level-8 requests, applies compression/writeable-neighbor parameters, loops while `more_data` is true, accepts plain or compressed level-1/6 replies, updates high-watermarks, and analyzes each chunk. Optional password-blob logging decrypts and dumps selected secret attributes using the DCE/RPC auth session key. `test_FetchNT4Data()` loops `DsGetNT4ChangeLog` restart cookies and skips unsupported server roles/procnums.

## State And Persistence Behavior
The suite is mostly read-only against the target directory but maintains local high-watermark and restart-cookie state during fetches. If configured with `dssync:save_pwd_blobs_dir`, it writes secret blob files for inspected attributes. It opens DRS policy handles and unbinds both admin and new-DC handles in teardown.

## Dependencies And Integration Points
It integrates generated DRSUAPI NDR clients, DRS blob decoders, DCE/RPC auth, GENSEC session keys, LDB, DSDB schema conversion, LDAP extended controls, CLDAP/name resolution, and Samba torture fixtures. It is an important bridge test between raw DRS replication data and LDAP-visible directory state.

## Risks
LDAP and DRS are not byte-identical transports, so the comparison has explicit skips for secret attributes and `nTSecurityDescriptor` on Deleted Objects. Difference handling warns for certain forward-link mismatches because linked attributes may arrive separately. Optional secret dumping is sensitive and must be controlled. The test depends on server extension support, compression settings, and naming-context size.

## Test Signals
Signals include successful signed/sealed DRS binds, successful LDAP bind, successful schema load from remote prefix map, no unexpected DRS-vs-LDAP message differences, correct handling of compressed replies, high-watermark progress until `more_data` clears, supported or correctly skipped NT4 changelog behavior, and clean DRS unbinds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/rpc/dssync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/rpc/msds_intid.c -->
# sources/user-network-fs/samba/source4/torture/drs/rpc/msds_intid.c

## Purpose
`msds_intid.c` is a C DRS torture suite validating ATTID selection rules for attributes with `msDS-IntId`. It proves that schema NC replication uses prefix-map `attributeID_id` ATTIDs, while non-schema NC replication uses `msDS-IntId` when present.

## Important APIs, Types, And Functions
- `struct DsIntIdTestCtx` holds LDAP URL, NC DNs, credentials, DRS bind info, and LDB context.
- `PROVISION_LDIF_FMT` creates a custom normal attribute, linked attribute, updates the User class, and creates a user carrying both attributes.
- `_test_DsaBind()` binds DRS with required `GETCHGREQ_V8` and `GETCHGREPLY_V6` extensions plus baseline extension flags and saves the auth session key.
- `_test_provision()` applies generated LDIF and `schemaUpdateNow` operations over LDAP.
- `_test_GetNCChanges()` fetches a complete NC, accumulating chunks and linked attributes into a single level-6 counter.
- `test_dsintid_schema()` and `_test_dsintid()` assert ATTID rules for schema and non-schema NCs respectively.

## Control Flow
Fixture setup creates context, DRS-binds with required extensions, LDAP-binds, and provisions randomized schema/test data. `_test_GetNCChanges()` sends a level-8 request with writeable, init, periodic, get-ancestors, and never-synced flags, loops through `more_data`, advances high-watermarks, chains object lists, and appends linked attributes. `test_dsintid_schema()` fetches the schema NC, loads schema from the returned prefix map, and asserts every object and linked attribute ATTID equals `attributeID_id` and not `msDS-IntId`. Domain and configuration tests fetch non-schema NCs and assert attributes with `msDS-IntId` use that value, while attributes without it use `attributeID_id`.

## State And Persistence Behavior
The test provisions schema attributes and a test user into the live directory. Like many schema tests, it does not remove schema objects. It opens a DRS policy handle and unbinds it in teardown. Accumulated replication chunks are held in a temporary talloc context per test.

## Dependencies And Integration Points
This file integrates DRSUAPI RPC, LDB/LDAP schema updates, DSDB schema loading from DRS prefix maps, generated NDR structures, linked attribute replication, and Samba torture registration. It specifically exercises the mapping between DRS ATTIDs, `attributeID_id`, and `msDS-IntId` across naming contexts.

## Risks
The test permanently extends schema with randomized IDs, so repeated runs grow the schema. It assumes server support for required DRS extensions and correct schema update behavior before replication fetch. The linked attribute lookup uses `dsdb_attribute_by_attributeID_id()` even when validating `msDS-IntId` cases, making schema map correctness critical. Chunk accumulation manually chains lists and reallocates linked attributes, so memory ownership must remain under the test context.

## Test Signals
Signals include successful DRS bind with required extensions, successful LDIF provisioning, complete level-6 `DsGetNCChanges` fetches, schema NC ATTIDs equal to `attributeID_id` and not `msDS-IntId`, domain/configuration NC ATTIDs equal to `msDS-IntId` when present, fallback to `attributeID_id` otherwise, and the same checks for linked attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/rpc/msds_intid.c -->
