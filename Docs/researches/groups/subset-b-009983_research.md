# Research: subset-b-009983

This grouped report covers Samba source4 RPC torture modules in `sources/user-network-fs/samba/source4/torture/rpc`. Each file section is wrapped with reconciliation markers so it can be split into source-tree-aligned per-file research outputs.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/clusapi.c -->
# sources/user-network-fs/samba/source4/torture/rpc/clusapi.c

## Purpose
`clusapi.c` is a Samba torture suite for the Microsoft Failover Cluster `clusapi` RPC interface. It probes cluster-level calls, resource/resource-type handling, node/group/network/netinterface object handles, cluster registry APIs, and Windows Server group-set APIs. The suite is not just a marshal/unmarshal smoke test: it asserts expected Win32 status codes, handle closure behavior, buffer retry behavior, enumeration type consistency, and several not-implemented or dangerous operations.

## Important APIs, types, and functions
The central state type is `struct torture_clusapi_context`, holding the DCERPC pipe, cached cluster/node names, and cluster version fields discovered during fixture setup. The file is organized around helper pairs: `test_Open*_*`/`test_Close*_*` wrappers for policy-handle objects, object-specific getters (`Get*State`, `Get*Id`, `Get*Type`), control-call helpers (`test_ClusterControl_int`, `test_ResourceTypeControl_int`, `test_NodeControl_int`, `test_GroupControl_int`), and enumeration walkers (`test_all_resources`, `test_all_nodes`, `test_all_groups`, `test_all_networks`, `test_all_netinterfaces`, `test_all_keys`, `test_all_groupsets`). It uses generated client stubs from `ndr_clusapi_c.h`, `torture_rpc_connection`, `torture_tcase_*`, `torture_assert_*`, and registry helpers such as `push_reg_multi_sz` and `pull_reg_sz`.

## Control flow
`torture_rpc_clusapi()` builds the top-level suite and creates test cases for cluster, resource, resourcetype, node, group, network, netinterface, registry, and groupset families. Every test case uses `torture_rpc_clusapi_setup`, which opens the `ndr_table_clusapi` pipe and caches `GetClusterName` plus `GetClusterVersion2` results. Individual tests then open the object under test, exercise one or more operations, and close the handle. Enumeration-based tests call `CreateEnum` for a type, assert each `ENUM_ENTRY.Type`, and dispatch to per-entry helpers that open and inspect the discovered object. Control-call tests deliberately issue control code `0` first and expect `WERR_INVALID_FUNCTION`, then retry with a real control code, handling `WERR_MORE_DATA` by allocating the required output buffer and retrying.

## State and persistence behavior
Most tests are read-only, but several mutate or can mutate cluster state. `CreateResource` creates a resource named `wurst` of type `Generic Service` in `Cluster Group` and deletes it afterward; `SetResourceName` renames the test-created resource before deletion. `OnlineResource`, `OfflineResource`, `PauseNode`, `EvictNode`, and `OfflineGroup` are marked dangerous in registration because they can disrupt cluster availability. `SetClusterName` sends the existing name and expects `WERR_RESOURCE_PROPERTIES_STORED`, so it validates persistence plumbing without changing the logical name. Cluster registry tests open keys and query values/security but do not write. Handle lifecycle is explicitly verified with `ndr_policy_handle_empty()` after close calls.

## Dependencies and integration points
The code depends on a reachable Windows-compatible cluster RPC service, generated NDR clusapi bindings, Samba torture RPC infrastructure, loadparm, talloc, and registry utility functions. It assumes common object names such as `Cluster Name`, `Network Name`, `Cluster Group`, `Cluster Network 1`, and `node1 - Ethernet`, while also relying on live enumeration for broader coverage. The suite is integrated into Samba's torture runner through `struct torture_suite *torture_rpc_clusapi(TALLOC_CTX *mem_ctx)`.

