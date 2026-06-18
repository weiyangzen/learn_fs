# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8960.c

## Purpose
`gcc-msm8960.c` implements the Qualcomm Global Clock Controller provider for the older MSM8960 and APQ8064 families. It exposes board-derived reference clocks, PLLs and HFPLLs, legacy RCG roots, branch gates, and reset-controller lines for serial GSBI/QUP/UART blocks, SDCC, USB, TSIF, crypto, ADM/DMA, PMIC/RPM support, and APQ8064-only SATA/PCIe/extra USB/CE resources. The file is a hardware-description table for the Linux common clock and reset frameworks, with a small amount of probe-time platform setup.

## Important APIs, Types, And Functions
The driver uses `struct clk_pll` for `pll3`, `pll8`, and `pll14`, `struct clk_regmap` vote clocks for `pll4_vote`, `pll8_vote`, and `pll14_vote`, and `struct clk_hfpll` plus `struct hfpll_data` for CPU/L2 high-frequency PLLs (`hfpll0`, `hfpll1`, `hfpll2`, `hfpll3`, and `hfpll_l2`). Parent selection is described with `parent_map`/`clk_parent_data` arrays for PXO, CXO, PLL8, and PLL3 combinations.

Most peripheral roots are legacy `struct clk_rcg` objects using `clk_rcg_ops`, with explicit NS/MD register layouts, M/N counter fields, predivider fields, source selector fields, and `freq_tbl` tables. Important families include GSBI UART and QUP roots, GP clocks, PRNG, SDC1-5, TSIF, USB HS/FS/HSIC, APQ8064 CE3, and APQ8064 SATA reference clocks. Consumer-facing gates are `struct clk_branch` objects using `clk_branch_ops`, often with `CLK_SET_RATE_PARENT` so peripheral branch rate requests propagate into their RCG source.

The exported resource arrays are `gcc_msm8960_clks` and `gcc_apq8064_clks`, both indexed by `dt-bindings/clock/qcom,gcc-msm8960.h` IDs. Reset maps are split similarly into `gcc_msm8960_resets` and `gcc_apq8064_resets`. `gcc_msm8960_desc` and `gcc_apq8064_desc` carry the chosen regmap bounds, clock array, and reset map into common QCOM CC registration. `gcc_msm8960_probe()` is the main entry point; it registers fixed board clocks for `cxo` at 19.2 MHz and `pxo` at 27 MHz, calls `qcom_cc_probe()`, applies APQ8064 HFPLL data pointers when needed, and either populates OF children or creates a legacy `qcom-tsens` platform device. `gcc_msm8960_remove()` unregisters that synthetic TSENS child.

## Control Flow
The platform driver is registered at `core_initcall()` and matches `qcom,gcc-msm8960` or `qcom,gcc-apq8064`. The match `.data` selects either `gcc_msm8960_desc` or `gcc_apq8064_desc`. Probe first creates the fixed reference-clock providers expected by many static clock descriptors, then delegates clock and reset provider registration to `qcom_cc_probe(pdev, desc)`.

After the common GCC probe succeeds, APQ8064 devices switch `hfpll1.d` and `hfpll_l2.d` to APQ8064-specific register layouts. The static HFPLL objects remain the same objects already referenced by the clock array, so later HFPLL operations dereference the updated data pointer. Finally, child handling is conditional: if the GCC node has available children, the driver uses `devm_of_platform_populate()`; if it has no available child nodes, it registers a `qcom-tsens` platform device manually and stores it as driver data for remove-time cleanup.

Runtime clock control is then framework-driven. Consumers request a clock ID from the GCC provider, common clock ops program the RCG source registers according to the frequency table and parent map, and branch ops toggle enable bits while polling the configured halt register/bit or vote status. Reset consumers assert/deassert entries from the selected `qcom_reset_map`.

