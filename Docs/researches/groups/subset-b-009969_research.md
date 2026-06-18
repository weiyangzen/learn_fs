# subset-b-009969 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/unit/prefixmap_tests.c -->
# sources/user-network-fs/samba/source4/torture/drs/unit/prefixmap_tests.c

## Purpose
This file defines the `drs.unit.prefixMap` torture test case for Samba's DSDB schema prefix map implementation. It validates OID prefix table construction, OID-to-ATTID conversion, ATTID-to-OID conversion, DRSUAPI mapping conversion, LDB blob conversion, and persistence of `prefixMap` data through a temporary LDB.

## Important APIs, Types, and Functions
The private fixture `struct drsut_prefixmap_data` owns two `dsdb_schema_prefixmap` fixtures (`pfm_new` and `pfm_full`), a default `dsdb_schema_info`, and a temporary `ldb_context`. `struct drsut_pfm_oid_data` describes expected prefix rows as an id, binary OID hex string, and human-readable OID prefix. `_prefixmap_test_new_data` encodes the default NewPrefixTable values from MS-DRSR, while `_prefixmap_full_map_data` models a fuller Windows Server 2008 clean-schema prefix map. `_prefixmap_test_data` drives OID/ATTID cases, including entries absent from the default map.

Core helpers are `_drsut_prefixmap_new()`, which constructs a `dsdb_schema_prefixmap` from static hex data using `strhex_to_data_blob()`, and `_torture_drs_pfm_compare_same()`, which compares prefix maps by length, id, and binary OID at each index. The tests exercise `dsdb_schema_pfm_new()`, `dsdb_schema_pfm_make_attid()`, `dsdb_schema_pfm_attid_from_oid()`, `dsdb_schema_pfm_oid_from_attid()`, `dsdb_drsuapi_pfm_from_schema_pfm()`, `dsdb_schema_pfm_contains_drsuapi_pfm()`, `dsdb_schema_pfm_from_drsuapi_pfm()`, `dsdb_get_oid_mappings_ldb()`, `dsdb_load_oid_mappings_ldb()`, `dsdb_write_prefixes_from_schema_to_ldb()`, `dsdb_read_prefixes_from_ldb()`, `dsdb_schema_pfm_copy_shallow()`, and `dsdb_create_prefix_mapping()`.

## Control Flow
`torture_drs_unit_prefixmap()` registers a fixture-backed torture tcase named `prefixMap`. Setup allocates the fixture, builds default and full prefix maps, obtains a default schemaInfo object from `drsut_schemainfo_new()`, and creates a temporary LDB containing a schema base DN with a placeholder `prefixMap` attribute. Individual tests then cover: default map construction; `make_attid` on full and initially small maps; lookup-only `attid_from_oid` without mutation; reverse `oid_from_attid`; rejected ATTID ranges; schema-prefixMap to DRSUAPI conversion and back; schema-prefixMap to LDB values and back; direct LDB read/write; and incremental prefix creation through `dsdb_create_prefix_mapping()`.

The `dsdb_create_prefix_mapping` test is the most stateful path. It writes the initial prefix map to LDB, then iterates over OID cases. For OIDs not present in the base map it predicts the new map by copying and extending the prefix map, calls `dsdb_create_prefix_mapping()`, asserts that the in-memory schema prefix map pointer and contents did not change immediately, and verifies that LDB now contains the predicted updated prefix map.

## State and Persistence Behavior
Most state is fixture-owned and freed by talloc teardown. Persistent behavior is limited to a temporary LDB created via `torture_temp_dir()`, `ldb_init()`, and `ldb_connect()`. Tests set the `"schemaNamingContext"` opaque to `CN=Schema,CN=Config`, add a schema base record, and write/read `prefixMap` plus `schemaInfo` through DSDB helpers. There is no durable repository or system state, but failed tests may leave temporary files under the torture temp area until harness cleanup.

## Dependencies and Integration Points
The file depends on Samba torture APIs, DSDB schema APIs, DRSUAPI structures, LDB, NDR data blob helpers, talloc, and `drsut_schemainfo_new()` from the schemaInfo unit tests. It integrates into the DRS torture module through `torture_drs_unit_prefixmap()` and is built by the neighboring DRS `wscript_build` as part of `TORTURE_DRS`.

