# sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.c

### Purpose
`cgu.c` implements the generic Ingenic Clock Generation Unit framework used by multiple JZ/X SoC clock tables. It turns declarative `ingenic_cgu_clk_info` entries into common clock framework clocks for external roots, PLLs, muxes, dividers, fixed dividers, gates, and custom SoC callbacks.

### Important APIs, Types, And Functions
Major internal operations are `ingenic_pll_recalc_rate()`, `ingenic_pll_determine_rate()`, `ingenic_pll_set_rate()`, PLL enable/disable/is_enabled, non-PLL parent/rate/gate operations, and `ingenic_register_clock()`. Public entry points are `ingenic_cgu_new()` and `ingenic_cgu_register_clocks()`. Gate helpers interpret `clear_to_gate`; divider helpers handle tables, busy bits, change-enable bits, stop bits, and parent bypass masks.

### Control Flow, State, And Persistence
`ingenic_cgu_new()` allocates a CGU, maps the OF MMIO region, records clock metadata, and initializes the spinlock. `ingenic_cgu_register_clocks()` allocates the onecell array, registers clocks in table order so parent indexes are available, and publishes the provider. Registration special-cases external clocks by obtaining named DT clocks and registering clkdev aliases. Runtime operations read/modify/write CGU registers under the shared CGU spinlock and poll stable/busy bits when hardware requires it.

### Dependencies, Integration Points, Risks, And Test Signals
The implementation depends on OF MMIO mapping, common clock registration, clkdev aliases, `readl_poll_timeout()`, and SoC tables with correct parent order. Risks include `BUG_ON()` for invalid parent/table encodings, insufficient parent array size, inaccurate PLL OD encodings, set-rate rejection when exact divider rates cannot be produced, and incomplete cleanup after provider failure. Test signals include booting every Ingenic compatible, rate changes through PLL/divider clocks, muxes with skipped parent slots, gate polarity tests, suspend/resume through PM helpers, and failure injection for missing external clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.c -->
