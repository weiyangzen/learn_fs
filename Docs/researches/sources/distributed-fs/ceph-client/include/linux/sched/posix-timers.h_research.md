# sources/distributed-fs/ceph-client/include/linux/sched/posix-timers.h

Purpose: compatibility include that exposes POSIX timer declarations through the scheduler include namespace.

Important APIs and types: this file defines no new symbols; it includes `linux/posix-timers.h`.

Control flow: scheduler or signal code can include this path and receive POSIX timer types/functions. Runtime behavior lives in POSIX timer implementation.

State and persistence: no state is owned here.

Dependencies and integration points: bridges scheduler headers and POSIX timer declarations.

Risks and test signals: risk is include layering drift. Compile-test scheduler/signal users that include this wrapper.
