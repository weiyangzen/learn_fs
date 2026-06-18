<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osithrdnt.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osithrdnt.h

Purpose: Provides the Windows NT thread, event, critical-section, and handle abstraction macros used by OSI code.

Important APIs, types, and functions: Maps `thread_t` to `HANDLE`, `ThreadFunc` to `LPTHREAD_START_ROUTINE`, `SecurityAttrib` to `PSECURITY_ATTRIBUTES`, and wrappers such as `thrd_Create`, `thrd_CloseHandle`, event create/set/reset/wait functions, interlocked increment/decrement, `thrd_Sleep`, critical-section init/enter/leave/delete, `thrd_Current`, `EVENT_HANDLE`, and `FILE_HANDLE`.

Control flow and state: This is a macro layer; callers write OSI-neutral names but compile directly to Win32 APIs.

Persistence and dependencies: No persistence. Depends on Windows headers already being available.

Integration points: Used throughout client OSI lock, queue, fd, sleep, stats, log, and tests.

Risks: Macros expose raw Win32 semantics and do not normalize error handling. `thrd_Create` ignores the `name` argument. Event and wait macro names do not distinguish manual-reset/autoreset creation options.

Test signals: Build tests should confirm the macro layer compiles under supported Windows SDKs and that callers include required Windows types before this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osithrdnt.h -->
