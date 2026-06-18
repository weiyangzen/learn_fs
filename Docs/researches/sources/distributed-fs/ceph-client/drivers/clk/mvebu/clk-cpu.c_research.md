# sources/distributed-fs/ceph-client/drivers/clk/mvebu/clk-cpu.c

Purpose: Armada XP per-CPU clock provider with dynamic divider updates through clock-complex and PMU DFS registers.

Important APIs/functions: `clk_cpu_recalc_rate`, `clk_cpu_determine_rate`, `clk_cpu_set_rate`, `clk_cpu_off_set_rate`, and `clk_cpu_on_set_rate` implement CCF operations. `of_cpu_clk_setup` creates `cpuN` clocks. `of_mv98dx3236_cpu_clk_setup` supplies a simple provider for mv98dx3236.

Control flow: early setup maps clock-complex and optional PMU DFS registers, allocates per-CPU clock structs, registers one clock per possible CPU, and publishes a onecell provider. Rate changes while disabled update divider registers directly and trigger reload; while enabled they program PMU DFS ratios and call `mvebu_pmsu_dfs_request`.

State and persistence: CPU divider state is hardware-backed; software stores per-CPU register offsets, parent name, and optional PMU DFS address.

Dependencies and integration: CCF, OF early init, `num_possible_cpus`, Armada PMSU DFS API, and SMP CPU topology.

Risks: `recalc_rate` divides by raw divider with no zero guard. Dynamic scaling is unavailable without PMU DFS mapping. `clk_data.clk_num` is fixed to `MAX_CPU` even if fewer CPUs/clks were allocated, which can expose invalid entries.

Test signals: CPU clock lookup for all possible CPUs, cpufreq transitions on online/offline CPUs, missing PMU DFS warning path, and mv98dx3236 simple provider behavior.
