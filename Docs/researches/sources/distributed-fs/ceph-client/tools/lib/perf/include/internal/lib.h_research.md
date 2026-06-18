## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/lib.h

Purpose: Declares small libperf internal process-wide helpers.

Important APIs/types: Global `page_size`; robust I/O helpers `readn()`, `writen()`, and `preadn()`.

Control flow: No implementation here. Callers rely on `libperf_init()` to initialize `page_size`, and I/O helpers to transfer exact byte counts.

State/persistence: `page_size` is global process state. I/O helpers operate on caller FDs.

Dependencies/integration: Included by core, evsel, evlist, mmap, and other internals. Requires `<sys/types.h>`.

Risks: Header guard closing comment incorrectly names `CPUMAP`, a documentation issue. Users must not read `page_size` before initialization unless implementation provides a default elsewhere.

Test signals: Build all internal users, verify exact-read/write helpers on short reads/writes/EINTR, and check page-size initialization.
