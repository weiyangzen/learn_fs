# sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8994.c

## Purpose

`mmcc-msm8994.c` is the Qualcomm multimedia clock controller driver for MSM8994 and its MSM8992-compatible variant. It describes the MMSS clock tree used by camera, display, video, JPEG, face-detection, OCMEM, and Adreno/Oxili multimedia blocks. The file is almost entirely declarative: it builds static common-clock-framework objects for PLLs, RCG frequency generators, branch gates, GDSC power domains, and resets, then passes them to the shared Qualcomm CC registration helpers during platform-driver probe.

## Important APIs, Types, And Data

- External Linux/QCOM APIs: `platform_driver`, `of_device_id`, `MODULE_DEVICE_TABLE`, `regmap`, `qcom_cc_map()`, `qcom_cc_really_probe()`, `clk_alpha_pll_configure()`, `of_device_is_compatible()`, and common clock framework structures through `clk_init_data`.
- Local Qualcomm clock types: `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_rcg2`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct qcom_cc_desc`, `struct parent_map`, `struct clk_parent_data`, and `struct freq_tbl`.
- Parent IDs are defined in the local enum: XO, GPLL0, MMPLL0/1/3/4/5, DSI PLLs, DSI byte PLLs, and HDMI PLL. Parent maps encode hardware mux selector values, while `clk_parent_data` binds those selectors to firmware names or local `clk_hw` pointers.
- PLL state is modeled as early alpha PLL clocks plus postdiv clocks for `mmpll0`, `mmpll1`, `mmpll3`, `mmpll4`, and `mmpll5`. `mmpll_p_vco` covers 250 MHz through 2 GHz ranges; `mmpll_t_vco` covers 500 MHz through 1.5 GHz. `mmpll_p_config` programs the post-divider mask for the P-type PLLs.
- RCG tables cover AHB/AXI, CSI, VFE, CPP, JPEG, CSI PHY timers, face-detection, MDP, OCMEMNOC, CCI, GP clocks, MCLKs, DSI byte/pixel/escape, HDMI/ext pixel, vsync, RBBM timer, and Venus video codec roots. Some have MSM8992-specific replacements.
- Branch clocks gate the consumer-visible clocks under CAMSS, MDSS, MMSS fabric, OCMEM, Oxili GPU, Venus, JPEG, VFE, CPP, and face-detection blocks. Most are `clk_branch2_ops`; DSI byte clocks use `clk_byte2_ops`, DSI pixel clocks use `clk_pixel_ops`, and generic RCG roots use `clk_rcg2_ops`.
- GDSCs represent power domains for Venus top/core0/core1/core2, MDSS, CAMSS top, JPEG, VFE, CPP, FD, Oxili CX, and Oxili GX. Several child domains use `.parent`, Venus core domains use `HW_CTRL`, Oxili CX is `VOTABLE`, and Oxili GX uses `CLAMP_IO` plus the `"VDD_GFX"` supply.
- The single reset exposed by this driver is `CAMSS_MICRO_BCR` at `0x3490`.

## Control Flow

1. The module binds through `mmcc_msm8994_match_table`, accepting `"qcom,mmcc-msm8992"` and `"qcom,mmcc-msm8994"`.
2. `mmcc_msm8994_probe()` first checks the device-tree compatible. For MSM8992 it mutates the shared descriptor arrays by nulling clocks and GDSCs that do not exist on MSM8992, and swaps selected RCG `freq_tbl` pointers to MSM8992-specific tables.
3. The probe maps the MMCC register space with `qcom_cc_map(pdev, &mmcc_msm8994_desc)`. Mapping failure returns the encoded error.
4. Four early PLLs are explicitly configured with `clk_alpha_pll_configure()` after mapping: `mmpll0_early`, `mmpll1_early`, `mmpll3_early`, and `mmpll5_early`. `mmpll4_early` is defined but not configured with `mmpll_p_config`, matching its separate T-type VCO handling.
5. `qcom_cc_really_probe()` registers the descriptor-provided clocks, resets, and GDSCs with the common clock framework, reset framework, and genpd/GDSC layer.

There is no runtime callback beyond probe. Clock rate selection, parent switching, branch enable/disable, reset assertion, and GDSC transitions are delegated to the shared clock/reset/GDSC implementations referenced by each static object.

## State And Persistence Behavior

The driver keeps no private heap state, no persistent storage, and no software state machine. Its state is static C data plus hardware register state. Probe mutates global static descriptor contents for MSM8992 compatibility, so the module assumes a single practical MMCC instance and a stable compatible decision. Hardware-facing persistence is in MMCC registers: PLL configuration, RCG mux/divider fields, branch enable bits, halt bits, reset registers, and GDSC power-control registers.

The MSM8992 branch is the most important stateful behavior: it permanently nulls entries in `mmcc_msm8994_desc.clks` and `mmcc_msm8994_desc.gdscs`, and replaces several `freq_tbl` pointers. That is safe for the normal one-device-per-SoC binding model, but it would be wrong if the same module were asked to register both MSM8992 and MSM8994 instances in one kernel lifetime.

## Dependencies And Integration Points

- Device tree must provide a compatible string, MMCC MMIO resource, and parent clock names such as `xo`, `gpll0`, `dsi0pll`, `dsi1pll`, DSI byte PLLs, and `hdmipll`.
- Clock IDs, reset IDs, and GDSC IDs are defined by `dt-bindings/clock/qcom,mmcc-msm8994.h`; the order of `mmcc_msm8994_clocks[]`, `mmcc_msm8994_gdscs[]`, and `mmcc_msm8994_resets[]` must match that binding.
- The driver depends on shared QCOM clock code in `common.h`, `clk-regmap.h`, `clk-alpha-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h`.
- Consumers are camera (`camss_*`), display (`mdss_*`), video (`venus0_*`), JPEG, FD, OCMEM, and GPU/Oxili device-tree nodes that request clocks, resets, and power domains by binding index/name.
- The register map is 32-bit, stride 4, fast I/O, with `.max_register = 0x5200`, defining the accessible MMCC register aperture for regmap validation.

## Risks And Edge Cases

- MSM8992 support relies on global descriptor mutation. A bad compatible string or accidental multi-instance scenario can silently remove clocks/GDSCs or leave MSM8994 tables with MSM8992 rates.
- Several parent names are firmware-name sensitive. Mismatches in device-tree clock-names for DSI/HDMI/GPLL/XO parents will cause registration deferral or missing parent links.
- The file contains an explicit uncertainty comment around `P_MMPLL5`; although `mmpll5` is configured and registered, downstream use was unclear to the author.
- Rate table correctness is hardware-critical. Incorrect divisors or parent selectors can produce display underflow, camera capture failures, video decode instability, or GPU hangs.
- Some branches are marked critical or ignore-unused (`mmss_mmssnoc_axi_clk`, `mmss_s0_axi_clk`) because gating them can destabilize MMSS. Removing those flags would be high risk.
- Pixel/byte clocks use `CLK_GET_RATE_NOCACHE` and `CLK_SET_RATE_PARENT`, so stale rate assumptions around external display PLLs are avoided; changing those flags can break dynamic display modes.
- GDSC flags and parent relationships encode sequencing requirements. Oxili GX depends on CX and a regulator supply, while Venus core domains are hardware-controlled children.

## Test Signals

- Build coverage: compile the QCOM MMCC driver with the MSM8994 binding header and common clock helpers enabled; warnings around missing initializers or array indices indicate binding drift.
- Device-tree boot: probe should log no missing parent-clock errors for `"qcom,mmcc-msm8994"` or `"qcom,mmcc-msm8992"` boards.
- Clock debugfs: expected registered names include MMPLLs, CAMSS, MDSS, Venus, Oxili, OCMEM, and FD clocks; MSM8992 should not expose the nulled FD/JPEG1/JPEG2/Venus core2 entries.
- Functional checks: display panel/HDMI/DSI modes, camera CSI/VFE/CPP/JPEG paths, video codec paths, and GPU initialization are the main integration signals.
- Power-domain checks: GDSC enable/disable around camera, display, video, and GPU consumers should complete without timeout, clamp, or regulator errors.
