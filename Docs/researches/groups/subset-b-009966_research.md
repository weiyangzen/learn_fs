# subset-b-009966 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dns/dlz_bind9.c -->
# sources/user-network-fs/samba/source4/torture/dns/dlz_bind9.c Research

## Purpose
This file defines the `dlz_bind9` smbtorture suite for Samba AD DC DNS integration through the BIND9 DLZ module. It validates module creation, BIND callback registration, zone configuration, GENSEC based update authorization, record lookup and dump callbacks, dynamic update transactions, zone transfer authorization, and DNS aging timestamp behavior backed by the AD DNS LDB.

## Important APIs, Types, And Functions
The suite calls the DLZ entry points from `dns_server/dlz_minimal.h`: `dlz_version`, `dlz_create`, `dlz_configure`, `dlz_destroy`, `dlz_lookup`, `dlz_allnodes`, `dlz_newversion`, `dlz_addrdataset`, `dlz_subrdataset`, `dlz_delrdataset`, `dlz_closeversion`, `dlz_ssumatch`, and `dlz_allowzonexfr`. `dlz_bind9_binddns_dir()` builds the `ldb://.../dns/sam.ldb` URL from `lpcfg_binddns_dir()`. `dlz_bind9_log_wrapper()` adapts DLZ logging to `torture_comment()` via the global `tctx_static`. `dlz_bind9_writeable_zone_hook()` is a test callback that opens `dns/sam.ldb` with `samdb_connect_url()` and verifies a `dnsZone` object exists. `test_expected_record` and `test_expected_rr` hold expected callback output for lookup and zone dump tests; `dlz_bind9_putrr_hook()` and `dlz_bind9_putnamedrr_hook()` feed actual records into `dlz_bind9_putnamedrr_torture_hook()` for normalization and assertion.

## Control Flow
The tests follow a common setup path: create a DLZ instance with `-H ldb://.../dns/sam.ldb`, register test callbacks, configure the instance, run a focused operation, then destroy `dbdata`. Basic tests check version, create, configure, repeated configure, and destroy order. Security tests build a GENSEC client for the `dns/host.domain` service with command line credentials, generate an initial token, and pass it to `dlz_ssumatch()`. Lookup and zone dump tests register `putrr` and `putnamedrr` callbacks, build expected SOA, NS, A, AAAA, and SRV records, and assert the callbacks fire with exact record counts.

`test_dlz_bind9_update01()` is a transactional dynamic-update scenario. It authenticates update rights, starts DLZ versions, adds and removes A records, commits or cancels versions, and checks lookup results after each step. `test_dlz_bind9_allowzonexfr()` checks default denial, then mutates `lp_ctx` with allow and deny client lists and verifies IPv4, IPv6, prefix, and explicit deny behavior. `test_dlz_bind9_aging()` is the most stateful path: it adds A, AAAA, PTR, MX, and CNAME-oriented test records, inspects `dnsRecord` blobs through NDR, toggles zone aging through `samba-tool dns zoneoptions`, directly edits record timestamps in LDB, and checks refresh, static zero timestamp, and aging-off semantics.

## State And Persistence
Most tests allocate temporary TALLOC objects and destroy `dbdata`, but several mutate persistent AD DNS state. `update01` creates and deletes a node named after the test function in the DNS application partition. `aging` creates records under `CN=MicrosoftDNS,DC=DomainDnsZones`, changes zone aging options through `samba-tool`, and writes `dnsRecord` blobs with `ldb_modify()`. The test assumes cleanup by deleting all records at the end, but failures before cleanup can leave DNS nodes or zone aging state behind. The global `calls_zone_hook` and `tctx_static` are process-global test state and would be unsafe for parallel execution inside one process.

## Dependencies And Integration Points
The suite depends on Samba smbtorture, BIND DLZ shim APIs, GENSEC, command line credentials, LDB/SamDB, DSDB DNS utilities, generated DNS server NDR types, and runtime AD DC settings such as `host`, `dnsdomain`, `SERVER`, `USERNAME`, and `PASSWORD`. It is built as the `TORTURE_BIND_DNS` module by `wscript_build` only when AD DC support is enabled and compiled with `-DBIND_VERSION_9_16`.

