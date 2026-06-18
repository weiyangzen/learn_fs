# File Research: sources/block-storage/linux-dm/drivers/md/bcache/trace.c

`trace.c` instantiates bcache tracepoints by defining `CREATE_TRACE_POINTS` before including `<trace/events/bcache.h>`. It then exports the tracepoint symbols GPL-only so other bcache compilation units and modules can use them.

Exported tracepoints cover request start/end, bypass decisions, reads/writes/retries, cache insertion, journal replay/write/full events, btree cache pressure, btree reads/writes, node allocation/free, GC start/end/copy/collision, btree key insertion and structural changes, invalidation, allocation failure, and writeback/collision events.

The file has no runtime logic beyond tracepoint creation/export, but it is the central build unit that makes all `trace_bcache_*()` calls in the other bcache files link correctly.
