# Research: subset-b-009925

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/unicodepwd_encrypted.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/unicodepwd_encrypted.py

## Purpose

`unicodepwd_encrypted.py` is an LDAP integration test for Samba AD password-change transport requirements. It verifies that writes to the sensitive `unicodePwd` attribute are accepted only when the LDAP connection is protected by SASL sealing or TLS, and rejected on unsigned or merely signed plaintext LDAP sessions.

## Important APIs, Types, and Functions

`UnicodePwdEncryptedConnectionTests` inherits from `PasswordTestCase`, using `allow_password_changes()` to relax policy during the test. `setUp()` creates a sealed `SamDB` connection, creates `cn=testuser,cn=users,<domain>`, sets an initial `userPassword`, and enables the account. `modify_unicode_pwd()` performs the actual `FLAG_MOD_REPLACE` on `unicodePwd`, encoding the quoted password as UTF-16LE as required by Active Directory semantics. The test methods cover SASL-sealed LDAP, SASL without seal, simple bind over plain LDAP, and simple bind over LDAPS.

## Control Flow

Command-line parsing builds Samba loadparm and credentials, then `TestProgram` runs the test class. Each test starts from a clean test user. The success paths call `modify_unicode_pwd()` directly. The rejection paths create alternate `SamDB` connections: one with `gensec.FEATURE_SEAL` removed and `client ldap sasl wrapping` forced to `sign`, and another using simple bind over `ldap://`. Both expect `LdbError` with `ERR_UNWILLING_TO_PERFORM` and a diagnostic saying password modification must be over an encrypted connection.

## State and Persistence Behavior

The test mutates live directory state by deleting and recreating `testuser`, setting `userPassword`, enabling the account, and replacing `unicodePwd`. It intentionally touches password-change policy through `allow_password_changes()`. Cleanup relies on per-test recreation through `delete_force`; the tested password value is not reused outside the current test case.

## Dependencies and Integration Points

The file depends on Samba Python bindings for `SamDB`, `system_session`, credentials and GENSEC feature flags, plus LDB message APIs. It exercises the DSDB password modification path reached through LDAP server connections, not a mocked password module. It also depends on an LDAPS listener being available for the TLS simple-bind positive case.

## Risks and Edge Cases

The no-seal SASL case requires Kerberos-required credentials or the client may negotiate a protected connection automatically, so the test explicitly masks seal and forces signing. Simple bind setup uses `get_admin_sid()` as the bind DN, which makes the test sensitive to Samba's simple-bind credential interpretation. Failures can come from TLS/listener setup rather than password policy if LDAPS is unavailable.

## Test Signals

Strong signals are: sealed SASL and LDAPS simple bind successfully replace `unicodePwd`; unsealed LDAP and plain simple bind fail with `ERR_UNWILLING_TO_PERFORM`; and the error text identifies the encrypted-connection requirement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/unicodepwd_encrypted.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/urgent_replication.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/urgent_replication.py

## Purpose

`urgent_replication.py` validates DSDB urgent replication bookkeeping. It creates, modifies, and deletes object classes and attributes whose changes should or should not advance the partition `uSNUrgent` value to match `uSNHighest`.

## Important APIs, Types, and Functions

`UrgentReplicationTests` uses `samba.tests.connect_samdb(..., global_schema=False)` to operate against a live DC. `delete_force()` deletes with `relax:0` and tolerates missing objects. The tests call `load_partition_usn()` after mutations and compare `uSNHighest` with `uSNUrgent`. They use LDB `Message`, `MessageElement`, `Dn`, and `FLAG_MOD_REPLACE` to change attributes, plus `samba.dsdb` UAC constants for urgent attribute checks.

## Control Flow

`setUp()` opens a SamDB connection and records the domain DN. Each test performs a specific mutation sequence, then checks whether the urgent USN moved. Non-urgent user object create/modify/delete should leave `uSNUrgent` behind. `nTDSDSA` and `crossRef` create/delete are urgent while ordinary modify is not. `attributeSchema` and `classSchema` changes are urgent. `secret` and `rIDManager` create/modify are urgent but delete is not. User `userAccountControl`, `lockoutTime`, and `pwdLastSet` modifications are urgent, while `description` and deletion are not.

