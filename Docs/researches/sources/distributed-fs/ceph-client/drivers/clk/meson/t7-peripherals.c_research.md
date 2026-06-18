# sources/distributed-fs/ceph-client/drivers/clk/meson/t7-peripherals.c

Purpose: This file describes the Amlogic T7 peripheral clock controller. It registers RTC/CEC dualdiv clocks, smartcard, DSP, fixed 12/24/25 MHz outputs, Anakin, MIPI CSI/ISP, transport stream, Mali, Ethernet RMII/125 MHz, SD/eMMC, six SPICC clocks, SARADC, normal and AO PWM clocks, and a large set of system peripheral bus gates.

Important APIs, types, and functions: The core table is `t7_peripherals_hw_clks[]` indexed by `amlogic,t7-peripherals-clkc.h` IDs. `T7_COMP_SEL`, `T7_COMP_DIV`, `T7_COMP_GATE`, and `T7_SYS_PCLK` generate repeated mux/divider/gate and pclk objects. The driver exposes `t7_peripherals_data` through `meson_clkc_mmio_probe` for compatible `amlogic,t7-peripherals-clkc`.

Control flow: Probe maps the controller and registers every `clk_hw`. After registration, CCF operations modify register fields through generic Meson regmap mux/divider/gate and dualdiv helpers. Glitch-sensitive dual input paths for DSP, Anakin, MIPI CSI PHY, and Mali use two sibling mux/divider/gate chains and a final selector so CCF can switch between prepared paths.

State and persistence behavior: The driver has no private dynamic state beyond CCF objects. Hardware state is the MMIO clock register block. Most system gates are normal gates, while `sys_gic` is marked `CLK_IS_CRITICAL` because disabling the GIC clock would break interrupt handling. Some muxes use `CLK_SET_RATE_NO_REPARENT` where external pins or fixed routing should not be automatically changed.

Dependencies and integration points: It depends on `clk-dualdiv`, `clk-regmap`, `meson-clkc-utils`, and parent names exported by T7 PLL/fixed controllers such as `xtal`, `sys`, `fix`, `fdiv*`, `gp0`, `gp1`, `hifi`, `mpll*`, and `vid_pll0`. Downstream consumers include GPU, DSP, camera, ISP, Ethernet, storage, SPI, PWM, ADC, CEC, and bus devices.

Risks and edge cases: The main risks are dt-binding index mismatches, wrong parent value tables for sparse hardware muxes, and accidental gating of infrastructure clocks. Dualdiv tables assume exact 32 kHz style ratios. Test signals include boot probe, clk summary coverage for every ID, GIC clock remaining enabled, Ethernet RMII parent/rate tests, storage/SPI/PWM functional tests, and rate switching on Mali/DSP/MIPI dual-path clocks.
