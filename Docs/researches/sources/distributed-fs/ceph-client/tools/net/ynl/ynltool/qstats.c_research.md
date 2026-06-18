# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/qstats.c

Purpose: `ynltool qstats` subcommand implementation. It displays netdev queue statistics, queue-balance analysis, and HW GRO savings in plain or JSON forms.

Important APIs/functions: `print_json_qstats()` and `print_plain_qstats()` render raw device or per-queue stats. `qstats_dump()` opens `ynl_netdev_family`, optionally sets `scope`, calls `netdev_qstats_get_dump()`, and returns the list. `do_show()` parses `scope/group-by`. `compute_stats()`, `print_balance_stats()`, and JSON variant calculate mean, sample standard deviation, coefficient of variation, and normalized spread. `do_balance()` sorts queue stats by ifindex/type/id and analyzes RX/TX packet/byte distribution. `do_hw_gro()` estimates packet savings from HW GRO counters.

Control flow/state: global `scope` defaults to device aggregation. The command table maps `show`, `balance`, `hw-gro`, and `help`; default `qstats` selects `show` because it is first. `do_balance()` builds a sorted pointer array and temporary per-counter arrays per device/type group.

Dependencies/integration: generated `netdev-user.h`, YNL runtime, math library (`sqrt`, linked with `-lm`), JSON globals, and ifindex-to-name resolution.

Risks/test signals: static global scope can persist within one process between invocations if command paths were ever reused internally. `cmp_ifindex_type()` subtracts unsigned fields into int. Balance skips a device/type group when the first queue has no counters, which may miss later active queues. Signals are plain/JSON qstats output, per-queue scope, balance math, and HW GRO output on devices exposing counters.