## State and Persistence Behavior

The test writes real objects under domain, configuration, schema, and system naming contexts. Several creates use `relax:0` to bypass normal restrictions for schema or configuration objects. Random OID suffixes reduce collisions for schema test objects, but cleanup is incomplete for some schema cases because deleted schema definitions are not simply removed. The central persistent signal is partition metadata: `load_partition_usn()` exposes whether the urgent replication marker was updated by the preceding transaction.

## Dependencies and Integration Points

The file integrates with DSDB replication metadata, schema handling, urgent replication trigger logic, and the LDB module stack. It depends on the domain, configuration, and schema naming contexts being writable by the test credentials and on Samba's `load_partition_usn()` helper returning both `uSNHighest` and `uSNUrgent`.

## Risks and Edge Cases

Schema tests can be environment-sensitive: `classSchema` creation is caught and skipped if the add fails, but the modify branch still assumes the object exists. Random OIDs can still collide in long-running or reused environments. The tests compare equality immediately after a mutation, so unrelated concurrent writes to the same partition can make `uSNHighest` advance and produce false negatives.

## Test Signals

Passing tests show that Samba marks urgent replication exactly for AD-sensitive classes and attributes. Regressions surface as equality mismatches between `uSNHighest` and `uSNUrgent`, or as unexpected LDB errors while adding schema/configuration objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/urgent_replication.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/user_account_control.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/user_account_control.py

## Purpose

`user_account_control.py` is a large Samba AD integration suite for non-ACL rules around `userAccountControl`, objectClass compatibility, machine-account creation rights, privileged trust-account transitions, trailing-dollar rules, and `primaryGroupID` restrictions. It checks behavior for both domain-admin and delegated/unprivileged writers.

## Important APIs, Types, and Functions

`UserAccountControlTests` is decorated with `DynamicTestCase` and generates many parameterized tests in `setUpDynamicTestCases()`. Helpers include `add_computer_ldap()`, `add_user_ldap()`, and `get_creds()`. `setUp()` creates an unprivileged user, a test OU, SAMR connection, security descriptor utilities, and reference computer security descriptors. Major test helpers include `_test_uac_bits_set_with_args()`, `_test_uac_bits_unrelated_modify_with_args()`, `_test_uac_bits_add_with_args()`, `_test_objectclass_uac_dollar_lock_with_args()`, `_test_mod_lock_with_args()`, `_test_objectclass_uac_mod_lock_with_args()`, and `_test_objectclass_mod_lock_with_args()`.

## Control Flow

The suite first establishes a controlled OU and grants temporary object creation or write-property ACEs to the unprivileged principal. Individual tests then add users or computers and attempt UAC, objectClass, `sAMAccountName`, security descriptor, and primary group changes. Expected results distinguish successful normal-account operations from `ERR_INSUFFICIENT_ACCESS_RIGHTS`, `ERR_OBJECT_CLASS_VIOLATION`, `ERR_UNWILLING_TO_PERFORM`, and `ERR_OTHER`. Dynamic cases cover transitions among `UF_NORMAL_ACCOUNT`, `UF_WORKSTATION_TRUST_ACCOUNT`, `UF_SERVER_TRUST_ACCOUNT`, and invalid or privileged bits using replace and delete-add modify styles.

## State and Persistence Behavior

Every test mutates a live AD database. `setUp()` removes and recreates the OU and unprivileged user, then registers cleanup for the user and OU tree. The suite temporarily changes OU DACLs and sometimes object DACLs to isolate semantic restrictions from ordinary ACL denial. It also modifies group membership and `primaryGroupID` for test accounts. No durable state is intended beyond the test run, but failed teardown can leave generated accounts under the test OU.

## Dependencies and Integration Points

The tests exercise DSDB object creation, SAMR connectivity, security descriptor packing/unpacking, extended rights for creating computer objects, UAC validation in the objectclass/user module stack, and primary group validation. They rely on `samba.dsdb` UAC constants, `security` RID/SID values, `sd_utils`, LDB search/modify APIs, sealed LDAP credentials, and a live DC accepting both LDAP and SAMR connections.

