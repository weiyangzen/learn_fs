# Research: subset-b-001142

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm6350.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm6350.c

## Purpose

`gcc-sm6350.c` is the Qualcomm Global Clock Controller driver for the SM6350 SoC. It exposes the GCC register block to Linux as a clock provider, reset controller, GDSC power-domain provider, and dynamic-frequency-scaling clock provider using binding IDs from `dt-bindings/clock/qcom,gcc-sm6350.h`.

The file is mostly declarative hardware description. It models Fabia GPLLs, post-dividers, parent mux encodings, RCG rate tables, read-only dividers, branch gates, GDSCs, resets, and QUP DFS descriptors, then registers them through the shared Qualcomm clock-controller framework.

## Important APIs, Types, And Data

- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv`: define `gpll0`, `gpll6`, and `gpll7`, plus `gpll0_out_even`, `gpll0_out_odd`, and `gpll6_out_even`. These use `CLK_ALPHA_PLL_TYPE_FABIA` and fixed Fabia PLL/post-divider ops.
- `struct parent_map` and `struct clk_parent_data`: translate hardware source selector values to CCF parents. External parents are referenced by firmware names such as `bi_tcxo`, `bi_tcxo_ao`, and `sleep_clk`; internal parents are GPLL hardware pointers.
- `struct clk_regmap_div`: exposes read-only GPU and NPU GPLL0 divider sources at `0x4514c` and `0x4ce00`.
- `struct freq_tbl`: encodes legal RCG rates for CPUSS AHB, GP1-GP3, PDM2, twelve QUPv3 serial engines, SDCC1/SDCC2, UFS PHY AXI/ICE/AUX/UniPro, and USB3 master/mock-UTMI/PHY-aux clocks.
- `struct clk_rcg2`: implements root clock generators. Most use `clk_rcg2_ops`; SDCC2 apps uses `clk_rcg2_floor_ops` and `CLK_OPS_PARENT_ENABLE`, which matters for safe MMC rate rounding and parent enable sequencing.
- `struct clk_branch`: exports leaf gates and bus gates for camera, display, video, GPU, NPU, CPUSS, QUPv3, SDCC, UFS, USB, PDM, PRNG, CE, and NOC paths. Several branch descriptors use `CLK_SET_RATE_PARENT`, hardware clock gating fields, `BRANCH_HALT_DELAY`, `BRANCH_HALT_VOTED`, or `clk_branch_simple_ops` for hardware-controlled UFS gates.
- `struct gdsc`: describes `usb30_prim_gdsc`, `ufs_phy_gdsc`, and two votable MMNOC MMU TBU domains.
- `struct qcom_reset_map`: maps USB, UFS, QUSB2 PHY, and SDCC reset IDs to GCC reset registers.
- `struct clk_rcg_dfs_data`: registers DFS support for QUPv3 wrap0/wrap1 serial-engine RCGs.
- `struct qcom_cc_desc`: binds the regmap config, clock table, reset table, and GDSC table for registration.

## Control Flow

The platform driver matches `qcom,gcc-sm6350` and is registered with `core_initcall()`. Probe is custom rather than a direct `qcom_cc_probe()` wrapper:

1. `gcc_sm6350_probe()` calls `qcom_cc_map()` to map the GCC MMIO block using a 32-bit, 4-byte-stride regmap with `max_register = 0xbf030`.
2. It writes MISC registers `0x4cf00` and `0x45f00` with mask/value `0x3` to disable the GPLL0 active input to NPU and GPU.
3. It registers DFS-capable QUPv3 RCGs with `qcom_cc_register_rcg_dfs()`.
4. It calls `qcom_cc_really_probe()` to register clocks, resets, and GDSCs with the kernel frameworks.

After probe, consumers use standard CCF, reset, and power-domain APIs through device-tree IDs. Rate changes are handled by shared RCG ops selecting rows from the local `freq_tbl` arrays and programming parent selectors, dividers, and M/N fields.

## State And Persistence Behavior

The driver has no allocated private state and no suspend/resume callbacks. Persistent state is the GCC MMIO register state, plus framework-managed clock/reset/GDSC objects created at probe.

Clock enables, RCG rates, PLL enables, reset assertions, and GDSC power states persist in hardware until changed by Linux, firmware, or reset. The probe-time MISC writes intentionally alter persistent GPU/NPU source-selection behavior before clocks are registered. The DFS registration makes QUPv3 RCGs available to the Qualcomm DFS framework, so serial-engine rates may be coordinated through shared RCG DFS machinery rather than only static CCF programming.

GDSC behavior differs by domain: USB is retention/on (`PWRSTS_RET_ON`), UFS is off/on, and MMNOC TBU domains are votable off/on domains.

## Dependencies And Integration Points

- Linux CCF and Qualcomm helpers: `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `clk-regmap.h`, `clk-regmap-divider.h`, `clk-regmap-mux.h`, `common.h`, and `gdsc.h`.
- Regmap: 32-bit register and value widths, 4-byte stride, `fast_io = true`.
- Reset framework: IDs from `qcom,gcc-sm6350.h` map through `gcc_sm6350_resets[]`.
- GDSC/power-domain framework: GDSC IDs in the same binding map through `gcc_sm6350_gdscs[]`.
- Device tree: external parents must provide firmware-clock names `bi_tcxo`, `bi_tcxo_ao`, and `sleep_clk`.
- Platform lifecycle: `MODULE_DEVICE_TABLE()`, `platform_driver_register()`, `core_initcall()`, and `module_exit()`.