## Risks and edge cases
The strongest risks are environmental: hard-coded object names may fail on clusters with different names, and dangerous tests can alter availability if enabled. Cleanup for created resources is best-effort inside the individual test path; an assertion failure after creation but before deletion can leave a `wurst` resource behind. Buffer-size retry logic is important because several control and registry APIs return `WERR_MORE_DATA`/`WERR_INSUFFICIENT_BUFFER`. Some expected results are version- or implementation-specific, including `WERR_CALL_NOT_IMPLEMENTED` for backup/password/version calls and group-set availability only for major version `0x000a` or newer.

## Test signals
Primary pass signals are successful DCERPC transport status plus expected `WERROR` values. The suite also checks empty policy handles after closes, enum entry type matches, `lpBytesReturned` less than supplied buffer size, proper parsing of REG_SZ blobs, and expected failures for invalid enum/resource names. Dangerous markers are explicit signals to the torture harness that certain operations require opt-in.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/clusapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/countcalls.c -->
# sources/user-network-fs/samba/source4/torture/rpc/countcalls.c

## Purpose
`countcalls.c` is a diagnostic torture helper that estimates how many opnums an RPC interface accepts before returning an out-of-range or disconnect-style status. It can target one configured interface or iterate every registered NDR interface.

## Important APIs, types, and functions
`count_calls()` opens an RPC pipe for a supplied `struct ndr_interface_table`, then invokes `dcerpc_binding_handle_raw_call()` with empty input stubs for opnums `0..499`. `torture_rpc_countcalls()` reads the optional `countcalls:interface` loadparm setting, resolves it with `ndr_table_by_name()`, or walks `ndr_table_list()`. It uses `DATA_BLOB`, `talloc_named()` loop contexts, `torture_rpc_connection()`, and NTSTATUS helpers.

## Control flow
For a single interface, the runner resolves and scans just that interface; unknown names are fatal. For all interfaces, it creates a short-lived talloc context per interface, calls `count_calls(..., all=true)`, and accumulates a boolean result. Inside `count_calls`, connection failures that commonly mean the pipe is absent, inaccessible, or not listening are non-fatal only in all-interface mode. Once connected, the loop stops on `NT_STATUS_RPC_PROCNUM_OUT_OF_RANGE`, disconnects, access denial, or logon failure; the final accepted count is printed. Reaching 500 without a stop status is treated as suspicious failure.

## State and persistence behavior
The module has no persistent state and sends no meaningful request payloads. It may still affect remote logs or connection counters because it sends raw calls to many opnums. It frees each pipe and per-interface context after scanning.

## Dependencies and integration points
It depends on Samba's global NDR table registry, torture RPC connection helpers, and the target server's endpoint availability. It integrates as `bool torture_rpc_countcalls(struct torture_context *torture)`, not as a standard `struct torture_suite` builder.

## Risks and edge cases
Raw empty calls can produce server-side faults, disconnects, or audit noise, especially against interfaces that treat early opnums as state-changing or require non-empty stubs. The count is approximate because access control, authentication failure, or pipe disconnect can end the scan before the true procnum limit. The hard upper bound of 500 is an arbitrary sanity cap.

## Test signals
Useful output is textual: "Scanning pipe" and "Found N calls". Failure signals include unknown interface names, unexpected connection failures for an explicitly requested interface, or no terminating status before 500 opnums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/countcalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/dfs.c -->
# sources/user-network-fs/samba/source4/torture/rpc/dfs.c

## Purpose
`dfs.c` tests the NetDFS RPC interface through Samba's torture framework. It covers DFS manager version/init calls, DFS enumeration and info levels, standalone DFS root creation/removal, DC address getters/setters, and fault-tolerant table flushing.

