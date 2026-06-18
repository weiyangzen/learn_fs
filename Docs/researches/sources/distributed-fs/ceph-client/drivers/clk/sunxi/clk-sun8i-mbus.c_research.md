# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-mbus.c

Builds the Allwinner A23 MBUS composite clock, combining mux, divider, and gate components into one critical memory-bus clock.

`sun8i_a23_mbus_setup()` counts parents, allocates a parent-name array, maps the register, allocates `clk_divider`, `clk_mux`, and `clk_gate`, fills component bitfields, and calls `clk_register_composite()` with `CLK_IS_CRITICAL`. The mux uses bits 25:24, the divider uses bits 2:0, and the gate uses bit 31. It then registers a simple OF provider.

The selected parent, divider, and gate bit persist in one hardware register. The clock is critical, so the CCF should not disable it as unused. The parent-name array is freed after registration because CCF deep-copies it. It uses CCF composite helpers, OF parent fill, early `CLK_OF_DECLARE`, and shared spinlock protection. It supplies the MBUS clock to memory/display/DMA consumers that cannot tolerate accidental gating.

The error path notes that composite registration may leak a bit after unregister. Parent count is not capped against the unused `SUN8I_MBUS_MAX_PARENTS` define. Test signals include boot survival with unused-clock disabling enabled, parent/divider readback, and memory/display traffic stability under rate changes.