## Risks
The tests assume exact prefix-map ordering, so legitimate implementation changes that preserve semantic lookup but reorder prefixes can fail. Several checks compare Windows-derived fixture data, which makes the file sensitive to schema fixture drift. LDB tests require the mock schema base DN and placeholder attribute to be shaped exactly as DSDB helper code expects. The small-map test intentionally allows new prefix ids to be implementation-dependent except for the ATTID low word; broadening that assertion would make the test brittle.

## Test Signals
Passing signals include exact default prefix map match, expected ATTID values for full maps, no mutation from lookup-only APIs, correct error codes for invalid ATTID ranges, successful DRSUAPI and LDB round trips including schemaInfo placement, and LDB updates that match predicted prefix map growth. Failures isolate prefix map creation, conversion, persistence, and mutation semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/unit/prefixmap_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/unit/schemainfo_tests.c -->
# sources/user-network-fs/samba/source4/torture/drs/unit/schemainfo_tests.c

## Purpose
This file defines `drs.unit.schemaInfo`, a DSDB/DRSUAPI schemaInfo torture unit suite. It validates construction, binary blob conversion, schemaInfo comparison semantics, and LDB module read/write/update helpers for the schemaInfo attribute used by Active Directory schema replication.

## Important APIs, Types, and Functions
`SCHEMA_INFO_INIT_STR` and `SCHEMA_INFO_DEFAULT_STR` define canonical 21-byte schemaInfo blobs: marker `0xFF`, revision, and invocation GUID. `struct schemainfo_data` stores a parsed blob, expected `dsdb_schema_info`, expected `WERROR`, and whether reverse conversion should be tested. `struct drsut_schemainfo_data` owns the temporary LDB, mock `ldb_module`, mock `dsdb_schema`, initial `schema_info`, and expanded test vector array. The `torture_assert_schema_info_equal` macro checks revision and invocation id.

Key helpers are `_drsut_schemainfo_new()`, public `drsut_schemainfo_new()`, `_drsut_ldb_schema_info_reset()`, and `_drsut_ldb_setup()`. Tests call `dsdb_schema_info_new()`, `dsdb_schema_info_blob_new()`, `dsdb_schema_info_from_blob()`, `dsdb_blob_from_schema_info()`, `dsdb_schema_info_cmp()`, `dsdb_module_schema_info_blob_write()`, `dsdb_module_schema_info_blob_read()`, and `dsdb_module_schema_info_update()`.

## Control Flow
Setup expands the static schemaInfo vectors into parsed `DATA_BLOB` and `GUID` structures, creates a wrapped temporary LDB, sets `"schemaNamingContext"`, adds an initial `schemaInfo`, creates a mock LDB module, creates a mock schema, pre-caches `"cache.invocation_id"`, and starts an LDB transaction. The test cases then validate default constructor output, parsing valid and invalid blobs, reverse blob generation for valid vectors, comparison behavior against malformed and revision-conflict DRSUAPI mapping containers, module-level blob write/read, and module-level schemaInfo update.

`test_dsdb_schema_info_cmp()` is the main behavioral matrix. It checks missing mapping data, empty schemaInfo mapping, invalid length, invalid marker, older remote schema acceptance, invalid id prefix rejection, equal schema acceptance, newer revision mismatch, newer revision with different invocation id mismatch, older revision with different invocation id acceptance, and same revision with different invocation id conflict.

## State and Persistence Behavior
The suite writes schemaInfo values into a temporary LDB record at the schema base DN and runs all tests inside one transaction. Teardown commits the transaction so failures can still expose LDB state during diagnostics, then frees the fixture. The tests manipulate mock LDB state but do not persist production SAM database data.

## Dependencies and Integration Points
The file depends on Samba torture, DSDB/SAMDB, DSDB LDB module utilities, `ldb_wrap`, DRSUAPI/NDR structures, loadparm, talloc, and GUID parsing. `drsut_schemainfo_new()` is intentionally public within the DRS torture unit area and is used by the prefixMap tests for schemaInfo fixture creation. The suite is registered through `torture_drs_unit_schemainfo()` and built into `TORTURE_DRS`.

