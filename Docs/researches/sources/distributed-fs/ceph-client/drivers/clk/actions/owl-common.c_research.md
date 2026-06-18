# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-common.c

Purpose: this is the shared OWL clock registration and regmap setup layer. It maps the platform CMU MMIO resource into a 32-bit regmap, installs that regmap into every `owl_clk_common`, and registers clocks as a onecell provider.

Important functions: `owl_clk_regmap_init()` calls `devm_platform_ioremap_resource()`, initializes `devm_regmap_init_mmio()` with 32-bit registers/stride and `max_register = 0x00cc`, then stores the regmap in the descriptor. `owl_clk_set_regmap()` iterates `desc->clks` and assigns each non-null common clock. `owl_clk_probe()` iterates `clk_hw_onecell_data`, skips null/error entries, calls `devm_clk_hw_register()`, and finally registers `devm_of_clk_add_hw_provider()`.

Control flow/state: regmap and registered clocks are device-managed. The persistent runtime state is hardware register content plus pointers stored in static descriptor structures. The provider exposes DT clock IDs through `of_clk_hw_onecell_get`.

Risks and tests: `owl_clk_regmap_init()` return value is ignored by the SoC probes, so a failed ioremap/regmap could lead to later invalid access. The fixed `max_register` must cover every SoC register used, including S900 offsets up to `0x00cc`; larger future SoCs would need adjustment. Test signals include probe success, `clk_summary`, OF clock lookup, and fault injection around regmap initialization.