## Risks And Test Signals
Important signals are exact ISC result codes, callback invocation counts, normalized DNS data comparisons, NDR timestamp checks, and expected zone transfer authorization results. Risks include reliance on a live provisioned AD DC, mutable global process state, shelling out to `bin/samba-tool`, time-sensitive DNS aging assertions with hourly resolution, persistent LDB mutations on assertion failure, and BIND API version coupling. The suite is a high-value integration test because it verifies both public DLZ behavior and Samba's persisted AD DNS record representation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dns/dlz_bind9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dns/internal_dns.c -->
# sources/user-network-fs/samba/source4/torture/dns/internal_dns.c Research

## Purpose
This file defines a small smbtorture suite named `dns_internal` that probes Samba's internal DNS server over DNS TCP. It verifies that the server answers an A query for its own DC hostname and refuses an unauthenticated dynamic update for that same host.

## Important APIs, Types, And Functions
`setup_connection()` opens a DNS TCP connection to `getenv("DC_SERVER_IP")` with `dns_open_connection()`. `get_dns_domain()` lowercases `REALM` into a DNS domain. `str_to_sockaddr()` converts an IPv4 string into a `sockaddr_storage` for A record construction. `test_internal_dns_query_self()` creates a query with `dns_create_query()`, sends it with `dns_transaction()`, and checks `dns_response_code()` for `DNS_NO_ERROR`. `test_internal_dns_update_self()` builds an update with `dns_create_update()`, creates an A record with `dns_create_a_record()`, adds it with `dns_add_rrec()`, sends it with `dns_update_transaction()`, and expects `DNS_REFUSED`.

## Control Flow
Both tests derive the FQDN as `DC_SERVER.lower(REALM)`, open a DNS connection, construct a request, execute the transaction, and validate only the DNS response code. The query test expects success for a self A lookup. The update test attempts to add the existing DC server IP as a 300 second A record and expects refusal, which establishes that unauthenticated or disallowed updates are blocked by the internal DNS server.

## State And Persistence
The query test is read-only. The update test should not persist a record because refusal is the expected result. All request objects are tied to the TALLOC context or DNS connection. The test depends heavily on process environment variables and does not validate that they are present before using them.

## Dependencies And Integration Points
The file uses `lib/addns/dns.h`, TALLOC, smbtorture registration, libc IPv4 parsing, and environment variables `DC_SERVER_IP`, `DC_SERVER`, and `REALM`. `torture_internal_dns_init()` registers the suite with the smbtorture harness. The build script creates it as `TORTURE_INTERNAL_DNS` when AD DC support is enabled.

## Risks And Test Signals
The main signals are `DNS_NO_ERROR` for the self query and `DNS_REFUSED` for the update. The file has two FIXME comments noting that the answer body is not unmarshaled, so it cannot assert the returned A data. Risks include IPv4-only update setup, missing environment validation, and false positives where any successful response code passes even if the payload is wrong.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dns/internal_dns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dns/wscript_build -->
# sources/user-network-fs/samba/source4/torture/dns/wscript_build Research

## Purpose
This Waf build fragment declares the DNS torture modules for Samba AD DC builds. It wires the BIND DLZ integration tests and internal DNS tests into the `smbtorture` subsystem.

## Important APIs, Types, And Functions
The script is guarded by `bld.AD_DC_BUILD_IS_ENABLED()`. Inside that guard it calls `bld.SAMBA_MODULE()` twice. `TORTURE_BIND_DNS` uses `dlz_bind9.c`, initializes through `torture_bind_dns_init`, defines `BIND_VERSION_9_16`, and depends on `torture`, `talloc`, `torturemain`, and `dlz_bind9_for_torture`. `TORTURE_INTERNAL_DNS` uses `internal_dns.c`, initializes through `torture_internal_dns_init`, and depends on `torture`, `talloc`, and `torturemain`.

