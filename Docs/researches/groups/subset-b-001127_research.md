# Research: subset-b-001127

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-kaanapali.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-kaanapali.c

## Purpose
This file is the Qualcomm Global Clock Controller driver for the Kaanapali SoC compatible string `qcom,kaanapali-gcc`. It declares the SoC's GCC clock tree, reset lines, GDSC power domains, DFS-capable RCGs, and critical CBCRs, then exposes them through the common Qualcomm clock-controller probe path. The driver is mostly static hardware description: each `clk_alpha_pll`, `clk_rcg2`, `clk_branch`, mux, divider, reset, and GDSC entry maps a device-tree clock/reset ID to MMIO offsets and common clk operations.

## Important APIs, Types, And Functions
- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` define fixed Taycan EKO T GPLLs: `gcc_gpll0`, `gcc_gpll0_out_even`, `gcc_gpll1`, `gcc_gpll4`, `gcc_gpll7`, and `gcc_gpll9`.
- `struct parent_map` and `struct clk_parent_data` arrays encode RCG parent selector values and the corresponding Linux clock parents. Some parents are external DT clocks such as `DT_BI_TCXO`, `DT_SLEEP_CLK`, PCIe pipe, UFS symbols, and USB pipe.
- `struct clk_regmap_phy_mux`, `struct clk_regmap_mux`, and `struct clk_regmap_div` cover PHY-sourced pipe/symbol clocks and read-only post-dividers, notably PCIe pipe, UFS RX/TX symbol clocks, USB3 pipe selection, QUPV3 wrap1 S2, and USB mock UTMI postdivider.
- `struct clk_rcg2` instances provide programmable roots for GP clocks, PCIe aux/rchng, PDM, QUPV3/I2C/QSPI serial engines, SDCC2/SDCC4, UFS PHY AXI/ICE/Unipro/AUX, and USB3 master/mock/aux clocks. Frequency tables use `F()` entries with parent IDs, dividers, and M/N values.
- `struct clk_branch` instances gate leaf and bus clocks. They use `clk_branch2_ops` or `clk_branch2_aon_ops`, `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, or `BRANCH_HALT_DELAY`, and optional hardware clock-gating fields.
- `struct gdsc` entries describe power domains for PCIe, PCIe PHY, UFS memory PHY, UFS PHY, USB30 primary, and USB3 PHY.
- `gcc_kaanapali_clocks[]`, `gcc_kaanapali_gdscs[]`, and `gcc_kaanapali_resets[]` are the binding-facing registration tables indexed by `dt-bindings/clock/qcom,kaanapali-gcc.h`.
- `gcc_dfs_clocks[]` declares dynamic frequency scaling support for selected QUPV3 RCGs.
- `gcc_kaanapali_critical_cbcrs[]` lists boot-critical CBCR offsets the common driver data preserves.
- `clk_kaanapali_regs_configure()` calls `qcom_branch_set_force_mem_core()` for `gcc_ufs_phy_ice_core_clk`.
- `gcc_kaanapali_probe()` delegates to `qcom_cc_probe(pdev, &gcc_kaanapali_desc)`.

## Control Flow
At module/subsys initialization, `gcc_kaanapali_init()` registers a platform driver named `gcc-kaanapali`. Device-tree matching on `qcom,kaanapali-gcc` invokes `gcc_kaanapali_probe()`, which passes the descriptor to `qcom_cc_probe()`. The Qualcomm common clock-controller layer maps the MMIO range according to `gcc_kaanapali_regmap_config`, registers the clock providers, reset controller, and GDSC domains, applies `gcc_kaanapali_driver_data`, and makes the exported IDs available to consumers. Runtime clock operations thereafter are handled by the common clk framework and Qualcomm helper ops referenced by each static object.

There is no custom runtime state machine in this file. The only local side-effect outside registration is `clk_kaanapali_regs_configure()`, which forces memory core retention behavior for the UFS ICE core branch during controller setup.

