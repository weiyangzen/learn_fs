# sources/distributed-fs/ceph-client/drivers/clocksource/timer-versatile.c

## Purpose

`timer-versatile.c` is a minimal sched_clock driver for ARM Versatile and Versatile Express sysreg blocks. It maps the sysreg node and registers the 24 MHz counter at offset `SYS_24MHZ` as a 32-bit sched_clock.

## APIs And Flow

`versatile_sched_clock_init()` maps the DT resource, clears `OF_POPULATED` so the sysreg driver can still bind later, stores `versatile_sys_24mhz`, and calls `sched_clock_register()`. `versatile_sys_24mhz_read()` reads the counter.

## State, Dependencies, Risks, Tests

State is a single MMIO pointer; the counter is hardware-owned and no cleanup or PM path exists. Dependencies are OF mapping, sched_clock, MMIO, and sysreg compatibles `arm,vexpress-sysreg` and `arm,versatile-sysreg`. Risks are wrong offset/rate assumptions, mapping failure, wrap behavior, and sysreg probe conflicts if `OF_POPULATED` handling changes. Test early boot timestamps and later sysreg driver probing.
