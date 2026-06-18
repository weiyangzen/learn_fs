# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/service.c

Purpose: implements the NodeManager Windows Secure Container Executor helper service, exposing privileged local RPC operations for process creation, file creation, deletion, chmod/chown, mkdir, move/copy, and task kill under constrained authorization.

Important APIs/functions: service lifecycle functions `RunService`, `SvcMain`, `SvcInit`, `SvcCtrlHandler`, `SvcShutdown`, `ReportSvcStatus`; security/config functions `ValidateConfigurationFile`, `AuthInit`, `InitLocalDirs`, `InitJobName`, `ValidateLocalPath`, `RpcAuthorizeCallback`; RPC functions `WinutilsCreateProcessAsUser`, `WinutilsCreateFile`, `WinutilsKillTask`, `WinutilsDeletePath`, `WinutilsMkDir`, `WinutilsChown`, `WinutilsChmod`, and `WinutilsMoveFile`.

Control flow: startup registers with SCM/event log, enables impersonation privileges, creates a stop event, validates that the WSCE config file is writable only by LocalSystem/Administrators, builds an allowed-caller security descriptor from config, loads local directories and optional job name, then starts a local-only RPC server with an AuthZ callback. RPC methods validate local paths, perform requested Win32 operations, duplicate handles back into the NodeManager process when needed, and log through Event Log/debug messages.

State and persistence: global service handles, event log handle, `pAllowedSD`, local-dir arrays, job name, and listener state persist for service lifetime. RPC operations mutate local files/directories, ACLs, ownership, process/job objects, and duplicated handles in the NodeManager process.

Dependencies/integration: depends on generated `hadoopwinutilsvc_h.h`, RPC runtime, AuthZ, service control manager, `libwinutils.c`, and WSCE XML config properties. It is the privileged peer of YARN NodeManager on Windows.

Risks and test signals: local path validation is prefix-based and path-normalization-sensitive; service auth depends on config ACL integrity; duplicate-handle cleanup is complex; process command-line construction has quoting and size limits. Tests should cover config ACL rejection, allowed/denied caller SIDs, local-dir escape attempts, handle transfer cleanup on mid-flight errors, and local-only RPC binding.
