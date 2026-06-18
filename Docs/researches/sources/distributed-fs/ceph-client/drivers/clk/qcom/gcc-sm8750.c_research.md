# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8750.c

## Purpose

`gcc-sm8750.c` is the Qualcomm Global Clock Controller driver for the SM8750 SoC. It publishes the SoC-wide GCC clock tree, reset controls, and GDSC power domains to the Linux common clock framework, reset framework, and generic power domain users. The driver is almost entirely declarative: static tables describe PLLs, root clock generators, muxes, dividers, branch gates, reset register offsets, GDSC descriptors, and the final binding between devicetree clock IDs and `struct clk_regmap` instances.

The controller covers system and peripheral infrastructure clocks for PCIe, UFS, USB3, SDCC, PDM, GPU/DDR/NOC, camera/display/video/EVA AHB or AXI voting clocks, general-purpose clocks, and QUPv3 I2C/QSPI serial engines. It binds to `qcom,sm8750-gcc` and is selected by `CONFIG_SM_GCC_8750`.

## Important APIs, Types, and Data

The exported ABI is the numeric ID space from `<dt-bindings/clock/qcom,sm8750-gcc.h>`. `gcc_sm8750_clocks[]`, `gcc_sm8750_resets[]`, and `gcc_sm8750_gdscs[]` map those binding IDs to clock, reset, and power-domain implementations. Consumers never call symbols in this file directly; they reference GCC IDs through devicetree phandles.

Core Qualcomm clock types used here:

- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` define fixed Taycan ELU GPLLs: `gcc_gpll0`, `gcc_gpll1`, `gcc_gpll4`, `gcc_gpll7`, `gcc_gpll9`, plus `gcc_gpll0_out_even`.
- `struct clk_rcg2` defines programmable root clock generators with `cmd_rcgr`, parent maps, M/N/D widths, HID widths, frequency tables, and shared RCG ops.
- `struct clk_regmap_mux`, `struct clk_regmap_phy_mux`, and `struct clk_regmap_div` model external PHY pipe/symbol selections and read-only post-dividers.
- `struct clk_branch` models branch gates and halt polling behavior with `enable_reg`, `enable_mask`, `halt_reg`, `halt_check`, and optional hardware clock gating fields.
- `struct gdsc` models GCC-controlled power domains for PCIe, PCIe PHY, UFS, UFS memory PHY, USB30 primary, and USB3 PHY.
- `struct qcom_reset_map` maps reset IDs to block-control registers and optional bit positions.
- `struct qcom_cc_desc` packages regmap config, clocks, resets, and GDSCs for the shared Qualcomm CC registration path.

Parent inputs are split between DT-provided clocks and local PLLs. DT parent indexes include TCXO, always-on TCXO, sleep clock, PCIe pipe clock, UFS RX/TX symbol clocks, and USB3 pipe clock. Local parent maps translate logical parent constants such as `P_GCC_GPLL0_OUT_MAIN` or `P_GCC_GPLL9_OUT_MAIN` to hardware mux values.

## Clock Coverage

The PLL layer provides the main high-frequency sources. GPLL0 is used broadly and exposes a divided `out_even` path; GPLL1, GPLL4, GPLL7, and GPLL9 feed higher-rate or peripheral-specific roots such as QUP, UFS, SDCC, and USB.

RCG frequency tables define:

- GP1/GP2/GP3 rates at 50, 100, and 200 MHz.
- PCIe auxiliary and PHY ref-change roots at 19.2 MHz and 100 MHz.
- PDM2 at 60 MHz.
- Ten QUPv3 I2C root sources fixed to the 19.2 MHz auxiliary table.
- QUPv3 wrap1/wrap2 serial roots with broad UART/SPI-style rates from 7.3728 MHz through 120 MHz, plus QSPI up to 250 MHz and wrap2 S6 to 128 MHz.
- SDCC2 and SDCC4 application roots, including low-speed 400 kHz initialization rates and higher data-path rates.
- UFS AXI, ICE, UniPro, and PHY auxiliary roots.
- USB30 primary master rates from about 66.7 MHz through 240 MHz, plus mock UTMI and PHY aux roots.

Branch gates expose the usable clocks behind those roots and also cover always-on or voted interconnect paths. Halt checks are significant: some clocks use strict `BRANCH_HALT`, some are `BRANCH_HALT_VOTED`, some use `BRANCH_HALT_DELAY` for PHY symbol/pipe paths, and several NOC/AXI-facing clocks intentionally use `BRANCH_HALT_SKIP` where status polling is not reliable or not meaningful.

## Control Flow

Driver initialization is via `subsys_initcall(gcc_sm8750_init)`, which registers a platform driver named `gcc-sm8750`. Matching is by `of_device_id` compatible `qcom,sm8750-gcc`.

`gcc_sm8750_probe()` performs the runtime sequence:

1. Calls `qcom_cc_map(pdev, &gcc_sm8750_desc)` to map the MMIO resource into a regmap using 32-bit registers, 4-byte stride, `max_register = 0x1f41f0`, and fast I/O.
2. Registers dynamic frequency scaling metadata for QUPv3 RCGs with `qcom_cc_register_rcg_dfs()`. The DFS table covers QUP wrap1 QSPI/S0/S1/S3-S7 and wrap2 S0-S7 roots.
3. Sets a small group of infrastructure clocks always enabled through `qcom_branch_set_clk_en()` or `regmap_update_bits()`. These include camera, display, EVA, GPU config, video, and PCIe RSCC AHB/XO clocks that are not represented as normal consumer-managed branches in the public table.
4. Forces memory-core retention behavior for `gcc_ufs_phy_ice_core_clk` and `gcc_ufs_phy_axi_clk` through `qcom_branch_set_force_mem_core(..., true)`.
5. Calls `qcom_cc_really_probe()` to register clocks, resets, and GDSCs with kernel frameworks.

Module exit unregisters the platform driver when built as a module.

## State and Persistence Behavior

The driver has no heap-owned persistent state beyond the shared framework registrations and the regmap mapping. Most state lives in hardware registers: PLL enable votes, RCG parent/rate programming, branch gate bits, halt status bits, reset bits, hardware clock-gating bits, and GDSC power-state registers.

The statically allocated clock descriptors are process-lifetime objects used by the common clock framework. Runtime rate, prepare, enable, and parent changes are mediated by CCF and Qualcomm `clk_regmap` operations, which read and write controller registers through regmap.

Persistent hardware policy is established in probe by forcing selected infrastructure branches on and by enabling force-mem-core for UFS clocks. These writes survive as long as the controller remains powered and are not represented as ordinary consumer reference counts. GDSCs persist their on/off state in controller power registers and can be toggled by genpd consumers.

## Dependencies and Integration Points

This file depends on Linux platform-device probing, module/of match tables, regmap, CCF provider types, Qualcomm alpha PLL, branch, RCG, regmap mux/divider, PHY mux, reset, GDSC, and common CC helpers. It also depends on the SM8750 GCC DT binding header for all exported IDs and on the devicetree binding `qcom,sm8750-gcc` for parent clock ordering.

Integration points include:

- Devicetree nodes with compatible `qcom,sm8750-gcc`, MMIO resources, and parent clocks matching the binding schema.
- Peripheral consumers using GCC clock IDs for PCIe, UFS, USB, SDCC, QUPv3, PDM, GPU, display, camera, video, and NOC paths.
- Reset consumers using BCR and ARES IDs for camera, display, EVA, GPU, PCIe, PDM, QUPv3, QUSB2PHY, SDCC, UFS, USB3, and video blocks.
- Genpd consumers for PCIe, PCIe PHY, UFS, UFS memory PHY, USB30 primary, and USB3 PHY GDSCs.
- Shared Qualcomm clock code that implements the register programming semantics; this driver supplies offsets, bit masks, parent maps, and frequency tables.

## Risks and Review Notes

The largest risk is table accuracy. Incorrect register offsets, enable bits, halt types, parent-map hardware values, or binding-array indexes can silently break a peripheral or expose the wrong clock to consumers. The `gcc_sm8750_clocks[]` indexes must remain synchronized with `qcom,sm8750-gcc.h`.

Parent ordering is fragile because DT parent indexes and local parent maps are mixed. External PHY symbol and pipe clock parents must match board DTS wiring, while local PLL parent references must remain valid for CCF registration.

Frequency tables include fractional values and unusual divisors, including USB rates using half divisors and QUP serial rates with M/N fractions. The in-file comment `/* Check this frequency table.*/` above the QSPI reference table is an explicit review signal that those rates deserve hardware validation.

Always-on probe writes are outside normal CCF ownership. Removing or converting them without a full audit can cause late boot, suspend/resume, or unused-clock cleanup regressions in camera, display, EVA, GPU, video, or PCIe RSCC support.

Several branches use `BRANCH_HALT_SKIP` or `BRANCH_HALT_DELAY`; changing those to stricter polling can introduce false timeout failures on clocks whose status bits are voted, delayed, or not trustworthy.

GDSC flags such as `VOTABLE`, `POLL_CFG_GDSCR`, and `RETAIN_FF_ENABLE` encode power sequencing requirements. Incorrect flags or wait values can cause PCIe/UFS/USB domains to fail power-up, lose retention state, or hang during collapse.

## Test Signals

Build coverage should include `CONFIG_SM_GCC_8750=y` and `=m` with `W=1` to catch missing IDs, type mismatches, and unused descriptor mistakes. DTS validation should run the SM8750 GCC schema and board DTs to verify compatible string, parent clock ordering, and reset/power-domain cell use.

Runtime validation on SM8750 hardware should confirm:

- Probe succeeds for `qcom,sm8750-gcc` before dependent PCIe, UFS, USB, SDCC, QUPv3, display, camera, video, and GPU drivers bind.
- `/sys/kernel/debug/clk/clk_summary` shows all exported GCC clocks with expected parents, rates, and enable counts.
- GP clocks can switch among 50/100/200 MHz.
- QUPv3 I2C/QSPI/serial consumers can request representative low, fractional, and high rates from the RCG tables.
- SDCC2/SDCC4 enter initialization and high-speed rates correctly.
- UFS uses AXI, ICE, UniPro, PHY auxiliary, and RX/TX symbol clocks without force-mem-core or PHY symbol-parent regressions.
- USB3 and PCIe pipe/PHY clocks tolerate link bring-up, link down, suspend, and resume.
- Reset IDs assert/deassert the intended blocks only.
- GDSC power domains transition cleanly under genpd for PCIe, UFS, and USB, including suspend/resume.
- Late unused-clock cleanup does not disable the probe-forced infrastructure clocks.
