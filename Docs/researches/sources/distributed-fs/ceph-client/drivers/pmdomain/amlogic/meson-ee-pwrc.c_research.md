# sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/meson-ee-pwrc.c

Purpose: generic PM-domain provider for Amlogic Meson “Everything-Else” domains controlled by AO sleep/isolation registers, HHI memory power registers, resets, and clocks. It supports Meson8/8b/8m2, GXBB, AXG, G12A, and SM1 domain layouts.

Important APIs/types/functions: descriptor types include `meson_ee_pwrc_mem_domain`, `meson_ee_pwrc_top_domain`, `meson_ee_pwrc_domain_desc`, and `meson_ee_pwrc_domain_data`. Runtime state is `meson_ee_pwrc_domain` and `meson_ee_pwrc`. Important callbacks are `meson_ee_pwrc_on()`, `meson_ee_pwrc_off()`, `meson_ee_pwrc_init_domain()`, `meson_ee_pwrc_probe()`, and `meson_ee_pwrc_shutdown()`. Domain tables define VPU, ETH, AUDIO, NNA, ISP, USB, PCIE, and GE2D memory/top domains per SoC.

Control flow: probe gets SoC match data, allocates onecell provider arrays, obtains HHI regmap from the parent syscon and AO regmap from `amlogic,ao-sysctrl`, copies each descriptor, initializes resets/clocks, sets genpd callbacks, detects bootloader-enabled clocked domains, and registers the provider. Power-on clears top sleep bits, clears memory power-down bits, asserts resets, clears isolation, deasserts resets, and enables clocks. Power-off sets top sleep, powers down memory slices, sets isolation, waits if needed, and disables clocks. Shutdown powers off any domain with status callback reporting still on.

State and persistence: software tracks per-domain descriptors, reset arrays, clocks, genpd status, and regmap handles. Hardware state persists in AO and HHI registers and in reset/clock controllers. Bootloader-enabled VPU-style domains can be marked always-on with clocks enabled to keep reference counts coherent.

Dependencies/integration: uses generic PM domains, OF onecell providers, syscon/regmap, reset controller consumers, bulk clock APIs, delay helpers, DT binding indices, and platform driver matching. Consumers reference the provider via power-domain cells in DT.

Risks: power sequencing is hardware-sensitive; wrong ordering of sleep, memory PD, isolation, reset, and clocks can hang display, USB, PCIe, or NNA blocks. Reset and clock counts are warned but tolerated, so bad DT can limp into runtime failures. Bootloader-enabled domains are protected by `GENPD_FLAG_ALWAYS_ON`; changing that risks disabling active display pipelines. Shutdown forcibly powers domains off if status says on, which can affect firmware handoff expectations.

Test signals: probe must find both AO and HHI regmaps; each compatible should expose the expected onecell domain count; VPU on/off should preserve display behavior; clocks and resets should pair cleanly; bootloader-on domains should become always-on; shutdown should not hang; and DT reset/clock count warnings should be treated as board-description test failures.