## Risks And Edge Cases

- The MISC writes for GPU and NPU are board-visible hardware policy. Wrong offsets or masks could select a bad GPLL0 active input or break GPU/NPU clocking.
- Parent-map selector values must match the SM6350 clock plan. A wrong selector can silently route QUP, SDCC, UFS, USB, GPU, or NPU clocks to the wrong PLL output.
- QUPv3 frequency tables are shared across twelve serial engines and include fractional UART-friendly rates. Mistakes can affect UART baud accuracy, SPI/I2C timing, and DFS transitions.
- SDCC1 and SDCC2 have different parent sets and rate tables; SDCC2 uses floor ops and parent-enable behavior. Changing this can overclock removable storage or cause parent-disable races.
- UFS has several paired software and hardware-control branch gates. The simple hardware-control branches depend on the corresponding software branch and halt behavior being modeled correctly.
- USB3 pipe and symbol clocks use skip/delay style halt checks in related branches. Treating these as ordinary halt-checked clocks may produce false failures when PHY-generated clocks are absent until link bring-up.
- The exported clock table is sparse and binding-indexed. Consumers must request IDs that are actually populated by this driver.

## Test Signals

- Build with the SM6350 GCC option enabled and verify no missing binding IDs, bad initializer types, or section warnings.
- Boot a device tree containing `compatible = "qcom,gcc-sm6350"` and confirm the driver probes before QUPv3, SDCC, UFS, USB, GPU/NPU, camera, display, and video consumers settle.
- Inspect `/sys/kernel/debug/clk/clk_summary` for GPLLs, `gcc_qupv3_wrap*_s*_clk`, `gcc_sdcc1_apps_clk`, `gcc_sdcc2_apps_clk`, `gcc_ufs_phy_*`, `gcc_usb30_prim_*`, GPU/NPU divider sources, and always-needed fabric clocks.
- Exercise UART/SPI/I2C on both QUP wrappers, SD/eMMC on SDCC1/2, UFS storage, USB3, PDM, PRNG/crypto, and multimedia blocks that consume camera/display/video/GPU/NPU clocks.
- Test resets for USB PHY/controller, QUSB2 PHYs, UFS PHY, and SDCC blocks on hardware where reset cycling is safe.
- Confirm GDSC transitions for USB and UFS, and vote behavior for MMNOC TBU domains, through power-domain debugfs or subsystem runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm6350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm6375.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm6375.c

## Purpose

`gcc-sm6375.c` is the Qualcomm Global Clock Controller driver for SM6375. It exports GCC clocks, resets, GDSC power domains, and DFS-capable QUP root clocks using IDs from `dt-bindings/clock/qcom,sm6375-gcc.h`.