## Control Flow
There is no runtime control flow beyond build-time conditional registration. If AD DC support is disabled, neither module is declared. If enabled, both modules are internal smbtorture modules and become available through the smbtorture plugin initialization functions named in this file.

## State And Persistence
The file affects build graph state only. It does not persist runtime data. Its important persistent effect is the compiled module set included in an AD DC capable build.

## Dependencies And Integration Points
This fragment integrates with Samba's Waf build system and the smbtorture subsystem. The BIND DLZ test has an explicit dependency on `dlz_bind9_for_torture`, which provides the DLZ interface under test. The `-DBIND_VERSION_9_16` define couples compilation to the expected BIND9 API shape.

## Risks And Test Signals
The key signal is successful module build and registration when AD DC is enabled. Risks include stale BIND version flags, missing DLZ torture dependency, or silently absent DNS torture coverage in non-AD-DC builds. Because this file is only 19 lines, most behavioral validation lives in the C test files it registers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/dns/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/drs_init.c -->
# sources/user-network-fs/samba/source4/torture/drs/drs_init.c Research

## Purpose
This file initializes the C-side DRSUAPI smbtorture module. It creates and registers two suite namespaces: remote RPC tests under `drs.rpc` and local/unit-style DRS tests under `drs.unit`.

## Important APIs, Types, And Functions
`torture_drs_rpc_suite()` creates a suite, adds `torture_drs_rpc_dssync_tcase()` and `torture_drs_rpc_dsintid_tcase()`, and assigns the description `DRSUAPI RPC Tests Suite`. `torture_drs_unit_suite()` creates a suite, adds `torture_drs_unit_prefixmap()` and `torture_drs_unit_schemainfo()`, and assigns the description `DRSUAPI Unit Tests Suite`. `torture_drs_init()` is the module entry point called by smbtorture.

## Control Flow
Initialization is linear. `torture_drs_init()` builds the RPC suite, checks for allocation failure, registers it, then builds and registers the unit suite. A failed suite allocation returns `NT_STATUS_NO_MEMORY`; otherwise the function returns `NT_STATUS_OK`.

## State And Persistence
The file creates in-memory `torture_suite` objects under the provided TALLOC context. It does not mutate directory state or persistent data directly. The persistent behavior of the registered cases is implemented elsewhere.

## Dependencies And Integration Points
The file includes smbtorture, DRSUAPI torture declarations, SamDB headers, and `torture/drs/proto.h` for test case registration functions. It is the integration point that exposes lower-level DRS C tests to the smbtorture runner.

## Risks And Test Signals
The main test signal is suite registration. Risks are minimal but include missing prototype coverage if a tcase registration function changes or if suite allocation failures are not surfaced by the caller. This file is structural glue rather than business logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/drs_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/drs_util.c -->
# sources/user-network-fs/samba/source4/torture/drs/drs_util.c Research

## Purpose
This file provides shared C utility functions for DRSUAPI torture tests. It decodes DRS attribute IDs into OID strings using a prefix map and loads a DSDB schema into an LDB connection from DRSUAPI prefix-map data.

## Important APIs, Types, And Functions
`drs_util_oid_from_attid()` implements the MS-DRSR attribute ID decoding algorithm. It splits an `attid` into high and low words, verifies the final prefix-map entry is the special schema-info entry with `id_prefix == 0` and binary OID marker `0xFF`, finds the matching prefix mapping by high word, appends a BER encoded low word, and converts the binary OID with `ber_read_OID_String()`. It optionally returns the prefix-map index.

`drs_util_dsdb_schema_load_ldb()` checks whether a schema is already attached to an LDB, builds a new schema when needed, loads the DRS prefix map with `dsdb_load_prefixmap_from_drsuapi()`, searches the schema naming context for `attributeSchema` and `classSchema` objects, loads them into the schema with `dsdb_load_ldb_results_into_schema()`, and attaches the schema through `dsdb_set_schema(..., SCHEMA_WRITE)`.

## Control Flow
Both functions are assertion-heavy test helpers. On malformed prefix maps, allocation failures, missing schema base DN, failed searches, schema conversion failures, or schema attachment failures, they call torture assertion/failure helpers rather than returning detailed error codes. Successful paths return `true`.

