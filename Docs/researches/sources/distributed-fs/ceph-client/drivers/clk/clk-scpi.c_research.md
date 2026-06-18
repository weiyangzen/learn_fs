<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-scpi.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-scpi.c

### Purpose
`clk-scpi.c` exposes ARM SCPI firmware clocks. It supports variable clocks controlled by direct rate get/set calls and DVFS clocks controlled by firmware OPP indexes, and creates a virtual `scpi-cpufreq` device when DVFS clocks are present.

### Important APIs, Types, And Functions
`struct scpi_clk` stores clock ID, `clk_hw`, optional DVFS info, and `scpi_ops`. Operation tables are `scpi_clk_ops` for variable clocks and `scpi_dvfs_ops` for OPP-index clocks. Key functions include `scpi_clk_ops_init()`, `scpi_clk_add()`, `scpi_of_clk_src_get()`, `scpi_clocks_probe()`, `scpi_clocks_remove()`, `__scpi_dvfs_round_rate()`, and `scpi_dvfs_set_rate()`.

### Control Flow, State, And Persistence
Probe requires `get_scpi_ops()`, scans child nodes under `arm,scpi-clocks`, matches `arm,scpi-dvfs-clocks` or `arm,scpi-variable-clocks`, and registers each named/indexed clock. Variable clocks query firmware min/max ranges; DVFS clocks query OPP tables and convert requested rates to exact OPP indexes. Provider lookup searches the registered array by SCPI clock ID rather than array position. A module-global `cpufreq_dev` is registered once for DVFS provider presence and unregistered during remove.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include legacy ARM SCPI firmware ops, DT child properties `clock-output-names` and `clock-indices`, OF provider registration, and cpufreq integration. Risks include global `cpufreq_dev` across possible instances, remove deleting the wrong provider node in the child loop, no parent support, firmware OPP ordering assumptions, and direct `get_scpi_ops()` lifetime. Test signals include variable clock range enforcement, DVFS OPP rounding and exact set, invalid child property failures, provider phandle lookup by ID, cpufreq platform-device creation/removal, and firmware error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-scpi.c -->