Compared with smaller GCC drivers, this file covers a broad multimedia clock plan: camera CSIPHY/TFE/OPE/MCLK clocks, video/Venus clocks, display/GPU/NPU fabric gates, QUPv3 serial engines, SDCC, UFS, USB, and many MMU TBU power-domain votes. It combines declarative descriptors with probe-time PLL configuration and always-on branch votes.

## Important APIs, Types, And Data

- `struct pll_vco` and `struct alpha_pll_config`: define Lucid and Zonda VCO ranges plus explicit configurations for `gpll10` at 1152 MHz, `gpll11` around 532 MHz, `gpll8`, and `gpll9`.
- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv`: model GPLL0/1/3/4/5/6/7/8/9/10/11, with Lucid PLL ops for most GPLLs and Zonda PLL ops for GPLL9. Several post-dividers expose even/odd/main derived outputs.
- Local `DT_*` enums and `clk_parent_data`: identify external clock-parent indices `DT_BI_TCXO`, `DT_BI_TCXO_AO`, and `DT_SLEEP_CLK`.
- `struct parent_map`: maps many hardware selector encodings to GPLL0, GPLL3, GPLL5, GPLL6, GPLL7, GPLL8, GPLL9, GPLL10, GPLL11, XO, and sleep parents.
- `struct freq_tbl`: supplies camera, CPUSS, GP, PDM, QUPv3, SDCC, UFS, USB, and video rates. Camera tables are especially dense for AXI, CCI, CSI PHY timers, five MCLKs, OPE, TFE, CSID, CPHY RX, and top AHB.
- `struct clk_rcg2`: models RCGs. Many multimedia RCGs use `clk_rcg2_shared_ops`, reflecting shared or potentially firmware-coordinated resources. Some set `CLK_SET_RATE_PARENT` to propagate rate requests into PLLs.
- `struct clk_regmap_div`: exposes read-only post-dividers for CPUSS AHB and USB mock UTMI.
- `struct clk_branch`: exports gates for camera, display, GPU, video, UFS, USB, QUPv3, SDCC, PDM, PRNG, QMIP, fabric, and clock-reference paths. Branches use a mix of regular, voted, delayed, skip, and simple hardware-control halt handling.
- `struct gdsc`: describes USB, UFS, CAMSS, Venus, Vcodec, and four votable Turing/MM SNOC MMU TBU domains. `vcodec0_gdsc` is hardware-controlled.
- `struct qcom_reset_map`: maps MMSS, USB/PHY, QUSB2 PHY, SDCC, QUP wrappers, PDM, GPU, UFS, CAMSS, Venus, Vcodec, and video-interface resets.
- `struct clk_rcg_dfs_data`: enables DFS for six QUPv3 engines in wrapper 0 and six in wrapper 1.
- `struct qcom_cc_desc`: registers clocks, resets, and GDSCs over a regmap with `max_register = 0xc7000`.

## Control Flow

The driver matches `qcom,sm6375-gcc` and registers at `subsys_initcall()`. Probe proceeds as follows:

1. `qcom_cc_map()` maps the GCC MMIO region.
2. `qcom_cc_register_rcg_dfs()` registers the QUPv3 DFS RCG list.
3. `qcom_branch_set_clk_en()` force-enables three always-on branches: camera XO at `0x17028`, CPUSS GNOC at `0x2b004`, and display XO at `0x1702c`.
4. `clk_lucid_pll_configure()` programs GPLL10, GPLL11, and GPLL8 from their static configs.
5. `clk_zonda_pll_configure()` programs GPLL9 from its static config.
6. `qcom_cc_really_probe()` registers the clock, reset, and power-domain providers.

Runtime control then flows through normal CCF operations. Leaf branches can request parent rates; RCG ops select rate-table rows and write parent/divider/M/N fields; GDSC and reset operations are delegated to the Qualcomm common code.

## State And Persistence Behavior

The driver keeps no private dynamic state after probe. Hardware state lives in GCC registers, PLL configuration registers, branch enable registers, reset registers, and GDSCR registers.

Probe actively programs four PLLs and force-enables three branches, so this driver does more than expose pre-existing hardware state. Those changes persist until later clock framework operations, firmware, reset, or power-domain changes alter them. DFS-capable QUP RCGs may be reprogrammed through the DFS framework for serial-engine operating points.

USB uses `PWRSTS_RET_ON` with an in-code TODO noting it should become off/on when USB suspend support is proper. UFS, CAMSS, Venus, and MMU TBU domains use off/on semantics, while `vcodec0_gdsc` is marked `HW_CTRL`, leaving power transitions partly hardware-managed.

## Dependencies And Integration Points

- Linux CCF and Qualcomm clock helpers: alpha PLL, RCG, branch, regmap divider/mux, and GDSC support.
- PLL configuration helpers: `clk_lucid_pll_configure()` and `clk_zonda_pll_configure()` are required for probe-time GPLL setup.
- Device-tree bindings: clock/reset/GDSC IDs from `qcom,sm6375-gcc.h`; external parent clocks are consumed by index rather than firmware name.
- Regmap: 32-bit registers, 4-byte stride, 32-bit values, fast I/O, `max_register = 0xc7000`.
- Reset framework: reset IDs are handled by `gcc_sm6375_resets[]`.
- Power domains: GDSC IDs are handled by `gcc_sm6375_gdscs[]`, including votable and hardware-controlled domains.
- Platform lifecycle: `MODULE_DEVICE_TABLE()`, `subsys_initcall()`, platform driver probe/remove registration, and module exit.

## Risks And Edge Cases

- Probe-time PLL configuration is hardware-critical. Incorrect Lucid/Zonda config fields can destabilize camera, video, or other high-frequency domains.
- Parent data for `gcc_parent_data_14` maps both GPLL11 odd and even selector entries to `&gpll11.clkr.hw`; this mirrors the local descriptor but is easy to misread when modifying video parent tables.
- Many camera RCGs use shared ops and shared GPLL sources. Camera clock changes can affect multiple TFE/CSID/OPE/MCLK paths if parent propagation or shared-rate assumptions are wrong.
- Always-on branch votes are not optional policy. Removing camera XO, display XO, or CPUSS GNOC force-enables can break dependent blocks that assume these roots survive unused-clock cleanup.
- USB GDSC retention semantics are deliberate. Moving to off/on before USB suspend/runtime PM is correct can cause USB resume or PHY failures.
- Vcodec0 uses hardware-controlled GDSC behavior; software-only assumptions in tests or consumers may observe delayed or autonomous transitions.
- QUP DFS coverage must stay aligned with the QUP RCGs exported in the clock table. Missing DFS registration can cause serial-engine performance or rate-switching issues.
- Reset registers are dense around multimedia blocks. Wrong offsets can reset adjacent CAMSS, Venus, Vcodec, UFS, GPU, or QUP hardware.

## Test Signals

- Build with SM6375 GCC enabled and check for binding ID, PLL ops, and initializer warnings.
- Boot with `compatible = "qcom,sm6375-gcc"` and verify successful probe after PLL configuration but before camera, display, video, UFS, USB, QUP, SDCC, GPU, and NPU consumers complete.
- Inspect `clk_summary` for `gpll8`, `gpll9`, `gpll10`, `gpll11`, camera TFE/CSID/MCLK/OPE roots, `gcc_video_venus_clk_src`, QUPv3 clocks, UFS, USB, and the always-on camera/display XO and CPUSS GNOC branches.
- Exercise camera capture paths using multiple CSIPHY/TFE/CSID/MCLK combinations, video encode/decode/Venus paths, display, GPU/NPU fabrics, UFS, USB3, SDCC1/2, and QUP UART/SPI/I2C.
- Verify GDSC behavior for CAMSS, Venus, Vcodec, USB, UFS, and MMU TBU vote domains through runtime PM and power-domain debugfs.
- Safely test reset lines for QUP wrappers, PDM, GPU, SDCC, UFS, USB PHY/controller, CAMSS, Venus, Vcodec, and MMSS/video-interface blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm6375.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm7150.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm7150.c

## Purpose

`gcc-sm7150.c` is the Qualcomm Global Clock Controller driver for SM7150. It provides clock, reset, GDSC, DFS, and standalone hardware-clock registration for the SoC GCC block using IDs from `dt-bindings/clock/qcom,sm7150-gcc.h`.

The driver covers core infrastructure and many peripheral domains: CPUSS, GPU/NPU, camera/display/video fabric gates, QUPv3 serial engines, SDCC1/2/4, TSIF, UFS, USB3, PCIe, voltage-sensor clocks, and MMU TBU GDSCs. Most behavior is descriptor-driven, with targeted probe-time register programming and always-on clock votes.

## Important APIs, Types, And Data

- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv`: define Fabia GPLL0, GPLL6, and GPLL7, plus `gpll0_out_even`.
- `struct clk_fixed_factor`: exposes `gcc_pll0_main_div_cdiv`, a GPLL0 divide-by-2 hardware clock listed separately in `gcc_sm7150_hws[]`.
- Local `DT_*` enums and `clk_parent_data`: use external parent indices for `bi_tcxo`, `bi_tcxo_ao`, and `sleep_clk`.
- `struct parent_map`: maps hardware parent selector values to XO, sleep, GPLL0 main/even, GPLL6, and GPLL7 for RCGs.
- `struct freq_tbl`: encodes rates for CPUSS AHB/RBCPR, GP1-GP3, PCIe aux/refgen, PDM2, sixteen QUPv3 serial engines, SDCC1/2/4, TSIF, UFS PHY, USB3, voltage-sensor, and voltage-sensor-control roots.
- `struct clk_rcg2`: implements RCGs. SDCC roots use `clk_rcg2_floor_ops`; SDCC2 also uses `CLK_OPS_PARENT_ENABLE`. Some QUP init data sets `CLK_SET_RATE_PARENT`.
- `struct clk_branch`: exports gates for aggregate NOC/TBU, UFS, USB, PCIe, CPUSS, GPU/NPU, QUP, SDCC, TSIF, voltage sensors, camera/display/video fabric, PDM, PRNG, and reference clocks.
- Branch ops vary by hardware behavior: `clk_branch2_ops`, `clk_branch2_aon_ops`, and `clk_branch_simple_ops` are used, with halt checks including `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_VOTED`, `BRANCH_HALT_DELAY`, and `BRANCH_HALT_SKIP`.
- `struct gdsc`: includes PCIe0, UFS, USB, and seven votable AGGRE/MMNOC MMU TBU power domains.
- `struct qcom_reset_map`: maps PCIe, PCIe PHY, UFS, USB3 PHY/DP PHY/QUSB2 PHY, USB controller, and a bit-level video AXI reset with `udelay = 150`.
- `struct clk_rcg_dfs_data`: registers DFS for QUPv3 wrap0 and wrap1 engines S0-S7.
- `struct qcom_cc_desc`: registers standalone hardware clocks, regmap clocks, resets, and GDSCs over a regmap with `max_register = 0x1820b0`.

