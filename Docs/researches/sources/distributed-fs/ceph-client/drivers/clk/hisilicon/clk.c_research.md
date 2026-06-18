## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk.c

### Purpose
`clk.c` is the shared Hisilicon clock-registration library. It allocates clock-provider data, maps registers, and converts SoC-specific descriptor tables into common clock framework objects.

### Important APIs, Types, And Functions
Allocation helpers are `hisi_clk_alloc()` for platform drivers and `hisi_clk_init()` for early OF init. Registration helpers include `hisi_clk_register_fixed_rate()`, `hisi_clk_register_fixed_factor()`, `hisi_clk_register_mux()`, `hisi_clk_register_phase()`, `hisi_clk_register_divider()`, `hisi_clk_register_gate()`, `hisi_clk_register_gate_sep()`, and `hi6220_clk_register_divider()`.

### Control Flow
Each helper loops over a descriptor array, creates a CCF object, stores it at `clk_data.clks[id]`, and optionally registers a clkdev alias. Fixed-rate/factor/mux/divider/gate helpers unwind successfully registered clocks on a hard error. Separated-gate and Hi6220 divider helpers log errors and continue.

### State, Persistence, And Dependencies
`hisi_clock_data` holds the onecell table and register base. A file-global `hisi_clk_lock` serializes register updates across mux/divider/gate types. The file depends on OF address mapping, platform resources, CCF registration APIs, and custom separated-gate/Hi6220 divider/phase helpers.

### Integration Points
Every Hisilicon SoC file in this subset builds on these functions. Platform CRG drivers call `hisi_clk_alloc()` and add providers themselves; early OF drivers call `hisi_clk_init()`, which also adds the provider.

### Risks
`hisi_clk_init()` adds the OF provider before clocks are registered, so early consumers could theoretically see partially populated tables during init. Error paths for `hisi_clk_init()` do not unmap `of_iomap()` on allocation failure. Continue-on-error helpers can leave holes in provider tables.

### Test Signals
Compile all Hisilicon clock users, boot representative SoCs, force registration failures in fault-injection builds, check alias registration, and validate no duplicate IDs or out-of-range IDs in SoC tables.
