# sources/compression/zstd/lib/common/threading.c

## Purpose
`threading.c` implements the nontrivial parts of zstd's pthread compatibility layer. It provides Windows thread creation/join wrappers and debug-mode POSIX mutex/condition allocation wrappers, while emitting a dummy symbol so the translation unit is never empty.

## Important APIs, Types, and Functions
The file defines `g_ZSTD_threading_useless_symbol`. On Windows threaded builds it defines `ZSTD_thread_params_t`, helper thread entry `worker()`, `ZSTD_pthread_create()`, and `ZSTD_pthread_join()`. On POSIX threaded debug builds it implements `ZSTD_pthread_mutex_init()`, `ZSTD_pthread_mutex_destroy()`, `ZSTD_pthread_cond_init()`, and `ZSTD_pthread_cond_destroy()` as heap-allocating wrappers around pthread primitives.

## Control Flow, State, and Persistence
The Windows create path initializes a stack `ZSTD_thread_params_t`, creates a condition and mutex, starts `_beginthreadex()` with the stack object, then waits until the worker copies `start_routine` and `arg` and signals `initialized`. This handshake prevents the parent from returning while the child still depends on stack memory. The worker then calls the user start routine and exits. Join waits indefinitely, closes the handle, and maps wait results to 0, `EINVAL`, or `GetLastError()`. POSIX debug wrappers allocate mutex/condition objects so missing init/destroy becomes visible as crashes or sanitizer leaks.

## Dependencies and Integration Points
It includes `threading.h`. Windows builds also include `<process.h>` and `<errno.h>`. POSIX debug builds request malloc/free from `zstd_deps.h`. `pool.c` consumes the wrapper API without knowing whether it is backed by Windows condition variables, direct pthread objects, debug heap pointers, or no-op non-threaded macros.

## Risks and Test Signals
Windows creation depends on the initialization handshake being correct; removing it would introduce a stack lifetime race. Error paths must destroy any synchronization primitives already initialized. POSIX debug wrappers intentionally change the type shape to pointers, so macros in `threading.h` must dereference consistently. Test signals include thread creation failure injection, Windows join behavior, debug builds under ASan/LSan catching missing destroy paths, and thread pool tests that exercise create, wait, signal, broadcast, and join.
