# sources/distributed-fs/ceph-client/drivers/clk/clk-eyeq.c


### Purpose
`clk-eyeq.c` is the Mobileye EyeQ5/EyeQ6 clock provider for OLB regions. It exposes read-only PLLs as fixed-factor clocks, divider clocks, fixed-factor child clocks, and optional auxiliary reset/pinctrl/PHY devices, with special early providers for clocks required before normal platform probing.

### Important APIs, Types, And Functions
Data tables use `struct eqc_pll`, `struct eqc_div`, `struct eqc_fixed_factor`, `struct eqc_match_data`, and `struct eqc_early_match_data`. Important logic includes `eqc_pll_parse_registers()` for PLL register decoding and spread-spectrum accuracy, `eqc_pll_downshift_factors()` for fixed-factor width limits, `eqc_probe_init_plls()`, `eqc_probe_init_divs()`, `eqc_probe_init_fixed_factors()`, `eqc_auxdev_create_optional()`, `eqc_probe()`, and `eqc_early_init()`.

### Control Flow, State, And Persistence
Late probe ioremaps the OLB resource, creates optional auxiliary devices, allocates onecell data, marks early-owned clocks as errors, registers late PLLs/dividers/fixed factors, and adds an OF provider. Early init allocates a larger onecell array, marks not-yet-late clocks as `-EPROBE_DEFER`, maps OLB, registers boot-critical PLLs and child fixed factors, and installs a provider through `CLK_OF_DECLARE_DRIVER()`. PLLs are read-only snapshots of hardware state; dividers read hardware fields through generic divider registration. State persists as registered clock providers and auxiliary devices using the mapped OLB base.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF address mapping, 64-bit non-atomic register reads, CCF fixed-factor/divider helpers, auxiliary bus creation, EyeQ DT bindings, and ordering between early and late providers. Risks include no unmap/free path for late `ioremap()` and `kzalloc_flex()` allocations, early-provider precedence subtleties, failure to parse unlocked PLLs, precision loss while downshifting large fractional factors, and source snapshot syntax anomalies near one EyeQ6H match table. Test signals include early boot clocks for timer/UART, late provider override behavior, PLL bypass/locked/fractional/spread-spectrum decoding, deferred lookup for late clocks, divider parent fallback to early provider, auxiliary device creation, and all compatible variants building.
