# sources/distributed-fs/ceph-client/include/linux/mutex_api.h

Purpose: compatibility wrapper that exposes the mutex API by including `linux/mutex.h`.

Important APIs and types: it defines no independent symbols; all API surface comes from `mutex.h`.

Control flow: include users that still reference `linux/mutex_api.h` are routed directly to the canonical mutex declarations.

State and persistence: no state is owned here.

Dependencies and integration points: depends solely on `linux/mutex.h`. It preserves source compatibility for code that includes the older split API header.

Risks and test signals: risk is header dependency drift if `mutex.h` changes include guards or ordering. Test by compiling include users and ensuring no duplicate declarations or missing mutex symbols.
