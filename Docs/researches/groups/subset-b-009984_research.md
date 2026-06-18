# Research: subset-b-009984

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/epmapper.c -->
# sources/user-network-fs/samba/source4/torture/rpc/epmapper.c

## Purpose
This file defines the `rpc.epmapper` smbtorture suite for exercising the DCE/RPC endpoint mapper interface. It validates endpoint lookup iteration, tower mapping, temporary endpoint insertion/deletion, and explicit lookup-handle cleanup through generated `dcerpc_epm_*` client stubs.

## Important APIs, Types, And Functions
The test case is registered by `torture_rpc_epmapper()`, which binds to `ndr_table_epmapper` and adds `Map_simple`, `Map_full`, `Lookup_simple`, `Lookup_terminate_search`, and `Insert_noreplace`. `display_tower()` formats `struct epm_tower` floors through `epm_floor_string()`. `test_Insert()` and `test_Delete()` build an endpoint tower from a `struct dcerpc_binding` with `dcerpc_binding_build_tower()` and call `dcerpc_epm_Insert_r()` or `dcerpc_epm_Delete_r()`. `test_Map_tcpip()` constructs a TCP endpoint-map request and validates the returned floors. `test_Lookup_simple()` and `test_Lookup_terminate_search()` drive `epm_Lookup` pagination and `epm_LookupHandleFree`.

## Control Flow
The suite creates an endpoint-mapper RPC tcase and runs independent tests against the same RPC interface. Lookup tests initialize an empty `policy_handle`, request all endpoint entries in batches, print returned annotations and towers, then assert the search ends with no more entries and an empty handle. The termination test stops after one batch and frees the non-empty lookup handle. The full mapping test inserts a synthetic TCP endpoint for a known object syntax, maps it back, then deletes it.

## State And Persistence Behavior
Most tests are read-only. `test_Insert()`, `test_Delete()`, `test_Map_full()`, and `test_Insert_noreplace()` mutate the endpoint mapper database by registering temporary endpoints. Insert tests are skipped when the `samba4` torture option is set, reflecting server compatibility and state-safety concerns. Cleanup depends on the delete call succeeding after insertion; failures between insert and delete can leave temporary `SMBTORTURE` or `smbtorture endpoint` entries.

## Dependencies And Integration Points
The file depends on generated endpoint mapper NDR stubs, NDR syntax tables, DCE/RPC binding helpers, endpoint tower conversion helpers, `is_ipaddress()`, and the Samba torture RPC harness. It integrates with endpoint mapper transport data through `struct epm_twr_t`, `struct epm_entry_t`, `struct epm_Map`, `struct epm_Lookup`, and `struct policy_handle`.

## Risks And Edge Cases
The inserted TCP binding uses a hard-coded IP and port only as tower data, so the test assumes the mapper accepts synthetic endpoints and later maps by interface syntax. Protocol-floor mutation in `test_Map_display()` reuses a tower from lookup results and changes floors in-place for TCP, HTTP, UDP, SMB, and NetBIOS probes, which can make debugging hard if later checks reuse the same entry. The lookup loops rely on correct empty-handle behavior to avoid leaked server-side search state.

## Test Signals
Strong signals are exact `EPMAPPER_STATUS_OK`, `EPMAPPER_STATUS_NO_MORE_ENTRIES`, `NT_STATUS_RPC_SS_CONTEXT_MISMATCH` absence, valid dynamic TCP ports, valid IP address strings, NDR transfer syntax matches, and empty lookup handles after natural completion. Insert/delete success and no-replace behavior are the mutation signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/epmapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/eventlog.c -->
# sources/user-network-fs/samba/source4/torture/rpc/eventlog.c

## Purpose
This file implements the `rpc.eventlog` smbtorture suite for Windows Event Log RPC operations. It opens a log handle, reads and decodes event records, reports a new event, flushes, clears, queries log metadata, and tests backup-log path behavior.

