# subset-b-009995 Research

Grouped research for Samba source4 torture files. Each section preserves the source path and is bounded for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/witness.c -->
# sources/user-network-fs/samba/source4/torture/rpc/witness.c

## Purpose
`witness.c` registers the `rpc.witness` smbtorture suite for exercising the SMB Witness RPC interface. It validates witness interface discovery, version and parameter handling for registration APIs, handle invalidation after unregister, cluster-resource driven async notifications, and server-side timeout behavior. The tests are integration-heavy: meaningful success requires a witness-capable clustered/SOFS environment plus RPC access to srvsvc and clusapi.

## Important APIs, Types, And Functions
The central state carrier is `struct torture_test_witness_state`, which caches `net_name`, discovered `share_name`, the `witness_interfaceList`, the active witness `policy_handle`, and a nested clusapi pipe. `test_witness_GetInterfaceList()` calls `dcerpc_witness_GetInterfaceList_r()` and stores the returned interfaces. `find_sofs_share()` uses srvsvc `NetShareEnumAll` to select a `STYPE_CLUSTER_SOFS` share, falling back to a disk share. `init_witness_test_state()` lazily fills shared state from torture settings, interface enumeration, and share enumeration. `test_witness_Register()` and `test_witness_RegisterEx()` run invalid-version and invalid-parameter matrices before performing valid registration against each witness-capable available interface. `test_witness_UnRegister_with_handle()` verifies that a context handle cannot be reused after successful unregister. `setup_clusapi_connection()`, `test_GetResourceState_int()`, and `toggle_cluster_resource_state()` drive cluster resource state changes over sealed `ncacn_ip_tcp` clusapi. `test_witness_AsyncNotify()` waits for resource-change notifications after toggling a resource. `test_witness_AsyncNotify_timeouts()` registers with multiple timeout values and expects `WERR_TIMEOUT`. `torture_rpc_witness()` wires these tests into an RPC interface tcase for `ndr_table_witness`.

## Control Flow
Suite initialization creates one shared `torture_test_witness_state` under the RPC tcase. Most tests first obtain a witness pipe from the torture RPC framework. Discovery starts with `GetInterfaceList`; valid registration loops then filter interfaces through `check_valid_interface()` and extract IPv4 or IPv6 strings through `get_ip_address_from_interface()`. Register/RegisterEx first assert expected failures for unsupported versions and missing names, then use the discovered net name and interface address to register and immediately unregister. Async notification tests initialize witness and clusapi state, register a witness context, submit an async notify request, toggle the cluster resource named by `state->net_name`, poll tevent until the reply arrives, validate one resource-change message, unregister, and toggle the cluster resource back. Timeout tests use RegisterEx with a timeout field, temporarily set the binding timeout to `UINT_MAX`, call the synchronous AsyncNotify RPC, and expect a witness-level timeout result.

## State And Persistence
The test suite maintains process-local talloc state for discovered interfaces, selected share/net names, RPC pipes, and policy handles. Remote state can be significant: `test_witness_AsyncNotify()` deliberately changes cluster resource online/offline state twice per matching interface and relies on successful restoration by toggling again. Witness registrations are transient server context handles; cleanup is done by `test_witness_UnRegister_with_handle()`, which also verifies invalidation. Failure between resource toggles or before unregister can leave cluster resources in the opposite state or active server-side registrations until the server expires them.

## Dependencies
Dependencies include Samba torture RPC helpers, generated NDR clients for witness, srvsvc, and clusapi, DCE/RPC binding manipulation, command-line credentials, loadparm settings, talloc, tevent, and local time reporting. Runtime dependencies include a target exposing the witness RPC endpoint, srvsvc share enumeration, a usable NetBIOS/client computer name, cluster RPC access with sealing, and credentials authorized to query and toggle cluster resources.

## Integration Points
The suite is attached under the RPC torture registry as `witness`. It integrates witness behavior with srvsvc share type discovery and clusapi resource management, making it a cross-service compatibility test rather than an isolated RPC-marshalling test. It also reads `torture:net_name` and uses `dcerpc_server_name()`, `lpcfg_netbios_name()`, and global command-line credentials, so smbtorture configuration determines which cluster network name and client identity the server sees.

