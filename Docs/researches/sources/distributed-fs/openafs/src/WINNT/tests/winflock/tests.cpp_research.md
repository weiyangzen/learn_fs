# sources/distributed-fs/openafs/src/WINNT/tests/winflock/tests.cpp

Purpose: implementation of Win32 file sharing and byte-range locking tests against a local or AFS-backed directory.

Important APIs and functions: `begin_tests` creates base and auxiliary files. `test_create` checks sharing violations and compatible sharing. `test_lock_prep` writes a 1 MiB deterministic page pattern. `testint_lock_excl_beof` and `testint_lock_excl_eeof` set and verify exclusive locks below and above EOF. `testint_lock_excl_rw_beof` checks read/write behavior in locked, unlocked, owned, and unowned regions. `testint_waitlock` uses overlapped `LockFileEx` to verify pending lock wakeups. `testint_unlock`, `testint_lock_escalation`, and `end_tests` clean up and validate unlock/escalation behavior.

Control flow: parent and child share the same file names and handles but execute different synchronized blocks. Page ranges are expressed with `PAGE_BEGIN`/`PAGE_LEN` at 4 KiB granularity. Many tests intentionally expect failure and treat `ERROR_SHARING_VIOLATION` or lock denial as pass conditions.

State and persistence: global `test_dir`, `fn_base`, `fn_aux`, `h_file_base`, and `h_file_aux` hold file state. Test files `FLTST000`, `FLTST001`, and `asyncft.dat` persist unless deleted externally.

Dependencies and integration: depends on `winflock.h` macros, `sync.cpp` handoffs, and Win32 `CreateFile`, `LockFile`, `LockFileEx`, `UnlockFile`, `UnlockFileEx`, `ReadFile`, `WriteFile`, and `FlushFileBuffers`.

Risks and test signals: some error handling logs warnings but returns success, so external parsing of `TEST:* FAILED` is more reliable than process exit alone. AFS redirector differences are surfaced through PASS/FAILED lines, last-error values, and deadlocks in wait-lock scenarios.
