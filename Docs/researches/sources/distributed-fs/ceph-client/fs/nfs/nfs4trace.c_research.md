# sources/distributed-fs/ceph-client/fs/nfs/nfs4trace.c

## Purpose
`nfs4trace.c` instantiates the NFSv4 tracepoint definitions declared in `nfs4trace.h` and exports selected pNFS/layout tracepoints to GPL modules. It is the single compilation unit that defines the tracepoint storage by setting `CREATE_TRACE_POINTS`.

## Important APIs and Functions
- `#define CREATE_TRACE_POINTS` before including `nfs4trace.h`: causes the Linux tracepoint macros to emit definitions rather than declarations.
- `EXPORT_TRACEPOINT_SYMBOL_GPL(...)`: exports selected tracepoints for pNFS read/write/commit, MDS fallback, data-server connect, flexfiles errors, block layout persistent reservation key events, and file-layout device info.

## Control Flow
There are no runtime functions in this file. Build-time macro expansion creates the tracepoint objects. At module load, those tracepoints become available through ftrace/perf/tracefs. Exported symbols allow other GPL NFS/pNFS layout modules to call the tracepoints without owning their definitions.

## State and Persistence
Tracepoint registration is kernel instrumentation state. Events are transient and emitted only when enabled by tracing infrastructure. There is no local persistent state.

## Dependencies and Integration Points
The file includes NFS core headers, `nfs4session.h`, callback support, and pNFS definitions so that all tracepoint prototypes in `nfs4trace.h` are fully typed. It bridges the header's trace definitions to external pNFS modules that need exported tracepoint symbols.

## Risks
Forgetting to keep exactly one `CREATE_TRACE_POINTS` compilation unit would cause missing or duplicate tracepoint definitions. Export lists must match tracepoints used outside this object; otherwise layout modules can fail to link or lose observability. Type changes in structs referenced by `nfs4trace.h` require this file's includes to remain sufficient.

## Test Signals
Build/link tests with pNFS layouts enabled are the main signal. Runtime checks should verify tracefs contains the NFSv4 events and that exported pNFS tracepoints can be called by flexfiles, block, and file-layout code when those modules are enabled.
