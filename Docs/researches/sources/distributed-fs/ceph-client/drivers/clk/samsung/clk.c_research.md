# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk.c

Purpose: common Samsung clock-provider infrastructure for registering fixed, factor, mux, divider, gate, PLL, CPU, alias, CMU, auto-gate, and sleep-save clocks.

Important APIs/types/functions: `samsung_clk_init()`, `samsung_clk_of_add_provider()`, `samsung_clk_add_lookup()`, registration helpers, sleep helpers `samsung_clk_save()/restore()/alloc_reg_dump()/extended_sleep_init()`, auto-gate helpers `samsung_is_auto_capable()` and `samsung_register_auto_gate()`, `samsung_cmu_register_clocks()`, `samsung_en_dyn_root_clk_gating()`, and `samsung_cmu_register_one()`.

Control flow: SoC code allocates a provider, registers descriptor arrays, and publishes a onecell provider. CMU one-shot registration maps registers, registers clock classes in PLL/mux/div/gate/fixed/CPU order, registers sleep caches, enables dynamic root clock gating through sysreg when available, and exposes the provider.

State and persistence behavior: provider stores MMIO base, device, optional sysreg, spinlock, auto-gate flags/offsets, and flexible onecell clock data. A global register-cache list drives syscore suspend/resume save/restore.

Dependencies/integration points: Linux CCF, clkdev, OF providers, syscon/regmap, syscore PM, Samsung descriptor types, and SoC CMU info structures.

Risks: most per-clock registration failures log and continue, leaving sparse providers; ID zero is intentionally not added to lookup; auto-gate requires exact resource sizing and sysreg phandles. The local source has a duplicated `for` line in `samsung_clk_register_div()`, which should be compile-checked.

Test signals: build Samsung CMUs, boot DT providers, verify missing IDs are `ERR_PTR(-ENOENT)`, test PM restore, and validate auto-gate fallback paths.
