# subset-b-009967 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/getncchanges.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/getncchanges.py

## Purpose

`getncchanges.py` is an integration test module for Samba Active Directory DRS `DsGetNCChanges` behavior. It constructs two-domain-controller replication scenarios and validates that paged replication, highwatermark handling, ancestor fetching, linked-attribute target fetching, deleted-object handling, cross-partition links, and naming-context root ordering do not lose objects or links.

The tests are not general library code. They are executable torture/subunit tests that drive real Samba DCs named by `DC1` and `DC2`, using `drs_base.DrsBaseTestCase` helpers for DRS binds, replication calls, highwatermark retrieval, GUID extraction, link extraction, and manual `net drs replicate` operations.

## Important APIs, Types, and Functions

The main class is `DrsReplicaSyncIntegrityTestCase`, derived from `drs_base.DrsBaseTestCase`. `setUp()` creates a per-test OU on DC2, points test LDAP state at DC2, records the base DN, and installs a `DcConnection` wrapper for the default DC. `init_test_state()` resets received DNs, links, GUIDs, the last DRS counter, `max_objects`, and booleans tracking whether GET_ANC and GET_TGT were actually used.

Core helpers include `add_object()`, `modify_object()`, and `delete_attribute()` for LDAP setup; `create_object_range()` for deterministic numbered OU trees; `assert_expected_data()` and `assert_expected_links()` for final coverage assertions; `assert_object_has_link()` for comparing replicated link GUID blobs against `extended_dn` LDAP results; `restore_deleted_object()` for clearing `isDeleted` and replacing `distinguishedName`; and `sync_DCs()` for explicit replication.

The central DRS client helpers are `_repl_send_request()` and `repl_get_next()`. `_repl_send_request()` reuses the previous response's `new_highwatermark` and `uptodateness_vector`, sets `DRSUAPI_DRS_WRIT_REP`, optionally sets `DRSUAPI_DRS_GET_ANC`, and optionally sends `DRSUAPI_DRS_GET_TGT` as a `more_flags` value. `repl_get_next()` calls `_get_replication()`, extracts DNs, GUIDs, and links from the returned ctr6, and recursively retries the same page with GET_ANC or GET_TGT when it sees an unknown parent, source GUID, or target GUID.

`DcConnection` stores a bound DRS connection, handle, default highwatermark, uptodateness vector, `ldb` connection, and DNS name for switching between DCs. `set_dc_connection()` copies that state back onto the inherited `DrsBaseTestCase` fields.

`DrsReplicaSyncFakeAzureAdTests` inherits the full integrity suite but overrides `modify_highwatermark()` to zero `reserved_usn`, modeling Azure AD / Entra ID Connect behavior. It skips most parent tests via `SKIPPED_TESTS`, leaving only cases expected to be meaningful under zeroed reserved USN.

## Control Flow and Scenarios

Most test methods follow a pattern: create ordered objects and optional linked attributes, start a paged replication cycle, mutate objects or links in the middle of the cycle, continue calling `repl_get_next()` until `replication_complete()` returns true, then assert that every expected object and link was received.

`test_repl_integrity()` validates that modifying objects while a paged cycle is in progress does not drop objects. `test_repl_integrity_get_anc()` creates parent/child ordering where children can appear before parents, forcing GET_ANC. `test_repl_get_tgt()` and `test_repl_get_tgt_chain()` force GET_TGT by sending links before their targets are known, including a long B/C chain reachable from A objects.

Linked-attribute scenarios cover adding links during replication, parents with linked attributes under GET_ANC, combined GET_TGT and GET_ANC with nested targets, deleted link source/target objects, reanimated objects, cross-partition links into the Configuration NC, cross-partition deleted targets, and multi-valued links that may arrive in link-only chunks.

Lower-level request validation covers invalid NC/GUID combinations, full replication with `DummyDN` and valid GUID, interleaving `EXOP_REPL_OBJ` with full replication pages, and ensuring full replication pages do not overlap. The NC-root tests in `_test_repl_nc_is_first()` verify that the naming context root is first under full or NC-change cases and that `tmp_highest_usn` and `highest_usn` advance in expected ways.

## State and Persistence Behavior

