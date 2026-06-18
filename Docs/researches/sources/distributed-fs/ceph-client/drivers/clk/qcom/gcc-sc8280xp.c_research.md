# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc8280xp.c

## Purpose

This file is the Qualcomm Global Clock Controller driver for the SC8280XP SoC. It binds to `qcom,gcc-sc8280xp`, maps the GCC MMIO register block through regmap, and exposes the SoC's GCC-managed clocks, resets, and GDSC power domains to the Linux common clock framework, reset controller framework, and generic power-domain users.

The implementation is mostly declarative hardware description: PLLs, RCGs, muxes, dividers, branch gates, reset offsets, and GDSCs are encoded as static tables and registered through `qcom_cc_really_probe()`. The active procedural path is limited to platform-driver registration and probe-time setup.

## Important APIs, Types, And Data

- External kernel APIs: `platform_driver_register()`, `platform_driver_unregister()`, `devm_pm_runtime_enable()`, `pm_runtime_resume_and_get()`, `pm_runtime_put()`, `pm_runtime_put_sync()`, `MODULE_DEVICE_TABLE()`, `subsys_initcall()`, and `module_exit()`.
- Qualcomm CC helpers: `qcom_cc_map()`, `qcom_cc_really_probe()`, `qcom_cc_register_rcg_dfs()`, and `qcom_branch_set_clk_en()`.
- Clock data types: `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `clk_rcg2`, `clk_regmap_mux`, `clk_regmap_phy_mux`, `clk_regmap_div`, `clk_branch`, `clk_parent_data`, `parent_map`, and `freq_tbl`.
- Power/reset data types: `gdsc`, `qcom_reset_map`, `qcom_cc_desc`, and `regmap_config`.
- Binding integration comes from `dt-bindings/clock/qcom,gcc-sc8280xp.h`; the large `gcc_sc8280xp_clocks[]`, `gcc_sc8280xp_resets[]`, and `gcc_sc8280xp_gdscs[]` arrays are indexed by IDs from that binding.

The file defines 6 Lucid alpha PLLs (`gcc_gpll0`, `gcc_gpll2`, `gcc_gpll4`, `gcc_gpll7`, `gcc_gpll8`, `gcc_gpll9`), one post-divider (`gcc_gpll0_out_even`), 78 `clk_rcg2` roots, 26 regmap muxes, 5 PHY muxes, 11 read-only dividers, 255 branch clocks, 79 reset entries, and 25 GDSC definitions. Parent enumerations distinguish external DT-supplied parents such as TCXO, sleep clock, USB/PCIe PHY pipe clocks, UFS symbol clocks, and RX reference clocks from in-driver PLL-derived parents.

## Clock Model

The parent maps near the top of the file translate common clock parent IDs into hardware source-selector values. Internal parents are connected through `.hw` pointers to PLLs or intermediate muxes; external parents use `.index` values that match the driver-local DT parent order. This makes the DT clock-names order a correctness requirement for TCXO, sleep, UFS symbol, USB4/USB3 PHY, PCIe pipe, and RXC reference inputs.

Rate-programmable RCGs cover EMAC, general-purpose clocks, PCIe aux and PHY rate-change clocks, PDM, three QUPv3 wrappers, SDCC, UFS, USB3, and USB4. The `freq_tbl` entries select parent PLLs plus divider or M/N values; examples include QUP serial rates, SD card rates up to 202 MHz, UFS AXI/ICE/UniPro rates up to 300 MHz, USB3 master rates up to 240 MHz, and USB4 master rates at 175/350 MHz.

Muxes and PHY muxes bridge hardware-provided pipe/symbol clocks into GCC-visible clock trees. USB4 has paired sets for the two controllers, with DP, RX, SYS, p2rr2p, PCIe pipe, and pipe-gmux selections. PCIe 2a/2b/3a/3b/4 use `clk_regmap_phy_mux_ops` and read-only pipe dividers before branch clocks expose pipe and pipediv2 outputs.

Branch clocks are the final gates exposed to consumers. They cover NoC aggregates, camera/display/video throttle and AXI clocks, EMAC0/1, GPU-related votes, PCIe instances and tunnels, PDM, QUPv3 wrapper serial/QSPI/AHB clocks, SDCC2/4, UFS card and UFS PHY, USB2/USB3/USB4 clock references and PHY clocks. Branch definitions encode halt behavior (`BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, `BRANCH_HALT_DELAY`), optional hardware clock gating registers, parent pointers, and `CLK_SET_RATE_PARENT` where consumer rate changes should propagate upstream.

## Control Flow

