# sources/distributed-fs/openafs/src/WINNT/tests/winflock/sync.cpp

Purpose: small synchronization and logging helper layer for the WinFLock parent/child test program.

Important APIs and functions: `_begin_log` and `_end_log` serialize log blocks with `mutex_logfile`. `_sync_begin_parent`, `_sync_end_parent`, `_sync_begin_child`, and `_sync_end_child` implement one-way phase handoffs using `event_child` and `event_parent`.

Control flow: parent-side sections begin logging immediately, then signal the child at end. Child-side sections wait for `event_child`, log and execute, then signal `event_parent`. The complementary macros in `winflock.h` wrap these functions with `if(!isChild)` or `if(isChild)` guards.

State and persistence: uses process-global `isChild`, event handles, and mutex handle. Logging is to `logfile`, currently `cout`.

Dependencies and integration: tightly coupled to `main.cpp` object creation and `tests.cpp` synchronization macros.

Risks and test signals: a missed event or unbalanced macro section can deadlock both processes. The absence of timeouts means hangs are diagnostic but not self-reporting. Correct output alternates `PARENT { ... }` and `CHILD { ... }` blocks.
