<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.c

Purpose: Implements an in-process file-descriptor abstraction used by OSI remote debugging. It lets subsystems register named diagnostic collections, open logical cursors, iterate records, close them, and advertise formatting metadata.

Important APIs, types, and functions: Globals include `osi_fdCS`, `osi_allFDs`, `osi_allFDTypes`, and monotonic `osi_nextFD`. `osi_TypeFDOps` implements the built-in `"type"` collection. `osi_FindFDType`, `osi_RegisterFDType`, and `osi_UnregisterFDType` manage type registrations. `osi_AddFDFormatInfo` attaches labels and formatting flags to type fields. `osi_InitFD` initializes the fd registry and registers `"type"`. `osi_AllocFD` creates an fd via a type's `Create` op and adds it to `osi_allFDs`. `osi_FindFD` resolves fd ids. `osi_CloseFD` unthreads and closes a descriptor. `osi_FDTypeCreate`, `osi_FDTypeGetInfo`, and `osi_FDTypeClose` implement iteration over registered type names.

Control flow and state: The registry is protected by a critical section for list and id mutations. Registering a type duplicates the name, stores the ops and owner rock, and pushes it on the type list. Opening an fd looks up the type by name, calls its create function, assigns a new id, and adds it to the live fd list. RPC callers then iterate records through the ops vector and close the fd.

Persistence and dependencies: No disk persistence. Runtime lists are process-global and allocated with `malloc`. Dependencies include `osiqueue` list operations, `dbrpc` data shapes, OSI thread critical-section wrappers, and the caller's fd op implementations.

Integration points: `osidb.c` exposes this registry over RPC. `osisleep.c`, `osistatl.c`, and `osilog.c` register `"sleep"`, `"lock"`, and `"log:<name>"` fd types. `osidebug.c` first opens `"type"` to discover available collections.

Risks: `osi_UnregisterFDType` returns without leaving `osi_fdCS` when the type is not found, which can deadlock future fd operations. `osi_FindFD` returns a live pointer after releasing the registry lock, so concurrent close could invalidate it if RPC calls race. Type iteration snapshots `osi_allFDTypes` without consistently holding the lock while reading the current pointer. Several functions lack explicit return types in K&R style. Duplicate type registration asserts instead of returning an error.

Test signals: Test duplicate registration, unregister missing type lock handling, fd open/close lifecycle, concurrent GetInfo/Close races, `"type"` iteration across registered dynamic types, and format metadata lookup including EOF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.c -->
