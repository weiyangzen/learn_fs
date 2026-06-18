# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a23.c

## Purpose

This is the main CCU provider for the Allwinner A23. It declares CPU, audio, video, VE, DDR, peripheral, GPU, MIPI, HSIC, DE PLLs, CPU/AHB/APB buses, bus gates, MMC/NAND/SPI/I2S/USB clocks, display/camera/media clocks, DRAM gates, MBUS, GPU, and reset lines.

## Important APIs, types, and functions

Important data includes `sun8i_a23_ccu_clks`, fixed-factor audio/peripheral/video clocks, `sun8i_a23_hw_clks`, `sun8i_a23_ccu_resets`, and `sun8i_a23_ccu_desc`. The entry point is `sun8i_a23_ccu_probe()`, bound to `allwinner,sun8i-a23-ccu`.

## Control flow, state, and persistence

Probe maps MMIO, forces the PLL-Audio-1x divider field to 1, clears the PLL-MIPI HDMI-mode bit so the driver can model only MIPI mode, then delegates registration to `devm_sunxi_ccu_probe()`. The registered state is devm-managed CCF/reset objects backed by hardware CCU registers; no software persistence exists.

## Dependencies and integration points

The driver uses the generic sunxi-ng CCU helpers plus the shared A23/A33 binding header. It provides clocks for CPUX, bus fabric, MMC phase tuning, NAND/SPI/I2C/UART, USB HSIC/OHCI/PHY, codec/I2S, MIPI DSI/DPHY, LCD, CSI, VE, display engine front/back ends, DRC, GPU, MBUS, and reset consumers.

## Risks and test signals

Risks include the intentionally simplified audio PLL divider, unsupported MIPI HDMI mode, TODO parent uncertainty for some USB clocks, and mux table encodings for display/camera clocks. Test with A23 boot, `clk_summary`, MMC tuning, display/MIPI, camera, USB HSIC/OHCI, audio rates, and reset-driven peripheral probes.