## Important APIs, types, and functions
The suite registers against `ndr_table_netdfs`. Key helpers include `test_GetManagerVersion_opts`, `test_EnumLevel`, `test_EnumLevelEx`, `test_GetInfo`, `test_AddStdRoot`, `test_AddStdRootForced`, `test_RemoveStdRoot`, `test_FlushFtTable`, `test_GetDcAddress`, and `test_SetDcAddress`. Local provisioning helpers use `libnet_AddShare`, `libnet_DelShare`, `torture_open_connection_share`, `torture_setup_dir`, and `smbcli_deltree`. Constants define the temporary share, directory, and path: `smbtorture_dfs_share`, `\smbtorture_dfs_dir`, and `C:\smbtorture_dfs_dir`.

## Control flow
`torture_rpc_dfs()` creates one RPC tcase named `netdfs` and registers seven tests. Enumeration tests iterate fixed DFS levels and, for level 1 or 300 results, recursively call `GetInfo` or nested `EnumEx` on returned roots. The standalone root test starts with cleanup, creates a directory on `C$`, creates a share pointing to that directory, adds/removes a standard root, exercises forced root creation, then deletes the share and directory. Manager and FT-root helpers first query manager version so Windows Server 2003 unsupported responses can be accepted through `IS_DFS_VERSION_UNSUPPORTED_CALL_W2K3`.

## State and persistence behavior
This file creates real server-side state: a directory under `C$`, an SMB share, and a standalone DFS root. `test_cleanup_stdroot()` attempts pre-cleanup before setup, and `test_StdRoot()` deletes artifacts at the end. If an assertion aborts after provisioning, the share/root/directory can remain. `SetDcAddress` also writes DFS DC address information with TTL 1000. Enumeration and info tests are read-only.

## Dependencies and integration points
The module requires admin-capable credentials from `samba_cmdline_get_creds()`, a configured `host` torture setting, SMB access to `C$`, libnet share management support, and the generated DFS client stubs. It uses both RPC and SMB client paths, making it an integration test across NetDFS, SRVSVC/share management, and SMB filesystem access.

## Risks and edge cases
The test assumes Windows-like administrative shares and permissive credentials. Version handling is explicit for W2K3 unsupported paths but other server differences may still fail. The cleanup sequence is not transactional, so partial artifacts can remain. `EnumEx` level 300 can recurse into multiple roots and amplify environmental failures.

## Test signals
Assertions check NTSTATUS success, WERR success or accepted no-more-items/unsupported values, and successful cleanup calls. Important negative/compatibility signals are `WERR_NOT_SUPPORTED` for selected W2K3 manager-version paths and `WERR_NO_MORE_ITEMS` during DFS enum/info discovery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/drsuapi.c -->
# sources/user-network-fs/samba/source4/torture/rpc/drsuapi.c

## Purpose
`drsuapi.c` is the main Samba torture test case for Active Directory DRSUAPI replication RPCs. It verifies bind negotiation, domain controller discovery, SPN writes, replica metadata queries, replica sync/update reference calls, `DsGetNCChanges`, site cost lookup, unbind, and association-group behavior across multiple DCE/RPC pipes and credential types.

## Important APIs, types, and functions
The file uses `struct DsPrivate` from `drsuapi.h` as shared fixture state: admin and DC credentials, DRS pipe, bind handle, server bind info, domain identifiers, DC info, and temporary domain join handle. Core helpers include `test_DsBind`, `test_DsGetDomainControllerInfo`, `test_DsWriteAccountSpn`, `test_DsReplicaGetInfo`, `test_DsReplicaSync`, `test_DsReplicaUpdateRefs`, `test_DsGetNCChanges`, `test_QuerySitesByCost`, `test_DsUnbind`, `torture_rpc_drsuapi_get_dcinfo`, and the common setup/teardown functions. It calls generated stubs such as `dcerpc_drsuapi_DsBind_r`, `DsGetDomainControllerInfo_r`, `DsWriteAccountSpn_r`, `DsReplicaGetInfo_r`, `DsReplicaSync_r`, `DsReplicaUpdateRefs_r`, `DsGetNCChanges_r`, `QuerySitesByCost_r`, and `DsCrackNames_r`.

