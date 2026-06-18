<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osistatl.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osistatl.h

Purpose: Declares data structures and entry points for the OSI statistics-gathering lock type and remote lock-stat fd.

Important APIs, types, and functions: `osi_activeInfo_t` records a thread's active owner/waiter timing state. `osi_statFD_t` stores fd scan cursor and whether it is scanning mutexes or rwlocks. `osi_qiStat_t` stores active list, lock name, and back pointer. `osi_mutexStat_t` and `osi_rwlockStat_t` contain queue linkage, turnstile, refcount, delete state, owner tid fields, timing/count aggregates, and shared queue info. `osi_watchProc_t` is a callback for long-held locks. The header declares stat lock initializers, active-info helpers, `osi_StatInit`, `osi_SetStatLog`, and `osi_SetWatchProc`.

Control flow and state: Stat locks use auxiliary records to retain instrumentation while the public lock structs keep the normal fields needed by callers and lock assertions.

Persistence and dependencies: No persistence. Depends on `osibasel.h`, `largeint.h` for older MSVC, and `osiqueue.h`.

Integration points: Included by `osilog.h` and stat implementation, and indirectly by code that selects dynamic lock type `"stat"`.

Risks: Public declarations for helpers implemented as `static` in `osistatl.c` can cause linkage inconsistency if referenced externally. The header documents layout assumptions for fd code; changing field order in stat structs can break iteration/finalization.

Test signals: Compile with strict warnings, verify struct layout assumptions, and test long-held-lock watch callback ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osistatl.h -->