## Important APIs, Types, And Functions
`torture_rpc_eventlog()` registers tests on `ndr_table_eventlog`. `get_policy_handle()` opens the `"dns server"` event log with `eventlog_OpenEventLogW`. `init_lsa_String()` prepares UTF-16 byte lengths for `lsa_String` inputs. Test functions call `dcerpc_eventlog_GetNumRecords_r`, `ReadEventLogW_r`, `ReportEventW_r`, `FlushEventLog_r`, `ClearEventLogW_r`, `GetLogInformation_r`, `OpenBackupEventLogW_r`, `BackupEventLogW_r`, and `CloseEventLog_r`.

## Control Flow
Each test opens a fresh event log handle, performs one scenario, and closes the handle. `test_ReadEventLog()` first confirms an invalid zero-flag read, then repeatedly probes with zero bytes to get `NT_STATUS_BUFFER_TOO_SMALL`, reallocates to the server-reported size, reads records backwards/sequentially, and unmarshals user-marshalled `EVENTLOGRECORD` blobs. `test_GetLogInformation()` verifies invalid level handling, then repeats at level 0 using the returned buffer size. `test_BackupLog()` verifies path syntax failure, successful NT object-path backup, name collision on duplicate backup, then opening the backup log.

## State And Persistence Behavior
`test_ReportEventLog()` writes an informational event into the target log. `test_ClearEventLog()` clears the log and is marked `dangerous`. `test_BackupLog()` creates a backup file at `\??\C:\samrtorturetest` and intentionally verifies duplicate-name collision; it is skipped against Samba modes. Handle state is explicit and closed in every normal path, but assertion failures before close may leave handles server-side until the connection is torn down.

## Dependencies And Integration Points
The file depends on generated eventlog NDR structures and the torture RPC framework. It also uses NDR record parsing (`ndr_pull_EVENTLOGRECORD`), `dump_data()`, `NDR_PRINT_DEBUG`, time functions, and Samba parameter settings for server-family skips.

## Risks And Edge Cases
The log name `"dns server"` assumes the target supports that event log. Clearing a real log is destructive. Backup tests can leave files on the server and use Windows-specific NT path semantics. Read-loop logic increments `offset` while also using sequential-read flags, so behavior is tied to server compatibility. `torture_rpc_eventlog()` has a visible typo in the registered test name `"GetLogIntormation"`, which affects test selection names.

## Test Signals
Success is signaled by exact NTSTATUS/WERROR expectations: invalid read parameters, buffer-too-small probes, successful event decode, access denied on flush, successful clear, invalid information level, backup path syntax errors, duplicate backup collision, and successful close operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/eventlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/forest_trust.c -->
# sources/user-network-fs/samba/source4/torture/rpc/forest_trust.c

## Purpose
This file defines the `rpc.lsa.forest.trust` suite. It creates LSA trusted-domain objects, sets and queries forest-trust information, validates trust secrets over Netlogon, and optionally creates reciprocal trusts between two domains when secondary binding and credential options are supplied.

## Important APIs, Types, And Functions
`torture_rpc_lsa_forest_trust()` registers `ForestTrust` on `ndr_table_lsarpc`. `test_get_policy_handle()` uses `lsa_OpenPolicy3` with revision information and checks AES trust-auth support. `test_create_trust_and_set_info()` drives `lsa_CreateTrustedDomainEx2`, `lsa_QueryTrustedDomainInfo`, `test_set_forest_trust_info()`, and `test_query_forest_trust_info()`. `get_trust_domain_passwords_auth_blob()` builds a `trustDomainPasswords` NDR blob. `test_setup_trust()` RC4-encrypts that blob with the RPC session key before creating the trust. `test_validate_trust()` uses Netlogon secure-channel setup, `netr_ServerGetTrustInfo`, and `netr_GetForestTrustInformation`.

## Control Flow
`testcase_ForestTrusts()` generates a random trust password, creates an auth blob, parses a fixed test SID, and creates a dummy forest trust on the primary target. It then queries local DNS policy info, exercises query/set info levels, validates the trust over Netlogon using the generated password, and deletes the dummy trust. If `torture:Forest_Trust_Dom2_Binding` and `torture:Forest_Trust_Dom2_Creds` are present, it connects to the second domain, verifies the domains differ, creates reciprocal trusts, validates both directions, and deletes both trusts.

