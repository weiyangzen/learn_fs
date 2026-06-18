# subset-b-007808 research

Grouped research for OpenAFS `uss` account-management sources and selected `util` support files. Each section is bounded for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss.c -->
# sources/distributed-fs/openafs/src/uss/uss.c

Purpose: `uss.c` is the executable entrypoint for the OpenAFS user account management tool. It defines the `add`, `bulk`, and `delete` commands, wires common command-line options through the OpenAFS `cmd` package, initializes global buffers and error tables, and coordinates the lower-level modules that touch PTS, KAS, VLDB, cache-manager mount points, ACLs, and template-driven filesystem setup.

Important APIs and functions: `main()` allocates `uss_fs_InBuff` and `uss_fs_OutBuff`, registers command syntaxes, installs `GetCommon()` as the `cmd_SetBeforeProc()` hook, dispatches the command, and conditionally calls `uss_fs_UnlogToken()`. `GetCommon()` parses common flags, expands the target cell, and records whether the target is local. `AddUser()` and `DelUser()` translate single-command arguments into `uss_common` globals and call `DoAdd()` or `DoDelete()`. `HandleBulk()` reads a bulk file line by line and dispatches `add`, `delete`, `delvolume`, `savevolume`, and `exec` records through helpers such as `DoBulkAddLine()`, `DoBulkDeleteLine()`, and `DoBulkExecLine()`. `SaveRestoreInfo()` captures PTS UID and volume/server/partition data before deletion.

Control flow: add validates/authenticates the creator, validates the requested username, opens the template, creates the PTS entry, creates the KAS entry unless skipped, parses the template with `yyparse()`, then restores staged ACLs through `uss_acl_CleanUp()`. delete validates the name, discovers volume metadata from the mount point, removes the mount point, optionally deletes the volume, removes the KAS entry, then removes the PTS entry. Bulk mode resets global state per input line but keeps command-wide flags such as dry-run, skipauth, overwrite, pipe, and default password expiration.

State and persistence: this file is heavily global-state-driven. It mutates `uss_*` globals from `uss_common.c`, keeps a static template filename, stores bulk password-expiration default in `uss_BulkExpires`, tracks `local_Cell`, and owns the cache-manager I/O buffers declared for `uss_fs`. Persistent effects are delegated: PTS/KAS DB records, volumes, mount points, ACLs, filesystem files, and tokens.

Dependencies and integration: uses OpenAFS `cmd`, cell configuration, KAS, VLDB, Ubik error tables, yacc/lex parser symbols, and all local `uss_*` modules. Template parsing relies on `uss_yyin`/`uss_yyout` and generated parser code outside this work item.

Risks: many command-line strings are copied with `strcpy()` into fixed buffers without local length checks, while bulk mode uses bounded `uss_common_FieldCp()`. Add flow is not transactional: if PTS succeeds and KAS or template work fails, earlier side effects are not rolled back. `yyparse()` can `exit(-1)` unless `uss_ignoreFlag` is set. Bulk status reports the previous line before executing the current line, which is intentional but easy to misread. Test signals should cover dry-run paths, bulk field overflow, password-expiration bounds, skipauth, duplicate users, preexisting templates, and partial-failure behavior across PTS/KAS/template boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_acl.c -->
# sources/distributed-fs/openafs/src/uss/uss_acl.c

Purpose: `uss_acl.c` implements ACL and quota operations for `uss`. It converts between AFS external ACL text and internal linked lists, applies positive or negative ACL changes, sets volume quotas, and restores final ACLs for directories staged during account creation.

Important APIs and functions: exported `uss_acl_SetAccess()` parses an argument containing a path followed by user/right pairs, fetches the current ACL with `uss_fs_GetACL()`, optionally clears it, applies each pair, externalizes the result, and writes it with `uss_fs_SetACL()`. `uss_acl_SetDiskQuota()` builds a `uss_VolumeStatus_t` payload and calls `uss_fs_SetVolStat()`. `uss_acl_CleanUp()` walks `uss_currentDir` and restores each saved final ACL. Internal helpers include `Convert()` for rights names or `rlidwka` characters, `ParseAcl()`, `AclToString()`, `ChangeList()`, `FindList()`, `PruneList()`, and `foldcmp()`.

Control flow: ACL modification first isolates the path, then repeatedly consumes `user rights` fields separated by spaces. For clear operations it starts from `EmptyAcl()`; otherwise it parses the current cache-manager ACL buffer. Rights set to zero are pruned from the chosen list. Cleanup restores directories in reverse creation order because `uss_currentDir` is a stack.

State and persistence: internal ACL structures are heap-allocated; cleanup frees the `uss_subdir` chain but not all temporary ACL nodes allocated during `uss_acl_SetAccess()`. Persistent state is AFS ACL and quota metadata via cache-manager pioctls.

