# sources/distributed-fs/lizardfs/src/devtools/TracePrinter.h

Purpose: optional compile-time tracing helpers for function entry/exit and ad-hoc value logging.

Important APIs/types/functions: under `ENABLE_TRACES`, `ThreadPrinter` assigns per-thread ANSI colors and indentation, `TracePrinter` logs entry in its constructor and elapsed microseconds in its destructor, and macros `TRACETHIS`, `TRACETHIS1` through `TRACETHIS6`, `PRINTTHIS`, `PRINTTHISMSG`, and `MARKTHIS` create trace calls. Without `ENABLE_TRACES`, macros compile to `(void)0`.

Control flow: trace macros instantiate RAII objects in function scope; constructor prints `==>`, destructor prints `<==` with elapsed time. `ThreadPrinter` serializes color/indent map access with a static mutex, but printing itself happens after unlocking.

State and persistence: process-global static maps store indentation and color per `pthread_t`; output goes to stdout and is not persisted by this code.

Dependencies and integration: depends on pthreads, `gettimeofday`, `boost::format`, and `common/platform.h`; used only in builds enabling traces.

Risks: static maps grow with distinct thread IDs and are not pruned. ANSI output and stdout logging are unsuitable for normal daemon logs. Thread ID formatting with `%lx` assumes compatible `pthread_t` representation.

Test signals: no direct tests; compile coverage depends on `ENABLE_TRACES` builds.