## State And Persistence
`drs_util_oid_from_attid()` allocates temporary binary OID data under a named TALLOC context and returns the decoded OID under the torture context. `drs_util_dsdb_schema_load_ldb()` mutates the in-memory state of the supplied LDB connection by installing a schema. It does not write schema objects to disk, but future operations on that LDB will observe the attached schema.

## Dependencies And Integration Points
The file depends on DRSUAPI generated types, DSDB schema helpers, SamDB, LDB, ASN.1 BER OID decoding, and the smbtorture assertion framework. It supports tests that consume `DsGetNCChanges()` schema or prefix map responses and then need normal DSDB schema interpretation locally.

## Risks And Test Signals
Signals are successful OID decoding and successful LDB schema attachment. Risks include trusting `prefix_map->num_mappings - 1` without an explicit zero-count guard, strict assumptions about the special final mapping, and fatal test assertions rather than recoverable errors. Correctness is important because prefix-map mistakes can make later replication assertions compare the wrong attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/drs_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/cracknames.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/cracknames.py Research

## Purpose
This Python test module validates DRSUAPI `DsCrackNames` behavior for common Active Directory name formats, including round trips through GUID form and edge cases for multi-valued or missing service principal names.

## Important APIs, Types, And Functions
`DrsCracknamesTestCase` extends `drs_base.DrsBaseTestCase`. `setUp()` binds to DC1 via `_ds_bind()`, creates an OU and a user with `sAMAccountName`, `userPrincipalName`, `servicePrincipalName`, and `displayName`, deletes and re-adds the user, and defines the supported `DS_NAME_FORMAT` constants to exercise. `_do_cracknames()` builds `drsuapi.DsNameRequest1`, sets codepage, language, offered and desired formats, and calls `self.drs.DsCrackNames()`.

## Control Flow
`test_Cracknames()` first cracks the user's FQDN DN to a GUID, then loops over every configured name format, cracking GUID to that format and back to GUID while asserting `DRSUAPI_DS_NAME_STATUS_OK`. `test_MultiValuedAttribute()` creates a second user with two SPNs, cracks to GUID, then requests service principal format and expects `DRSUAPI_DS_NAME_STATUS_NOT_UNIQUE`. `test_NoSPNAttribute()` creates a user without SPN and expects `DRSUAPI_DS_NAME_STATUS_NOT_FOUND` when converting GUID to service principal format.

## State And Persistence
The test creates an OU and several user objects in DC1. `tearDown()` deletes the main user and OU; individual tests delete their additional users. If a failure occurs before cleanup, test objects can remain in the directory. The delete and re-add in `setUp()` appears to ensure cracknames works for a re-created object and avoids stale state.

## Dependencies And Integration Points
The module depends on `drs_base`, `samba.tests`, LDB, and `samba.dcerpc.drsuapi`. It requires a two-DC test environment through the base class, although these tests primarily bind and mutate DC1. It integrates with Samba's Python subunit test runner.

## Risks And Test Signals
Signals are `ctr.count == 1` and precise `ctr.array[0].status` values. Risks include fixed object names that can collide with leftover state, partial cleanup on failure, and assumptions about which DS name formats Samba supports compared with Windows. It is valuable coverage for name cracking format compatibility and ambiguity handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/cracknames.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/delete_object.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/delete_object.py Research

## Purpose
This module tests how deleted objects and linked attributes replicate between two DCs when concurrent modifications occur on one DC and deletion occurs on another. It verifies tombstone shape, deletion replication ordering, and group membership backlink cleanup.

## Important APIs, Types, And Functions
`DrsDeleteObjectTestCase` derives from `DrsBaseTestCase`. `setUp()` disables inbound and outbound replication on both DCs, then forces synchronization both ways. `tearDown()` re-enables replication. `_check_obj()` searches by original `objectGUID` with `show_deleted:1`, finds the Deleted Objects container through `_deleted_objects_dn()`, and verifies either normal object state or deleted-object/tombstone state. It checks attributes such as `isDeleted`, `objectCategory`, `sAMAccountType`, `description`, `memberOf`, `member`, DN location, and `name/cn` mangling with `DEL:<guid>`.

