# sources/distributed-fs/ceph-client/tools/perf/util/cacheline.c

## sources/distributed-fs/ceph-client/tools/perf/util/cacheline.c

Purpose: this file determines and caches the system data-cache line size for perf's memory/cacheline analysis helpers.

Important API: `cacheline_size()` returns a cached integer. On systems with `_SC_LEVEL1_DCACHE_LINESIZE`, it uses `sysconf`; otherwise it reads `devices/system/cpu/cpu0/cache/index0/coherency_line_size` from sysfs and logs debug failure.

Control flow: the first call initializes a static `size`; subsequent calls return the cached value.

State and persistence: static process-local `size` persists for the program lifetime. No filesystem writes occur.

Dependencies and integration: used by `cacheline.h` inline address/offset helpers and memory analysis code. Depends on unistd/sysconf or perf sysfs helpers.

Risks: if discovery fails, `size` can remain zero, and callers doing bit operations with `size - 1` would behave incorrectly. Systems with heterogeneous cacheline sizes are represented by one value from CPU0/sysconf.

Test signals: run on platforms with and without `_SC_LEVEL1_DCACHE_LINESIZE`, mock sysfs read failure, and verify consumers handle zero or add fallback behavior.