## Risks
The tests encode exact binary schemaInfo layout and comparison policy, so changes to marker, length, revision semantics, or invocation-id conflict handling need corresponding fixture updates. The transaction commit in teardown means a setup failure after LDB allocation can still attempt commit; the code comments acknowledge teardown runs after partial setup. Mocking the LDB module is lightweight and may not catch behavior that depends on a full module stack.

## Test Signals
Passing signals include valid 21-byte schemaInfo round trips, invalid blob rejection, correct default zero schemaInfo construction, expected schema mismatch/conflict codes, successful module blob persistence, and update behavior that writes the schema's default invocation id/revision into LDB.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/unit/schemainfo_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/wscript_build -->
# sources/user-network-fs/samba/source4/torture/drs/wscript_build

## Purpose
This Waf build fragment declares the `TORTURE_DRS` internal smbtorture module. It bundles DRS initialization, DRS helper utilities, DRS unit tests, and DRS RPC torture tests into one module gated by Python build support.

## Important APIs, Types, and Functions
The file uses `bld.SAMBA_MODULE()` with module name `TORTURE_DRS`. The `source` list includes `drs_init.c`, `drs_util.c`, `unit/prefixmap_tests.c`, `unit/schemainfo_tests.c`, `rpc/dssync.c`, and `rpc/msds_intid.c`. It emits `proto.h` through `autoproto`, declares subsystem `smbtorture`, sets `init_function='torture_drs_init'`, marks the module internal, and enables it only when `bld.PYTHON_BUILD_IS_ENABLED()` is true.

## Control Flow
At configure/build time Waf evaluates this Python fragment. If the Python build is enabled, Waf compiles the listed sources, generates prototypes, links them against the declared dependencies, and registers `torture_drs_init` as the module initializer for smbtorture discovery.

## State and Persistence Behavior
The file has no runtime state. Its persistence effect is build-system metadata: changing sources, dependencies, or enablement changes what torture tests are compiled into the Samba build.

## Dependencies and Integration Points
Dependencies include core Samba utility libraries, LDB, Samba error handling, torture framework, DCERPC/NDR DRSUAPI bindings, GENSEC, hostconfig, DSDB module helpers, ASN.1 utilities, SAMDB, credentials, resolve helpers, loadparm resolve support, and `torturemain`. The build fragment is the integration point that makes the DRS unit files visible to the larger smbtorture binary/module set.

## Risks
Missing a dependency here can surface as link failures or latent build-order problems after source changes. Removing a source silently removes tests from the DRS module. The Python-build gate means environments without Python build support will not compile these tests, which matters for coverage expectations.

## Test Signals
The signal is build-time: successful compilation of `TORTURE_DRS`, generated `proto.h`, resolved `torture_drs_init`, and availability of DRS torture suites in smbtorture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/drs/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/gentest.c -->
# sources/user-network-fs/samba/source4/torture/gentest.c

## Purpose
`gentest.c` is a differential SMB/SMB2 torture generator. It connects to two UNC shares, executes the same seeded sequence of randomly generated file operations against both servers, and fails when statuses, metadata, oplock behavior, or change notifications diverge outside configured ignore patterns.

## Important APIs, Types, and Functions
Global `options` controls protocol (`smb2`), seed, operation count, oplock use, ignored differences, preset seed replay, reconnect strategy, cleanup, and valid-only field generation. `servers[NSERVERS]` stores two test targets, each with two connection instances. `open_handles` maps local handle slots to corresponding SMB1 fnums or SMB2 handles on both servers. `op_parms` stores per-operation seeds and disabled flags for replay/backtracking. `current_op` records the active operation name, seed, status, talloc context, op index, and mismatch label.

Connection and state helpers include `connect_servers()`, `connect_servers_fast()`, `time_skew()`, handle mapping/add/remove functions, `wipe_files()`, and `dump_seeds()`. Random generators cover filenames, patterns, offsets, counts, access masks, create options, attributes, timestamps, EAs, security descriptors, locks, and reserved fields. SMB1 handlers include open/openx/ntcreatex, close, unlink, mkdir/rmdir, rename/ntrename, seek, readx/writex, lockingx, qpathinfo/qfileinfo, spathinfo/sfileinfo, and change notify. SMB2 handlers include create, close, read, write, lock, flush, echo, qfileinfo, and sfileinfo.

