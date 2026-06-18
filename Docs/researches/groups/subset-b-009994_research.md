# Research: subset-b-009994

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/spoolss_access.c -->
# sources/user-network-fs/samba/source4/torture/rpc/spoolss_access.c

## Purpose

`spoolss_access.c` is a Samba torture suite for print spooler access-control behavior. It creates several temporary domain users, gives selected users built-in group memberships, privileges, or explicit printer security descriptor ACEs, then verifies which `spoolss_OpenPrinterEx` access masks succeed against print-server and printer handles.

## Important APIs, Types, and Functions

The local state types are `struct torture_user`, which describes the test identity and expected rights, and `struct torture_access_context`, which carries the spoolss pipe, selected printer name, original printer security descriptor, and created user handle. `test_openprinter_handle()` and `test_openprinter_access()` wrap `spoolss_OpenPrinterEx` and optional `ClosePrinter`. Setup helpers include `spoolss_access_setup_membership()` for SAMR BUILTIN alias membership, `spoolss_access_setup_privs()` for LSA account rights, `spoolss_access_setup_sd()` for printer DACL mutation, and `test_EnumPrinters_findone()` for selecting a printer. The exported suite factory is `torture_rpc_spoolss_access()`.

## Control Flow

Each fixture allocates a `torture_access_context`, fills the user profile, and calls `torture_rpc_spoolss_access_setup_common()`. The common setup creates a SAMR test user, builds credentials, optionally adds group membership or LSA rights, connects to spoolss as an administrator to find a printer, optionally adds printer ACEs, then reconnects to spoolss as the new user. `test_openprinter()` iterates a fixed table of server and printer access masks and compares results with expectations derived from `admin_rights` and `system_security`. Teardown deletes the test user and restores the original printer security descriptor for the security-descriptor fixture.

## State and Persistence Behavior

The suite mutates the test domain by creating accounts named `torture_user*`, changing BUILTIN alias memberships, and adding account rights. The `normaluser_sd` fixture also mutates a real printer DACL and preserves `sd_orig` for restoration. Membership and privilege cleanup are explicitly left as comments, so user deletion is the main cleanup mechanism for those changes. If teardown is interrupted after DACL mutation, printer permissions may remain changed until restored manually.

## Dependencies and Integration Points

The file depends on generated spoolss, SAMR, LSA, and security NDR client stubs; `torture_rpc_connection()`, test user helpers from `testjoin.c`, spoolss helper routines such as `test_GetPrinter_level()` and `test_ClosePrinter()`, Samba credentials/loadparm state, and domain policy supporting SAMR account creation.

## Risks and Edge Cases

Tests depend on at least one enumerable local printer and on server support for the relevant privileges. The XPS printer is skipped only when multiple printers exist, so printer selection can affect results. The privilege setup path treats missing privileges as a skip signal rather than a hard failure. Teardown restores printer security only when `printername` is present, and handle close coverage is best effort. The expected access matrix encodes Windows/Samba behavior and is sensitive to ACL inheritance, administrator mapping, and print operator privilege semantics.

## Test Signals

Strong signals are successful `normaluser`, `adminuser`, `printopuser`, `printopuserpriv`, `normaluser_sd`, and machine-workstation `openprinter` cases. Failures isolate to SAMR user creation, LSA right assignment, printer enumeration, printer DACL restore, or individual `OpenPrinterEx` access-mask expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/spoolss_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/spoolss_notify.c -->
# sources/user-network-fs/samba/source4/torture/rpc/spoolss_notify.c

## Purpose

`spoolss_notify.c` tests spoolss printer change-notification callback behavior. It starts an in-process DCE/RPC callback server that implements a minimal spoolss endpoint, subscribes to remote printer change notifications, records callback packets, and verifies the server sends expected `ReplyOpenPrinter` and `ReplyClosePrinter` calls.

## Important APIs, Types, and Functions

