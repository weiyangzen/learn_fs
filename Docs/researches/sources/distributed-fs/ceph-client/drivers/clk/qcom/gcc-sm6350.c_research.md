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
