## sources/distributed-fs/ceph-client/arch/mips/ralink/early_printk.c

### Purpose
This file implements early `prom_putchar()` for Ralink/MediaTek SoCs using fixed KSEG1 UART addresses before normal serial drivers are available.

### Important APIs, Types, And Functions
Compile-time constants choose `EARLY_UART_BASE` and `CHIPID_BASE` for RT288x, MT7621, or other Ralink SoCs. `uart_membase`, `chipid_membase`, and `init_complete` hold early state. `soc_is_mt7628()` detects MT7628 by chip name. `find_uart_base()` scans possible MT7628 UART offsets. `prom_putchar()` writes one byte using SoC-specific TX/LSR register conventions.

### Control Flow
The first `prom_putchar()` call optionally discovers MT7628 UART base once. MT7621 and MT7628 write `UART_TX` then wait for THRE in `UART_REG_LSR`. Older SoCs wait on `UART_REG_LSR_RT2880`, write `UART_REG_TX`, then wait again.

### State, Persistence, And Dependencies
State is fixed uncached UART/chipid mappings and the one-time base discovery flag. Dependencies include serial register bit definitions, KSEG1 address mapping, and selected SoC Kconfig.

### Integration Points
Used by `CONFIG_EARLY_PRINTK` before full Ralink serial and pinctrl setup.

### Risks
MT7628 UART discovery assumes a nonzero LCR identifies the active UART. Fixed base addresses must match bootloader UART routing. Busy-waiting can hang if UART clocking is unavailable.

### Test Signals
Verify early output on RT288x, MT7621, MT7620, and MT7628/MT7688 boards, including correct UART selection and no hangs when TX FIFO is full.
