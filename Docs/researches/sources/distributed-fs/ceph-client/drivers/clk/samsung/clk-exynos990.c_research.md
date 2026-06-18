# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos990.c

## Purpose
`clk-exynos990.c` is the Samsung common clock framework provider for Exynos990 CMU blocks. It translates Exynos990 clock-controller register layout and clock IDs from `dt-bindings/clock/samsung,exynos990.h` into CCF-visible PLL, mux, divider, fixed-factor, and gate clocks. The implemented hardware islands are `CMU_TOP`, `CMU_HSI0`, `CMU_PERIC0`, `CMU_PERIC1`, and `CMU_PERIS`.

The file is declarative rather than algorithm-heavy. Most behavior is encoded in static `samsung_*_clock` tables and `samsung_cmu_info` descriptors consumed by `exynos_arm64_register_cmu()`. `CMU_TOP` supplies the root PLL-derived clock tree for display, audio, bus, CPU cluster, camera, HSI, MFC, NPU, PERIC, PERIS, and other top-level domains. `CMU_HSI0` covers USB/DisplayPort high-speed I/O. `CMU_PERIC0` and `CMU_PERIC1` cover UART, USI, I2C, I3C, GPIO, and peripheral bus gates. `CMU_PERIS` covers system/peripheral infrastructure such as GIC, MCT, WDT, TMU, OTP, sysreg, and TZPC clocks.

## Important APIs, Types, And Functions
The central descriptors are `struct samsung_pll_clock`, `struct samsung_mux_clock`, `struct samsung_div_clock`, `struct samsung_fixed_factor_clock`, `struct samsung_gate_clock`, and `struct samsung_cmu_info` from the Samsung clock framework. Clock descriptor macros include `PLL()`, `PNAME()`, `MUX()`, `DIV()`, `FFACTOR()`, and `GATE()`. The root registration API is `exynos_arm64_register_cmu()`.

`top_pll_clks[]` registers shared PLLs, the MMC PLL, and the G3D PLL using Samsung PLL variants `pll_0717x`, `pll_0718x`, and `pll_0732x`. `top_mux_clks[]` selects between oscillator, PLL, and divided PLL parents for top-level functional domains. `top_div_clks[]` creates shared PLL dividers and per-domain derived outputs. `cmu_top_ffactor[]` creates fixed 1:8 outputs for HSI PCIe/debug and OTP clocks. `top_gate_clks[]` gates top-level outputs.

`hsi0_cmu_info`, `peric0_cmu_info`, `peric1_cmu_info`, and `peris_cmu_info` package the non-top CMU tables. `exynos990_cmu_top_init()` and `exynos990_cmu_peris_init()` are early init callbacks registered through `CLK_OF_DECLARE()`. `exynos990_cmu_probe()` is the platform-driver probe for the remaining CMUs; it uses `of_device_get_match_data()` to select the matching `samsung_cmu_info` and registers that CMU against the platform device node.

## Control Flow
Boot-time control flow is split between early OF clock registration and platform-driver registration. `CMU_TOP` is registered early through compatible `samsung,exynos990-cmu-top` because other domains depend on top-level parent clocks. `CMU_PERIS` is also registered early through `samsung,exynos990-cmu-peris` because the MCT and interrupt/timer infrastructure need it before ordinary platform devices may probe.

The platform driver is registered from `core_initcall(exynos990_cmu_init)`. Device-tree nodes compatible with `samsung,exynos990-cmu-hsi0`, `samsung,exynos990-cmu-peric0`, or `samsung,exynos990-cmu-peric1` match entries in `exynos990_cmu_of_match[]`; probe extracts the descriptor and calls `exynos_arm64_register_cmu(dev, dev->of_node, info)`. After registration, runtime operations are handled by the generic CCF and Samsung clock ops: mux changes program selector fields, divider changes program divisor fields, gate enables set bit 21 in the relevant gate register, and PLL handling uses the Samsung PLL helper.

There is no custom rate-selection algorithm in this file. Parent topology, bit positions, widths, and flags are the control surface. Consumer drivers interact with these clocks by phandle ID and name through the Linux clock framework.

## State And Persistence
There is no filesystem persistence. State is the live hardware register state plus the CCF clock objects created during boot. The `*_clk_regs[]` arrays enumerate registers that the Samsung CMU framework should know about for save/restore and registration bookkeeping. Clock enable state, mux selections, divisors, and PLL state persist only for the current boot and may be changed by consumers through CCF.

