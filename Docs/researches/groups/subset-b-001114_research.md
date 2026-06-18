# Research: subset-b-001114

## sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8250.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8250.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8250.c

## Purpose

`camcc-sm8250.c` is the Qualcomm camera clock controller driver for SM8250. It describes the CAMCC register layout, PLLs, root clock generators, branch clocks, resets, and GDSC power domains used by camera hardware blocks such as BPS, IPE, IFE, SBI, ICP, JPEG, CSI PHY timers, CSIPHY lanes, CCI, CAMNOC, and sensor MCLK outputs. The file is mostly declarative data consumed by the common Qualcomm clock controller framework; its only runtime control flow is platform probe, PLL programming, and registration.

## Important APIs, Types, and Functions

- `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, and `struct alpha_pll_config` define five CAMCC PLLs and their post-dividers. PLL0, PLL1, PLL3, and PLL4 use Lucid PLL ops; PLL2 uses Zonda PLL ops.
- `struct clk_rcg2` plus `struct freq_tbl` define programmable root clock generators. Important roots include BPS, CAMNOC AXI, CCI, CPHY RX, CSI PHY timer, fast/slow AHB, FD core, ICP, IFE, IFE CSID, IFE Lite, IPE, JPEG, MCLK, SBI CSID, sleep, and XO sources.
- `struct clk_regmap_div cam_cc_sbi_div_clk_src` exposes a read-only SBI divider sourced from `cam_cc_ife_0_clk_src`.
- `struct clk_branch` entries define gateable branch clocks using `clk_branch2_ops` and CBCR halt polling.
- `struct gdsc` entries model power domains: `bps_gdsc`, `ipe_0_gdsc`, `sbi_gdsc`, `ife_0_gdsc`, `ife_1_gdsc`, and parent `titan_top_gdsc`.
- `struct qcom_reset_map cam_cc_sm8250_resets[]` maps BCR reset IDs to register offsets.
- `struct qcom_cc_desc cam_cc_sm8250_desc` is the central descriptor passed to the Qualcomm CC framework.
- `cam_cc_sm8250_probe()` maps CAMCC registers, programs PLLs with `clk_lucid_pll_configure()` and `clk_zonda_pll_configure()`, then calls `qcom_cc_really_probe()`.
- `module_platform_driver(cam_cc_sm8250_driver)` registers the platform driver for `qcom,sm8250-camcc`.

## Control Flow

Device-tree matching selects the driver through `qcom,sm8250-camcc`. Probe calls `qcom_cc_map()` with `cam_cc_sm8250_desc`, giving the common framework the regmap configuration and the clock/reset/GDSC tables. If mapping fails, probe returns the error pointer value.

After mapping succeeds, probe explicitly configures all five PLLs before registration: PLL0, PLL1, PLL3, and PLL4 with Lucid configuration values, and PLL2 with Zonda configuration values. Finally `qcom_cc_really_probe()` registers the clocks, resets, and GDSCs with the clock, reset, and power-domain frameworks. Runtime clock enable, disable, rate selection, parent switching, reset assertion, and power-domain sequencing are delegated to the common qcom clock, reset, and GDSC implementations referenced by each table entry.

## State and Persistence

There is no filesystem or persistent software state. Hardware state is stored in CAMCC registers behind the MMIO regmap. Static C objects hold clock topology, register offsets, frequency tables, parent maps, and GDSC metadata for the life of the module. PLL configuration writes happen once at probe unless later framework operations change rates. Branch clocks maintain enable state in CBCR registers, RCGs maintain command/source/divider state in RCGR registers, resets use BCR registers, and GDSCs use GDSCR registers. `cam_cc_gdsc_clk` is marked `CLK_IS_CRITICAL`, keeping the GDSC support clock from being disabled by normal unused-clock cleanup.

## Dependencies and Integration Points

The driver depends on Linux CCF, platform-device probing, regmap, module infrastructure, and Qualcomm clock framework helpers from `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `clk-regmap-divider.h`, `common.h`, `gdsc.h`, and `reset.h`. Its numeric IDs come from `dt-bindings/clock/qcom,camcc-sm8250.h`; consumers in device tree request those IDs through phandles to CAMCC. External parent clocks are named by firmware strings `bi_tcxo` and `sleep_clk`. Integration with camera clients occurs indirectly through CCF clock lookup, reset-controller lookup, and genpd power-domain attachment.