## Risks and Edge Cases

The test intentionally grants broad write-property ACEs in some scenarios, so it must run only against disposable test domains. Error expectations encode Samba/Windows compatibility decisions and may need updates when DSDB validation ordering changes. Some generated test names include `None` string fragments from optional parameter combinations, which is harmless but easy to misread. The suite is expensive because it creates many dynamic tests and uses live LDAP/SAMR setup per case.

## Test Signals

Important signals include blocked unprivileged promotion to DC/RODC/trust accounts, objectClass/UAC mismatch failures, ignored or invalid UAC bits not sticking, allowed admin transitions where appropriate, protection against setting privileged `primaryGroupID` on create, and prohibition on changing structural objectClass after creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/user_account_control.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/vlv.py -->
# sources/user-network-fs/samba/source4/dsdb/tests/python/vlv.py

## Purpose

`vlv.py` is a comprehensive LDAP integration suite for Virtual List View, server-side sort, paged results, deleted-object visibility, cookie lifetime, and mutation behavior during active views. It compares Samba behavior against expected AD/Windows semantics for sorted and paged searches.

## Important APIs, Types, and Functions

Top-level helpers `encode_vlv_control()` and `get_cookie()` build VLV request controls and parse response cookies. `TestsWithUserOU` creates a test OU tree and synthetic users with locale, binary, numeric, timestamp, Unicode, newline, and special-character attributes. `VLVTestsBase.vlv_search()` performs a sorted VLV search. `VLVTests`, `VLVTestsRO`, and `VLVTestsGC` cover read/write, read-only, and global catalog variants. `PagedResultsTests`, `PagedResultsTestsRO`, `PagedResultsTestsGC`, and `PagedResultsTestsRW` cover paged-results behavior.

## Control Flow

Setup creates `ou=vlvtesttree` and `ou=vlvou`, then populates `N_ELEMENTS` users. VLV tests derive expected ordering from plain server-side sort, then perform offset/count and greater-than-or-equal VLV requests with and without cookies. Mutation tests create, delete, rename, or modify users during an active cookie-backed view and assert the view remains anchored to the original candidate list while visible attributes may update. Paged tests walk multiple concurrent cookies, mutate entries between pages, verify changed expression/control/attribute requests fail with LDAP error 12, and confirm VLV plus paged results is rejected as an unsupported critical extension.

## State and Persistence Behavior

The suite writes a temporary OU tree and many users, then deletes the tree in `tearDown()` unless `--delete-in-setup` defers cleanup to the next run. Cookies are connection-local server state: `test_multiple_searches()` confirms old VLV cookies expire when the per-connection search limit is exceeded and that cookies do not work on a new `SamDB` connection. Paged and VLV tests intentionally mutate directory state while cookies are live to verify snapshot and membership semantics.

## Dependencies and Integration Points

The file depends on Samba LDAP controls (`server_sort`, `vlv`, `paged_results`, `show_deleted`), SamDB, LDB controls/errors, global catalog port `3268`, and command-line options for test size and attribute filtering. It stresses DSDB indexing, sorting collation, binary/numeric conversion, deleted-object search, ANR filter rewriting, referral handling, and cookie management in the LDAP server stack.

## Risks and Edge Cases

Sorting behavior is sensitive to locale, binary NUL handling, syntax-specific comparisons, and server-specific ordering of equivalent values. The test includes options to skip known-problem attributes, and some comments document Windows/Samba behavioral differences. Randomized mutation loops use fixed seeds but still depend on object counts and server timing. Large `--elements` values can make the combinatorial VLV loops expensive.

## Test Signals

Passing signals include correct sorted windows for all before/after/offset combinations, stable cookie-backed views across additions/deletions, expected attribute updates within existing views, deleted-object ordering with `show_deleted`, rejection of changed paged-search parameters, first-page-only referrals, and correct handling of ANR with paged results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/tests/python/vlv.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/wscript_build -->
# sources/user-network-fs/samba/source4/dsdb/wscript_build

