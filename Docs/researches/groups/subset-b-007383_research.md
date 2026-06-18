# subset-b-007383 Research

Grouped research for the Hadoop common configuration and Windows utility files in this work item. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/resources/core-default.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/resources/core-default.xml

## Purpose
`core-default.xml` is the authoritative built-in default configuration resource for Hadoop Common. It defines 488 `<property>` entries loaded before site-specific overrides such as `core-site.xml`, and its header explicitly instructs operators to override values in `core-site.xml` rather than editing this file directly. The file spans common daemon/client behavior: global temp paths and HTTP filters, service authorization, Kerberos and group mapping, credential redaction/provider defaults, file system implementation registration, S3A/Azure/ADL/GCS/OBS connector defaults, IPC tuning, proxy impersonation, network topology, local/FTP/TFile/SequenceFile settings, HTTP authentication/CORS, HA fencing and ZK failover, SSL, crypto/KMS, registry, shell safety, tracing, metrics, tags, hostname resolution, Prometheus, and space-usage behavior.

## Important APIs, Types, And Properties
The public API is Hadoop's XML configuration schema: a `<configuration>` root with repeated `<property>` entries containing `<name>`, optional `<value>`, optional `<description>`, and occasional metadata. The highest-impact property families are:

- Security and identity: `hadoop.security.authentication`, `hadoop.security.authorization`, service ACL defaults, `hadoop.security.group.mapping`, group cache/negative-cache/background reload controls, LDAP group mapping settings, `hadoop.security.auth_to_local`, `hadoop.security.auth_to_local.mechanism`, Kerberos kinit/relogin/keytab renewal, token files, sensitive-key redaction regexes, credential provider paths, and clear-text credential fallback.
- Filesystems and implementations: `fs.defaultFS`, `fs.AbstractFileSystem.*.impl`, `fs.*.impl`, ViewFS overload targets for hdfs/s3a/ofs/o3fs/ftp/webhdfs/swebhdfs/file/abfs/abfss/wasb/oss/http/https/gs, FTP parameters, local file checksum and shutdown-hook settings, trash/protected-directory settings, and `fs.creation.parallel.count`.
- Object stores: S3A credentials/provider chain, assumed-role and delegation token controls, connection pools/timeouts/retry/backoff, multipart/upload buffering, committers, S3 Select, checksums/change detection/SSL/auditing; Azure WASB/ABFS and ADL auth/SAS/authorization/buffer/readahead settings; Google Cloud Storage auth, working dir, rewrite, bucket delete guard, conflict check, fadvise, gzip handling, buffering, and seek controls; OBS scheme registration.
- IPC/RPC: async call limits, idle scan/kill thresholds, connect and timeout retry knobs, TCP_NODELAY/low-latency, request/response maximums, server queue/listen/read threads, slow RPC logging, per-port and fallback call queue/scheduler/identity/cost-provider properties, FairCallQueue and DecayRpcScheduler weights/thresholds/backoff, and weighted time cost multipliers.
- Web/observability/HA: HTTP auth token/secret/cookie/SPNEGO settings, endpoint whitelists, CORS, static web user, `/logs`, JMX NaN filtering, Prometheus endpoint, SSL keystore factory/protocol/hostname verifier, HA fencing and ZK failover, registry ZooKeeper defaults, caller context audit metadata, RPC/user-group percentile metrics, and HTrace placeholders.

## Control Flow
There is no imperative control flow in the file itself. Runtime flow is Hadoop `Configuration` resource loading: defaults are parsed from this classpath resource, variable substitutions such as `${hadoop.tmp.dir}`, `${user.name}`, `${user.home}`, and `${env.LOCAL_DIRS:-...}` are resolved by configuration consumers, then site files or programmatic settings override defaults. Many property descriptions define secondary runtime branches, for example:

- `hadoop.security.group.mapping` selects JNI group lookup with shell fallback by default; LDAP/composite providers are activated only when configured.
- `hadoop.rpc.protection`, SASL resolver, and SIMPLE fallback settings steer secure RPC negotiation.
- `fs.SCHEME.impl` and `fs.AbstractFileSystem.SCHEME.impl` values determine which Java filesystem implementation is instantiated for a URI.
- S3A upload settings choose disk/heap/off-heap buffering and bound thread-pool behavior; committer settings determine output commit semantics.
- IPC per-port properties override fallback scheduler/callqueue properties, so a port-specific key can change call admission independently from global defaults.
- HA and registry ZooKeeper settings drive session, ACL, auth, and retry behavior in components that opt into them.

