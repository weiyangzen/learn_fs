## sources/distributed-fs/openafs/src/WINNT/client_osi/basic.c

Purpose: Implements a Win32 stress test for the OSI mutex/RW-lock package.

Important APIs/functions: `main_BasicTest` initializes OSI/logging, creates modifier and scanner threads, reports progress, waits for completion, finalizes locks, and closes thread handles. Worker functions `main_Mod1`, `main_Mod2`, `main_Scan1`, and `main_Scan2` exercise mutexes, read/write locks, assertions, logging, and unlocked observation.

Control flow/state: Shared globals `a` and `b` must sum to 100 under lock protection; `done` tracks thread completion under `main_doneRWLock`. Loop counters and event counters feed the UI display.

Dependencies/integration: Uses `osi.h`, `main.h`, Win32 threads, `Sleep`, and OSI logging. Invoked by the OSI test application menu.

Risks/tests: Some thread-create failures leak already-created handles. Loop counters are intentionally unlocked and may display transient values. Test lock correctness under debug/stat lock types, assertion failures, repeated runs, thread-create failures, and final lock cleanup.
