# subset-b-001131 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8960.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8960.c

### Purpose
`gcc-msm8960.c` implements the Qualcomm Global Clock Controller provider for the older MSM8960 and APQ8064 families. It exposes board-derived reference clocks, PLLs and HFPLLs, legacy RCG roots, branch gates, and reset-controller lines for serial GSBI/QUP/UART blocks, SDCC, USB, TSIF, crypto, ADM/DMA, PMIC/RPM support, and APQ8064-only SATA/PCIe/extra USB/CE resources. The file is a hardware-description table for the Linux common clock and reset frameworks, with a small amount of probe-time platform setup.

### Important APIs, Types, And Functions
The driver uses `struct clk_pll` for `pll3`, `pll8`, and `pll14`, `struct clk_regmap` vote clocks for `pll4_vote`, `pll8_vote`, and `pll14_vote`, and `struct clk_hfpll` plus `struct hfpll_data` for CPU/L2 high-frequency PLLs (`hfpll0`, `hfpll1`, `hfpll2`, `hfpll3`, and `hfpll_l2`). Parent selection is described with `parent_map`/`clk_parent_data` arrays for PXO, CXO, PLL8, and PLL3 combinations.

Most peripheral roots are legacy `struct clk_rcg` objects using `clk_rcg_ops`, with explicit NS/MD register layouts, M/N counter fields, predivider fields, source selector fields, and `freq_tbl` tables. Important families include GSBI UART and QUP roots, GP clocks, PRNG, SDC1-5, TSIF, USB HS/FS/HSIC, APQ8064 CE3, and APQ8064 SATA reference clocks. Consumer-facing gates are `struct clk_branch` objects using `clk_branch_ops`, often with `CLK_SET_RATE_PARENT` so peripheral branch rate requests propagate into their RCG source.

The exported resource arrays are `gcc_msm8960_clks` and `gcc_apq8064_clks`, both indexed by `dt-bindings/clock/qcom,gcc-msm8960.h` IDs. Reset maps are split similarly into `gcc_msm8960_resets` and `gcc_apq8064_resets`. `gcc_msm8960_desc` and `gcc_apq8064_desc` carry the chosen regmap bounds, clock array, and reset map into common QCOM CC registration. `gcc_msm8960_probe()` is the main entry point; it registers fixed board clocks for `cxo` at 19.2 MHz and `pxo` at 27 MHz, calls `qcom_cc_probe()`, applies APQ8064 HFPLL data pointers when needed, and either populates OF children or creates a legacy `qcom-tsens` platform device. `gcc_msm8960_remove()` unregisters that synthetic TSENS child.

### Control Flow
The platform driver is registered at `core_initcall()` and matches `qcom,gcc-msm8960` or `qcom,gcc-apq8064`. The match `.data` selects either `gcc_msm8960_desc` or `gcc_apq8064_desc`. Probe first creates the fixed reference-clock providers expected by many static clock descriptors, then delegates clock and reset provider registration to `qcom_cc_probe(pdev, desc)`.

After the common GCC probe succeeds, APQ8064 devices switch `hfpll1.d` and `hfpll_l2.d` to APQ8064-specific register layouts. The static HFPLL objects remain the same objects already referenced by the clock array, so later HFPLL operations dereference the updated data pointer. Finally, child handling is conditional: if the GCC node has available children, the driver uses `devm_of_platform_populate()`; if it has no available child nodes, it registers a `qcom-tsens` platform device manually and stores it as driver data for remove-time cleanup.

Runtime clock control is then framework-driven. Consumers request a clock ID from the GCC provider, common clock ops program the RCG source registers according to the frequency table and parent map, and branch ops toggle enable bits while polling the configured halt register/bit or vote status. Reset consumers assert/deassert entries from the selected `qcom_reset_map`.

### State And Persistence Behavior
There is no filesystem persistence. Persistent runtime state is hardware-visible MMIO state: PLL/HFPLL programming, vote bits, RCG source/divider/MN settings, branch enable bits, hardware clock-gating bits, and reset bits. The C file also has global static state: clock descriptors, reset maps, and mutable HFPLL `.d` pointers adjusted for APQ8064 after probe.