Dependencies and integration: depends on AFS rights constants from `prs_fs.h`, cache-manager wrappers in `uss_fs.c`, common parsing in `uss_common_FieldCp()`, global verbosity/dry-run/account-creator state, and `uss_VolumeStatus_t` from `uss_common.h`.

Risks: `AclToString()` concatenates into a static `AFS_PIOCTL_MAXSIZE` buffer without explicit bounds checks. `ChangeList()` uses `strcpy()` into a 100-byte name field after callers accept up to 64-byte user fields, so current call sites are bounded but the helper is fragile. Allocation failures are not consistently checked. `uss_acl_CleanUp()` ignores return codes from final ACL restoration. Test signals should exercise clear versus merge behavior, negative ACLs, rights aliases, zero-right pruning, oversized ACLs, invalid rights characters, quota payload length, and cleanup after multi-directory template creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_acl.h -->
# sources/distributed-fs/openafs/src/uss/uss_acl.h

Purpose: `uss_acl.h` declares the ACL and quota interface consumed by template actions, volume creation, and final account cleanup.

Important APIs: `uss_acl_SetAccess(char *a_access, int a_clear, int a_negative)` sets an ACL from a path plus user/right pairs, optionally clearing existing entries and optionally targeting the negative ACL list. `uss_acl_SetDiskQuota(char *a_path, int a_q)` updates the max quota of the volume mounted at `a_path`. `uss_acl_CleanUp(void)` restores final ACLs for directories chained in `uss_currentDir`.

Control flow and integration: the header is included by `uss_vol.c` and `uss_procs.c` to temporarily grant the account creator full control during setup, then by `uss.c` to call cleanup after template parsing. It intentionally hides the internal ACL list representation from callers.

State and persistence: no storage is defined here, but all functions operate on global `uss_common` state or persistent AFS metadata through `uss_fs`.

Risks and test signals: callers must format `a_access` exactly as expected; the type does not encode path/user/right boundaries. Tests should verify callers pass clear/negative flags correctly, especially final cleanup and volume-home creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_common.c -->
# sources/distributed-fs/openafs/src/uss/uss_common.c

Purpose: `uss_common.c` owns the global working state shared by all `uss` modules and provides initialization/reset plus bounded field parsing for bulk files and ACL/template argument strings.

Important APIs and state: it defines exported buffers such as `uss_User`, `uss_Uid`, `uss_Server`, `uss_Partition`, `uss_MountPoint`, `uss_RealName`, `uss_Pwd`, `uss_Volume`, `uss_Cell`, and `uss_ConfDir`; flags such as `uss_DryRun`, `uss_SkipKaserver`, `uss_Overwrite`, `uss_SaveVolume`, `uss_ignoreFlag`, and `uss_syntax_err`; numeric IDs for volume/server/partition and desired UID; directory-pool storage; and the `uss_currentDir` cleanup stack. `uss_common_Init()` sets one-time defaults, including config directory and template line number. `uss_common_Reset()` clears per-account fields back to idle or saved values. `uss_common_FieldCp()` copies a delimited field with overflow detection.

Control flow: main calls `uss_common_Init()` once. Each single command and each bulk record calls `uss_common_Reset()` before filling account-specific fields. Field parsing consumes until separator, NUL, or newline, null-terminates the destination, skips excess input on overflow, and collapses repeated spaces when the separator is a space.

State and persistence: all storage is process-global and non-reentrant. It persists only for the process lifetime, but its values drive persistent side effects in other modules. Saved password path/format/restore/save-volume fields are intended to persist across resets.

Dependencies and integration: includes OpenAFS configuration constants and KAS name lengths. `line` is external parser state from the yacc/lex layer.

Risks: globals make concurrency impossible and make partial resets a source of cross-record leakage. Some arrays have strict legacy limits, especially eight-character usernames and sixteen-character passwords. `uss_common_Init()` never sets `initDone = 1`, so its guard is ineffective and repeated calls reinitialize defaults. Test signals should verify reset isolation between bulk lines, field overflow behavior, space-collapsing semantics, saved/default values, and repeated initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_common.h -->
# sources/distributed-fs/openafs/src/uss/uss_common.h

Purpose: `uss_common.h` is the shared contract for `uss` state, constants, and helper routines. It centralizes legacy field sizes, default password, verbosity constants, path sizes, volume status layout, cleanup-list type, and all exported globals.

Important types and APIs: `struct uss_subdir` records directories whose ACLs must be restored, with a backward link, path, and final ACL string. `uss_VolumeStatus_t` mirrors the volume status structure needed for pioctl quota/status calls without including conflicting headers. The API exposes `uss_common_Init()`, `uss_common_Reset()`, and `uss_common_FieldCp()`.

Control flow and integration: nearly every `uss` implementation includes this header. The parser, command layer, PTS/KAS/VLDB modules, ACL code, and filesystem template actions communicate mostly through these globals instead of explicit context objects.