## Control Flow

The platform driver matches `qcom,sm7150-gcc` and registers with `subsys_initcall()`. Probe is custom:

1. `qcom_cc_map()` maps the GCC register space.
2. Three MISC registers are updated with mask/value `0x3` at `0x09ffc`, `0x4d110`, and `0x71028` to disable the GPLL0 active input to MM blocks, NPU, and GPU.
3. Eight branches are force-enabled with `qcom_branch_set_clk_en()`: CPUSS GNOC, video AHB, camera AHB, display AHB, camera XO, video XO, display XO, and GPU CFG AHB.
4. QUPv3 DFS descriptors for sixteen serial-engine RCGs are registered with `qcom_cc_register_rcg_dfs()`.
5. `qcom_cc_really_probe()` registers clocks, standalone hardware clocks, resets, and GDSCs.

After registration, device drivers request clocks and resets by binding ID. CCF branch and RCG ops do the runtime register programming, and GDSC/reset state changes are delegated to Qualcomm common code.

## State And Persistence Behavior

The file does not allocate private state and has no explicit runtime PM or suspend/resume callbacks. Its persistent effects are hardware register writes and framework registrations.

Probe-time MISC updates and always-on branch votes intentionally modify GCC state before consumers bind. These bits persist until reset or later software changes. Critical flags on CPUSS/sys-NOC and NPU configuration clocks protect essential fabric/control paths from unused-clock cleanup.