## Control Flow
`test_ReplicateDeletedObject1()` creates a user on DC1, replicates it to DC2, deletes it on DC1, then modifies the still-live copy on DC2 by adding a description and group membership. It first replicates DC2 to DC1 to ensure those modifications do not resurrect or overwrite the deletion, then replicates DC1 to DC2 to propagate the tombstone. It also deletes the related groups and verifies backlinks are removed.

`test_ReplicateDeletedObject2()` sets up the same conflict but replicates the deletion from DC1 to DC2 before pulling DC2 to DC1. It validates that the deletion wins and that group membership attributes are cleaned up on both sides. Both scenarios use forced `samba-tool drs replicate` through base helpers.

## State And Persistence
The tests deliberately alter DC replication options, create users and groups, modify links, delete objects, and force replication. They rely on `tearDown()` to re-enable replication. Deleted objects remain as tombstones by design until directory garbage collection. Failures can leave replication disabled or temporary groups/users present, making this a high-impact integration test.

## Dependencies And Integration Points
The module depends on LDB, DRS helper methods in `drs_base`, two writable DCs, `samba-tool drs options`, and `samba-tool drs replicate`. It uses direct LDAP writes plus explicit replication commands to create deterministic conflict order.

## Risks And Test Signals
Signals are correct tombstone attributes, correct Deleted Objects DN placement, unchanged deleted state after conflicting modification replication, and removal of forward links. Risks include replication option cleanup failure, timing-sensitive replication state, leftover tombstones, and incomplete TODO coverage for `replPropertyMetaData` and recycle-bin behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/delete_object.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/drs_base.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/drs_base.py Research

## Purpose
This file is the shared base library for Samba's Python DRS tests. It provides environment setup for two DCs, command helpers for `samba-tool drs`, DRS RPC bind helpers, raw `DsGetNCChanges` request builders, response validators, and linked-attribute comparison primitives.

## Important APIs, Types, And Functions
`DrsBaseTestCase.setUp()` obtains credentials, enables GENSEC sealing, connects to `DC1` and `DC2` as LDAP SamDBs, and caches schema, domain, config, forest level, and DNS host names. Command helpers include `_samba_tool_cmd_list()`, `_run_drs_kcc()`, `_net_drs_replicate()`, `_enable_inbound_repl()`, `_disable_inbound_repl()`, `_enable_all_repl()`, and `_disable_all_repl()`. Directory helpers include `_deleted_objects_dn()`, `_lost_and_found_dn()`, `_make_obj_name()`, `_get_highest_hwm_utdv()`, and `_get_identifier()`.

The DRS RPC helpers are central. `_ds_bind()` creates a sealed `ncacn_ip_tcp` DRSUAPI binding and calls `drs_DsBind()`. `_exop_req8()` and `_getnc_req10()` construct request levels 8 and 10, including naming context identifier, high-watermark, replica flags, extended operation, partial attribute sets, prefix maps, and request10 `more_flags`. `_get_replication()` sends `DsGetNCChanges`, validates a level 6 response, source DSA GUID, invocation ID, and extended return, then returns the response. `_check_replication()` and `_check_ctr6()` validate returned DNs, linked attributes, `more_data`, NC counts, and DRS error state. `AbstractLink` implements MS-DRSR link ordering/equality semantics.

## Control Flow
Subclasses call `setUp()`, create or mutate directory state, then use base helpers either to run black-box `samba-tool drs` commands or to issue raw DRSUAPI RPC calls. The validation path generally builds a request, sends `DsGetNCChanges`, extracts object DNs and linked attributes from CTR6, filters intermittent RID Set changes, and compares ordered or unordered expectations. Request construction defaults to the active test LDB's NTDS GUID, invocation ID, and domain DN unless overridden.

