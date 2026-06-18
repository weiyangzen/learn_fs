# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a33.c

## Purpose

This is the Allwinner A33 main CCU provider. It is close to the A23 driver but adds A33-specific clocks such as `pll-ddr1`, a `pll-ddr` mux, SAT/SS gates, `dram` as an explicit critical clock, `ac-dig-4x`, and A33-specific reset coverage.

## Important APIs, types, and functions

The major objects are `pll_cpux_clk`, `pll_audio_base_clk`, PLL/video/VE/DDR/peripheral/GPU/MIPI/HSIC/DE clocks, `pll_ddr1_clk`, `pll_ddr_clk`, `sun8i_a33_ccu_clks`, `sun8i_a33_hw_clks`, `sun8i_a33_ccu_resets`, and `sun8i_a33_ccu_desc`. `sun8i_a33_ccu_probe()` is the platform probe, matched by `allwinner,sun8i-a33-ccu`. CPU rate-change helpers are `sun8i_a33_pll_cpu_nb` and `sun8i_a33_cpu_nb`.

## Control flow, state, and persistence

Probe maps registers, forces audio PLL 1x divider to 1, forces PLL-MIPI to MIPI mode, registers the CCU, then registers notifiers to gate/ungate PLL CPU and reparent CPUX to the 24 MHz oscillator during PLL rate changes. Hardware register state and CCF/reset registrations are the only state.

## Dependencies and integration points

The driver depends on the shared A23/A33 header and sunxi-ng CCU primitives. Consumers include CPU/cpufreq, DRAM/MBUS, LCD/DSI/CSI/display engine, VE/GPU, SS crypto/security, NAND/MMC/SPI, USB, I2S/codec, I2C/UART, and reset-controller clients.

## Risks and test signals

Risks include CPU transition notifier correctness, PLL DDR parent switching, critical DRAM/MBUS flags, and mode-forcing writes for audio/MIPI. Test with cpufreq stress, suspend/resume, DRAM-heavy workloads, display/camera/USB/audio paths, and reset assertions for the additional SS/SAT blocks.
