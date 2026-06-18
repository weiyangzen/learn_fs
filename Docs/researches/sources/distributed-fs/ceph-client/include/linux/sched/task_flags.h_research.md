# sources/distributed-fs/ceph-client/include/linux/sched/task_flags.h

Purpose: compatibility include for task PF/PFA flag declarations.

Important APIs and types: no new symbols are declared here; it includes `linux/sched.h`, which defines PF flags and atomic PFA helper macros.

Control flow: callers include this wrapper to access task flags. Runtime behavior is in task flag operations from `sched.h`.

State and persistence: no state is owned here.

Dependencies and integration points: depends entirely on `linux/sched.h`; preserves header organization for task-flag users.

Risks and test signals: risk is include dependency drift. Compile-test users including only `sched/task_flags.h`.
