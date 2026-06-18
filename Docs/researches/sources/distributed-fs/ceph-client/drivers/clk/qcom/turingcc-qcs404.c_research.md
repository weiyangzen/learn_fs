# sources/distributed-fs/ceph-client/drivers/clk/qcom/turingcc-qcs404.c

## Purpose
This driver registers the QCS404 Turing clock controller, exposing always-on/wrapper/Q6SS AHB and AXI branch clocks around the Turing/QDSP subsystem.

## Important APIs, types, and functions
- Five `clk_branch` descriptors define wrapper AON, Q6SS AHBM, Q6 AXIM, Q6SS AHBS AON, and wrapper QoS AHBS AON clocks.
- AON branches use `clk_branch2_aon_ops`; regular branch uses `clk_branch2_ops`.
- `turingcc_clocks[]` maps binding IDs from `qcom,turingcc-qcs404.h`.
- `turingcc_probe()` enables runtime PM, creates/acquires a PM clock, resumes the device, calls `qcom_cc_probe()`, then releases the runtime PM reference.
- `turingcc_pm_ops` delegates runtime suspend/resume to PM clock helpers.

## Control flow
The platform driver matches `"qcom,qcs404-turingcc"`. Probe prepares runtime PM and the interface clock, resumes the hardware for MMIO access, registers the qcom CC descriptor, then idles the runtime PM reference. CCF consumers later toggle branches as needed.

## State and persistence behavior
Clock enable and halt state persists in Turing CC registers. Runtime PM controls the interface clock used for register access. No private software state is stored beyond devres/runtime-PM state.

## Dependencies and integration points
It depends on qcom common CC, branch ops, platform resources, runtime PM, PM clocks, regmap, and `dt-bindings/clock/qcom,turingcc-qcs404.h`. It integrates with Q6/Turing subsystem consumers that need bus and wrapper clocks.

## Risks
Missing interface clock or runtime PM resume failure prevents registration. AON branch semantics must match hardware; using non-AON ops on always-on paths could gate critical access. There are no reset maps, so reset control must come from elsewhere.

## Test signals
Probe should log no interface-clock errors and register five clocks. Runtime suspend/resume should preserve register access. Q6/Turing boot or firmware loading should exercise the AHBS/AHBM/AXIM paths. `clk_summary` should show AON branches with expected prepare/enable behavior.