## Control flow
`torture_rpc_drsuapi_tcase()` registers one fixture-backed tcase. Setup opens the DRSUAPI pipe, joins the domain as a temporary BDC-like server trust account named from `torturetest` plus a random suffix, binds using a `DsBindInfo28` request advertising many extensions, and gathers DC info. Tests then run independent DRS operations using the cached bind handle. Association-group tests open two pipes in the same association group, bind on one, run `DsCrackNames` on both, close the first, and verify the second still works. The workstation association test temporarily joins a workstation account and leaves it after the check.

## State and persistence behavior
The suite creates a temporary domain machine account during setup and removes it in teardown with `torture_leave_domain`. `test_DsWriteAccountSpn` adds two `smbtortureSPN/*` SPNs to the joined DC computer object and deletes them immediately. `test_DsReplicaUpdateRefs` creates a random destination DSA DNS name, exercises delete/add/duplicate/reset/delete/replace/delete flows, and expects cleanup through final delete. `DsReplicaSync` is gated behind the `dangerous` torture setting because it can trigger replication behavior. `DsGetNCChanges` and metadata queries are read-oriented but can be heavy.

## Dependencies and integration points
This module depends on DRSUAPI generated bindings, domain join helpers, Samba command-line credentials, GUID/SID utilities, loadparm settings, and the companion `drsuapi_cracknames.c` test function. It is tightly integrated with AD semantics and assumes a writable domain controller unless `samba4` skip gates apply.

## Risks and edge cases
Failures between mutation and cleanup can leave SPNs, replica refs, or temporary computer accounts. Several tests skip or alter expectations for Samba4 or dangerous mode, so coverage changes by environment. Random names reduce collision risk but do not make cleanup transactional. `test_DsGetDomainControllerInfo` has a `found` flag that is not reset inside every domain-name iteration, which can hide per-iteration misses after a previous success. Some calls intentionally use random GUIDs and zero high-watermarks, which may be expensive or rejected by stricter servers.

## Test signals
Pass signals combine NTSTATUS success and `WERR_OK` through `torture_drsuapi_assert_call`. Negative expectations include unknown domains returning `WERR_DS_OBJ_NOT_FOUND`, deleting a missing replica ref returning `WERR_DS_DRA_REF_NOT_FOUND`, duplicate add returning `WERR_DS_DRA_REF_ALREADY_EXISTS`, and unsupported replica info returning `NT_STATUS_RPC_ENUM_VALUE_OUT_OF_RANGE`. Dangerous and Samba4 skip comments are explicit runtime signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/drsuapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/drsuapi.h -->
# sources/user-network-fs/samba/source4/torture/rpc/drsuapi.h

## Purpose
`drsuapi.h` is the shared local header for the DRSUAPI torture tests. It defines fixture-private state structures for normal and W2K8-style DRS tests and wraps common DRSUAPI assertion behavior.

## Important APIs, types, and functions
`struct DsPrivate` carries admin credentials, DRS pipe, bind handle, `drsuapi_DsBindInfo28`, domain DN/GUID/DNS state, `drsuapi_DsGetDCInfo2`, a domain join handle, and DC credentials. `struct DsPrivate_w2k8` is similar but stores a bind GUID, generic `drsuapi_DsBindInfoCtr`, and `drsuapi_DsGetDCInfo3` for level 3 DC info. The macros `torture_drsuapi_assert_call_werr` and `torture_drsuapi_assert_call` convert DCERPC NTSTATUS plus request `out.result` into concise torture failures.

## Control flow
The header has no runtime control flow of its own. Including C files allocate one of the private structs in fixture setup, fill it through domain join and `DsBind`, then pass it as tcase data to individual tests. The assertion macro first checks transport status, formats an NT error on failure, and then checks the expected WERROR in the request result.

