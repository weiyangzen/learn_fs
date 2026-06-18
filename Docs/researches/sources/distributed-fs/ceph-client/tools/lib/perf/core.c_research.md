## sources/distributed-fs/ceph-client/tools/lib/perf/core.c

Purpose: Provides libperf global initialization and logging hook.

Important APIs/functions: `libperf_init()` initializes global `page_size` and installs a caller-supplied print callback. `libperf_print()` formats variadic messages and dispatches to the current callback. `__base_pr()` is the default stderr printer.

Control flow: Before initialization, logging uses `__base_pr`. `libperf_init()` sets `page_size = sysconf(_SC_PAGE_SIZE)` and replaces the callback, which may be NULL to suppress output.

State/persistence: Mutates global `page_size` and static `__libperf_pr`. These are process-wide.

Dependencies/integration: Uses public `<perf/core.h>`, internal `page_size` declaration, and libc `sysconf`/`vfprintf`.

Risks: No locking around global callback/page size; concurrent initialization/logging is not synchronized. `sysconf` failure is not checked. Passing NULL intentionally disables logging.

Test signals: Verify default logging, custom callback invocation, NULL callback suppression, initialized page size, and thread-safety assumptions in multithreaded users.