The macros `GEN_COPY_PARM`, `GEN_CALL`, `GEN_CALL_SMB`, `GEN_CALL_SMB2`, handle translation macros, and `CHECK_*` comparison macros are central. They clone generated parameters to both servers, translate local handles to each server's real handle, execute the protocol call, compare NTSTATUS values, check async side effects, and compare selected output fields.

## Control Flow
`main()` initializes Samba command-line support, parses two UNC targets and options, loads credentials, splits UNC names, initializes events and GENSEC, and calls `start_gentest()`. `start_gentest()` allocates handle and seed arrays, loads preset seeds or generates deterministic seeds from `options.seed`, then calls `run_test()`. `run_test()` connects/reconnects, writes seeds, wipes the `gentest` tree unless disabled, resets open handle state and operation counters, and loops over `options.numops`.

For each operation, `run_test()` seeds the PRNG with that operation's stored seed, picks an instance and an operation matching the selected protocol and ignore list, creates an operation talloc context, invokes the handler, records success counts, and stops on first mismatch. If analysis is enabled, `backtrack_analyze()` repeatedly disables chunks of operations and reruns the test to shrink the reproducer while preserving the same mismatch class. `analysecontinuous` keeps rerunning until failure.

## State and Persistence Behavior
The program deliberately mutates remote shares under a `gentest` directory: it creates, deletes, renames, writes, locks, changes metadata, creates EAs/security descriptors, and may leave files if `--skip-cleanup` is set or the process aborts. It persists a seed file through atomic `seeds.tmp` rename when `--seedsfile` is configured, enabling replay. Runtime state is mostly global and deterministic per operation seed, which is essential for reproducing failures and backtracking.

## Dependencies and Integration Points
The file uses Samba client raw SMB1 APIs, SMB2 APIs, event handling, credentials, GENSEC, loadparm, resolver configuration, security descriptor helpers, popt command-line support, and utility file loading. It is a standalone torture executable/tool rather than a suite registration file, and it integrates with real SMB servers via UNC paths and credentials.

## Risks
This tool is intentionally destructive to the target `gentest` tree and should run only against disposable shares. Differential comparison can produce false positives for legitimate server differences such as timestamp skew, indexing attributes, unsupported EAs/ACLs, or ignored status mappings; options like `--maskindexing`, `--noeas`, `--noacls`, and ignore files mitigate this. Global mutable state and async oplock/notify paths make replay sensitive to timing. Some SMB2 async processing is stubbed/commented, and SMB2 oplock/notify coverage is explicitly incomplete.

## Test Signals
Primary success is completing all generated operations with no unignored divergence and printing per-operation success counts. Failure reports include operation number, operation name, mismatched NTSTATUS or field, and current seeds. Seed dumping and backtracking provide reproducible minimized sequences for protocol or server behavior bugs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/gentest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/gpo/apply.c -->
# sources/user-network-fs/samba/source4/torture/gpo/apply.c

## Purpose
This file implements the `gpo.apply.gpo_param_from_gpo` torture test. It verifies that Samba's GPO update command applies, skips reapplying, force reapplies, and unapplies domain password policy settings from SYSVOL `GptTmpl.inf` into SAMDB domain attributes.

## Important APIs, Types, and Functions
`gpo_apply_suite()` creates the `apply` suite and registers `torture_gpo_system_access_policies()`. `exec_wait()` runs the configured GPO update command asynchronously via `samba_runcmd_send()`, polls with `tevent_req_poll_ntstatus()`, and returns the child exit status from `samba_runcmd_recv()`. `unix2nttime()` converts negative AD interval strings to days for comparing `minPwdAge` and `maxPwdAge`.

Constants `GPODIR`, `GPOFILE`, `GPTTMPL`, and `GPTINI` define the SYSVOL policy paths and generated security template. The tested SAMDB attributes are `minPwdAge`, `maxPwdAge`, `minPwdLength`, and `pwdProperties`.

## Control Flow
The test resolves the configured `sysvol` path, creates the default domain policy SecEdit directory, fetches `gpo update command`, connects to SAMDB as `system_session()`, and stores the original domain password-policy attributes. It then iterates three policy vectors, writes `GptTmpl.inf`, increments `GPT.INI` version, runs the update command, searches SAMDB, and asserts that all four attributes match the vector.

