# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRIoctl.h

## Purpose
Declares the redirector pioctl subsystem API and, when `RDR_IOCTL_PRIVATE` is defined, exposes the private instance structure, flags, function-pointer type, and all opcode handler prototypes used by `RDRIoctl.c`.

## Important APIs, Types, And Functions
The public API is `RDR_InitIoctl`, `RDR_ShutdownIoctl`, `RDR_SetupIoctl`, `RDR_CleanupIoctl`, `RDR_IoctlRead`, and `RDR_IoctlWrite`. The private `RDR_ioctl_t` stores list links, request index, parent/root FIDs, held parent scache, embedded `cm_ioctl_t`, flags, lock-protected refcount, and `cm_req_t`. `RDR_ioctlProc_t` is the common handler signature. The header declares handlers for ACLs, token management, volume/cell/server/cache controls, mount points, symlinks, rx statistics, UUID/path availability, file type, Unix owner/group/mode, verify data, and caller access.

## Control Flow
Callers create pioctl state with `RDR_SetupIoctl`, push bytes with `RDR_IoctlWrite`, retrieve the return code and response stream with `RDR_IoctlRead`, and tear state down with `RDR_CleanupIoctl`. Private helpers declared here allow `RDRIoctl.c` to transition a request from data-in to data-out and find/refcount live instances.

## State And Persistence
The header defines no state by itself, but its private structure describes the in-memory persistence of a pioctl request across multiple redirector read/write calls. `RDR_IOCTL_FLAG_CLEANED` marks instances that were closed while still referenced.

## Dependencies And Integration Points
It depends on cache-manager pointer types and `cm_ioctl_t` from surrounding includes. It is included by `RDRIoctl.c` with `RDR_IOCTL_PRIVATE` and by other redirector modules for public entry points. The handler prototypes integrate with `VIOC*` opcode registration in `RDR_InitIoctl`.

## Risks And Test Signals
The main risk is declaration drift against implementations and the opcode table. Because private declarations expose many cache-manager wrappers, signature mismatches can break C/C++ callers. Compile coverage of `RDRIoctl.c` and pioctl integration tests are the primary signals.
