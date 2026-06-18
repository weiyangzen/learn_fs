# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-glymur.c

## Purpose
This file is the Qualcomm GPU Clock Controller provider for the Glymur platform. It publishes GPU-specific PLL, RCG, divider, branch, reset, and CX GDSC resources used by the GPU, GMU, hub, SMMU vote path, RSCC, and fast-frequency support.

## Important APIs, Types, And Functions
The driver uses `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct qcom_cc_driver_data`, and `struct qcom_cc_desc`. `gpu_cc_pll0` is a Taycan EKO T alpha PLL configured for 1150 MHz from `bi_tcxo`; `gpu_cc_pll0_out_even` exposes a divide-by-2 postdiv path. Parent maps cover DT-provided `bi_tcxo`, `gpll0_out_main`, `gpll0_out_main_div`, and internal PLL0 main/even/odd references.

The RCGs are `gpu_cc_ff_clk_src` fixed at 200 MHz from GPLL0, `gpu_cc_gmu_clk_src` with XO and high GPU PLL-derived rates from 575 to 750 MHz, and `gpu_cc_hub_clk_src` at 200/300/400 MHz. `gpu_cc_hub_div_clk_src` is a read-only divider below the hub root. Branches publish AHB, CX/GX accu-shift, CX fast-frequency, CX/GX GMU, CXO, DEMET, DPM, frequency measurement, GPU SMMU vote, GX ACD/AHB/RCG fast-frequency, hub AON, hub CX internal, MEMNOC GFX, RSCC hub AON, and sleep clocks.

`gpu_cc_cx_gdsc` describes the GPU CX power domain at GDSCR `0x9080`, with separate hardware-control status at `0x9094`, OFF/ON support, `POLL_CFG_GDSCR`, and `RETAIN_FF_ENABLE`. `gpu_cc_glymur_resets[]` provides CB, CX, fast hub, FF, GMU, GX, and XO resets. `gpu_cc_glymur_driver_data` asks common qcom code to configure the alpha PLL and mark critical CBCRs at `0x93a4`, `0x9008`, and `0x9004`.

## Control Flow
The module registers a normal platform driver matching `qcom,glymur-gpucc`. Probe is a thin wrapper around `qcom_cc_probe(pdev, &gpu_cc_glymur_desc)`. The common qcom path maps the GPUCC MMIO range, configures PLLs and critical CBCRs from driver data, registers CCF clocks, exposes resets, and registers the CX GDSC.

Runtime control is table-driven. GPU/GMU consumers set rates on the GMU and hub RCGs; branch ops gate leaves and poll or delay according to each halt mode; the read-only divider reflects hardware hub division; reset users toggle the GPUCC BCR offsets; and the GDSC framework controls the CX power domain with retain-FF handling.

## State And Persistence
Persistent state lives in GPUCC registers up to `max_register = 0x95e8`: PLL configuration/status, RCG command/config registers, divider state, branch enable/halt bits, reset bits, critical CBCR bits, and GDSC power/retention bits. The driver holds static descriptors only. `use_rpm = true` indicates the qcom common registration must integrate RPM-aware behavior for this controller.

Critical CBCRs and AON branch ops are persistence-sensitive because they keep low-level XO/RSCC/hub paths available while other GPU clocks are gated. The CX GDSC uses retain-FF to preserve flip-flop state across domain transitions. There is no explicit suspend/resume code in the file; runtime PM and sleep behavior depend on CCF, RPM integration, the GDSC core, GMU firmware, and hardware retention.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/qcom,glymur-gpucc.h`, the `qcom,glymur-gpucc` device-tree node, DT parent clock indexes for XO and GPLL0 inputs, and qcom helpers for alpha PLLs, branches, RCGs, regmap dividers, GDSCs, resets, and common provider registration.

Consumers include the Adreno GPU and GMU, GPU SMMU, MEMNOC/DDR fabric paths, RSCC, DPM/frequency measurement logic, and recovery/reset paths for CX/GX/GMU/fast-hub blocks. The descriptor exposes both clock IDs and reset IDs to those drivers.

## Risks And Test Signals
Risks center on GPU timing and shared ownership. A bad PLL0 configuration or GMU frequency table can destabilize the GMU. A wrong critical CBCR can break low-power entry or wake. A wrong voted halt mode can disable a path still needed by RPM, GMU, SMMU, or firmware. The CX GDSC flags and status register must match hardware or genpd can time out or lose retained state.

Useful test signals include clean probe with configured PLL0 rate, `clk_summary` entries for GMU/hub/FF branches, successful GPU driver attach and GMU boot, GPU frequency changes across listed GMU rates, SMMU vote clock behavior during GPU activity, reset controls working during GPU recovery, CX GDSC transitions without timeout warnings, and suspend/resume retaining critical GPUCC paths.