State and persistence: the header declares process-global mutable fields that represent one current user/account operation. Persistent side effects are not in the header, but this state determines PTS/KAS identities, mount-point paths, volume metadata, ACL cleanup, and dry-run/overwrite behavior.

Risks and test signals: fixed sizes and global mutability are the dominant hazards. APIs do not enforce initialization order or safe copying. Test coverage should include maximum-size boundary values for each exported buffer, reset of `uss_currentDir`, and interactions between saved and per-operation values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_fs.c -->
# sources/distributed-fs/openafs/src/uss/uss_fs.c

Purpose: `uss_fs.c` wraps AFS cache-manager operations used by `uss`: ACL pioctls, volume status pioctls, backup-map refresh, mount-point symlink creation/deletion, and token removal for a cell.

Important APIs and functions: exported wrappers include `uss_fs_GetACL()`, `uss_fs_SetACL()`, `uss_fs_GetVolStat()`, `uss_fs_SetVolStat()`, `uss_fs_CkBackups()`, `uss_fs_MkMountPoint()`, `uss_fs_RmMountPoint()`, and `uss_fs_UnlogToken()`. Internal `InAFS()` probes with `VIOC_FILE_CELL_NAME`, `ParentAndComponent()` splits a path for mount-point deletion, and `CarefulPioctl()` retries pioctls after `ENODEV` by calling `uss_fs_CkBackups()`.

Control flow: ACL and volume status functions fill a static `ViceIoctl` blob and route through `CarefulPioctl()`. Mount creation checks that the parent is in AFS, formats local or cross-cell mountpoint symlink contents, and calls `symlink()`. Mount deletion first validates the target with `VIOC_AFS_STAT_MT_PT`, then removes it with `VIOC_AFS_DELETE_MT_PT` unless dry-run is enabled. Token unlog enumerates tokens, marks those whose client cell matches, forgets all, and re-registers the rest.

State and persistence: uses a file-static `ViceIoctl` and global `uss_fs_InBuff`/`uss_fs_OutBuff`; it is not thread-safe. Persistent changes are AFS ACL/status data, mount-point objects, and user tokens.

Dependencies and integration: depends on `pioctl`, `venus.h` opcode constants, Rx/auth token APIs, global dry-run state, and `local_Cell` from `uss.c`.

Risks: static pioctl blob and shared buffers make reentrancy unsafe. `ParentAndComponent()` uses `strcpy()` into caller buffers. `uss_fs_UnlogToken()` does not check `malloc()` and can discard all tokens before failing to restore some. `uss_fs_MkMountPoint()` is less used than direct symlink creation in `uss_vol.c`, so behavior may diverge. Test signals should include ENODEV retry, non-AFS parent rejection, dry-run mount removal, token preservation, and cross-cell mount text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_fs.h -->
# sources/distributed-fs/openafs/src/uss/uss_fs.h

Purpose: `uss_fs.h` declares the cache-manager and token operations used by account creation and deletion.

Important APIs: it defines `USS_FS_MAX_SIZE` as the shared 2048-byte buffer size and declares `uss_fs_InBuff`/`uss_fs_OutBuff`. The public functions get/set ACLs, get/set volume status, refresh backup mappings, create/remove mount points, and unlog tokens for a cell.

Control flow and integration: `uss_acl.c` uses ACL and volume-status setters, `uss_vol.c` uses volume status and mount-point handling, and `uss.c` allocates the declared buffers and calls token unlog on exit when administrator authentication was staged.

State and persistence: callers must allocate the two exported buffers before functions that rely on them. The API directly represents persistent AFS cache-manager effects.

Risks and test signals: the header exposes raw mutable buffers and raw `char *` path arguments, so callers must enforce size and lifetime. Tests should verify buffer allocation before use, pioctl error propagation, and dry-run callers avoiding persistent calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_kauth.c -->
# sources/distributed-fs/openafs/src/uss/uss_kauth.c

Purpose: `uss_kauth.c` integrates `uss` with the legacy AFS Authentication Server. It identifies the administrator, obtains admin tokens, creates/deletes user auth entries, validates usernames using KAS parsing rules, and sets password/security fields.

Important APIs and state: exported `uconn_kauthP` is the Ubik client for KAS. `uss_kauth_InitAccountCreator()` sets `uss_AccountCreator` and `CreatorInstance` from `-admin` or local passwd data. `InitThisModule()` obtains or prompts for an admin token, handles piped passwords, establishes `ka_AuthServerConn()`, and may stage a local token for later unlog. `uss_kauth_AddUser()`, `uss_kauth_DelUser()`, `uss_kauth_CheckUserName()`, and `uss_kauth_SetFields()` perform the account operations.