## State And Persistence
State is hardware state in GCC MMIO registers. The driver does not allocate persistent private state or store software configuration across boots. PLL enable state, branch enables, mux selects, divider values, GDSC status, resets, hardware clock gating, DFS changes, and critical CBCR handling all persist only as register contents until hardware reset or power loss. The `qcom_cc_desc` and static clock descriptors are immutable registration data.

## Dependencies And Integration Points
- Linux common clk framework via `clk-provider.h`.
- Qualcomm clock helper implementations: `clk-alpha-pll`, `clk-branch`, `clk-rcg`, `clk-regmap`, `clk-regmap-divider`, `clk-regmap-mux`, `clk-regmap-phy-mux`, `common`, `gdsc`, and `reset`.
- Device-tree clock/reset bindings in `dt-bindings/clock/qcom,kaanapali-gcc.h`; array indices must match the binding constants exactly.
- External parent clocks are supplied by device tree indices: XO, always-on XO, sleep clock, PCIe pipe, UFS symbol clocks, and USB3 pipe wrapper clock.
- Consumer drivers for PCIe, UFS, USB3, SDCC, QUPV3 serial engines, PDM, camera/display/video/GPU/EVA, and interconnect/NOC paths request these clocks, resets, and power domains by DT ID.
- GDSCs integrate with Linux generic power domains through the Qualcomm GDSC layer.

## Risks And Edge Cases
- Binding/table index drift is the largest correctness risk: a misplaced entry in `gcc_kaanapali_clocks[]`, `gcc_kaanapali_gdscs[]`, or `gcc_kaanapali_resets[]` silently exposes the wrong hardware control to consumers.
- The driver relies on many hard-coded register offsets and bit numbers. A wrong `halt_reg`, `enable_reg`, `hwcg_reg`, collapse register, or reset offset can cause hangs, incorrect power collapse, or clocks that appear enabled but do not reach hardware.
- `BRANCH_HALT_SKIP`, `BRANCH_HALT_DELAY`, and `BRANCH_HALT_VOTED` choices encode hardware behavior. Overly strict halt checking can time out; overly loose checking can hide failures.
- External PHY mux parents for PCIe/UFS/USB require correct DT parent ordering and PHY provider readiness. Bad parent wiring can break high-speed link bring-up even when GCC registration succeeds.
- `qcom_branch_set_force_mem_core()` on the UFS ICE core is a targeted workaround. Removing or misapplying it may regress UFS inline crypto or low-power behavior.
- DFS metadata is limited to QUPV3 RCGs. Missing a DFS-capable RCG or listing the wrong RCG can cause firmware/clock handoff issues.
- Critical CBCR offsets keep infrastructure clocks alive. Omissions can break boot or runtime PM; stale offsets can keep unnecessary clocks on.

## Test Signals
- Build coverage: compile the driver with the matching Qualcomm clock framework and Kaanapali bindings enabled.
- Probe coverage: boot a Kaanapali DT with `qcom,kaanapali-gcc` and confirm `qcom_cc_probe()` succeeds without regmap, clock registration, reset, or GDSC errors.
- Clock summary: inspect `/sys/kernel/debug/clk/clk_summary` for expected GPLLs, QUPV3, SDCC, UFS, USB, PCIe, and media clocks, including sensible parentage and rates after consumers probe.
- Functional consumers: exercise PCIe link training, UFS enumeration and inline crypto path, USB3 link modes, SDCC2/SDCC4 storage, QUPV3 I2C/SPI/UART/QSPI, PDM, and display/camera/video/GPU/EVA clocks as applicable to the board.
- Power-management signals: suspend/resume and runtime PM tests should verify GDSC transitions, retained critical CBCRs, and no unexpected clock-off hangs.
- Reset signals: consumer reset assertions/deassertions should target expected blocks, especially PCIe, QUPV3 wrappers, UFS, USB PHYs, and media resets.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-kaanapali.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-mdm9607.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-mdm9607.c

