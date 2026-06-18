# sources/distributed-fs/ceph-client/drivers/clk/mvebu/cp110-system-controller.c

Purpose: CP110 system-controller clock provider for core clocks and 32 possible gateable peripheral clocks.

Important APIs/functions: `cp110_syscon_common_probe` registers core and gate clocks. `cp110_register_gate`, `cp110_gate_enable`, `cp110_gate_disable`, and `cp110_gate_is_enabled` implement custom regmap-backed gates. `cp110_of_clk_get` decodes two-cell clock specifiers.

Control flow: probe gets the syscon regmap, reads NAND clock selection, allocates onecell data, registers PLL0 and derived PPv2/x2core/core/NAND/SDIO clocks, creates unique gate names, chooses each gate parent, registers gates, and publishes a custom provider. Legacy and modern platform drivers call the same common probe.

State and persistence: fixed-factor core clocks are static after probe; gates are controlled by `CP110_PM_CLOCK_GATING_REG`. Platform data stores clock HW pointers for cleanup.

Dependencies and integration: syscon parent, AP/CP unique naming helper, CCF, regmap, two-cell DT binding with clock type and index.

Risks: PCIe gates use `CLK_IGNORE_UNUSED` to avoid breaking active links, so unused-clock cleanup will not disable them. `gate_base_names` has sparse NULL entries; indexing must stay aligned with binding bits. Manual cleanup paths are complex.

Test signals: legacy and modern binding probe, two-cell clock lookup for core/gate types, NAND 400/core selection, PCIe active-link boot, and gate enable register tests.
