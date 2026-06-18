# sources/distributed-fs/ceph-client/tools/perf/util/config.h

Purpose: declares perf config structures, callback signatures, loading/iteration APIs, typed parsers, and iteration macros.

Important APIs/types: `struct perf_config_item`, `struct perf_config_section`, `struct perf_config_set`, `config_fn_t`, extern `config_exclusive_filename`, config load/apply/get/scan APIs, typed converters, lifecycle APIs, and iteration macros.

Control flow: users apply the cached global set with `perf_config` or explicitly load/manipulate `perf_config_set` instances and iterate section/item pairs.

State and persistence: config sets own section/item strings and values in memory. `config_exclusive_filename` redirects loading to one file.

Dependencies and integration: includes Linux list and bool; used by command setup, UI/color, stat, callgraph, build-id, and subsystem config callbacks.

Risks: iteration macros expand to nested loops, so early exit needs `goto`. Value pointers are owned by config sets.

Test signals: macro users, explicit config loading, callback failures, and delete/leak checks.