## Purpose

`source4/dsdb/wscript_build` defines the Waf build graph for Samba's source4 DSDB libraries, schema subsystem, AD DC services, and Python `samba.dsdb` extension.

## Important APIs, Types, and Functions

The file uses Waf/Samba build declarations: `bld.RECURSE()`, `bld.SAMBA_LIBRARY()`, `bld.SAMBA_SUBSYSTEM()`, `bld.SAMBA_MODULE()`, `bld.SAMBA_PYTHON()`, and `bld.pyembed_libname()`. It declares `samdb`, `samdb-common`, `SAMDB_SCHEMA`, service modules `service_drepl`, `service_kcc`, `service_dns_update`, `service_ft_scanner`, private libraries `dsdb_garbage_collect_tombstones` and `scavenge_dns_records`, and Python module `python_dsdb`.

## Control Flow

At configure/build generation time Waf recurses into `samdb/ldb_modules`, then registers DSDB targets with their source files, autoproto outputs, public/private library status, subsystem placement, service init functions, and dependencies. AD DC service modules are gated by `bld.AD_DC_BUILD_IS_ENABLED()`. Python embedding helper library names are computed before creating `samba/dsdb.so`.

## State and Persistence Behavior

This file does not persist runtime state. It determines build artifacts and generated prototype files such as `samdb/samdb_proto.h`, `common/proto.h`, `schema/proto.h`, and service proto headers. Changes here affect link composition, installed Python extension availability, and which service modules are built into or alongside the Samba service subsystem.

## Dependencies and Integration Points

The build graph connects DSDB code to Kerberos, DRSUAPI NDR, LDB, auth, credentials, schema, KCC/DREPL services, DNS update support, garbage collection, gMSA, Python LDB/RPC/param embedding libraries, and AD DC enablement. The Python DSDB module has an explicit `dcerpc` dependency to avoid unresolved GENSEC symbols after circular dependency pruning.

## Risks and Edge Cases

Dependency omissions can surface only at link time or when loading `samba/dsdb.so`. Service modules are conditional on AD DC support, so tests that assume DREPL/KCC/DNS update services exist must run with AD DC enabled. Build target naming also forms part of Samba's internal module contract; changing init function names or subsystem values can break service registration.

## Test Signals

Useful signals are successful Waf configure/build, generated autoproto headers, linked `samdb` and `samba/dsdb.so`, and AD DC selftests that load DREPL, KCC, DNS update, tombstone garbage collection, and DNS scavenging services.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/echo_server/echo_server.c -->
# sources/user-network-fs/samba/source4/echo_server/echo_server.c

## Purpose

`echo_server.c` implements Samba's example echo server service. When enabled for selftest, it registers a `service` subsystem module that listens for UDP echo packets on configured interfaces and sends each payload back unchanged.

## Important APIs, Types, and Functions

Key structures are `echo_socket`, `echo_udp_socket`, and `echo_udp_call`. `echo_process()` copies input `DATA_BLOB` bytes to an output blob. `echo_udp_call_loop()` receives datagrams asynchronously, calls `echo_process()`, and schedules replies. `echo_udp_call_sendto_done()` frees per-call state after send completion. `echo_add_socket()` binds a UDP socket and starts the receive loop. `echo_startup_interfaces()` binds each configured interface. `echo_task_init()` decides whether the service runs and initializes service state. `server_service_echo_init()` registers the service details.

## Control Flow

Service registration points the Samba process model at `echo_task_init()`. The task starts only for standalone and AD DC roles, loads the interface list, allocates `struct echo_server`, then calls `echo_startup_interfaces()`. For each interface, `echo_add_socket()` creates a `tsocket_address`, binds a `tdgram` UDP socket, creates a tevent send queue, and posts a `tdgram_recvfrom_send()`. Each receive callback processes one packet, queues a send response to the sender, and immediately posts the next receive operation.

## State and Persistence Behavior

State is entirely in memory and talloc-scoped beneath the task and socket objects. Each UDP packet gets a temporary `echo_udp_call` containing source address, input blob, and output blob; the call is freed when send completes or on failure. There is no durable storage, authentication state, or protocol session state beyond the asynchronous send queue.

