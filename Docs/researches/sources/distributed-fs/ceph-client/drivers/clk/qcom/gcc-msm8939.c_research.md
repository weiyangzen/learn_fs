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
