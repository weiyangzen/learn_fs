# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/clock.c

## Purpose
`clock.c` exposes the Alchemy SoC clock tree to the Linux common clock framework. It models the 12 MHz root crystal, CPU PLL, AUX PLLs, sysbus/peripheral/memory/LR clocks, six frequency generators, and internal clock-source muxes for different Au1xxx/Au1300 CPU variants.

## Important APIs, Types, And Functions
The main init entry is `alchemy_clk_init()` registered with `postcore_initcall()`. `alchemy_set_lpj()` computes `preset_lpj` from the CPU clock for early delay calibration. Clock operation groups include `alchemy_clkops_cpu`, `alchemy_clkops_aux`, `alchemy_clkops_fgenv1`, `alchemy_clkops_fgenv2`, and `alchemy_clkops_csrc`. Private clock types are `struct alchemy_auxpll_clk` and `struct alchemy_fgcs_clk`.

Setup helpers include `alchemy_clk_setup_cpu()`, `alchemy_clk_setup_aux()`, `alchemy_clk_setup_sysbus()`, `alchemy_clk_setup_periph()`, `alchemy_clk_setup_mem()`, `alchemy_clk_setup_lrclk()`, `alchemy_clk_init_fgens()`, and `alchemy_clk_setup_imux()`. Rate helpers include `alchemy_clk_cpu_recalc()`, `alchemy_clk_aux_recalc()`, `alchemy_clk_aux_setr()`, `alchemy_clk_aux_determine_rate()`, `alchemy_calc_div()`, and `alchemy_clk_fgcs_detr()`. Variant-specific internal clock names and aliases map legacy names such as `usbh_clk`, `usbd_clk`, `irda_clk`, and `psc*_intclk`.

## Control Flow
At postcore init, `alchemy_clk_init()` registers the fixed root clock, CPU clock, AUX PLL(s), fixed-factor sysbus/peripheral/memory/LR clocks, then registers six frequency generators and up to six internal clock muxes based on `alchemy_get_cputype()`. Au1300 receives AUXPLL2 and v2 frequency generators with a wider parent mux and flexible divider scale; older variants use v1 generators with CPU/AUXPLL parents and even dividers. Finally, aliases are added for CPU-specific shared clock names.

Clock consumers call common clock APIs. Recalc callbacks read system registers to compute rates. Set-rate and set-parent callbacks update `SYS_AUXPLL`, `SYS_FREQCTRL0/1`, or `SYS_CLKSRC` under spinlocks. Enable/disable callbacks either set explicit enable bits on older hardware or switch muxes to/from disabled states on Au1300 and internal sources.

## State And Persistence
Persistent state is both registered `struct clk` objects and hardware clock register contents. Allocated `clk_hw` wrappers and clkdev aliases remain for the lifetime of the kernel. The file tracks cached parent/enabled state for muxes whose hardware disabled state does not preserve the previous parent. Register writes persist until firmware, suspend/resume, or another clock consumer changes them.

## Dependencies And Integration Points
It depends on common clock framework APIs, clkdev aliases, Alchemy system/memory register helpers, CPU type detection, KSEG1 physical mapping, and clock name macros from Alchemy headers. `setup.c` calls `alchemy_set_lpj()` before normal clock registration is complete. `platform.c` consumes `ALCHEMY_PERIPH_CLK` for UART baud clocking. `power.c` saves/restores the same clock registers across sleep.

## Risks
Clock math and register bitfields are CPU-variant-specific; a wrong CPU type can program invalid mux/divider fields. Some PLL/register behavior is special, such as write-only early Au1000 CPU PLL handling and Au1300 disabled mux encodings. The code uses raw MMIO and spinlocks; missing barriers or lock coverage can corrupt shared clock-control registers. `alchemy_clk_fgcs_detr()` approximates active parent detection with `clk_hw_is_prepared()`, so rate selection can choose suboptimal or unexpectedly mutable parents. Failures during init abort with `-ENODEV`, potentially leaving consumers without required clocks.

## Test Signals
Boot an Alchemy configuration and check `"Alchemy clocktree installed"`. Use clk summary/debugfs, if available, to confirm root, CPU, AUXPLL, sysbus, peripheral, memory, LR, frequency generators, internal clocks, and aliases appear for the selected CPU. Exercise UART probing, USB clocks, PSC clocks, LCD clocks, and PCI clock outputs on relevant variants. Rate-change tests should verify divisor boundaries, AUX PLL min/max multipliers, Au1300 scale-bit behavior, and no register corruption under concurrent clock operations.