## Dependencies and Integration Points

The implementation integrates with Samba's process model, `task_server` lifecycle, loadparm server role, network interface discovery, `tsocket`/`tdgram`, tevent callbacks and queues, NTSTATUS error handling, and service registration. It uses `ECHO_SERVICE_PORT` from `echo_server.h` and is built as the `ECHO` service module by the echo server Waf file.

## Risks and Edge Cases

The service binds port 7 on all configured interfaces, which may require privileges or conflict with an existing echo service. It ignores UDP send errors, appropriate for a sample server but weak for diagnostics. Receive-loop rearming happens even after many failure cases, but allocation failure terminates the task. The `name` and `model_ops` parameters in `echo_add_socket()` are unused, reflecting example-code heritage.

## Test Signals

Signals include successful service registration under selftest builds, startup in standalone or AD DC roles but not domain-member role, UDP bind success for each configured interface, and byte-for-byte UDP echo responses for arbitrary datagrams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/echo_server/echo_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/echo_server/echo_server.h -->
# sources/user-network-fs/samba/source4/echo_server/echo_server.h

## Purpose

`echo_server.h` is the small private header for the source4 echo service example. It declares the service state structure and fixed UDP service port.

## Important APIs, Types, and Functions

The header forward-declares `struct task_server`, defines `struct echo_server` with a single `struct task_server *task` member, and defines `ECHO_SERVICE_PORT` as `7`. It uses an include guard named `__ECHO_SERVER_H__`.

## Control Flow

There is no runtime control flow in the header. `echo_server.c` includes it so service callbacks can carry the owning Samba task through socket and packet-processing state.

## State and Persistence Behavior

`struct echo_server` holds only in-memory task ownership. The port macro fixes all listener creation to the standard echo service port; changing it changes runtime bind behavior wherever `echo_add_socket()` is called.

## Dependencies and Integration Points

The header couples the echo implementation to Samba's `task_server` type without including the full process model header. It is private to the echo server directory and participates in the `ECHO` module build.

## Risks and Edge Cases

Port 7 is a privileged, historically assigned echo port. The double-underscore include guard is reserved-style C naming, though common in older code. The minimal struct leaves future service state additions ABI-local to this module.

## Test Signals

Compile coverage of `echo_server.c` validates the header. Runtime echo service startup validates that the task pointer is initialized before event callbacks dereference it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/echo_server/echo_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/echo_server/wscript_build -->
# sources/user-network-fs/samba/source4/echo_server/wscript_build

## Purpose

`source4/echo_server/wscript_build` registers the echo server example as a Samba service module named `ECHO`.

## Important APIs, Types, and Functions

It uses `bld.SAMBA_MODULE()` with source `echo_server.c`, subsystem `service`, init function `server_service_echo_init`, dependencies `samba-hostconfig LIBTSOCKET LIBSAMBA_TSOCKET`, `local_include=False`, and `enabled=bld.CONFIG_GET('ENABLE_SELFTEST')`.

## Control Flow

During Waf build generation, the module is declared only when `ENABLE_SELFTEST` is configured. If enabled, Samba's service subsystem can load/register the module through `server_service_echo_init()`.

## State and Persistence Behavior

The build file has no runtime state. It controls whether the echo service artifact exists in selftest builds and keeps the sample service out of normal builds.

## Dependencies and Integration Points

The module declaration links the echo service to host configuration and tsocket libraries. Its `subsystem='service'` value is the integration point with Samba's task/service registration mechanism.

## Risks and Edge Cases

Tests or examples that expect the echo service must ensure `ENABLE_SELFTEST` is set. Missing tsocket dependencies would break linkage, while changing `init_function` without matching the C symbol would prevent registration.

## Test Signals

The main signal is a selftest-enabled build producing the `ECHO` service module and successfully resolving `server_service_echo_init`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/echo_server/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/include/includes.h -->
# sources/user-network-fs/samba/source4/include/includes.h

## Purpose

