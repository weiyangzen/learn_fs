# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc8280xp.c

## Purpose

`camcc-sc8280xp.c` is the Qualcomm CAMCC driver for SC8280XP camera hardware. It registers the camera clock tree, reset controls, and GDSC power domains, and it adds explicit runtime-PM handling around register access during probe.

The file is a static hardware description plus a small but important probe sequence. It programs eight camera PLLs, enables a critical GDSC branch clock, registers clocks/resets/GDSCs with shared Qualcomm code, and carefully unwinds runtime PM and the critical branch on failure.

## Important APIs, Types, and Data

- External interfaces: platform driver name `camcc-sc8280xp`, OF compatible `qcom,sc8280xp-camcc`, and DT IDs from `<dt-bindings/clock/qcom,sc8280xp-camcc.h>`.
- Runtime PM APIs: `devm_pm_runtime_enable()`, `pm_runtime_resume_and_get()`, `pm_runtime_put()`, and `pm_runtime_put_sync()`.
- Qualcomm helper APIs: `qcom_cc_map()`, `qcom_cc_really_probe()`, `qcom_branch_set_clk_en()`, `clk_lucid_pll_configure()`, `clk_zonda_pll_configure()`, and `regmap_update_bits()`.
- DT parent indexes: `DT_IFACE`, `DT_BI_TCXO`, `DT_BI_TCXO_AO`, and `DT_SLEEP_CLK`.
- PLL inventory: eight PLLs, `camcc_pll0` through `camcc_pll7`. PLL0/1/3/4/5/6/7 use Lucid 5LPE/Lucid post-divider style operations with the Lucid VCO range; PLL2 is Zonda-based. Post-divider outputs expose even and odd variants where used by downstream roots.
- RCG inventory: programmable roots cover BPS, CAMNOC AXI, four CCI roots, CPHY RX, four CSI PHY timers, FAST/SLOW AHB, ICP, IFE0-3 roots and CSID roots, IFE Lite0-3 roots and CSID roots, IPE0, JPEG, LRME, MCLK0-7, sleep, and XO.
- Branch inventory: branch gates cover AHB/AXI/AREG and functional clocks for BPS, CAMNOC, CCI, CPAS, CSI PHYs, ICP, IFEs, IFE Lites, IPE0/1, JPEG, LRME, MCLK0-7, and sleep. Most branches use `BRANCH_HALT`; CPAS AHB uses `BRANCH_HALT_DELAY`.
- Power domains: eight GDSCs are exported: BPS, IFE0-3, IPE0-1, and Titan top. BPS and IPE0/1 use `HW_CTRL | RETAIN_FF_ENABLE`; the IFE domains and Titan top retain state without HW_CTRL. Child domains are parented to Titan top.
- Reset controls: `camcc_sc8280xp_resets[]` exposes BCRs for BPS, CAMNOC, CCI, CPAS, CSI0-3 PHYs, ICP, IFE0-3, IFE Lite0-3, IPE0-1, JPEG, and LRME.
- Descriptor details: `camcc_sc8280xp_desc` registers clocks, resets, and GDSCs. The regmap uses 32-bit registers, stride 4, `max_register = 0x13020`, and `fast_io = true`.

## Control Flow

1. The platform bus matches `qcom,sc8280xp-camcc` and calls `camcc_sc8280xp_probe()`.
2. Probe enables runtime PM for the device and resumes it with `pm_runtime_resume_and_get()` so CAMCC registers are accessible.
3. `qcom_cc_map()` maps the register block. On failure, probe drops the runtime-PM reference with `pm_runtime_put_sync()`.
4. Probe programs PLL0, PLL1, PLL3, PLL4, PLL5, PLL6, and PLL7 with Lucid configuration and PLL2 with Zonda configuration.
5. Probe calls `qcom_branch_set_clk_en(regmap, 0xc1e4)` to keep `CAMCC_GDSC_CLK` enabled.
6. `qcom_cc_really_probe()` registers the descriptor. On registration failure, the error path clears bit 0 at `0xc1e4`, drops the runtime-PM reference synchronously, and returns the error.
7. On success, probe drops its runtime-PM reference with `pm_runtime_put()` and leaves framework-managed clocks, resets, and GDSCs available to consumers.

## State and Persistence

There is no persistent storage. Static C structures encode topology and register offsets. Probe mutates hardware state by configuring PLL registers and enabling the critical GDSC branch. Later state changes are driven by common clock, reset-controller, genpd, and runtime-PM users. Runtime PM state is transient and reference-counted by the PM core; the explicit probe reference only protects registration-time MMIO access.

## Dependencies and Integration Points

- Requires a DT node with compatible `qcom,sc8280xp-camcc`, a valid MMIO resource, and parent clocks matching the DT parent indexes.
- Depends on runtime-PM infrastructure being able to resume the CAMCC device before MMIO access.
- Integrates with Qualcomm shared clock code in the same qcom clock subsystem and with Linux common clock, reset-controller, genpd, platform-driver, regmap, and PM-runtime frameworks.
- Camera consumers can use the exported clocks for BPS, CAMNOC, CCI, CSI PHY timers, IFEs, IFE Lite, IPE, JPEG, LRME, MCLK, sleep, slow AHB, and XO paths.
- GDSC exports provide power domains for Titan top and camera processing blocks; reset exports let consumers reset major camera engines.

## Risks and Review Notes

- Runtime-PM sequencing is a central risk. Any early return after `pm_runtime_resume_and_get()` must drop the PM reference; this file does so through `err_put_rpm`.
- The critical `CAMCC_GDSC_CLK` enable at raw offset `0xc1e4` must match the hardware. The failure path clears the bit only after a failed `qcom_cc_really_probe()`, so incorrect offset handling can affect power or registration stability.
- The regmap `max_register` is larger than in SC7280/SC8180X. Adding clocks above `0x13020` would require updating this bound.
- PLL and frequency-table constants are opaque hardware programming values. Small mistakes can break a subset of camera rates without compile-time errors.
- Reset coverage differs from SC8180X: this file does not expose FD or MCLK reset entries. Consumers must follow the SC8280XP binding, not a sibling SoC assumption.
- GDSC flags mix HW-controlled and software-controlled domains. Wrong flags can cause hangs, unexpected power retention, or inability to collapse a block.

## Test Signals

- Build with SC8280XP CAMCC enabled and ensure all DT binding indexes resolve.
- Probe test: boot on SC8280XP hardware or an equivalent integration environment and confirm runtime PM resume, regmap mapping, PLL configuration, and `qcom_cc_really_probe()` succeed.
- Error-path review or fault injection: force regmap/probe failure and verify runtime-PM references are released and the `CAMCC_GDSC_CLK` bit is cleared after registration failure.
- Clock debug: inspect debugfs for CAMCC PLLs, MCLK0-7, IFE/IFE Lite roots, sleep clock, and the critical GDSC branch.
- Camera workload tests: exercise sensor streaming, multi-IFE paths, IPE/JPEG/LRME use, reset sequencing, and suspend/resume to validate runtime-PM and GDSC interactions.
