# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8550.c

## Purpose

`gcc-sm8550.c` is the Qualcomm Global Clock Controller driver for the SM8550 SoC. It describes the GCC MMIO register block to the common Qualcomm clock-controller framework, exporting clock, reset, and power-domain handles through the IDs in `dt-bindings/clock/qcom,sm8550-gcc.h`.

The file is mostly declarative clock data. It builds the platform clock tree from external device-tree parents (`bi_tcxo`, sleep, PCIe pipe, PCIe PHY aux, UFS symbol, and USB3 pipe clocks), internal Lucid OLE GPLLs, parent selector tables, RCGs, read-only dividers, PHY muxes, branch gates, GDSCs, and reset maps. Runtime register access and common-clock behavior are delegated to shared qcom helpers.

## Important APIs, Types, And Functions

- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` model `gcc_gpll0`, `gcc_gpll4`, `gcc_gpll7`, `gcc_gpll9`, and `gcc_gpll0_out_even`. All use Lucid OLE register layouts and fixed PLL/post-divider operations.
- Local `DT_*` and `P_*` enums define, respectively, external DT parent indices and internal parent identifiers used by the RCG `parent_map` arrays.
- `struct parent_map` plus `struct clk_parent_data` arrays translate hardware selector values to CCF parents. These cover XO/sleep/GPLL selections, PCIe PHY aux, UFS symbol parents, and the USB3 pipe parent.
- `struct clk_regmap_phy_mux` is used for PCIe pipe parents. `struct clk_regmap_mux` is used for PCIe1 PHY aux, UFS RX/TX symbol, and USB3 pipe muxes with `clk_regmap_mux_closest_ops`.
- `struct freq_tbl` arrays encode allowed rates for GP clocks, PCIe aux/rchng clocks, PDM, QUPv3 serial engines, SDCC2/SDCC4, UFS PHY AXI/ICE/AUX/UNIPRO, and USB30 master/mock UTMI paths.
- `struct clk_rcg2` instances implement root clock generators. QUP serial engines use `clk_rcg2_ops`, GP/PCIe/PDM/UFS use shared RCG ops, SDCC apps clocks use `clk_rcg2_shared_floor_ops`, and USB30 master uses `clk_rcg2_shared_no_init_park_ops`.
- `struct clk_regmap_div` exposes `gcc_usb30_prim_mock_utmi_postdiv_clk_src` as a read-only divider.
- `struct clk_branch` entries provide the leaf gates exported to consumers. Branches use `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, or `BRANCH_HALT_DELAY` depending on hardware ownership and halt semantics; many include hardware clock gating (`hwcg_reg`/`hwcg_bit`).
- `struct gdsc` entries define PCIe0/1 controller and PHY domains, UFS PHY and memory PHY domains, and USB30/USB3 PHY domains.
- `struct qcom_reset_map gcc_sm8550_resets[]` maps binding reset IDs to block reset registers and two video AXI ARES bits with a 1000 us delay.
- `gcc_sm8550_probe()` maps the controller, registers DFS metadata, performs UFS ICE memory-core retention setup, marks a set of infrastructure clocks always-on, clears the GDSC sleep vote register, and then calls `qcom_cc_really_probe()`.

## Control Flow

Driver registration happens from `subsys_initcall(gcc_sm8550_init)`, which registers a platform driver matching `compatible = "qcom,sm8550-gcc"`. Probe performs a two-stage qcom CC setup rather than using `qcom_cc_probe()` directly:

1. `qcom_cc_map(pdev, &gcc_sm8550_desc)` maps the GCC register range using `gcc_sm8550_regmap_config`.
2. `qcom_cc_register_rcg_dfs()` registers dynamic frequency scaling metadata for the sixteen QUPv3 wrapper RCGs.
3. `regmap_update_bits()` sets bit 14 in the UFS PHY ICE core clock halt register to force memory core retention for that clock path.
4. `qcom_branch_set_clk_en()` enables always-on camera, display, GPU, and video AHB/XO/config clocks that are not otherwise exported as normal branch entries in this file.
5. `regmap_write(regmap, 0x52024, 0x0)` clears `GDSC_SLEEP_ENA_VOTE`, preventing sleep from automatically removing GDSC votes.
6. `qcom_cc_really_probe()` registers clocks, resets, and GDSCs with CCF, reset, and genpd.

After probe, consumers use normal CCF/reset/genpd APIs. Rate requests select rows from each `freq_tbl`, RCG ops program parent selectors and dividers, branch ops toggle enable bits, reset ops manipulate reset registers, and GDSC ops manage power-domain state.

## Clock And Subsystem Coverage

