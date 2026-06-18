# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-v3s.c

## Purpose
This is the sunxi-ng CCU provider for Allwinner V3 and V3s SoCs. It describes PLLs, CPU/AXI/AHB/APB roots, bus gates, MMC clocks and phases, USB, DRAM, display, CSI, VE, audio, MBUS, and reset lines, then registers the block as a CCF and reset-controller provider.

## Important APIs, Types, And Functions
Important descriptors include `pll_cpu_clk`, SDM-backed `pll_audio_base_clk`, fractional `pll_video_clk`, `pll_ve_clk`, `pll_isp_clk`, DDR and peripheral PLLs, CPU/AHB/APB mux/dividers, many `SUNXI_CCU_GATE` bus clocks, `SUNXI_CCU_MP_WITH_MUX_GATE` MMC/SPI/CE module clocks, `SUNXI_CCU_PHASE` MMC sample/output clocks, onecell tables for V3 and V3s, reset maps, and `sun8i_v3s_ccu_probe()`.

## Control Flow
Probe selects the descriptor from OF match data, maps MMIO, forces the PLL-audio 1x divider to 1 for SDM operation, forces DE and TCON parents to the video PLL so display units share a parent, then calls `devm_sunxi_ccu_probe()`. Runtime CCF operations are table-driven by the common sunxi-ng helpers.

## State And Persistence
No filesystem state is stored. Boot state consists of probe-time register fixups plus subsequent hardware register changes from clock and reset consumers. CPU, DRAM, and MBUS clocks are marked critical where disabling would destabilize the system.

## Dependencies And Integration Points
The driver depends on sunxi-ng helpers, V3s clock/reset dt-bindings, Linux platform and OF APIs, and external oscillator parents. It integrates with MMC, CE, SPI, USB host/PHY, EMAC/ePHY, UART/I2C, codec/I2S, display/TCON/DE, CSI/MIPI CSI, VE, DRAM, and MBUS consumers.

## Risks
Descriptor correctness is the main risk: V3 and V3s share most hardware but expose different I2S/reset IDs. Audio SDM uses fixed supported rates and forced dividers. DE/TCON parent fixups are required for display operation. Mistyped bit positions can affect adjacent bus gates or reset lines.

## Test Signals
Test by booting V3 and V3s DTs, checking probe success and clock-summary entries, validating CPU rate changes, audio 22.5792/24.576 MHz paths, MMC phases and transfers, USB host/PHY, EMAC/ePHY, UART/I2C/SPI, display pipeline, CSI, VE, and reset-controller toggles.
