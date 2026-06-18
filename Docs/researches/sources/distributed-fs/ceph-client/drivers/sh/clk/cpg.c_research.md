# sources/distributed-fs/ceph-client/drivers/sh/clk/cpg.c

Purpose: helper library for SuperH Clock Pulse Generator clocks in the legacy framework. It implements module-stop, div4/div6, reparenting, and FSI divisor clock operations.

Important APIs and functions: `sh_clk_mstp_register` creates clocks with module-stop enable/disable ops. Div helpers include `sh_clk_div6_register`, `sh_clk_div6_reparent_register`, `sh_clk_div4_register`, `sh_clk_div4_enable_register`, and `sh_clk_div4_reparent_register`. `sh_clk_read/write/read_status` abstract 8/16/32-bit registers. `sh_clk_div_recalc/set_rate/round_rate/enable/disable` build frequency tables and manipulate divisor fields. FSI-DIV support uses `sh_clk_fsidiv_register` with dedicated recalc/round/set/enable/disable ops.

Control flow: platform clock arrays are passed to registration helpers; helpers assign ops, allocate frequency tables, initialize parent from hardware fields when needed, and call `clk_register`. Enable/disable and set-rate callbacks later write CPG registers through the mapped register pointer supplied by the core.

State and dependencies: per-clock state is in `struct clk` fields such as `enable_reg`, `status_reg`, divisor masks, parent tables, arch flags, and private div tables. Dependencies include `linux/sh_clk.h`, MMIO, cpufreq frequency tables, and parent clocks. Risks include invalid divisor tables, wrong register width flags, status polling timeout, div6 CKSTP quirks, parent-table mismatch, and leaked frequency-table allocation if later registration fails. Test signals are platform CPG registration, clock enable status-bit clearing, rate round/set correctness, parent switching, and FSI register behavior.
