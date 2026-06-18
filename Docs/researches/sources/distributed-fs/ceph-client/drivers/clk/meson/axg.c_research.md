# sources/distributed-fs/ceph-client/drivers/clk/meson/axg.c

Purpose: `axg.c` is the main Amlogic AXG clock-controller driver for the HHI domain. It exposes PLLs, MPLLs, fixed-clock dividers, PCIe reference clocks, clk81, SD/eMMC clocks, VPU/VAPB clocks, video clocks, measurement clocks, a general-purpose clock, and many EE/AO peripheral gates.

Important APIs and types: the file is almost entirely static descriptors using `struct clk_regmap`, `struct clk_fixed_factor`, Meson PLL data, MPLL data, mux/divider/gate data, and `MESON_PCLK` gates. It provides `axg_clkc_data` and a platform driver named `axg-clkc` that uses `meson_clkc_syscon_probe`.

Control flow: probe is delegated through the OF match for `"amlogic,axg-clkc"`. The clock tree starts with fixed, sys, gp0, hifi, and PCIe PLL descriptors; derives fclk div2/div3/div4/div5/div7; creates MPLL0-3 from an MPLL predivider; builds PCIe mux/ref/CML gates; creates the critical `clk81` tree; defines SD/eMMC mux/div/gates; creates dual VPU and VAPB branches with mux selection; builds video clock and video2 paths with fixed post-dividers and ENCL selection; defines VDIN measurement and generic clock paths; and finally registers large groups of pclk gates for EE and AO domains.

State and persistence: runtime state is in HHI syscon registers and CCF registrations. Some clocks are marked critical or ignore-unused to preserve firmware or display state, especially fclk dividers, clk81, VPU/VAPB, and video gates. No persistent storage is used.

Dependencies and integration points: the file depends on Meson `clk-regmap`, `clk-pll`, `clk-mpll`, and `meson-clkc-utils`, with IDs from `axg-clkc.h`. It consumes firmware parent `xtal` and provides core clocks used by AXG peripheral, storage, PCIe, display, audio, and AO subsystems.

Risks: clock IDs in `axg_hw_clks[]` must match the binding exactly. PLL init tables are hardware-sensitive. Several parent value tables skip reserved hardware values, so selector programming must preserve those assumptions. `CLK_IGNORE_UNUSED` can hide ownership bugs but protects bootloader-enabled display paths. Shared syscon registers mean mux/div/gate definitions must not overlap incorrectly.

Test signals: boot on AXG and inspect `clk_summary`, especially PLL lock/rates, clk81, fclk divisors, SD/eMMC rates, PCIe ref, VPU/VAPB, and video clocks. Exercise MMC, PCIe, display, VDIN, audio parent clocks, USB, Ethernet, UART, SPI, and AO consumers. Test module removal or probe failure if built as a module.
