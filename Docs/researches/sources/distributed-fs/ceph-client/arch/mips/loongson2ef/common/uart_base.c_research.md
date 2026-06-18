<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/uart_base.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/uart_base.c

Purpose: Chooses raw and uncached UART base addresses for early printk and later serial platform registration.

Important APIs/types/functions: Exports `loongson_uart_base` and `_loongson_uart_base`; `prom_init_loongson_uart_base()` switches on `mips_machtype`.

Control flow: Fuloong 2E uses PCI IO 0x3f8, Fuloong/Lynloong 2F use PCI IO 0x2f8, and netbook/NAS-style machines use CPU LPC at `LOONGSON_LIO1_BASE + 0x3f8`. The uncached address is passed to `setup_8250_early_printk_port()`.

State and persistence: Stores early serial bases in globals used by `serial.c`.

Dependencies and integration: Called from `prom_init()` after machine type initialization.

Risks: Wrong machtype gives a silent console or corrupts unrelated IO. Early printk assumes a 1024 baud divisor parameter is appropriate.

Test signals: Early boot output should appear before platform serial registration and should continue on the same UART after 8250 binds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/uart_base.c -->