Several gates intentionally carry state-protection flags. Top-level bus, CPU switch, DPU bus, and PERIS bus paths use `CLK_IGNORE_UNUSED` where disabling them during late unused-clock cleanup would be unsafe. HSI0 link/ACEL interconnect gates, PERIC CMU/bus interconnect gates, and the PERIS GIC gate use `CLK_IS_CRITICAL` where the system relies on the clock being continuously enabled. GPIO and sysmmu-related gates also use `CLK_IGNORE_UNUSED` in selected places to avoid losing access to pinctrl, memory translation, or bus fabric during bring-up.

## Dependencies And Integration Points
The file depends on Linux CCF and platform/OF infrastructure through `<linux/clk-provider.h>`, `<linux/of.h>`, `<linux/mod_devicetable.h>`, and `<linux/platform_device.h>`. It depends on Samsung clock helpers in `clk.h`, `clk-exynos-arm64.h`, and `clk-pll.h`, and on Exynos990 numeric IDs in `dt-bindings/clock/samsung,exynos990.h`.

Integration is primarily through device tree. Other drivers consume the exported clock IDs for USB31/USB-DP PHY and controller clocks, DisplayPort timing clocks, PERIC UART/USI/I2C/I3C serial clocks, GPIO and sysreg PCLKs, watchdog/timer/GIC/TMU/OTP clocks, camera/display/video/NPU/MFC/G2D/DSP top-level clocks, and bus or interconnect clocks. The binding names in `exynos990_cmu_of_match[]` must match SoC DTS nodes and their MMIO ranges, while clock IDs must remain synchronized with the binding header.

## Risks
Most risk is descriptor accuracy. Register offsets, selector widths, gate bits, and clock-parent names must match the Exynos990 CMU hardware manual and DTS topology exactly. A wrong parent name may create an orphan clock; a wrong gate offset can disable an unrelated IP block; a wrong mux width can select a reserved parent; and a wrong `CLKS_NR_*` value can truncate registration or leave IDs unreachable.

The file contains several areas that deserve focused validation. PERIC0 and PERIC1 have dense USI/IPCLK/PCLK mappings where off-by-one clock IDs or parent assignments can break serial buses subtly. PERIC1 includes several gates whose parent string is `dout_peric1_bus_user`, while the visible bus-user clock descriptor is named `mout_peric1_bus_user`; that relationship should be checked against the broader Samsung CCF behavior and clock summary for orphaned parents. PERIS mixes GIC, MCT, watchdog, TMU, OTP, TZPC, and sysreg gates; incorrect `CLK_IS_CRITICAL` or `CLK_IGNORE_UNUSED` policy can lead to boot hangs or late failures during unused-clock cleanup.

PLL definitions are another high-impact surface. The top CMU uses multiple PLL variants, including MMC and G3D PLLs, and the downstream parent trees depend on fixed names such as `fout_shared*_pll`, `fout_mmc_pll`, and `fout_g3d_pll`. A mismatch with bootloader-programmed PLL state or the binding header would affect many derived clocks.

## Test Signals
Basic validation is a boot with no CMU registration errors for `samsung,exynos990-cmu-top`, `samsung,exynos990-cmu-peris`, `samsung,exynos990-cmu-hsi0`, `samsung,exynos990-cmu-peric0`, and `samsung,exynos990-cmu-peric1`. `/sys/kernel/debug/clk/clk_summary` should show the registered PLLs, top mux/div/gate clocks, HSI0 USB/DP clocks, PERIC0/PERIC1 USI and bus clocks, and PERIS GIC/MCT/WDT/TMU/OTP clocks without unexpected orphan parents.

Hardware-level signals include working UART console and Bluetooth/debug UART where present, I2C/SPI/I3C transactions through all populated USI instances, GPIO access in both PERIC domains, USB31/USB-DP initialization for HSI0, watchdog and timer operation through PERIS, thermal sensor access through TMU clocks, and stable suspend/resume or unused-clock cleanup with no loss of critical interconnect, GIC, MCT, sysmmu, or CMU PCLK paths. Rate checks should confirm expected parent/divider choices for PERIC serial clocks and top-level HSI/MFC/NPU/display/camera clocks.