The callback server is represented by `notify_test_spoolss_interface` and callback table `srv_cb`. Server hooks include `spoolss__op_ndr_pull()`, `spoolss__op_dispatch()`, `spoolss__op_ndr_push()`, `spoolss__op_init_server()`, and interface lookup functions by UUID/name. Stub implementations `_spoolss_ReplyOpenPrinter()`, `_spoolss_ReplyClosePrinter()`, and `_spoolss_RouterReplyPrinterEx()` return successful callback responses. `struct received_packet` and the global `received_packets` list retain observed callback opnums and decoded requests. Client-side helpers cover `OpenPrinter`, `RemoteFindFirstPrinterChangeNotifyEx`, and `RouterRefreshPrinterChangeNotify`.

## Control Flow

`test_RFFPCNEx()` clears any stale packet list, starts a local SMB/DCE/RPC server via `test_start_dcerpc_server()`, opens the remote print server, subscribes using `RemoteFindFirstPrinterChangeNotifyEx()` with a print-server notify option, asserts a `NDR_SPOOLSS_REPLYOPENPRINTER` callback arrived, refreshes notifications twice, closes the printer, and asserts the last callback is `NDR_SPOOLSS_REPLYCLOSEPRINTER`. `test_ReplyOpenPrinter()` directly calls the server implementation path and then closes the returned handle; it skips Samba 3 because it is testing Samba 4 server internals.

## State and Persistence Behavior

The test starts local listener state, registers a DCE/RPC endpoint server, and temporarily changes the loadparm setting `dcerpc endpoint servers` to `spoolss`. It does not intentionally persist remote printer state. Callback packets are allocated under the NULL talloc context so they survive request contexts, then are freed by `free_received_packets()`. If the process aborts before cleanup, only process-local listener and memory state are lost.

## Dependencies and Integration Points

The file integrates client spoolss stubs with the Samba DCE/RPC server runtime, SMB server socket setup, process model initialization, endpoint registration, interface discovery, NTVFS initialization, network interface selection, and generated spoolss NDR tables.

## Risks and Edge Cases

The test relies on a usable local IPv4 interface and on the remote spooler being able to connect back to the worker's callback address. Firewalls, NAT, interface ordering, or binding restrictions can cause false failures. `received_packets` is a global list and assumes single-threaded test execution. The callback dispatch hard-codes opnums 58, 60, and 66, so IDL changes or alternate protocol versions would break it. Several richer printer-level notification paths are compiled out.

## Test Signals

Passing `testRFFPCNEx` proves callback endpoint registration, remote subscription, callback NDR decoding, and close notification all work together. Passing `testReplyOpenPrinter` verifies the server-side reply calls return handles and close cleanly on Samba 4.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/spoolss_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/spoolss_win.c -->
# sources/user-network-fs/samba/source4/torture/rpc/spoolss_win.c

## Purpose

`spoolss_win.c` reproduces a Windows XP-style sequence of spoolss RPCs. It validates printer/server open patterns, buffer retry behavior, printer data queries, printer enumeration, job/form/driver/key enumeration, and handle close ordering as observed from Windows clients.

## Important APIs, Types, and Functions

`struct test_spoolss_win_context` holds enumeration results, the current `GetPrinter` output, printer keys, and whether the selected printer has a driver. `test_OpenPrinterEx()` and `test_OpenPrinterAsAdmin()` centralize `OpenPrinterEx` calls. Data and enumeration helpers include `test_GetPrinterData()`, `test_EnumPrinters()`, `test_GetPrinter()`, `test_EnumJobs()`, `test_GetPrinterDriver2()`, `test_EnumForms()`, `test_EnumPrinterKey()`, and `test_EnumPrinterDataEx()`. The single scenario is `test_WinXP()`, registered by `torture_rpc_spoolss_win()`.

## Control Flow

