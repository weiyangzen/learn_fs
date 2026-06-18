# Research: subset-b-009920

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ldap.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ldap.py

## Purpose

`ldap.py` is a large Samba DSDB LDAP compatibility test suite. It exercises Active Directory-like behavior exposed through Samba's `SamDB`/LDB LDAP layer: schema object-class validation, add/modify/delete/rename semantics, generated operational attributes, linked attributes, security descriptors, search controls, global-catalog visibility, RootDSE attributes, DN forms, and Windows-compatible LDAP result codes.

The file is a test executable, not a reusable library. It parses a host argument, opens a normal `SamDB` connection and, when the target is not a local `tdb://` database, a GC connection on port 3268. `TestProgram` then runs two `samba.tests.TestCase` classes: `BasicTests` for domain object behavior and `BaseDnTests` for RootDSE behavior.

## Important APIs, Types, and Functions

Key external APIs are `samba.samdb.SamDB`, `samba.Ldb`, `samba.tests.connect`-style test support through the global connections, `samba.tests.delete_force`, `samba.auth.system_session`, and LDB primitives such as `Message`, `MessageElement`, `Dn`, scopes, modify flags, and `LdbError` result codes. The test also uses DSDB constants for `userAccountControl`, `sAMAccountType`, and system flags; NDR helpers for security descriptor packing/unpacking; `security.descriptor`/SID conversion; and LSA RPC to create a secret object outside LDAP.

`BasicTests.setUp()` binds the shared connections and deletes a fixed set of `ldaptest*`, `posixuser`, container, secret, and time-value objects so each test starts from a clean domain state. `BaseDnTests.setUp()` only attaches the shared LDB handle.

Important test methods include:

- `test_objectclasses()`: structural, abstract, auxiliary, inherited, and replacement `objectClass` behavior.
- `test_system_only()`: rejects direct LDAP writes to system-only classes and attributes, including LSA-created secrets and `isCriticalSystemObject`.
- `test_invalid_parent()` and `test_invalid_attribute()`: parent existence, naming, unknown attributes, mandatory attributes, and object-class containment rules.
- `test_single_valued_attributes()`, `test_single_valued_linked_attributes()`, and `test_multivalued_attributes()`: cardinality rules and high-count multi-value modify behavior.
- `test_attribute_ranges()` and `test_attribute_ranges_too_long()`: minimum and maximum syntax/range enforcement on `sn`.
- `test_instanceType()`, `test_distinguished_name()`, and `test_rdn_name()`: protected constructed attributes, invalid DN syntax, RDN constraints, and non-writable `name`/RDN attributes.
- `test_rename()`, `test_rename_twice()`, and the large `test_all()`: normal renames, subtree renames, system-flag move restrictions, alternate DN forms, duplicate-name errors, linked-attribute repair, object category matching, ANR, UTF-8 matching, controls, and GC behavior.
- `test_objectGUID()`, `test_parentGUID()`, and `test_usnChanged()`: generated metadata and update sequencing.
- `test_linked_attributes()` and `test_wkguid()`: forward/back-link enforcement and DN+Binary matching.
- `test_security_descriptor_add()`, `test_security_descriptor_add_neg()`, and `test_security_descriptor_modify()`: SDDL and base64 security descriptor add/modify paths.
- `test_dsheuristics()`, `test_ldapControlReturn()`, `test_operational()`, `test_timevalues1()`, and the three LDAP search attribute-selection tests: controls, operational attributes, generalized time normalization, no-attribute OID, and `*`.
- `BaseDnTests` methods: RootDSE `highestCommittedUSN`, naming contexts, server paths, functionality levels, DNS hostname, and LDAP service name.

## Control Flow

At import/execution time, the script parses Samba options, credentials, subunit options, and the required host. It normalizes bare host paths/names into `tdb://` or `ldap://`, creates the domain LDB connection, optionally creates a GC connection, then launches `TestProgram`.

Each test follows a direct arrange/act/assert pattern. Most create domain entries under `CN=Users`, `CN=Computers`, or temporary containers, perform one or more LDB operations, catch `LdbError`, and assert the numeric LDAP/DSDB error code. Positive paths usually re-search by base DN or filter and verify generated attributes, canonicalized DNs, value order, or linked-attribute state. Cleanup is mostly explicit with `delete_force()` or direct `delete()`, with `setUp()` acting as an additional guard for the fixed object names.