## Risks
The `UnRegister` test stub currently returns true without acquiring or freeing a handle, so actual unregister coverage is provided only indirectly by registration and async tests. `init_witness_test_state()` ignores the boolean result of `find_sofs_share()`, and the RegisterEx helper `test_do_witness_RegisterEx()` accepts a `share_name` argument but always sends `NULL`, reducing intended share-specific coverage. Async tests can disrupt a live cluster resource because they intentionally toggle resource state; failures may leave state changed. Tests silently pass loops with no valid witness interface, which can mask undercoverage. Environment sensitivity is high: missing cluster services, non-SOFS shares, insufficient privileges, wrong net name, or timeouts can dominate results.

## Test Signals
Strong positive signals are `WERR_OK` from `GetInterfaceList`, expected `WERR_REVISION_MISMATCH` and `WERR_INVALID_PARAMETER` matrices, successful register/unregister pairs, `WERR_INVALID_PARAMETER` on handle reuse, resource-change AsyncNotify replies with `WITNESS_NOTIFY_RESOURCE_CHANGE`, and timeout calls returning `WERR_TIMEOUT`. Negative signals include clusapi connection failures, unchanged resource state after toggle, empty interface lists, unexpected success for invalid versions, and mismatched witness resource availability messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/witness.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/wkssvc.c -->
# sources/user-network-fs/samba/source4/torture/rpc/wkssvc.c

## Purpose
`wkssvc.c` registers the `rpc.wkssvc` smbtorture suite for the Workstation Service RPC interface. It checks workstation information, transports, logged-on users, network-use mappings, computer-name management, validation and logon-domain calls, domain join/unjoin calls, workstation statistics, and message sending. The file combines read-only conformance tests, expected unsupported/disabled-path assertions, and dangerous tests that can alter target workstation or domain membership state.

## Important APIs, Types, And Functions
The file uses generated `dcerpc_wkssvc_*_r()` client calls from `ndr_wkssvc_c.h` and a single RPC tcase over `ndr_table_wkssvc`. Constants such as `SMBTORTURE_MACHINE_NAME`, `SMBTORTURE_ALTERNATE_NAME`, `SMBTORTURE_TRANSPORT_NAME`, `SMBTORTURE_USE_NAME`, and `SMBTORTURE_MESSAGE` define temporary names and messages. Informational tests include `test_NetWkstaGetInfo()`, `test_NetWkstaTransportEnum()`, `test_NetWkstaEnumUsers()`, `test_NetrWkstaUserGetInfo()`, `test_NetrUseEnum()`, `test_NetrUseGetInfo()`, `test_NetrEnumerateComputerNames()`, `test_NetrWorkstationStatisticsGet()`, and `test_NetrGetJoinInformation()`. Mutating or semi-mutating helpers include `test_NetrUseAdd()`, `test_NetrUseDel()`, `test_NetrAddAlternateComputerName()`, `test_NetrRemoveAlternateComputerName()`, `test_NetrSetPrimaryComputername()`, `test_NetrRenameMachineInDomain2()`, `test_NetrJoinDomain2()`, and `test_NetrUnjoinDomain2()`. `test_GetJoinInformation()` is a helper for join-state verification. `encode_wkssvc_join_password_buffer()` and `dcerpc_binding_handle_transport_session_key()` are used to prepare encrypted join/unjoin passwords.

## Control Flow
Each test populates the relevant wkssvc request structure, calls through the pipe binding handle, asserts NT transport success, then checks the returned `WERROR`. Enumeration tests allocate level-specific containers, set resume handles, and iterate levels or returned names. Use-mapping tests add a level-1 mapping to `\\\\localhost\\sysvol`, enumerate or query it, then delete `S:`. Computer-name tests add an alternate name, verify enumeration, optionally promote it to primary, then restore the original name and remove the alternate. Rename tests capture the primary name, rename to `smbtrt_name`, verify, and rename back. JoinDomain2 and UnjoinDomain2 read current join state, derive expected result, require explicit torture settings for domain admin credentials and domain name, encrypt the password with the RPC session key, perform the operation, and verify the resulting join state. `torture_rpc_wkssvc()` registers all tests and marks state-changing rename/join/unjoin/primary-name paths as dangerous.

