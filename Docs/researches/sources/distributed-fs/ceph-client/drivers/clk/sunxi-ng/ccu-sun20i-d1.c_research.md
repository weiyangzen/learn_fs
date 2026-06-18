# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1.c

## Purpose
`ccu-sun20i-d1.c` is the main CCU provider for Allwinner D1/R528/T113 SoCs. It models the central clock tree and reset controller for CPU/RISC-V, PLLs, fabric buses, DRAM/MBUS, storage, serial buses, Ethernet, audio, USB, display, camera, DSP, RISC-V subsystem, and fanout clocks.

The file is primarily static hardware descriptor data, with a probe routine that normalizes several PLL/test divider fields before registering the clock provider.

## Important APIs, Types, And Functions
The driver uses the sunxi-ng descriptor macros and clock types extensively:

- PLLs use `struct ccu_mult`, `struct ccu_nkmp`, `struct ccu_nm`, SDM tables, and fixed-factor children. Covered PLLs include CPUX, DDR0, PERIPH0 4x/2x/800M/div3, VIDEO0/1 4x/2x/1x, VE, AUDIO0 4x/2x/1x with sigma-delta, and AUDIO1.
- Bus and module clocks use `SUNXI_CCU_MUX`, `SUNXI_CCU_M`, `SUNXI_CCU_MP_*`, `SUNXI_CCU_M_*`, `SUNXI_CCU_DIV_TABLE_*`, and gate macros with firmware parent data or direct hardware parent arrays.
- `sun20i_d1_ccu_clks[]` collects all `struct ccu_common` descriptors, while `sun20i_d1_hw_clks` maps public binding IDs to `struct clk_hw` pointers.
- `sun20i_d1_ccu_resets[]` maps reset binding IDs to register/bit pairs for MBUS, display, CE, VE, DMA, message boxes, spinlock, timers, PWM, DRAM, MMC, UART, I2C, CAN, SPI, EMAC, audio, USB, display/camera, DSP, and RISC-V CFG.
- `sun20i_d1_ccu_probe()` maps MMIO, sets PLL enable/LDO/lock bits, forces undocumented/test dividers to modeled values, registers the CCU, and installs a CPU/RISC-V mux notifier.

## Control Flow
Probe matches `allwinner,sun20i-d1-ccu`, maps the MMIO resource, then performs hardware normalization before descriptor registration. It enables enable, LDO, and lock bits on all modeled PLLs; forces CPUX factor M to zero; clears video PLL output test divider bits; enforces `m1 = 0, m0 = 0` for PLL_AUDIO0; and forces fanout-27M factor N to zero. After `devm_sunxi_ccu_probe()` succeeds, it registers `sun20i_d1_riscv_nb` so the RISC-V/CPU clock can temporarily reparent to `pll-periph0` during PLL CPUX rate changes.

After registration, generic CCF operations handle rate rounding, parent selection, gate enable/disable, and reset assertion. The descriptor tables define whether a clock is mux-only, divider-only, MP/NM/NKMP, gate-only, fixed-factor, or has postdiv/prediv behavior.

## State And Persistence
Runtime state is entirely in hardware registers and CCF registration objects. Probe mutates persistent-for-boot PLL state by enabling PLL support bits and by clearing test divider fields so the software model matches hardware. Subsequent state includes PLL rates, mux selections, divider values, gate bits, reset bits, and notifier-controlled temporary reparenting during CPU PLL changes.

There is no cross-boot persistence. However, this provider touches CPU, DRAM, MBUS, and PLL state that may have been initialized by firmware, so probe-time changes are part of the platform boot contract.

## Dependencies And Integration Points
The driver depends on `clk-provider.h`, `io.h`, platform/module APIs, shared sunxi-ng clock types, `../clk.h`, and binding IDs from `ccu-sun20i-d1.h`. It imports the `SUNXI_CCU` module namespace and exposes clocks/resets to device-tree consumers through CCF and reset-controller frameworks.

Integration points are broad: CPU/RISC-V DVFS, DRAM and MBUS clients, MMC/SD, UART/I2C/CAN/SPI, Ethernet, IR/LEDC/GPADC/THS, I2S/SPDIF/DMIC/audio codec, USB OHCI/EHCI/OTG and PHY resets, HDMI/MIPI-DSI/TCON/TVE/TVD/LVDS/display pipeline, CSI/camera, DSP, timers, DMA, message boxes, spinlocks, PWM, and fanout clock pins.

## Risks
Descriptor correctness is the dominant risk. Parent arrays mix firmware names, fixed-factor children, and internal hardware pointers; a wrong parent index can yield valid but incorrect rates. PLL comments document hardware test divider fields that are intentionally not modeled; if probe stops forcing those fields, CCF rate calculations can diverge from actual output.

CPU/RISC-V clock switching is sensitive. Removing or misconfiguring the mux notifier can make CPU PLL rate changes glitch the CPU clock. DRAM/MBUS and MMC postdiv clocks require exact divider semantics. USB OHCI parent/predivider behavior and display/audio fractional/SDM clocks require hardware validation because incorrect rates may appear as link, audio, or video quality problems rather than probe failures.

## Test Signals
Basic signals are successful probe of `sun20i-d1-ccu`, expected PLL and module clocks in `clk_summary`, no CCF registration errors, and working reset-controller consumers. CPU PLL rate changes should complete without hangs, with the RISC-V/CPU clock reparenting path active.

Hardware validation should cover CPU/DVFS, DRAM/MBUS consumers, MMC0-2, UART/I2C/CAN/SPI, Ethernet, USB host/device, HDMI/MIPI/TCON display paths, camera/CSI, audio rates for I2S/SPDIF/DMIC/codec, IR/LEDC, thermal/GPADC, DSP/RISC-V subsystem clocks, and reset assertions for representative peripherals.
