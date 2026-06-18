# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sa8775p.c

## Purpose
This driver registers SA8775P/QCS8300 VIDEOCC clocks, resets, and GDSCs for MVS0/MVS0C/MVS1/MVS1C video domains, with explicit runtime-PM and PLL setup in probe.

## Important APIs, types, and functions
- `video_pll0` and `video_pll1` are Lucid EVO alpha PLLs.
- RCGs cover AHB, MVS0, MVS1, sleep, XO, and a status/monitor divider path.
- Branches expose MVS0/MVS0C/MVS1/MVS1C clocks, PLL lock monitor, and SM observation clocks.
- Four GDSCs and seven reset map entries cover MVS domains and interface reset.
- `video_cc_sa8775p_probe()` enables runtime PM, maps registers, configures both PLLs, applies a QCS8300-specific MVS0C divider override, forces critical AHB/sleep/XO branches on, registers qcom CC, and drops the PM reference.

## Control flow
The platform driver matches `"qcom,sa8775p-videocc"` or `"qcom,qcs8300-videocc"`. Unlike many newer video drivers that rely entirely on driver data, probe manually performs power management, regmap mapping, PLL configuration, optional variant tweak, critical branch enables, and `qcom_cc_really_probe()`.

## State and persistence behavior
Runtime PM controls register-access power during probe. Hardware registers retain PLL configuration, variant divider override, branch enables, reset bits, and GDSC state. Critical branches are forced on by direct `qcom_branch_set_clk_en()` writes.

## Dependencies and integration points
It depends on qcom alpha PLL/PLL/branch/RCG/divider/mux/common/GDSC/reset helpers, regmap, runtime PM, platform matching, and SA8775P video dt-bindings. Video drivers consume its clocks, resets, and power domains; QCS8300 uses the compatible-specific divider behavior.

## Risks
Manual probe sequencing increases risk: each error path must release runtime PM correctly. The QCS8300 divider write is variant-specific and could misclock MVS0C if the compatible is wrong. Critical branch forcing affects power and masks missing consumers. No `qcom_cc_driver_data` lists PLLs, so PLL setup depends on probe code.

## Test signals
Run video workloads on both SA8775P and QCS8300. Confirm PLL0/PLL1 lock, MVS0/MVS1 rates, GDSC transitions, and reset behavior. On QCS8300, verify MVS0C divider register equals div-3 override. Runtime PM trace should show balanced get/put on success and map errors.