## State And Persistence
Most read-only calls keep only talloc-owned local output buffers. Remote persistent effects are important: `NetrUseAdd` creates a workstation use entry until `NetrUseDel`; alternate computer-name tests mutate the target's name list; primary-name and rename tests can alter the machine's identity; JoinDomain2 and UnjoinDomain2 can change domain membership and create or remove domain-side machine-account state depending on server behavior. Several tests attempt restoration, but a failed assertion between mutation and cleanup can leave mappings, alternate names, changed primary names, or domain membership changes behind.

## Dependencies
The suite depends on Samba torture RPC infrastructure, generated wkssvc NDR bindings, command-line credentials, loadparm workgroup/DNS-domain settings, Unicode conversion via `push_ucs2_talloc()`, session-key retrieval, and the wkssvc password-buffer encoder. Runtime coverage depends on the target OS/service implementation, server name formatting, administrative privileges for name and join operations, access to `localhost\\sysvol` for use mapping, and optional torture settings `domain_admin_account`, `domain_admin_password`, and `domain_name`.

## Integration Points
The suite integrates with smbtorture's RPC registry under `wkssvc`. It bridges local command-line credentials into remote wkssvc operations and uses `lpcfg_workgroup()`, `lpcfg_dnsdomain()`, and `dcerpc_server_name()` to form server, domain, account, and UNC strings. Dangerous tests are flagged in the torture framework so normal runs can avoid disruptive machine-name and domain-membership changes.

## Risks
The file contains many environment-specific expectations: unsupported calls are expected to return `WERR_NOT_SUPPORTED` or `RPC_E_REMOTE_DISABLED`, and different Windows/Samba versions may vary. `test_GetJoinInformation()` appears to copy `name_buffer` only if `*name` is non-null, which means callers passing an initialized `NULL` output pointer do not receive the join name. Some cleanup depends on later tests running in a particular order, especially use mapping and computer-name removal. Dangerous tests can rename or join/unjoin real machines. The message-buffer test depends on a local messenger service. The transport delete test expects success when deleting a synthetic transport name, which may not be portable.

## Test Signals
Useful signals are successful suite registration, NTSTATUS OK for all RPC transports, expected WERROR values per call, stable enumeration counts, presence and later absence of `smbtrt_altname`, restoration of the original primary computer name, correct join-state transitions after JoinDomain2/UnjoinDomain2, and no leftover `S:` use mapping. Failure diagnostics are mostly torture comments plus exact NT/WERROR mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rpc/wkssvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/shell.c -->
# sources/user-network-fs/samba/source4/torture/shell.c

## Purpose
`shell.c` implements smbtorture's interactive command shell. It provides a readline-driven REPL that lets users inspect and change torture settings, credentials, and targets, list registered suites, and run named tests without restarting the process.

## Important APIs, Types, And Functions
`struct shell_command` maps a command name to a handler, usage string, and help text. The `commands[]` table defines `auth`, `help`, `list`, `quit`, `run`, `set`, and `target`. `torture_shell()` owns the REPL loop using `smb_readline()`, optional `add_history()`, and `poptParseArgvString()`. `shell_set()` dumps or updates loadparm settings via `lpcfg_dump()` and `lpcfg_set_cmdline()`. `shell_run()` calls `torture_run_named_tests()`. `shell_list()` calls `torture_print_testsuites()`. `shell_auth()` reads and mutates global command-line credentials through `cli_credentials_get_*()` and `cli_credentials_set_*()`. `shell_target()` prints or parses target strings with `torture_parse_target()`. `match_command()` supports full command names and one-character abbreviations.