## Risks and Edge Cases

The file is sensitive to hardware register accuracy. Incorrect offsets, parent-map selector values, M/N/D parameters, or halt-check modes can cause camera blocks to hang, underclock, overclock, or fail to power up. `clk_rcg2_shared_ops` is used for many shared roots, while some roots use `clk_rcg2_ops`; changing those ops can affect concurrent users. GDSC parent topology is important because child domains point at `titan_top_gdsc`; wrong ordering can break power sequencing. The read-only SBI divider assumes firmware or hardware owns that divider value. Because PLLs are configured explicitly before registration, bad PLL constants or VCO ranges can destabilize all dependent camera clocks.

## Test Signals

Useful signals are kernel probe logs for `cam_cc-sm8250`, absence of deferred probe from missing `bi_tcxo` or `sleep_clk`, successful clock registration under debugfs, and camera pipeline tests that exercise sensors, CSI PHY timers, CCI, IFE, IPE, BPS, JPEG, and SBI paths. Runtime validation should include `clk_summary` rate/enable checks, reset-controller users asserting/deasserting CAMCC BCRs, genpd transitions for all CAMCC GDSCs, suspend/resume with unused-clock cleanup, and high-load camera capture to expose wrong halt checks or parent-rate plans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8250.c -->

## sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8450.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8450.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8450.c

## Purpose

`camcc-sm8450.c` implements the Qualcomm CAMCC driver for SM8450 and SM8475. It provides the camera clock, reset, PLL, and GDSC description for the Titan camera subsystem, including BPS, IPE NPS/PPS, IFE0/1/2, IFE Lite, SFE0/1, SBI, ICP, JPEG, CAMNOC, CSI/CSIPHY, CCI, QDSS debug, sensor MCLK, sleep, and XO-related clocks. Compared with SM8250, it has more PLLs, more camera processing blocks, RPM integration, critical CBCR registration, and variant-specific SM8475 PLL mutation in probe.

## Important APIs, Types, and Functions

- The DT parent enum (`DT_IFACE`, `DT_BI_TCXO`, `DT_BI_TCXO_AO`, `DT_SLEEP_CLK`) and `clk_parent_data` entries use indexed DT clocks rather than only firmware names.
- Nine `struct clk_alpha_pll` instances cover PLL0 through PLL8. Most are Lucid Evo on SM8450; SM8475 probe rewrites several to Lucid OLE register layouts/configuration and changes PLL2 to a Rivian OLE VCO table/config.
- `sm8475_cam_cc_pll*_config` and `sm8475_cam_cc_pll*_out_even/_odd_init` hold the variant overrides used only when compatible is `qcom,sm8475-camcc`.
- `struct clk_rcg2` entries define rate plans for BPS, CAMNOC, CCI, CPHY RX, CSI timers, CSID, AHB roots, ICP, IFEs, IFE Lite, IPE NPS, JPEG, MCLK0-7, QDSS debug, SFE0/1, sleep, slow AHB, and XO.
- `struct clk_branch` entries expose the gated outputs consumed by camera blocks, CPAS votes, debug clocks, and sensor paths.
- `cam_cc_sm8450_plls[]` and `cam_cc_sm8450_critical_cbcrs[]` feed `struct qcom_cc_driver_data`, allowing `qcom_cc_probe()` to initialize alpha PLLs and keep the GDSC CBCR critical.
- `cam_cc_sm8450_resets[]`, `cam_cc_sm8450_gdscs[]`, and `cam_cc_sm8450_desc` provide reset, genpd, and common CC registration data.
- `cam_cc_sm8450_probe()` applies SM8475 overrides if needed and then calls `qcom_cc_probe()`.

## Control Flow

The platform driver matches either `qcom,sm8450-camcc` or `qcom,sm8475-camcc`. On SM8450, probe immediately delegates to `qcom_cc_probe()` with `cam_cc_sm8450_desc`; the common framework maps registers, initializes PLLs listed in driver data, registers clocks, resets, critical CBCRs, and GDSCs, and enables RPM-aware handling because `.use_rpm = true`.

