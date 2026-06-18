# sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4780-cgu.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4780-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4780-cgu.c

### Purpose
`jz4780-cgu.c` defines the clock topology for the Ingenic JZ4780, including APLL/MPLL/EPLL/VPLL, CPU and bus muxes/dividers, DDR and multimedia clocks, USB OTG PHY rate/control, and a custom clock for bringing up the second CPU core.

### Important APIs, Types, And Functions
Custom operations include `jz4780_otg_phy_recalc_rate()`, `determine_rate()`, `set_rate()`, OTG PHY enable/disable/is_enabled, and `jz4780_core1_enable()`. The table `jz4780_cgu_clocks[]` uses `DEF_PLL()` for PLLs and defines mux/div/gate clocks for DDR, VPU, I2S, LCD, MSC, UHC, SSI, CIM, PCM, GPU, HDMI, BCH, RTC, and many gate-only peripherals.

### Control Flow, State, And Persistence
Initialization maps and registers the common CGU, then registers PM syscore. The OTG PHY custom clock constrains refclk rates to 12/19.2/24/48 MHz and updates USBPCR1 under the CGU lock; enable/disable toggles OPCR and USBPCR bits. `jz4780_core1_enable()` clears secondary CPU power-down/gate bits under lock, then polls LCR for power-up completion with timeout.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on the JZ4780 DT binding, common CGU code, common clock framework, USB PHY programming rules, and SMP/CPU bring-up users of the `core1` clock. Risks include custom USB writes racing with other PHY users, timeout handling for secondary CPU power-up, critical DDR/L2/CPU flags being mandatory, and skipped parent slots requiring correct index translation. Test signals include USB PHY refclk rate changes, CPU1 enable during SMP boot, DDR clock stability, display/audio/storage rate changes, and unused-clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4780-cgu.c -->
