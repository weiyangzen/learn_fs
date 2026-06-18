# sources/distributed-fs/ceph-client/drivers/clk/clk-npcm7xx.c

Purpose: Nuvoton NPCM7xx clock generator driver. It is read-mostly: bootloader initializes hardware, and the driver registers PLLs, muxes, fixed dividers, and dividers so consumers can query current rates.

Important APIs, types, and functions: `npcm7xx_clk_pll` and `npcm7xx_clk_pll_ops` recalculate PLL rates from PLLCON fields. Tables `npcm7xx_plls`, `npcm7xx_muxes`, and `npcm7xx_divs` describe all registered clocks and exported onecell IDs. `npcm7xx_clk_init()` is the `CLK_OF_DECLARE` entry.

Control flow: init converts the DT resource to an MMIO mapping, allocates onecell data, initializes exported IDs to `-EPROBE_DEFER`, registers PLLs, registers fixed `/2` PLL clocks, registers mux-table clocks against `CLKSEL`, registers divider clocks against `CLKDIV*`, and adds the OF provider. Failures free the onecell data and unmap the base.

State and persistence: hardware state is bootloader-programmed clock generator registers. Software state is allocated clock objects and onecell data. A global spinlock protects mux/divider operations even though the driver comments emphasize reading current settings.

Dependencies and integration points: depends on DT clock bindings, OF early clock setup, common clock mux/divider/fixed-factor helpers, MMIO, bitfield helpers, and onecell provider consumers.

Risks and test signals: PLL recalc divides by `indv * otdv1 * otdv2` without zero checks. `of_node_put(clk_np)` is called on the node passed to the OF declare callback, which may not be owned by the function. Error paths do not unregister already registered clocks. Test signals are exported ID coverage, PLL recalc from real boot registers, mux table mappings, divider rates, and failure behavior on invalid register fields.