On SM8475, probe first mutates static PLL objects in place. PLL0/1/3/4/5/6/7/8 and their post-dividers switch from Lucid Evo register tables and ops init data to Lucid OLE-compatible register tables/init data. PLL2 changes VCO table, and all PLL config pointers are redirected to SM8475-specific `alpha_pll_config` structures. After these mutations, the same descriptor and clock arrays are registered through `qcom_cc_probe()`.

## State and Persistence

The driver has no persistent storage. Hardware state resides in CAMCC registers described by `cam_cc_sm8450_regmap_config` up to `0x1601c`. Static object state is significant because SM8475 support mutates global PLL and post-divider objects during probe; this is safe for a single SoC instance but means the object graph is no longer purely constant after variant detection. PLL, RCG, branch, reset, and GDSC state persists only in hardware registers until reset or power loss. `qcom_cc_driver_data` marks a GDSC support CBCR critical so framework cleanup does not gate it unexpectedly.

## Dependencies and Integration Points

The driver depends on Linux CCF, reset-controller and genpd integration, regmap, OF matching, and Qualcomm CC helpers from `clk-alpha-pll.h`, `clk-branch.h`, `clk-pll.h`, `clk-rcg.h`, `clk-regmap-divider.h`, `clk-regmap-mux.h`, `clk-regmap.h`, `common.h`, `gdsc.h`, and `reset.h`. Its binding IDs come from `dt-bindings/clock/qcom,sm8450-camcc.h`. DT supplies indexed parents, including normal TCXO, always-on TCXO, and sleep clock. Camera, media, sensor, interconnect/CPAS, and debug consumers integrate through clock IDs, reset IDs, and GDSC IDs in the binding.

## Risks and Edge Cases

Variant handling is the main code risk. SM8475 support mutates shared static structures based on `of_device_is_compatible()`, so any future multi-instance or mixed-compatible scenario would be unsafe. Missing a PLL override, post-divider init override, or config pointer update can silently program SM8475 PLLs with SM8450 values. Register offsets and parent selector values are dense and hardware-specific; mistakes affect only particular camera blocks and can appear as camera stream failures rather than probe failures. `.use_rpm = true` and critical CBCR handling must align with firmware power management; wrong critical clocks can either waste power or break GDSC transitions.

## Test Signals

Probe should succeed for both `qcom,sm8450-camcc` and `qcom,sm8475-camcc`, with clock debugfs showing PLL0-8, MCLK0-7, IFE0/1/2, SFE0/1, IPE NPS/PPS, CPAS, CSI, CSIPHY, and QDSS debug clocks. Variant testing should compare PLL register programming on SM8475 against expected Lucid OLE/Rivian OLE settings. Functional tests should cover camera capture across all sensors and CSI lanes, SFE and IFE paths, JPEG and BPS/IPE processing, genpd on/off transitions for all GDSCs, reset toggles for all BCRs, suspend/resume, and unused-clock cleanup with the critical GDSC CBCR still active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8450.c -->

## sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8550.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8550.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8550.c

## Purpose

`camcc-sm8550.c` is the Qualcomm camera clock controller driver for SM8550. It describes a larger CAMCC topology with thirteen PLLs, many RCGs, camera block branch clocks, resets, critical CBCRs, and GDSC power domains. It supports BPS, IFE0/1/2, IFE Lite, IPE, SBI, SFE0/1, CRE, ICP, JPEG and JPEG_1, CPAS paths, CCI0/1/2, CSI0-7 timers and CSIPHY0-7, driver/XO clocks, QDSS debug, sensor MCLK0-7, CAMNOC, sleep, slow AHB, and XO sources.

## Important APIs, Types, and Functions