## State And Persistence
The base class persists DC connections and cached naming context state per test instance. It can mutate DC replication options via `samba-tool drs options` and trigger replication. It does not create application objects by itself, but its helpers are used by subclasses that do. `AbstractLink` stores packed GUID blobs for deterministic sort and hash behavior.

## Dependencies And Integration Points
The file integrates Python Samba test infrastructure, LDB, generated DRSUAPI/misc/security/drsblobs types, NDR packing, GENSEC, Kerberos ccache command plumbing, and the subunit/SambaTool test base. It is the compatibility layer between high-level Python tests and low-level DRSUAPI protocol structures.

## Risks And Test Signals
Key signals are successful sealed DRS binds, command success with empty stderr, exact CTR6 object/link/count fields, and stable linked-attribute ordering. Risks include strong dependence on `DC1` and `DC2` environment variables, side effects from replication option helpers, filtering of RID Set changes hiding some noise but not all, broad exception handling around link target unpacking, and request defaults that can mask missing test setup if a subclass forgets to set explicit DNs or handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/drs_base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/fsmo.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/fsmo.py Research

## Purpose
This module tests FSMO role transfer through `samba-tool fsmo transfer` for schema, infrastructure, PDC, RID, naming, DomainDnsZones, and ForestDnsZones roles. It verifies both real transfers between DCs and no-op behavior when the target already owns a role.

## Important APIs, Types, And Functions
`DrsFsmoTestCase.setUp()` caches each DC's `dsServiceName` and builds role owner DNs such as schema DN, `CN=Infrastructure`, `CN=Partitions`, `CN=RID Manager$,CN=System`, and DNS application partition infrastructure DNs. `_net_fsmo_role_transfer()` runs `samba-tool fsmo transfer --role=<role> -H ldap://<DC>:389` using the current Kerberos ccache. `_wait_for_role_transfer()` polls `fSMORoleOwner` until it matches the expected service name or times out. `_role_transfer()` is the shared scenario for transfer to DC2, transfer back to DC1, and no-op transfer to DC1.

## Control Flow
Each `test_*Transfer()` method calls `_role_transfer()` with a role name and role DN. `_role_transfer()` transfers from DC1 to DC2 and waits against DC2, transfers back from DC2 to DC1 and waits against DC1, then invokes a no-op transfer to DC1 and verifies ownership remains DC1. Polling uses a 20 second maximum with 0.2 second sleeps.

## State And Persistence
The test changes real FSMO role ownership in the test domain. It attempts to restore each role to DC1 as part of the scenario, but failures between transfer and transfer-back can leave roles on DC2. No custom objects are created. The test relies on replication or local update visibility for `fSMORoleOwner`.

## Dependencies And Integration Points
The module depends on `drs_base`, LDB base searches, SambaTool command execution, Kerberos ccache credentials, and two DCs able to transfer all listed FSMO roles. It is a black-box command test with LDAP verification.

## Risks And Test Signals
Signals are successful command exit, expected stdout text for real and no-op transfers, empty stderr, and `fSMORoleOwner` values matching the target DC service names. Risks include role ownership left changed on failure, timing-sensitive polling, and role DN construction issues for DNS application partitions due to embedded spacing in the formatted strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/fsmo.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/getnc_exop.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/getnc_exop.py Research

## Purpose
This module is a broad semi-black-box test suite for `DsGetNCChanges` extended operations, prefix-map handling, linked-attribute return ordering, ancestor and target flags, FSMO error paths, and partial attribute set behavior. It aims to keep Samba behavior compatible with Windows DRSUAPI edge cases.

## Important APIs, Types, And Functions
`_linked_attribute_compare()` implements MS-DRSR linked-attribute ordering for raw DRS link structures. `DrsReplicaSyncTestCase` covers extended operation behavior and invalid inputs. It uses `_determine_fSMORoleOwner()` to identify FSMO owner and non-owner DC metadata, `_check_exop_failed()` to validate failed EXOP CTR6 shape, and inherited `_getnc_req10()`, `_exop_req8()`, `_check_replication()`, and `_check_ctr6()` for most checks.