## State and persistence behavior
The structs hold borrowed and talloc-owned pointers to credentials, pipes, names, GUIDs, and join handles. They do not persist state outside a test process, but the join handles refer to domain accounts created by setup code in the C files. The macros do not clean up; they can abort a test before caller cleanup if used after a state mutation.

## Dependencies and integration points
The header includes generated `librpc/gen_ndr/drsuapi.h` and assumes consumers have visible definitions for `struct cli_credentials`, `struct dcerpc_pipe`, `struct policy_handle`, `struct test_join`, and torture assertion helpers. It is included by the DRSUAPI test modules and is the contract that lets `drsuapi.c`, `drsuapi_cracknames.c`, `drsuapi_w2k8.c`, and `dsgetinfo.c` share fixture semantics.

## Risks and edge cases
The assertion macro body references `tctx` in the `torture_fail()` call instead of consistently using the `_tctx` parameter, so it relies on callers having a variable named `tctx` in scope. Because the macros evaluate `(_pr)->out.result`, they require request structures with that member shape. Abort-on-failure can bypass caller-side best-effort cleanup if used after a mutation.

## Test signals
The macros define the canonical DRSUAPI test signal: successful RPC transport and expected request-level WERROR. `torture_drsuapi_assert_call` is the all-OK shortcut; `torture_drsuapi_assert_call_werr` captures expected failures such as duplicate or missing replica refs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/drsuapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/drsuapi_cracknames.c -->
# sources/user-network-fs/samba/source4/torture/rpc/drsuapi_cracknames.c

## Purpose
`drsuapi_cracknames.c` provides extensive DRSUAPI `DsCrackNames` coverage. It validates conversions among SID, GUID, NT4 account, FQDN 1779 DN, canonical, canonical-ex, user principal, service principal, display, DNS-domain, and unknown formats for a temporary joined machine account and well-known directory objects.

## Important APIs, types, and functions
`struct DsCrackNamesPrivate` embeds `struct DsPrivate` and reserves fields for matrix names. `test_DsCrackNames` is the main table-driven test. `test_DsCrackNamesMatrix` first derives one representation for each supported format and then checks conversion consistency across the format matrix. Setup and teardown delegate to `torture_drsuapi_tcase_setup_common` and `torture_drsuapi_tcase_teardown_common`. The code uses `dcerpc_drsuapi_DsCrackNames_r`, LDB DN canonicalization helpers, SID/GUID helpers, generated `drsuapi_DsName*` structures, and well-known SID constants from `security.h`.

## Control flow
The tcase fixture joins the domain and binds via the common DRSUAPI setup. `test_DsCrackNames` first converts the domain SID to NT4, GUID, and FQDN forms, caches domain DNS/GUID/DN state in `DsPrivate`, builds canonical forms through LDB, discovers the joined test DC DN, and constructs UPN/SPN variants. It then iterates a large `crack[]` table with expected status, optional expected result string, expected DNS domain, alternate accepted status, flags such as `DRSUAPI_DS_NAME_FLAG_SYNTACTICAL_ONLY`, and skip markers for Samba4-specific behavior. After table checks it runs the matrix conversion test.

## State and persistence behavior
The file itself does not write directory state; it relies on the temporary machine account created by common setup. It mutates only in-memory fixture fields such as `domain_dns_name`, `domain_guid_str`, `domain_guid`, and `domain_obj_dn`. It allocates many strings under the fixture talloc context. Directory-visible lifecycle is handled by common teardown, which leaves the joined domain account.

## Dependencies and integration points
This module is coupled to `drsuapi.c` setup helpers and `drsuapi.h` state. It depends on LDB for DN parsing/canonicalization, generated DRSUAPI NDR client stubs, Samba torture settings, well-known SID definitions, and domain join helper accessors such as `torture_join_sid`, `torture_join_user_guid`, and `torture_join_netbios_name`. It is registered into the DRS suite by `torture_rpc_drsuapi_cracknames_tcase()`.