The probe-created fixed board clocks (`cxo_board` and `pxo_board`) are in-kernel providers that satisfy `fw_name` lookups in this driver. The optional synthetic TSENS platform device is device-model state owned by the GCC platform device and explicitly unregistered in `remove`. The many branch descriptors with `hwcg_reg`/`hwcg_bit` also describe hardware-controlled gating behavior that persists in GCC registers once programmed.

### Dependencies
This file depends on Linux platform-device, OF match, OF platform population, module, regmap, reset-controller, and common clock framework APIs. Local QCOM dependencies are `common.h` for `qcom_cc_register_board_clk()` and `qcom_cc_probe()`, `clk-pll.h`, `clk-hfpll.h`, `clk-rcg.h`, `clk-branch.h`, `clk-regmap.h`, and `reset.h`. Binding constants come from `dt-bindings/clock/qcom,gcc-msm8960.h` and `dt-bindings/reset/qcom,gcc-msm8960.h`.

External integration depends on device tree names for the PXO/CXO references, although this driver creates fixed clock providers with those names during probe. Consumers bind by GCC clock/reset phandle IDs, and legacy thermal integration can either be represented as child DT nodes or as the fallback `qcom-tsens` platform device.

### Integration Points
Major consumers include GSBI serial blocks 1-12, QUP SPI/I2C engines, UARTs, SDC/eMMC/SD controllers, USB HS/FS/HSIC blocks, TSIF, PRNG, CE crypto, ADM/DMA, PMIC arbiter, RPM message RAM, and bus fabric reset clients. APQ8064 expands the same provider with USB HS3/HS4, SATA clocks and resets, PCIe clocks and resets, CE3, and additional HFPLLs.

The two SoC descriptors are the primary integration boundary. MSM8960 exposes a wider GSBI/SDC set, while APQ8064 exposes SATA/PCIe/extra USB/CE3 and different reset coverage. Binding ID alignment is therefore critical: each array entry is directly keyed by a binding constant, and an incorrect entry changes the resource returned to device-tree consumers.

### Risks
The largest risk is hardware table accuracy: register offsets, halt bits, reset bits, parent selector values, M/N widths, and frequency table parameters are hand-coded across a large legacy register map. A single bad table entry can affect only one peripheral and may be hard to diagnose from probe logs.

Variant handling needs care. APQ8064-specific `hfpll1` and `hfpll_l2` data pointers are changed after `qcom_cc_probe()` returns; this relies on later HFPLL ops using the mutable object pointer rather than any data copied during registration. MSM8960 and APQ8064 also share many static clock objects while using different exported arrays, so changes to a shared descriptor can affect both variants.

The fallback TSENS platform-device creation is another integration risk: systems with child DT nodes use managed population instead, while systems without children get a synthetic device. Error handling after successful GCC registration can still fail probe if TSENS registration fails, leaving common-clock registration side effects to normal driver-core handling.

### Test Signals
Useful build signals are clean compilation with both binding headers and no array-index warnings. Boot signals include successful probe for both `qcom,gcc-msm8960` and `qcom,gcc-apq8064`, visible GCC clock and reset providers, successful fixed-clock registration for `cxo_board` and `pxo_board`, and correct TSENS behavior on DTs with and without child nodes.

Runtime tests should exercise representative consumers: GSBI UART baud rates, QUP SPI/I2C rates, SDCC rate switching including low initialization rates and high data rates, USB HS/FS/HSIC operation, PRNG and CE crypto clocks, PMIC/RPM support clocks, and reset-controller operations for peripheral BCRs. APQ8064-specific validation should cover SATA, PCIe, USB HS3/HS4, CE3, and HFPLL-backed CPU/L2 rate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8974.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8974.c