Control flow: operations short-circuit successfully when `uss_SkipKaserver` is set. Otherwise they lazily initialize KAS state. Add converts the cleartext password to a key and calls `ubik_KAM_CreateUser()`. Delete calls `ubik_KAM_DeleteUser()` and treats missing users as success. Username validation parses principal/instance/cell, rejects instance/cell/colon, enforces the eight-character legacy limit, and rewrites `uss_User` to the parsed principal. `SetFields()` encodes password expiry, reuse policy, login failure count, and lockout duration into spare auth bytes before `ubik_KAM_SetFields()`.

State and persistence: module state includes `initDone`, parsed user principal buffers, creator instance, `Pipe`, and `doUnlog`. Persistent effects are KAS database entries, token cache changes, and auth field updates.

Dependencies and integration: uses KAS/kauth libraries, Ubik, token cache APIs, passwd lookups, global command flags, and `uss_common` identity buffers.

Risks: cleartext passwords are held in stack buffers and may be read from stdin. Several initialization failures call `exit(code)` instead of returning. The code preserves legacy DES/KAS limits and truncation behavior. `strncpy(longPassBuff, getpipepass(), sizeof(longPassBuff))` may omit explicit NUL if input fills the buffer. Test signals should include skipauth, pipe password, long admin password fallback, invalid username forms, dry-run KAS add/delete/setfields, and token cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_kauth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_kauth.h -->
# sources/distributed-fs/openafs/src/uss/uss_kauth.h

Purpose: `uss_kauth.h` declares authentication-server operations for `uss`.

Important APIs: `uss_kauth_InitAccountCreator()` prepares administrator identity, `uss_kauth_AddUser()` creates a KAS user from a cleartext password, `uss_kauth_DelUser()` deletes one, `uss_kauth_CheckUserName()` validates and normalizes `uss_User`, and `uss_kauth_SetFields()` changes expiry/reuse/failure/lockout fields.

Control flow and integration: `uss.c` calls initialization before add/delete/bulk processing and uses `CheckUserName()` before persistent changes. Template grammar code can call `SetFields()` for security options.

State and persistence: implementation uses process-global KAS connection and global user/cell/admin state. Persistent effects are KAS database mutations unless `-skipauth` or dry-run is active.

Risks and test signals: API parameters are weakly typed strings, especially for security fields. Tests should verify validation before PTS/KAS mutations, skipauth behavior, and field-boundary handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_kauth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_procs.c -->
# sources/distributed-fs/openafs/src/uss/uss_procs.c

Purpose: `uss_procs.c` implements template actions for building a user filesystem: create directories, copy prototype files, echo content, run shell commands, create links, choose `$AUTO` directories, resolve owners, locate templates, and report parser errors.

Important APIs and functions: exported `uss_procs_BuildDir()`, `uss_procs_CpFile()`, `uss_procs_EchoToFile()`, `uss_procs_Exec()`, `uss_procs_SetLink()`, `uss_procs_GetOwner()`, `uss_procs_PickADir()`, `uss_procs_AddToDirPool()`, `uss_procs_FindAndOpen()`, and `uss_procs_PrintErr()`. Static `Copy()` and `Echo()` perform low-level file writes.

Control flow: all mutating template actions bail when `uss_syntax_err` is already set. Overwrite checks skip existing targets unless `uss_OverwriteThisOne` is true. Directory creation sets Unix mode/owner, grants temporary full ACL to `uss_AccountCreator`, and pushes final ACL onto `uss_currentDir`. File copy and echo create or overwrite files, set mode, and chown. `$AUTO` selection counts non-dot entries under configured candidate directories and picks the least populated.

State and persistence: uses global `temp[1000]`, parser `line`, common flags, directory pool, and cleanup stack. Persistent effects are filesystem directories/files/links, owners, modes, ACLs, and arbitrary shell-command side effects.

Dependencies and integration: called by generated grammar actions after `uss.c` opens a template. Depends on POSIX filesystem APIs, passwd APIs, `uss_acl_SetAccess()`, and common globals.

Risks: `uss_procs_Exec()` passes template content to `system()`. `Copy()` opens overwrite targets without `O_TRUNC`, so shorter copied files can retain stale trailing bytes. Several `strcpy()`/`strcat()` calls operate on fixed buffers or mutate caller-owned `a_proto`. `$AUTO` path logic is fragile and has a pointer comparison typo-like loop condition. Test signals should cover dry-run, overwrite/no-overwrite, copy truncation, owner lookup failures, template search paths, `$AUTO` selection, and ACL cleanup stack order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_procs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_procs.h -->
# sources/distributed-fs/openafs/src/uss/uss_procs.h

Purpose: `uss_procs.h` declares the template action interface used by the generated `uss` grammar and by bulk `exec` handling.

Important APIs and definitions: `uss_procs_YOUNG` and `uss_procs_ANCIENT` classify preexisting mountpoints. Function declarations cover directory creation, file copying, file echoing, shell execution, link creation, directory-pool management, template lookup, error reporting, owner lookup, and `$AUTO` directory selection.

