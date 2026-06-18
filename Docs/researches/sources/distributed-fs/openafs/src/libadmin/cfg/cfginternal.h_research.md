# sources/distributed-fs/openafs/src/libadmin/cfg/cfginternal.h

## Purpose
This private header defines the configuration library host-handle structure and declares internal helper routines shared by cfg implementation files. It is not a public admin API surface; it exposes internals needed by modules that configure BOS, servers, clients, and host state.

## Important APIs, Types, and Functions
- `cfg_host_t` contains validation magic, `is_valid`, the target `hostName`, `is_local`, an admin `cellHandle`, `cellName`, a pthread mutex, lazy `bosHandle`, and closing magic.
- Declarations cover host validation, BOS initialization, cell-name compatibility, host canonicalization/alias/address queries, directory cleanup, no-auth flag toggling, and portable sleep.
- Under `AFS_NT40_ENV`, declarations expose Windows service start/stop/query helpers using `LPCTSTR`, `DWORD`, service state values, and admin status output.

## Control Flow and State
The header encodes the shared handle lifecycle model used by cfg modules: callers receive an opaque host handle, implementation code casts it to `cfg_host_p`, validates magic and state, and then uses the embedded cell and BOS handles. The mutex specifically protects one-time BOS initialization, not all host-handle fields.

## Persistence and Side Effects
The header itself has no side effects, but it declares functions that mutate BOS/service state, local no-auth files, and directories. It also establishes that host handles retain a reusable BOS connection pointer.

## Dependencies and Integration Points
It depends on prior inclusion of pthread and AFS admin types such as `afs_status_p` and `afs_int32`. Public cfg source files include this header beside `afs_cfgAdmin.h`; client/BOS/adminutil modules provide the types and functions referenced by declarations.

## Risks
Because the struct is shared internally, any ABI or field-order change affects all cfg object files compiled against it. The header relies on include-order for pthread and AFS types. The raw `void *` cell/BOS handles avoid type checking. The `cellName` field is a borrowed `const char *`, so lifetime must follow the owning cell handle.

## Test Signals
Compile coverage is important: every cfg implementation using this header should build on Unix and Windows. Runtime tests should validate that host handles created by the public cfg open path satisfy these declarations and that invalidated handles fail consistently after close.