### Purpose
`gcc-msm8974.c` implements the Qualcomm Global Clock Controller for MSM8974-family SoCs and includes MSM8226 compatibility handling plus MSM8974 Pro/Pro-AC clock extensions. It exposes GPLLs, RCG2 roots, branch clocks, resets, and one USB HS/HSIC GDSC for NoC, BLSP/QUP/UART, crypto, SDCC, USB, TSIF, PDM, MSS/LPASS/MMSS support, and assorted system infrastructure.

### Important APIs, Types, And Functions
The PLL layer uses `struct clk_pll` and `clk_pll_ops` for `gpll0`, `gpll1`, and optional `gpll4`, with vote wrappers `gpll0_vote`, `gpll1_vote`, and optional `gpll4_vote` using `clk_pll_vote_ops`. Parent maps describe XO, GPLL0, GPLL1, and GPLL4 hardware selector values. Programmable roots are `struct clk_rcg2` objects using `clk_rcg2_ops` or `clk_rcg2_floor_ops`, with `freq_tbl` tables for USB3, BLSP I2C/SPI/UART, CE1/CE2, GP clocks, PDM2, SDCC, TSIF, USB HS, and HSIC paths.

Consumer gates are `struct clk_branch` objects using `clk_branch2_ops`, with many `CLK_SET_RATE_PARENT` flags on peripheral app clocks. Some AHB/AXI/system branches use `BRANCH_HALT_VOTED` because their enable bits are vote-controlled through shared registers at `0x1484`. `gcc_mmss_gpll0_clk_src` is a simple regmap branch-style vote exported as `mmss_gpll0_vote`. `usb_hs_hsic_gdsc` is a `struct gdsc` power domain at GDSCR offset `0x404` with `PWRSTS_OFF_ON`.

There are three descriptor/resource sets in the file: `gcc_msm8226_clocks`/`gcc_msm8226_resets`/`gcc_msm8226_gdscs`/`gcc_msm8226_desc`, and `gcc_msm8974_clocks`/`gcc_msm8974_resets`/`gcc_msm8974_gdscs`/`gcc_msm8974_desc`. Variant mutators `msm8226_clock_override()` and `msm8974_pro_clock_override()` modify static frequency tables, SDCC1 parent data, and optional GPLL4/CDCCAL clock array entries before registration. `gcc_msm8974_probe()` registers XO and sleep clocks, applies variant overrides, then calls the common probe path.

### Control Flow
The driver is registered at `core_initcall()` and matches `qcom,gcc-msm8226`, `qcom,gcc-msm8974`, `qcom,gcc-msm8974pro`, and `qcom,gcc-msm8974pro-ac`. Probe reads `device_get_match_data()`, and for any compatible other than the base `qcom,gcc-msm8974` it applies a variant override: MSM8226 swaps CE1 and GP clock frequency tables to reduced MSM8226 tables; Pro/Pro-AC enables SDCC1 GPLL4 parent/rates and fills previously NULL GPLL4 and SDCC1 CDCCAL entries in `gcc_msm8974_clocks`.

After override, probe registers a fixed `xo_board` provider at 19.2 MHz and registers the shared sleep clock provider via `qcom_cc_register_sleep_clk()`. It then calls `qcom_cc_probe(pdev, &gcc_msm8974_desc)`, which maps registers, registers clocks, resets, and the USB HS/HSIC GDSC from the descriptor, and exposes clock/reset/power-domain providers to device-tree consumers.

Runtime control is data-driven through common clock ops. RCG2 roots select XO/GPLL parents and program HID/MND fields from frequency tables; branch clocks set enable bits and poll halt status; reset consumers use `gcc_msm8974_resets`; genpd consumers control the USB HS/HSIC domain through the GDSC helper.

### State And Persistence Behavior
There is no persistent storage. Hardware-visible state lives in GCC registers: PLL mode/config/status, PLL vote bits, command RCGR settings, branch enable bits, reset bits, sleep-clock branches, and GDSC power state. Static C state is mostly descriptor data, but the variant override functions mutate global descriptors before registration: CE1/GP frequency table pointers for MSM8226, SDCC1 init parent metadata and frequency table for Pro variants, and optional entries in `gcc_msm8974_clocks`.

