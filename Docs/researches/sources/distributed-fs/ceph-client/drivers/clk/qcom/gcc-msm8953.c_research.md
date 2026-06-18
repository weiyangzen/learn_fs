# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8953.c

## Purpose

`gcc-msm8953.c` is the Qualcomm Global Clock Controller driver for the MSM8953 SoC. It describes the SoC's GCC clock tree, resets, and GDSC power domains and registers them with the Linux common clock, reset-controller, and genpd/GDSC infrastructure. Like other Qualcomm GCC drivers, it is table-driven: static descriptors encode PLLs, fixed dividers, parent mux values, RCG rates, branch gates, resets, and power domains, while a short probe maps registers and performs the one PLL configuration step needed by this controller.

The driver covers a broader peripheral set than the MSM8939 driver: BLSP1 and BLSP2 serial blocks, APSS AHB/AXI, APC droop detector clocks, camera with dual VFE and extra CSIPHY 3-phase clocks, display/MDSS dual DSI parents, crypto, DCC, QDSS, GP clocks, MSS, GPU/Oxili, PDM, RBCPR graphics, SDCC with ICE, USB3/USB PHY/ref clocks, Venus, SMMU/TBU, and multiple media/GPU GDSCs.

## Important APIs, Types, And Data

- The private parent enum includes `P_XO`, `P_SLEEP_CLK`, GPLL0/2/3/4/6, GPLL0 and GPLL6 fixed divide-by-2 outputs, and DSI0/DSI1 PLL and byte-clock parents.
- PLLs use alpha PLL infrastructure. `gpll0_early`, `gpll2_early`, `gpll4_early`, and `gpll6_early` are fixed alpha PLL clocks with vote bits in 0x45000; their read-only postdiv clocks (`gpll0`, `gpll2`, `gpll4`, `gpll6`) are exposed separately. `gpll0_early_div` and `gpll6_early_div` are `clk_fixed_factor` divide-by-2 hardware clocks exported through `gcc_msm8953_hws[]`.
- GPLL3 is programmable: `gpll3_p_vco[]` defines the 1-2 GHz VCO range, `gpll3_early_config` sets L/config/postdiv fields, `gpll3_early` uses `clk_alpha_pll_ops` with `SUPPORTS_DYNAMIC_UPDATE`, and `gpll3` is a postdiv clock with `CLK_SET_RATE_PARENT`.
- Parent maps and `clk_parent_data` arrays connect RCG mux values to PLLs, dividers, sleep clock, and DSI PLLs. Important maps include BLSP/APSS GPLL0-div2 maps, droop-detector GPLL0/GPLL4 maps, GPU GPLL0/GPLL3/GPLL6/GPLL4 maps, camera/media maps, MDSS pclk/byte maps for dual DSI, SDCC/ICE maps, USB3 maps, and VFE/Venus maps.
- RCGs (`struct clk_rcg2`) define command register offsets, divider widths, MND widths, frequency tables, parent maps, and ops. Most use `clk_rcg2_ops`; SDCC and GPU use floor rounding ops where needed; byte and pixel clocks use `clk_byte2_ops` and `clk_pixel_ops`.
- Branch clocks (`struct clk_branch`) define enable registers, halt checks, and optional parents. The driver uses a mix of `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, `BRANCH_HALT_DELAY`, and `BRANCH_VOTED` according to hardware behavior.
- GDSCs include `usb30_gdsc`, `venus_gdsc`, `venus_core0_gdsc`, `mdss_gdsc`, `jpeg_gdsc`, `vfe0_gdsc`, `vfe1_gdsc`, `oxili_gx_gdsc`, `oxili_cx_gdsc`, and `cpp_gdsc`. Many have `cxcs` arrays naming clock/reset-related registers that must be considered during collapse; USB30 is marked `ALWAYS_ON`, Venus core0 is `HW_CTRL`, and Oxili GX uses `CLAMP_IO`.
- `gcc_msm8953_clocks[]` maps binding IDs to the RCG/branch/PLL descriptors, `gcc_msm8953_hws[]` maps the fixed-factor hardware clocks, `gcc_msm8953_resets[]` maps the smaller reset set, and `gcc_msm8953_desc` publishes all of these to the Qualcomm common clock code.

## Control Flow

At `core_initcall`, `gcc_msm8953_init()` registers a platform driver named `gcc-msm8953`. The driver matches device-tree compatible `qcom,gcc-msm8953`. `gcc_msm8953_probe()` calls `qcom_cc_map()` with `gcc_msm8953_desc` to create a regmap for the GCC MMIO block. If mapping succeeds, it programs `gpll3_early` by calling `clk_alpha_pll_configure(&gpll3_early, regmap, &gpll3_early_config)`. It then calls `qcom_cc_really_probe()` to register clocks, resets, GDSCs, and the fixed-factor hardware clocks.

After probe, the file's runtime behavior is entirely framework-driven. Clock consumers invoke CCF operations through registered `clk_hw` instances. RCG ops program mux/divider/MND fields; branch ops set enable bits and poll or skip halt checks based on `halt_check`; alpha PLL ops handle GPLL3; fixed-factor clocks derive rates from parent PLLs; reset ops toggle BCR registers; and GDSC ops manage power domains using the GDSCR/cxc metadata.

## State And Persistence Behavior

The driver stores hardware topology in static C objects. It does not allocate or persist private runtime state. Mutable state is in GCC registers and in framework state after provider registration. Important hardware state includes alpha PLL config/mode registers, 0x45000/0x45004/0x4500c vote bits, RCG command and M/N/D registers, branch enable and halt status bits, reset BCR registers, USB/display/media/GPU GDSCR bits, and clamp/hardware-control flags.

Some descriptors intentionally model nonstandard state handling:

- `usb30_gdsc` is `ALWAYS_ON` because the comment notes DWC3 gadget resume failures after GDSC power-off.
- `venus_core0_gdsc` is `HW_CTRL`, meaning hardware participates in domain control.
- `oxili_gx_gdsc` uses `CLAMP_IO` and a clamp control register, so GPU power transitions have extra IO-clamp state.
- `gcc_usb3_pipe_clk` uses delayed halt handling, while QUSB/USB SS reference clocks skip halt checks, reflecting clocks that cannot be polled with the normal branch protocol.
- Fixed dividers in `gcc_msm8953_hws[]` are registered as independent hardware clocks so RCG parent data can target GPLL0/GPLL6 divided outputs.

## Dependencies And Integration Points

The driver depends on `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `common.h`, `gdsc.h`, and `reset.h`, plus kernel platform/OF/regmap/CCF/reset APIs. Device tree must provide the GCC node and external parent clocks named `xo`, `sleep`, `dsi0pll`, `dsi0pllbyte`, `dsi1pll`, and `dsi1pllbyte` where display parents are used. It also depends on `dt-bindings/clock/qcom,gcc-msm8953.h` for clock, reset, and GDSC IDs.

