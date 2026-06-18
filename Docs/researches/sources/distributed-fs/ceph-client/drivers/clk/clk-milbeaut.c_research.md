# sources/distributed-fs/ceph-client/drivers/clk/clk-milbeaut.c

Purpose: Socionext Milbeaut M10V clock controller driver. It provides early PLL/fixed/rclk setup and platform-probed divider/mux clocks for the full clock controller.

Important APIs, types, and functions: data tables describe fixed-factor PLLs, fixed dividers, programmable dividers, and muxes. Custom `m10v_mux_ops` write mux values with a write-enable bit. `m10v_clk_divider` extends divider behavior with an optional `write_valid_reg` handshake. `m10v_cc_init()` is the early `CLK_OF_DECLARE_DRIVER` path; `m10v_clk_probe()` completes deferred clocks.

Control flow: early init allocates global onecell data, maps registers, initializes all exported clocks to `-EPROBE_DEFER`, registers bootloader-programmed PLL fixed factors, registers `rclk` needed by timers, and adds the provider. Platform probe maps the same block, registers programmable dividers, fixed dividers, and muxes, then verifies all exported IDs have real clocks. Divider set-rate writes value plus write-enable bit and optionally polls `CLKSEL(11)` until hardware clears the request.

State and persistence: state is MMIO register fields and global `m10v_clk_data`. Some clocks are early fixed-factor representations of bootloader state. A global spinlock protects mux/divider RMW.

Dependencies and integration points: depends on OF early clock setup, platform driver probing, common clock fixed/divider/mux helpers, MMIO polling, and Milbeaut register layout.

Risks and test signals: `m10v_clk_data` is global and shared across early/probe phases. Several custom registrations allocate with `kzalloc` and no explicit unregister in normal built-in use. Poll timeout only logs an error but still returns success. Test signals are timer availability from early `rclk`, later replacement of deferred clocks, divider handshake behavior, and onecell exported IDs.