## State And Persistence Behavior
The XML does not persist runtime state, but it defines defaults for components that do. Examples include local temp directories under `hadoop.tmp.dir`, S3A disk upload buffers, Azure/ABFS buffers, SequenceFile merge directories, trash checkpoints, KMS encrypted key caches, group and UID caches, filesystem instance caches, ZooKeeper znodes for failover/registry, HTTP auth cookies and signature secrets, local checksum sidecar files, caller-context audit records, metrics quantile state, and object-store multipart uploads or commit metadata. Several settings intentionally prevent destructive persistence side effects by default: trash is disabled unless configured, protected directories are empty by default, S3A multipart purge is deprecated and disabled, GCS bucket deletion is disabled, and secure ZooKeeper/registry modes are off unless enabled.

## Dependencies And Integration Points
This resource integrates broadly with Hadoop Common, HDFS, YARN, MapReduce, and cloud connector modules. Class-name values reference Hadoop Java classes such as `org.apache.hadoop.security.JniBasedUnixGroupsMappingWithFallback`, `org.apache.hadoop.fs.s3a.S3AFileSystem`, `org.apache.hadoop.fs.azurebfs.AzureBlobFileSystem`, `org.apache.hadoop.fs.gs.GoogleHadoopFileSystem`, IPC schedulers, crypto codecs, SSL factories, topology mappers, and filesystem abstractions. External dependencies implied by defaults include Kerberos/kinit, LDAP/JNDI, AWS SDK and STS, Azure storage/AAD/SAS services, Google Cloud Storage credentials, ZooKeeper, OpenSSL, JCE/BouncyCastle, native compression and erasure coding libraries, Jetty HTTP, and OS DNS/user/group facilities.

## Risks
The file carries high configuration blast radius because defaults apply cluster-wide unless overridden. Security risks include `simple` authentication and service authorization disabled by default, permissive ZooKeeper ACL defaults, anonymous simple HTTP auth, HTTP `/logs` enabled, clear-text credential fallback enabled, empty credential provider paths, and operator mistakes around CORS wildcards, SPNEGO endpoint whitelists, LDAP passwords, object-store secrets, or SSL hostname verifier values. Availability/performance risks include overly large IPC message limits, unbounded LDAP/shell group lookup behavior when timeouts are zero or negative, S3A/Azure/GCS buffer/thread settings that can consume local disk or memory, aggressive or lax HA/ZK timeouts, and object-store consistency settings that may be incompatible with third-party stores. The XML also contains typo-like metadata tags (`<decription>` for two ZooKeeper SSL descriptions), so tools expecting only `<description>` may miss those descriptions.

## Test Signals
Useful tests are configuration-resource parsing tests, XML schema/well-formedness checks, duplicate-key checks, property documentation generation, redaction tests for `hadoop.security.sensitive-config-keys`, classloading tests for every default implementation class in assembled distributions, and integration tests that instantiate representative schemes (`file`, `hdfs`, `viewfs`, `s3a`, `abfs`, `wasb`, `adl`, `gs`, `obs`) when their modules are present. Security test signals include Kerberos/SPNEGO negotiation, LDAP group lookup/failover, credential provider resolution, sensitive config logging, ZooKeeper ACL/auth parsing, and object-store secret redaction. Performance/behavior tests should exercise IPC queue fallback vs per-port overrides, S3A retry/upload/committer settings, trash/protected-directory behavior, and failure modes for missing optional native crypto/compression libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/resources/core-default.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chmod.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chmod.c

## Purpose
`chmod.c` implements the Windows `winutils chmod` subcommand. It parses octal and symbolic Unix-style permission modes, optionally recurses through directory trees, converts each target path to a Windows long-path form, computes the resulting Unix permission mask, and delegates actual ACL mutation to shared winutils permission helpers.