## Risks and edge cases
The expected results encode many AD-specific name-cracking details and can vary with server implementation, localization, existing duplicate objects, or service principal configuration. Alternate statuses are accepted for some well-known names, and some display-name tests skip under Samba4. The matrix test compares strings strictly except for known unmappable formats, so case or formatting differences can be noisy. A notable diagnostic wart is a direct `printf("%s\n", n_from[i])` inside matrix preparation.

## Test signals
The strongest signals are per-row `DsNameStatus` values, expected result strings, expected DNS-domain-only responses, and successful full-matrix consistency. Negative coverage includes invalid GUID/SID/NT4/DN/UPN/SPN strings, bogus services, domain-only SPNs, built-in/NT authority SID behavior, and bind GUID not present in the directory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/drsuapi_cracknames.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/drsuapi_w2k8.c -->
# sources/user-network-fs/samba/source4/torture/rpc/drsuapi_w2k8.c

## Purpose
`drsuapi_w2k8.c` tests DRSUAPI behavior as a Windows Server 2008-style client. Its focus is `DsBind` with a 48-byte bind info structure and `DsGetDomainControllerInfo` level 3, which requires newer extension negotiation.

## Important APIs, types, and functions
The file uses `struct DsPrivate_w2k8`, `test_DsBind_w2k8`, `test_DsGetDomainControllerInfo_w2k8`, `test_DsUnbind_w2k8`, common W2K8 setup/teardown helpers, and `torture_rpc_drsuapi_w2k8_tcase`. `test_DsBind_w2k8` fills `drsuapi_DsBindInfo48`, advertises the same core extension family as the normal DRS tests plus `DRSUAPI_SUPPORTED_EXTENSION_LH_BETA2` in `supported_extensions_ext`, and caches the returned bind info.

## Control flow
Fixture setup opens the DRSUAPI pipe, joins the domain as a temporary server trust account, and performs W2K8 bind. The registered tests include a direct bind test and a level-3 DC-info test. The DC-info test binds first, extracts `supported_extensions_ext` from returned bind-info lengths 32 or 48, asserts LH_BETA2 support, then queries level 3 against NetBIOS and DNS domain names plus unknown names expecting object-not-found. Successful results are searched for the joined DC's NetBIOS name and cached as `dcinfo`.

## State and persistence behavior
The test creates a temporary domain server-trust account in setup and removes it in teardown. It caches the bind GUID, bind handle, server bind info, and level-3 DC info in memory. It has no explicit unbind in registered teardown, though `test_DsUnbind_w2k8` exists and can be reused by callers.

## Dependencies and integration points
It depends on generated DRSUAPI client stubs, Samba torture RPC/domain-join helpers, loadparm, and `drsuapi.h` assertion macros. It complements the normal DRS tests by validating a newer wire contract and DC-info response shape (`drsuapi_DsGetDCInfo3`).

## Risks and edge cases
The level-3 test requires server support for LH_BETA2; older or partial implementations fail early. The loop over domain names contains a `break` before the final `torture_assert(found, ...)`, making that assertion unreachable and limiting checks to the first successful iteration. Setup performs a bind, and the DC-info test performs another bind without an intervening unbind, which is acceptable for the harness but relevant for handle tracking.

## Test signals
Pass signals are NTSTATUS success, `WERR_OK` from bind and level-3 DC-info calls for known names, `WERR_DS_OBJ_NOT_FOUND` for unknown names, non-null bind info, and negotiated LH_BETA2 support. The cached level-3 DC record is the main data signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/drsuapi_w2k8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/dsgetinfo.c -->
# sources/user-network-fs/samba/source4/torture/rpc/dsgetinfo.c

## Purpose
`dsgetinfo.c` is a DRSUAPI `DsReplicaGetInfo` torture test based on `dssync.c`. It binds to DRSUAPI with sealed/signed RPC, discovers the LDAP default naming context, and exercises many replica info types, including linked-object metadata variants.

