<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/of.c -->
# sources/distributed-fs/ceph-client/drivers/opp/of.c

## Purpose
`of.c` parses device-tree OPP bindings and connects them to the generic OPP core. It supports old `operating-points` v1 tuples, `operating-points-v2` tables, shared OPP tables, indexed OPP tables, named voltage/current properties, required-opps dependency graphs, interconnect bandwidth, CPU sharing masks, required performance-state translation, and Energy Model registration.

## Important APIs, Types, And Functions
Public APIs include `dev_pm_opp_of_get_opp_desc_node()`, `dev_pm_opp_of_find_icc_paths()`, `dev_pm_opp_of_add_table()`, `devm_pm_opp_of_add_table()`, indexed variants, CPU mask add/remove/share helpers, `of_get_required_opp_performance_state()`, `dev_pm_opp_of_has_required_opp()`, `dev_pm_opp_get_of_node()`, `dev_pm_opp_calc_power()`, and `dev_pm_opp_of_register_em()`. Internal mechanisms include `lazy_opp_tables`, `_managed_opp()`, `_opp_table_alloc_required_tables()`, `_of_opp_alloc_required_opps()`, `lazy_link_required_opp_table()`, `_opp_is_supported()`, `opp_parse_supplies()`, and `_opp_add_static_v2()`.

## Control Flow
Table initialization starts in `_of_init_opp_table()`, which reads backward-compatible latency/tolerance properties, detects genpd providers, obtains the indexed `operating-points-v2` node, sets shared/exclusive access, and pre-allocates required OPP table references from the first child OPP. Missing required tables place the table on `lazy_opp_tables`.

Adding a table uses `_of_add_table_indexed()`: it creates or finds an `opp_table`, then parses v2 if an OPP node exists, otherwise v1. V2 parsing iterates child nodes, allocates an OPP, reads key properties (`opp-hz`, peak/avg bandwidth, `opp-level`), checks `opp-supported-hw`, reads turbo/suspend/latency/supply properties, links required-opps when possible, and calls `_opp_add()`. After adding a table, `lazy_link_required_opp_table()` revisits pending tables and fills required OPP pointers when their target table appears.

CPU helpers add/remove OPP tables over masks and derive sharing masks by comparing `operating-points-v2` phandles plus `opp-shared`. Energy Model registration prefers per-OPP `opp-microwatt`; otherwise it uses `dynamic-power-coefficient` and voltage/frequency values.

## State And Persistence
The file stores OF node references in `opp_table->np` and `opp->np`, required table references in `required_opp_tables`, required OPP references in each OPP, static parse counts in `parsed_static_opps`, and optional interconnect paths in the table. All state is kernel runtime state backed by the DT; no DT is modified.

## Dependencies And Integration Points
This file depends on OF APIs, genpd, interconnect, Energy Model, CPU device-node helpers, and OPP core internals. It is the main bridge between platform firmware descriptions and consumers such as CPUFreq, devfreq, genpd, and power/thermal code.

## Risks
Required-opps lazy linking is subtle: until all tables are available, users may receive `-EBUSY` or OPPs may be marked unavailable. `_managed_opp()` shares tables only when the DT table has `opp-shared`; otherwise identical nodes can still produce separate tables. Supply parsing mutates `regulator_count` based on the first discovered property, so inconsistent OPP nodes fail later. 64-bit `opp-hz` is cast to `unsigned long`, which warns but still truncates on 32-bit. Energy Model registration fails if power data is incomplete.

## Test Signals
Test v1 and v2 bindings, named microvolt/microamp/microwatt properties, multi-clock `opp-hz`, interconnect peak/avg bandwidth counts, unsupported hardware masks, duplicate OPPs, suspend OPP selection, required-opps across genpds with late table registration, CPU shared masks, indexed tables, and Energy Model registration from both `opp-microwatt` and `dynamic-power-coefficient`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/of.c -->
