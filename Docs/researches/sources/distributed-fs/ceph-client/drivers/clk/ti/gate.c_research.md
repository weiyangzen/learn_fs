# sources/distributed-fs/ceph-client/drivers/clk/ti/gate.c

Purpose: OMAP/TI gate clock registration and operations. It registers standalone gates, wait gates, clockdomain-only gates, HSDIV gates, and composite gate components.

Important APIs/types/functions: exported `omap_gate_clk_ops`, internal `omap_gate_clkdm_clk_ops`, `omap_gate_clk_hsdiv_restore_ops`, `_register_gate()`, `_of_ti_gate_clk_setup()`, `_of_ti_composite_gate_clk_setup()`, and multiple `CLK_OF_DECLARE()` setup functions. `omap36xx_gate_clk_enable_with_hsdiv_restore()` implements errata i556.

Control flow: standalone setup parses register/bit unless the gate only controls a clockdomain, validates one parent, handles `ti,set-rate-parent` and inverted enable, registers a `clk_hw_omap`, and adds an OF provider. Composite setup builds a `clk_hw_omap` gate component for later assembly. Runtime ops use default OMAP enable/disable or clockdomain-only enable/disable. HSDIV restore first enables the gate, then toggles the parent divider register to reload divider values after PWRDN.

State and persistence: each gate stores enable register, bit, flags, optional hardware ops, and clockdomain pointer after init. Context restore delegates to generic `clk_gate_restore_context`.

Dependencies/integration: depends on `clkt_dflt.c`, `clockdomain.c`, `clkt_iclk.c` ops for variants, `ti_clk_get_reg_addr()`, and composite assembly.

Risks: HSDIV workaround assumes a specific parent hierarchy. Clockdomain-only gates skip register parsing and rely entirely on clockdomain callbacks. Inverted enable flags must match hardware polarity.

Test signals: enable/disable each compatible gate type, composite gate assembly, inverted gate behavior, HSDIV errata reload, and context restore after suspend.