## Important APIs, types, and functions
`struct DsGetinfoBindInfo` stores pipe, binding handle, bind request, bind GUID, local/peer bind info, and policy handle. `struct DsGetinfoTest` stores the parsed DRSUAPI binding, LDAP/site/domain strings, and admin credentials/bind state. Key functions are `torture_get_ldap_base_dn`, `test_create_context`, `_test_DsBind`, `test_getinfo`, fixture setup/teardown, and `torture_drs_rpc_dsgetinfo_tcase`. It calls `dcerpc_parse_binding`, `dcerpc_binding_set_flags(DCERPC_SIGN | DCERPC_SEAL)`, `dcerpc_pipe_connect_b`, `dcerpc_drsuapi_DsBind_r`, `dcerpc_drsuapi_DsReplicaGetInfo_r`, `dcerpc_drsuapi_DsUnbind_r`, LDB connect/search helpers, and `dsdb_search_dn`.

## Control flow
Setup creates a context from the configured `binding` string, enables signing and sealing, prepares a max-extension `DsBindInfo28`, connects as admin credentials, and binds. `test_getinfo` obtains the domain DN by opening LDAP to the same RPC host and reading `defaultNamingContext`. It skips the replica-info loop when `torture:samba4` is true. Otherwise it iterates a table of DRSUAPI get-info levels and infotypes, builds level 1 or level 2 requests, appends the domain DN to object DN prefixes ending in a comma, applies optional flags, and accepts either success, enum-value-out-of-range transport status, or `WERR_INVALID_LEVEL` as a not-yet-supported signal. Teardown unbinds if the handle exists and frees the context.

## State and persistence behavior
The module does not create directory objects. It creates an RPC bind handle and an LDAP connection; teardown attempts `DsUnbind`. The test reads replication metadata for the domain naming context and for `CN=Domain Admins,CN=Users,<domain DN>` in selected rows. In-memory peer bind info is normalized from returned bind-info lengths 24, 28, 32, 48, or 52 into a `DsBindInfo28` view.

## Dependencies and integration points
It integrates DRSUAPI RPC, LDAP/LDB, DSDB helpers, GENSEC-related includes, Samba command-line credentials, module path resolution for LDB modules, and the DRS torture suite via `torture_drs_rpc_dsgetinfo_tcase()`. It requires a valid `binding` torture setting and credentials with enough directory replication/read metadata permissions.

## Risks and edge cases
LDAP discovery can fail independently of RPC bind, causing the whole test to fail before RPC coverage. The `no_invalid_levels` return value deliberately makes `WERR_INVALID_LEVEL` a soft discovery signal during the loop but a final false result, so partial server support is reported. Some table fields, such as `attribute_name`, are present but not populated in the current rows. Servers with different metadata availability or permission filtering may return implementation-specific errors.

## Test signals
Signals include successful signed/sealed bind, resolved default naming context, per-infotype NTSTATUS success or `NT_STATUS_RPC_ENUM_VALUE_OUT_OF_RANGE`, request-level `WERR_OK`, and `WERR_INVALID_LEVEL` comments for unsupported levels. The final boolean distinguishes full support from not-yet-supported levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/dsgetinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/dssetup.c -->
# sources/user-network-fs/samba/source4/torture/rpc/dssetup.c

## Purpose
`dssetup.c` is a compact torture suite for the DSSETUP RPC interface. It tests `DsRoleGetPrimaryDomainInformation` across all defined info levels from basic information through operation status.

## Important APIs, types, and functions
`test_DsRoleGetPrimaryDomainInformation_ext` is the reusable helper that accepts an expected transport `NTSTATUS`; `test_DsRoleGetPrimaryDomainInformation` calls it expecting `NT_STATUS_OK`. `torture_rpc_dssetup` registers the test against `ndr_table_dssetup`. It uses generated `dcerpc_dssetup_DsRoleGetPrimaryDomainInformation_r` and torture assertions.

