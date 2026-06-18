# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100.c

## Purpose
`ccu-sun50i-a100.c` is the main CCU provider for Allwinner A100. It models the primary SoC clock tree and reset controller, including CPU/AXI/fabric buses, PLLs, DRAM/MBUS, display/G2D/GPU/VE, CE, storage, serial buses, Ethernet, IR/ADC/thermal, audio, USB, display/camera, and crypto-related peripheral gates.

The file is descriptor-heavy and includes a probe routine that programs hardware defaults for PLL lock/enable behavior, PLL_PERIPH1 spread-spectrum/SDM, video/audio test dividers, USB OHCI parent selection, and CPU PLL transition notifiers.

## Important APIs, Types, And Functions
Important descriptor groups include:

- PLLs: CPUX multiplier, DDR0 NKMP, PERIPH0/1 NKMP with fixed postdiv, GPU NKMP, VIDEO0-3 NM with fixed postdiv, VE NKMP, COM NM with sigma-delta, and AUDIO NM with sigma-delta.
- Bus clocks: CPUX mux, AXI, CPUX APB, PSI/AHB1/AHB2, AHB3, APB1/APB2, and MBUS.
- Module and bus gates: DE, G2D, GPU, CE, VE, DMA, message box, spinlock, hstimer, AVS, debug, PSI, PWM, IOMMU, DRAM/MBUS clients, NAND, MMC0-2, UART0-4, I2C0-3, SPI0-2, EMAC, IR RX/TX, GPADC, THS, I2S0-3, SPDIF, DMIC, audio codec, USB OHCI/PHY/bus gates, LRADC, DPSS, MIPI DSI, TCON, LVDS, LEDC, CSI/ISP, and other media/peripheral clocks.
- `sun50i_a100_ccu_clks[]`, `sun50i_a100_hw_clks`, `sun50i_a100_ccu_resets[]`, and `sun50i_a100_ccu_desc` provide the shared CCU registration descriptors.
- `sun50i_a100_ccu_probe()` performs register preparation and registers notifiers.
- `ccu_pll_notifier_register()` and `ccu_mux_notifier_register()` are used to gate/ungate PLL CPU and reparent CPU during rate changes.

## Control Flow
Probe matches `allwinner,sun50i-a100-ccu`, maps MMIO, then normalizes hardware before registration. It enables PLL lock and common enable bits on all listed PLL registers because several PLLs share a power switch and disabling the switch can destabilize neighbors. It writes the PERIPH1 SDM pattern and enables SDM for EMI reasons. It clears video PLL output-divider test bits, enforces the modeled audio PLL m-divider values, and forces OHCI 12 MHz clock muxes to a valid source. After `devm_sunxi_ccu_probe()`, it registers CPU PLL and CPU mux notifiers.

Runtime CCF operations are generic descriptor-driven operations: rates are calculated from factor fields and fixed postdivs, muxes select parents, gates toggle bits, and reset-controller clients assert/deassert reset bits.

## State And Persistence
Current-boot hardware state includes all PLL enable/lock bits, SDM pattern registers, mux selections, dividers, gate bits, and reset bits. Probe explicitly changes PLL and USB register state to make the software model match expected hardware behavior. CPU PLL rate changes involve notifier-managed state transitions: gate/ungate PLL CPU and temporarily reparent CPU to `pll-periph0`.

No state persists through full reset unless firmware reprograms it. However, PLL shared-power behavior makes the driver's decision to leave PLL power enabled part of the runtime stability contract.

## Dependencies And Integration Points
The driver depends on Linux CCF, MMIO and platform APIs, sunxi-ng common clock types, reset support, SDM helpers, and binding IDs from `ccu-sun50i-a100.h`. It imports `SUNXI_CCU`.

Integration points include CPU DVFS, DRAM/MBUS clients, display engine, G2D, GPU, crypto engine, video engine, DMA, timers, PWM, IOMMU, NAND/MMC, UART/I2C/SPI, EMAC, IR, ADC/thermal, audio codec/I2S/SPDIF/DMIC, USB PHY/OHCI/EHCI/OTG, LRADC, DPSS/MIPI/TCON/LVDS, LEDC, CSI/ISP, and reset consumers for all mapped buses and PHYs.

## Risks
PLL handling is the highest-risk area. The probe deliberately enables PLL lock/power behavior and avoids shutting off shared PLL power; changing this can destabilize unrelated clocks. PERIPH1 SDM is enabled for EMI while retaining old rate calculations, so treating SDM as a normal frequency-affecting factor could regress rates. Video and audio test divider bits must remain forced to the modeled values.

CPU rate changes require both PLL and mux notifiers. Parent arrays, fixed postdivs, and reset maps are descriptor-sensitive; small mistakes can break MMC, USB, audio, display, GPU, or DRAM paths. OHCI clock parent handling is explicitly described as not fully understood, so USB validation must be empirical.

## Test Signals
Baseline signals are successful probe of `sun50i-a100-ccu`, expected clocks in `clk_summary`, no registration errors, and reset-controller availability. CPU PLL rate changes should complete without hangs and with notifier activity.

Hardware validation should cover CPU/DVFS, DRAM/MBUS stability, MMC0-2, NAND, UART/I2C/SPI, EMAC, USB host/device including OHCI 12 MHz behavior, audio rates, display/MIPI/TCON/LVDS/DPSS, camera/CSI/ISP, GPU/G2D/VE/CE, thermal/ADC/IR/LEDC, suspend/resume where applicable, and reset assertions for storage, USB PHY, media, and serial buses.
