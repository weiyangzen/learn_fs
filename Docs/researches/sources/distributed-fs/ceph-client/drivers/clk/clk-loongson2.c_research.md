# sources/distributed-fs/ceph-client/drivers/clk/clk-loongson2.c

Purpose: platform clock driver for Loongson2/LS2K SoC families. It registers PLL, scale, divider, gate, and fixed clocks from SoC-specific clock tables.

Important APIs, types, and functions: `loongson2_clk_board_info` is the central table format, with macros for `CLK_PLL`, `CLK_SCALE`, `CLK_SCALE_MODE`, `CLK_DIV`, `CLK_GATE`, and `CLK_FIXED`. `loongson2_clk_provider` owns MMIO base, device, lock, and onecell data. Custom recalc ops handle PLL and frequency-scale clocks; standard common-clock helpers register dividers, gates, and fixed-rate clocks.

Control flow: probe gets match data and reference clock parent name, computes the maximum clock ID, allocates a flexible provider, maps registers, initializes all onecell slots to `-ENOENT`, then iterates table entries. Each entry selects a registration path based on type and stores the resulting hw by table ID. The provider is added after all entries register.

State and persistence: hardware state is 64-bit clock control registers read through non-atomic lo/hi helpers. Divider/gate updates use a provider spinlock. Table data is static and the provider is devm-managed.

Dependencies and integration points: depends on Loongson DT clock bindings, OF/platform matching for multiple compatible strings, common gate/divider/fixed helpers, 64-bit MMIO accessors, and onecell provider consumers.

Risks and test signals: the probe loop indexes `data[i]` up to `clks_num`, assuming table IDs are dense and in order; sparse or out-of-order tables could read sentinel/invalid entries. PLL recalc divides by register `div` without zero guard. Gate bit indexes can exceed 31 for 64-bit registers while generic gate helpers operate on 32-bit registers, so high-bit gates need validation. Test signals are each compatible's full ID map, fixed clocks, high-bit gates, and rate recalc with bootloader-programmed PLLs.