## Control Flow
Before entering the loop, `torture_shell()` sets an empty guessed password if none was specified to avoid credential prompts during `auth` display. Each prompt reads one line, parses it into argc/argv, scans the command table for a full-name or single-letter match, shifts off the command token, and invokes the matching handler. Handlers either print usage on invalid arity, mutate the shared torture context, or call into the existing smbtorture registry. `quit` exits the whole process with `exit(0)`. Unknown commands are ignored after parsing because no fallback message is emitted.

## State And Persistence
The shell keeps no persistent private state beyond readline history. It mutates process-global command-line credentials and the in-memory loadparm/torture context, so later commands and tests in the same shell session observe changed authentication, target, and configuration values. No changes are written back to smb.conf or other files by this code.

## Dependencies
Dependencies include Samba's readline wrapper, popt argument parsing, command-line credentials, loadparm, smbtorture registry functions, and target parsing helpers. Behavior depends on the global credential object returned by `samba_cmdline_get_creds()` and the active `torture_context`.

## Integration Points
This file is an operator-facing control surface over the broader smbtorture runtime. It integrates test discovery and execution with configuration mutation and credential management. It does not register tests itself; it calls into already-registered suites and shared command-line state.

## Risks
The REPL does not handle empty parsed input before reading `argv[0]`, so a blank or whitespace-only line may dereference invalid data depending on `poptParseArgvString()` output. Parsed `argv` is not freed in the loop, which can leak memory in long sessions. One-letter abbreviations can become ambiguous if future commands share initial letters; the first table match wins. The `auth` command prints the current password to stdout. Unknown commands produce no diagnostic, which can confuse interactive users.

## Test Signals
Signals are successful parsing and dispatch for full and abbreviated commands, correct usage output for wrong arity, successful mutation of credentials and target settings, visible suite listing, and `run TESTNAME` invoking registered tests. Robustness tests should include blank lines, malformed quoting, unknown commands, long sessions, and credential display after no password was supplied.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/shell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/acls.c -->
# sources/user-network-fs/samba/source4/torture/smb2/acls.c

## Purpose
`acls.c` implements the SMB2 ACL and security-descriptor torture suites. It validates generic access-bit mapping, owner and CREATOR_OWNER semantics, inheritance flag propagation, dynamic inheritance behavior, access-based directory enumeration, OWNER_RIGHTS behavior, DENY ACE ordering, maximum-access validation, overwrite behavior for read-only access, and a special non-canonical ACL flag mode. These tests exercise server authorization behavior through real SMB2 create, query-info, set-info, find, and cleanup operations.

## Important APIs, Types, And Functions
Macros `CHECK_STATUS`, `CHECK_ACCESS_FLAGS`, `FAIL_UNLESS`, and `CHECK_SECURITY_DESCRIPTOR` centralize assertion and cleanup flow. `restore_sd_orig()` restores a DACL on an open handle when possible. Core tests include `test_creator_sid()`, `test_generic_bits()`, `test_owner_bits()`, `test_inheritance()`, `test_inheritance_flags()`, `test_sd_flags_vs_chown()`, `test_inheritance_dynamic()`, `test_access_based()`, `test_owner_rights()`, `test_owner_rights_deny()`, `test_owner_rights_deny1()`, `test_deny1()`, `test_mxac_not_granted()`, `test_overwrite_read_only_file()`, and `test_acls_non_canonical_flags()`. Suite factories are `torture_smb2_acls_init()` and `torture_smb2_acls_non_canonical_init()`. Security descriptors are constructed with `security_descriptor_dacl_create()`, compared with `security_descriptor_equal()`, and inspected via generated NDR debug printers on mismatch.

