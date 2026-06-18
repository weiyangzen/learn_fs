## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx31.c

### Purpose
`clk-imx31.c` registers i.MX31 CCM clocks for PLL roots, MCU/AHB/HSP/IPG buses, peripheral mux/dividers, and gate2-style peripheral gates.

### Important APIs, Types, And Functions
`_mx31_clocks_init()` creates the clock tree from a mapped base and reference frequency. `mx31_clocks_init_dt()` finds the 26 MHz oscillator fixed-clock override, maps CCM, and publishes the provider.

### Control Flow
Init creates fixed roots, MPLL/SPLL/UPLL, muxes for MCU/peripheral/CSI/FIR paths, dividers for bus and peripheral outputs, many gate2 clocks, checks the array, sets CSI parent to UPLL, enables EMI and IIM temporarily for revision detection, and then disables IIM.

### State, Persistence, And Dependencies
State is static clock array/provider plus mapped CCM registers. Hardware state persists in CCMR, PDR, PLL, CGR, and PMCR registers. Dependencies include i.MX PLLv1/gate2 helpers and revision code.

### Integration Points
Provides clocks for SDHC, GPT, EPIT, IIM, ATA, SDMA, SPI, RNG, UARTs, SSI, I2C, CSI, RTC, USB, IPU, EMI, RTIC, and FIRI.

### Risks
Mapping failure calls `panic()`. Initial parent changes and temporary IIM enable modify bootloader state. Gate2 fields assume two-bit CGR semantics. Provider registration errors are ignored.

### Test Signals
Boot with default and DT-provided oscillator rates, verify CSI parent, silicon revision detection, EMI enabled state, and peripheral driver probes.