## Important APIs, Types, And Functions
The exported command entry point is `int Chmod(int argc, wchar_t *argv[])`, with `ChmodUsage()` printing supported syntax. Internal enums model symbolic mode grammar: `CHMOD_WHO_*` maps user/group/other/all bit fields, `CHMOD_OP_*` models `+`, `-`, and `=`, and `CHMOD_PERM_*` models `r`, `w`, `x`, and capital `X`. `MODE_CHANGE_ACTION` is a linked-list node holding one parsed symbolic action (`who`, `op`, `perm`, `ref`, `next_action`). Core helpers are `ParseCommandLineArguments`, `ParseOctalMode`, `ParseMode`, `ComputeNewMode`, `ConvertActionsToMask`, `ChangeFileModeByActions`, `ChangeFileMode`, `ChangeFileModeRecursively`, and `FreeActions`.

## Control Flow
`Chmod` validates arguments, parses either `[OPTION] OCTAL-MODE FILE` or `[OPTION] MODE FILE`, converts the target with `ConvertToLongPath`, then calls either `ChangeFileMode` or `ChangeFileModeRecursively`. `ParseCommandLineArguments` accepts only three or four arguments; the four-argument path must use `-R`, and recursion is enabled only when `GetFileInformationByName(..., followLink=FALSE)` and `IsDirFileInfo` identify the input as a directory. Mode parsing tries octal first; four-digit octal modes ignore the leading setuid/setgid/sticky digit because Windows has no direct equivalent.

Symbolic mode parsing is a state machine over `[ugoa]*([-+=]([rwxX]*|[ugo]))+` clauses. Each completed action is appended to a linked list; missing `who` defaults to all, and chained operations without a comma inherit the last `who`. `ComputeNewMode` applies literal permissions or references another class's bits, expands capital `X` only for directories or files with an existing execute bit, and then applies plus/minus/equal. Recursive chmod walks children with `FindFirstFile`/`FindNextFileW`, skips `.` and `..`, converts child paths to long-path form, recurses into non-symlink directories, and applies the change after children.

## State And Persistence Behavior
The command persists only filesystem ACL/mode changes through `ChangeFileModeByMask`; all parser state is temporary heap allocation via `LocalAlloc`. Recursive mode can change many descendants before failing on a later entry, and there is no rollback. Symlinks and junctions are not traversed as directories by the documented recursion rule; symlink targets are not followed by permission discovery calls using `followLink=FALSE`.

## Dependencies And Integration Points
This file depends on `winutils.h` for path conversion, file information, directory/symlink checks, Unix mask constants, owner/permission lookup, ACL mutation, error reporting, and Windows headers. It integrates with the main winutils command dispatcher through `Chmod`, and with Hadoop Java code that shells out to `winutils.exe chmod` on Windows for POSIX-like permission behavior.

## Risks
Recursive chmod is partial on failure and can leave a tree in mixed permission state. The parser accepts only a subset of POSIX chmod semantics and intentionally drops special mode bits, so parity with Unix chmod is approximate. In `ParseMode`, failed parsing calls `FreeActions(*pActions)` but does not clear the caller's pointer, so a caller that later frees again could double-free if it reused the same pointer after failure; the current `Chmod` path returns immediately on parse failure, limiting practical exposure. `FindFirstFile` handles are not closed in `ChangeFileModeRecursively`, which can leak handles during large recursive walks. Symbolic `X` depends on mode bits returned by `FindFileOwnerAndPermission`, so incorrect Windows-to-Unix mapping propagates into recursive behavior.

## Test Signals
Tests should cover octal modes with three and four digits, invalid octal values, symbolic clauses with comma and inherited `who`, references such as `g=u`, capital `X` on files vs directories, `-R` on files and directories, symlink/junction non-traversal, long paths, permission-denied failures, and partial-recursion behavior. Windows integration tests should verify the resulting ACLs through `FindFileOwnerAndPermission` and Hadoop filesystem permission APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chown.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chown.c

## Purpose
`chown.c` implements the Windows `winutils chown` subcommand. It parses Hadoop's Unix-like owner/group argument form and delegates the actual owner/group ACL update to the shared `ChownImpl` helper.

## Important APIs, Types, And Functions
The exported entry point is `int Chown(int argc, wchar_t *argv[])`; `ChownUsage()` documents `OWNER[:GROUP] FILE`. The key internal values are `ownerInfo`, `pathName`, `colonPos`, and optional heap-allocated `userName` and `groupName`. It uses `StringCchCopyNW` for bounded copying, `LocalAlloc`/`LocalFree` for temporary names, and `ChownImpl(userName, groupName, pathName)` from the common winutils layer.

