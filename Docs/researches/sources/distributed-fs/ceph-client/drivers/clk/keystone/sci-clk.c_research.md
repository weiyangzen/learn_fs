# sources/distributed-fs/ceph-client/drivers/clk/keystone/sci-clk.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/sci-clk.c -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/sci-clk.c

### Purpose
`sci-clk.c` implements TI System Control Interface clock support for Keystone/K3 systems. It exposes firmware-managed clocks to the common clock framework and translates CCF operations into TI SCI protocol calls.

### Important APIs, Types, And Functions
Important types are `sci_clk_provider` and `sci_clk`. Clock ops include `sci_clk_prepare()`, `unprepare()`, `is_prepared()`, `recalc_rate()`, `determine_rate()`, `set_rate()`, `get_parent()`, and `set_parent()`. Discovery and registration are handled by `_sci_clk_build()`, `sci_clk_get()`, `ti_sci_scan_clocks_from_dt()` or `ti_sci_scan_clocks_from_fw()`, `ti_sci_init_clocks()`, `ti_sci_clk_probe()`, and `ti_sci_clk_remove()`.

### Control Flow, State, And Persistence
Probe gets a TI SCI handle, selects firmware-wide or DT-driven clock discovery at compile time, registers each discovered clock with generated names like `clk:<dev>:<clk>`, and adds an OF hw provider using a two-cell specifier. CCF prepare/put calls acquire or release firmware clock usage; rate operations ask firmware for current, best-match, and set frequencies; parent ops use firmware clock ID arithmetic. `determine_rate()` caches the last requested and resolved rate until parent changes.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on `TI_SCI_PROTOCOL`, firmware ABI behavior, OF phandle parsing for `clocks` and assigned-clock properties, sorted clock arrays for `bsearch()`, devm-managed CCF registration, and platform driver binding to `ti,k2g-sci-clk`. Risks include firmware scan boot-time cost, DT scan missing unused-but-needed clocks, parent count cropping to 255, cache staleness across firmware-side changes, and SCI errors returning zero rates or failed prepares. Test signals include assigned-clock handling, mux parent changes, rate setting within +/-10 percent window, duplicate DT references being de-duplicated, firmware scan builds, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/sci-clk.c -->