The largest flow is `test_all()`: it builds users, groups, and computers; validates generated account fields; tests duplicate SPNs and ranged retrieval; exercises ANR filters; performs SID/GUID-based rename and delete operations; renames a subtree and verifies linked memberships update; validates UTF-8/case-insensitive searches; proves search boundary behavior with `search_options` and GC connections; and finally toggles `posixAccount` auxiliary class membership.

## State and Persistence Behavior

The tests mutate a real Samba AD database. They create users, computers, groups, containers, POSIX-style users, a system secret through LSA RPC, and temporary metadata changes such as `dSHeuristics`. Most mutations are removed explicitly; `test_dsheuristics()` saves and restores the old value in a `finally` block. Several tests rely on server-generated persistent metadata (`objectGUID`, `objectSid`, `uSNCreated`, `uSNChanged`, `whenCreated`, `whenChanged`, `parentGUID`, `memberOf`, `nTSecurityDescriptor`) and compare it across operations.

The suite uses fixed object names rather than fully random names. That makes stale state possible if a previous run aborts between setup and cleanup, but the broad `setUp()` deletion list reduces repeat-run contamination for the known names. The suite also sleeps after linked-attribute/subtree operations, implying asynchronous or delayed consistency concerns.

## Dependencies and Integration Points

This file integrates tightly with Samba's AD DC stack: the DSDB schema module, object-class module, linked-attributes module, descriptor/security code, RootDSE implementation, LDB controls (`paged_results`, `domain_scope`, `search_options`, `extended_dn`), Global Catalog search, generated operational attributes, LSA RPC, NDR security descriptor serialization, and Samba's test/subunit runner. It also relies on exact Windows-compatible numeric errors from `ldb`.

## Risks and Edge Cases

The suite is intentionally brittle about protocol compatibility: many assertions require exact result codes for invalid operations, not just failure. Any change in DSDB module order, schema refresh behavior, object-class validation, generated metadata, or control handling can alter these results.

The global `ldb`/`gc_ldb` objects and fixed names make the tests non-isolated and unsuitable for concurrent runs against the same domain. Some tests depend on timing (`time.sleep(4)`) for linked attributes, which can be slow or flaky on overloaded environments. The security descriptor tests depend on correct domain SID conversion and SDDL round-tripping. The GC path is skipped for local `tdb://` targets, so local and remote coverage differ.

## Test Signals

Passing this file signals broad LDAP compatibility for Samba AD DC. Strong signals include exact LDB error codes on invalid schema/object writes, stable generated account attributes for users/computers/groups, linked `member`/`memberOf` cleanup after delete/rename, ranged attribute retrieval correctness, security descriptor SDDL/base64 round-trip, RootDSE functionality consistency with backing objects, GC and phantom-root search behavior, and correct handling of UTF-8 and alternate SID/GUID DN forms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ldap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_modify_order.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_modify_order.py

## Purpose

`ldap_modify_order.py` is a Samba DSDB regression/compatibility test for LDAP modify operation ordering. It proves that Samba's modify processing gives stable, expected results for every permutation of a set of add, replace, and delete operations in one `Message`, including cases where attribute applicability, syntax, single-valued constraints, object-class changes, and linked attributes interact.

Unlike typical unit tests, this file compares a generated signature against checked-in expected data files under `source4/dsdb/tests/python/testdata`. That makes the expected behavior explicit for every operation permutation.

## Important APIs, Types, and Functions

The central helper is `_test_modify_order(start_attrs, mod_attrs, extra_search_attrs=(), name=None)`. It creates a fresh object for each permutation of `mod_attrs`, applies the permuted LDB `Message`, searches the resulting object, clusters permutations by identical result or error, normalizes the base DN to `{base dn}`, and compares the signature with `testdata/<name>.expected`.

Other important functions and members:

- `_build_ldb_strerr()` builds a numeric LDB error-code-to-name table from the `ldb` module for stable signatures.
- `ModifyOrderTests.setUp()` creates an admin `SamDB` connection and stores the domain DN.
- `delete_object()` and `get_user_dn()` support cleanup and optional normal-user credential creation.
- `get_dsdb(creds=None)` opens `SamDB` with a system session and the selected credentials.
- Test cases such as `test_modify_order_mixed`, `test_modify_order_objectclass`, `test_modify_order_singlevalue`, `test_modify_order_inapplicable`, `test_modify_order_container_flags`, and `test_modify_order_member` define targeted start and modify tuples.

The script supports `--rewrite-ground-truth` to regenerate expected signatures, `--verbose` to print signatures, and `--normal-user` to run modify attempts with a newly created non-admin user instead of admin credentials.

## Control Flow

The file first builds `LDB_STRERR`, defines the test class, then parses options and normalizes the host into `tdb://` or `ldap://`. During each test, `_test_modify_order()` optionally creates a normal user and credentials, computes every permutation using `itertools.permutations`, creates one test object per permutation, applies the modification message, captures either the LDB error name/number or the sorted searched attribute values, and stores the operation ordering under that result cluster.

After all permutations run, it joins the signature text, substitutes the real base DN, optionally rewrites the expected file, reads the expected file, and calls `assertStringsEqual()`.

## State and Persistence Behavior

The test mutates a live DSDB by creating many `cn=ldaptest_<name>_<index>,cn=users,<base>` objects. Cleanup is registered with `addCleanup()` after each add. The `--normal-user` mode also creates `user123` with a fixed password and deletes it after the test. The ground-truth mode writes persistent `.expected` files in the source tree, but normal runs only read them.

The signature intentionally preserves operation order and result grouping, so it detects subtle ordering and module-processing changes even when the final object state is otherwise valid.

## Dependencies and Integration Points

The file depends on `SamDB`, `system_session`, LDB `Message`/`MessageElement`/`Dn`, modify flags, `LdbError`, Samba credential helpers, `delete_force`, subunit test running, and the `testdata` expected-output directory. It exercises DSDB modify internals for object-class validation, attribute syntax validation, single-valued enforcement, attribute applicability, integer parsing, linked attributes (`member`/`memberOf`), and access-control differences between admin and normal-user credentials.

## Risks and Edge Cases

Permutation coverage grows factorially with the number of modify tuples, so adding many operations to a case can make the test expensive and create many live objects. The expected files are compatibility contracts; `--rewrite-ground-truth` can accidentally bless a regression if used without review. Fixed normal-user credentials and object names can collide with concurrent runs or stale objects. Result signatures sort searched values, which is useful for set-like attributes but can hide ordering bugs for attributes where order is significant unless the operation/result text itself exposes them.

## Test Signals

Passing tests mean Samba applies complex multi-operation LDAP modifies consistently with the checked ground truth. The strongest signals are stable clustering across all permutations, correct LDB error names for invalid orderings, expected behavior when object-class changes make attributes newly applicable or inapplicable, correct handling of single-valued replacement/delete/add combinations, and linked-attribute consistency for `member` plus `memberOf`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_modify_order.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_schema.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_schema.py

## Purpose

`ldap_schema.py` is a Samba AD schema behavior test suite. It verifies that schema reads, schema updates, generated schema attributes, custom attributes/classes, uniqueness constraints, generated IDs, and constructed RODC-related attributes behave like Active Directory over LDAP.

The suite creates real `attributeSchema` and `classSchema` objects in the schema naming context, triggers schema refresh with RootDSE `schemaUpdateNow`, then searches or instantiates objects to prove the schema changes are active.

## Important APIs, Types, and Functions

The file uses `SamDB` connections with optional `modules:paged_searches` for remote LDAP targets, `system_session`, LDB scopes/errors/messages, `delete_force`, DS functional-level constants, and NDR unpacking of `drsblobs.replPropertyMetaDataBlob`.

`SchemaTests` covers general schema behavior:

- `test_generated_schema()` and `test_generated_schema_is_operational()` verify `cn=aggregate` generated schema attributes are returned only when requested.
- `test_schemaUpdateNow()` creates a custom attribute and class, rejects an invalid `defaultObjectCategory`, forces schema refresh, instantiates the class, and checks replication metadata contains the generated `msDS-IntId` attid when applicable.
- `test_subClassOf()` creates a custom class derived from `organizationalUnit` and instantiates it.
- Duplicate/immutability tests cover `attributeID`, `governsID`, `cn`, implicit/explicit `ldapDisplayName`, rename-to-duplicate, removing/renaming `ldapDisplayName`, and changing `attributeID`/`governsID`.
- `test_generated_linkID()` verifies automatic linkID generation, uniqueness, forward/back-link pairing, and rejection of duplicate or invalid backlink definitions.
- `test_generated_mAPIID()` verifies automatic mAPIID generation and duplicate rejection.

`SchemaTests_msDS_IntId` focuses on `msDS-IntId` rules. Helpers `_ldap_schemaUpdateNow()`, `_make_obj_names()`, `_is_schema_base_object()`, `_make_attr_ldif()`, and `_make_class_ldif()` generate schema LDIF and inspect `systemFlags`. Tests verify whether attributes/classes may set or modify `msDS-IntId`, and whether non-base attributes receive it at sufficient forest functional level.

`SchemaTests_msDS_isRODC` searches existing `nTDSDSA`, `server`, and `computer` objects with the phantom-root-style `search_options:1:2` control and checks that `msDS-isRODC` is present when a corresponding NTDS settings/server-reference relationship exists.

## Control Flow

At startup, the script parses options, credentials, and host. It normalizes the host scheme and chooses `ldb_options`; remote LDAP gets paged-search modules. `TestProgram` runs the three test classes.

Each test method opens or reuses a `SamDB` connection in `setUp()`, discovers `base_dn` and `schema_dn`, builds LDIF strings with timestamp/random OID suffixes, and performs `add_ldif()`, `modify_ldif()`, `modify()`, and `search()` calls. Negative tests catch `LdbError` and assert exact codes such as `ERR_UNWILLING_TO_PERFORM`, `ERR_CONSTRAINT_VIOLATION`, `ERR_ENTRY_ALREADY_EXISTS`, `ERR_OBJECT_CLASS_VIOLATION`, or `ERR_NO_SUCH_OBJECT`.

Schema activation is explicit in tests that need immediate use of new definitions: they modify RootDSE with `schemaUpdateNow: 1`, then instantiate objects or search generated IDs.

## State and Persistence Behavior

These tests persistently add schema objects to the target directory. Most schema objects are named with `time.strftime("%s")` plus random OID components, reducing collisions but leaving schema extensions behind because schema entries cannot generally be deleted like normal test objects. Some domain objects instantiated from new schema classes are deleted after validation.

Generated persistent state under test includes `lDAPDisplayName`, `defaultObjectCategory`, `schemaIDGUID`, `msDS-IntId`, `linkID`, `mAPIID`, and replication metadata. Functional level affects expected `msDS-IntId` and linkID behavior; tests read RootDSE `forestFunctionality` or `domainControllerFunctionality` before deciding expectations or skipping.

## Dependencies and Integration Points

The file integrates with the DSDB schema loader/cache, RootDSE schema refresh, generated schema aggregate, OID uniqueness enforcement, `schemaIDGUID` generation, replication metadata encoding, prefix-map/attid behavior, functional-level gates, linked-attribute schema rules, paged LDAP searches, and constructed `msDS-isRODC` logic across server/computer/NTDS settings objects.

## Risks and Edge Cases

Because schema additions are durable and use random suffixes, repeated runs can grow the schema. Tests that assert exact errors are sensitive to validation ordering. Time-based names only have second resolution, so rapid concurrent runs still need the random OID portions to avoid collisions; names without random suffix in some tests may collide if parallelized in the same second. Functional-level differences intentionally change expectations, and comments note Windows refresh behavior requiring explicit schema update. `test_verify_msDS_IntId()` prints warnings for missing IDs rather than failing in some cases, so it is partly diagnostic.

## Test Signals