## Purpose
This file is the Qualcomm GCC driver for the MDM9607 modem SoC compatible string `qcom,gcc-mdm9607`. It registers the SoC's PLLs, root clock generators, branch gates, and a small reset map through the Qualcomm common clock-controller layer. The hardware described here covers XO/sleep parents, GPLL/BIMC PLLs, BLSP serial controllers, crypto, GP clocks, PDM, SDCC, APSS/TCU, USB HS/HSIC, MSS, SMMU, QDSS, and core NOC/APSS bus clocks.

## Important APIs, Types, And Functions
- `enum { P_XO, P_BIMC, P_GPLL0, P_GPLL1, P_GPLL2, P_SLEEP_CLK }` defines internal parent IDs used by parent maps and frequency tables.
- `gpll0_early` and `gpll2_early` are `clk_alpha_pll` objects with post-divided `gpll0` and `gpll2` outputs. `gpll1` and `bimc_pll` are classic `clk_pll` objects with `clk_regmap` vote wrappers.
- Parent maps cover XO/GPLL0, XO/GPLL0/GPLL1/sleep, XO/GPLL0/GPLL2, XO/GPLL0/GPLL1/GPLL2, and XO/GPLL0/BIMC.
- `clk_rcg2` roots define rates for APSS AHB, PCNOC/system NOC, six BLSP I2C/SPI/UART sources, crypto, GP1-3, PDM2, SDCC1/2, APSS TCU, USB HS system, USB HSIC, HSIC IO calibration, and HSIC system clocks.
- `clk_branch` objects expose the actual gateable clocks, usually pointing at one RCG or NOC parent and using `clk_branch2_ops`.
- `gcc_mdm9607_clocks[]` maps every binding ID from `dt-bindings/clock/qcom,gcc-mdm9607.h` to its `struct clk_regmap`.
- `gcc_mdm9607_resets[]` maps USB HS/HSIC, MSS restart, USB2 PHY-only, and QUSB2 PHY resets.
- `gcc_mdm9607_probe()` explicitly maps the controller, votes GPLL0 on with `regmap_update_bits(regmap, 0x45000, BIT(0), BIT(0))`, then calls `qcom_cc_really_probe()`.

## Control Flow
`gcc_mdm9607_init()` is registered with `core_initcall`, so this controller is registered early. When a matching platform device appears, `gcc_mdm9607_probe()` calls `qcom_cc_map()` to obtain the regmap for the GCC MMIO block. If mapping fails, the probe returns the error. Otherwise, it sets the GPLL0 vote bit because acpuclock requires GPLL0 enabled, then hands the regmap and descriptor to `qcom_cc_really_probe()` to register clocks and resets.

After probe, all rate changes, parent selection, enables, disables, and reset operations are performed through common clk/reset callbacks. The local file has no per-request logic once registration succeeds.

## State And Persistence
The driver's software data is static and read-only after registration. Persistent hardware state is limited to GCC registers: PLL votes, PLL programming, RCG source/divider/M/N configuration, branch enables, halt status, and reset bits. The explicit GPLL0 vote modifies the hardware vote register during probe and may keep GPLL0 active for CPU clock consumers. No state is stored in files, firmware variables, or dynamically allocated driver-private structures.

## Dependencies And Integration Points
- Linux common clk framework, platform driver core, regmap, reset controller, and device tree matching.
- Qualcomm common clock infrastructure: `common.h`, `clk-regmap.h`, `clk-alpha-pll.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h` headers. This driver includes `gdsc.h` but does not register GDSCs.
- Binding IDs from `dt-bindings/clock/qcom,gcc-mdm9607.h` must align with `gcc_mdm9607_clocks[]` and `gcc_mdm9607_resets[]`.
- Device tree must provide firmware-named parents `xo` and `sleep_clk`.
- Consumers include BLSP I2C/SPI/UART controllers, crypto engine, SDCC controllers, USB HS/HSIC blocks, APSS/TCU, MSS, SMMU, QDSS DAP, PDM, PRNG, and bus fabric.
- The special GPLL0 vote is an integration contract with the CPU clock path (`acpuclock`) and should be considered when changing probe order or PLL handling.