`DrsReplicaPrefixMapTestCase` verifies partial attribute set and mapping behavior, including missing prefix map, invalid attid, secret `unicodePwd`, regular `name`, and `partial_attribute_set_ex`. `_samdb_fetch_pfm_and_schi()` reads `prefixMap` and `schemaInfo` from the schema NC and appends a schema-info mapping. `DrsReplicaSyncSortTestCase` creates users/groups and validates linked-attribute sort ordering for both single-object replication and whole-NC replication.

## Control Flow
The sync tests create a random OU, bind to DC1 by DRS RPC, and capture default high-watermark and up-to-date vectors. Single object tests assert `DRSUAPI_EXOP_REPL_OBJ` returns only the requested object even with `GET_ANC` or `GET_TGT`. Invalid NC/GUID tests construct request8 payloads with dummy DNs, invalid GUIDs, or valid GUID-only identifiers and assert Windows-compatible error or success behavior. `test_link_utdv_hwm()` progressively creates nested OUs, a disabled computer, containers, and `managedBy` links, then repeats replication checks under combinations of `WRIT_REP`, `CRITICAL_ONLY`, `GET_ANC`, `GET_TGT`, high-watermark, and up-to-date vector inputs.

FSMO tests send EXOP FSMO requests to owner and non-owner DCs and validate extended return codes such as `FSMO_NOT_OWNER` and `UNKNOWN_CALLER`. Prefix-map tests intentionally request attributes through normal and modified mappings to ensure Samba maps incoming attids correctly and rejects schema mismatches. Sort tests compare returned linked attributes to local expected ordering before and after a link deletion makes one link inactive.

## State And Persistence
The module creates random OUs, users, groups, computer objects, containers, and linked attributes on DC1, then deletes test OUs with `tree_delete:1` in teardown. It does not generally force replication with `samba-tool`; it tests DRS RPC responses directly. High-watermarks and UTD vectors are captured as state checkpoints and reused to query incremental changes. Failures can leave temporary directory objects and changed links.

## Dependencies And Integration Points
The suite depends on `drs_base`, LDB, Samba generated DRSUAPI and misc types, NDR packing/unpacking, `drs_DsBind`, Windows-compatible werror values, and two DCs for FSMO owner decisions. It is tightly integrated with DRS request levels 8 and 10 and with schema prefix-map encoding.

## Risks And Test Signals
Signals include exact WERROR exceptions, level 6 responses, `extended_ret`, source DSA GUID/invocation ID, object DN order, linked attribute count/order, `more_data`, NC counts, and returned attribute attids. Risks include very high scenario complexity, Windows/Samba differences documented inline, broad exception handling while unpacking linked targets, dependence on random object cleanup, and sensitivity to unrelated directory churn that changes high-watermarks or returned object order.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/getnc_exop.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/getnc_schema.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/getnc_schema.py Research

## Purpose
This module tests schema partition replication scenarios, especially schema objects with dependency links that cross replication chunks and linked attributes on schema objects. It is explicitly gated because repeated execution can damage Windows Active Directory test environments.

## Important APIs, Types, And Functions
The module asserts `PLEASE_BREAK_MY_WINDOWS=1` before defining tests. `SchemaReplicationTests` extends `DrsBaseTestCase`. `setUp()` captures credentials, sets command-line auth, chooses DC1 as source and DC2 as destination, disables inbound/all replication on DC1, and initializes a uniqueness offset. `do_repl()` temporarily enables replication, runs `samba-tool drs replicate <dest> <source> <partition>`, retries once after 10 seconds on failure, disables replication again, and asserts success. `get_unique()`, `unique_gov_id_prefix()`, and `unique_cn_prefix()` generate schema-safe unique identifiers because schema objects cannot be deleted normally.

## Control Flow
`test_poss_superiors_across_chunk()` creates 150 `classSchema` objects chained through `systemPossSuperiors`, handling `ERR_NO_SUCH_ATTRIBUTE` by triggering schema update, then modifies them in reverse order and replicates the schema partition. The goal is to ensure links that cross the default 133 object replication chunk boundary are replicated correctly.

