## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx27.c

### Purpose
`clk-imx27.c` registers i.MX27 CCM clocks, accounting for silicon revision differences in AHB/IPG/CPU divider fields.

### Important APIs, Types, And Functions
`_mx27_clocks_init()` builds the clock tree from an external reference frequency. `mx27_clocks_init_dt()` discovers the oscillator fixed-clock frequency, maps CCM, calls the initializer, and adds the OF provider.

### Control Flow
Init creates roots, FPM, oscillator gate, PLL selections, MPLL/SPLL, revision-dependent bus dividers, peripheral dividers, VPU/USB/CPU/CLKO/SSI muxes, and extensive IPG/AHB/peripheral gates. It checks clocks, registers CPU clkdev, enables EMI AHB, registers UART clocks, and prints revision.

### State, Persistence, And Dependencies
State is static clock array and CCM base. Register state persists in CSCR, PLL, PCDR, PCCR, and CCSR. Dependencies include OF fixed-clock lookup, i.MX revision helpers, PLLv1 helper, and `dt-bindings/clock/imx27-clock.h`.

### Integration Points
Consumers include CPU clock code, timers, UARTs, USB, FEC, VPU, LCDC, DMA, storage, SPI, I2C, and watchdog.

### Risks
Revision-specific bitfield handling is critical. Defaulting to 26 MHz when no oscillator property is found can be wrong for custom boards. `clk_prepare_enable()`/provider registration errors are not checked.

### Test Signals
Test rev <2.0 and >=2.0 hardware, oscillator-frequency override, CPU clkdev registration, EMI gate state, and peripheral probe coverage.
