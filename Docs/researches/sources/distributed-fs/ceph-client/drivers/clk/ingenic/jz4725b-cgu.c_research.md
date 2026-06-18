# sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4725b-cgu.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4725b-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4725b-cgu.c

### Purpose
`jz4725b-cgu.c` supplies the table-driven CGU description for the Ingenic JZ4725B SoC, including external roots, one PLL, core/bus dividers, multimedia/storage dividers, gate-only peripherals, RTC selection, and USB device PHY gating.

### Important APIs, Types, And Functions
The important artifacts are register offset definitions, `pll_od_encoding`, CPCCR divider tables, `jz4725b_cgu_clocks[]`, and `jz4725b_cgu_init()`. The clock table uses `ingenic_cgu_clk_info` entries indexed by `dt-bindings/clock/ingenic,jz4725b-cgu.h`. Initialization calls `ingenic_cgu_new()`, `ingenic_cgu_register_clocks()`, and `ingenic_cgu_register_syscore()`.

### Control Flow, State, And Persistence
At boot, `CLK_OF_DECLARE_DRIVER("ingenic,jz4725b-cgu")` invokes initialization, creating one CGU instance and registering all clocks in binding order. Runtime behavior is inherited from `cgu.c`; table metadata controls PLL calculations, divider writes, gate bits, and parent selection. Critical persistence is mostly through generic CGU register state plus the PM syscore low-power-mode hook.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on the JZ4725B dt-binding indices, external `ext` and `osc32k` clocks, and downstream peripherals consuming names like `mmc0`, `lcd`, `tcu`, and `udc_phy`. Risks include comments marking uncertain parents for BCH/TCU, the `ext/512` clock using /256 despite its name, and global `cgu` limiting multiple instances. Test signals include boot with JZ4725B DT, RTC parent selection, USB device PHY enable polarity, MMC/LCD rate programming, and suspend/resume low-power entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4725b-cgu.c -->
