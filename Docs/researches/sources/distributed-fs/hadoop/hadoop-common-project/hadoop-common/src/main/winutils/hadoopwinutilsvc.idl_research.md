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