## State And Persistence Behavior
The test intentionally creates and deletes trusted-domain objects. It sets forest-trust top-level-name and domain-info records, writes trust authentication information, and can install reciprocal forest trusts across two real domains. Cleanup is explicit through `delete_trusted_domain_by_sid()`, but early assertion failures can leave trust objects behind. The password blob contains incoming and outgoing current trust secrets; no previous secret is set.

## Dependencies And Integration Points
Dependencies include LSA, DRS blob definitions for trust-password structures, Netlogon RPC, credential and secure-channel helpers, Samba LSA initializer helpers, GnuTLS ARCFOUR, generated random passwords, SID parsing, and torture settings for primary/secondary bindings. It integrates tightly with Active Directory domain policy and Netlogon credential validation.

## Risks And Edge Cases
This is an invasive administrative test. It requires privileges to create and delete trusts and can change real trust topology. `LSA_TRUST_ATTRIBUTE_FOREST_TRANSITIVE` behavior differs by server functional level, and unsupported encryption-type info can cause early success return in `get_and_set_info()`. The file uses a fixed dummy SID and names, so stale objects from previous failures can affect `check_name()` or creation.

## Test Signals
Signals include `OpenPolicy3` revision and feature checks, exact trusted-domain info fields, absence of forest-trust collision info, expected query/set results for supported info levels, successful decryption and comparison of new/old OWF trust passwords, expected forest trust records from Netlogon, and successful deletion by SID.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/forest_trust.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/frsapi.c -->
# sources/user-network-fs/samba/source4/torture/rpc/frsapi.c

## Purpose
This file implements the `rpc.frsapi` suite for File Replication Service API RPC calls. It checks polling interval get/set behavior, replicated-path classification, forced replication, and informational levels.

## Important APIs, Types, And Functions
`torture_rpc_frsapi()` registers tests on `ndr_table_frsapi`. Helpers wrap `dcerpc_frsapi_GetDsPollingIntervalW_r`, `SetDsPollingIntervalW_r`, and `IsPathReplicated_r`. Top-level tests call `dcerpc_frsapi_ForceReplication_r` and `dcerpc_frsapi_InfoW_r`.

## Control Flow
`test_DsPollingIntervalW()` reads the current intervals, writes them back unchanged, then writes a zeroed long/short interval with the original current interval and finally expects the original values to be returned. `test_IsPathReplicated()` verifies invalid NULL path handling and then probes the server name, `\\server\SYSVOL`, and `C:\windows\sysvol\domain` for replica-set types 0, domain, and DFS. `test_InfoW()` loops levels 0 through 9, sending a pre-sized `frsapi_Info` structure and printing non-zero bytes from the returned blob.

## State And Persistence Behavior
Polling interval tests call the setter and may alter server FRS polling configuration if the server accepts the writes. The intended invariant is that a later read returns the original values, but the sequence still exercises persistent configuration. Force replication can trigger replication activity for the configured DNS domain and partner server.

## Dependencies And Integration Points
The file depends on generated FRSAPI NDR stubs, Samba configuration for `lpcfg_dnsdomain()`, DCE/RPC server-name helpers, WERROR assertions, and the torture RPC harness.

## Risks And Edge Cases
The polling interval sequence assumes server semantics normalize or ignore zero long/short values. Force replication depends on domain membership and FRS availability. `InfoW()` treats the returned blob as printable text and writes directly to stdout, which is a weak structured validation. Servers without FRS or SYSVOL behavior may return implementation-specific errors.

## Test Signals
Signals are WERR success for get/set, exact invalid-service-parameter for NULL path, WERR success across path/type combinations, successful force replication, and success for all ten `InfoW` levels with printable diagnostic blob output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/frsapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/fsrvp.c -->
# sources/user-network-fs/samba/source4/torture/rpc/fsrvp.c