## State And Persistence Behavior
There is no filesystem persistence. Persistent runtime state is hardware-visible MMIO state: PLL/HFPLL programming, vote bits, RCG source/divider/MN settings, branch enable bits, hardware clock-gating bits, and reset bits. The C file also has global static state: clock descriptors, reset maps, and mutable HFPLL `.d` pointers adjusted for APQ8064 after probe.

The probe-created fixed board clocks (`cxo_board` and `pxo_board`) are in-kernel providers that satisfy `fw_name` lookups in this driver. The optional synthetic TSENS platform device is device-model state owned by the GCC platform device and explicitly unregistered in `remove`. The many branch descriptors with `hwcg_reg`/`hwcg_bit` also describe hardware-controlled gating behavior that persists in GCC registers once programmed.

## Dependencies
This file depends on Linux platform-device, OF match, OF platform population, module, regmap, reset-controller, and common clock framework APIs. Local QCOM dependencies are `common.h` for `qcom_cc_register_board_clk()` and `qcom_cc_probe()`, `clk-pll.h`, `clk-hfpll.h`, `clk-rcg.h`, `clk-branch.h`, `clk-regmap.h`, and `reset.h`. Binding constants come from `dt-bindings/clock/qcom,gcc-msm8960.h` and `dt-bindings/reset/qcom,gcc-msm8960.h`.

External integration depends on device tree names for the PXO/CXO references, although this driver creates fixed clock providers with those names during probe. Consumers bind by GCC clock/reset phandle IDs, and legacy thermal integration can either be represented as child DT nodes or as the fallback `qcom-tsens` platform device.

## Integration Points
Major consumers include GSBI serial blocks 1-12, QUP SPI/I2C engines, UARTs, SDC/eMMC/SD controllers, USB HS/FS/HSIC blocks, TSIF, PRNG, CE crypto, ADM/DMA, PMIC arbiter, RPM message RAM, and bus fabric reset clients. APQ8064 expands the same provider with USB HS3/HS4, SATA clocks and resets, PCIe clocks and resets, CE3, and additional HFPLLs.

The two SoC descriptors are the primary integration boundary. MSM8960 exposes a wider GSBI/SDC set, while APQ8064 exposes SATA/PCIe/extra USB/CE3 and different reset coverage. Binding ID alignment is therefore critical: each array entry is directly keyed by a binding constant, and an incorrect entry changes the resource returned to device-tree consumers.

## Risks
The largest risk is hardware table accuracy: register offsets, halt bits, reset bits, parent selector values, M/N widths, and frequency table parameters are hand-coded across a large legacy register map. A single bad table entry can affect only one peripheral and may be hard to diagnose from probe logs.

Variant handling needs care. APQ8064-specific `hfpll1` and `hfpll_l2` data pointers are changed after `qcom_cc_probe()` returns; this relies on later HFPLL ops using the mutable object pointer rather than any data copied during registration. MSM8960 and APQ8064 also share many static clock objects while using different exported arrays, so changes to a shared descriptor can affect both variants.

The fallback TSENS platform-device creation is another integration risk: systems with child DT nodes use managed population instead, while systems without children get a synthetic device. Error handling after successful GCC registration can still fail probe if TSENS registration fails, leaving common-clock registration side effects to normal driver-core handling.

## Test Signals
Useful build signals are clean compilation with both binding headers and no array-index warnings. Boot signals include successful probe for both `qcom,gcc-msm8960` and `qcom,gcc-apq8064`, visible GCC clock and reset providers, successful fixed-clock registration for `cxo_board` and `pxo_board`, and correct TSENS behavior on DTs with and without child nodes.

Runtime tests should exercise representative consumers: GSBI UART baud rates, QUP SPI/I2C rates, SDCC rate switching including low initialization rates and high data rates, USB HS/FS/HSIC operation, PRNG and CE crypto clocks, PMIC/RPM support clocks, and reset-controller operations for peripheral BCRs. APQ8064-specific validation should cover SATA, PCIe, USB HS3/HS4, CE3, and HFPLL-backed CPU/L2 rate behavior.
