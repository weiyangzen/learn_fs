# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc7180.c

## Purpose
Implements the Qualcomm/QTI Global Clock Controller driver for SC7180. It registers Fabia GPLLs, RCG rate sources, fixed factor hardware, branch gates, resets, and GDSCs for core SoC peripherals including QUPv3, SDCC1/2, UFS PHY, USB3, QSPI, PDM, crypto, CPU/system NoC, camera/display/video, GPU, NPU, modem, and LPASS-related clocks.

## Important APIs, Types, And Functions
- `struct clk_alpha_pll` defines Fabia GPLL0, GPLL1, GPLL4, GPLL6, and GPLL7, with `gpll0_out_even` as a Fabia post-divider.
- `struct clk_fixed_factor gcc_pll0_main_div_cdiv` provides a CCF-visible divide-by-two hardware clock, exported through `gcc_sc7180_hws` as `GCC_GPLL0_MAIN_DIV_CDIV`.
- Parent maps and parent-data arrays use firmware clock names such as `bi_tcxo`, `bi_tcxo_ao`, and `sleep_clk`, plus internal PLL hardware pointers, to construct RCG parent selections.
- `struct clk_rcg2` and frequency tables cover CPUSS AHB, GP1-3, PDM2, QSPI, QUPv3 wrap0/wrap1 serial ports, SDCC1/2, UFS PHY, USB30, USB3 PHY auxiliary, and secure controller rates.
- `struct clk_branch` gates leaf and vote clocks across UFS, USB, boot ROM, camera/display/video, crypto, CPUSS, GPU, NPU, QSPI, QUPv3, SDCC, MSS, and LPASS. Some CPU/system NoC branches are marked `CLK_IS_CRITICAL`.
- `struct gdsc` exposes UFS PHY, USB30 primary, and two votable MMNOC MMU TBU domains.
- `gcc_sc7180_probe()` maps the controller, disables GPLL0 active input to MM/NPU/GPU blocks through three MISC register updates, enables required always-on clocks, registers DFS data, and calls `qcom_cc_really_probe()`.

## Control Flow
The platform driver binds to `qcom,gcc-sc7180` and is registered via `core_initcall(gcc_sc7180_init)`. Probe maps GCC registers using the descriptor's regmap config (`max_register = 0x18208c`). Before common registration, it writes MISC bits at `0x09ffc`, `0x4d110`, and `0x71028` with mask/value `0x3` to disable the GPLL0 active input path for multimedia blocks, NPU, and GPU. It then forces several branches on: CPUSS GNOC, video/camera/display AHB and XO clocks, and GPU CFG AHB. The QUPv3 wrap0/wrap1 serial RCGs are registered for DFS, and the shared qcom CC registration publishes the descriptor's clocks, hardware-only clock, resets, and GDSCs.

Normal consumer operations are handled by the common clock framework. Rate requests select frequency-table entries, parent muxes choose PLL or XO/sleep parents, branches gate hardware and poll or skip halt status according to their definitions, reset IDs assert/deassert BCR registers, and GDSC users vote power domains through genpd.

## State And Persistence
The driver is declarative except for probe-time register programming. Hardware register state stores PLL enables at `0x52010`, RCG configuration, branch enables, reset assertions, and GDSC power votes. Probe-time MISC writes and always-on branch enables persist until hardware reset or later firmware/kernel changes. Critical flags on CPUSS/system NoC clocks prevent the common clock framework from disabling paths needed for CPU/interconnect operation. The `gcc_sc7180_hws` table separately persists the fixed-factor GPLL0 main divider registration in addition to the regmap clocks.

## Dependencies And Integration Points
Depends on Linux CCF, error/kernel/module/platform/OF/regmap support, qcom alpha PLL, branch, RCG, common CC, reset, and GDSC helpers, plus `dt-bindings/clock/qcom,gcc-sc7180.h`. It integrates with SC7180 device-tree clock consumers for serial engines, storage, USB, QSPI, crypto, CPU/interconnect, GPU/NPU, camera/display/video, modem, and LPASS. Unlike the newer SA8775P/SAR2130P drivers, this source uses firmware-name parent lookup rather than numeric DT parent indexes for external TCXO/sleep clocks.

## Risks And Edge Cases
The probe-time GPLL0 active-input disable writes are undocumented-looking SoC quirks; removing or altering them can destabilize MM/NPU/GPU clocking. `CLK_IS_CRITICAL` on CPUSS and system NoC clocks is essential to avoid disabling CPU/interconnect paths. Parent lookup relies on firmware clock names, so DT clock-names mismatches break parent resolution. Several UFS/USB symbol or pipe branches use skipped halt checks where hardware status may not reflect external PHY-driven clocks. Binding-array index consistency remains critical because public consumers address clocks, resets, and GDSCs by generated IDs. The separate `clk_hws` table for the fixed factor divider must remain in sync with the binding ID.

## Test Signals
Useful runtime signals are successful probe, presence of `GCC_GPLL0_MAIN_DIV_CDIV` and all public regmap clocks, stable boot without CPUSS/GNOC clock disable warnings, working QUPv3 DFS serial rates, SDCC1/2 and UFS storage operation, USB3 enumeration, QSPI/PDM/crypto availability, GPU/NPU/display/video clients enabling clocks without halt timeouts, and suspend/resume with GDSC votes intact. Static signals include binding ID alignment, build coverage for the SC7180 GCC driver, and review of probe writes against downstream or hardware documentation.