Test state is deliberately local to a test case but mutates real Samba LDAP databases. Objects are created under a test OU and removed via cleanup with `tree_delete:1`. The class tracks received DNs, object GUID strings, linked attributes, `last_ctr`, GET_ANC/GET_TGT usage, and connection-specific highwatermarks.

DRS continuation state persists through `last_ctr.new_highwatermark` and `last_ctr.uptodateness_vector`. `start_new_repl_cycle()` preserves the last counter enough to continue from the previous highwatermark while clearing link state and flag tracking for a second cycle. Several tests disable replication on DC2, perform batches of local changes, and then re-enable/sync so the peer receives a controlled replication stream.

Deleted objects are inspected or restored using `show_deleted:1`, GUID-based LDAP binds, `isDeleted`, and `distinguishedName` replacement. Cross-partition tests create temporary server objects under the Configuration partition and explicitly replicate `nc_dn=self.config_dn`.

## Dependencies and Integration Points

The module depends on `drs_base`, `samba.tests`, `ldb`, `samba.dcerpc.drsuapi`, `samba.dcerpc.misc`, `samba.WERRORError`, and `samba.werror`. It assumes the Samba DRS torture environment exports DC names and credentials and that `drs_base.DrsBaseTestCase` provides DC LDAP handles, DNS names, config DN, DRS bind helpers, replication helpers, GUID formatting, ctr6 object/link extraction, and replication enable/disable hooks.

Integration points are the DRSUAPI `DsGetNCChanges` operation, Samba LDAP modify/delete/add operations, `net drs replicate` via `_net_drs_replicate()`, and the replication metadata/link representation returned by `drs_base` helper methods.

## Risks and Edge Cases

The tests are timing and ordering sensitive because they rely on USN ordering, object creation order, and mid-cycle mutations. Some behavior differs between Samba and Windows, and comments explicitly note optional Microsoft behavior, Windows duplicate ancestor sends, and Samba-specific ordering. The recursive retry behavior in `repl_get_next()` can hide a broken test setup if object/link ordering does not force the expected flag, so tests assert `used_get_anc` or `used_get_tgt` where relevant.

Large object counts and real DC replication make the suite slow. Cross-partition and reanimation scenarios are high-risk because incomplete cleanup or failed re-enable paths can leave DCs in unusual states; the tests use explicit cleanup and re-enable calls but still depend on a healthy integration environment.

## Test Signals