## Risks And Edge Cases
- Incorrect binding indices or array placement can miswire clocks and resets for many consumers.
- The GPLL2 enable mask comment notes that it uses `BIT(3)` rather than the expected bit 2. Changing this to look "regular" would likely break the hardware vote.
- The probe-time GPLL0 vote is mandatory for acpuclock. If removed or delayed, CPU clock initialization can fail or run from an unintended source.
- Several branches omit explicit halt checks or use `BRANCH_HALT_VOTED`; mismatches between hardware behavior and the chosen check can cause false timeouts or hidden failures.
- Fractional dividers in SDCC, USB, PDM, and UART tables use non-integer divisors encoded through the `F()` macro. Rate-table changes need hardware-validation, especially for storage and USB tolerance.
- `bimc_ddr_clk_src` uses `CLK_GET_RATE_NOCACHE`; stale rate assumptions from consumers or tests can mask real parent changes.
- This driver is early-registered with `core_initcall`; dependencies on parent clocks and DT names must be available early enough.

## Test Signals
- Build the driver with MDM9607 DT bindings and Qualcomm clock helpers.
- Boot a board or test DT containing `qcom,gcc-mdm9607` and verify early probe success plus absence of `qcom_cc_map()` or clock-registration errors.
- Confirm GPLL0 vote bit behavior and CPU/acpuclock initialization.
- Use debugfs clk summaries to verify XO/sleep parents, GPLL0/GPLL1/GPLL2/BIMC parents, BLSP serial rates, SDCC rates, USB HS/HSIC rates, and APSS/TCU rates.
- Exercise BLSP UART/I2C/SPI instances 1-6, SDCC1/2, USB HS and HSIC paths, crypto, PRNG, and modem/APSS bus consumers.
- Assert and deassert listed resets via consumers or reset-controller tests, especially USB and MSS restart.
- Run suspend/resume or runtime PM smoke tests to catch always-on/voted clock and NOC dependency regressions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-mdm9607.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-mdm9615.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-mdm9615.c

## Purpose
This file is the Qualcomm GCC driver for the MDM9615 modem SoC compatible string `qcom,gcc-mdm9615`. It describes an older GCC block using classic PLLs, voted PLL wrappers, legacy `clk_rcg` roots, branch gates, and reset maps. It exposes clocks for GSBI UART/QUP blocks, GP clocks, PMEM, PRNG, SDC, USB HS/HSIC, crypto engine, BAM/DMA, PMIC/RPM, EBI2, and related AHB/H clocks.

## Important APIs, Types, And Functions
- Device-tree parent indices include `DT_CXO` and `DT_PLL4`. Internal parent IDs are `P_CXO`, `P_PLL8`, and `P_PLL14`.
- PLL definitions include `pll0`, external/voted `pll4_vote`, `pll8`, and `pll14`, with vote wrappers using `clk_pll_vote_ops`.
- Parent maps `gcc_cxo_map`, `gcc_cxo_pll8_map`, and `gcc_cxo_pll14_map` drive RCG source selection.
- Legacy `struct clk_rcg` roots describe GSBI UART sources, GSBI QUP sources, GP0-2 sources, PRNG source, SDC1/2 sources, USB HS1 and HSIC sources. These use explicit NS/MD registers and `mn`, `p`, and `s` bitfield layouts rather than the newer `clk_rcg2` shape.
- `struct clk_branch` entries gate each source or bus clock and include halt registers/bits, hardware clock gating fields, and flags such as `CLK_SET_RATE_PARENT`, `CLK_SET_PARENT_GATE`, `CLK_SET_RATE_GATE`, and `CLK_IGNORE_UNUSED`.
- `gcc_mdm9615_clks[]` maps binding constants from `dt-bindings/clock/qcom,gcc-mdm9615.h` to the static clock objects.
- `gcc_mdm9615_resets[]` maps reset constants from `dt-bindings/reset/qcom,gcc-mdm9615.h` to register offsets and optional bits.
- `gcc_mdm9615_probe()` maps the MMIO block through `qcom_cc_map()` and registers the descriptor with `qcom_cc_really_probe()`.

