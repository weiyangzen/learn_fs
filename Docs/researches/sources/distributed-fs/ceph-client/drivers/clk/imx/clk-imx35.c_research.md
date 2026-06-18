## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx35.c

### Purpose
`clk-imx35.c` registers the i.MX35 CCM clock tree, deriving ARM/AHB/HSP rates from boot-time divider selections and registering many peripheral gates.

### Important APIs, Types, And Functions
`struct arm_ahb_div` and `clk_consumer` decode consumer mux selections. `_mx35_clocks_init()` maps the CCM fixed physical base, builds roots, PLLs, dividers, muxes, and gate2 clocks. `mx35_clocks_init_dt()` publishes the provider.

### Control Flow
Init reads PDR0 to choose ARM/AHB divider settings, falls back on invalid encodings, creates fixed roots and PLLv1 clocks, derives ARM/HSP/AHB/IPG, registers UART/ESDHC/SPDIF/SSI/USB/NFC/CSI paths, creates gates across CGR0-3, checks clocks, enables a set of critical gates, enables SCC for MMC boot after watchdog reset, registers UART clocks, and prints revision.

### State, Persistence, And Dependencies
State is static `clk[]`, onecell data, and mapped CCM registers. Hardware state persists in CCM PDR, PLL, and CGR registers. Dependencies include i.MX helper clocks, revision APIs, and gate2 semantics.

### Integration Points
Provides clocks for storage, USB OTG, FEC, GPIO, GPT, I2C, IOMUXC, IPU, PWM, RNG, RTC, SDMA, SPBA, SPDIF, SSI, UARTs, watchdog, SCC, and GPU2D.

### Risks
The code overwrites `clk[mpll]` with `"mpll_075"` instead of assigning `mpll_075`, which looks suspicious and may leave the MPLL entry lost while the enum entry for `mpll_075` remains unset. It uses hard-coded physical `ioremap()` rather than the DT node resource. Several critical `clk_prepare_enable()` results are ignored.

### Test Signals
Boot i.MX35, verify all enum clock entries via `imx_check_clocks()`, check ARM/AHB/HSP rates against PDR0 encodings, confirm critical gates stay enabled, and specifically inspect `mpll`/`mpll_075` clock names and IDs.
