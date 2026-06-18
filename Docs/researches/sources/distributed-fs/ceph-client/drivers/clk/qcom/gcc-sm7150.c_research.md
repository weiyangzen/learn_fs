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
