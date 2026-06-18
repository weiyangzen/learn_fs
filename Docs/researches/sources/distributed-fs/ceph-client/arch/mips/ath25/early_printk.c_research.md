## sources/distributed-fs/ceph-client/arch/mips/ath25/early_printk.c

Purpose: implements `prom_putchar()` for ATH25 early printk by writing directly to the family-appropriate UART0 MMIO base.

Important APIs and functions: `prom_putchar(char ch)` lazily selects the UART base from `AR2315_UART0_BASE` or `AR5312_UART0_BASE` using `is_ar2315()`. `prom_uart_rr()` and `prom_uart_wr()` perform 32-bit raw UART register reads/writes with 4-byte register spacing.

Control flow: on first call, `prom_putchar()` caches the KSEG1 UART base. It spins until `UART_LSR_THRE` is set, writes the byte to `UART_TX`, and waits again for transmitter holding register empty.

State and persistence: static cached `base` is runtime-only. It changes no persistent state beyond UART transmit FIFO/registers.

Dependencies and integration: depends on `CONFIG_EARLY_PRINTK`, serial register definitions, ATH25 family detection, and AR2315/AR5312 UART base constants. It integrates with MIPS early printk through the standard `prom_putchar()` symbol.

Risks: if CPU family detection is wrong, writes go to the wrong MMIO address. The busy waits have no timeout, so a disabled or clock-gated UART can hang early output. It assumes MEM32 UART access with regshift 2.

Test signals: characters should appear very early on the serial console before normal 8250 setup. Boot with early printk disabled should omit this object.
