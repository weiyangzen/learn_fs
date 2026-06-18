# Research: subset-b-001130

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8939.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8939.c

## Purpose

`gcc-msm8939.c` is the Qualcomm Global Clock Controller driver for the MSM8939 SoC. It publishes the SoC's GCC-managed clocks, reset lines, and power domains to Linux through the common clock framework, reset-controller framework, and Qualcomm GDSC/genpd support. The file is almost entirely static hardware description: PLL register layouts, vote bits, parent mux encodings, RCG frequency tables, branch gate registers, GDSC registers, reset offsets, and a small platform-driver probe that maps the GCC register block and registers the descriptors.

The driver covers core interconnect sources, APSS AHB, BLSP1 I2C/SPI/UART, camera, display, crypto, GPU/Oxili, PDM, SDCC, USB HS/FS, video/Venus, ultra-audio, SMMU/TBU, BIMC, and related reset controls. The public ABI is the device-tree binding IDs from `dt-bindings/clock/qcom,gcc-msm8939.h` and `dt-bindings/reset/qcom,gcc-msm8939.h`; consumer drivers request clocks/resets by those IDs.

## Important APIs, Types, And Data

- Parent IDs are defined in a private enum (`P_XO`, `P_GPLL0`, `P_BIMC`, `P_SLEEP_CLK`, DSI PHY PLL parents, external I2S/MCLK inputs, and GPLL aux names). These IDs connect `freq_tbl` entries to hardware mux values through `parent_map` arrays.
- PLLs use `struct clk_pll` plus voted `struct clk_regmap` wrappers. `gpll0`, `gpll1`, `gpll2`, `bimc_pll`, `gpll3`, `gpll4`, `gpll5`, and `gpll6` describe PLL control/status offsets; `*_vote` clocks share the 0x45000 vote register bits.
- `gpll3_config` and `gpll4_config` are the only PLL configurations actively applied in probe. The comments document GPLL3 at 1100 MHz and GPLL4 at 1200 MHz, with main/aux output masks and SR/HPM/LP configuration fields.
- Parent tables (`struct parent_map` and `struct clk_parent_data`) bind hardware mux values to local PLL vote clocks and firmware-provided parents such as `xo`, `sleep_clk`, `dsi0pllbyte`, `dsi0pll`, `ext_pri_i2s`, `ext_sec_i2s`, and `ext_mclk`.
- RCGs use `struct clk_rcg2` with `cmd_rcgr`, `hid_width`, optional `mnd_width`, parent maps, `freq_tbl`, and CCF ops. Most use `clk_rcg2_ops`; SDCC uses `clk_rcg2_floor_ops`; MDSS byte/pixel sources use `clk_byte2_ops` and `clk_pixel_ops`; some clocks set `CLK_SET_RATE_PARENT` or `CLK_GET_RATE_NOCACHE`.
- Frequency tables use the Qualcomm `F()` macro to encode rate, parent, divider, M, and N. They include domain-specific rates for camera CSI/VFE/CPP/JPEG, BLSP serial buses, GP PWM-like clocks, SDCC card clocks, GPU, USB, ultra-audio I2S/codec, MDP, and Venus.
- Branch clocks use `struct clk_branch`, usually with a `halt_reg`, `enable_reg`, `enable_mask`, optional `halt_check`, parent source, and `clk_branch2_ops`. Many peripheral branches set `CLK_SET_RATE_PARENT` so rate changes propagate to their RCG source.
- Power domains use `struct gdsc` for `venus`, `mdss`, `jpeg`, `vfe`, `oxili`, `venus_core0`, and `venus_core1`, each with a GDSCR offset and `PWRSTS_OFF_ON`.
- `gcc_msm8939_clocks[]`, `gcc_msm8939_gdscs[]`, and `gcc_msm8939_resets[]` are the main binding-ID lookup tables consumed by `qcom_cc_really_probe()`.
- `gcc_msm8939_regmap_config` describes a 32-bit, stride-4, fast-IO register map with `max_register = 0x80000`; `gcc_msm8939_desc` ties regmap, clocks, resets, and GDSCs together.

## Control Flow

At `core_initcall`, `gcc_msm8939_init()` registers `gcc_msm8939_driver`. The platform driver matches device-tree nodes with compatible string `qcom,gcc-msm8939`. In `gcc_msm8939_probe()`, the driver calls `qcom_cc_map()` to map the MMIO register block using `gcc_msm8939_desc`; if mapping fails, it returns the encoded error. It then programs GPLL3 and GPLL4 with `clk_pll_configure_sr_hpm_lp(..., true)` before calling `qcom_cc_really_probe()`.