## Purpose
This file defines the `rpc.fsrvp` suite for the File Server Remote VSS Protocol. It validates path support, version/context negotiation, shadow-copy set creation, expose/delete flows, timeout behavior, snapshot SMB I/O, previous-version enumeration, bad IDs, abort behavior, and share security-descriptor cloning.

## Important APIs, Types, And Functions
`torture_rpc_fsrvp()` binds to `ndr_table_FileServerVssAgent`. The central helper `test_fsrvp_sc_create()` sequences `IsPathSupported`, `GetSupportedVersion`, `SetContext`, `StartShadowCopySet`, `AddToShadowCopySet`, `PrepareShadowCopySet`, `CommitShadowCopySet`, `ExposeShadowCopySet`, and `GetShareMapping`, with injected timeout checkpoints from `enum test_fsrvp_inject`. `test_fsrvp_sc_delete()` calls `DeleteShareMapping`. Other tests use SMB2 helpers, `FSCTL_SRV_ENUM_SNAPS`, SRVSVC `NetShareGetInfo/SetInfo`, and security descriptor APIs.

## Control Flow
Basic tests call individual RPCs or create/delete one shadow-copy mapping. Share-I/O tests connect to `fsrvp_share`, write `pre-snap`, create a snapshot, overwrite the base file with `post-snap`, connect to the snapshot share, and confirm the snapshot still reads `pre-snap`. Enumeration tests create one or two snapshots and query snap counts through SMB2 IOCTL. Share-SD testing reads the base share DACL, adds one placeholder ACE before snapshot creation, stops before expose, adds another ACE, exposes the snapshot, restores the original base DACL, and checks the snapshot DACL.

## State And Persistence Behavior
The suite requires a snapshotable share named `fsrvp_share` and creates shadow-copy sets, exposed snapshot shares, files named `testfss.dat`, and temporary DACL modifications. Most created mappings are deleted, but `test_fsrvp_enum_created()` intentionally frees mappings without deletion so enumeration can observe snapshots. Timeout injection may leave incomplete server-side shadow-copy state depending on server cleanup. Share-SD test restores the base share DACL before checking the snapshot.

## Dependencies And Integration Points
Dependencies span generated FSRVP and SRVSVC RPC stubs, SMB2 client APIs, SMB command-line credentials, name resolution, security descriptors/SIDs, HRESULT mapping, and Samba loadparm settings such as `fss:sequence timeout`. The comments document Windows Server requirements for NDR64, signing, domain membership, and an FSRVP-capable share.

## Risks And Edge Cases
The tests are operationally heavy and can leave snapshots, exposed shares, modified ACLs, or test files on failures. Timeout tests sleep for configured sequence timeouts plus a margin, so they can be slow. Enumeration expectations note Windows Server 2012 behavior may not list FSRVP-created snapshots as previous versions. Placeholder ACEs cause the share-SD test to skip if those built-in operator SIDs already exist.

## Test Signals
Signals include zero FSRVP HRESULTs for normal sequences, exact FSRVP/HRESULT errors after injected timeout or bad IDs, snapshot share mapping GUID equality, SMB2 data equality for pre-snapshot content, expected previous-version counts, successful DACL restoration, and both placeholder ACEs appearing in the snapshot share DACL at expose time.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/fsrvp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/handles.c -->
# sources/user-network-fs/samba/source4/torture/rpc/handles.c

## Purpose
This file implements the `rpc.handles` suite for DCE/RPC context-handle behavior. It checks whether LSA, SAMR, and DRSUAPI policy handles are scoped to a connection, shared across an association group, invalid across interfaces, and invalid after closure or association teardown.

## Important APIs, Types, And Functions
`torture_rpc_handles()` registers simple tests for `lsarpc`, `lsarpc-shared`, `samr`, `mixed-shared`, `random-assoc`, and `drsuapi`. Tests use `torture_rpc_connection()`, `torture_rpc_connection_transport()`, `dcerpc_binding_get_assoc_group_id()`, `dcerpc_binding_get_transport()`, LSA `OpenPolicy/QuerySecurity/Close`, SAMR `Connect/Close`, and DRSUAPI `DsBind/DsUnbind`.