`test_create_linked_attribute_in_schema()` creates a user outside schema, creates an auxiliary class that may contain `managedBy`, creates a schema object using that class with `managedBy` pointing to the user, and verifies both the forward link and `managedObjects` backlink. `test_schema_linked_attributes()` creates multiple such schema objects, replicates schema, then validates all destination forward links and the user's backlink set.

## State And Persistence
This file permanently creates schema classes and schema objects. It also creates users in the domain partition and toggles replication options. The top-level environment assertion is a deliberate safety gate because schema changes accumulate and can break Windows AD after several runs. `tearDown()` re-enables replication but does not delete schema objects.

## Dependencies And Integration Points
The module depends on `drs_base`, LDB LDIF add/modify APIs, SambaTool DRS replication, environment variables `DC1`, `DC2`, `SMB_CONF_PATH`, credentials, and live writable schema permissions. It exercises schema update behavior and DRS chunking in a way normal unit tests cannot.

## Risks And Test Signals
Signals are successful schema object searches on the destination, correct `managedBy` forward links, and exact `managedObjects` backlink sets. Risks are intentionally severe: permanent schema mutation, replication option side effects, possible Windows AD breakage, timing retries around replication, and no cleanup for schema objects. The environment gate is the primary risk control.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/getnc_schema.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/getnc_unpriv.py -->
# sources/user-network-fs/samba/source4/torture/drs/python/getnc_unpriv.py Research

## Purpose
This module tests `DsGetNCChanges` authorization behavior for users with no replication rights, only `DS-Replication-Get-Changes`, only `DS-Replication-Get-Changes-All`, or both rights. It covers single-object replication, secret replication, full NC replication, invalid DNs, OU-as-NC requests, and partial attribute sets.

## Important APIs, Types, And Functions
`DrsReplicaSyncUnprivTestCase.setUp()` creates a random OU, creates a test user, binds as administrator and as that user, builds ACE strings for `GUID_DRS_GET_CHANGES` and `GUID_DRS_GET_ALL_CHANGES`, saves the original base DN security descriptor, and disables Kerberos for the new user credentials to avoid replication-to-KDC races. `tearDown()` restores the original security descriptor and tree-deletes the OU.

Helper methods `_test_repl_exop()`, `_test_repl_single_obj()`, `_test_repl_secret()`, `_test_repl_full()`, and `_test_repl_full_on_ou()` build request8 payloads with `DRSUAPI_DRS_WRIT_REP`, send them through the unprivileged DRS handle, and either expect success or catch `WERRORError` with one of a permitted set of Windows/Samba-compatible errors.

## Control Flow
Each test grants a specific ACL state on the domain base DN and runs the same family of replication requests. With only GET_CHANGES, most single-object and secret requests are denied, full replication is denied, but partial attribute set requests can succeed. With only GET_ALL_CHANGES, the module deliberately reuses the no-rights expectations because this right alone permits seeing results but not initiating replication. With both rights, valid single-object and full replication succeed while invalid DNs and REPL_SECRET keep documented error expectations. With no rights, all replication forms are rejected, with some accepted variability between `BAD_DN`, `BAD_NC`, and `ACCESS_DENIED`.

## State And Persistence
The test creates a user and OU and modifies the security descriptor on the domain base DN by adding object-specific control access ACEs. It stores and restores the original SDDL, which is critical because a failed teardown could leave elevated replication rights granted to the test user. Temporary objects are tree-deleted.

## Dependencies And Integration Points
The module depends on `drs_base`, `samba.tests`, `sd_utils.SDUtils`, generated DRSUAPI/security constants, Samba credentials, LDB, and werror exception types. It integrates directly with DRSUAPI request8 and Active Directory security descriptors.

## Risks And Test Signals
Signals are success/no-exception for permitted requests and exact WERROR families for denied or invalid requests. Risks include security descriptor restoration failure, differences between Samba and Microsoft error precedence, race avoidance by disabling Kerberos rather than waiting for replication, and reliance on random OU names to avoid stale cleanup collisions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/python/getnc_unpriv.py -->