`source4/include/includes.h` is a broad compatibility and utility umbrella header for Samba source4 C files. It ensures the correct replacement/config headers are used, pulls in common system wrappers, and exposes core Samba utility facilities.

## Important APIs, Types, and Functions

The header includes `../replace/replace.h`, system wrappers for time, wait, and locale, `talloc.h`, utility attribute macros, debug support, `samba_util.h`, error definitions, safe string helpers, and setid helpers. In developer Linux C builds, it defines common C++ reserved words such as `class`, `private`, and `new` to preprocessor errors to catch accidental reserved-name use.

## Control Flow

There is no runtime flow. Compile-time flow verifies that any included `config.h` came from Samba unless `NO_CONFIG_H` is set. Conditional macros activate reserved-name checks only outside C++ and only under `DEVELOPER` on Linux.

## State and Persistence Behavior

The header owns no runtime state, but it shapes translation-unit compilation globally. Its include order is intentional: `debug.h` must precede `samba_util.h` for `SMB_ASSERT`, and `_PRINTF_ATTRIBUTE` is mapped to `PRINTF_ATTRIBUTE` if not already defined.

## Dependencies and Integration Points

This file is included by many source4 C files, including the echo server in this subset. It integrates source4 with libreplace portability, talloc allocation, debug/assertion macros, Samba error types, safe string routines, and privilege-changing helpers.

## Risks and Edge Cases

Umbrella headers can hide missing direct dependencies and make compile behavior sensitive to include order. The developer reserved-word macros can break third-party or system headers if enabled too broadly, which is why they are narrowly gated. The config header check intentionally fails standalone builds that accidentally pick up a non-Samba `config.h`.

## Test Signals

Signals are broad compile coverage across source4, developer builds catching reserved-name use, and standalone test builds explicitly defining `NO_CONFIG_H` when they do not include Samba's generated config header.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/include/includes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/ad_claims.c -->
# sources/user-network-fs/samba/source4/kdc/ad_claims.c

## Purpose

`ad_claims.c` constructs Active Directory claims for Kerberos PAC issuance. It decides whether claims are available at the current functional level, reads configured claim types, maps claim definitions to principal attributes, converts attribute values into NDR claim structures, and adds the constructed AuthenticationSilo claim when an enforced authentication silo applies.

## Important APIs, Types, and Functions

Public entry points are `ad_claims_are_issued()` and `get_claims_set_for_principal()`. Internal helpers include `add_attr_unique()` for sorted unique attribute search lists, `fill_claim_int64()`, `fill_claim_uint64()`, `fill_claim_uint64_oid_syntax()`, `fill_claim_boolean()`, `fill_claim_string()`, `fill_claim_string_sec_desc_syntax()`, and `fill_claim_entry()` for value conversion, `claim_applies_to_class()` for class scoping, `get_assigned_silo()` for constructed silo claims, `is_valid_claim_attribute_syntax()` for claim type validation, and `get_all_claims()` for the main DSDB query and assembly loop.

## Control Flow

`get_claims_set_for_principal()` exits unless the DC functional level is at least 2012, reads the principal's last structural class from `objectClass`, and calls `get_all_claims()`. `get_all_claims()` searches `CN=Claim Types,CN=Claims Configuration,CN=Services,<configDN>`, filters enabled claim definitions that apply to the principal class, validates source type and schema syntax, builds a deduplicated list of AD source attributes, and optionally handles the constructed `ad://ext/AuthenticationSilo` claim. If AD-sourced claims remain, it rereads the principal with only the needed attributes and fills `CLAIM_ENTRY` values into a `CLAIMS_SET`.

## State and Persistence Behavior

The file is read-only against DSDB. It allocates transient `CLAIMS_SET`, `CLAIMS_ARRAY`, and `CLAIM_ENTRY` structures under caller-provided talloc contexts and steals/moves successful results out of temporary contexts. It does not persist claims; they are computed for PAC construction from current directory configuration and principal attributes. Invalid individual attribute values are skipped with warnings where possible rather than aborting the whole claim set.

## Dependencies and Integration Points