After the apply loop, the test resets SAMDB attributes to the original message using `LDB_FLAG_MOD_REPLACE`, runs the normal update command again, and asserts the settings are not reapplied without a version/force trigger. It builds a command with `--force`, verifies the last vector is reapplied, then builds a command with `--unapply` and verifies original SAMDB values are restored.

## State and Persistence Behavior
This is an integration test with real side effects. It creates and overwrites files under SYSVOL for the default domain policy, increments `GPT.INI`, invokes the configured GPO updater process, and modifies domain password-policy attributes in SAMDB. It attempts to restore the original SAMDB attributes through unapply, but file contents and GPT version changes remain part of the test environment. It relies on talloc cleanup for local allocations, not on transaction rollback.

## Dependencies and Integration Points
The file depends on loadparm for SYSVOL path and GPO command, `mkdir_p()`, SAMDB connection helpers, system session credentials, LDB search/modify APIs, the tevent command runner, and the smbtorture assertion framework. It integrates into `TORTURE_GPO` through `gpo_apply_suite()` and `torture_gpo_init()`.

## Risks
Running this test against a non-disposable domain can alter password policy and SYSVOL contents. It assumes the AD DNS name/path `addom.samba.example.com` and default domain policy GUID layout, so environments with different names or layouts may fail unless provisioned for this test. Command construction appends `--force` and `--unapply` to the configured command array, so unusual wrapper commands may not accept those flags. If the test aborts before reset/unapply, policy settings can be left changed.

## Test Signals
Passing signals include successful command execution, SAMDB search returning exactly one base object, applied attribute values matching each generated template, normal re-run preserving manually restored values, `--force` reapplying the latest template, and `--unapply` restoring original values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/gpo/apply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/gpo/gpo.c -->
# sources/user-network-fs/samba/source4/torture/gpo/gpo.c

## Purpose
This file is the smbtorture registration entry point for Group Policy tests. It creates the top-level `gpo` suite, attaches the apply sub-suite, and registers it with the torture framework.

## Important APIs, Types, and Functions
The sole function is `NTSTATUS torture_gpo_init(TALLOC_CTX *ctx)`. It calls `torture_suite_create(ctx, "gpo")`, adds `gpo_apply_suite(suite)` through `torture_suite_add_suite()`, sets a description, registers the suite with `torture_register_suite()`, and returns `NT_STATUS_OK`.

## Control Flow
When the `TORTURE_GPO` module is loaded, the build-declared init function `torture_gpo_init` runs. It constructs the suite hierarchy and exposes the apply tests to smbtorture discovery.

## State and Persistence Behavior
The file has no persistent runtime state beyond allocating suite metadata under the supplied talloc context. It does not execute tests directly.

## Dependencies and Integration Points
It depends on `torture/smbtorture.h` and generated/local `torture/gpo/proto.h`. Its direct integration point is `gpo_apply_suite()` from `apply.c`; its external integration point is the `TORTURE_GPO` build module's `init_function`.

## Risks
The file is small but critical for discoverability: if the suite name, init function, or sub-suite call drifts from `wscript_build`, GPO tests may compile but not appear in smbtorture. There is no local validation of `gpo_apply_suite()` returning a non-null suite.

## Test Signals
The signal is suite registration: smbtorture should list a `gpo` suite with an `apply` child containing the GPO parameter test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/gpo/gpo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/gpo/wscript_build -->
# sources/user-network-fs/samba/source4/torture/gpo/wscript_build

## Purpose
This Waf build fragment declares the `TORTURE_GPO` internal smbtorture module that compiles and registers Group Policy torture tests.

## Important APIs, Types, and Functions
The file calls `bld.SAMBA_MODULE('TORTURE_GPO', ...)`. It lists `gpo.c` and `apply.c` as sources, targets subsystem `smbtorture`, depends on `torture samba-util-core ldb`, marks the module internal, generates `proto.h`, and sets `init_function='torture_gpo_init'`.

## Control Flow
During build evaluation Waf compiles the two GPO source files, generates prototypes, links the declared dependencies, and records `torture_gpo_init` as the entry point for module registration.

## State and Persistence Behavior
The fragment has no runtime state. Its persistent effect is build metadata controlling whether GPO torture code is compiled into Samba's internal test module set.

## Dependencies and Integration Points
The dependencies reflect the suite's use of the torture framework, core utility helpers, and LDB/SAMDB-adjacent APIs. The generated `proto.h` connects `gpo.c` and `apply.c` declarations.