- DT parent enums include indexed `DT_BI_TCXO`, `DT_BI_TCXO_AO`, and `DT_SLEEP_CLK`; parent maps also expose `P_BI_TCXO_AO`.
- Thirteen `struct clk_alpha_pll` instances define PLL0 through PLL12. Lucid OLE VCO/config is used for most PLLs, while PLL2 uses a Rivian OLE VCO and Rivian Evo ops/register layout. Post-dividers exist for PLL0/1/3/4/5/6/7/8/9/10/11/12, with PLL0 also exposing an odd divider.
- `struct clk_rcg2` roots define rate plans for all major camera domains, including newer CRE, IFE DSP roots, expanded CSI/CSIPHY timers, and JPEG-specific rates.
- `struct clk_branch` entries expose gates and halt checks for block clocks, CPAS proxy clocks, fast AHB clocks, driver clocks, QDSS debug clocks, and sensor clocks.
- `struct gdsc` entries use SM8550-specific names (`cam_cc_*_gdsc`) and include wait values plus `RETAIN_FF_ENABLE` on all domains.
- `cam_cc_sm8550_plls[]` and `cam_cc_sm8550_critical_cbcrs[]` populate `struct qcom_cc_driver_data` for framework-managed PLL initialization and critical CBCR handling.
- `cam_cc_sm8550_desc` enables `.use_rpm = true` and supplies clock, reset, GDSC, regmap, and driver-data tables.
- `cam_cc_sm8550_probe()` is intentionally thin and calls `qcom_cc_probe()` directly.

## Control Flow

OF matching binds the platform driver to `qcom,sm8550-camcc`. Probe immediately calls `qcom_cc_probe(pdev, &cam_cc_sm8550_desc)`. The common Qualcomm CC code maps CAMCC MMIO according to `cam_cc_sm8550_regmap_config`, initializes alpha PLLs from `cam_cc_sm8550_plls[]`, registers all clocks in `cam_cc_sm8550_clocks[]`, registers reset lines from `cam_cc_sm8550_resets[]`, registers GDSCs from `cam_cc_sm8550_gdscs[]`, and applies critical CBCR handling for the GDSC and sleep clocks. All later runtime behavior is performed by common CCF, reset, and GDSC callbacks referenced by the static table entries.

## State and Persistence

There is no disk-backed state. CAMCC hardware register state is addressed through a 32-bit, stride-4, fast-IO regmap with maximum register `0x16320`. Static tables describe topology for the module lifetime and are not variant-mutated in this file. PLL programming, RCG source/divider selection, branch gate state, reset state, and GDSC state are retained only in hardware while powered. GDSCs include explicit enable/rest/few and clock-disable wait values plus `RETAIN_FF_ENABLE`, indicating power-collapse sequencing must preserve flip-flop retention behavior.

## Dependencies and Integration Points

The file depends on Linux platform-device, OF match, regmap, CCF, reset-controller, genpd, and Qualcomm clock helpers from `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `clk-regmap.h`, `common.h`, `gdsc.h`, and `reset.h`. Binding constants come from `dt-bindings/clock/qcom,sm8550-camcc.h`. Camera and media drivers consume its exported clocks, resets, and power domains through DT phandles. RPM integration is enabled, so firmware/resource-power-management behavior is part of the integration contract. Always-on TCXO is used for XO-derived roots such as `cam_cc_xo_clk_src`.

## Risks and Edge Cases

The driver is almost entirely hardware data, so correctness depends on exact register offsets, parent selectors, frequency tables, PLL constants, and GDSC wait/retention settings. Expanded topology raises mapping risk: CCI2, CSI/CSIPHY6-7, CRE, DRV clocks, JPEG_1, IFE DSP roots, and additional PLLs must all align with the binding IDs. Critical CBCRs include both GDSC and sleep clocks; incorrect critical handling can affect suspend, idle power, or camera power-up. Because `qcom_cc_probe()` initializes PLLs via driver data, missing a PLL from `cam_cc_sm8550_plls[]` would leave dependent roots unusable even though their clock entries register.

## Test Signals

Probe should create clocks for all SM8550 binding IDs and expose PLL0-12, MCLK0-7, CSI0-7, CSIPHY0-7, CCI0-2, CRE, IFE DSP, SFE, JPEG/JPEG_1, CPAS, and QDSS debug entries in clock debugfs. Hardware validation should exercise multi-sensor capture across all CSI lanes, IFE/SFE/BPS/IPE processing, JPEG paths, CRE users, reset operations for all BCRs, GDSC on/off transitions with retention enabled, RPM-aware suspend/resume, and unused-clock cleanup while critical GDSC/sleep CBCRs remain enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8550.c -->