It depends on DSDB schema lookup, LDB DN/value conversion, generated NDR claim and PAC types, binary search helpers, SDDL/security descriptor conversion, and `authn_policy_util` for authentication silo assignment. The output integrates with KDC PAC construction through `struct CLAIMS_SET`. Claim attribute syntax handling is coupled to AD schema OIDs such as integer, boolean, string, DN/OID, and security descriptor syntaxes.

## Risks and Edge Cases

Functional-level gates mean configured claims are silently absent below FL2012. Claim definitions with invalid source DNs, unsupported syntaxes, disabled state, missing names, or non-applicable classes are skipped. `add_attr_unique()` relies on the array being sized to the number of claim definitions plus a NULL terminator. Value conversion can drop malformed values, potentially issuing partial claims. Security descriptor syntax conversion fails the operation on NDR/SDDL errors.

## Test Signals

Useful tests cover no-claims behavior below FL2012, enabled/disabled claim types, class applicability, each claim value type and syntax, malformed source values being skipped or failed as designed, duplicate source attributes being searched once, constructed AuthenticationSilo claim issuance only for enforced assigned silos, and empty `claims_set_out` when no claim has values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/ad_claims.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/ad_claims.h -->
# sources/user-network-fs/samba/source4/kdc/ad_claims.h

## Purpose

`ad_claims.h` declares the KDC-facing Active Directory claims utility interface used to decide whether to issue claims and to build a claims set for a principal.

## Important APIs, Types, and Functions

The header forward-declares `struct CLAIMS_SET` and declares `ad_claims_are_issued(struct ldb_context *samdb)` plus `get_claims_set_for_principal(struct ldb_context *ldb, TALLOC_CTX *mem_ctx, const struct ldb_message *principal, struct CLAIMS_SET **claims_set_out)`. It includes `data_blob.h` and `ldb.h` for shared Samba/LDB types.

## Control Flow

There is no runtime control flow in the header. Callers first may use `ad_claims_are_issued()` as a feature gate, then call `get_claims_set_for_principal()` with an LDB principal message containing at least `objectClass`.

## State and Persistence Behavior

The API returns claim data allocated under the caller's talloc context. `claims_set_out` is set to `NULL` when claims are not issued or no configured claims produce values. The header itself owns no state.

## Dependencies and Integration Points

This is the integration point between KDC PAC code and `ad_claims.c`. Consumers must link against the KDC claims implementation and generated claims NDR types even though the header keeps `CLAIMS_SET` opaque.

## Risks and Edge Cases

Callers must provide a sufficiently populated principal message; missing `objectClass` causes an operational error in the implementation. The returned `CLAIMS_SET` lifetime follows `mem_ctx`, so PAC assembly must not outlive that context.

## Test Signals

Compile coverage validates signature consistency. Runtime coverage should confirm callers handle `NULL` claim sets and LDB error returns distinctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/ad_claims.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/authn_policy_util.c -->
# sources/user-network-fs/samba/source4/kdc/authn_policy_util.c

## Purpose

`authn_policy_util.c` implements Samba KDC helpers for Active Directory authentication silos and authentication policies. It discovers policies assigned directly or through silos, extracts Kerberos/NTLM/server restriction data, performs security descriptor access checks for authentication restrictions, and creates audit-info structures describing allowed or denied decisions.

## Important APIs, Types, and Functions

Feature gates are `authn_policy_silos_and_policies_in_effect()` for FL2012_R2 and `authn_policy_allowed_ntlm_network_auth_in_effect()` for FL2016. Discovery helpers include `authn_policy_get_attrs()`, `authn_policy_get_assigned_silo()`, and `samba_kdc_authn_policy_msg()`. Public policy lookup functions are `authn_policy_kerberos_client()`, `authn_policy_ntlm_client()`, and `authn_policy_server()`. Enforcement functions are `authn_policy_authenticate_from_device()`, `authn_policy_ntlm_apply_device_restriction()`, and `authn_policy_authenticate_to_service()`. Audit helpers include `_authn_policy_audit_info()` and typed wrappers for Kerberos client, NTLM client, and server policies.

## Control Flow

