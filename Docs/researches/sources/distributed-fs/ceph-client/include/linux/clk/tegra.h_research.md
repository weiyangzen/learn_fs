# sources/distributed-fs/ceph-client/include/linux/clk/tegra.h

Purpose: This header exposes NVIDIA Tegra CPU clock/reset control wrappers, EMC clock callbacks and providers, and Tegra210 PLL/USB/SATA/EMC control hooks.

Important APIs/types/functions: Core type `struct tegra_cpu_car_ops` contains CPU reset, clock, and PM callbacks. Wrappers include `tegra_wait_cpu_in_reset`, `tegra_put_cpu_in_reset`, `tegra_cpu_out_of_reset`, `tegra_enable_cpu_clock`, `tegra_disable_cpu_clock`, `tegra_cpu_rail_off_ready`, `tegra_cpu_clock_suspend`, and `tegra_cpu_clock_resume`. EMC types include callback typedefs for Tegra20 and Tegra124, `struct tegra210_clk_emc_config`, and `struct tegra210_clk_emc_provider`. Tegra210 APIs cover PLLE hardware sequencing, XUSB/SATA PLL hardware control, UTMIPLL IDDQ, MBIST workaround handling, EMC DLL/source updates, and `tegra210_clk_emc_attach`/`detach`.

Control flow: On Tegra builds, inline CPU wrappers validate callback pointers with `WARN_ON` and dispatch through global `tegra_cpu_car_ops`; otherwise they become no-ops. PM wrappers exist only when sleep support is enabled. EMC callback registration lets memory-controller code coordinate timing changes with clock rate changes. Tegra210-specific helpers are compiled in only for Tegra210; other builds use stubs.

State and persistence behavior: State lives in the global ops pointer, clock/reset hardware registers, EMC provider config arrays, and PLL/IDDQ hardware state. The header stores no persistent data but exposes paths that alter CPU reset, CPU clock, memory clock, and PLL state.

Dependencies and integration points: It includes `<linux/types.h>` and `<linux/bug.h>`, and integrates with Tegra architecture CPU hotplug/reset code, PM sleep, memory controller timing, XUSB/SATA PHY clocking, and CCF providers.

Risks: Missing `tegra_cpu_car_ops` callbacks trigger warnings and skipped operations, which can break CPU bring-up or hotplug. EMC timing callbacks must be ordered around rate changes or memory instability can result. Tegra210 stubs returning success can hide missing platform support in generic builds.

Test signals: Tegra CPU hotplug, suspend/resume, rail-off readiness, EMC frequency switching, XUSB/SATA link bring-up, PLL sequence status, MBIST workaround paths, and compile coverage across Tegra generations are key signals.