`test_WinXP()` opens the print server with an XP-like read/admin/execute sequence, validates selected server printer-data values, enumerates printers with initial and retry buffers, and skips printer-specific checks when no printer exists. When a printer is present, it opens multiple handles with different access masks, calls `GetPrinter` at levels 0, 2, and 7 with varying offered sizes, checks `EnumJobs`, optional driver lookup, forms, printer registry keys, and data under each key. The test intentionally interleaves open and close calls to mirror real client behavior.

## State and Persistence Behavior

The test is designed to be non-mutating. It opens and closes spoolss handles and queries server/printer state, but it does not set printer data or modify jobs. State is held in talloc contexts and policy handles. A failure before later close calls may leak remote handles until the server connection is torn down.

## Dependencies and Integration Points

The file depends on generated spoolss client stubs, common torture RPC registration, `test_ClosePrinter()`, Samba loadparm context, `dcerpc_server_name()`, and server printer/driver configuration. It uses registry-like spoolss key/data APIs and Windows NT x86 driver architecture strings.

## Risks and Edge Cases

Behavior is intentionally tied to Windows XP traces, so modern Windows or Samba behavior can diverge. The suite tolerates absent printers by skipping deep checks, which reduces coverage in minimal environments. `GetPrinterDriver2` is only required to succeed when `GetPrinter` level 2 reports a driver name. Printer key enumeration stores pointers into returned NDR buffers, so context lifetime matters. Several hard-coded expected values, such as `MajorVersion == 3`, `W3SvcInstalled == 0`, and error codes for `UISingleJobStatusString`, are compatibility assumptions.

## Test Signals

The strongest signal is `testWinXP` completing against a configured print server with at least one printer. Useful sub-signals are correct insufficient-buffer retries, stable printer name round-trips, key/data enumeration, and clean close behavior across many handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/spoolss_win.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/srvsvc.c -->
# sources/user-network-fs/samba/source4/torture/rpc/srvsvc.c

## Purpose

`srvsvc.c` is the Samba torture suite for the Server Service RPC interface. It validates character-device, queue, connection, file, session, share, server, disk, transport, remote time-of-day, and name-validation operations under administrative and anonymous credentials.

## Important APIs, Types, and Functions

The file consists of focused test helpers for each SRVSVC family: `test_NetCharDevEnum/GetInfo/Control`, `test_NetCharDevQEnum/GetInfo`, `test_NetConnEnum`, `test_NetFileEnum`, `test_NetSessEnum`, `test_NetShareGetInfo`, `test_NetShareAddSetDel`, `test_NetShareEnumAll`, `test_NetShareEnum`, `test_NetSrvGetInfo`, `test_NetDiskEnum`, `test_NetTransportEnum`, `test_NetRemoteTOD`, and `test_NetNameValidate`. The suite factory `torture_rpc_srvsvc()` creates one authenticated admin tcase and one anonymous tcase.

## Control Flow

Enumeration functions build the appropriate info-control union for each level, call the generated `dcerpc_srvsvc_*_r()` request, and either assert exact expected errors or log non-fatal unexpected results depending on historical tolerance. Share enumeration tests compare anonymous versus admin expectations and, for level 2 results, drill into each returned share through `NetShareGetInfo` and `NetShareCheck`. `test_NetShareAddSetDel()` creates a temporary `testshare`, applies multiple `NetShareSetInfo` levels, reads back level 502 details, checks fields, and deletes the share. `test_NetNameValidate()` probes accepted maximum lengths and invalid ASCII characters for name types 1 through 13 under two flag values.

## State and Persistence Behavior

Most tests are read-only enumerations. `test_NetShareAddSetDel()` mutates server share configuration by adding, changing, and deleting `testshare`; it is marked `dangerous`. If deletion fails, the test share can remain configured. Name validation allocates temporary strings only. Resume handles are local variables and are not persisted.

## Dependencies and Integration Points

The file depends on generated `ndr_srvsvc_c.h` client stubs, `torture_rpc.h` testcase helpers, server name binding through `dcerpc_server_name()`, and server-side share/session/file state. Anonymous access tests depend on the torture framework's anonymous RPC tcase setup.

