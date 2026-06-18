# subset-b-009856 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_nt.h -->
# sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_nt.h

Purpose: Public internal declarations for the spoolss server implementation in `srv_spoolss_nt.c`. It exposes lifecycle cleanup, printer driver upgrade messaging, and monitored print queue cache refresh hooks to other Samba source3 RPC/server code.

Important APIs: `srv_spoolss_cleanup()` tears down spoolss server state; `do_drv_upgrade_printer()` is a messaging callback taking `messaging_context`, sender `server_id`, message type, and payload `DATA_BLOB`; `update_monitored_printq_cache()` refreshes cached print queue state. The header itself defines no data structures and depends on forward-visible Samba types from included compilation units.

Control flow and state: This file only declares entry points. State is owned by the spoolss implementation and Samba messaging/printing subsystems. `do_drv_upgrade_printer()` integrates with asynchronous server messages, while cache update and cleanup imply process-global spoolss state outside the header.

Dependencies and integration: Consumers must include Samba messaging and RPC type definitions before or via surrounding includes. The functions integrate spoolss with driver upgrade notifications and print queue monitoring, likely called during spoolss server startup/shutdown or messaging dispatch.

Risks and test signals: ABI/signature drift against `srv_spoolss_nt.c` would break build. Useful tests are compile coverage, spoolss startup/shutdown paths, driver upgrade message delivery, and print queue cache refresh behavior after printer configuration changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_util.c -->
# sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_util.c

Purpose: Implements spoolss helper wrappers that call Samba's internal winreg RPC client routines. The file centralizes creation of a local winreg binding handle and then forwards printer, driver, form, security descriptor, core-driver, and driver-package operations to `cli_winreg_spoolss` helpers.

Important APIs: `winreg_printer_binding_handle()` builds a loopback `127.0.0.1` tsocket address and calls `rpcint_binding_handle()` for `ndr_table_winreg`. The rest of the exported `*_internal()` functions all follow the same pattern: allocate a stackframe, obtain the winreg binding, call the corresponding `winreg_*` helper, free the temporary context, and return `WERROR`. Covered operations include printer create/update/get/delete-key/changeid, printer data get/set/enum/delete, driver get/list/add/delete, core driver get/add, driver package get/add/delete, printer security descriptor get/set, form enum/get/add/set/delete, and printer key enumeration.

Control flow and state: The helpers are synchronous wrappers. Persistent state lives in the registry backend reached through the winreg server, not in this file. Output data is allocated on the caller-provided `mem_ctx`; temporary binding objects live on `tmp_ctx`. Every failure to allocate or bind returns immediately with `WERR_NOT_ENOUGH_MEMORY` or the winreg connection error.

Dependencies and integration: Includes `rpc_server/rpc_ncacn_np.h`, tsocket, generated spoolss/winreg NDR headers, `srv_spoolss_util.h`, and `rpc_client/cli_winreg_spoolss.h`. It bridges spoolss server code to the registry-backed printer database without duplicating registry path logic.

Risks and test signals: The repeated wrapper pattern is easy to regress by passing `tmp_ctx` where caller-owned output is required; output-owning helpers intentionally receive `mem_ctx`. Binding failures are logged at level 0 and surface as converted `WERROR`s. Test with printer add/update/delete, driver package install/remove, form operations, and printer ACL get/set while forcing winreg unavailable and low-memory paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_util.h -->
# sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_util.h

Purpose: Declares the spoolss-to-winreg utility interface implemented by `srv_spoolss_util.c`. It is the source3 spoolss server's typed contract for registry-backed printer and print driver operations.

Important APIs: The header declares `winreg_printer_binding_handle()` plus wrappers for printer lifecycle and metadata, printer data keys/values, driver list and driver info manipulation, printer security descriptors, forms, subkey enumeration, core printer drivers, and driver packages. It forward-declares `auth_session_info` and `dcerpc_binding_handle` and relies on generated spoolss/winreg types being visible to includers.

Control flow and state: No code or storage is defined here. All functions accept caller memory, session credentials, and `messaging_context`, making authentication and local RPC messaging explicit inputs. Persistent state is the Samba registry, reached indirectly by implementations.