## Control Flow
Simple LSA/SAMR/DRSUAPI tests open a handle on one pipe, try to close it on another pipe and expect `NT_STATUS_RPC_SS_CONTEXT_MISMATCH`, close it on the original pipe, then verify a second close faults. Shared LSA tests create additional pipes in the same association group before and after opening a handle, verify the handle works across those pipes, close from one pipe, then verify all others fault. They also test that a handle survives disconnect of the original pipe while other group members remain, but that creating another pipe after all group members are gone fails. Mixed-shared tests verify SAMR handles cannot be consumed through LSARPC even in the same association group, then probe failure for stale or random association IDs.

## State And Persistence Behavior
The file creates transient RPC connections and server-side context handles. It does not persist directory or registry state. Its stateful behavior is association-group lifetime: freeing pipes is part of the test and is followed by short sleeps so the server observes disconnects.

## Dependencies And Integration Points
The suite depends on generated LSA, SAMR, and DRSUAPI NDR clients and the torture RPC transport helper that can force a transport and association group ID. It integrates with low-level RPC runtime behavior rather than high-level service data.

## Risks And Edge Cases
Several expected failures are transport/runtime-specific, especially `NT_STATUS_UNSUCCESSFUL` when reusing expired or random association groups. The shared LSA test has two assertions that compare a stale `status` variable after `QuerySecurity` calls rather than `qsec.out.result`; this could mask a bad result even when the RPC transport status is OK. Timing sleeps are small and may expose races in slow environments.

## Test Signals
Primary signals are exact context-mismatch faults on cross-pipe or double-close attempts, successful shared-handle use within a live association group, `NT_STATUS_UNSUCCESSFUL` for stale/random group connection attempts, and skip behavior for unsupported `OpenPolicy` or `DsBind`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/handles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/initshutdown.c -->
# sources/user-network-fs/samba/source4/torture/rpc/initshutdown.c

## Purpose
This file defines the `rpc.initshutdown` suite for the InitShutdown RPC interface. It tests initiating a system shutdown through both `Init` and `InitEx`, then immediately aborts the pending shutdown.

## Important APIs, Types, And Functions
`torture_rpc_initshutdown()` registers an RPC tcase on `ndr_table_initshutdown`. `init_lsa_StringLarge()` fills shutdown message strings. `test_Init()` calls `dcerpc_initshutdown_Init_r`; `test_InitEx()` calls `dcerpc_initshutdown_InitEx_r`; `test_Abort()` calls `dcerpc_initshutdown_Abort_r`.

## Control Flow
The suite contains two dangerous tests. Each allocates a message string, sets force-applications, timeout 30 seconds, and reboot true, sends the shutdown request, checks transport and WERROR success, and then calls `test_Abort()` with a null server pointer value to cancel it.

## State And Persistence Behavior
This file intentionally schedules a reboot/shutdown on the target host and relies on a follow-up abort to cancel the operation. No persistent Samba data is changed, but the system-level side effect is severe if abort fails, is delayed, or permissions allow shutdown but not abort.

## Dependencies And Integration Points
The file depends on generated InitShutdown NDR stubs and the torture RPC framework. It integrates directly with Windows-compatible remote shutdown service semantics and WERROR result handling.

## Risks And Edge Cases
Both tests are marked `dangerous` for good reason. A target may begin shutdown actions before abort completes. The message initializer only sets the string pointer, not explicit length/size fields, relying on generated marshalling semantics for `lsa_StringLarge`. Running against production hosts is unsafe.

## Test Signals
Signals are NTSTATUS success and WERR success for `Init` or `InitEx`, followed by NTSTATUS and WERR success for `Abort`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/initshutdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool.c -->
# sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool.c

## Purpose
This file defines the main `rpc.iremotewinspool` suite. It tests the MS-RPRN remote Winspool async endpoint, including object UUID requirements, printer open/close, notification registration, driver-package query/delete negative cases, printer enumeration, printer data, driver directory discovery, and raw response equivalence with classic spoolss.

