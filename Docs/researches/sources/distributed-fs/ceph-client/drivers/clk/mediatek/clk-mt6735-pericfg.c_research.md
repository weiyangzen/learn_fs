<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-pericfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-pericfg.c

### Purpose
This driver registers MT6735 peripheral gates and a two-bank peripheral reset controller.

### Important APIs, Types, And Functions
It defines `pericfg_gates[]`, `pericfg_rst_bank_ofs[]`, `pericfg_rst_idx_map[]`, `pericfg_resets`, `pericfg_clks`, and a simple driver for `mediatek,mt6735-pericfg`.

### Control Flow, State, And Persistence
Simple probe registers peripheral gate clocks and reset controller. Gate state persists in PERI PDN registers; resets persist in `PERI_GLOBALCON_RST0/RST1` and are exposed through the index map.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on UART/I2C/SPI/MSDC/USB/PWM consumers, DT reset bindings, and the common reset layer. Risks include reset-map mistakes, disabling active serial/storage clocks, and parent mux name mismatches. Test signals include peripheral enumeration, reset toggles, serial console stability, and simple remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-pericfg.c -->
