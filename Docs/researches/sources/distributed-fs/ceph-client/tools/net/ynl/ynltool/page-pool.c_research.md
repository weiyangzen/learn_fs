# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/page-pool.c

Purpose: `ynltool page-pool` subcommand implementation. It dumps netdev page-pool state and statistics, either grouped by device or listed per page pool, with optional JSON output.

Important APIs/types: `struct pp_stat` aggregates live/zombie counts, refs, bytes, and recycling counters. `struct pp_stats_array` stores dynamic per-ifindex aggregates. `find_ifc()`, `count_pool()`, `aggregate_device_stats()`, and `find_pool_stat_in_list()` build summaries. Print functions emit JSON/plain recycling, aggregate stats, and individual pool lists. `do_stats()` parses `group-by` and `zombies`, opens `ynl_netdev_family`, calls `netdev_page_pool_get_dump()` and `netdev_page_pool_stats_get_dump()`, prints, frees, and closes.

Control flow/state: default grouping is by device. `zombies` implies per-pool output and filters to detached pools. Dynamic aggregation starts with 64 slots and doubles with `reallocarray()`.

Dependencies/integration: depends on generated `netdev-user.h`, YNL runtime, global JSON writer from `main.c`, `if_indextoname()`, and command dispatch from `main.h`.

Risks/test signals: `find_ifc()` increments before resize and does not check `reallocarray()` failure, so allocation failure can corrupt state. Aggregation reads `pp->info.ifindex` in stats entries and assumes info is present. Signals include `ynltool page-pool stats`, `group-by page-pool`, `zombies`, and `--json` validity.