Strong signals include exact object coverage via `assert_expected_data()`, link-count and GUID-blob validation via `assert_expected_links()`, GET_ANC/GET_TGT flag usage assertions, DRS error-code checks such as `WERR_DS_DRA_BAD_NC`, highwatermark monotonicity assertions, link-only chunk detection, and consistency checks against both primary and secondary DCs using `assert_DCs_replication_is_consistent()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/getncchanges.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/link_conflicts.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/link_conflicts.py

## Purpose

`link_conflicts.py` tests Samba DRS conflict resolution for linked attributes when two DCs independently create, delete, or update conflicting link state. It focuses on single-valued links such as `managedBy`, multi-valued links such as `member`, generated backlinks such as `memberOf`, active versus deleted link state, object-deletion precedence, full-sync behavior, and link metadata versioning.

## Important APIs, Types, and Functions

The test class is `DrsReplicaLinkConflictTestCase`, derived from `drs_base.DrsBaseTestCase`. `setUp()` creates a stable test OU on DC1, binds DRS connections to both DCs, and disables inbound replication on both DCs so every conflict scenario can control exactly when bidirectional replication runs. `tearDown()` re-enables inbound replication, deletes the test OU tree, and delegates to the base teardown.

Constants `DC1_TO_DC2` and `DC2_TO_DC1` select replication order. `sync_DCs()` performs a two-step manual sync in the requested order so each test can make either DC resolve the conflict first. `ensure_unique_timestamp()` sleeps one second to force timestamp ordering when tests need deterministic "newer" metadata.

Object and link helpers are `get_guid()`, `add_object()`, `modify_object()`, `add_link_attr()`, `del_link_attr()`, and `unique_dn()`. `assert_attrs_match()` verifies expected attribute value counts on both DCs and checks value equality. `zero_highwatermark()` returns a zeroed `DsReplicaHighWaterMark` for full `REPL_OBJ` reads. `_check_replicated_links()` uses `_check_replication()` against both DCs with `DRSUAPI_EXOP_REPL_OBJ` and `AbstractLink` expectations to confirm raw DRS still preserves active and inactive conflict links that LDAP cannot show directly.

## Control Flow and Scenarios

Each conflict test creates source and target objects, syncs to establish a common baseline, applies divergent updates on the two DCs, calls `sync_DCs()` in both possible orders through a wrapper public test, and checks convergence.

Single-valued link tests cover different `managedBy` targets on two DCs, duplicate same-target additions, conflicts where the winning or losing link has been deleted, and reactivating link values that already exist as inactive metadata. Multi-valued tests cover same-DN conflicting user objects in a group membership, duplicate membership additions, and backlink repair when conflicting source groups are renamed with `CNF` names.

Deletion tests verify that a link delete versus active link conflict resolves by metadata version, that deleting a source or target object trumps a concurrent link add, and that doing full-sync cycles before a conflict does not change link conflict semantics. `test_link_attr_version()` directly calls `_get_replication()` for a single object and asserts the first linked-attribute metadata version is `1`.

## State and Persistence Behavior

State is stored in the real DC databases and isolated under the test OU. Inbound replication is disabled for the lifetime of each test case, so divergent object/link states persist on each DC until explicit sync calls. The tests rely on GUID-based searches to follow objects after conflict renames and use DRS raw link checks to observe inactive/deleted link records that are not visible through ordinary LDAP attributes.

Random suffixes in `unique_dn()` avoid collisions because some public test methods execute the same helper twice with different sync orders. Timestamp sleeps provide deterministic ordering for conflict algorithms that consider originating time. Version-sensitive tests create add/delete/add sequences to prove version number can beat timestamp recency.

## Dependencies and Integration Points

Dependencies include `drs_base`, `samba.tests`, `ldb`, `random`, `time`, `drs_base.AbstractLink`, `samba.dcerpc.drsuapi`, and `samba.dcerpc.misc`. Integration is with Samba LDAP operations, DRS bind handles to both DCs, `net drs replicate`, `DsGetNCChanges` via `_check_replication()`, and linked-attribute attids such as `DRSUAPI_ATTID_managedBy`.

## Risks and Edge Cases

The tests are intentionally sensitive to replication order, metadata timestamps, and metadata version increments. A one-second sleep is coarse but necessary for timestamp-based conflict resolution; slow or unusual environments can still make timing assumptions expensive. Because inbound replication is disabled in setup, teardown must reliably re-enable it to avoid contaminating later tests.

Conflict expectations are subtle: active links generally beat deleted alternatives in single-valued conflict cases, but version can beat timestamp in deletion conflicts. Raw DRS link verification is essential because LDAP cannot expose deleted link metadata; regressions that only affect inactive-link replication would be missed by LDAP-only assertions.

## Test Signals

Primary signals are cross-DC convergence checks for exact attribute counts and values, explicit checks for `CNF:<guid>` conflict-renamed objects, absence of `member`/`memberOf` after object-deletion conflicts, raw `AbstractLink` expected active/inactive records from DRS, and the linked-attribute version assertion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/link_conflicts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/linked_attributes_drs.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/linked_attributes_drs.py

## Purpose

`linked_attributes_drs.py` is a small DRS test module for forward linked-attribute visibility through `DsGetNCChanges`. It verifies that deleting a group, deleting individual membership links, or deleting a linked target user produces the expected active and inactive linked-attribute records in raw DRS output.

## Important APIs, Types, and Functions

`LATests` derives from `drs_base.DrsBaseTestCase`. `setUp()` selects DC1 as `samdb`, creates `OU=la,<domain>`, records the DC invocation id, and binds to DRS. `tearDown()` deletes the OU tree and ignores missing-object cleanup errors.

Object helpers are `add_object()`, `add_objects()`, `add_linked_attribute()`, `remove_linked_attribute()`, and `get_object_guid()`. `delete_user()` removes a user from a local `self.users` list, but that list is not initialized or used by the shown tests, making this helper effectively stale.

The central helper is `attr_search()`. It builds a `DRSUAPI_EXOP_REPL_OBJ` request with `_exop_req8()`, calls `self.drs.DsGetNCChanges()`, selects linked attributes matching `DRSUAPI_ATTID_<attr>`, unpacks each link value blob as `DsReplicaObjectIdentifier3`, and returns `(dn, active)` pairs based on `DRSUAPI_DS_LINKED_ATTRIBUTE_FLAG_ACTIVE`. `assert_forward_links()` compares these pairs to an expected mapping of DN to active boolean.

## Control Flow and Scenarios

`test_links_all_delete_group()` creates two users and two groups, adds memberships, deletes one group, asserts the surviving group still replicates its active member link, then searches the deleted group with `show_deleted:1` by GUID and asserts it has no forward links.

`test_la_links_delete_link()` creates two groups and two users, removes and re-adds membership links, and repeatedly asserts that raw DRS returns both active and inactive link records for the group as links are toggled. It validates inactive records after deletion and active records after re-add.

`test_la_links_delete_user()` deletes a target user after group memberships exist and asserts raw DRS for the source groups no longer returns links to the deleted user, while unrelated active links remain.

## State and Persistence Behavior

All state is stored under a single test OU on DC1 and cleaned by tree delete. The tests do not involve DC2 replication; they inspect the local DC's DRS representation after LDAP changes. Deleted groups are found by GUID with `show_deleted:1`, and raw link state is observed through DRS rather than LDAP search results.

## Dependencies and Integration Points

Dependencies include `sys.path.insert(0, "bin/python")`, `ldb`, `samba.dcerpc.drsuapi`, `samba.dcerpc.misc`, `samba.ndr.ndr_unpack`, `samba.ndr.ndr_pack` (imported but unused), and `drs_base`. The main integration point is direct `DsGetNCChanges` `EXOP_REPL_OBJ` on DC1, plus LDAP add/modify/delete operations.

## Risks and Edge Cases

This file is compact but depends on raw DRS link ordering only indirectly by set-style assertions. `attr_search()` ignores its `expected` and `scope` parameters, which are harmless but misleading. The unused `LATestException`, `delete_user()`, and `ndr_pack` import are stale signals. Since only DC1 is used, the file tests DRS exposure of local linked attributes, not inter-DC convergence.

## Test Signals

Signals are exact count matches from `assert_forward_links()`, active-flag comparisons for each expected DN, GUID-based lookup of deleted objects, and DRS unpacking of linked-attribute target identifiers rather than LDAP-only membership checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/linked_attributes_drs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/repl_move.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/repl_move.py

## Purpose

`repl_move.py` is a large Samba DRS integration test module for object moves, renames, deletes, and conflict resolution across two DCs. It validates that users and OUs keep correct DNs, names, parent GUIDs, deletion state, and replication metadata when moved between containers, renamed in place, modified concurrently on another DC, deleted, replicated in different directions, or created under conflicting parent containers.

## Important APIs, Types, and Functions

`DrsMoveObjectTestCase` derives from `drs_base.DrsBaseTestCase`. `setUp()` disables replication on both DCs, force-syncs them, creates a top test OU plus two sibling OUs (`DrsOU1`, `DrsOU2`) on DC1, replicates them to DC2, records both invocation IDs, and binds DRS connections to both DCs. `tearDown()` deletes the top OU, re-enables replication on both DCs, and delegates to the base teardown.

`_make_username()` creates timestamped user names. `_check_obj()` is the main object-state assertion helper: it searches by original object GUID with `show_deleted:1`, compares RDN, `name`, DN, `parentGUID`, and `isDeleted` behavior for live versus deleted objects, and optionally calls `_check_metadata()`. `_check_metadata()` unpacks LDAP `replPropertyMetaData` as `drsblobs.replPropertyMetaDataBlob` and optionally performs a raw DRS `DRSUAPI_EXOP_REPL_OBJ` request to compare DRS metadata and attribute attids against expected tuples of `(attid, originating_invocation_id, version)`.

`DrsMoveBetweenTreeOfObjectTestCase` tests deeper OU trees. Its `setUp()` creates DN objects and dictionaries for nested OUs (`DrsOU1`, `DrsOU2`, `DrsOU2B`, `DrsOU2C`, `DrsOU3` through `DrsOU6`) and disables replication. Its `_check_obj()` is a smaller GUID-based checker for CN/name/DN/deleted state and parent placement.

The file imports many DRSUAPI attid constants for metadata tables: user attributes, name/CN/OU attributes, deletion attributes such as `isDeleted`, `isRecycled`, `lastKnownParent`, and DRS request types such as `DsGetNCChangesRequest8`, `DsReplicaHighWaterMark`, and `DsReplicaObjectIdentifier`.

## Control Flow and Scenarios

`test_ReplicateMoveObject1` through `test_ReplicateMoveObject11` cover user and OU movement between two sibling OUs, rename-only moves, concurrent description modifications on DC2, deletion on DC1 or DC2, replication in DC1-to-DC2 and DC2-to-DC1 directions, and cases where the peer had never seen the moved object. Early tests include detailed metadata expectation tables for initial creation, move, delete, and concurrent description states; later tests focus on behavioral object checks and description preservation/removal.

The common flow is: create or locate a user/OU on DC1, optionally replicate to DC2, rename/move it on DC1, optionally modify `description` on DC2 at the old DN, run manual replication in a chosen direction, assert the live object is at the expected DN with expected metadata and description, delete it, replicate cleanup, and assert deleted-object semantics and metadata.

`DrsMoveBetweenTreeOfObjectTestCase` expands this into deep tree and parent-conflict cases. It verifies moving a user into a newly created nested OU chain, moving users back, moving parent OUs around after users have been moved, shuffling sibling OUs through temporary names, combining unrelated attribute modifications with rename operations to force out-of-USN-order replication, adding users under OUs whose parent metadata sorts after the child, and resolving conflicting parent OUs by timestamp/version so the child lands under the intended `parentGUID`.

## State and Persistence Behavior

The tests deliberately disable automatic replication and use forced `_net_drs_replicate()` calls as the only propagation mechanism. This makes the database state on DC1 and DC2 intentionally divergent during each scenario. Objects are followed by GUID, not DN, because moves, conflict renames, and deletion mangling change DNs.

Persistent assertions inspect both ordinary LDAP attributes and replication metadata. Deleted objects are searched with `show_deleted:1`; deleted DNs and names are expected to preserve the pre-delete RDN prefix before deletion mangling, and live objects must preserve exact DN/name/RDN equality plus `parentGUID`. Description attributes modified on the losing side are expected either to survive on live objects or disappear after deletion conflict resolution, depending on the scenario.

Metadata tables encode originating DC and version behavior. Notably, RDN attributes are skipped in raw DRS metadata comparisons because the RDN itself is not sent as an ordinary DRS attribute in the same way as LDAP `replPropertyMetaData`.

## Dependencies and Integration Points

Dependencies include `time`, `samba.tests`, `samba.ndr.ndr_unpack`, `samba.dcerpc.drsblobs`, `samba.dcerpc.misc`, `samba.drs_utils.drs_DsBind` (imported but not used directly), `ldb`, `drs_base`, and many `samba.dcerpc.drsuapi` constants and request classes. The integration points are Samba LDAP `newuser`, add, rename, modify, delete, GUID search, raw DRS `DsGetNCChanges` `EXOP_REPL_OBJ`, `replPropertyMetaData`, and manual forced DRS replication.

## Risks and Edge Cases

This is a brittle but valuable integration suite. It depends on exact metadata ordering, exact attid sequences, invocation IDs, version increments, and deletion mangling behavior. Repeated large metadata tables make maintenance error-prone; changing Samba's metadata representation can require updating many expected lists. Timestamp-derived usernames can collide if multiple tests create the same value within one second in a shared OU, although each test creates its own top OU.

Replication must be re-enabled in teardown even after failures. The tests also rely on modifying objects at old DNs on DC2 while DC1 has renamed them, which is intentional but sensitive to whether the peer has already seen prior changes. Deep-tree tests rely on `parentGUID` rather than DN strings to disambiguate conflicting parent containers.

## Test Signals

Signals include GUID-based live/deleted object lookup, exact DN/RDN/name/parentGUID assertions, absence or presence of `description`, exact `isDeleted` expectations, LDAP `replPropertyMetaData` attid/origin/version matching, raw DRS `REPL_OBJ` metadata checks, successful forced replication in both directions, and final parentGUID equality after complex tree shuffles and conflict resolution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/repl_move.py -->