## Control Flow
`Chown` requires at least three arguments and uses `argv[1]` as the owner/group spec and `argv[2]` as the path. If a colon exists, text before the colon becomes `userName` unless empty, and text after the colon becomes `groupName` unless empty. If there is no colon, the full string becomes `userName`. Empty owner and empty group is a no-op success, matching cases such as `:`. Otherwise, the command calls `ChownImpl`; a nonzero return keeps the process exit status as failure.

## State And Persistence Behavior
The file itself holds no persistent state. Filesystem ownership or group ownership is changed by `ChownImpl`, likely through Windows security descriptors and owner/group SIDs declared in `winutils.h`. Temporary strings are freed before return. Unlike Unix, `user:` does not change the group to the user's login group; the usage text documents that Windows has no such login-group concept and leaves group unchanged.

## Dependencies And Integration Points
`chown.c` depends on `winutils.h` for Windows headers, string/error helpers, and `ChownImpl`. It is invoked through `winutils.exe chown` and supports Hadoop components that need to mimic POSIX ownership operations on Windows local files.

## Risks
The code ignores extra arguments beyond `argv[2]` because it checks only `argc >= 3`; callers expecting strict command-line validation may miss malformed invocations. `StringCchCopyNW` is called with destination lengths that include the null terminator, but the group/no-colon copy passes the full allocated length as the character count, which is safe because the source is null terminated yet slightly imprecise. Owner/group names depend on Windows account resolution elsewhere, so domain/local account ambiguity and privilege requirements are primary operational risks. Partial owner-only or group-only changes must be validated in `ChownImpl`.

## Test Signals
Tests should cover `owner file`, `owner:group file`, `owner: file`, `:group file`, `: file`, missing arguments, extra arguments, Unicode/domain-qualified account names, nonexistent users/groups, insufficient privileges, and ACL verification after owner-only and group-only changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/chown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/client.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/client.c

## Purpose
`client.c` is the client-side RPC shim for privileged Hadoop Windows utility service operations. It prepares a secure local RPC binding to `hadoopwinutilsvc`, wraps each IDL-defined service call, translates RPC exceptions into `DWORD` error codes, transfers returned kernel handles, and logs diagnostics when a debugger is attached.

## Important APIs, Types, And Functions
The central setup function is `PrepareRpcBindingHandle(RPC_BINDING_HANDLE*)`. It composes a binding from `SVCBINDING` and `SVCNAME` generated by `hadoopwinutilsvc.idl`, creates a LocalSystem SID, and calls `RpcBindingSetAuthInfoEx` with packet privacy, WinNT authentication, mutual auth/local machine hint QoS, dynamic identity tracking, and a LocalSystem SID. RPC wrapper functions include `RpcCall_WinutilsKillTask`, `RpcCall_WinutilsMkDir`, `RpcCall_WinutilsChown`, `RpcCall_WinutilsChmod`, `RpcCall_WinutilsMoveFile`, `RpcCall_WinutilsCreateFile`, `RpcCall_WinutilsDeletePath`, and `RpcCall_TaskCreateAsUser`. Request/response structures come from `hadoopwinutilsvc_h.h`.

## Control Flow
Every wrapper follows the same pattern: prepare the binding, zero-initialize an IDL request structure, populate string/scalar fields, execute the service method inside `RpcTryExcept`, map `RpcExceptionCode()` to the return code on exception, free the binding, free MIDL-allocated responses, log the outcome, and return a `DWORD`. Operations with responses copy returned `LONG_PTR` handles into output `HANDLE*` parameters after `ERROR_SUCCESS`. `RpcCall_TaskCreateAsUser` and `RpcCall_WinutilsCreateFile` also pass the current process ID so the service can duplicate handles back into the caller process.

## State And Persistence Behavior
The client does not persist data itself. It creates transient RPC bindings, allocates a LocalSystem SID and RPC string binding, and frees them after each call. The service-side operations persist filesystem changes, process creation state, job/task termination, or file deletion/move/copy effects. Returned process, thread, stdio, and file handles become caller-owned resources after success.

