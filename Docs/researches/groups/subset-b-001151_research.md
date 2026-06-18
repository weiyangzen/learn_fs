# Research: subset-b-001151

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8994.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8994.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8996.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8996.c

## Purpose

`mmcc-msm8996.c` is the Qualcomm multimedia clock controller driver for MSM8996. It publishes the SoC multimedia clock, reset, and GDSC topology for MMAGIC fabric, SMMU paths, GPU, VMEM, video, display, camera, JPEG, CPP, VFE, CSI, and face-detection blocks. The driver is a static hardware-description table plus a small probe routine that applies two register workarounds before registering the descriptor through the common QCOM clock-controller framework.

## Important APIs, Types, And Data

- External and shared APIs: `platform_driver`, `MODULE_DEVICE_TABLE`, `regmap_update_bits()`, `qcom_cc_map()`, `qcom_cc_really_probe()`, common clock framework `clk_init_data`, and fixed-factor `clk_fixed_factor_ops`.
- Local QCOM types: `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `clk_fixed_factor`, `clk_rcg2`, `clk_rcg2_gfx3d`, `clk_branch`, `gdsc`, `qcom_reset_map`, and `qcom_cc_desc`.
- Parent enum values cover XO, MMPLL0/1/2/3/4/5/8/9, GPLL0, a derived GPLL0_DIV, DSI PLLs, DSI byte PLLs, and HDMI PLL.
- `gpll0_div` is a fixed-factor half-rate clock derived from `gpll0`; it is registered through the descriptor's `.clk_hws` path and used as a parent source for several RCGs.
- PLLs are represented as early alpha PLLs plus postdiv clocks for MMPLL0, 1, 2, 3, 4, 5, 8, and 9. The file uses separate VCO tables for multimedia P-type PLLs, graphics PLLs, and T-type PLLs.
- Parent maps combine XO, GPLL0, GPLL0_DIV, local MMPLLs, DSI/HDMI PLLs, and byte PLLs. Several RCGs use large parent sets so the clock framework can choose among local PLLs and fabric parents.
- RCG families include AHB, AXI, MAXI, `gfx3d_clk_src`, RBBM timer, isense, RBCPR, video core/subcores, display pixel/MDP/HDMI/byte/escape/vsync, camera GP/MCLK/CCI/CSI/CSIPHY/JPEG/VFE/CPP/FD, and internal bus roots.
- Branch clocks expose MMAGIC and SMMU clocks, GPU clocks, VMEM, RBCPR, video, MDSS, CAMSS, JPEG, VFE, CPP, CSI, and FD clocks. Critical flags are used on key MMAGIC AXI/NOC configuration paths that must not be gated.
- GDSCs include always-on/votable MMAGIC fabric domains, video/Venus domains, CAMSS/VFE/JPEG/CPP/FD domains, MDSS, GPU, and GPU GX. `gpu_gx_gdsc` uses `CLAMP_IO` and the `"vdd-gfx"` supply.
- Reset coverage is much broader than MSM8994: MMAGIC, SMMU, throttle blocks, GPU, VMEM, RBCPR, video, MDSS, CAMSS, CCI, PHYs, JPEG, VFE, CPP, CSI, ISPIF, FD, and SPDM reset registers are mapped.

## Control Flow

1. The platform driver binds only to `"qcom,mmcc-msm8996"`.
2. `mmcc_msm8996_probe()` maps the MMCC register space with `qcom_cc_map()`.
3. Probe applies two direct register updates: it clears bit 31 at `0x50d8` to disable AHB DCD, and clears bit 15 at `0x5054` to disable the NoC FSM for `mmss_mmagic_cfg_ahb_clk`.
4. `qcom_cc_really_probe()` registers the descriptor, including clocks, resets, GDSCs, and the `gpll0_div` hardware clock.

After registration, all clock operations are handled by common QCOM ops. The special `clk_rcg2_gfx3d` source uses `clk_gfx3d_ops` and has explicit PLL hardware references for graphics parent handling. The driver itself has no remove or suspend/resume logic.

## State And Persistence Behavior

The file has no dynamically allocated driver-private state. Persistent state is the hardware state in MMCC registers and GDSC/regulator/power-domain state managed by the common frameworks. Unlike the MSM8994 driver, it does not mutate descriptor arrays based on compatible strings. The only imperative state changes in probe are the two `regmap_update_bits()` workaround writes.

Because `gpll0_div` is registered as a `clk_hw` outside the regmap clock array, consumers and RCG parent maps rely on descriptor `.clk_hws` registration succeeding in addition to normal `clk_regmap` registration. GDSC parent pointers encode persistent power-domain hierarchy: MMAGIC domains sit above functional blocks, video cores are children of Venus, and GPU GX is a child of GPU.

## Dependencies And Integration Points

- The binding header `dt-bindings/clock/qcom,mmcc-msm8996.h` defines the clock/reset/GDSC array indices consumed by device tree and kernel clients.
- Device tree must provide MMIO resources and parent clocks named like `xo`, `gpll0`, DSI PLLs/byte PLLs, HDMI PLL, and GCC-provided NOC configuration clocks.
- Integration is with the common QCOM clock stack, reset controller registration, and GDSC/genpd power-domain code.
- Downstream consumers include Adreno/GPU, MDSS display, Venus video, CAMSS camera, SMMU/IOMMU paths, JPEG, CPP, VFE, FD, VMEM, and MMAGIC fabric users.
- The regmap aperture is 32-bit, stride 4, fast I/O, and `.max_register = 0xb008`, large enough for MMCC and graphics-related multimedia blocks represented in this SoC.

## Risks And Edge Cases

- The two probe-time register workarounds are undocumented in this file beyond short comments. Removing or reordering them may reintroduce AHB DCD or NoC FSM hangs around MMAGIC configuration clocks.
- Many bus and MMAGIC/SMMU clocks carry `CLK_IS_CRITICAL`. Over-aggressive clock cleanup or flag changes can break memory access for display, camera, video, or GPU before clients can vote explicitly.
- Parent names include both `.fw_name` and legacy `.name` fallbacks such as `"xo_board"`, `"gpll0"`, `"gcc_mmss_noc_cfg_ahb_clk"`, and PLL names. Device-tree naming drift can cause unresolved parents or probe deferral.
- `clk_rcg2_gfx3d` is a special graphics clock source rather than a plain RCG. Rate/parent bugs there directly affect GPU DVFS and stability.
- GDSC `ALWAYS_ON`, `VOTABLE`, `HW_CTRL`, `CLAMP_IO`, and regulator supply flags encode sequencing constraints. Bad changes can cause power-collapse timeouts or GPU rail/clamp issues.
- Reset-array drift against the binding header is easy because the reset table is large and index-based.

## Test Signals

- Build and sparse-style checks should verify all binding indices resolve and the descriptor arrays compile without missing symbols.
- Probe validation on MSM8996 hardware should show successful `mmcc-msm8996` registration with no missing parent clocks and no regmap access failures.
- `clk_summary` should include `gpll0_div`, MMPLLs, `gfx3d_clk_src`, MMAGIC/SMMU clocks, GPU clocks, MDSS, CAMSS, video, JPEG, CPP, VFE, CSI, and FD clocks.
- Functional signals: GPU bring-up and DVFS, display modes, camera capture paths, Venus encode/decode, JPEG/CPP/VFE operation, and IOMMU/SMMU-backed multimedia DMA.
- Power testing should exercise GDSC transitions for MMAGIC, video, CAMSS, MDSS, GPU/GX, FD, JPEG, CPP, and VFE domains while checking for timeout or regulator errors.
- Reset testing should cover CAMSS and multimedia reset controls from their consumers and confirm no unrelated block is reset through a wrong index.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8996.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8998.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8998.c -->