## Control Flow
Most tests create or reset `BASEDIR` (`smb2-testsd`), create a file or directory with enough rights to read and change security descriptors, save the original descriptor, set a crafted DACL or owner, perform one or more SMB2 opens/query-info/find operations, validate returned status and granted access, then restore descriptors and delete test artifacts. Inheritance tests iterate combinations of ACE inheritance flags and descriptor type bits, creating child files/directories and comparing resulting descriptors to expected owner, ACE, and inherited-flag layouts. Access-based enumeration optionally reconnects to the `hideunread` share for Samba targets, changes file DACLs across several read-permission masks, and checks directory listing counts. OWNER_RIGHTS and DENY tests query `maximal_access` from SMB2 create responses. Suite initialization registers each test as a one-tree SMB2 test; the non-canonical suite registers only the specialized inherited-flag canonicalization test.

## State And Persistence
Runtime state is mostly remote filesystem state under `smb2-testsd`, plus open SMB2 handles and talloc-owned descriptors. The tests intentionally mutate DACLs, owners, attributes, and directory contents. Cleanup uses `restore_sd_orig()`, handle closes, unlink/rmdir/deltree, tdis, and logoff, but failures can leave modified ACLs or files behind. Some tests disconnect the session/tree passed to them at cleanup, while later tests leave tree lifetime to the harness. `test_sd_flags_vs_chown()` temporarily changes file owner to World and back; `test_access_based()` may open a separate tree to a special share.

## Dependencies
Dependencies include Samba SMB2 client APIs, raw fileinfo/setfileinfo unions, SMB2 create/find helpers, security descriptor/SID helpers, NDR security printing, torture SMB2 connection helpers, loadparm/target detection, and server support for Windows-compatible ACLs. The access-based enumeration test depends on a Samba share named `hideunread` with `SMB2_SHAREFLAG_ACCESS_BASED_DIRECTORY_ENUM`, unless running against Windows. The non-canonical suite depends on a share configured with inherited ACL flag canonicalization disabled.

## Integration Points
The main suite is registered as `smb2.acls` with description `SMB2-ACLS tests`; the specialized suite is `smb2.acls_non_canonical`. The tests integrate with Samba's SMB2 harness through `torture_suite_add_1smb2_test()`, with authorization code through security descriptor set/get operations, with maximum-access calculation through SMB2 create responses, and with share configuration through target-specific settings such as `hide_on_access_denied` and access-based enumeration flags.

## Risks
The file is broad and highly stateful, so cleanup correctness is critical. Several tests assume Windows-compatible but version-sensitive details, such as whether `SEC_STD_DELETE` appears in maximum access or whether default child descriptors include SYSTEM. Some paths skip Windows or require Samba-only shares, reducing portability. A small cleanup bug exists in `test_acls_non_canonical_flags()`: the first cleanup condition checks `handle` before closing `testdirh`, so an open directory handle may be missed if the file handle is empty. Tests that call `smb2_tdis()` and `smb2_logoff()` on the provided tree can surprise harness code if future changes assume the tree remains connected. The disabled `test_sd_get_set()` indicates known incompatibility with XP/Vista and remains unregistered.

## Test Signals
Positive signals include exact NTSTATUS matches, granted-access masks matching expectations, descriptor equality for generic mapping and inheritance cases, correct default descriptor handling, expected listing counts under access-based enumeration, expected maximal-access masks for OWNER_RIGHTS and DENY ordering, `NT_STATUS_ACCESS_DENIED` when maximum-allowed is combined with an ungranted explicit right, sharing violations for overwrite dispositions on read-only shared opens, and preserved `SEC_DESC_DACL_AUTO_INHERITED` in the non-canonical suite. Failure output typically includes `__location__`, NT status strings, access masks, and NDR dumps of mismatched descriptors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/attr.c -->
# sources/user-network-fs/samba/source4/torture/smb2/attr.c

## Purpose
`attr.c` implements SMB2 torture tests for DOS/Windows file attributes and security-descriptor read behavior. It checks attribute creation and truncation semantics, verifies that setting attributes does not mutate ACLs, confirms directory attribute behavior, verifies that reopening an existing file with new create attributes does not rewrite existing attributes, and validates access rules for reading security descriptors without `READ_CONTROL`.

