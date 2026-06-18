# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientInternal.cpp

Purpose: provides a lazily initialized process-wide critical section for the admin-server client library.

Important APIs/types/functions: `asc_Enter()` initializes `l.pcs` if needed and enters it. `asc_Leave()` leaves it. `asc_GetCriticalSection()` returns the initialized critical-section pointer for hash lists and other modules.

Control flow: modules call `asc_Enter/Leave` around shared cache/listener operations or assign the critical section to `HASHLIST` instances for internal locking.

State/persistence: static `l.pcs` is allocated once and never freed in this file. No disk persistence.

Dependencies/integration: depends on Windows `CRITICAL_SECTION` and OpenAFS `New` allocation macro. Used by cache and notification modules.

Risks/test signals: lazy initialization is not itself thread-safe if two threads call before `l.pcs` is set. There is no deletion path. Tests should stress concurrent first use, nested use expectations, and modules sharing the same critical section.