## Important APIs, Types, And Functions
The suite is registered by `torture_rpc_iremotewinspool()`. Fixture setup parses `IREMOTEWINSPOOL_OBJECT_GUID`, sets it on the binding, opens the print server with `AsyncOpenPrinter`, and discovers architecture through shared helpers. Tests call generated `dcerpc_winspool_*` functions such as `AsyncOpenPrinter`, `AsyncClosePrinter`, `SyncRegisterForRemoteNotifications`, `AsyncEnumPrinters`, `AsyncGetPrinterData`, `AsyncCorePrinterDriverInstalled`, `AsyncDeletePrinterDriverPackage`, and `AsyncGetPrinterDriverDirectory`. `test_compare_spoolss()` uses raw DCE/RPC calls to compare async Winspool and spoolss replies.

## Control Flow
The `printserver` and `handles` tcases use a fixture that opens a server handle and closes it during teardown. Individual tests either open additional handles, register and unregister notifications, perform two-phase buffer-size calls, or validate negative HRESULT/WERROR paths. The `protocol` tcase does not use the fixture; it connects with missing, zero, random, valid, and interface UUID object IDs to verify only `IREMOTEWINSPOOL_OBJECT_GUID` works. The raw comparison builds a spoolss `EnumPrinters` request blob and sends it to both endpoints with different opnums.

## State And Persistence Behavior
Most tests are read-only or handle-scoped. Notification registration creates a transient notification handle that is explicitly unregistered. Delete-driver-package tests attempt to delete core driver packages but expect access denied when inputs are valid enough, so they should not remove installed core drivers. Teardown closes the fixture server handle.

## Dependencies And Integration Points
This file depends on generated Winspool and Spoolss NDR stubs, shared iremotewinspool helper functions, registry string decoding, DCE/RPC object UUID binding support, and named-pipe spoolss transport for cross-interface handle comparison. It integrates with printer server configuration and architecture-specific driver data.

## Risks And Edge Cases
Server behavior depends on advertised client build number; the test expects Windows 2000-era clients to be denied on newer servers. Core-driver installed checks assume the XPS core package is present for x64. Raw reply comparison is strict byte-for-byte and can fail on harmless marshalling or padding differences. Some negative package-delete calls touch real driver package identifiers but expect permission denial.

## Test Signals
Signals include successful fixture open, expected access denied for old build numbers, WERR/HRESULT matches for invalid upload/delete inputs, successful enumeration at levels 1/2/4/5 after insufficient-buffer probes, registry type/value checks for `MajorVersion` and `Architecture`, object-UUID unsupported-type failures, and identical raw response blobs for equivalent enum-printer calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_common.c -->
# sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_common.c

## Purpose
This file provides shared helper code for the iremotewinspool test suites. It constructs client-info structures, opens and closes Winspool printer handles, reads printer data values, extracts server architecture, and parses printer driver INF metadata.

## Important APIs, Types, And Functions
`init_winreg_String()` initializes `winreg_String` length fields. `test_get_client_info()` returns a `spoolss_UserLevel1` for selected client OS versions and build numbers. `test_AsyncOpenPrinter_byprinter_expect()` and `test_AsyncOpenPrinter_byprinter()` wrap `dcerpc_winspool_AsyncOpenPrinter_r`. `test_AsyncClosePrinter_byhandle()` wraps close. `test_AsyncGetPrinterData_checktype()` implements the buffer-probe pattern for `AsyncGetPrinterData`; `test_AsyncGetPrinterData_args()` exposes it without an expected type. `test_get_environment()` reads and decodes the `Architecture` REG_SZ value. `parse_inf_driver()` delegates to `driver_inf_parse()`.

## Control Flow
Open-printer helpers build a devmode container and level-1 client-info container, send the RPC, and assert caller-provided NTSTATUS/WERROR expectations. Printer data reads first call with size zero, handle `WERR_MORE_DATA` by allocating the reported buffer, and repeat. Environment extraction wraps that data path and decodes a registry string. INF parsing allocates an `AddDriverInfo8`, invokes the printer-driver parser, emits a targeted diagnostic for internal parser errors, and returns the parsed structure.