## Important APIs, Types, And Functions
`open_attrs_table[]` enumerates normal, archive, readonly, hidden, system, and combined attribute masks used across tests. `struct trunc_open_results` and `attr_results[]` encode selected expected outcomes for overwrite/truncation combinations. `smb2_setatr()` opens a path with `SEC_FILE_READ_DATA | SEC_FILE_WRITE_ATTRIBUTE`, sends `RAW_SFILEINFO_BASIC_INFORMATION`, and closes the handle. Test entry points are `torture_smb2_openattrtest()`, `torture_smb2_winattrtest()`, `torture_smb2_winattr2()`, and `torture_smb2_sdreadtest()`. The tests use `smb2_create()`, `smb2_util_getatr()`, `smb2_util_unlink()`, `smb2_deltree()`, `smb2_getinfo_file()`, and `security_ace_equal()`.

## Control Flow
`torture_smb2_openattrtest()` iterates every initial attribute and truncation attribute combination: it creates `openattr.file`, reopens with `NTCREATEX_DISP_OVERWRITE`, expects either success with the correct final attributes or `NT_STATUS_ACCESS_DENIED`, and checks selected cases against `attr_results[]`. `torture_smb2_winattrtest()` creates a file, records its security descriptor, repeatedly sets attributes and verifies both reported attributes and unchanged ACEs, then repeats analogous checks for a directory where `FILE_ATTRIBUTE_DIRECTORY` must be present in the returned attributes. `torture_smb2_winattr2()` creates a file as archive-only, reopens with archive/system/hidden/readonly while using `OPEN_IF`, and asserts the create response still reports only archive. `torture_smb2_sdreadtest()` creates a file, reopens it with only `SEC_FILE_READ_ATTRIBUTE`, confirms security descriptor queries for owner/group/DACL are denied, then confirms a zero-bit security descriptor query succeeds but returns an empty descriptor.

## State And Persistence
Remote state consists of temporary files `openattr.file`, `winattr1.file`, `winattr2.file`, `sdread.file`, and directory `winattr1.dir`. Tests mutate DOS attributes and create/read security descriptors but do not intentionally persist changes. Cleanup resets attributes to normal where needed and unlinks or removes test paths. If a failure occurs before cleanup, readonly/hidden/system files can remain and may require attribute reset before deletion.

## Dependencies
Dependencies include SMB2 client create, setinfo, getinfo, close, unlink, deltree, and attribute helpers; raw fileinfo/setfileinfo structures; security descriptor definitions; and the SMB2 torture harness. Runtime correctness depends on server support for Windows attribute semantics, `RAW_SFILEINFO_BASIC_INFORMATION`, security descriptor queries, and expected access checks around `READ_CONTROL`.

## Integration Points
The functions are SMB2 torture test entry points declared in the SMB2 proto surface and registered elsewhere in the smbtorture SMB2 suite. They complement `acls.c`: `winattrtest` explicitly checks that DOS attribute changes preserve DACL ACEs, and `sdreadtest` validates descriptor access behavior for handles with only read-attribute rights.

## Risks
`smb2_setatr()` returns early on setinfo failure without closing the handle, which can leak a remote handle in failure paths. It also uses `tree` as the talloc context for `smb2_create()`, which is conventional in this area but ties allocations to connection lifetime. `open_attrs_table` contains adjacent `FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_SYSTEM` entries rather than a combined expression at the end, which may be intentional coverage but is visually easy to misread. `torture_smb2_openattrtest()` only has explicit expected-success table entries for selected matrix positions; unlisted success paths are not fully validated against an expected final value. Attribute cleanup can fail if the server denies resetting readonly/system attributes after an earlier failure.

## Test Signals
Strong signals are successful creation/reopen loops, expected `NT_STATUS_ACCESS_DENIED` for disallowed truncation of readonly-like states, exact final attributes for entries in `attr_results[]`, identical ACEs before and after attribute changes, directory attributes always including `FILE_ATTRIBUTE_DIRECTORY`, `winattr2` preserving archive-only attributes across `OPEN_IF`, access denied for owner/group/DACL security descriptor reads without `READ_CONTROL`, and an empty descriptor for a zero-bit security descriptor query.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/attr.c -->
