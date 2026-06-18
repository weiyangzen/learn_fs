# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sa8775p.c

## Purpose
Implements the Qualcomm Global Clock Controller driver for SA8775P. It publishes the SoC's GCC clock tree, resets, and GDSC power domains to the common clock framework and genpd through the qcom clock-controller helpers. The driver covers general-purpose PLLs, QUPv3 serial engines, SDCC, UFS PHY and UFS card controllers, USB2/USB3 primary and secondary blocks, PCIe0/PCIe1, EMAC0/EMAC1, GPU/display/camera/video interconnect clocks, throttle clocks, and assorted clock reference enables.

## Important APIs, Types, And Functions
- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` define Lucid EVO GPLL0, GPLL1, GPLL4, GPLL5, GPLL7, GPLL9, and GPLL0 even post-divider outputs, all ultimately parented by the DT `bi_tcxo` clock.
- `struct parent_map` plus `struct clk_parent_data` arrays encode mux values for RCGs and pipe/symbol muxes. The first enum must match the DT binding order, while the second enum names internal parent IDs.
- `struct clk_rcg2` entries and `struct freq_tbl` tables implement programmable rate sources for EMAC, GP clocks, PCIe auxiliary/rchng clocks, PDM, QUPv3 serial ports, SDCC1, TSCSS, UFS card/PHY, USB, and QSPI-style QUPv3 wrap3 clocks.
- `struct clk_regmap_mux`, `struct clk_regmap_phy_mux`, and `struct clk_regmap_div` represent hardware muxes/dividers for PCIe pipe/aux clocks, UFS symbol clocks, USB PHY pipe clocks, QUPv3 wrap3 divider, and UTMI post-dividers.
- `struct clk_branch` gates the leaf clocks and carries halt policy (`BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, `BRANCH_HALT_DELAY`) plus rate propagation flags such as `CLK_SET_RATE_PARENT`.
- `struct gdsc` entries model PCIe, UFS card/PHY, USB, and EMAC power domains; PCIe domains use votable/retain/poll flags.
- `gcc_sa8775p_clocks`, `gcc_sa8775p_resets`, `gcc_sa8775p_gdscs`, and `gcc_sa8775p_desc` are the exported descriptor tables consumed by `qcom_cc_really_probe()`.
- `gcc_sa8775p_probe()` maps MMIO with `qcom_cc_map()`, registers DFS-capable RCGs, forces required always-on clocks, enables FORCE_MEM_CORE_ON for the UFS PHY ICE core clock, then registers the clock controller.

## Control Flow
Module loading is via `core_initcall(gcc_sa8775p_init)`, which registers the platform driver for compatible `qcom,sa8775p-gcc`. Probe maps the GCC register space using the descriptor's regmap config (`32-bit` registers, stride `4`, max register `0xc7018`, `fast_io`). If the map succeeds, the driver registers dynamic frequency scaling metadata for the QUPv3 serial clock sources, sets a fixed group of camera, display, GPU, and video AHB/XO clocks on with direct branch enable writes, marks the UFS PHY ICE core branch for forced memory-core retention, and finally calls `qcom_cc_really_probe()` to publish clocks, resets, and power domains.

Runtime clock control after probe is delegated to the common qcom clock ops. Consumers request IDs from `dt-bindings/clock/qcom,sa8775p-gcc.h`; the framework then uses the registered regmap-backed clock objects to set parent muxes, program RCG M/N/D values from frequency tables, toggle branch enable bits, observe halt bits, assert resets, or vote GDSCs.

## State And Persistence
The driver is statically described; persistent state lives in GCC hardware registers and in framework objects registered at probe. PLL enable state is controlled through a shared enable register at `0x4b028`, while individual RCGs, branches, muxes, and dividers use their declared offsets. The explicit always-on branch enables persist until reset or firmware/kernel reprogramming. DFS registration persists in the qcom clock framework for QUPv3 clocks. GDSC state is backed by GDSCR registers and is reference-counted by genpd users; reset state is driven by the reset-controller API and hardware reset registers.

## Dependencies And Integration Points
Depends on Linux common clock framework headers, platform-driver/OF matching, regmap, qcom clock primitives (`clk-alpha-pll`, `clk-branch`, `clk-rcg`, `clk-regmap*`, `clk-regmap-phy-mux`), qcom reset/GDSC helpers, and the SA8775P GCC DT binding. It integrates with device-tree consumers for UART/SPI/I2C via QUPv3, SDHCI, UFS, USB, PCIe, Ethernet, GPU, camera/display/video, and power-domain users. The source includes `common.h`, so probe relies on qcom CC mapping/registration helpers rather than open-coding platform resource handling.

## Risks And Edge Cases
The DT input-clock enum is explicitly required to match the binding order; any mismatch silently corrupts parent lookup for external clocks such as TCXO, sleep, UFS symbols, USB/PCIe pipes, and RXC references. Large descriptor tables are index-sensitive against the binding IDs; omitted or shifted entries break consumers by ID. Many branches use voted or skipped halt checks, so a wrong halt policy can hang enable/disable paths or mask a dead clock. Always-on direct register writes are not represented as normal consumers and must remain consistent with hardware requirements for MM/GPU/video access. The UFS ICE forced memory-core setting is a SoC quirk; dropping it can create data-path failures during low-power transitions.

## Test Signals
Useful validation signals are successful probe on `qcom,sa8775p-gcc`, all expected clock/debugfs IDs present, QUPv3 serial rates selectable through DFS, SDCC/UFS/USB/PCIe/EMAC drivers able to enable their clocks and deassert resets, GDSC power domains transitioning without timeout, and suspend/resume retaining the explicitly protected MM/GPU/video/UFS paths. Static test signals include binding index consistency, no duplicate clock/reset IDs, and build coverage for `CONFIG_SA_GCC_8775P` or the relevant qcom GCC Kconfig option.
