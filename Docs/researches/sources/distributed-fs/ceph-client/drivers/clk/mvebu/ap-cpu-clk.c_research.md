# sources/distributed-fs/ceph-client/drivers/clk/mvebu/ap-cpu-clk.c

Purpose: platform driver for Armada AP806/AP807 CPU cluster DFS clocks.

Important APIs/functions: `ap_cpu_clk_recalc_rate`, `ap_cpu_clk_determine_rate`, and `ap_cpu_clk_set_rate` implement per-cluster CCF operations. `ap_cpu_clock_probe` discovers active CPU clusters, creates cluster clocks, and registers a onecell provider. `ap806_dfs_regs` and `ap807_dfs_regs` encode SoC register layouts.

Control flow: probe obtains the parent syscon regmap, scans CPU nodes to determine whether cluster 1 exists, allocates clock data, creates one clock per cluster with a unique AP/CP name, and adds an OF provider. Set-rate writes divider fields, optionally writes AP807 secondary ratio, forces reload, requests ratio switch, polls stability, then clears the request bit.

State and persistence: cluster clock state is hardware divider/status registers; software stores cluster index, regmap, and layout descriptor.

Dependencies and integration: syscon parent node, CPU DT nodes, `ap_cp_unique_name`, CCF, regmap polling, and compatible data for `marvell,ap806-cpu-clock`/`ap807-cpu-clock`.

Risks: `recalc_rate` divides by the raw divider; invalid zero hardware state would fault. Cluster counting depends on CPU `reg` values and enabled nodes. Parent clocks are acquired by cluster index.

Test signals: cpufreq/DFS transitions, AP806 and AP807 boot, two-cluster and one-cluster DT variants, timeout handling, and `clk_summary` cluster names.