Driver load calls `gcc_sc8280xp_init()` at `subsys_initcall` time, registering `gcc_sc8280xp_driver`. Device-tree matching on `qcom,gcc-sc8280xp` invokes `gcc_sc8280xp_probe()`.

Probe enables runtime PM for the device, resumes the GCC register block, maps it with `qcom_cc_map()`, and then force-enables a small set of always-on camera, display, GPU, video, and secondary-display AHB/XO branches by raw register address. It registers DFS metadata for all QUPv3 serial RCGs through `qcom_cc_register_rcg_dfs()`, then calls `qcom_cc_really_probe()` with `gcc_sc8280xp_desc`. On success it drops the runtime PM reference with `pm_runtime_put()`; on any failure after resume it uses `pm_runtime_put_sync()` and returns the error.

The clock, reset, and GDSC operations after probe are handled by shared Qualcomm clock-controller code via the registered descriptors. This file does not implement custom set-rate, enable, disable, reset, or power-domain callbacks.

## State And Persistence Behavior

Persistent state is hardware state in the GCC register block. The driver's static C objects describe offsets, bit masks, parent maps, and operation callbacks, while runtime state is held by the common clock framework, regmap, runtime PM, reset controller, and genpd/GDSC frameworks.

Probe mutates hardware by enabling always-on branches and registering DFS-capable QUP clocks. Clock consumers later mutate registers through the shared ops: RCG rate programming writes RCGR/MND fields, muxes select parent values, branch ops set enable bits and poll halt status, resets assert or deassert BCR/ARES bits, and GDSC ops vote or collapse domains. There is no file-backed persistence and no driver-private dynamic allocation beyond devm-managed resources in the shared mapping path.

## Dependencies And Integration Points

The driver depends on the Qualcomm clock framework helpers in the same directory (`clk-alpha-pll`, `clk-branch`, `clk-rcg`, `clk-regmap*`, `common`, `gdsc`, and `reset`). It also depends on the SC8280XP DT binding header for stable clock/reset/GDSC indices and on device tree to supply the external parent clocks in the exact order documented by the local enum.

Consumers include device-tree nodes for PCIe, UFS, USB, SDHCI, QUP serial engines, Ethernet MACs, GPU/display/camera/video interconnect-related blocks, and power-domain users. The descriptor's regmap has 32-bit registers, 4-byte stride, `max_register = 0xc3014`, and `fast_io = true`, so all table offsets must remain inside that register range.

## Risks And Maintenance Notes

- Binding index drift is high impact. The local DT parent enum must match DT binding order, and the exported arrays must stay aligned with `qcom,gcc-sc8280xp.h` IDs.
- Register offsets and enable masks are hardware-specific. A bad offset can silently control the wrong clock, reset, or GDSC; many entries share vote registers such as `0x52000`/`0x52008`/`0x52010`/`0x52018`/`0x52020`.
- Halt-check mode choice is behavioral. Using `BRANCH_HALT` where hardware does not report halt reliably can create timeouts, while `BRANCH_HALT_SKIP` can hide stuck gates.
- External PHY/symbol parents are fragile integration points for USB4, USB3, PCIe, UFS, and EMAC RX reference clocks. Missing or misordered DT parent clocks can make mux selection or rate rounding choose fallback TCXO paths.
- Runtime PM error unwinding is simple but important: failures after `pm_runtime_resume_and_get()` must keep the put path intact.
- Always-on branch writes in probe are raw address operations; changing them can affect camera/display/GPU/video boot stability and should be validated on hardware.

## Test Signals

Useful build-time signals are `make drivers/clk/qcom/gcc-sc8280xp.o`, `dtbs_check` for `qcom,gcc-sc8280xp` nodes and parent clock ordering, and compiler coverage for all binding IDs referenced by designated initializers. Runtime signals include successful probe without regmap or runtime PM errors, expected clocks under `/sys/kernel/debug/clk/clk_summary`, consumer drivers acquiring SC8280XP GCC clocks by ID, reset lines toggling through the reset framework, and GDSC domains appearing and transitioning through genpd debugfs.

Hardware-focused validation should exercise QUP serial rates and DFS, SDCC card rates, UFS card/PHY link bring-up, USB3 and USB4 PHY pipe clocks, PCIe link training on all instances, EMAC PTP/RGMII rates with RXC reference parents, and suspend/resume paths that collapse and restore GDSCs. Regression symptoms to watch for are probe deferral from missing parent clocks, branch enable timeouts, incorrect rounded rates, PCIe/USB/UFS link failures, and display/camera/video instability if always-on support clocks are changed.
