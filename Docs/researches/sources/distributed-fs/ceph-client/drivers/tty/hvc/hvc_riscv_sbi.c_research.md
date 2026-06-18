# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_riscv_sbi.c

## Purpose
`hvc_riscv_sbi.c` provides a RISC-V SBI-backed HVC console. It supports the newer SBI debug console extension when available and falls back to legacy SBI v0.1 console calls when configured.

## Important APIs, Types, and Functions
`hvc_sbi_tty_put()` and `hvc_sbi_tty_get()` wrap legacy `sbi_console_putchar()` and `sbi_console_getchar()`. `hvc_sbi_dbcn_tty_put()` and `hvc_sbi_dbcn_tty_get()` wrap `sbi_debug_console_write()` and `sbi_debug_console_read()`. The two `hv_ops` tables are `hvc_sbi_v01_ops` and `hvc_sbi_dbcn_ops`. `hvc_sbi_init()` selects and registers the available backend.

## Control Flow
At device init, the driver first checks `sbi_debug_console_available`. If present, it allocates an HVC device and instantiates console slot 0 using DBCN ops. Otherwise, if legacy SBI v0.1 support is enabled, it allocates and instantiates with legacy ops. If neither path is available, init returns `-ENODEV`.

## State and Persistence Behavior
There is no driver-private persistent state. All state is in the generic HVC instance and SBI firmware.

## Dependencies and Integration Points
It depends on RISC-V `asm/sbi.h` and the HVC core. It has no IRQ notifier and therefore relies on HVC polling.

## Risks and Edge Cases
Legacy SBI console reads return negative when no character is available, while DBCN returns the debug console read result directly. The driver allocates before instantiating; if `hvc_instantiate()` failed, init still returns success after allocation, so console visibility depends on the instantiate result.

## Test Signals
Signals include boot on firmware with DBCN, boot with only SBI v0.1, readable input through polling, console output before userspace, and no registration on systems lacking both SBI console mechanisms.
