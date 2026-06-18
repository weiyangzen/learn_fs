<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-palmas.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-palmas.c

### Purpose
`clk-palmas.c` exposes the Palmas PMIC 32 kHz clock outputs `clk32kg` and `clk32kgaudio` through the common clock framework. It supports direct software enablement and optional external sleep-control pins.

### Important APIs, Types, And Functions
`struct palmas_clk32k_desc` describes control register, active/sleep masks, external requestor ID, and stabilization delay. `struct palmas_clock_info` stores the parent MFD handle, descriptor, `clk_hw`, and selected external-control pin. Clock ops are `palmas_clks_prepare()`, `palmas_clks_unprepare()`, `palmas_clks_is_prepared()`, and `palmas_clks_recalc_rate()`. Probe uses `palmas_clks_get_clk_data()`, `palmas_clks_init_configure()`, `devm_clk_hw_register()`, and `of_clk_add_hw_provider()`.

### Control Flow, State, And Persistence
Probe selects descriptor data from OF match, reads optional `ti,external-sleep-control`, registers one fixed 32768 Hz clock, clears sleep mode, and, when externally controlled, prepares the clock and configures `palmas_ext_control_req_config()`. Prepare sets the active bit and delays when requested; unprepare avoids clearing the bit when external control owns disable behavior. Remove only deletes the OF provider; allocations are devm-managed.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on the Palmas MFD core, `palmas_read()`, `palmas_update_bits()`, external requestor programming, OF child nodes, and consumers of 32 kHz PMIC clocks. Risks include leaked prepared state for externally controlled clocks on remove, invalid DT external-control values falling back to software mode, register update failures during clock ops, and fixed `CLK_IGNORE_UNUSED` keeping outputs on. Test signals include toggling both clock outputs, external ENABLE1/ENABLE2/NSLEEP control behavior, sleep-mask clearing, DT property validation, and consumers receiving 32768 Hz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-palmas.c -->
