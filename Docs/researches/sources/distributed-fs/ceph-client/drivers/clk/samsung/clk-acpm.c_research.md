# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-acpm.c

Purpose: Samsung Exynos ACPM firmware-backed clock driver. It exposes clocks whose rates are controlled through the ACPM DVFS protocol rather than direct clock-controller registers.

Important APIs/types/functions: `struct acpm_clk`, `struct acpm_clk_variant`, `struct acpm_clk_driver_data`, `ACPM_CLK()`, `gs101_acpm_clks[]`, `acpm_clk_gs101`, `acpm_clk_recalc_rate()`, `acpm_clk_determine_rate()`, `acpm_clk_set_rate()`, `acpm_clk_ops`, `acpm_clk_register()`, and `acpm_clk_probe()`. Platform ID is `"gs101-acpm-clk"`.

Control flow: probe obtains an ACPM handle from the parent OF node with `devm_acpm_get_by_node()`, allocates onecell hardware-clock data and `struct acpm_clk` array, assigns sequential firmware IDs, registers each `clk_hw`, then publishes an OF hardware-clock provider. Rate reads call `dvfs_ops.get_rate()`. Rate writes call `dvfs_ops.set_rate()`. `determine_rate()` accepts the requested rate because firmware is authoritative.

State and persistence: devres-managed clock objects retain ACPM handle, mailbox channel ID, and sequential clock ID. Actual rates persist in firmware/hardware managed through ACPM.

Dependencies and integration: Linux CCF, platform bus, Samsung Exynos ACPM protocol, GS101 clock names (`mif`, `int`, CPU clusters, GPU, TPU, camera/media/display/bo), and OF onecell provider consumers.

Risks: code currently hard-codes `acpm_clk_gs101` rather than selecting driver data from the platform ID entry, limiting variant extensibility. It assumes clock IDs are zero-based, sequential, and gapless. ACPM operation failures propagate through CCF rate calls and may affect DVFS-sensitive domains.

Test signals: GS101 probe with ACPM firmware, `clk_summary` showing all ACPM clocks, successful get/set rate through CCF consumers, firmware error injection, and adding another variant to verify data selection is generalized before reuse.
