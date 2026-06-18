<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.h

Purpose: Declares the OSI diagnostic fd abstraction and the registration/iteration APIs used by remote-debug collections.

Important APIs, types, and functions: `osi_fdOps_t` contains `Create`, `GetInfo`, and `Close` callbacks. `osi_fd_t` is the common descriptor header with queue linkage, ops pointer, and numeric fd. `osi_typeFD_t` is the cursor for the built-in type iterator. `osi_fdTypeFormat_t` describes a field label, region, index, and formatting flags. `osi_fdType_t` stores a registered collection name, owner rock, operations, and format list. Public functions cover type lookup/registration/unregistration, adding format info, fd initialization, allocation, lookup, close, and built-in type fd ops.

Control flow and state: Collection owners register a type once, then fd clients open by name. The fd header must be the first member of concrete fd structs so generic code can cast.

Persistence and dependencies: No persistence. Depends on generated `dbrpc.h` for `osi_remGetInfoParms_t` and constants, and on `osiqueue.h` for intrusive list fields.

Integration points: This header is included by sleep, stat, log, and debug RPC modules. It is the common bridge between in-process diagnostics and RPC exposure.

Risks: Intrusive layout requirements are convention-based. Returned pointers are not ref-counted by the API. Format metadata ownership belongs to the registry and is freed only on unregister.

Test signals: Compile-time tests should ensure concrete fd structs start with `osi_fd_t`; runtime tests should register a mock type and verify create/get/close and format discovery through `osidb.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.h -->
