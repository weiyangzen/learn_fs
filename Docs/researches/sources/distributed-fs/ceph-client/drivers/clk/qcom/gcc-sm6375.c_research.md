# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm6375.c

## Purpose

`gcc-sm6375.c` is the Qualcomm Global Clock Controller driver for SM6375. It exports GCC clocks, resets, GDSC power domains, and DFS-capable QUP root clocks using IDs from `dt-bindings/clock/qcom,sm6375-gcc.h`.

Compared with smaller GCC drivers, this file covers a broad multimedia clock plan: camera CSIPHY/TFE/OPE/MCLK clocks, video/Venus clocks, display/GPU/NPU fabric gates, QUPv3 serial engines, SDCC, UFS, USB, and many MMU TBU power-domain votes. It combines declarative descriptors with probe-time PLL configuration and always-on branch votes.

## Important APIs, Types, And Data

- `struct pll_vco` and `struct alpha_pll_config`: define Lucid and Zonda VCO ranges plus explicit configurations for `gpll10` at 1152 MHz, `gpll11` around 532 MHz, `gpll8`, and `gpll9`.
- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv`: model GPLL0/1/3/4/5/6/7/8/9/10/11, with Lucid PLL ops for most GPLLs and Zonda PLL ops for GPLL9. Several post-dividers expose even/odd/main derived outputs.
- Local `DT_*` enums and `clk_parent_data`: identify external clock-parent indices `DT_BI_TCXO`, `DT_BI_TCXO_AO`, and `DT_SLEEP_CLK`.
- `struct parent_map`: maps many hardware selector encodings to GPLL0, GPLL3, GPLL5, GPLL6, GPLL7, GPLL8, GPLL9, GPLL10, GPLL11, XO, and sleep parents.
- `struct freq_tbl`: supplies camera, CPUSS, GP, PDM, QUPv3, SDCC, UFS, USB, and video rates. Camera tables are especially dense for AXI, CCI, CSI PHY timers, five MCLKs, OPE, TFE, CSID, CPHY RX, and top AHB.
- `struct clk_rcg2`: models RCGs. Many multimedia RCGs use `clk_rcg2_shared_ops`, reflecting shared or potentially firmware-coordinated resources. Some set `CLK_SET_RATE_PARENT` to propagate rate requests into PLLs.
- `struct clk_regmap_div`: exposes read-only post-dividers for CPUSS AHB and USB mock UTMI.
- `struct clk_branch`: exports gates for camera, display, GPU, video, UFS, USB, QUPv3, SDCC, PDM, PRNG, QMIP, fabric, and clock-reference paths. Branches use a mix of regular, voted, delayed, skip, and simple hardware-control halt handling.
- `struct gdsc`: describes USB, UFS, CAMSS, Venus, Vcodec, and four votable Turing/MM SNOC MMU TBU domains. `vcodec0_gdsc` is hardware-controlled.
- `struct qcom_reset_map`: maps MMSS, USB/PHY, QUSB2 PHY, SDCC, QUP wrappers, PDM, GPU, UFS, CAMSS, Venus, Vcodec, and video-interface resets.
- `struct clk_rcg_dfs_data`: enables DFS for six QUPv3 engines in wrapper 0 and six in wrapper 1.
- `struct qcom_cc_desc`: registers clocks, resets, and GDSCs over a regmap with `max_register = 0xc7000`.

## Control Flow

The driver matches `qcom,sm6375-gcc` and registers at `subsys_initcall()`. Probe proceeds as follows:

1. `qcom_cc_map()` maps the GCC MMIO region.
2. `qcom_cc_register_rcg_dfs()` registers the QUPv3 DFS RCG list.
3. `qcom_branch_set_clk_en()` force-enables three always-on branches: camera XO at `0x17028`, CPUSS GNOC at `0x2b004`, and display XO at `0x1702c`.
4. `clk_lucid_pll_configure()` programs GPLL10, GPLL11, and GPLL8 from their static configs.
5. `clk_zonda_pll_configure()` programs GPLL9 from its static config.
6. `qcom_cc_really_probe()` registers the clock, reset, and power-domain providers.

Runtime control then flows through normal CCF operations. Leaf branches can request parent rates; RCG ops select rate-table rows and write parent/divider/M/N fields; GDSC and reset operations are delegated to the Qualcomm common code.

## State And Persistence Behavior

The driver keeps no private dynamic state after probe. Hardware state lives in GCC registers, PLL configuration registers, branch enable registers, reset registers, and GDSCR registers.

Probe actively programs four PLLs and force-enables three branches, so this driver does more than expose pre-existing hardware state. Those changes persist until later clock framework operations, firmware, reset, or power-domain changes alter them. DFS-capable QUP RCGs may be reprogrammed through the DFS framework for serial-engine operating points.

USB uses `PWRSTS_RET_ON` with an in-code TODO noting it should become off/on when USB suspend support is proper. UFS, CAMSS, Venus, and MMU TBU domains use off/on semantics, while `vcodec0_gdsc` is marked `HW_CTRL`, leaving power transitions partly hardware-managed.

## Dependencies And Integration Points

- Linux CCF and Qualcomm clock helpers: alpha PLL, RCG, branch, regmap divider/mux, and GDSC support.
- PLL configuration helpers: `clk_lucid_pll_configure()` and `clk_zonda_pll_configure()` are required for probe-time GPLL setup.
- Device-tree bindings: clock/reset/GDSC IDs from `qcom,sm6375-gcc.h`; external parent clocks are consumed by index rather than firmware name.
- Regmap: 32-bit registers, 4-byte stride, 32-bit values, fast I/O, `max_register = 0xc7000`.
- Reset framework: reset IDs are handled by `gcc_sm6375_resets[]`.
- Power domains: GDSC IDs are handled by `gcc_sm6375_gdscs[]`, including votable and hardware-controlled domains.
- Platform lifecycle: `MODULE_DEVICE_TABLE()`, `subsys_initcall()`, platform driver probe/remove registration, and module exit.

## Risks And Edge Cases

- Probe-time PLL configuration is hardware-critical. Incorrect Lucid/Zonda config fields can destabilize camera, video, or other high-frequency domains.
- Parent data for `gcc_parent_data_14` maps both GPLL11 odd and even selector entries to `&gpll11.clkr.hw`; this mirrors the local descriptor but is easy to misread when modifying video parent tables.
- Many camera RCGs use shared ops and shared GPLL sources. Camera clock changes can affect multiple TFE/CSID/OPE/MCLK paths if parent propagation or shared-rate assumptions are wrong.
- Always-on branch votes are not optional policy. Removing camera XO, display XO, or CPUSS GNOC force-enables can break dependent blocks that assume these roots survive unused-clock cleanup.
- USB GDSC retention semantics are deliberate. Moving to off/on before USB suspend/runtime PM is correct can cause USB resume or PHY failures.
- Vcodec0 uses hardware-controlled GDSC behavior; software-only assumptions in tests or consumers may observe delayed or autonomous transitions.
- QUP DFS coverage must stay aligned with the QUP RCGs exported in the clock table. Missing DFS registration can cause serial-engine performance or rate-switching issues.
- Reset registers are dense around multimedia blocks. Wrong offsets can reset adjacent CAMSS, Venus, Vcodec, UFS, GPU, or QUP hardware.

## Test Signals

- Build with SM6375 GCC enabled and check for binding ID, PLL ops, and initializer warnings.
- Boot with `compatible = "qcom,sm6375-gcc"` and verify successful probe after PLL configuration but before camera, display, video, UFS, USB, QUP, SDCC, GPU, and NPU consumers complete.
- Inspect `clk_summary` for `gpll8`, `gpll9`, `gpll10`, `gpll11`, camera TFE/CSID/MCLK/OPE roots, `gcc_video_venus_clk_src`, QUPv3 clocks, UFS, USB, and the always-on camera/display XO and CPUSS GNOC branches.
- Exercise camera capture paths using multiple CSIPHY/TFE/CSID/MCLK combinations, video encode/decode/Venus paths, display, GPU/NPU fabrics, UFS, USB3, SDCC1/2, and QUP UART/SPI/I2C.
- Verify GDSC behavior for CAMSS, Venus, Vcodec, USB, UFS, and MMU TBU vote domains through runtime PM and power-domain debugfs.
- Safely test reset lines for QUP wrappers, PDM, GPU, SDCC, UFS, USB PHY/controller, CAMSS, Venus, Vcodec, and MMSS/video-interface blocks.
