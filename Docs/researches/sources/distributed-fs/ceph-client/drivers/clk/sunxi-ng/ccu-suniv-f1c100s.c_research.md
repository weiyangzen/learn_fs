# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-suniv-f1c100s.c

## Purpose
This is the sunxi-ng CCU provider for the Allwinner suniv F1C100s/F1C200s family. It describes CPU, audio, video, VE, DDR, peripheral PLLs, bus roots, module gates, MMC phases, IR/audio/display/camera/video clocks, DRAM gates, resets, and probe registration.

## Important APIs, Types, And Functions
Important descriptors include `pll_cpu_clk`, audio/video/VE/DDR/peripheral PLLs, CPU/AHB/APB mux/dividers, bus gates for DMA/MMC/DRAM/SPI/USB/display/camera/audio/I2C/UART, MMC MP clocks and sample/output phases, audio muxes, IR MP clock, display/TV/CSI/VE/codec/AVS gates, `suniv_hw_clks`, reset maps, `suniv_pll_cpu_nb`, `suniv_cpu_nb`, and `suniv_f1c100s_ccu_probe()`.

## Control Flow
Probe maps the CCU resource, registers all clocks/resets through `devm_sunxi_ccu_probe()`, then registers a CPU mux notifier and PLL notifier so CPU consumers temporarily switch away during PLL CPU rate changes and the PLL is reset after rate changes.

## State And Persistence
State is hardware register state plus notifier registration for the boot. CPU clocking is protected by notifier sequencing; PLL/audio fixed-factor clocks are CCF objects without storage beyond registration.

## Dependencies And Integration Points
Dependencies include sunxi-ng helpers, suniv dt-bindings, platform/OF APIs, and oscillator parents. It integrates with CPUfreq, MMC, SPI, USB OTG, display engine/TCON/TV, CSI/TVD/TVE, audio codec/I2S/SPDIF, IR, I2C/UART, DRAM clients, VE, and reset-controller users.

## Risks
Notifier order is important for safe CPU PLL changes. Display/video mux tables use sparse values. The small SoC has many unrelated gates packed into few registers, so bit mistakes have broad effects. Audio fixed factors are intentionally arranged for supported clocking and should not be renamed casually.

## Test Signals
Test signals include successful F1C100s/F1C200s boot, clk-summary coverage, CPU rate changes without lockups, MMC transfer and phase changes, USB OTG, SPI/I2C/UART, audio playback/capture, display/TV output, camera paths, VE, DRAM gates, and reset toggles.
