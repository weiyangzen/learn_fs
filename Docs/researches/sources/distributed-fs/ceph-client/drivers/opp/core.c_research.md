<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/core.c -->
# sources/distributed-fs/ceph-client/drivers/opp/core.c

## Purpose
`core.c` is the central implementation of the Linux generic OPP framework. It owns global OPP table registration, lookup, reference counting, dynamic OPP insertion/removal, availability changes, notifier dispatch, and the actual device transition sequence for clocks, regulators, interconnect bandwidth, PM-domain performance states, and required OPP dependencies. The file is not Ceph-specific; in this source tree it is kernel infrastructure used by device drivers that describe operating points.

## Important APIs, Types, And Functions
The global state is `opp_tables`, protected by `opp_table_lock`, plus an `opp_configs` xarray that stores opaque tokens from `dev_pm_opp_set_config()`. Per-table state is defined in `opp.h` as `struct opp_table`, with `opp_list`, `dev_list`, `kref`, `lock`, notifier `head`, clock/regulator/interconnect handles, required OPP tables/devices, and current transition state.

Public exported APIs include getters such as `dev_pm_opp_get_voltage()`, `dev_pm_opp_get_supplies()`, `dev_pm_opp_get_power()`, `dev_pm_opp_get_freq_indexed()`, `dev_pm_opp_get_level()`, `dev_pm_opp_get_required_pstate()`, latency/count helpers, search APIs for exact/ceil/floor frequency, level, bandwidth, and key matches, transition APIs `dev_pm_opp_set_rate()` and `dev_pm_opp_set_opp()`, table/config lifecycle APIs, dynamic add/remove, voltage adjustment, regulator sync, enable/disable, notifier registration, and table removal.

Internal helpers include `_add_opp_table_indexed()`, `_allocate_opp_table()`, `_opp_add()`, `_opp_compare_key()`, `_set_opp()`, `_disable_opp_table()`, `_set_required_opps()`, `_opp_set_regulators()`, `_opp_set_clknames()`, and `_opp_clear_config()`.

## Control Flow
Table lookup walks the global `opp_tables` list and matches devices through each table's `dev_list`, then returns a kref-held `opp_table`. Table creation uses a careful `opp_tables_busy` protocol: callers briefly hold `opp_table_lock`, drop it for allocations and framework calls that may re-enter OPP/debugfs/clock/interconnect code, then re-acquire it to publish the new table.

OPP searches share generic list-walking helpers. Exact, ceil, and floor queries select available or unavailable entries and increment the returned OPP kref. OPP list ordering is maintained by `_opp_compare_key()`, which compares all clocks, then peak bandwidths, then level.

The transition path is `_set_opp()`. It identifies the current OPP, skips no-op transitions unless forced, compares old and new keys to infer scaling direction, then sequences dependencies. On scale-up it sets required OPPs, PM-domain level, interconnect bandwidth, and regulator voltages before clocks. On scale-down it changes clocks first, then regulators, bandwidth, level, and required OPPs in reverse order. `dev_pm_opp_set_rate()` rounds the requested clock, finds the ceiling OPP, and can force a clock update when the same OPP still covers a different rounded frequency. Passing `NULL` or zero frequency disables bandwidth, the primary regulator, PM-domain level, and required OPP state.

## State And Persistence
The file persists kernel runtime state only. OPP tables live until their krefs reach zero; OPP entries live until their own krefs are dropped. Dynamic OPPs hold an extra table reference that is released when removed. Static OPPs are reference-counted through `parsed_static_opps`. Current programmed state is tracked by `current_opp`, `current_rate_single_clk`, and `enabled`.

Hardware-visible persistence is delegated to subsystems: `clk_set_rate()`, `regulator_set_voltage_triplet()`, `regulator_enable/disable()`, `icc_set_bw()`, and `dev_pm_domain_set_performance_state()`. Notifier chains report add, remove, enable, disable, and voltage-adjust events to interested clients.

## Dependencies And Integration Points
This file integrates with the clock framework, regulator framework, interconnect framework, PM domains/genpd, device tree helpers from `of.c`, debugfs hooks from `debugfs.c`, CPU helpers from `cpu.c`, and consumers through `<linux/pm_opp.h>`. The `__free(put_opp)` and `__free(put_opp_table)` cleanup attributes are used throughout to make reference release less error-prone.

## Risks
Transition ordering is high risk: wrong scale direction or an early return after partially updating dependencies can leave hardware overclocked, undervolted, or with stale bandwidth/performance state. `dev_pm_opp_get_voltage()` assumes a single supply and dereferences `supplies[0]`, so callers must not use it for multi-regulator tables. Duplicate detection mostly reports the first supply in warnings and duplicate policy. `opp_tables_busy` uses a busy wait with `cpu_relax()`, so table creation bugs could spin. Notifier callbacks are invoked after state changes and may observe partially removed objects if reference rules are violated.

## Test Signals
Useful tests include OPP table creation/removal races, duplicate dynamic/static OPP additions, ceil/floor searches with multi-clock and bandwidth tables, `set_rate()` scale-up/scale-down ordering under tracepoints, regulator failure injection, required-opps lazy-link failures, notifier ordering, `dev_pm_opp_clear_config()` token misuse, and KASAN/lockdep coverage for table and OPP lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/core.c -->