Because the static objects are global, the selected variant should be treated as boot-time one-shot state. The file assumes one compatible instance and does not restore mutated descriptor data on remove. Sleep-clock parent references are resolved through the provider registered in probe, and GDSC state persists until changed by genpd or reset.

### Dependencies
Dependencies include Linux platform-driver, OF match, module, regmap, reset-controller, common clock framework, QCOM common CC helpers, PLL/RCG/branch helpers, reset support, and GDSC support. Binding IDs come from `dt-bindings/clock/qcom,gcc-msm8974.h` and `dt-bindings/reset/qcom,gcc-msm8974.h`.

The driver integrates with board/root clocks through `qcom_cc_register_board_clk(dev, "xo_board", "xo", 19200000)` and `qcom_cc_register_sleep_clk(dev)`. It relies on QCOM common CC code to wire the `qcom_cc_desc` arrays into the kernel clock, reset, and genpd frameworks.

### Integration Points
Clock consumers include BLSP1/BLSP2 QUP I2C/SPI and UART ports, CE1/CE2 crypto, GP clocks, SDCC1-4, USB2 PHY sleep clocks, USB3 master/mock/sleep clocks, USB HS and HSIC clocks, TSIF, PDM, PRNG, BAM DMA, boot ROM, NoC/system fabric, MMSS/OCMEM/MSS/LPASS support clocks, and MMSS GPLL0 vote users. Reset consumers include NoC, USB, SDCC, BLSP, PDM, BAM, TSIF, TCSR, boot ROM, message RAM, TLMM, MPM, security, SPMI, SPDM, CE, BIMC, bus timeout, DEHR/RBCPR, and subsystem restart lines.

The `USB_HS_HSIC_GDSC` power domain is exported for USB HS/HSIC consumers. Pro variants add GPLL4 and SDCC1 calibration/sleep clocks to support higher SDCC1 rates. MSM8226 has a narrower hardware description in the file, but the current probe path still calls `qcom_cc_probe()` with `gcc_msm8974_desc` rather than the match-provided descriptor.

### Risks
The highest-risk area is variant handling. The match table includes `gcc_msm8226_desc`, but `gcc_msm8974_probe()` ignores `data` for the final common probe call and always passes `&gcc_msm8974_desc`. As written, MSM8226 gets reduced CE1/GP frequency tables but not the MSM8226 clock/reset/regmap descriptor during registration; that can expose unsupported MSM8974 resources or access beyond MSM8226's declared register range. This should be treated as a strong review/test signal before relying on MSM8226 behavior.

The Pro override mutates global SDCC1 init data and the shared `gcc_msm8974_clocks` array. That is appropriate for a single GCC instance, but it is not reversible and can affect any later probe in the same kernel if multiple compatibles were ever instantiated. Parent-map correctness is also critical for GPLL4 SDCC1 rates because the normal SDCC tables do not include GPLL4.

Other risks are the usual hand-authored GCC table hazards: wrong register offsets, selector values, halt policies, reset offsets, or frequency entries can break one peripheral while the provider still probes. Branches using voted enable registers and the simple MMSS GPLL0 vote require hardware-specific halt behavior to be correct. GDSC offset and power-state assumptions need USB runtime PM validation.

### Test Signals
Build tests should compile all four compatibles' binding IDs and array indexes cleanly. Boot tests should verify successful probe for base MSM8974, MSM8974 Pro/Pro-AC, and MSM8226, with `xo_board` and `sleep_clk` providers registered before GCC clocks resolve.

Runtime signals include clk-summary visibility for expected IDs, BLSP I2C/SPI/UART transfers at listed rates, CE crypto operation at each available rate, SDCC1-4 card/eMMC rate changes, USB2/USB3/HSIC enumeration and suspend/resume, TSIF/PDM/PRNG consumers, reset assertion/deassertion for representative BCRs, MMSS GPLL0 vote behavior, and GDSC on/off transitions for `usb_hs_hsic`. MSM8226 validation should specifically check that only valid MSM8226 resources are exposed and that no register access reaches resources absent from that SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8974.c -->