## Risks
If `apply.c` gains dependencies without updating this fragment, link failures or missing symbols can occur. If `init_function` no longer matches `gpo.c`, the module may build but fail to register tests.

## Test Signals
Build success and smbtorture discovery of `TORTURE_GPO`/`gpo` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/gpo/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/kdc-canon-heimdal.c -->
# sources/user-network-fs/samba/source4/torture/krb5/kdc-canon-heimdal.c

## Purpose
This file builds a Heimdal-specific Kerberos canonicalization torture suite. It tests AS-REQ and TGS behavior for combinations of canonicalization, enterprise principals, uppercase usernames, Win2K option, UPNs, S4U2Self, implicit dollar removal, and AS-REQ service principals, then validates both client-side principal expectations and server-side PAC acceptance.

## Important APIs, Types, and Functions
Bit flags `TEST_CANONICALIZE`, `TEST_ENTERPRISE`, `TEST_UPPER_USERNAME`, `TEST_WIN2K`, `TEST_UPN`, `TEST_S4U2SELF`, `TEST_REMOVEDOLLAR`, and `TEST_AS_REQ_SPN` generate the test matrix. `struct test_data` stores naming inputs and booleans for each matrix dimension. `struct torture_krb5_context` owns the Samba krb5 context, target KDC address, current test data, and a packet counter. `struct pac_data` captures the principal name extracted during server-side GENSEC/PAC processing.

`test_generate_session_info_pac()` decodes a PAC via `kerberos_pac_blob_to_user_info_dc()` and generates session info without local database lookup while recording the principal string. `test_accept_ticket()` starts a server-side GENSEC krb5 context, accepts an AP-REQ blob, retrieves session info, and asserts the PAC principal matches expectation. `test_krb5_send_to_realm_canon_override()` forces TCP sends to the configured KDC address and increments packet counts. `torture_krb5_init_context_canon()` creates the Samba krb5 context and installs that send override. `torture_krb5_as_req_canon()` is the main test body. `torture_krb5_canon()` generates sub-suites for valid flag combinations.

## Control Flow
Each generated test resolves optional torture settings for UPN, service, hostname, removed-dollar enablement, machine-account expectation, and canonicalization-related loadparm values. It skips combinations that require missing UPN/SPN settings or intentionally unsupported flag mixes. It builds the requested principal string, canonical principal, and expected returned principal; parses them with Heimdal `krb5_parse_name_flags()`; sets principal name types for SPN cases; then performs password-based initial credential acquisition with canonicalize and Win2K options.

After AS-REQ, it validates expected errors for unknown SPNs, removed-dollar restrictions, or required-canonicalization policy. On success it checks client principal type/name, krbtgt server principal components and realm, stores credentials in a memory ccache, and then exercises several TGS paths: canonicalized krbtgt referral behavior, self-service ticket acquisition including S4U2Self, AP-REQ creation and acceptance, host/service ticket creation through `krb5_mk_req()`, explicit `KRB5_NT_SRV_INST` and `KRB5_NT_SRV_HST` requests, and exact request for the krbtgt from the initial ticket.

## State and Persistence Behavior
The test performs real Kerberos exchanges with the target KDC at port 88 and stores credentials in a memory ccache named from the test case. It does not write Samba databases, but it depends on live credentials, KDC policy, configured service principals, and optional UPN/SPN fixtures. Packet count is transient state used to assert expected network behavior.

## Dependencies and Integration Points
The file is tightly integrated with Heimdal-style krb5 APIs, Samba's `smb_krb5_context`, GENSEC server krb5 mechanism, PAC decoding, Samba command-line credentials, loadparm KDC policy options, and torture settings. It is registered as the `canon` Kerberos suite by `torture_krb5_canon()` in the krb5 torture module.

## Risks
The matrix is environment-sensitive: missing UPNs, host SPNs, machine-account SPNs, or removed-dollar enablement cause skips or expected failures. Assertions depend on Samba KDC options such as `kdc require canonicalization`, implicit-dollar matching, and whether acceptors report canonical client names. Heimdal client behavior around referrals and looping is encoded directly, so porting assumptions to MIT would be incorrect. Because it uses real credentials and a live KDC, failures can reflect environment provisioning rather than code regressions.

