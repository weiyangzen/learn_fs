<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk_8250.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk_8250.c

### Purpose
This file provides a `prom_putchar()` backend for early printk using an already-mapped 8250/16550 UART.

### Important APIs, Types, And Functions
It defines setup state `serial8250_base`, `serial8250_reg_shift`, `serial8250_tx_timeout`, public `setup_8250_early_printk_port()`, helpers `serial_in()` and `serial_out()`, and `prom_putchar()`.

### Control Flow
Setup records UART base, register shift, and timeout. `prom_putchar()` returns if no base is configured; otherwise it polls LSR for `UART_LSR_TEMT | UART_LSR_THRE` until timeout and writes the byte if ready.

### State, Persistence, And Dependencies
State is static UART configuration. Dependencies include MMIO `readb/writeb`, serial register constants, and the early console using `prom_putchar()`.

### Integration Points
Platform early setup calls `setup_8250_early_printk_port()`, and `early_printk.c` uses the exported `prom_putchar()` symbol to emit boot messages.

### Risks
The base address must already be usable with `readb/writeb`; no ioremap is performed here. Too-small timeout drops characters, too-large timeout can delay boot on bad UARTs.

### Test Signals
Boot tests with valid and missing UART setup, different register shifts, timeout behavior, and early console output integrity are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk_8250.c -->
