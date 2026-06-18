# sources/compression/zstd/lib/common/threading.h

## Purpose
`threading.h` abstracts zstd's small pthread-like synchronization surface across Windows, POSIX, and non-threaded builds. It lets `pool.c` use one set of mutex, condition, thread-create, and join names without platform-specific branches.

## Important APIs, Types, and Functions
For Windows threaded builds it configures `WINVER`, `_WIN32_WINNT`, `WIN32_LEAN_AND_MEAN`, includes `windows.h`, maps mutexes to `CRITICAL_SECTION`, conditions to `CONDITION_VARIABLE`, and declares `ZSTD_pthread_create()`/`ZSTD_pthread_join()` over `HANDLE`. For POSIX threaded builds it includes `<pthread.h>` and either maps directly to pthread types/macros in release mode or declares debug heap-backed wrappers when `DEBUGLEVEL >= 1`. For non-threaded builds it typedefs mutex and condition types to `int` and turns all synchronization operations into no-ops.

## Control Flow, State, and Persistence
The header itself has no dynamic state. Its preprocessor flow selects exactly one implementation family based on `ZSTD_MULTITHREAD`, `_WIN32`, and `DEBUGLEVEL`. The selected macros control whether synchronization calls actually block, are direct pthread calls, wrap Windows primitives, or compile away in single-threaded builds.

## Dependencies and Integration Points
It includes `debug.h` for `DEBUGLEVEL` and, on Windows, temporarily undefines and restores `ERROR` around `windows.h` to avoid macro conflicts with zstd's `ERROR(name)` convention. `threading.c` provides Windows thread and POSIX debug wrapper functions, and `pool.c` is the main consumer.

## Risks and Test Signals
Build-configuration drift is the main risk. In non-threaded builds synchronization no-ops are correct only because `pool.c` also executes jobs synchronously. In debug POSIX builds the mutex and condition types are pointers, so any caller that assumes raw pthread layout would fail. Tests should compile and run threaded and non-threaded builds, Windows and POSIX builds, and debug-level builds that exercise every wrapper macro path.
