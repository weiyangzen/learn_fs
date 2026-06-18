# sources/distributed-fs/ceph-client/drivers/clk/spear/spear1340_clock.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear1340_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/spear1340_clock.c

Purpose: initializes the SPEAr1340 clock tree from a mapped MISC register base, registering oscillators, VCO/PLL roots, system/AMBA synthesizers, bus clocks, peripheral synthesizers/gates, and clkdev aliases for SPEAr1340 devices.

Important APIs and control flow: `spear1340_clk_init()` registers fixed oscillators and pad clocks, RTC gate, VCO parent muxes, PLL1-PLL4 through `clk_register_vco_pll()`, fixed PLL5/PLL6, VCO divided clocks, thermal/DDR clocks, `sys_syn_clk`, `amba_syn_clk`, `sys_mclk`, CPU/cpu_div3/watchdog/TWD, AHB mux, APB fixed factor, GPT mux/gates, UART0/1 auxiliary synthesizers and mux/gates, SDHCI, CFXD, C3, GMAC PHY mux/synth, CLCD fractional path, I2S paths, AHB/APB peripheral gates, generic fractional synthesizers, Mali, CEC, SPDIF in/out, ACP, PLGPIO, video, camera, and PWM gates. It uses hard-coded clkdev aliases to bind clocks to legacy platform-device names.

State and persistence behavior: hardware state is in SPEAr1340 MISC registers controlling sources, dividers, synthesizers, and gates. Software state is the global `_lock` and manually allocated CCF wrapper objects. Initialization is one-shot and not unwindable.

Dependencies and integration points: depends on valid `misc_base`, local SPEAr synthesizer helpers, standard CCF mux/gate/fixed helpers, and clkdev consumers for serial, SDHCI, CF/XD, C3, Ethernet, CLCD, I2S, I2C, DMA, USB, PCIe/SATA, ADC, SPI, GPIO, keyboard, Mali, CEC, SPDIF, video, cameras, and PWM. Rate tables and parent arrays encode SPEAr1340-specific clock-source choices.

Risks and test signals: risks include no per-clock error handling, legacy device-name coupling, shared-register concurrency depending on one spinlock, helper failure NULLs being registered into clkdev if unchecked, table-order assumptions, VCO/PLL set-rate behavior affecting system clocks, and subtle source differences from SPEAr1310 such as sys/AMBA synthesizers and PERIP3 gates. Test signals include successful boot with expected CPU/AHB/APB rates, working UART0/1, SDHCI, GMAC, CLCD, I2S/SPDIF, USB, PCIe/SATA, DMA, GPIO, Mali/video/camera/PWM clocks, and debugfs/clk summaries matching the SPEAr1340 reference topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear1340_clock.c -->