Dependencies and integration: Used by spoolss RPC code that needs to read/write printer registry state through the internal winreg server. The API shape mirrors `cli_winreg_spoolss` operations and keeps server code from constructing winreg bindings manually.

Risks and test signals: Interface changes affect many spoolss operations. Watch for mismatches between pointer ownership, constness, and output allocation. Build tests plus spoolss functional tests around drivers, forms, printer data, and ACLs provide coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srv_access_check.c -->
# sources/user-network-fs/samba/source3/rpc_server/srv_access_check.c

Purpose: Shared RPC server access-control helpers. It wraps security descriptor checks with Samba privilege/root/system-token overrides and maps `MAXIMUM_ALLOWED_ACCESS` into concrete generic access requests.

Important APIs: `access_check_object()` calls `se_access_check()` against a supplied security descriptor and token, but can remove requested `rights_mask` bits before the descriptor check when either supplied privilege is present, later adding those bits back to granted access. It also overrides denial for system tokens with system privilege and for `root_mode()`. `map_max_allowed_access()` expands `MAXIMUM_ALLOWED_ACCESS` to read/execute for everyone and to generic all for root, Builtin Administrators, Builtin Account Operators, and Domain Admins on a DC.

Control flow and state: The functions are stateless except for reading process/root state, global SIDs, machine SID, and DC role. `access_check_object()` mutates `des_access` locally and writes `acc_granted`; `map_max_allowed_access()` mutates the caller's access mask in place.

Dependencies and integration: Depends on `../libcli/security/security.h`, privilege APIs, root/euid helpers, and passdb machine SID helpers. It is intended for SAMR/other RPC object access paths that need privilege-specific rights augmentation.