## State And Persistence Behavior
The helpers do not persist server state directly except by opening and closing RPC context handles. `parse_inf_driver()` reads local driver package files and returns parsed metadata in talloc-managed memory.

## Dependencies And Integration Points
The file depends on generated Winspool/Spoolss NDR headers, registry data conversion helpers (`pull_reg_sz`), the common header structures, and `lib/printer_driver/printer_driver.h` for `driver_inf_parse()`. It is consumed by both `iremotewinspool.c` and `iremotewinspool_driver.c`.

## Risks And Edge Cases
`test_get_client_info()` has discrete OS branches; unrecognized enum values leave `build` unset. The printer-data helper only allocates a second buffer when the server returns `WERR_MORE_DATA`, so unusual servers that return success with zero size need callers to handle that. INF parsing depends on correct torture options and architecture strings; wrong driver names surface as parser internal errors.

## Test Signals
Signals are exact open-printer status/result matches, WERR success for close and data reads, REG_SZ architecture decoding, REG_DWORD/REG_SZ type validation by callers, and successful INF parsing into `spoolss_AddDriverInfo8`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_common.h -->
# sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_common.h

## Purpose
This header declares shared data structures and helper APIs used by the iremotewinspool RPC tests and driver-install tests. It centralizes print-driver state, suite fixture context, client OS version identifiers, and helper prototypes.

## Important APIs, Types, And Functions
`REG_DRIVER_CONTROL_KEY` names the registry subtree used to validate installed printer drivers. `struct test_driver_info` tracks SMB connection state, parsed `spoolss_AddDriverInfo8`, local driver path metadata, server/share names, upload GUID directory, uploaded INF path, driver name, architecture, and optional core-driver INF. `struct test_iremotewinspool_context` holds the required object UUID, iremotewinspool pipe, server handle, driver info, and discovered environment. The header declares open/close printer helpers, environment lookup, printer-data reads, Winreg string initialization, client-info construction, and INF parsing.

## Control Flow
The header has no executable flow, but it defines the fixture contract: setup code fills `test_iremotewinspool_context`, optional driver setup attaches `test_driver_info`, tests reuse the open server handle and environment, and teardown consumes the same fields for cleanup.

## State And Persistence Behavior
The structures model both transient RPC handle state and persistent server artifacts created by driver tests, including files copied to `print$`, uploaded driver packages, installed driver registry keys, and driver-store INF paths. The fields are talloc-owned by the test context in the implementation files.

## Dependencies And Integration Points
The header includes the torture RPC harness and relies on generated types from Winspool/Spoolss/Winreg headers included by implementation files. It is the integration boundary between the generic iremotewinspool protocol tests, the shared helpers, and the driver package tests.

## Risks And Edge Cases
Because `test_driver_info` stores cleanup-critical paths like `print_upload_guid_dir` and `uploaded_inf_path`, setup failures can leave teardown with partially populated state. Callers need to ensure fields are initialized before driver cleanup is attempted. The OS-version enum only supports the build values encoded in the common implementation.

## Test Signals
The header itself has no runtime assertions. Its quality signal is compile-time agreement among the three iremotewinspool source files and correct propagation of shared handles, environment strings, and driver metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_driver.c -->
# sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_driver.c

## Purpose
This file defines the `rpc.iremotewinspool_driver` suite for uploading, installing, validating, and cleaning up printer driver packages through iremotewinspool. It combines local INF parsing, SMB copy to `print$`, Winspool package RPCs, and Winreg validation.

## Important APIs, Types, And Functions
`torture_rpc_iremotewinspool_drv()` registers a fixture-backed `drivers` tcase. Setup helpers collect required torture options (`driver_path`, `inf_file`, `driver_name`, `driver_arch`, optional `core_driver_inf`), parse the INF into `spoolss_AddDriverInfo8`, open iremotewinspool, discover environment, create a random upload GUID directory, and connect to `print$` over SMB1. `test_CopyDriverFiles()` walks the local driver tree with `tftw()` and copies files through SMB. `test_UploadPrinterDriverPackage()`, `test_InstallPrinterDriverFromPackage()`, and `test_ValidatePrinterDriverInstalled()` drive the main workflow. Teardown deletes the upload directory, exits the SMB session, uninstalls the driver, removes the package, and closes the printer handle.