## Control flow
The suite creates one RPC tcase named `dssetup`. The test loops from `DS_ROLE_BASIC_INFORMATION` through `DS_ROLE_OP_STATUS`, sets `r.in.level`, calls the generated RPC stub, asserts the transport status equals the expected status, and when that expected status is OK asserts `r.out.result` is `WERR_OK`.

## State and persistence behavior
The module is read-only. It does not allocate persistent server state, alter domain role information, or maintain fixture-private state beyond the stack request structure.

## Dependencies and integration points
It depends on generated DSSETUP NDR client bindings and Samba torture RPC framework. The exported suite builder is the integration point used by the broader torture runner.

## Risks and edge cases
The loop assumes every level in the contiguous enum range is valid and expected to succeed when the transport does. If future enum values are inserted or a server intentionally restricts a level, this simple range loop may over-assert. The `_ext` helper allows other tests to reuse the same loop for expected transport failures.

## Test signals
Pass is simple: every level returns the expected NTSTATUS, and successful transport includes `WERR_OK`. Torture comments include the level number being tested, which is useful for pinpointing failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/dssetup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/echo.c -->
# sources/user-network-fs/samba/source4/torture/rpc/echo.c

## Purpose
`echo.c` is the Samba torture suite for the test `rpcecho` interface. It validates basic scalar calls, conformant arrays, large source/sink data, strings, unions, enums, pointer depth, asynchronous multiplexed calls, and disabled timeout behavior.

## Important APIs, types, and functions
The file registers against `ndr_table_rpcecho`. Test functions include `test_addone`, `test_echodata`, `test_sourcedata`, `test_sinkdata`, `test_testcall`, `test_testcall2`, `test_sleep`, `test_enum`, `test_surrounding`, and `test_doublepointer`. `TEST_ADDONE` is a macro for repeated scalar assertions. `test_sleep` uses `dcerpc_echo_TestSleep_r_send`, `tevent_req_set_callback`, `tevent_loop_once`, and `dcerpc_echo_TestSleep_r_recv` to validate concurrent async behavior. A timeout test exists under `#if 0`.

## Control flow
`torture_rpc_echo()` creates the suite, adds one RPC tcase, and registers all enabled tests. Scalar and data tests build a request, call the generated stub, and compare returned values or byte patterns. `test_sleep` skips in quick mode; otherwise it opens a second echo connection using the same transport and association group with `DCERPC_CONCURRENT_MULTIPLEX`, sends three sleep calls with decreasing durations, and verifies completions arrive asynchronously and not serially. The disabled timeout code documents intended timeout/destruction behavior but is not compiled.

## State and persistence behavior
The suite has no persistent server-side state. It allocates temporary buffers and a second pipe for async testing. Large source/sink tests intentionally move hundreds of kilobytes unless quick mode plus validation flags reduce the sizes. Random lengths and scalar values make runs non-identical but still deterministic in expected byte patterns.

## Dependencies and integration points
It depends on generated echo NDR client stubs, Samba torture RPC helpers, talloc, tevent, binding flag inspection, and transport-aware connection helpers. The suite is a broad integration signal for NDR marshalling, DCE/RPC binding behavior, event-loop progress, and concurrent multiplexing support.

## Risks and edge cases
Large data tests can be slow under validation flags or constrained transports, which is why quick mode reduces sizes. Async timing uses rounded wall-clock differences and can be sensitive to busy servers; it tolerates one-second overhead but fails if sleeps appear serialized. The timeout test is disabled because it needs repair for `ncacn_np`, preserving a known coverage gap.

## Test signals
Signals include exact add-one arithmetic including wraparound cases, byte-for-byte echo/source data validation, string round-trip equality, `TestCall2` NTSTATUS results for levels 1 through 7, enum/pointer/conformant-array success, and async sleep completion timing. Quick-mode skips are explicit for long-running sleep coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/echo.c -->
