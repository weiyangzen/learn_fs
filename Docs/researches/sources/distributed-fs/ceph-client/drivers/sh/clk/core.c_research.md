# sources/distributed-fs/ceph-client/drivers/sh/clk/core.c

Purpose: legacy SuperH clock framework core. It registers `struct clk` instances, manages parent/child topology, enable reference counts, rate calculation/rounding helpers, MMIO register mappings, and resume/late-disable behavior.

Important APIs and functions: exported APIs include `clk_register/unregister`, `clk_enable/disable`, `clk_get_rate`, `clk_set_rate`, `clk_set_parent`, `clk_get_parent`, `clk_round_rate`, `clk_rate_table_build`, rate-table/range rounders, `followparent_recalc`, `clk_reparent`, `propagate_rate`, `recalculate_root_clocks`, and `clk_enable_init_clocks`. Mapping helpers establish shared `clk_mapping` ioremaps with kref lifetime. PM hooks reapply parent/rate settings on resume, and `clk_late_init` disables unused clocks after boot.

Control flow: platforms register clock objects; registration maps registers, links parent/child lists, and optionally calls legacy init ops. Enable walks parents before enabling a leaf, while disable decrements and may disable parent after child usecount hits zero. Rate changes call ops, recalc, then propagate recursively to children.

State and dependencies: global `clock_list`, `root_clks`, spinlock, mutex, `allow_disable`, per-clock usecount/mapping/rate/children. Dependencies include legacy `linux/sh_clk.h`, cpufreq tables, MMIO, syscore PM, and kernel clk consumers. Risks are global locking correctness, usecount imbalance, recursive parent propagation, mapping lifetime, late-init disabling hardware too aggressively, and legacy API divergence from common-clk. Test signals include platform boot clock tree, cpufreq rate tables, suspend/resume rate restoration, warnings on disable with zero usecount, and register access under lockdep.
