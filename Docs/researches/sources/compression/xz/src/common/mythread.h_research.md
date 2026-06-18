<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/mythread.h -->
# sources/compression/xz/src/common/mythread.h

Purpose: portability abstraction for threading, mutexes, condition variables, one-time initialization, and signal masks.

Important APIs/types/functions: `MYTHREAD_ENABLED`, `mythread_sync`, `mythread_once`, `mythread_create`, `mythread_join`, mutex helpers, condition helpers, `mythread_condtime_set`, `MYTHREAD_RET_TYPE`, and platform-specific typedefs.

Control flow: preprocessor selects no-thread, POSIX pthread, Win95, or Vista implementations. POSIX thread creation temporarily blocks all signals; condition variables prefer monotonic clocks when available. Windows uses `_beginthreadex`, critical sections, events or condition variables, and tick-count timeouts.

State and persistence: synchronization state is caller-owned; no persistent state except static once guards inside macros.

Dependencies and integration: selected by `MYTHREAD_POSIX`, `MYTHREAD_WIN95`, or `MYTHREAD_VISTA` from `configure.ac`; used by threaded liblzma and tools.

Risks: no-thread `mythread_once` is not thread-safe by design. Win95 once support is absent. Assertions check synchronization API errors, so release behavior depends on `NDEBUG`.

Test signals: threaded encoder/decoder tests on POSIX and Windows variants, timeout behavior under clock changes, and signal-mask inheritance checks.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/mythread.h -->
