# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-kaanapali.c

## Purpose
This file is the Qualcomm GPU Clock Controller provider for the Kaanapali platform. It publishes the GPUCC PLL, GMU and hub RCGs, branch clocks, reset controls, and CX GDSC needed by the platform GPU and GMU stack.

## Important APIs, Types, And Functions
The driver uses the same qcom CCF primitives as the Glymur GPUCC driver: `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, `qcom_cc_driver_data`, and `qcom_cc_desc`. `gpu_cc_pll0` is a Taycan EKO T alpha PLL configured for 950 MHz from `bi_tcxo`, with `cal_l = 0x48`; `gpu_cc_pll0_out_even` provides the divide-by-2 postdiv.

One parent map combines DT-provided XO/GPLL0 parents and internal PLL0 main/even/odd outputs. `gpu_cc_gmu_clk_src` supports XO plus 475, 575, 700, 725, and 750 MHz PLL-derived rates and has `hw_clk_ctrl = true`. `gpu_cc_hub_clk_src` supports 150, 200, 300, and 400 MHz and also has `hw_clk_ctrl = true`. `gpu_cc_hub_div_clk_src` is a read-only divider.

The branch set is smaller than Glymur: AHB, CX accu-shift, CX GMU, CXO, DEMET, DPM, frequency measurement, GPU SMMU vote, GX accu-shift, GX GMU, hub AON, hub CX internal, and MEMNOC GFX. `gpu_cc_cx_gdsc` uses GDSCR `0x9080`, hardware-control/status `0x9094`, OFF/ON states, `POLL_CFG_GDSCR`, and `RETAIN_FF_ENABLE`, with a shorter `clk_dis_wait_val` of `0x8`. The reset map covers CB, CX, fast hub, FF, GMU, GX, and XO BCRs. Critical CBCRs are `GPU_CC_CXO_AON_CLK`, `GPU_CC_RSCC_HUB_AON_CLK`, and `GPU_CC_RSCC_XO_AON_CLK`.

## Control Flow
The module platform driver matches `qcom,kaanapali-gpucc`, and probe simply calls `qcom_cc_probe()` with `gpu_cc_kaanapali_desc`. The common qcom path maps the register range, configures PLL0 using the driver-data alpha PLL list, enables/marks the critical CBCRs, registers the clock array by dt-binding IDs, exposes the reset controller entries, and registers the single CX GDSC.

At runtime, GPU and GMU drivers request rate changes on the GMU and hub roots, branch ops gate and ungate leaves according to halt semantics, the read-only divider reflects existing hub division, reset consumers toggle BCRs, and genpd controls the CX GDSC. The two RCGs with `hw_clk_ctrl = true` are prepared for hardware-assisted clock control while still exposing software rate selection through the common RCG ops.

## State And Persistence
Hardware state is stored in GPUCC registers up to `max_register = 0x95e8`: PLL0 configuration and status, postdivider state, RCG command/config registers, branch enable and halt bits, reset bits, critical CBCR state, and CX GDSC retain/power bits. Software state is static descriptor data plus qcom common clock registration state.

Critical AON/RSCC clocks and retain-FF on the CX GDSC are the main persistence mechanisms in this file. There is no file-local suspend/resume path, so GPU low-power behavior is coordinated by CCF, RPM-aware qcom common code (`use_rpm = true`), the GDSC core, and GPU/GMU firmware.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/qcom,kaanapali-gpucc.h`, a `qcom,kaanapali-gpucc` DT node, DT parent clock indexes for `bi_tcxo`, `gpll0_out_main`, and `gpll0_out_main_div`, and local qcom clock, reset, GDSC, and common registration helpers.

Consumers are the Kaanapali GPU/GMU driver stack, GPU SMMU, MEMNOC graphics path, DPM/frequency measurement logic, RSCC/AON infrastructure, and GPU reset/recovery paths. The descriptor bridges those consumers to CCF clock IDs, reset IDs, and a genpd CX power-domain ID.

## Risks And Test Signals
The key risks are SoC-specific table differences. Kaanapali uses a lower PLL0 configuration than Glymur, includes a 475 MHz GMU rate, omits Glymur's fast-frequency branches, uses `hw_clk_ctrl` on GMU and hub RCGs, and has a different CX GDSC clock-disable wait value. Copying Glymur values into this file would expose unsupported clocks or incorrect rates. Wrong critical CBCRs can break AON/RSCC behavior, and wrong GDSC flags can cause power-domain timeouts or context loss.

Useful test signals include clean probe, PLL0 configured near 950 MHz, `clk_summary` showing only Kaanapali binding IDs, GPU/GMU boot, successful GMU rate changes including 475 MHz, stable hub rates at 150/200/300/400 MHz, SMMU vote activity during GPU use, reset controls working during recovery, CX GDSC on/off transitions without warnings, and system suspend/resume with AON GPUCC clocks intact.