After `qcom_cc_really_probe()` succeeds, the common Qualcomm clock-controller code registers all non-NULL clocks in `gcc_msm8939_clocks[]`, exposes reset controls from `gcc_msm8939_resets[]`, and registers the GDSC power domains. Runtime operations are then delegated to CCF ops: PLL enable/status logic, RCG mux/divider/MND programming, branch enable and halt polling, reset assertion/deassertion, and GDSC state transitions.

## State And Persistence Behavior

The C file owns no dynamic persistent state beyond static descriptor objects. Actual state lives in the GCC hardware registers: PLL mode/config/status registers, shared vote bits, RCG command/mux/divider registers, branch enable/halt registers, reset control registers, and GDSCR power-domain registers. Clock enable counts and provider registration state are maintained by the kernel frameworks after probe.

Several state details are important:

- Voted PLLs and voted branches share vote registers, so enable/disable semantics depend on hardware vote aggregation rather than simple private gates.
- `CLK_GET_RATE_NOCACHE` on BIMC-related sources signals that the framework should not trust cached rates for those hardware paths.
- `CLK_SET_RATE_PARENT` on display, camera, audio, SDCC, and other branches allows a consumer request on the branch to reprogram its parent source.
- The driver does not preserve configuration across reboot or suspend by itself; any persistence depends on hardware retention and framework reinitialization.

## Dependencies And Integration Points

This driver depends on Linux platform devices, OF matching, regmap, CCF, reset-controller, and Qualcomm helpers in `common.h`, `clk-regmap.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h`. Device tree must provide a matching GCC node and firmware parent clocks with names used in `clk_parent_data` (`xo`, `sleep_clk`, DSI PLL clocks, and external audio clocks where used). Consumers depend on the binding headers for stable clock/reset/GDSC indices.

Major integration surfaces include BLSP serial drivers, camera and ISP/VFE/JPEG/CPP drivers, DRM/MDSS/DSI display drivers, Venus video, Adreno/Oxili GPU, SDHCI/MSM, USB HS/FS, crypto, PDM/audio, SMMU/TBU users, PRNG, and boot/ROM or security-related blocks. The GDSCs are also power-domain providers to device-tree consumers.

## Risks And Edge Cases

- This file is register-table sensitive. A wrong offset, mux value, vote bit, halt register, or binding index can silently clock the wrong block or hang a consumer during enable/disable.
- Shared vote registers at 0x45000, 0x45004, and 0x4500c require exact bit assignments; collisions or incorrect `BRANCH_HALT_VOTED` usage can break unrelated hardware.
- External parents (`dsi0pll`, `dsi0pllbyte`, audio MCLK/I2S, sleep clock) must match DT names. Missing parents can cause probe deferral or unavailable display/audio clocks.
- The comments identify `crypto_clk_src` and `pdm2_clk_src` as downstream-derived rather than documented. Those entries deserve hardware validation when porting.
- GP clock frequency tables include duty-cycle constraints tied to MND width; changing M/N values can reduce PWM duty-cycle control.
- GDSC ordering and power-domain names must match downstream hardware dependencies. Video core GDSCs and media blocks can fail if required bus/AXI clocks are not coordinated by consumers.
- There is no custom remove-time cleanup beyond `platform_driver_unregister()` at module exit; framework registration must remain consistent.

## Test Signals

Useful validation signals are successful boot with `qcom,gcc-msm8939` matched, absence of `qcom_cc_map()` or parent-clock probe failures, clock summary entries under debugfs, and stable enable/disable of representative consumers: BLSP UART/I2C/SPI, SDCC1/2, USB HS/FS, MDSS/DSI, camera CSI/VFE/JPEG/CPP, Venus, GPU/Oxili, audio, crypto, and PRNG. Reset-controller tests should assert/deassert mapped BCRs without bus hangs. GDSC tests should power-cycle media, display, GPU, and Venus domains while checking for timeout or stuck halt bits. Rate tests should request table rates for SDCC, UART, SPI, MDP pixel/byte, VFE/CSI, GPU, USB, and audio I2S paths and verify that parent propagation and hardware readback agree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8939.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8953.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8953.c -->
