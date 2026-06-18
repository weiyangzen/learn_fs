# sources/distributed-fs/openafs/src/rxkad/stats.h

Purpose: Defines rxkad statistics structures and increment/aggregation macros for threaded and non-threaded builds.

Important APIs/types: `struct rxkad_stats` or `rxkad_stats_t` tracks connections, destruction paths, expiry, challenge/response counts, packet prepare/check counts, encrypted/decrypted bytes, fcrypt/DES operations, object counts, and spares. Pthread builds maintain `rxkad_global_stats`, `rxkad_stats_key`, and macros that lazily create per-thread stat records. Non-pthread builds mutate global `rxkad_stats` directly.

Control flow and state: Pthread stats are inserted into a global doubly linked list and aggregated by `rxkad_stats_agg` in `rxkad_common.c`. Macros allocate thread-local records on first use.

Dependencies and integration: Included by rxkad client/server/common and fcrypt code; uses pthreads and `opr_Verify` in threaded builds.

Risks: Comments explicitly accept nearly accurate aggregation. Thread-local allocations are not freed by a destructor in this header. OpenBSD-specific macros disable add/sub operations due to known issues.

Test signals: Stress tests with `-printstats` and packet operations drive counters; build matrix coverage is important because macro behavior differs by pthread/kernel platform.
