<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.c

Purpose: OMAP1 common-clock implementation. It provides OMAP-specific recalc, gate, rate-rounding, set-rate, idle-control, DSP-domain, UART, SoSSI, external clock, and propagation operations for the clock data table.

Important APIs/types/functions: Important functions include `omap1_ckctl_recalc`, `omap1_select_table_rate`, `omap1_clk_set_rate_ckctl_arm`, `omap1_set_uart_rate`, `omap1_set_ext_clk_rate`, `omap1_set_sossi_rate`, `omap1_init_ext_clk`, `propagate_rate`, and exported `clk_ops`/`clkops` structures.

Control flow, state, and persistence: State includes `arm_idlect1_mask`, direct pointers to `api_ck`, `ck_dpll1`, and `ck_ref`, and spinlocks protecting shared hardware registers. Rate changes may reprogram DPLL from SRAM and update cached rates.

Dependencies and integration points: Important functions include `omap1_ckctl_recalc`, `omap1_select_table_rate`, `omap1_clk_set_rate_ckctl_arm`, `omap1_set_uart_rate`, `omap1_set_ext_clk_rate`, `omap1_set_sossi_rate`, `omap1_init_ext_clk`, `propagate_rate`, and exported `clk_ops`/`clkops` structures. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP register accessors, SRAM clock reprogramming, common clock framework, CPU/machine detection, and OPP data. Risks are hardware divisor constraints, register locking omissions, DSP-domain access requiring `api_ck`, and legacy sysc handling in clock ops. Test clk enable/disable, cpufreq rate changes, UART 12/48 MHz switching, SoSSI/external rates, and reset-unused-clocks.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 847 lines, 21663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.c -->