- Root sources: external XO/sleep/pipe/symbol clocks plus GPLL0, GPLL4, GPLL7, GPLL9, and GPLL0 even divider.
- General-purpose clocks: `gcc_gp1_clk`, `gcc_gp2_clk`, and `gcc_gp3_clk` with 50/100/200 MHz source choices.
- PCIe: two controllers with aux, cfg AHB, master/slave AXI, slave Q2A AXI, pipe, PHY rchng, and PCIe1 PHY aux paths, plus PCIe controller and PHY GDSCs/resets.
- QUPv3: ten I2C serial clocks and two QUP wrapper blocks with eight serial engines each. DFS metadata covers the wrapper serial RCGs.
- Storage: SDCC2 and SDCC4 apps/AHB clocks with floor rate selection; UFS PHY AXI, ICE core, PHY aux, UNIPRO core, RX/TX symbol clocks, hardware-control variants, UFS GDSCs, and UFS reset.
- USB: USB30 primary master/mock UTMI/sleep, USB3 PHY aux/com aux/pipe, USB30 and USB3 PHY GDSCs, and USB/QUSB/DP PHY resets.
- Multimedia and GPU infrastructure: camera/display/video AXI and QMIP AHB clocks, GPU GPLL0 branch exports, GPU memnoc/SNOC/DVM clocks, and always-on probe enables for some AHB/XO paths.
- PDM and boot ROM: PDM2 source/branch, PDM AHB/XO4, and boot ROM AHB.

## State And Persistence Behavior

The persistent state is hardware register state in the GCC block. The driver does not allocate private runtime state, does not start workqueues or timers, and has no suspend/resume callbacks. Framework state is owned by CCF, reset-controller, and genpd registration.

Clock rates, gate enables, reset assertions, DFS programming, and GDSC votes persist in MMIO registers until another agent changes them or the SoC resets. Probe intentionally mutates a few persistent bits: it forces UFS ICE memory core retention, enables selected infrastructure clocks, and clears the GDSC sleep-vote auto-removal register. Boot firmware may have left some clocks and PLLs enabled before Linux probes; this driver describes legal control paths rather than reinitializing every clock.

## Dependencies And Integration Points

- Linux platform driver and OF matching: `<linux/platform_device.h>`, `<linux/of.h>`, `MODULE_DEVICE_TABLE()`, `subsys_initcall()`, and `module_exit()`.
- Linux CCF: `<linux/clk-provider.h>`, qcom alpha PLL, RCG, branch, regmap mux/divider, and PHY mux helpers.
- Regmap: `gcc_sm8550_regmap_config` uses 32-bit registers, 4-byte stride, 32-bit values, `max_register = 0x1f41f0`, and `fast_io = true`.
- Reset framework: `gcc_sm8550_resets[]` is bound into `gcc_sm8550_desc`.
- Generic power domains/GDSC: `gdsc.h` and `gcc_sm8550_gdscs[]` expose PCIe, UFS, and USB domains.
- Device-tree ABI: external parent order must match the local `DT_*` enum, and consumers use the IDs from `qcom,sm8550-gcc.h`.
- Shared qcom CC helpers: `qcom_cc_map()`, `qcom_cc_register_rcg_dfs()`, `qcom_cc_really_probe()`, and `qcom_branch_set_clk_en()`.

## Risks And Edge Cases

- Binding order is critical. A mismatch between the GCC node `clocks` list and the `DT_*` enum can silently select the wrong pipe, symbol, XO, or sleep parent.
- Rate tables are hardware-facing. Mistakes in QUP fractional rates, SDCC floor rates, UFS high-speed rates, PCIe rchng rates, or USB master rates can break peripheral function or overclock hardware.
- Halt-check mode changes are risky. Pipe and symbol clocks use delayed/skip halt checks for externally timed sources, while shared infrastructure uses voted checks. Converting these to ordinary halt checks can cause false timeouts or races.
- Probe mutates non-obvious retention and always-on state. Removing the UFS ICE force bit, always-on AHB/XO enables, or `GDSC_SLEEP_ENA_VOTE` clear may cause suspend/resume or late peripheral failures.
- GDSC collapse register offsets and masks are shared control-plane data. Incorrect masks can collapse the wrong PCIe controller/PHY domain.
- The reset map is dense and offset-based. Off-by-one reset IDs or register offsets could reset camera, display, GPU, PCIe, UFS, USB, or video blocks unexpectedly.
- External PHY pipe and UFS symbol clocks depend on PHY providers. Missing or late providers can lead to probe deferral or unusable high-speed links.

## Test Signals

- Build with the SM8550 GCC Kconfig option enabled and ensure no missing binding IDs, bad initializer types, or qcom clock helper API mismatches.
- Boot an SM8550 device tree with `qcom,sm8550-gcc` and confirm GCC probes before dependent PCIe, UFS, USB, SDCC, QUP, GPU/display/camera/video consumers.
- Inspect `/sys/kernel/debug/clk/clk_summary` for GPLLs, GP clocks, QUPv3 wrapper clocks, SDCC2/4, UFS, PCIe, and USB entries.
- Exercise QUP I2C/SPI/UART serial engines, SDCC2/SDCC4 storage, UFS link bring-up and ICE operation, PCIe0/1 link training, and USB3 operation.
- Validate power domains by toggling PCIe, UFS, and USB consumers and checking genpd/GDSC debugfs state.
- Validate reset consumers for PCIe, UFS, USB PHYs, SDCC, QUP wrappers, video ARES, camera/display/GPU/video block resets.
- Suspend/resume tests should watch for regressions from the always-on clocks and the cleared GDSC sleep-vote behavior.
