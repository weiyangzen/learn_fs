# sources/distributed-fs/ceph-client/include/linux/sched/thread_info_api.h

Purpose: compatibility include that exposes thread-info APIs through the scheduler namespace.

Important APIs and types: no new symbols are defined; it includes `linux/thread_info.h`.

Control flow: callers use this wrapper to access thread flags and current thread-info helpers.

State and persistence: no state is owned here.

Dependencies and integration points: bridges scheduler headers and architecture/generic thread-info declarations.

Risks and test signals: risk is include layering drift. Compile-test thread-info users after scheduler header refactors.