Control flow and integration: grammar actions call these functions as they parse template statements. `uss_vol.c` uses the mountpoint age constants and owner lookup. `uss.c` calls `uss_procs_FindAndOpen()` for the template and `uss_procs_Exec()` for bulk `exec`.

State and persistence: the API is stateless on paper, but the implementation is controlled by global dry-run, overwrite, parser line, syntax error, account creator, directory-pool, and cleanup-stack state.

Risks and test signals: callers pass all values as strings, so mode, owner, path, and command validation lives in the implementation. Tests should cover grammar-to-function argument mapping, especially path ordering for `SetLink()` and directory ACL arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_procs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_ptserver.c -->
# sources/distributed-fs/openafs/src/uss/uss_ptserver.c

Purpose: `uss_ptserver.c` wraps Protection Server operations for `uss`: initialize the PTS client, create a user entry with optional desired UID, delete a user entry, and translate a name to UID.

Important APIs and functions: `InitThisModule()` lazily calls `pr_Initialize()` with authenticated security, config directory, and cell. `uss_ptserver_AddUser()` calls `pr_CreateUser()`, handles existing name or ID cases, verifies name-to-ID mappings with `pr_SNameToId()`, and writes the resulting ID string to the caller buffer. `uss_ptserver_DelUser()` calls `pr_Delete()` and treats missing entries as warning/success. `uss_ptserver_XlateUser()` translates a name and rejects `ANONYMOUSID`.

Control flow: add initializes PTS, handles dry-run by only filling the requested UID string, then creates or reconciles an existing entry. Delete and translate initialize lazily and then perform one server operation.

State and persistence: module state is just `initDone`; persistent effects are Protection Database entries. It reads global `uss_DesiredUID`, `uss_DryRun`, `uss_Cell`, `uss_ConfDir`, verbosity, and program name.

Dependencies and integration: `uss.c` uses this before KAS creation during add and after KAS deletion during delete; `SaveRestoreInfo()` uses translation before volume deletion. Depends on OpenAFS PTS client libraries and error tables.

Risks: add is permissive for preexisting users if the mapping matches, which can mask partial previous runs. Dry-run with no desired UID records `0`, so downstream dry-run paths may see an unrealistic UID. Test signals should include PREXIST, PRIDEXIST with matching/mismatched mappings, missing delete, ANONYMOUSID translation, and PTS initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_ptserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_ptserver.h -->
# sources/distributed-fs/openafs/src/uss/uss_ptserver.h

Purpose: `uss_ptserver.h` declares the Protection Server interface for `uss`.

Important APIs: `uss_ptserver_AddUser()` creates or reconciles a PTS user and returns its UID string; `uss_ptserver_DelUser()` removes a PTS name; `uss_ptserver_XlateUser()` translates a name to numeric AFS UID.

Control flow and integration: add flow calls PTS creation before KAS creation and template parsing. delete flow translates before volume deletion and removes the PTS entry last.

State and persistence: implementation is lazily initialized and mutates the Protection Database unless dry-run is active for add/delete.

Risks and test signals: UID is returned through a caller-provided `char *`, so the caller must size it correctly. Tests should check ID collision semantics and delete idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_ptserver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_vol.c -->
# sources/distributed-fs/openafs/src/uss/uss_vol.c

Purpose: `uss_vol.c` handles volume and VLDB operations for `uss`: resolving servers and partitions, creating and deleting user volumes, mounting volumes, setting quota/owner/temporary ACL, and discovering volume/server/partition metadata from an existing mount point.

Important APIs and functions: `uss_vol_GetServer()` parses dotted IPv4 or resolves hostnames. `uss_vol_GetPartitionID()` parses numeric, `a`, `vicepa`, or `/vicepa` forms. `uss_vol_CreateVol()` is the main template action for volume creation and setup. `uss_vol_DeleteVol()` calls `UV_DeleteVolume()`. `uss_vol_GetVolInfoFromMountPoint()` reads cache-manager volume status and VLDB entry data into `uss_common` globals. Internal `InitThisModule()` initializes Rx, config, security, VLDB server connections, Ubik client, and `cstruct` for volser helpers. Additional helpers translate host/partition IDs, detect double mount points, and support old/new VLDB entry APIs.

Control flow: create applies command-line overrides over template server/partition/mountpoint values, resolves server/partition, initializes VLDB access, calls `UV_CreateVolume()`, handles existing volume with overwrite prompting and double-mount detection, creates the mountpoint symlink, sets disk quota, records `uss_MountPoint`, chowns mountpoint, pushes final ACL state, and grants temporary creator ACL. Delete initializes VLDB and deletes by server/partition/volume ID. Mountpoint info fetches status through `uss_fs_GetVolStat()`, tolerates missing/unreachable mountpoints by zeroing metadata, then validates VLDB read/write single-server placement.

