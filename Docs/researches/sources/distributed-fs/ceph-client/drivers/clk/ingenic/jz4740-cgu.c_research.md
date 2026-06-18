# sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4740-cgu.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4740-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4740-cgu.c

### Purpose
`jz4740-cgu.c` describes the CGU clocks for Ingenic JZ4740-compatible SoCs. It provides the external roots, PLL, PLL-half divider, CPU/HCLK/PCLK/MCLK clocks, LCD/I2S/SPI/MMC/UHC/UDC functional clocks, and gate-only peripheral clocks.

### Important APIs, Types, And Functions
Important definitions include CGU register offsets, PLL control bit constants, divider tables, `jz4740_cgu_clocks[]`, and `jz4740_cgu_init()`. The table uses `CLK_IS_CRITICAL` for CPU and memory clocks and expresses the UDC gate with clear-to-gate polarity through the SCR register.

### Control Flow, State, And Persistence
The OF declaration for `ingenic,jz4740-cgu` initializes the CGU early, registers table entries in order, and installs the generic Ingenic syscore PM hook. Clock control flow after boot is generic: the common CGU ops calculate PLL rate, apply divider table values, update mux parents, and gate peripherals based on table fields.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the JZ4740 clock binding, external `ext` and `rtc` clocks, common CGU code, and consumers such as LCD, MMC, USB, UART, DMA, ADC, I2C, AIC, and TCU drivers. Risks include critical-clock flag omissions, UDC gate polarity mistakes, unused register constants, and mismatches between CPCCR divider tables and hardware. Test signals include JZ4740 boot, clock summary rates, USB UDC operation, LCD pixel clock changes, MMC clocking, and unused-clock cleanup preserving critical roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4740-cgu.c -->