The standalone GPLL0 fixed-factor clock is registered through `clk_hws`, not the `clk_regmap` table, so consumers can reference the divided GPLL0 source as a CCF hardware clock. GDSCs persist as power-domain state; votable MMU TBU domains represent shared votes rather than exclusive software ownership.

## Dependencies And Integration Points

- Linux CCF and Qualcomm GCC helpers: Fabia alpha PLL, RCG, branch, regmap, reset, common, and GDSC support.
- Device tree: `qcom,sm7150-gcc` compatible plus external clock parents ordered to match `DT_BI_TCXO`, `DT_BI_TCXO_AO`, and `DT_SLEEP_CLK`.
- Regmap: 32-bit registers, 4-byte stride, 32-bit values, `fast_io = true`, and a large `max_register` covering high GCC offsets.
- Reset framework: block and bit-level resets are exported via `gcc_sm7150_resets[]`.
- Power-domain framework: PCIe0, UFS, USB, and MMU TBU domains are exported via `gcc_sm7150_gdscs[]`.
- Platform lifecycle: `MODULE_DEVICE_TABLE()`, `subsys_initcall()`, `platform_driver_register()`, and module exit.

## Risks And Edge Cases

- The probe-time MISC writes for MM, NPU, and GPU are SoC-specific. A wrong offset or mask can break multimedia, NPU, or GPU parent selection.
- Always-on branch votes preserve fabric and XO clocks needed by dependent blocks. Removing them can cause camera/display/video/GPU or CPUSS consumers to fail after unused-clock cleanup.
- QUPv3 has sixteen serial-engine RCGs and DFS descriptors. Missing one descriptor or mismatching an RCG offset can cause only one UART/SPI/I2C instance to fail, which is easy to miss in partial board tests.
- PCIe pipe and UFS symbol clocks use skipped halt checks because the signal may depend on PHY/link state. Converting them to strict halt checks can create spurious enable failures.
- SDCC1/2/4 use separate rate tables and floor ops. Rate-table mistakes can overclock storage or choose unsafe removable-card rates.
- `GCC_VIDEO_AXI_CLK_BCR` is a bit reset with an explicit delay, unlike most block resets. Treating it as an ordinary block reset can miss required settling time.
- Critical flags on CPUSS/sys-NOC and NPU config clocks are intentional fabric-protection measures. Removing them can create boot or runtime hangs.
- The clock table is sparse and split between `clk_hws` and `clks`; binding changes must update the correct array.

## Test Signals

- Build with SM7150 GCC enabled and verify all clock/reset/GDSC IDs compile, including the standalone `GCC_GPLL0_MAIN_DIV_CDIV` hardware clock.
- Boot with `compatible = "qcom,sm7150-gcc"` and confirm probe before PCIe, USB, UFS, SDCC, QUPv3, GPU/NPU, camera/display/video, TSIF, and voltage-sensor consumers.
- Inspect `clk_summary` for GPLL0/6/7, `gcc_pll0_main_div_cdiv`, QUPv3 S0-S7 clocks on both wrappers, SDCC1/2/4, UFS, USB3, PCIe0, TSIF, and voltage-sensor branches.
- Exercise PCIe link training, USB3, UFS, SD/eMMC/SDIO, QUP UART/SPI/I2C across both wrappers, TSIF if present, GPU/NPU consumers, and multimedia fabric users.
- Test reset controls for PCIe/PCIe PHY, USB PHY/DP PHY/QUSB2 PHY/controller, UFS PHY, and video AXI only on hardware where reset cycling is safe.
- Verify GDSC on/off or vote transitions for PCIe0, UFS, USB, and AGGRE/MMNOC MMU TBU domains through runtime PM and power-domain debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm7150.c -->