Risks and test signals: Privilege overrides can overgrant if callers pass an excessive `rights_mask`; the final code ORs the full mask, not only saved requested bits, despite the comment referencing saved bits. Test with normal users, root, system token, Builtin Administrators, Account Operators, Domain Admins, and requests with/without `MAXIMUM_ALLOWED_ACCESS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srv_access_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srv_access_check.h -->
# sources/user-network-fs/samba/source3/rpc_server/srv_access_check.h

Purpose: Header for shared RPC server access-check helpers in `srv_access_check.c`.

Important APIs: Declares `access_check_object()` for descriptor/token/privilege-based access decisions and `map_max_allowed_access()` for converting `MAXIMUM_ALLOWED_ACCESS` into usable requested access bits. The signatures expose Samba security descriptors, security tokens, UNIX tokens, privilege IDs, desired/granted access masks, and debug labels.

Control flow and state: No local state. Callers provide all descriptors/tokens and receive results by output pointer or in-place requested-access mutation.

Dependencies and integration: Used by RPC servers needing consistent Samba access semantics. It depends on Samba security type declarations available from surrounding includes.

Risks and test signals: Signature drift breaks all shared authorization call sites. Tests should compile dependent RPC modules and verify privilege-sensitive access paths that call these helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srv_access_check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srv_pipe_hnd.c -->
# sources/user-network-fs/samba/source3/rpc_server/srv_pipe_hnd.c

Purpose: Implements fake-file named-pipe proxy handles for source3 RPC over `ncacn_np`. It connects SMB named-pipe opens to the local RPC server stream and provides asynchronous read/write operations.

Important APIs: `fsp_is_np()` identifies `FAKE_FILE_TYPE_NAMED_PIPE_PROXY`; `np_open()` allocates `fake_file_handle`, initializes `npa_state`, and calls `local_np_connect()` with remote/local socket addresses and session info; `np_read_in_progress()` checks the read queue length; `np_write_send()/np_write_recv()` write data through `tstream_writev_queue_send`; `np_read_send()/np_read_recv()` read PDUs through `tstream_readv_pdu_queue_send`.

Control flow and state: State is stored in `fake_file_handle->private_data` as `npa_state`, including stream, read queue, and write queue. Writes are queued and complete via `np_write_done()`. Reads use `np_ipc_readv_next_vector()` to cap reads at `UINT16_MAX`, return short reads when no more pending bytes are available, and set `is_data_outstanding` when stream pending bytes exceed the caller buffer. Zero-length reads intentionally remain pending and are completed as `NT_STATUS_PIPE_BROKEN` if the zero-read state is destroyed.

Dependencies and integration: Depends on fake file support, RPC DCE, local named-pipe client, `tevent`, `tstream`, tsocket, and NDR table declarations. This is the bridge between SMB file operations on named pipes and the in-process Samba RPC endpoint machinery.

Risks and test signals: Queue/destructor behavior is subtle; regressions can hang zero-byte reads, misreport outstanding data, or return invalid handles. Test named-pipe open/read/write, concurrent queued reads/writes, short-read behavior, client disconnects, invalid fake-file types, and zero-length read cancellation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srv_pipe_hnd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srv_pipe_hnd.h -->
# sources/user-network-fs/samba/source3/rpc_server/srv_pipe_hnd.h

Purpose: Declares the named-pipe fake-file proxy API used by SMB file handling and RPC server code.

Important APIs: Exposes `fsp_is_np()`, `np_open()`, `np_read_in_progress()`, asynchronous `np_write_send()/recv()`, and asynchronous `np_read_send()/recv()`. Forward declarations include `tsocket_address` and `pipes_struct`; signatures use `fake_file_handle`, `auth_session_info`, `tevent_context`, `messaging_context`, and `dcesrv_context`.

Control flow and state: The header defines no storage; callers receive a `fake_file_handle` that owns implementation state created in `np_open()`. Read/write completion follows Samba `tevent_req` conventions.

Dependencies and integration: Integrated with source3 fake-file and local RPC named-pipe code. Callers must honor async send/recv pairing and handle `NTSTATUS` completion.

Risks and test signals: API misuse can leak handles or leave requests pending. Compile coverage and named-pipe RPC integration tests are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srv_pipe_hnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srvsvc/srv_srvsvc_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/srvsvc/srv_srvsvc_nt.c

Purpose: Implements the source3 SRVSVC RPC server: server information, share enumeration/get/set/add/delete, session/connection/file enumeration, remote time, file security get/set, disk enumeration, name validation, and file close requests. Many less-used SRVSVC/DFS/transport/character-device opnums intentionally fault as unsupported.

Important APIs/functions: Share formatting helpers populate levels 0, 1, 2, 501, 502, 1004, 1005, 1006, 1007, and 1501 from loadparm state and share security DB. `init_srv_share_info_ctr()` reloads shares/printers/usershares/registry shares, applies browseable/local-address/access-based-enumeration filters, optionally adds a homes share, and builds the requested share counter. `_srvsvc_NetShareSetInfo()`, `_srvsvc_NetShareAdd()`, and `_srvsvc_NetShareDel()` call configured `change share command`, `add share command`, and `delete share command`, update share ACL persistence, and notify all processes with `MSG_SMB_CONF_UPDATED`. Session/connection/file enumeration traverses session databases, `smbXsrv_tcon_global.tdb`, and share mode records. `_srvsvc_NetGetFileSecurity()` and `_srvsvc_NetSetFileSecurity()` create a temporary connection to a share, resolve a path, open the file through VFS, and get/set NT ACLs.

Control flow and state: Read paths synthesize RPC structures from live Samba state: loadparm services, current connections, sessions, share modes, byte-range locks, share security DB, and VFS ACLs. Write paths require root or `SeDiskOperatorPrivilege`, sanitize quotes in command arguments, optionally `become_root()`, run external helper commands via `smbrun()`, reload or notify configuration changes, and persist share security with `set_share_security()`/`delete_share_security()`. `NetSessDel` and `NetFileClose` send messages to target smbd processes (`MSG_SHUTDOWN`, `MSG_SMB_CLOSE_FILE`).

Dependencies and integration: Integrates loadparm, usershares, registry shares, printer reload, global messaging, session database, share mode locking, byte-range locks, VFS file open/ACL operations, Samba privilege checks, generated `ndr_srvsvc` server glue, and generic file security mapping.

Risks and test signals: Major risk areas are authorization, shell-command construction, race/staleness in live TDB traversals, path canonicalization, and share security synchronization when command execution succeeds but ACL persistence fails. Test admin vs non-admin enumeration, access-based share enum, hidden shares, homes auto-registration cleanup, add/change/delete share with and without helper commands, Disk Operator privilege, share ACL round trips, file ACL get/set through VFS, stale process filtering, and unsupported opnum fault behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/srvsvc/srv_srvsvc_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_nt.c

Purpose: Implements the source3 SVCCTL RPC server for service-control-manager and service handles. It supports opening SCM/services, querying display names/status/config/security, enumerating services, starting/stopping/interrogating services, locking/unlocking the service database as a stub handle, and server init/shutdown. Many write/configuration and notification opnums intentionally fault as unsupported.

Important APIs/functions: `init_service_op_table()` builds global `svcctl_ops` from configured external services using `rcinit_svc_ops` plus built-ins Spooler, NETLOGON, RemoteRegistry, and WINS. `construct_scm_sd()` grants SCM read to Everyone and all access to Builtin Administrators. `create_open_service_handle()` stores `SERVICE_INFO` in policy handles. `_svcctl_OpenSCManagerW()` and `_svcctl_OpenServiceW()` map generic access and check SCM/service security descriptors. Query and control functions enforce handle type and granted access bits before calling service operation callbacks or registry-backed service metadata helpers.

Control flow and state: The only file-local persistent state is the global `svcctl_ops` table, allocated at server init and freed at shutdown. Service metadata and security descriptors are read/written via `svcctl_get_*`/`svcctl_set_secdesc` helpers backed by winreg service keys. Service start/stop/status operations dispatch to `SERVICE_CONTROL_OPS`. Unsupported operations set `p->fault_state = DCERPC_FAULT_OP_RNG_ERROR` and return `WERR_NOT_SUPPORTED`.

Dependencies and integration: Depends on generated SVCCTL NDR glue, service operation modules, `services/svc_winreg_glue.h`, security descriptor utilities, auth session info, global messaging, and `svcctl_init_winreg()` from `srv_svcctl_reg.c`. Init wraps generated endpoint init to seed service registry keys first.

Risks and test signals: Access masks are handle-time decisions, so tests should verify least privilege on query/start/stop/security operations. Buffer sizing and NDR marshaling for enum/config/status-ex replies are compatibility-sensitive. Test SCM open, service open absent/present, service status, enum with small buffers, config/config2, DACL get/set, unsupported opnums, init failure when winreg seeding fails, and cleanup freeing `svcctl_ops`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_nt.h -->
# sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_nt.h

Purpose: Header exposing SVCCTL service operation table lifecycle functions.

Important APIs: `init_service_op_table()` initializes the global service-name-to-operations table; `shutdown_service_op_table()` frees it. These are used by SVCCTL endpoint init/shutdown wrappers.

Control flow and state: No state in the header; the implementation owns `svcctl_ops`. Successful initialization is prerequisite for service lookup and handle creation.

Dependencies and integration: Used by SVCCTL RPC server setup. It has minimal declarations and relies on surrounding Samba includes for boolean type definitions.

Risks and test signals: If initialization is skipped or fails, service opens can dereference missing operation tables. Compile coverage plus SVCCTL endpoint startup/shutdown tests are appropriate.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_reg.c -->
# sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_reg.c

Purpose: Seeds the Samba registry with service-control-manager service keys under `SYSTEM\\CurrentControlSet\\Services`. It creates built-in and configured external service records with display names, image paths, descriptions, basic service values, and default service security descriptors.

Important APIs/functions: `svcctl_init_winreg()` opens HKLM services key as the system session, enumerates existing subkeys, and adds missing built-in/configured services via `svcctl_add_service()`. `svcctl_add_service()` creates the service key, writes `Start`, `Type`, `ErrorControl`, `ObjectName`, `DisplayName`, `ImagePath`, and `Description`, then creates a `Security` subkey and stores a generated service security descriptor. `read_init_file()` parses service script comments for `Description:`. `svcctl_get_common_service_dispname()` maps common Unix service names to friendlier display names.

Control flow and state: Persistent state is the registry backend reached through internal winreg RPC calls. Built-in service metadata is hardcoded; external service metadata comes from `lp_svcctl_list()` and optional init script descriptions under `${MODULESDIR}/${SVCCTL_SCRIPT_DIR}`. Temporary state lives under a stackframe and policy handles are closed on exit.

Dependencies and integration: Depends on service metadata/glue, generated winreg client stubs, internal winreg helpers, auth system session, registry backend DB, and Samba loadparm service list. It is invoked during SVCCTL server initialization before generated endpoint init.

Risks and test signals: There are suspicious skip-loop index uses comparing `subkeys[i]` instead of `subkeys[j]`, which can miss existing keys or read the wrong entry. Error handling must close policy handles and avoid partially initialized service keys. Test registry seeding on empty and pre-populated registries, built-in/external service lists, missing/unreadable init files, generated security descriptor presence, and idempotent repeated startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_reg.h -->
# sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_reg.h

Purpose: Header for SVCCTL registry initialization.

Important APIs: Declares `svcctl_init_winreg(struct messaging_context *msg_ctx)`, which ensures service keys exist in the registry before SVCCTL serves requests.

Control flow and state: No state in the header. The implementation uses the passed messaging context to open internal winreg handles and persist service metadata.

Dependencies and integration: Included by SVCCTL server startup code. Requires `messaging_context` type visibility from surrounding Samba includes.

Risks and test signals: A failed or missing declaration affects endpoint initialization. Build coverage and SVCCTL startup tests with winreg available/unavailable are sufficient signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/winreg/srv_winreg_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/winreg/srv_winreg_nt.c

Purpose: Implements the source3 WINREG RPC server. It provides registry hive/key open/close, value/key query/enumeration, key/value create/delete/set, key security get/set, performance-data query support, remote shutdown script hooks, multiple-value queries, and generated winreg endpoint glue. Several hive load/save/notify/extended delete operations are stubs or unsupported.

Important APIs/functions: `open_registry_key()` opens a hive via `reg_openhive()` or subkey via `reg_openkey()` and stores a `registry_key` in a policy handle. `_winreg_QueryValue()`, `_winreg_QueryInfoKey()`, `_winreg_EnumKey()`, and `_winreg_EnumValue()` read registry data and implement Windows buffer-size conventions. `_winreg_CreateKey()`, `_winreg_SetValue()`, `_winreg_DeleteKey()`, and `_winreg_DeleteValue()` mutate the registry backend. `_winreg_GetKeySecurity()` and `_winreg_SetKeySecurity()` enforce `READ_CONTROL`/`WRITE_DAC`, marshal/unmarshal security descriptors, and call registry security APIs. `_winreg_InitiateSystemShutdownEx()` and `_winreg_AbortSystemShutdown()` run configured scripts with optional root elevation for `SeRemoteShutdownPrivilege`. `_winreg_QueryMultipleValues2()` batches value reads into one output buffer.

Control flow and state: Per-open state is stored in dcesrv policy handles as `registry_key` objects tagged as registry-key handles. Persistent state lives in Samba registry backends and performance counter providers. Shutdown operations do not modify registry state; they substitute parameters into configured commands and execute with `smbrun()`. Unsupported opnums set `DCERPC_FAULT_OP_RNG_ERROR` where appropriate.

Dependencies and integration: Depends on generated winreg NDR glue, registry API/backends, performance counter helpers, RPC policy-handle management, auth session info, privilege checks, security descriptor marshal helpers, loadparm shutdown scripts, and Samba command execution.

Risks and test signals: Buffer-size semantics, handle validation, and registry ACL enforcement are critical. Shutdown command substitution sanitizes the message with `talloc_alpha_strcpy()` but still executes administrator-configured shell commands; privilege and configuration tests matter. Test hive/subkey opens, invalid handles, query value with small/no buffers, HKPD values, enum key/value, create/set/delete persistence, security descriptor round trips, multiple-value partial buffers/missing values, shutdown privilege behavior, and unsupported operation faults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/winreg/srv_winreg_nt.c -->