State and persistence: persistent effects include volume creation/deletion in VLDB/volserver, symlink mountpoints, quota, ownership, and ACLs. Module state includes VLDB connection arrays, `uconn_vldbP`, `NoAuthFlag`, and `initDone`; it also writes volume metadata globals.

Dependencies and integration: depends on Rx, Ubik, VLDB, volser, cache-manager pioctls, host utilities, `uss_acl`, `uss_fs`, and `uss_procs`.

Risks: create is not transactional; failures after `UV_CreateVolume()` can leave volumes or mountpoints behind. Existing-volume overwrite prompts block noninteractive runs unless `-overwrite` is set. Mountpoint symlink creation is implemented directly instead of via `uss_fs_MkMountPoint()`. Fixed buffers and `strcpy()`/`sprintf()` are common. Test signals should cover server/partition parsing, VLDB init without tokens, existing volume/mountpoint paths, dry-run, quota/ACL failures after volume creation, and non-RW or multi-server VLDB entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_vol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_vol.h -->
# sources/distributed-fs/openafs/src/uss/uss_vol.h

Purpose: `uss_vol.h` declares volume-management operations used by the `uss` parser and delete workflow.

Important APIs: `uss_vol_GetServer()` resolves a server string to an address; `uss_vol_GetPartitionID()` converts partition names to numeric IDs; `uss_vol_CreateVol()` creates, mounts, quotas, owns, and ACL-stages a user volume; `uss_vol_DeleteVol()` deletes a known volume; `uss_vol_GetVolInfoFromMountPoint()` populates global volume/server/partition metadata from a mount point.

Control flow and integration: template grammar calls `CreateVol()`. Delete flow calls `GetVolInfoFromMountPoint()` before optional deletion. Server/partition helpers support template overrides and validation.

State and persistence: APIs operate through global `uss_common` state and AFS VLDB/volserver/cache-manager side effects.

Risks and test signals: create accepts all parameters as strings and may perform several irreversible operations. Tests should validate parsing helpers separately from integration tests that require a live AFS cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/uss/uss_vol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/Makefile.in -->
# sources/distributed-fs/openafs/src/util/Makefile.in

Purpose: this makefile builds and installs OpenAFS utility libraries, exported utility headers, the `sys` program, generated `dirpath.h`, and utility tests.

Important targets and variables: `LT_objs` aggregates utility object files such as `base64`, time parsing, host parsing, logging, directory paths, atom list, linear hash, pthread lock, and tabular output. `all` builds headers, `util.a`, `libafsutil.a`, PIC/static variants, shared libtool libraries, `sys`, and tests. Install and dest targets copy headers and libraries into configured trees. `dirpath.h` is generated from `dirpath.hin` with configured installation paths. `check-splint` runs static analysis over key utility sources.

Control flow: dependency targets install generated/source headers under `${TOP_INCDIR}/afs`. Library targets use OpenAFS libtool macros for LWP, PIC, and shared builds. `test` delegates to the `test` subdirectory after library/header creation.

State and persistence: build outputs include generated headers, `.lo`/`.o`, archives, shared libraries, `sys`, and installed copies under build/dest prefixes.

Dependencies and integration: includes central OpenAFS config makefiles, LWP tooling, roken, thread libraries, `liboafs_opr`, version generation, and optional regex object.

Risks: header install lists and object lists must stay synchronized with source additions. `dirpath.h` generation uses `sed` with a quote delimiter and assumes configured paths do not contain that delimiter. Test signals include `make all`, `make test`, `make install DESTDIR=...`, `buildtools`, clean idempotence, and splint coverage when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afs_atomlist.c -->
# sources/distributed-fs/openafs/src/util/afs_atomlist.c

Purpose: `afs_atomlist.c` implements a block-backed fixed-size allocator for small objects. It reduces allocator fragmentation by allocating large blocks, splitting them into aligned atoms, and maintaining a free list.

Important APIs and functions: `afs_atomlist_create()` validates and aligns atom/block sizes, stores caller-provided allocation hooks, and initializes lists. `afs_atomlist_get()` allocates a new block when the free list is empty, chains the block into `block_head`, threads its atoms into `atom_head`, and returns one atom. `afs_atomlist_put()` returns an atom to the free list. `afs_atomlist_destroy()` frees every allocated block and the allocator object.

Control flow: block layout stores the next-block pointer after all usable atoms, using leftover block space when possible. Atom size is rounded up to pointer size and pointer alignment. If block size cannot hold at least one atom plus a next-block pointer, creation fails.

State and persistence: allocator state is in `struct afs_atomlist`: atom size, block size, atoms per block, allocation hooks, atom free-list head, and block list head. No persistent external state exists.

Dependencies and integration: used by `afs_lhash.c` to allocate bucket records. Caller provides memory allocation functions and locking if needed.

Risks: no internal locking, no validation that returned atoms belong to this allocator, and no double-free detection. Allocation failure during `get` returns NULL. Test signals should cover alignment, minimal block-size rejection, block growth, atom reuse after put, destruction with outstanding atoms, and custom allocator failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afs_atomlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afs_atomlist.h -->
# sources/distributed-fs/openafs/src/util/afs_atomlist.h