## Dependencies And Integration Points
Dependencies include Windows RPC (`Rpcrt4.lib`), advanced security APIs (`advapi32.lib`), service headers (`Winsvc.h`), the generated `hadoopwinutilsvc_h.h`, and shared logging/time helpers from `winutils.h`. The file is tightly coupled to `hadoopwinutilsvc.idl`: request fields, endpoint names, and operation names must match generated stubs. It integrates with higher-level winutils commands that need the service for privileged create/delete/chown/chmod/process operations.

## Risks
The RPC security setup is critical: weakening packet privacy, mutual auth, or the LocalSystem target SID would expose privileged operations over the local RPC endpoint. Output pointer handling has a bug in `RpcCall_WinutilsDeletePath`: `pDeleted = FALSE;` overwrites the local pointer variable instead of `*pDeleted`, so a caller passing a valid pointer may later dereference null in logging or skip initialization. Most wrappers do not validate output pointer arguments before assignment. Debug logging of owner, group, file paths, command lines, or errors can expose sensitive paths and process commands when a debugger is present. Per-call binding setup is simple but adds overhead for frequent operations.

## Test Signals
Tests should mock or run the service endpoint and cover successful and failing calls for every wrapper, RPC endpoint unavailable, authentication failure, exception paths, handle transfer to the current process, response memory freeing, null output pointer handling, and security settings on the binding. A regression test should specifically detect that `RpcCall_WinutilsDeletePath` initializes `*pDeleted` rather than corrupting the pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/config.cpp -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/config.cpp

## Purpose
`config.cpp` provides Windows winutils helpers for locating configuration files relative to the running module and reading a single Hadoop XML configuration value by property name using MSXML6.

## Important APIs, Types, And Functions
`BuildPathRelativeToModule(relativePath, len, buffer)` builds an absolute path from the executable's drive and directory plus a caller-supplied relative path. `GetConfigValue(relativePath, keyName, len, value)` resolves the XML path relative to the module and delegates to `GetConfigValueFromXmlFile`. `GetConfigValueFromXmlFile(xmlFile, keyName, outLen, outValue)` initializes COM, loads an MSXML DOM document, builds an XPath of the form `//configuration/property[name='KEY']/value/text()`, selects the first matching value node, allocates a wide string with `LocalAlloc`, copies the BSTR content, and returns length plus caller-owned value. The `ERROR_CHECK_HRESULT_DONE` macro logs and exits on HRESULT failures.

## Control Flow
The relative-path helper calls `GetModuleFileName`, splits drive/path with `_wsplitpath_s`, then formats the final path with `StringCbPrintf`. The config getter initializes outputs to empty, resolves the full path, and logs when a value is found. The XML parser calls `CoInitialize`, creates `MSXML2::DOMDocument60`, disables async validation and external resolution, loads the XML file, selects the XPath, copies the value if present, catches `_com_error`, and calls `CoUninitialize` if COM was initialized.

## State And Persistence Behavior
The module has no persistent state. It allocates returned configuration values with `LocalAlloc`; callers must free them with `LocalFree`. COM initialization is per-call. It reads but does not modify XML. When a key is absent, it returns `ERROR_SUCCESS` with `*outLen == 0` and `*outValue == NULL`.

## Dependencies And Integration Points
Dependencies include `winutils.h`, Windows path/string APIs, COM, and `#import "msxml6.dll"` for MSXML smart pointers. It is used by Windows service or utility code that needs Hadoop XML settings from files deployed next to the executable. It assumes Hadoop XML uses the standard `<configuration><property><name>...` layout also used by `core-default.xml` and site files.

## Risks
`BuildPathRelativeToModule` treats any nonzero `GetLastError()` after `GetModuleFileName` as failure even though `GetLastError` is not reliable on success unless the return value indicates truncation; stale last-error state could cause false failures. The XPath directly interpolates `keyName`, so property names containing XPath quote/control syntax could break selection; Hadoop property names are normally safe. `StringCbPrintf` receives a character count from callers but expects bytes, so buffer-size semantics are inconsistent in `BuildPathRelativeToModule`; the current `MAX_PATH` use leaves room, but future callers could understate/overstate capacity. XML external resolution is disabled, reducing XXE risk, but parsing arbitrary XML still depends on MSXML behavior. The function only returns the first matching property value.

