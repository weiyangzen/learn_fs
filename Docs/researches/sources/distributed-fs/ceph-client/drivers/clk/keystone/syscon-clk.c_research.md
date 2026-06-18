# sources/distributed-fs/ceph-client/drivers/clk/keystone/syscon-clk.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/syscon-clk.c -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/syscon-clk.c

### Purpose
`syscon-clk.c` implements syscon-backed TI gate clocks, primarily ePWM time-base clocks and AM62 audio reference clock gates. It exposes bit-controlled gates in simple MMIO registers through common clock framework providers.

### Important APIs, Types, And Functions
Important types are `ti_syscon_gate_clk_priv` and `ti_syscon_gate_clk_data`. Core functions are `ti_syscon_gate_clk_enable()`, `disable()`, `is_enabled()`, `ti_syscon_gate_clk_register()`, and `ti_syscon_gate_clk_probe()`. Static data tables cover AM654 EHRPWM, AM64 ePWM, AM62 ePWM, and AM62 audio refclk compatibles.

### Control Flow, State, And Persistence
Probe matches a compatible to a data table, maps the single MMIO resource, creates a regmap, counts gate entries, validates that AM62 audio refclk has a parent, allocates onecell hw data, registers each gate clock using an optional parent, then installs either a simple or onecell provider. Runtime enable/disable writes the gate bit through regmap; `is_enabled()` reads the same bit.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on platform-device probing, OF match data, devm MMIO/regmap setup, common clock gate semantics, and child consumers using the provider. Risks include warnings but continued provider registration when individual gate registration fails, generated names changing when a parent is present, single-parent assumption, and regmap write errors being ignored on disable/is_enabled. Test signals include clock lookup for each compatible, ePWM time-base enable bits, AM62 audio parent requirement, multi-clock onecell index behavior, and module unload through devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/syscon-clk.c -->