Purpose: `afs_atomlist.h` declares the fixed-size atom allocator abstraction used by utility code needing low-fragmentation allocation.

Important APIs: opaque `afs_atomlist`; `afs_atomlist_create(atom_size, block_size, allocate, deallocate)`; `afs_atomlist_destroy()`; `afs_atomlist_get()`; and `afs_atomlist_put()`.

Control flow and integration: the header documents caller-supplied allocation hooks and states that destroying the allocator frees all blocks, including atoms not returned individually. It explicitly assigns locking responsibility to callers.

State and persistence: the type is opaque, so callers cannot access block/free-list internals. No persistent state beyond process memory.

Risks and test signals: callers must not return foreign or already-returned atoms. Tests should verify opaque ABI usage, allocation-hook invocation counts, and behavior under failed allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afs_atomlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afs_lhash.c -->
# sources/distributed-fs/openafs/src/util/afs_lhash.c

Purpose: `afs_lhash.c` implements a linear hash table that expands incrementally instead of rehashing the entire table at once. It is intended for unknown-size collections with bounded average chain length and caller-managed keys.

Important APIs and functions: `afs_lhash_create()` initializes table state and a bucket allocator. `afs_lhash_enter()` inserts a key/data pair and triggers `afs_lhash_expand()` when load exceeds five records per logical bucket. `afs_lhash_search()` finds and moves a bucket to the head of its chain; `afs_lhash_rosearch()` searches without mutation; `afs_lhash_remove()` unlinks and recycles a bucket; `afs_lhash_iter()` visits entries; `afs_lhash_stat()` reports chain and operation counters; `afs_lhash_destroy()` frees table and buckets. Internal `afs_lhash_address()` implements Larson-style addressing with split pointer `p` and `maxp`; `afs_lhash_accomodate()` grows the physical bucket-pointer array.

Control flow: expansion splits bucket `p` into `p + maxp`, advances `p`, doubles `maxp` at the end of a round, increments logical table size, and relocates only records from the split bucket. Physical table allocation grows in fixed chunks around 1 KiB.

State and persistence: state includes equal callback, allocator hooks, split state, record count, logical/physical table sizes, bucket array, atomlist bucket allocator, and statistics counters. No external persistence.

Dependencies and integration: depends on `afs_atomlist` for bucket storage and optional user-space assertions for invariants. Callers own element lifetime and locking.

Risks: duplicate entries are allowed. If `afs_atomlist_create()` fails in create, an assertion catches it only when assertions are enabled; otherwise a NULL bucket allocator may later crash. No locking. Key quality is caller responsibility. Test signals should cover insert/search/remove, duplicate keys, incremental expansion, read-only search preserving order, stat counters, allocator failure, and invariant builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afs_lhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afs_lhash.h -->
# sources/distributed-fs/openafs/src/util/afs_lhash.h

Purpose: `afs_lhash.h` declares the linear hash table abstraction and its statistics structure.

Important APIs and types: opaque `afs_lhash`; `struct afs_lhash_stat` with min/max chain length, bucket/record counts, and cumulative search/remove counters. Public functions create/destroy, iterate, search, read-only search, remove, enter, and collect stats.

Control flow and integration: callers provide an equality predicate, allocation hooks, and precomputed unsigned keys. The header documents incremental growth and makes clear that duplicate entries are not rejected.

State and persistence: state is opaque and process-local. Caller owns data objects and synchronization.

Risks and test signals: misuse risks include poor key distribution, duplicate entries, freeing data before removal, or concurrent mutation without locks. Tests should validate API contracts and stats after representative workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afs_lhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afsutil.h -->
# sources/distributed-fs/openafs/src/util/afsutil.h

Purpose: `afsutil.h` is the broad utility umbrella header for OpenAFS user-space utilities. It provides common includes, address sentinel constants, logging option types/macros, platform shims, base encoding typedefs, and pulls in `afsutil_prototypes.h`.

Important APIs and types: `AFS_IPINVALID` and `AFS_IPINVALIDIGNORE` identify invalid or absent address parsing results. `enum logDest`, `enum logRotateStyle`, and `struct logOptions` configure server logging to files or syslog. Logging APIs include `vFSLog()`, `FSLog()`, `OpenLog()`, `ReOpenLog()`, signal setup, log close, and getters. Macros `ViceLog`, `vViceLog`, and `ViceLogThenPanic` gate messages on `LogLevel`. `b32_string_t` and `lb64_string_t` define buffer sizes for encoders.

Control flow and integration: consumers include this header to get utility prototypes and platform differences in one place. Windows builds receive winsock initialization declarations and `setlinebuf` emulation; builds without POSIX regex get `re_comp`/`re_exec` declarations.