## Test Signals
Tests should cover module-relative path construction, absent keys, empty values, duplicate keys, malformed XML, missing XML files, property names with punctuation, Unicode values, COM initialization failures, and caller freeing. Static analysis should flag the `GetLastError` success-path assumption and byte-vs-character size mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/config.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/groups.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/groups.c

## Purpose
`groups.c` implements the Windows `winutils groups` subcommand. It prints the local groups for a specified user, or for the current user when no username is supplied, with an optional machine-readable pipe separator.

## Important APIs, Types, And Functions
The exported entry point is `int Groups(int argc, wchar_t *argv[])`; `GroupsUsage()` documents `[OPTIONS] [USERNAME]` and `-F`. Internal helpers are `ParseCommandLine`, which handles optional user and formatting mode, and `PrintGroups`, which iterates an array of `LOCALGROUP_USERS_INFO_0` entries. The command uses `GetUserNameW` to discover the current user, `GetLocalGroupsForUser` from the shared winutils layer, `NetApiBufferFree` for NetAPI buffers, and `LocalFree` for the current-user buffer.

## Control Flow
Argument parsing accepts no arguments, a username, `-F`, or `-F username`. If no username is provided, the code probes `GetUserNameW` with a null buffer, expects `ERROR_INSUFFICIENT_BUFFER`, allocates the required buffer, and calls `GetUserNameW` again. It then calls `GetLocalGroupsForUser`, prints each group name separated by spaces by default or `|` in formatted mode, prints a trailing newline only on successful iteration, and returns failure on lookup or output traversal errors.

## State And Persistence Behavior
This command is read-only. It allocates temporary memory for the current username and receives a NetAPI-allocated group buffer, both freed on exit. It writes only to stdout/stderr and has no persistent cache.

## Dependencies And Integration Points
`groups.c` depends on `winutils.h` for Windows/NetAPI declarations, error reporting, and `GetLocalGroupsForUser`. Hadoop can use it as a Windows substitute for Unix `groups` output when resolving authorization groups or testing local identity behavior.

## Risks
The current-user discovery path assumes the first `GetUserNameW(NULL, &size)` sets `ERROR_INSUFFICIENT_BUFFER`; different API behavior would report failure. `PrintGroups` has a defensive null check inside iteration but cannot validate the actual buffer length beyond `entries`. The implementation returns only local groups as provided by `GetLocalGroupsForUser`; domain group behavior depends on that helper and may differ from Unix group resolution expectations. `-F` uses `|` as a separator without escaping group names, so group names containing `|` would be ambiguous.

## Test Signals
Tests should cover current-user lookup, explicit local and domain users, users with zero groups, nonexistent users, `-F` formatting, invalid argument combinations, Unicode group names, and NetAPI failure injection. Integration tests should compare output against Windows local group membership APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/hadoopwinutilsvc.idl -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/hadoopwinutilsvc.idl

## Purpose
`hadoopwinutilsvc.idl` defines the Microsoft RPC contract for the privileged Hadoop Windows utility service. It specifies the local RPC endpoint, request/response structures, operation enum values, and callable methods used by `client.c` and the corresponding service implementation.

## Important APIs, Types, And Functions
The IDL imports `oaidl.idl` and `ocidl.idl`, defines interface `HadoopWinutilSvc` with UUID `0492311C-1718-4F53-A6EB-86AD7039988D`, version `1.0`, unique pointer defaults, and endpoint `ncalrpc:[hadoopwinutilsvc]`. Structs include `CREATE_PROCESS_REQUEST/RESPONSE`, `CHOWN_REQUEST`, `CHMOD_REQUEST`, `MKDIR_REQUEST`, `MOVEFILE_REQUEST`, `CREATEFILE_REQUEST/RESPONSE`, `DELETEPATH_REQUEST/RESPONSE`, and `KILLTASK_REQUEST`. Enums are `MOVE_COPY_OPERATION` (`MOVE_FILE`, `COPY_FILE`) and `DELETEPATH_TYPE` (`PATH_IS_DIR`, `PATH_IS_FILE`). RPC methods include `WinutilsKillTask`, `WinutilsMkDir`, `WinutilsMoveFile`, `WinutilsChown`, `WinutilsChmod`, `WinutilsCreateFile`, `WinutilsDeletePath`, and `WinutilsCreateProcessAsUser`.