## Control Flow
The module registers its platform driver at `core_initcall` time. A device-tree node matching `qcom,gcc-mdm9615` invokes `gcc_mdm9615_probe()`. Probe maps the controller register window using `gcc_mdm9615_regmap_config`, returns the mapping error if present, and otherwise calls `qcom_cc_really_probe()` to register clocks and resets. Runtime control is then fully delegated to the common clk and reset frameworks.

There is no local clock policy beyond the static descriptors. The one notable static policy is `CLK_IGNORE_UNUSED` on `usb_hs1_system_clk`, keeping that USB system clock from being disabled by the common unused-clock cleanup.

## State And Persistence
The file maintains no dynamic driver-private state. Hardware state lives in MMIO registers for PLL enables/votes, RCG source and M/N programming, branch gates, halt status, hardware clock gating, and reset bits. The static tables are compiled into the driver and do not persist user or runtime choices. Register state is lost across hardware reset or power loss.

## Dependencies And Integration Points
- Linux platform driver, device tree, regmap, reset controller, and common clk frameworks.
- Qualcomm helpers from `common.h`, `clk-regmap.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, and `reset.h`.
- Clock binding constants in `dt-bindings/clock/qcom,gcc-mdm9615.h` and reset constants in `dt-bindings/reset/qcom,gcc-mdm9615.h`.
- Device tree must provide `DT_CXO` as `cxo_board` and `DT_PLL4` as `pll4`; the driver also registers/votes PLL0/PLL8/PLL14 internally.
- Consumers include GSBI UART/QUP devices, SDC1/2, USB HS1/HSIC, PRNG, CE1, DMA BAM, PMIC arbiter/SSBI, RPM message RAM, EBI2, ADM, and bus/peripheral H clocks.
- The `MODULE_ALIAS("platform:gcc-mdm9615")` supports platform module alias matching in addition to OF matching.

## Risks And Edge Cases
- This is a legacy RCG layout with hand-coded NS/MD bitfields. Mistakes in `mn`, `p`, or `s` shifts and widths can produce wrong rates even when the clock registers successfully.
- Parent mapping values are sparse (`P_PLL8` selector 3, `P_PLL14` selector 4). Normalizing these values would break hardware source selection.
- `pll4_vote` is an external parent indexed from DT rather than a locally defined PLL. Missing or misordered DT parents can break clocks that depend on it.
- Branch halt registers share status words with different bits. A wrong halt bit can produce false-positive enable success or timeout.
- `usb_hs1_system_clk` is marked `CLK_IGNORE_UNUSED`; removing that can let common clk disable a clock required by USB hardware.
- Some branches use hardware clock gating bits and combined enable masks, for example PMEM, BAM, EBI2, and GSBI H clocks. Incorrect masks can enable only part of a functional path.
- Reset offsets include both whole-register and bit-specific resets. Incorrect bit use may reset wider hardware than intended.

## Test Signals
- Build with the MDM9615 clock and reset bindings.
- Boot with a `qcom,gcc-mdm9615` node and verify `qcom_cc_really_probe()` succeeds.
- Inspect debugfs clock summaries for PLL0/PLL4/PLL8/PLL14 votes, GSBI UART/QUP source rates, SDC rates, USB HS/HSIC rates, and branch enable states.
- Exercise GSBI UART and QUP instances 1-5, SDC1/2, USB HS1, USB HSIC, PRNG, CE1, DMA BAM, PMIC arbiter, RPM message RAM, and EBI2 consumers.
- Verify reset-controller behavior for DMA BAM, CE1, SDC, ADM, USB, GSBI, and PDM resets.
- Run unused-clock cleanup and suspend/resume tests to confirm `CLK_IGNORE_UNUSED`, voted PLLs, and hardware-gated branches do not regress device availability.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-mdm9615.c -->