State and persistence: exposes `LogLevel` for logging macros and config structs for log destination, rotation, and filenames. Persistent effects are log files/syslog writes in implementation files outside this item.

Risks and test signals: as an umbrella header, include-order conflicts are possible. Macros evaluate logging arguments only when enabled, but panic macro depends on `osi_Panic`. Tests should compile representative Unix and Windows configurations, log rotation modes, and consumers of base string typedefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afsutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afsutil_prototypes.h -->
# sources/distributed-fs/openafs/src/util/afsutil_prototypes.h

Purpose: `afsutil_prototypes.h` centralizes prototypes for OpenAFS utility-library functions so `afsutil.h` consumers can share a consistent declaration set.

Important APIs: declarations cover base32/base64/flipbase64 conversion, directory path construction, NT error mapping, alternate exec lookup, filepath normalization, host parsing and address formatting, HP-UX portability functions, relative and periodic time parsing, logging, tabular output, UUID handling, partition parsing, and numeric parsing helpers.

Control flow and integration: the file is organized by implementation module comments. Conditional blocks expose pthread, Windows, HP-UX, non-kernel, and non-NT functions according to build configuration.

State and persistence: this header defines no storage. Declared functions can affect logs, paths, UUIDs, and parsing outputs depending on their implementation.

Risks and test signals: duplicate base32 declarations appear under both `base32.c` and `flipbase64.c` comments. Prototype drift is a maintenance risk because many modules are listed manually. Test signals include full util-library compilation with strict prototypes across platform macros and consumers that include both specific headers and `afsutil.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/afsutil_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/base32.c -->
# sources/distributed-fs/openafs/src/util/base32.c

Purpose: `base32.c` converts signed `int` values to and from a compact base-32 string using digits and uppercase letters.

Important APIs: `int_to_base32(b32_string_t s, int a)` writes a NUL-terminated representation to the caller-supplied eight-byte buffer and returns it. `base32_to_int(char *s)` parses a base-32 string back to an integer.

Control flow: encoding special-cases zero, handles the top two bits separately, then emits five-bit groups from the highest nonzero group down. Decoding shifts the accumulated result left five bits and adds each digit value, mapping `0`-`9` to 0-9 and anything above `9` as uppercase letters starting at 10.

State and persistence: only static translation string `c_xlate` is used; no persistent effects.

Dependencies and integration: included via `afsutil.h`; buffer type is declared there. Used by utility consumers needing compact IDs.

Risks: decoder does not validate input range or lowercase; characters such as punctuation above `'9'` produce unintended values. Signed `int` bit operations depend on implementation details for negative values, though masking uses unsigned temporaries. Test signals should include zero, high-bit values, round trips, invalid characters, lowercase input, and maximum output length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/base32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/base64.c -->
# sources/distributed-fs/openafs/src/util/base64.c

Purpose: `base64.c` provides a compact integer base-64 encoder/decoder for SGI XFS IOPS builds only, guarded by `AFS_SGI_XFS_IOPS_ENV`.

Important APIs: under the guard, `int_to_base64(b64_string_t s, int a)` emits a string using `+`, `,`, digits, uppercase, and lowercase letters. `base64_to_int(char *s)` decodes that alphabet back into an `int`.

Control flow: encoding special-cases zero, handles the top two bits, then emits six-bit groups from the highest nonzero group down. Decoding maps characters before `'0'` relative to `'+'`, digits to 2-11, uppercase to 12-37, and lowercase to 38-63.

State and persistence: static alphabet only; no persistent state.

Dependencies and integration: compiled only for the SGI/XFS environment. `Makefile.in` includes `base64.lo` in RPC utility objects.

Risks: outside the guard no functions are compiled, so prototypes must match platform build choices. Decoder has no validation and includes an unused local pointer. Test signals should compile both guarded and unguarded configurations, round-trip representative values, and reject or document invalid-character behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/base64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/dirent_nt.h -->
# sources/distributed-fs/openafs/src/util/dirent_nt.h

Purpose: `dirent_nt.h` supplies a minimal Windows-compatible `DIR` and `struct dirent` interface for OpenAFS utility code that expects POSIX directory iteration.

Important APIs and types: `struct dirent` contains only `char *d_name`. `DIR` wraps a Windows search `HANDLE`, `WIN32_FIND_DATA`, cached current dirent, and `first` flag. Prototypes are `opendir()`, `closedir()`, and `readdir()`.

Control flow and integration: consumers can compile directory traversal code against POSIX-like names while the Windows implementation maps to FindFirst/FindNext APIs in a companion source file.

State and persistence: `DIR` instances store the live Windows handle and current result. No global state is declared here.

Risks and test signals: this is a deliberately partial dirent API; fields such as inode, type, and record length are absent. Tests should cover first-entry behavior, close-after-open, missing directories, wildcard/path handling, and consumers that only rely on `d_name`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/util/dirent_nt.h -->