## Control Flow
The intended sequence is: fixture setup, copy local package into `\\server\print$\{GUID}`, call `AsyncUploadPrinterDriverPackage` with `UPDP_UPLOAD_ALWAYS`, store the returned destination INF path, call `AsyncInstallPrinterDriverFromPackage` with parsed driver name/environment and `IPDFP_COPY_ALL_FILES`, then connect to Winreg over `ncacn_np` and verify the installed driver key has an `InfPath` matching the upload result.

## State And Persistence Behavior
This suite is highly stateful. It creates directories and files on the remote `print$` share, uploads a driver package into the driver store, installs a printer driver, writes/observes registry entries under `SYSTEM\CurrentControlSet\Control\Print`, and removes those artifacts in teardown. Cleanup is best-effort: teardown calls uninstall and package removal regardless of test failures, but partially initialized fields or failed uploads can make cleanup incomplete.

## Dependencies And Integration Points
Dependencies include generated Winspool, Spoolss, and Winreg stubs; SMB client APIs; raw SMB session exit; registry conversion helpers; local filesystem walking; printer-driver INF parsing; command-line credentials; loadparm resolver/socket/gensec settings; and common iremotewinspool helpers.

## Risks And Edge Cases
Running this against a real print server can install or remove printer drivers. SMB1 is required on Windows for the `print$` connection path. The architecture option validation appears inverted: it sets `valid = true` when `strequal(*p, driver_arch) == 0`, which looks like it may accept non-matching entries rather than the matching one depending on Samba `strequal()` semantics. Teardown assumes `dinfo`, SMB connection, upload directory, and uploaded INF path are valid, so setup failures can produce cleanup hazards.

## Test Signals
Signals include successful option collection, INF class containing `PRINTER_DRIVER_CLASS`, successful SMB tree copy, HRESULT success for upload/install/remove package, WERR success for uninstall, successful Winreg key open, and case-insensitive equality between registry `InfPath` and the uploaded INF path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/join.c -->
# sources/user-network-fs/samba/source4/torture/rpc/join.c

## Purpose
This file implements `torture_rpc_join()`, a helper-style RPC torture test for joining a domain with temporary machine accounts and verifying those credentials can connect to `IPC$`.

## Important APIs, Types, And Functions
The function uses `torture_join_domain()` and `torture_leave_domain()` to create and remove test accounts named `smbtorturejoin`. It uses `smbcli_full_connection()` to connect to the target host's `IPC$` share with the generated machine credentials. It reads the target host from the `host` torture setting and obtains SMB client/session options from loadparm.

## Control Flow
The test first joins as a member workstation using `ACB_WSTRUST`, connects to `IPC$`, disconnects, and leaves the domain. It then repeats the flow as a domain-controller-style trust account using `ACB_SVRTRUST`. Any join or IPC connection failure returns false.

## State And Persistence Behavior
The function creates domain machine accounts and removes them after each phase. If the IPC connection fails after a successful join, the code returns false before calling `torture_leave_domain()`, so stale `smbtorturejoin` accounts may remain. Successful paths disconnect the SMB tree and leave the domain.

## Dependencies And Integration Points
Dependencies include Samba torture domain-join helpers, credential generation, SMB client connection APIs, name resolution, socket options, session options, event loop, and gensec settings. It integrates with directory/account management and IPC$ authentication paths.

## Risks And Edge Cases
The fixed NetBIOS name can collide with stale accounts or parallel test runs. Cleanup is not protected by a common failure path, so connection failures after join leak domain state. The debug message for the second phase still says workstation credentials, although the account type is server trust.

## Test Signals
Success requires both account types to join, authenticate to `IPC$`, disconnect, and leave the domain. Failure signals are null `test_join` returns or non-OK `smbcli_full_connection()` statuses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/join.c -->
