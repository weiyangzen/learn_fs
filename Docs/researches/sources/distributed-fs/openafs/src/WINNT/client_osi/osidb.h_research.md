<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.h

Purpose: Defines remote-debug data layouts for lock and sleep diagnostics plus the initialization entry point and RPC call count defaults.

Important APIs, types, and functions: `osi_remLockInfo_t` describes a remotely exported lock with type, address, reader/writer/waiter/owner state, and aggregate read/write lock and blocked timing counts. `osi_remSleepInfo_t` describes a blocked thread id and sleep value. `OSI_MAXRPCCALLS` reserves two RPC server calls. `osi_InitDebug` initializes the debug server. `osi_maxCalls` and `osi_maxCallsp` expose configuration hooks inside and outside OSI.

Control flow and state: This header is schema, not behavior. Implementations populate the structures from `osistatl.c` and `osisleep.c` fd iterators. Clients interpret integer arrays and string arrays defined in the generated RPC types alongside these named structures.

Persistence and dependencies: No persistence. It depends on OSI scalar types such as `LONG_PTR`, `thread_t`, and `osi_uid_t`, and on the generated debug RPC transport contract.

Integration points: Included by OSI remote-debug server/client code and any external diagnostic tool that wants to interpret lock and sleep records.

Risks: The structure comments and the fd iterator fields must stay consistent; otherwise remote tools can mislabel statistics. Timing is stored in `long` milliseconds and may overflow on long-lived processes. `owner` is explicitly incomplete for multiple readers.

Test signals: Validate ABI sizes across 32/64-bit builds, ensure `OSI_MAXRPCCALLS` can be overridden where expected, and compare generated RPC data against these structures for lock and sleep reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.h -->
