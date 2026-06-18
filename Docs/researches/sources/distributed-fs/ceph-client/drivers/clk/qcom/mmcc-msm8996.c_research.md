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