Policy lookup starts by classifying the account as user, computer, or managed service account and selecting the relevant silo/policy attribute names. `authn_policy_get_assigned_silo()` verifies `msDS-AssignedAuthNPolicySilo`, confirms the account DN appears in `msDS-AuthNPolicySiloMembers`, and reports whether the silo is enforced. `samba_kdc_authn_policy_msg()` chooses the policy from the silo or direct `msDS-AssignedAuthNPolicy`, reads the policy object, and records policy/silo names and enforcement state. Typed lookup functions then copy relevant descriptor blobs, NTLM booleans, or TGT lifetime values into policy structs.

## State and Persistence Behavior

The implementation reads DSDB policy/silo objects and does not modify directory state. It creates talloc-owned policy and audit structures for callers. Descriptor blobs are stolen from searched LDB messages into policy objects so their data survives temporary context cleanup. Audit info stores references to client info and copies policy names/status so later logging can happen after enforcement code frees temporary objects.

## Dependencies and Integration Points

The file depends on `auth/authn_policy_impl.h`, generated auth policy types, DSDB search helpers, loadparm, security descriptor NDR parsing, `auth_generate_security_token()`, claims-aware security token construction, and `sec_access_check_ds()`. It integrates with Kerberos device restrictions, NTLM network authentication policy, and server-side authentication-to-service checks.

## Risks and Edge Cases

Functional-level gates intentionally ignore policies below FL2012_R2 and the NTLM network-auth boolean below FL2016. Missing objectClass or unsupported account classes produce no policy rather than hard failure. Access-check enforcement depends on valid security descriptors with owners; invalid descriptors return audit reasons and can deny when enforced. If a policy is not enforced, access-check failures are converted back to success after audit info is produced.

## Test Signals

Good coverage includes direct policy vs silo policy precedence, enforced vs audit-only behavior, user/computer/service account attribute selection, missing/deleted silo or policy objects, descriptor parse failures, ownerless descriptors, device compound-authentication flags, NTLM denial when device restrictions exist and allowed NTLM is false, and server restriction checks for both Kerberos and NTLM audit event types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/authn_policy_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/authn_policy_util.h -->
# sources/user-network-fs/samba/source4/kdc/authn_policy_util.h

## Purpose

`authn_policy_util.h` exposes the KDC authentication policy utility API for feature gates, policy discovery, restriction enforcement, and audit-info construction.

## Important APIs, Types, and Functions

The header declares feature gates, assigned-silo lookup, Kerberos client policy lookup/enforcement, NTLM client policy lookup/enforcement, server policy lookup/enforcement, and restriction-present predicates. It defines `enum authn_policy_auth_type` with Kerberos and NTLM values, `struct authn_policy_flags` with `force_compounded_authentication`, and location-capturing macros `authn_kerberos_client_policy_audit_info()`, `authn_ntlm_client_policy_audit_info()`, and `authn_server_policy_audit_info()` around underscored implementations.

## Control Flow

Callers use lookup functions to obtain optional policy structs, then call the relevant enforcement or audit helper depending on the authentication path. The audit macros inject `__location__` so later audit records can identify the call site without each caller passing it manually.

## State and Persistence Behavior

Returned policy and audit structures are talloc-owned by the caller's context. The header carries no state, but it documents that `auth_user_info_dc` inputs must be talloc-allocated because implementations may keep references for audit logging.

## Dependencies and Integration Points

It includes replacement portability, public authentication policy/session types, and talloc. Forward declarations avoid exposing LDB and loadparm internals beyond pointer types. This header is consumed by KDC, NTLM, and claims code needing consistent policy behavior.

## Risks and Edge Cases

The API distinguishes `int` LDB-style lookup errors from `NTSTATUS` enforcement results, so callers must not conflate them. Audit output parameters are optional; callers that pass `NULL` lose diagnostics. The location macros should be used instead of underscored functions except when forwarding an existing location.

## Test Signals

Compile tests should catch declaration drift with the implementation. Runtime tests should verify optional `NULL` audit outputs, correct auth-type dispatch, and correct lifetime of returned policy/audit structures across temporary context cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/kdc/authn_policy_util.h -->