Consumer integration covers serial controllers on BLSP1/2, APSS interconnect clocks, CPU droop detector support, camera and ISP/VFE/JPEG/CPP blocks, MDSS/DSI display, Adreno/Oxili GPU, USB3/DWC3 and PHYs, SDCC/eMMC/SD plus ICE, Venus video, crypto, PRNG, QDSS/DCC debug blocks, PDM, RBCPR graphics, MSS, SMMU/TBU, and genpd consumers for media, USB, display, video, and GPU domains.

## Risks And Edge Cases

- The binding arrays are sparse, ID-indexed hardware contracts. A wrong array index or missing descriptor can break existing device-tree consumers.
- Parent maps are hardware mux-value sensitive. Several maps have different mux values for similar parents (`gcc_xo_gpll0_gpll0div2_2_map` versus `_4_map`, CSI0 versus CSI1/2, DSI0 versus DSI1 pclk/byte maps), so copy/paste changes are risky.
- GPLL3 is actively configured and rate-change capable. Incorrect VCO/config/postdiv values can affect high-rate GPU paths that use GPLL3.
- USB clocks have special halt semantics and USB30 GDSC is forced always on. Removing those exceptions could cause resume or probe failures in DWC3/PHY paths.
- GDSC `cxcs`, `HW_CTRL`, `CLAMP_IO`, and `ALWAYS_ON` flags encode domain-specific sequencing requirements; incomplete cxc lists can cause power-collapse timeouts or hardware access failures.
- Several branch clocks have no explicit parent because they represent bus, vote-only, or always-derived hardware paths. Adding parents without hardware validation could change enable sequencing.
- Dual-VFE and dual-DSI support increases the chance of mismatched parent names, mux values, or reset/power-domain dependencies.

## Test Signals

Validation should start with successful probe of `qcom,gcc-msm8953`, no missing parent-clock errors, and a populated clock/debugfs tree including the fixed GPLL dividers. Functional tests should exercise BLSP1/2 serial, SDCC1/2 and ICE, USB3 host/device and suspend/resume, MDSS with DSI0/DSI1 pixel/byte clocks, camera paths for CSI0/1/2 plus VFE0/VFE1/CPP/JPEG, Venus video, GPU frequency changes through GPLL3-backed rates, crypto/PRNG, QDSS/DCC, PDM, and RBCPR graphics. GDSC tests should power-cycle media, display, GPU CX/GX, Venus, CPP, VFE0/1, JPEG, and USB30 while checking for stuck halt bits, failed resumes, and genpd errors. Rate tests should request table entries for BLSP UART/SPI/I2C, SDCC, USB3 mock UTMI/master/aux, MDP/pclk/byte, VFE/CSI/JPEG/CPP/Venus, GPU, and droop-detector sources.
