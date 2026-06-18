# sources/distributed-fs/ceph-client/drivers/watchdog/aspeed_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/aspeed_wdt.c` is a watchdog-core driver for Aspeed BMC watchdog blocks across AST2400, AST2500, AST2600, and AST2700. It supports reset-mode selection, external reset pulse configuration, boot status reporting, alternate-flash boot recovery sysfs, optional pretimeout interrupts, and restart. The complete 589-line source was read for this report.

## Important APIs, Types, and Functions

SoC data is described by `struct aspeed_wdt_config` and `struct aspeed_wdt_scu`; instance state is `struct aspeed_wdt`. Operations are `aspeed_wdt_start()`, `aspeed_wdt_stop()`, `aspeed_wdt_ping()`, `aspeed_wdt_set_timeout()`, `aspeed_wdt_set_pretimeout()`, and `aspeed_wdt_restart()`. Other important functions include `aspeed_wdt_enable()`, `aspeed_wdt_update_bootstatus()`, `access_cs0_show()`, `access_cs0_store()`, `aspeed_wdt_irq()`, `aspeed_wdt_probe()`, `aspeed_wdt_init()`, and `aspeed_wdt_exit()`.

## Control Flow

An `arch_initcall` registers the platform driver early. Probe matches OF compatible data, maps registers, optionally requests a pretimeout IRQ, initializes watchdog core fields, applies nowayout, builds a cached control word from DT properties such as `aspeed,reset-type`, `aspeed,external-signal`, and `aspeed,alt-boot`, normalizes already-running hardware, programs external pulse polarity/drive/duration and reset masks for newer SoCs, updates bootstatus via SCU regmap, conditionally exposes `access_cs0`, and registers the watchdog. Start writes reload, restart magic, and control. Ping writes restart magic. Pretimeout updates IRQ fields in control. Restart arms a short timeout and delays.

## State and Persistence Behavior

`wdt->ctrl` is the driver's cached hardware control policy. Boot reset cause is read and cleared through SCU reset-status registers. Alternate boot selection can persist in watchdog timeout status until userspace clears it through `access_cs0`. Hardware reload, timeout, reset mask, and external pulse configuration live in MMIO registers.

## Dependencies and Integration Points

It depends on OF compatible tables, syscon/regmap for SCU status, optional IRQs, sysfs attribute groups, watchdog pretimeout notifications, MMIO access, and watchdog core. It integrates with BMC boot media behavior through the alternate boot bits.

## Risks and Edge Cases

SoC-specific reset-status widths and shifts are subtle; incorrect config data can misreport or clear the wrong reset cause. External pulse write semantics require magic high-byte values on some SoCs. Pretimeout support depends on an IRQ and correct `irq_mask`. The driver normalizes already-enabled hardware, which may change bootloader choices. `access_cs0` is intentionally limited to older alternate-boot scenarios.

## Test Signals

Test all compatible strings, reset-type parsing, external-signal and pulse settings, reset-mask programming, bootstatus read/clear for each SoC generation, pretimeout IRQ notification, alternate-boot sysfs behavior, active bootloader watchdog normalization, and early init build coverage.