## Risks and Edge Cases

Some SRVSVC calls are obsolete or may be unimplemented on a target server. The test often logs non-OK WERRORs rather than failing for enumeration families, so it is better at compatibility smoke coverage than strict conformance for those calls. `test_NetShareAddSetDel()` uses a Windows path `C:\` and assumes permissions allow share mutation. The final delete assertion mistakenly checks `a.out.result` instead of `d.out.result`, which can mask a failed delete result after a successful add.

## Test Signals

Passing admin tests show broad SRVSVC availability, share information access, share mutation support, and name validation behavior. Passing anonymous tests verify expected access-denial boundaries for level 2/501/502 share data while allowing low-detail share enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/srvsvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/svcctl.c -->
# sources/user-network-fs/samba/source4/torture/rpc/svcctl.c

## Purpose

`svcctl.c` tests the Service Control Manager RPC interface against the default `Spooler` service. It covers manager and service handle lifecycle, service status/configuration queries, service security descriptor get/set, control paths, dependent-service enumeration, and a no-op configuration update.

## Important APIs, Types, and Functions

`TORTURE_DEFAULT_SERVICE` is `Spooler`. Common wrappers are `test_OpenSCManager()`, `test_OpenService()`, and `test_CloseServiceHandle()`. Query tests include `test_QueryServiceStatus()`, `test_QueryServiceStatusEx()`, `test_QueryServiceConfigW()`, `test_QueryServiceConfig2W()`, `test_QueryServiceConfigEx()`, `test_QueryServiceObjectSecurity()`, `test_EnumServicesStatus()`, and `test_EnumDependentServicesW()`. Mutating or control-shaped tests include `test_SetServiceObjectSecurity()`, `test_StartServiceW()`, `test_ControlService()`, `test_ControlServiceExW()`, and `test_ChangeServiceConfigW()`.

## Control Flow

Almost every test opens the SCM with maximum allowed access, opens `Spooler`, performs one operation, then closes service and manager handles. Buffer-sized APIs first call with zero or undersized buffers and retry on `WERR_INSUFFICIENT_BUFFER` or `WERR_MORE_DATA`. Security descriptor tests query DACL bytes and parse them with `ndr_pull_security_descriptor`; the setter writes back the same DACL. `ChangeServiceConfigW` queries the current config and then calls `ChangeServiceConfigW` with the existing type/start/error fields and NULL optional fields, checking that NULL means preserve current values.

## State and Persistence Behavior

The suite is mostly read-only, but it does call setter/control APIs. `SetServiceObjectSecurity` writes back the exact queried DACL. `ChangeServiceConfigW` performs a no-op configuration write. `StartServiceW` expects `WERR_SERVICE_ALREADY_RUNNING`, and `ControlService`/`ControlServiceExW` deliberately use invalid controls or parameters to avoid stopping the service. Remote service state can still be touched in audit logs and permissions must allow these calls.

## Dependencies and Integration Points

The file uses generated `ndr_svcctl` client stubs, generated security NDR parsing, common torture RPC helpers, and a target exposing the SCM named pipe endpoint with a `Spooler` service. It also depends on Windows/Samba SCM error-code compatibility.

## Risks and Edge Cases

The hard-coded `Spooler` service may be disabled, absent, or protected. Setter calls require sufficient rights and may fail under restricted credentials. The code allocates raw buffers for NDR-packed service arrays and manually pulls `ENUM_SERVICE_STATUSW`; buffer length and returned count must stay consistent. Tests encode expected quirks such as only `QueryServiceConfigEx` level 8 succeeding and `ControlServiceExW` returning `WERR_INVALID_PARAMETER`.

## Test Signals

Passing tests indicate SCM open/close correctness, query buffer retry behavior, DACL retrieval/parsing, no-op DACL/config writes, expected invalid-control errors, and service enumeration decoding. Failures usually point to endpoint availability, access rights, service policy, or IDL marshalling issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/svcctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/testjoin.c -->
# sources/user-network-fs/samba/source4/torture/rpc/testjoin.c

## Purpose

`testjoin.c` provides shared torture infrastructure for creating and deleting domain users or machine accounts used by RPC tests. It wraps SAMR and libnet domain join flows, creates credentials for temporary accounts, exposes account metadata, and provides privilege assignment helpers.

## Important APIs, Types, and Functions

`struct test_join` stores the SAMR pipe, user/domain policy handles, libnet join result, domain SID/names, user SID/GUID, and NetBIOS name. `torture_create_testuser_max_pwlen()` creates a normal or special SAMR account with a generated password, while `torture_create_testuser()` uses a 255-character maximum. `torture_join_domain()` creates a machine trust account through libnet and returns machine credentials. `torture_leave_domain()` deletes the account and, for AD DC joins, calls `torture_leave_ads_domain()` to remove server objects. `torture_setup_privs()` adds LSA rights to a SID. Accessors return the SAMR pipe, user policy handle, SIDs, GUID, and domain names.

## Control Flow

User creation connects to SAMR, locates the requested domain or enumerates domains to find the non-BUILTIN domain, opens it, creates or replaces the user, computes the user SID, queries password policy, generates a compliant password, encrypts it with the transport session key, and sets user info levels 24 and 21. Machine joins parse the binding, normalize transport to named pipes where appropriate, call `libnet_JoinDomain()` with `recreate_account = true`, copy output account/domain data into `test_join`, annotate the account through SAMR, and build `cli_credentials` with secure channel type based on account flags.

## State and Persistence Behavior

This file deliberately mutates domain state. It creates accounts, deletes pre-existing accounts with the same requested name, sets passwords and account flags, assigns descriptive fields, grants LSA rights, and deletes accounts during leave. If account creation fails partway, the failure path calls `torture_leave_domain()`. If the process exits before leave, accounts, rights, or AD server objects can remain.

## Dependencies and Integration Points

The file integrates generated SAMR and LSA stubs, libnet join APIs, Samba command-line credentials/loadparm, `init_samr_CryptPassword()`, transport session keys, LDB/LDAP cleanup for AD server objects, and security SID helpers. It is declared through `torture_rpc.h` and consumed by many RPC torture suites.

## Risks and Edge Cases

The helpers require powerful credentials and a working SAMR/LDAP path. `DeleteUser_byname()` deletes any existing object with the requested test name before retrying creation, so names must remain tightly scoped. Password generation depends on policy minimum length and the caller's maximum. `torture_leave_domain()` assumes `join->user_handle` is valid and logs but does not propagate delete failures. LSA rights added by `torture_setup_privs()` are not independently removed except through account deletion.

## Test Signals

Success is visible when downstream suites can authenticate with returned credentials, retrieve the expected SID/GUID/domain names, use the SAMR pipe and user handle, and cleanly delete accounts. Failure signals isolate to SAMR connect/open/create/set-info, session-key extraction, libnet join, LDAP cleanup, or insufficient privileges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/testjoin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/torture_rpc.h -->
# sources/user-network-fs/samba/source4/torture/rpc/torture_rpc.h

## Purpose

`torture_rpc.h` is the shared public header for Samba source4 RPC torture suites. It defines the RPC testcase wrapper types and declares helpers for opening RPC connections, creating domain joins, adding RPC tests to suites, and initializing authenticated, anonymous, or machine-account testcases.

## Important APIs, Types, and Functions

`struct torture_rpc_tcase` embeds `struct torture_tcase` and adds the target NDR interface table, optional machine name, and optional setup/teardown callbacks that receive the DCE/RPC pipe. `struct torture_rpc_tcase_data` carries the joined account context, pipe, and credentials used by testcase setup. Connection declarations are `torture_rpc_connection()` and `torture_rpc_connection_with_binding()`. Domain helpers include `torture_join_domain()`, `torture_join_sid()`, and `torture_leave_domain()`. Suite builders include `torture_suite_add_rpc_iface_tcase()`, `torture_suite_add_rpc_setup_tcase()`, anonymous and machine variants, plus test registration helpers for plain pipe tests, join-aware tests, setup-data tests, arbitrary userdata tests, and credential-aware tests.

## Control Flow

The header has no runtime control flow. At compile time, individual RPC torture files include it to register tests against generated NDR interface tables. At runtime, implementations behind these declarations open DCE/RPC pipes before test functions run and invoke optional setup/teardown wrappers around each testcase.

## State and Persistence Behavior

The declared API can create persistent remote state indirectly through domain join helpers and machine-account testcases. The header's data structs hold per-testcase pipe and credential state, but ownership and cleanup are implemented elsewhere. The machine testcase helpers imply lifecycle management of temporary trust accounts.

## Dependencies and Integration Points

It includes the core torture framework, credentials, DRSUAPI torture declarations, libnet join types, DCE/RPC binding types, raw CLI types, spoolss NDR types, and generated `torture/rpc/proto.h`. It is the integration contract between suite source files and common RPC torture infrastructure.

## Risks and Edge Cases

Because this header is a broad coupling point, signature drift affects many suites. Function pointer signatures are strict; mismatching a test helper with the wrong registration function can compile with casts in some callers but fail at runtime. The header exposes only forward-declared join state for some helpers, so consumers rely on accessor functions and must not assume layout.

## Test Signals

Compile success across RPC torture suites is the main signal for this header. Runtime signals come from suites successfully creating authenticated, anonymous, BDC, workstation, setup-data, and credential-aware testcases through the declared helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/torture_rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/unixinfo.c -->
# sources/user-network-fs/samba/source4/torture/rpc/unixinfo.c

## Purpose

`unixinfo.c` is a compact torture suite for the `unixinfo` RPC interface. It tests SID to UID/GID mapping, UID/GID to SID mapping, and batched password-entry lookup by UID.

## Important APIs, Types, and Functions

The suite contains five direct test functions: `test_sidtouid()`, `test_uidtosid()`, `test_getpwuid()`, `test_sidtogid()`, and `test_gidtosid()`. It uses generated request structs `unixinfo_SidToUid`, `unixinfo_UidToSid`, `unixinfo_GetPWUid`, `unixinfo_SidToGid`, and `unixinfo_GidToSid`. `torture_rpc_unixinfo()` registers all tests against `ndr_table_unixinfo`.

## Control Flow

Each test fills one generated request, calls the corresponding `dcerpc_unixinfo_*_r()` function on the pipe binding handle, and asserts transport success. SID-to-ID tests use a synthetic BUILTIN-derived SID and accept `NT_STATUS_NONE_MAPPED` as a valid semantic result. ID-to-SID tests query UID and GID 1000 and require semantic success. `GetPWUid` builds an array of 512 UIDs from 0 to 511 and expects the batched lookup to succeed.

## State and Persistence Behavior

The suite is read-only. It does not create users, groups, or mappings. All state is request-local, allocated under the torture context, and discarded when the test context is freed.

## Dependencies and Integration Points

The file depends on `torture_rpc.h`, generated unixinfo client stubs, and SID parsing helpers from `libcli/security/security.h`. Its behavior depends on the target server's Unix identity mapping backend and NSS/passdb configuration.

## Risks and Edge Cases

UID/GID 1000 may not exist or may not map on all systems, so strict success for `UidToSid` and `GidToSid` can be environment-sensitive. The synthetic SID may or may not map, and the test correctly tolerates `NONE_MAPPED`. The 512-element `GetPWUid` request exercises bulk marshalling but assumes the server can handle that count.

## Test Signals

Passing tests indicate the unixinfo endpoint is reachable, basic SID/ID conversion paths work, and batched UID lookup marshals and returns successfully. Failures usually point to endpoint exposure, idmap configuration, NSS backend behavior, or generated NDR marshalling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/unixinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/winreg.c -->
# sources/user-network-fs/samba/source4/torture/rpc/winreg.c

## Purpose

`winreg.c` is a broad torture suite for the Windows Remote Registry RPC interface. It tests hive opening, version reporting, key create/open/delete/flush/query/enumeration, value set/query/delete/enumeration, multiple-value query variants, security descriptor operations, volatile key semantics, well-known HKLM values, and dangerous shutdown RPCs.

## Important APIs, Types, and Functions

Constants define test keys and values under `winreg_torture_test`. Utility initializers build `lsa_StringLarge` and `winreg_String` length fields. Core wrappers include `test_CreateKey_opts()`, `test_OpenKey_opts()`, `test_CloseKey()`, `test_FlushKey()`, `test_DeleteKey_opts()`, `test_QueryInfoKey()`, `test_SetValue()`, `test_DeleteValue()`, and `test_OpenHive()`. Security helpers serialize and parse descriptors through `GetKeySecurity` and `SetKeySecurity`, then test DACL/SACL/owner/group presence, inheritance, blocked inheritance, and `SECINFO_*` masks. Value helpers cover standard types, unusual value names, extended registry types, `QueryValue`, `QueryMultipleValues`, `QueryMultipleValues2`, and `EnumValue`. `test_Open()` orchestrates per-hive coverage, and `torture_rpc_winreg()` registers HKLM, HKU, HKCR, HKCU, plus dangerous shutdown tests.

## Control Flow

`test_Open()` opens a hive through a function pointer, calls `GetVersion`, maps the hive to a base test key, optionally validates HKLM well-known `CurrentVersion` values, runs `test_key_base()` to create and delete temporary keys/values, skips currently disabled security-descriptor base tests, and optionally recurses through existing keys to a limited depth. `test_key_base()` cleans old test keys, creates nested keys, runs value and key-name tests, flushes, verifies deletion, and cleans up. Query helpers deliberately exercise invalid-parameter, missing-value, too-small-buffer, and successful retry paths. Shutdown tests initiate and then abort a system shutdown and are marked dangerous.

## State and Persistence Behavior

This suite intentionally mutates the remote registry by creating and deleting test keys and values under HKCU, HKU, HKCR, and `HKLM\SOFTWARE\Samba\winreg_torture_test`. It writes random binary data and multiple registry types, flushes keys, and may write security descriptors in helper paths, though the high-level security descriptor test is currently skipped. Volatile key and symlink key tests are skipped for Samba or globally disabled in relevant paths. If cleanup fails or a dangerous shutdown test is run, persistent registry keys or a pending shutdown can affect the target; the shutdown tests call `AbortSystemShutdown` afterward.

## Dependencies and Integration Points

The file integrates generated winreg client stubs, generated security NDR, Samba registry helpers such as `push_reg_sz`, `push_reg_multi_sz`, and `str_regtype`, SID/security descriptor helpers, common RPC torture registration, and target registry service policy. It uses `test_winreg_QueryValue()` from shared torture helpers.

## Risks and Edge Cases

The file contains several deliberately skipped or disabled paths: symlink keys, key security descriptor high-level tests, and some multiple-value cases known to crash Windows 2008 remote registry. Registry semantics vary heavily by hive, privilege, Samba version, and Windows version. Some cleanup is best effort, and there is a likely typo in `test_key_base_sd()` deleting `test_key4` twice instead of deleting `test_key2`. Dangerous shutdown tests require careful opt-in. Recursive enumeration is capped by `MAX_DEPTH` but HKCR fanout is still large, so the suite special-cases it.

## Test Signals

Passing HKLM/HKU/HKCR/HKCU tests show the remote registry endpoint can open hives, create/delete keys, round-trip values across many types and names, enumerate keys and values, query well-known values, and handle expected error paths. Passing dangerous tests show shutdown RPCs and abort behavior work, but they should only run in disposable environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/winreg.c -->
