# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80.c

## Purpose
This is the main sunxi-ng CCU provider for Allwinner A80. It describes cluster CPU PLLs and muxes, audio/peripheral/video/GPU/DE/ISP PLLs, bus roots, module clocks, MMC phases, display/media clocks, extensive bus gates, and reset lines.

## Important APIs, Types, And Functions
Important APIs and data include `CCU_SUN9I_LOCK_REG`, CPU PLL `ccu_mult` descriptors with shared lock register bits, `pll_audio_clk`, many `ccu_nkmp` PLL descriptors, CPU/AHB/APB dividers and muxes, module gates/dividers for NAND/MMC/SPI/I2S/display/CSI/GPU/SATA, `sun9i_a80_hw_clks`, `sun9i_a80_ccu_resets`, `sun9i_a80_cpu_pll_fixup()`, and `sun9i_a80_ccu_probe()`.

## Control Flow
Probe maps registers, clears unsupported audio PLL d1/d2 divider usage, fixes both CPU cluster PLLs by clearing P and restoring N when needed, then calls `devm_sunxi_ccu_probe()`. Runtime operation is descriptor-driven through shared sunxi-ng CCF and reset helpers.

## State And Persistence
State is entirely hardware register state for this boot. Probe mutates PLL registers before registration. Critical flags protect CPU muxes, GT bus, CCI400, and SDRAM paths from accidental disable.

## Dependencies And Integration Points
Dependencies include sunxi-ng common helpers, A80 clock/reset dt-bindings, OF/platform APIs, and oscillator parents. Integration spans CPU clusters, interconnect, CCI400, NAND, MMC, TS, security engine, SPI, audio, SDRAM, DE/LCD/MIPI/HDMI/CSI, VE, GPU, SATA, GMAC/USB bus gates, GPIO/PIO, I2C, UART, message box, spinlock, and reset consumers.

## Risks
Risk is high because this file is large and register dense. CPU PLLs are approximated as multipliers with P forced to /1; audio PLL d1/d2 are forcibly cleared; several mux tables use sparse hardware selector values. Duplicate or wrong array entries, bit offsets, or lock bits can silently misroute clocks or reset unrelated blocks.

## Test Signals
Test with A80 boot, successful `allwinner,sun9i-a80-ccu` probe, clock-summary inspection, CPU cluster rate changes, MMC with phase tuning, NAND/SPI/I2C/UART, audio sample rates, display and HDMI, CSI, VE, GPU, SATA/GMAC/USB bus clients, reset-controller operations, and suspend/resume.
