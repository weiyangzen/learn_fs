
# sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks-list.h

Purpose: central X-macro list of supported perf hook names.

Important APIs/types/functions: expands `PERF_HOOK(record_start)`, `PERF_HOOK(record_end)`, and `PERF_HOOK(test)` wherever included.

Control flow: no direct execution; inclusion context decides whether declarations, definitions, inline invokers, or arrays are generated.

State and persistence: no state, but each hook name produces global hook descriptor/function pointer storage in `perf-hooks.c`.

Dependencies: requires the including file to define `PERF_HOOK`.

Integration points: used by `perf-hooks.h` and `perf-hooks.c` to keep declarations and implementation arrays synchronized.

Risks: adding a hook changes public API and global symbols; forgetting to include this list in all generation contexts would desynchronize hooks. Test signals include compile/link coverage and hook set/get/invoke tests for all names.