## Test Signals
Passing signals include expected AS-REQ success or precise Kerberos error codes, correct canonical client principal and krbtgt naming, expected packet counts for referral paths, correct service-ticket success/failure based on machine-account expectations, and successful server-side GENSEC acceptance with the expected PAC principal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/kdc-canon-heimdal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/kdc-canon-mit.c -->
# sources/user-network-fs/samba/source4/torture/krb5/kdc-canon-mit.c

## Purpose
This file is the MIT Kerberos variant of Samba's KDC canonicalization torture tests. It covers a narrower matrix than the Heimdal version, focusing on canonicalization, enterprise principals, uppercase usernames, UPNs, removed-dollar matching, and AS-REQ service principal behavior using MIT-compatible krb5 APIs.

## Important APIs, Types, and Functions
The test flags are `TEST_CANONICALIZE`, `TEST_ENTERPRISE`, `TEST_UPPER_USERNAME`, `TEST_UPN`, `TEST_REMOVEDOLLAR`, and `TEST_AS_REQ_SPN`. `struct test_data` mirrors the naming and flag state needed by each generated case. `struct torture_krb5_context` holds a Samba krb5 context and parsed target KDC address. `test_generate_session_info_pac()` and `test_accept_ticket()` match the Heimdal variant's purpose: decode PAC data without local database lookup and verify the accepted ticket's principal string through GENSEC.

MIT-specific API use includes `krb5_get_init_creds_opt_set_canonicalize(krb_options, ...)`, `smb_krb5_principal_set_type()`, `smb_krb5_principal_get_type()`, `smb_krb5_principal_get_comp_string()`, `smb_krb5_principal_get_realm()`, `krb5_get_credentials()`, and `krb5_mk_req_extended()`. `torture_krb5_init_context_canon()` initializes the Samba krb5 context and records the target KDC address, but unlike the Heimdal variant it does not install a packet-counting send override.

## Control Flow
Each generated case checks required torture settings, skips intentionally unsupported combinations, derives UPN or SPN principal strings, uppercases realm and optionally username, applies removed-dollar transformation when enabled, and computes canonical/expected principal strings. It parses principals with optional enterprise flags and sets principal types for SPN cases through Samba wrapper helpers.

The main test obtains initial credentials by password with the canonicalize option, verifies expected unknown-principal errors for non-UPN SPNs, removed-dollar restrictions, or required-canonicalization policy, then checks returned client principal type/name and krbtgt server principal structure. It stores the TGT in a memory ccache, obtains canonicalized credentials with `krb5_get_credentials()`, and then attempts to get a service ticket for the tested principal. For machine-account-capable cases it builds an AP-REQ using `krb5_mk_req_extended()` and verifies server-side PAC acceptance; otherwise it expects `KRB5KDC_ERR_S_PRINCIPAL_UNKNOWN`.

## State and Persistence Behavior
The test uses live KDC communication and memory credential caches. It does not persist database state or write files. It relies on the process credentials from Samba command-line parsing and on configured torture settings for optional UPN/SPN coverage.

## Dependencies and Integration Points
The file depends on MIT-compatible Kerberos behavior exposed through Samba wrappers, Samba's krb5 context, GENSEC krb5 server support, PAC decoding, command-line credentials, loadparm KDC policy options, and smbtorture suite generation. `torture_krb5_canon_mit()` registers the generated `canon` suite for MIT builds.

## Risks
MIT and Heimdal APIs differ, so this file intentionally avoids Heimdal-only send overrides, packet count assertions, Win2K option handling, S4U2Self matrix coverage, and some host referral checks. Environment provisioning remains a major source of skips/failures: UPN tests require `torture:krb5-upn`, SPN tests require hostname/service settings, removed-dollar tests require an explicit opt-in, and successful service-ticket/AP-REQ paths usually require a machine account with a servicePrincipalName. Loadparm canonicalization policy changes alter expected errors.

## Test Signals
Passing signals include expected initial-credential success or exact Kerberos errors, correct returned principal name/type, correct krbtgt component and realm handling, successful memory ccache storage, expected `krb5_get_credentials()` behavior, and successful GENSEC/PAC principal verification for machine-account service-ticket cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/krb5/kdc-canon-mit.c -->
