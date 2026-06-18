<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.h

Purpose: Defines the dynamic lock operation vector ABI and state-bit constants returned by lock state query functions.

Important APIs, types, and functions: `OSI_NLOCKTYPES` limits dynamic lock types to 32. `osi_lockOps_t` includes operations for rwlock read/write obtain/release, mutex obtain/release, try operations, sleep with lock release, initialization/finalization, read/write conversions, and state queries. The header exports `osi_lockOps`, `osi_lockTypeDefault`, `osi_LockTypeAdd`, and `osi_LockTypeSetDefault`. State bits are `OSI_MUTEX_HELD`, `OSI_RWLOCK_READHELD`, and `OSI_RWLOCK_WRITEHELD`.

Control flow and state: Nonzero lock objects store a type index and private data pointer; lock API functions dispatch through the matching `osi_lockOps_t`.

Persistence and dependencies: No persistence. Depends on forward-declared `osi_rwlock` and `osi_mutex` shapes, `LONG_PTR`, and OSI lock structs from `osibasel.h`.

Integration points: Used by `osibasel.c` and `osistatl.c` to plug in instrumented lock behavior without changing callers.

Risks: Every ops vector must be complete and semantically compatible with the base lock API. The ABI assumes function signatures match exactly; missing or reordered fields would break dispatch.

Test signals: Compile-time coverage for all vector fields, runtime dispatch of each operation through a nonzero type, and state query compatibility with assertion macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.h -->
