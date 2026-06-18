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
