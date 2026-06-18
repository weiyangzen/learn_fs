# sources/distributed-fs/ceph-client/drivers/interconnect/icc-clk.c

Purpose: exposes ordinary clocks as simple interconnect providers, translating peak bandwidth votes into clock enable/disable and `clk_set_rate()`.

Important APIs/types/functions: `struct icc_clk_node`, `struct icc_clk_provider`, provider callbacks `icc_clk_set()` and `icc_clk_get_bw()`, and exported `icc_clk_register()`, `devm_icc_clk_register()`, `icc_clk_unregister()`.

Control flow: registration creates two nodes per clock, links master to slave, fills onecell data, and registers the provider. `icc_clk_set()` disables on zero peak bandwidth; otherwise it prepares/enables the clock and sets the rate to `icc_units_to_bps(src->peak_bw)`.

State and persistence: devm allocations hold provider and node data. Each clock node tracks whether this wrapper enabled the clock; unregister disables any still-enabled clocks.

Dependencies/integration: common clock framework, `linux/interconnect-clk.h`, interconnect core APIs, onecell OF translation.

Risks and test signals: test enable failure, rate-set failure after enable, zero-rate disable, NULL clocks, duplicate IDs, unregister with active paths, and `icc_clk_get_bw()` leaving `avg` untouched.