## Control Flow
The IDL itself is declarative. The MIDL compiler generates client/server stubs and a header consumed by `client.c`. At runtime, clients bind explicitly to the local endpoint, send request structs, and receive `error_status_t` plus response pointers for methods that return handles or deletion status. Methods that create handles also receive `nmPid`, enabling the service to duplicate handles for the requesting process.

## State And Persistence Behavior
The contract carries strings, booleans, enums, integer modes/access flags, and `LONG_PTR` handle values across process boundaries. It does not persist state directly; service implementations perform persistent effects such as filesystem changes, process creation, task kill, and deletion. Response structures are allocated by RPC/MIDL conventions and freed by the client with `MIDL_user_free`.

## Dependencies And Integration Points
This file is the schema binding `client.c`, generated `hadoopwinutilsvc_h.h`, and the Windows service implementation. The `ncalrpc` endpoint restricts transport to local machine RPC, while actual security policy is supplied by client/server binding authentication and service access checks. It is part of the Windows-specific Hadoop Common build.

## Risks
Changing field order, enum values, endpoint name, UUID, or pointer annotations breaks ABI compatibility between client and service binaries. The contract exposes privileged filesystem and process operations, so server-side authorization must validate callers and request parameters; the IDL alone does not enforce path safety, ownership rules, or handle lifetime. `LONG_PTR` handle transport requires careful duplication and architecture consistency. Request strings are marked `[string] const wchar_t*`; service code must validate nullability and length even when the IDL permits unique pointers.

## Test Signals
Tests should include MIDL generation, client/server binary compatibility, endpoint binding, null and long string marshalling, enum marshalling, 32-bit/64-bit handle round trips if supported, service authorization failures, and every operation's success/failure path through generated stubs. ABI changes should trigger integration tests that run an old client against a new service only when compatibility is intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/hadoopwinutilsvc.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/hardlink.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/hardlink.c

## Purpose
`hardlink.c` implements the Windows `winutils hardlink` subcommand. It supports creating a hard link to an existing file and reporting the number of hard links for a file.

## Important APIs, Types, And Functions
`HardLinkCommandOptionType` defines `HardLinkInvalid`, `HardLinkCreate`, and `HardLinkStat`. The exported entry point is `int Hardlink(int argc, wchar_t *argv[])`, with `HardlinkUsage()` documenting `hardlink create LINKNAME FILENAME` and `hardlink stat FILENAME`. Internal helpers are `ParseCommandLine`, `HardlinkStat`, and `HardlinkCreate`. The implementation uses shared `ConvertToLongPath`, `GetFileInformationByName`, and `ReportErrorCode` helpers, plus the Windows `CreateHardLink` API.

## Control Flow
`ParseCommandLine` requires exactly three args for `hardlink stat` or four for `hardlink create`, and also requires `argv[0]` to equal `hardlink`. For `stat`, the command converts the file path, reads `BY_HANDLE_FILE_INFORMATION`, and prints `nNumberOfLinks`. For `create`, it converts both link and target paths, calls `CreateHardLink(longLinkName, longFileName, NULL)`, and prints a success message on completion. Any conversion, file-information, or API failure is reported and returns process failure.

## State And Persistence Behavior
`stat` is read-only. `create` persists a new directory entry pointing to the same file data on the same volume. Temporary long-path strings are allocated and freed with `LocalFree`. There is no rollback needed beyond the single `CreateHardLink` call.

## Dependencies And Integration Points
The file depends on `winutils.h` for path conversion, file information, and error reporting. It integrates with Hadoop's Windows shell utilities where Java code expects hard-link functionality analogous to Unix `ln` or link-count inspection.

## Risks
`CreateHardLink` works only for files on volumes/filesystems that support hard links and generally requires source and link on the same volume; errors are surfaced but not interpreted. The strict `argv[0] == "hardlink"` check can fail if a dispatcher passes a full executable name or command alias instead of the subcommand name. `HardlinkStat` uses `followLink=FALSE`, so behavior on symlink paths depends on how `GetFileInformationByName` handles reparse points. The success message includes paths and may expose sensitive local paths in logs.

## Test Signals
Tests should cover successful create/stat on NTFS, cross-volume create failure, missing source, existing link path, directory input, symlink/reparse point input, long paths, Unicode paths, strict argument validation, and expected link count changes through both winutils and native Windows APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/hardlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/include/winutils.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/include/winutils.h

