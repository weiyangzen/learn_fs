# sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon-riscv-sbi.c

Purpose: RISC-V SBI-backed early console provider named `sbi`, allowing early printk output through firmware before a real UART driver is available.

Important APIs/types/functions: `sbi_putc()` wraps legacy `sbi_console_putchar()`. `sbi_0_1_console_write()` uses `uart_console_write()`. `sbi_dbcn_console_write()` emits chunks via `sbi_debug_console_write()`. `early_sbi_setup()` chooses SBI DBCN if available, otherwise legacy v0.1 when configured. Registered by `EARLYCON_DECLARE(sbi, early_sbi_setup)`.

Control flow: generic earlycon matches `earlycon=sbi` and calls setup. Setup installs the appropriate write callback or returns `-ENODEV`. DBCN writes loop until all bytes are accepted or an SBI error occurs; legacy writes are character based through `uart_console_write()`.

State/persistence: no private persistent state; it relies on global SBI capability/configuration and the generic earlycon device.

Dependencies/integration: RISC-V SBI interfaces, generic console/earlycon serial-core support, and `CONFIG_RISCV_SBI_V01` for fallback.

Risks: firmware-dependent availability; DBCN negative returns stop output without detailed recovery; legacy path requires kernel config support.

Test signals: boot with `earlycon=sbi` on DBCN firmware, legacy v0.1 firmware, no-provider failure, and long writes with partial SBI accepts.
