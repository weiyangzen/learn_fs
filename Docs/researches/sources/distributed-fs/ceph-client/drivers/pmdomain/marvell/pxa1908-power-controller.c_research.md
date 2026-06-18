# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/pxa1908-power-controller.c

Purpose: auxiliary-bus generic PM domain provider for Marvell PXA1908 APMU power islands. It exposes six onecell domains: `vpu`, `gpu`, `gpu2d`, `isp`, `dsi`, and `audio`.

Important APIs, types, and functions: `struct pxa1908_pd_ctrl` stores the shared syscon regmap, onecell provider data, and domain pointers. `struct pxa1908_pd_data` describes APMU control offsets, status bits, hardware-mode bits, and keep-on policy. `struct pxa1908_pd` embeds `struct generic_pm_domain`. `pxa1908_pd_is_on()` reads either normal APMU power status or special DSI/audio bits. `pxa1908_pd_power_on()`/`pxa1908_pd_power_off()` sequence normal domains through `APMU_PWR_CTRL_REG`, block timer, status polling, and clock/reset mode bits. DSI and audio have minimal bit-set/clear callbacks. `pxa1908_pd_init()`, `pxa1908_pd_probe()`, and `pxa1908_pd_remove()` handle registration and cleanup.

Control flow: probe allocates controller state, gets the parent syscon regmap, initializes all static domain descriptors, and publishes `of_genpd_add_provider_onecell()` on the parent node. Initialization syncs hardware to software: keep-on domains are powered on, while unexpectedly-on default-off domains are warned about and powered down before `pm_genpd_init()`. Remove walks domains in reverse, powers off any initialized non-keep-on domain still on, and removes genpd objects.

State and persistence behavior: no persistent storage is used. Runtime state is hardware register state plus `initialized` and onecell pointers. DSI is `GENPD_FLAG_ALWAYS_ON` and `keep_on` because no DSI driver exists yet, so remove also preserves it.

Dependencies and integration points: depends on auxiliary bus binding name `clk_pxa1908_apmu.power`, parent OF syscon, Linux genpd, regmap, and `dt-bindings/power/marvell,pxa1908-power.h` IDs. It integrates as a provider for device-tree `power-domains` consumers under the APMU parent.

Risks: the static global `domains[]` means this driver assumes one controller instance. Power sequencing is register-literal and SoC-specific; wrong mode/status bit mapping can hang consumers. Normal domains poll only the common power status register; DSI/audio state is special-cased. Failed `of_genpd_add_provider_onecell()` after successful domain init does not automatically call cleanup on that return path.

Test signals: boot probe should publish six domains, show no timeout errors, and leave only DSI always-on by policy. Runtime PM tests should attach consumers to each domain and verify status bit transitions, remove cleanup, and timeout handling by fault injection or register tracing.
