# sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8998.c

## Purpose

`mmcc-msm8998.c` is the Qualcomm multimedia clock controller driver for MSM8998. It describes the multimedia clock tree and power/reset controls for display, DisplayPort/HDMI, DSI, camera, video, VFE/CPP/JPEG/FD, CSIPHY/CPHY, MNOC/BIMC-SMMU/VMEM, and related MMSS infrastructure. Compared with MSM8996 it uses fixed Fabia alpha PLLs and exported even post-dividers, and compared with MSM8994 it has newer DisplayPort and MMNOC/BIMC-SMMU coverage.

## Important APIs, Types, And Data

- External/shared APIs: `platform_driver`, `MODULE_DEVICE_TABLE`, `qcom_cc_map()`, `qcom_cc_really_probe()`, `regmap`, common clock framework init structures, and QCOM common clock helpers.
- Core local types: `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `clk_rcg2`, `clk_branch`, `gdsc`, `qcom_reset_map`, `regmap_config`, `qcom_cc_desc`, `parent_map`, `clk_parent_data`, and `freq_tbl`.
- Parent IDs cover XO, GPLL0, GPLL0_DIV, even outputs of MMPLL0/1/3/4/5/6/7/10, DSI PLLs, DSI byte PLLs, HDMI PLL, DP VCO, and DP link.
- PLLs use `CLK_ALPHA_PLL_TYPE_FABIA` registers. `mmpll0`, `mmpll1`, `mmpll3`, `mmpll4`, `mmpll5`, `mmpll6`, `mmpll7`, and `mmpll10` are modeled as fixed Fabia PLLs with `clk_alpha_pll_fixed_fabia_ops`; each has an `*_out_even` postdivider using `clk_alpha_pll_postdiv_fabia_ops` and `post_div_table_fabia_even`.
- Parent maps connect local Fabia even PLL outputs with GCC-provided `gpll0`, `gcc_mmss_gpll0_div_clk`, DSI/HDMI PLLs, and DP parents (`dplink`, `dpvco`).
- RCG sources cover byte, CCI, CPP, CSI0-3, CSIPHY, CSI PHY timers, DP auxiliary/crypto/link/pixel, DSI escape/ext pixel, FD core, HDMI, JPEG, MAXI, MCLK0-3, MDP, vsync, AHB/AXI, display pixel, rotator, video core/subcores, and VFE0/1.
- Branch clocks expose video, MDSS, DP/HDMI/DSI display clocks, CAMSS and camera sensor clocks, VFE/CPP/JPEG/CSI/CPHY/CSIPHY clocks, FD clocks, MNOC, BIMC SMMU, VMEM, and related bus paths. Some SMMU and MNOC/BIMC branches use `BRANCH_HALT_SKIP`, reflecting halt-status behavior that must not be polled normally.
- GDSCs cover video top/subcore0/subcore1, MDSS, CAMSS top, CAMSS VFE0/VFE1/CPP, and BIMC SMMU. Video subcores are hardware-controlled children of video top, and BIMC SMMU is votable with a hardware-control register.
- Resets cover SPDM, video, MDSS, display throttling, camera PHY/CSI/ISPIF/CCI/top/JPEG/VFE/CPP/FD, MNOC, BIMC SMMU, VMEM, and BTO reset registers.

## Control Flow

1. The platform driver binds to `"qcom,mmcc-msm8998"`.
2. `mmcc_msm8998_probe()` maps the register block with `qcom_cc_map(pdev, &mmcc_msm8998_desc)`.
3. If mapping succeeds, `qcom_cc_really_probe()` registers all descriptor clocks, resets, and GDSCs.

This file has no probe-time PLL configuration calls or register workaround writes. It relies on fixed Fabia PLL ops and predescribed postdivider state rather than imperative setup. All later rate, parent, branch, reset, and power-domain operations are handled by the framework ops referenced in static data.

## State And Persistence Behavior

The driver does not allocate private state and does not mutate descriptor arrays at runtime. Persistent state lives in the MMCC hardware registers: Fabia PLL controls, RCG command registers, branch enable/halt registers, GDSC power registers, and reset registers. The static data is effectively immutable after registration.

Because parent data mixes firmware names, legacy clock names, and local `clk_hw` pointers, registration state depends on both local PLL objects and external providers being present. Display and DP clocks use parent-rate propagation so mode-setting clients can drive external PHY/PLL rates through the clock framework.

## Dependencies And Integration Points

- Binding IDs come from `dt-bindings/clock/qcom,mmcc-msm8998.h` and must remain aligned with the descriptor arrays.
- Device tree must provide the MMCC resource and parents such as `xo`, `gpll0`, `gpll0_div`/`gcc_mmss_gpll0_div_clk`, DSI PLL/byte clocks, HDMI PLL, DP link, and DP VCO.
- The driver integrates with QCOM clock, reset, and GDSC frameworks through `common.h`, `clk-regmap.h`, `clk-alpha-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h`.
- Consumers include MDSS/DSI/HDMI/DP display, CAMSS camera and sensors, VFE/CPP/JPEG/FD imaging blocks, Venus/video cores, MNOC and BIMC SMMU infrastructure, and VMEM.
- The regmap config is 32-bit, stride 4, fast I/O, with `.max_register = 0x10004`, matching the wider MSM8998 MMCC register range.

## Risks And Edge Cases

- Fabia PLL modeling is different from the older alpha PLL setup. Using non-Fabia ops, wrong postdivider tables, or wrong even-output parents would break many derived rates.
- DisplayPort support introduces multiple external parents and RCGs (`dp_aux`, `dp_crypto`, `dp_link`, `dp_pixel`). Parent-name or rate-propagation mistakes can break DP link training or pixel clocks.
- Branches with `BRANCH_HALT_SKIP` indicate hardware halt status is unreliable or unavailable. Converting them to normal halt polling may create false enable/disable timeouts.
- Clock tables contain many high-performance camera/display/video rates. Parent selector mistakes can overclock/underclock VFE, CPP, MDP, video, or sensor paths.
- GDSC hierarchy is shallower than MSM8996 for some blocks but still contains hardware-controlled video subcores and a votable BIMC SMMU domain. Wrong parent or flag changes can affect power collapse and multimedia DMA.
- Reset indices are numerous and binding-indexed; a one-line shift can expose a reset under the wrong ID.

## Test Signals

- Compile testing should validate MSM8998 binding IDs, Fabia PLL symbols, and all descriptor array indices.
- Probe testing should confirm `mmcc-msm8998` registers without missing parents for XO, GPLL0/GPLL0_DIV, DSI, HDMI, and DP parents.
- `clk_summary` should show Fabia MMPLLs and their `_out_even` clocks, DP RCGs, MDSS DP/HDMI/DSI branches, CAMSS/VFE/CPP/JPEG/FD clocks, video clocks, MNOC/BIMC SMMU, and VMEM clocks.
- Functional validation should include DSI and DP display modes, camera capture through CSI/CSIPHY/CPHY/VFE/CPP/JPEG, Venus video operation, FD clocks if used, and multimedia DMA through SMMU.
- Power-domain testing should toggle video, MDSS, CAMSS top, VFE0/1, CPP, and BIMC SMMU domains while checking GDSC timeouts and bus access.
- Reset tests should assert/deassert CAMSS, VFE, CPP, MDSS, video, MNOC, BIMC SMMU, and VMEM resets from consumers and verify no cross-block reset side effects.