Passing this suite indicates Samba can expose generated schema over LDAP, accept valid custom attributes/classes, reject duplicate or illegal schema identity changes, refresh schema for immediate use, generate and protect `msDS-IntId`, `linkID`, and `mAPIID` correctly, and construct `msDS-isRODC` on relevant directory objects. Failure usually points to DSDB schema validation, generated-ID allocation, RootDSE refresh, functional-level handling, or constructed-attribute regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_schema.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_syntaxes.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_syntaxes.py

## Purpose

`ldap_syntaxes.py` tests Samba LDAP handling of two complex AD syntaxes: DN+String and DN+Binary. It dynamically adds schema attributes/classes using those syntaxes, creates objects with valid and invalid values, and verifies search matching requires the complete composite value rather than only the DN or only the string/binary component.

## Important APIs, Types, and Functions

The file uses `samba.tests.connect_samdb`, `system_session`, LDB scopes and errors, `uuid`, `time`, and random OID suffixes. `SyntaxTests.setUp()` connects to SamDB, stores the domain and schema DNs, then calls both schema setup helpers before every test.

Important helpers:

- `_setup_dn_string_test()` creates an `attributeSchema` with `attributeSyntax: 2.5.5.14`, `omSyntax: 127`, and DN+String `omObjectClass`, then creates a structural class that may contain that attribute.
- `_setup_dn_binary_test()` creates the analogous DN+Binary attribute with `attributeSyntax: 2.5.5.7` and DN+Binary `omObjectClass`, plus a containing class.
- `_get_object_ldif()` builds an object LDIF under `CN=Users` using the generated class and attribute value.

Test methods:

- `test_dn_string()` adds a valid `S:<len>:<string>:<dn>` value, verifies component-only searches do not match, verifies full DN+String search matches, and checks malformed length plus GUID/SID/random-DN substitutes fail with expected errors.
- `test_dn_binary()` does the same for `B:<len>:<hex-or-bytes>:<dn>`, including invalid binary length and non-DN target forms.

## Control Flow

Startup parses host/options/credentials and runs `TestProgram`. Each test instance creates fresh schema attribute/class definitions in `setUp()`. The syntax tests then build LDIF strings, call `add_ldif()` for valid setup/object creation, run subtree searches against the domain, and catch `LdbError` for invalid additions. Duplicate object DN attempts are expected to return `ERR_ENTRY_ALREADY_EXISTS` regardless of changed composite attribute contents.

## State and Persistence Behavior

The suite mutates the schema on every test setup by adding new attributes and classes named with the current epoch second and random OID components. It also creates test objects under `CN=Users`; the file does not register explicit cleanup for those objects or schema entries. As with other schema tests, schema additions are persistent and should be run against disposable test domains.

The generated attributes/classes are stored as instance variables (`dn_string_class_ldap_display_name`, `dn_string_attribute`, `dn_binary_class_ldap_display_name`, `dn_binary_attribute`, and class names) and used by the test methods.

## Dependencies and Integration Points

This test exercises DSDB schema extension, syntax parser/normalizer support for DN+String and DN+Binary, LDAP filter matching rules for composite values, DN validation inside composite syntaxes, and error mapping for invalid syntax versus constraint violations. It depends on the AD schema accepting the specified `omObjectClass` byte strings and on immediate availability of the new schema definitions after add.

## Risks and Edge Cases

The use of `time.strftime("%s")` can collide when setup runs more than once in the same second; random OID suffixes reduce OID collisions but not necessarily CN/class-name collisions. The tests do not force `schemaUpdateNow`, so they rely on Samba making new schema available quickly enough for immediate object creation. The `except LdbError` blocks assert codes only when an exception occurs; if an invalid add unexpectedly succeeds, several blocks do not call `fail()`, so a regression could be missed. Persistent schema/object additions can contaminate long-lived environments.

## Test Signals

Passing tests signal that Samba can add DN+String and DN+Binary schema attributes, instantiate objects containing those attributes, match only full composite values in LDAP filters, reject malformed length/value encodings with `ERR_INVALID_ATTRIBUTE_SYNTAX`, reject GUID/SID/random-string substitutes for required DNs with `ERR_CONSTRAINT_VIOLATION`, and preserve duplicate-DN behavior independently of attribute differences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_syntaxes.py -->
