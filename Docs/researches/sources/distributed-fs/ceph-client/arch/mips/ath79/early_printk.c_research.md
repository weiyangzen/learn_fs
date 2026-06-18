## sources/distributed-fs/ceph-client/arch/mips/ath79/early_printk.c

Purpose: implements early `prom_putchar()` for ATH79 SoCs, selecting between classic 16550-style UART and AR933x UART register layouts and enabling UART pinmux bits where supported.

Important APIs and functions: `prom_putchar()` lazily initializes `_prom_putchar`. `prom_putchar_ar71xx()` writes to `AR71XX_UART_BASE` using standard UART registers with 4-byte spacing. `prom_putchar_ar933x()` writes to `AR933X_UART_BASE` using `AR933X_UART_DATA_REG`. `prom_enable_uart()` sets the GPIO function UART enable bit based on revision ID. `prom_putchar_init()` reads `AR71XX_RESET_REG_REV_ID` and selects the backend or a dummy function.

Control flow: first character read maps reset base through KSEG1, decodes major revision, selects AR71xx-style backend for most SoCs, AR933x backend for AR9330/9331, dummy for unknown, enables UART pinmux where implemented, then subsequent calls go directly through `_prom_putchar`.

State and persistence: static function pointer caches the selected output backend. GPIO function writes change pinmux state until reset or later configuration.

Dependencies and integration: depends on early printk config, raw MMIO, serial register constants, ATH79 revision macros, AR933x UART definitions, and the standard MIPS `prom_putchar()` early console path.

Risks: QCA953x/QCA955x/QCA956x use the AR71xx UART backend but `prom_enable_uart()` only handles older families and AR933x; pinmux may need firmware preconfiguration on newer chips. Busy waits have no timeout. Unknown SoC IDs silently discard early output.

Test signals: early boot text should appear before normal console setup on each supported UART type. AR933x should use its special TX CSR path, while other SoCs should use standard LSR/TX registers.
