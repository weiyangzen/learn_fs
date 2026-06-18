# sources/distributed-fs/openafs/src/afs/AIX/osi_machdep.h

Purpose: AIX machine-dependent OSI definitions that adapt common OpenAFS kernel code to AIX types, locks, time, lookup, credentials, and process identity.

Important APIs and macros: defines `osi_ThreadUnique`, `afs_hz`, `osi_Time`, `afs_ucred_t`, `afs_proc_t`, `afs_bufferpages`, lookup macros, `get_ulimit`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `osi_InitGlock`, `osi_procname`, and inline `osi_GetTime`.

Control flow: global lock macros assert ownership invariants before locking/unlocking and panic on misuse. `osi_GetTime` calls `curtime` and converts nanoseconds to microseconds.

State and persistence: no persistent storage, but lock macros protect global OpenAFS kernel state. `osi_Time` reads AIX `time`.

Dependencies and integration: included indirectly by `afs_osi.h`. Depends on AIX lock, sleep, time, and ulimit headers.

Risks and test signals: lock ownership assertions can panic if common code violates AIX expectations. `osi_procname` intentionally returns an empty string. Signals are successful lock initialization and absence of GLOCK ownership panics.