## Purpose
`winutils.h` is the shared public header for Hadoop's Windows utility executable and service support code. It centralizes Windows includes, exit codes, Unix-to-Windows permission constants, subcommand prototypes, security/ACL helpers, Kerberos/LSA token helpers, service helpers, configuration parsing, RPC/service security utilities, and process/job naming helpers.

## Important APIs, Types, And Functions
The header forces Unicode builds, includes core Windows/security headers (`windows.h`, `aclapi.h`, `accctrl.h`, `lm.h`, `ntsecapi.h`, `userenv.h`), and exposes `extern "C"` for C++ consumers. `enum EXIT_CODE` defines shared return codes including `SUCCESS`, `FAILURE`, `SYMLINK_NO_PRIVILEGE`, `ERROR_TASK_NOT_ALIVE`, and Unix-compatible `KILLED_PROCESS_EXIT_CODE` 137. `enum UnixAclMask` defines POSIX mode bits for owner/group/other read/write/execute plus directory/regular/symlink file-type bits. `enum WindowsAclMask` indexes `WinMasks[]` for read/write/execute/owner/all Windows ACL masks.

Command APIs include `Ls`, `Chmod`, `Chown`, `Groups`, `Hardlink`, `Task`, `Symlink`, `Readlink`, `SystemInfo`, and service entry/usage functions. Filesystem/security helpers include `GetFileInformationByName`, `CheckAccessForCurrentUser`, `ConvertToLongPath`, SID/account conversion, `FindFileOwnerAndPermission`, directory/symlink/junction checks, `ChangeFileModeByMask`, file/directory creation with mode, `ChangeFileOwnerBySid`, and `ChownImpl`. Identity and service helpers include local-group lookup, DLL name lookup, privilege enabling, LSA string registration/unregistration, Kerberos package lookup, logon token/profile loading, impersonation privileges, service security descriptor construction, adding NodeManager/user ACEs, and secure job object naming. Utility APIs include timestamp/logging, string splitting, module-relative path building, and XML config lookup.

## Control Flow
As a header, this file has no runtime control flow. It defines the call graph contract followed by individual command files and shared implementation units. `winutils.exe` dispatches subcommands to the declared command functions; command implementations call the shared helpers for path conversion, Windows account/SID resolution, ACL translation, and error reporting. Service-related code uses the LSA, token, profile, and security descriptor APIs to run tasks as users and protect job/process objects.

## State And Persistence Behavior
Declared functions operate on persistent Windows state: file ACLs and owners, directories/files created with modes, symlinks/junctions, local group membership queries, privileges in process tokens, LSA logon sessions, user profiles, job objects, service security descriptors, process/object ACEs, and configuration values read from XML. The header also declares constants used to map persistent Windows ACLs into Hadoop's Unix-style permission model.

## Dependencies And Integration Points
This header is the integration spine for the Windows-specific Hadoop Common native code. It ties together `chmod.c`, `chown.c`, `groups.c`, `hardlink.c`, RPC client/service files, task launching, symlink/readlink, local filesystem ACL emulation, and Hadoop Java callers that shell out to `winutils.exe`. It depends on Windows-only APIs and is not portable to Unix builds. The XML config functions connect service/native code to Hadoop configuration files, while Kerberos/LSA helpers connect Hadoop identity to Windows authentication.

## Risks
Because this header exposes broad privileged operations, API contract drift can break multiple commands or the service. SAL annotations help static analysis but do not enforce runtime null/length checks. The Unix permission mask abstraction is necessarily lossy relative to Windows ACLs, so callers may assume POSIX semantics that the underlying ACL helpers cannot fully provide. Exit code overlap exists (`FAILURE`, `ERROR_TASK_NOT_ALIVE` both map to 1), which can limit diagnostic precision. Any change to `WinMasks[]` semantics affects chmod, file creation modes, and permission reporting across Hadoop on Windows.

## Test Signals
Test signals include native compilation in C and C++ translation units, static analysis of SAL contracts, unit tests for Unix/Windows ACL mask translation, long path conversion, SID/account round trips, owner/group/mode discovery, chmod/chown/file creation behavior, symlink/junction checks, service security descriptor construction, privilege enabling, LSA/Kerberos token creation, user profile load/unload, and integration tests through Java Hadoop filesystem APIs on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/include/winutils.h -->
