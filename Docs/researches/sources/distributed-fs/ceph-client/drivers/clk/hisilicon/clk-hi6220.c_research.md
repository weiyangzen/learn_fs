## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi6220.c

### Purpose
`clk-hi6220.c` registers the static Hi6220 clock tree for AO, SYS, MEDIA, PMCTRL, and ACPU SCTRL domains. It maps hardware clocks into CCF objects using shared Hisilicon fixed-rate, fixed-factor, separated-gate, mux, gate, and Hi6220-specific divider helpers.

### Important APIs, Types, And Functions
The file defines clock tables for AO fixed sources, SYS MMC/UART/HIFI paths, MEDIA display/ISP/GPU paths, PMCTRL PLL gates and DDR dividers, and ACPU separated gates. Init entry points are `hi6220_clk_ao_init()`, `hi6220_clk_sys_init()`, `hi6220_clk_media_init()`, `hi6220_clk_power_init()`, and `hi6220_clk_acpu_init()`.

### Control Flow
Each `CLK_OF_DECLARE` or `CLK_OF_DECLARE_DRIVER` entry maps its controller node, allocates a onecell provider with `hisi_clk_init()`, and registers the relevant tables. SYS and MEDIA clocks register separated gates first, then muxes and Hi6220 dividers. PMCTRL uses normal gates plus Hi6220 dividers.

### State, Persistence, And Dependencies
State is CCF registration state plus memory-mapped clock registers. The topology depends on `dt-bindings/clock/hi6220-clock.h`, shared Hisilicon helper semantics, and the custom divider write-mask behavior in `clkdivider-hi6220.c`.

### Integration Points
Device-tree consumers use HI6220 clock IDs across multiple controllers. Several gates are marked `CLK_IGNORE_UNUSED` or `CLK_IS_CRITICAL` to protect early console, timers, DAPB, and trace-related clocks.

### Risks
The tree spans several independent providers with parent names crossing domains, so init ordering and parent availability matter. Some MMC functional and sample clocks share the same gate bit, which requires consumers to coordinate enable counts through CCF. There is no explicit teardown for the early OF-declared providers.

### Test Signals
Boot Hi6220 with all clock controller nodes present, inspect clock summary for no orphaned parents, test MMC0/1/2 rate and sample parent switching, UART/I2C/SPI enablement, HIFI/MEDIA clocks, and PMCTRL DDR/PLL gate visibility.
