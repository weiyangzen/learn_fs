# sources/distributed-fs/ceph-client/drivers/clk/qcom/nwgcc-nord.c

## Purpose
This platform driver registers the NORD NWGCC clock controller. It primarily supplies NoC-facing GPU, video, camera, display, EVA, DPRX, general-purpose, and measurement clocks, plus a small set of block resets.

## Important APIs, types, and functions
- Static PLL descriptors `nw_gcc_gpll0` and `nw_gcc_gpll0_out_even` provide GPLL0 and its even post-divider.
- `parent_map`/`clk_parent_data` tables define XO/GPLL parent choices for RCGs and branch-derived source clocks.
- `nw_gcc_gp1_clk_src` and `nw_gcc_gp2_clk_src` are programmable RCGs with common GP frequency tables.
- Numerous `clk_branch` descriptors expose vote/branch gates for camera, display, GPU, video, EVA, HSCNOC, and SMMU/TCU paths.
- `nw_gcc_nord_clocks[]`, `nw_gcc_nord_resets[]`, `nw_gcc_nord_critical_cbcrs[]`, and `nw_gcc_nord_desc` form the qcom CC registration payload.
- `nw_gcc_nord_probe()` calls `qcom_cc_probe()`.

## Control flow
The platform bus matches `"qcom,nord-nwgcc"` and calls probe. `qcom_cc_probe()` maps the MMIO resource using `nw_gcc_nord_regmap_config`, registers the clock table and reset map, and applies `qcom_cc_driver_data` so critical CBCRs stay enabled. After registration, consumers enable/disable branches or reprogram GP RCGs through normal CCF calls.

## State and persistence behavior
The driver has static descriptor state only. Persistent state lives in NWGCC registers: branch enable bits, halt status, GP RCG command/config registers, GPLL postdivider state, and reset registers. Critical CBCRs are intentionally kept enabled across normal consumer churn.

## Dependencies and integration points
It depends on qcom common CC helpers, alpha PLL, branch, RCG, divider, mux, reset support, and `dt-bindings/clock/qcom,nord-nwgcc.h`. Integration is device-tree based and provides infrastructure clocks to GPU/NoC/display/video/camera consumers rather than a user-facing subsystem.

## Risks
Most branch clocks use fixed register offsets and binding-index array positions; an off-by-one in the binding or descriptor array would expose the wrong hardware clock. Critical CBCR choices can mask missing consumers or keep hardware powered. Reset map offsets must match the NWGCC register map because qcom reset ops perform direct bit updates.

## Test signals
Boot should bind `nwgcc-nord` without regmap errors and show the exported clock names in `clk_summary`. GPU/display/video/camera traffic should be able to vote their AXI/HF/SF paths. Reset-controller lookups for the NWGCC reset IDs should assert/deassert the intended blocks. Suspend/resume and unused-clock disabling should preserve critical CBCR state.
